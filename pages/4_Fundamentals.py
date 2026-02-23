"""
Fundamentals Page — Revenue, Margins, EPS, Valuation Multiples
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from utils.industry_selector import render_industry_selector
from utils.data_fetchers import get_financials, get_info, get_valuation_table
from utils.charts import revenue_bar_chart, margin_chart, _base_layout
from utils.style import inject_css
from utils.export import (
    reset_export_state, add_export_figure, add_export_table,
    add_export_metric, render_export_sidebar,
)

st.set_page_config(page_title="Fundamentals", layout="wide")
st.logo(os.path.join(os.path.dirname(__file__), "..", "assets", "arini_logo.svg"))
inject_css()

# ── Industry selector (very top) ─────────────────────────────────────────
cfg = render_industry_selector()

st.title("Fundamentals")
reset_export_state()
COMPANIES = cfg["companies"]
TICKERS = list(COMPANIES.keys())
SEGMENTS = cfg["segments"]

st.caption("Data from Yahoo Finance · Updates with ~1 quarter lag after earnings")

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")
    segments_sel = st.multiselect(
        "Segments", list(SEGMENTS.keys()), default=list(SEGMENTS.keys())
    )
    selected = [t for seg in segments_sel for t in SEGMENTS[seg]]
    # Deduplicate while preserving order
    selected = list(dict.fromkeys(selected))

if not selected:
    st.info("Select at least one segment.")
    st.stop()

colors = {t: COMPANIES[t]["color"] for t in TICKERS}

# ── Valuation multiples table ──────────────────────────────────────────────
st.subheader("Valuation Multiples")
with st.spinner("Fetching valuation data…"):
    val_df = get_valuation_table(selected)

if not val_df.empty:
    val_df["Company"] = val_df.index.map(lambda t: COMPANIES[t]["name"])
    val_df["Segment"] = val_df.index.map(lambda t: COMPANIES[t]["segment"])
    cols_order = ["Company", "Segment", "Mkt Cap ($B)", "P/E (TTM)", "Fwd P/E", "EV/EBITDA", "Div Yield %"]
    val_display = val_df[[c for c in cols_order if c in val_df.columns]]

    def color_pe(val):
        if isinstance(val, float) and not np.isnan(val):
            if val > 50:
                return "color: #e74c3c"
            elif val < 15:
                return "color: #2ecc71"
        return ""

    st.dataframe(
        val_display.style
            .map(color_pe, subset=["P/E (TTM)", "Fwd P/E"])
            .format({
                "Mkt Cap ($B)": lambda v: f"${v:.1f}B" if pd.notna(v) else "N/A",
                "P/E (TTM)":    lambda v: f"{v:.1f}x" if pd.notna(v) else "N/A",
                "Fwd P/E":      lambda v: f"{v:.1f}x" if pd.notna(v) else "N/A",
                "EV/EBITDA":    lambda v: f"{v:.1f}x" if pd.notna(v) else "N/A",
                "Div Yield %":  lambda v: f"{v:.2f}%" if pd.notna(v) else "N/A",
            }),
        width="stretch",
    )

# ── Revenue and margin fetch ───────────────────────────────────────────────
st.subheader("Revenue & Margins")
st.caption("Pulling from Yahoo Finance quarterly income statements…")

rev_rows = []
margin_rows = []

progress = st.progress(0)
for i, ticker in enumerate(selected):
    progress.progress((i + 1) / len(selected))
    info = get_info(ticker)
    fins = get_financials(ticker)

    ttm_rev = info.get("totalRevenue", None)
    rev_rows.append({
        "Ticker": ticker,
        "Revenue ($B)": round(ttm_rev / 1e9, 2) if ttm_rev else np.nan,
    })

    op_margin  = info.get("operatingMargins", None)
    net_margin = info.get("profitMargins", None)
    gross_margin = info.get("grossMargins", None)
    margin_rows.append({
        "Ticker":         ticker,
        "Gross Margin %": round(gross_margin * 100, 1) if gross_margin else np.nan,
        "Oper Margin %":  round(op_margin * 100, 1)   if op_margin   else np.nan,
        "Net Margin %":   round(net_margin * 100, 1)  if net_margin  else np.nan,
    })

progress.empty()

rev_df     = pd.DataFrame(rev_rows).set_index("Ticker")
margin_df  = pd.DataFrame(margin_rows).set_index("Ticker")

col1, col2 = st.columns(2)
with col1:
    if not rev_df.empty:
        st.plotly_chart(revenue_bar_chart(rev_df, colors), width="stretch")

with col2:
    if not margin_df.empty:
        metric = st.radio(
            "Margin metric",
            ["Oper Margin %", "Net Margin %", "Gross Margin %"],
            horizontal=True,
        )
        st.plotly_chart(
            margin_chart(margin_df, colors, metric, f"{metric} by Company"),
            width="stretch",
        )

# ── EPS trend for selected ticker ──────────────────────────────────────────
st.subheader("Quarterly EPS Trend")
eps_ticker = st.selectbox(
    "Select ticker",
    selected,
    format_func=lambda t: f"{t} – {COMPANIES[t]['name']}",
)

with st.spinner(f"Loading {eps_ticker} financials…"):
    fins = get_financials(eps_ticker)

if fins and "income_q" in fins and not fins["income_q"].empty:
    inc = fins["income_q"]
    eps_row = None
    for candidate in ["Basic EPS", "Diluted EPS", "Net Income"]:
        if candidate in inc.index:
            eps_row = inc.loc[candidate]
            label = candidate
            break

    if eps_row is not None:
        eps_s = eps_row.dropna().sort_index()
        if label == "Net Income":
            eps_s = eps_s / 1e9

        fig = go.Figure(go.Bar(
            x=[d.strftime("%b %Y") for d in eps_s.index],
            y=eps_s.values,
            marker_color=[
                "#2ecc71" if v >= 0 else "#e74c3c" for v in eps_s.values
            ],
            hovertemplate="%{x}: %{y:.2f}<extra></extra>",
        ))
        unit_label = "($B)" if label == "Net Income" else "($)"
        fig.update_layout(
            **_base_layout(title=f"{eps_ticker} – {label} {unit_label} (Quarterly)"),
            yaxis_title=unit_label,
            height=380,
        )
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("EPS data not available from Yahoo Finance for this ticker.")
else:
    st.info(f"No quarterly income data found for {eps_ticker}.")

# ── Revenue growth table ───────────────────────────────────────────────────
st.subheader("Revenue Growth (YoY TTM)")
growth_rows = []
for ticker in selected:
    info = get_info(ticker)
    fins = get_financials(ticker)
    ttm = info.get("totalRevenue", np.nan)
    if fins and "income_a" in fins and not fins["income_a"].empty:
        inc_a = fins["income_a"]
        if "Total Revenue" in inc_a.index:
            rev_a = inc_a.loc["Total Revenue"].dropna().sort_index()
            prev_yr = rev_a.iloc[-2] if len(rev_a) >= 2 else np.nan
            yoy = (ttm / prev_yr - 1) * 100 if ttm and not np.isnan(prev_yr) and prev_yr else np.nan
        else:
            yoy = np.nan
    else:
        yoy = np.nan

    growth_rows.append({
        "Ticker":  ticker,
        "Company": COMPANIES[ticker]["name"],
        "TTM Rev ($B)": round(ttm / 1e9, 2) if ttm and not np.isnan(ttm) else np.nan,
        "YoY Rev Growth %": round(yoy, 1) if not np.isnan(yoy) else np.nan,
    })

if growth_rows:
    g_df = pd.DataFrame(growth_rows).set_index("Ticker")

    def color_growth(val):
        if isinstance(val, float) and not np.isnan(val):
            return f"color: {'#2ecc71' if val > 0 else '#e74c3c'}"
        return ""

    st.dataframe(
        g_df.style.map(color_growth, subset=["YoY Rev Growth %"])
                  .format({
                      "TTM Rev ($B)": lambda v: f"${v:.2f}B" if pd.notna(v) else "N/A",
                      "YoY Rev Growth %": lambda v: f"{v:.1f}%" if pd.notna(v) else "N/A",
                  }),
        width="stretch",
    )

st.divider()
st.caption(
    "**Data note:** Yahoo Finance data may lag by 1-2 quarters. "
    "Revenue/margins from yfinance `.info` are TTM (trailing twelve months)."
)

# ── Export sidebar ─────────────────────────────────────────────────────
render_export_sidebar(cfg["name"])
