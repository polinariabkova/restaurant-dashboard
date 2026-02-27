"""
Macro & Industry Page — Universal macro indicators + industry-specific data
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.industry_selector import render_industry_selector
from utils.data_fetchers import get_fred_series, fred_key_available
from utils.charts import (
    dual_cpi_chart, wages_chart, sentiment_chart,
    unemployment_chart, employment_chart, fed_funds_chart,
    job_openings_chart, _base_layout,
)
from utils.style import inject_css

st.set_page_config(page_title="Macro & Industry", layout="wide")
st.logo(os.path.join(os.path.dirname(__file__), "..", "assets", "arini_logo.svg"))
inject_css()

# ── Industry selector (very top) ─────────────────────────────────────────
cfg = render_industry_selector()

st.title(cfg.get("page_titles", {}).get("macro", "Macro & Industry Environment"))
fs = cfg["fred_series"]
lbl = cfg["macro_labels"]

st.caption(
    "Data via FRED (Federal Reserve Economic Data) · "
    "Requires free FRED API key — see sidebar if charts are empty."
)

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Settings")
    start_year = st.slider("History Start Year", 2010, 2022, 2015)
    start_date = f"{start_year}-01-01"

    if not fred_key_available():
        st.error(
            "**FRED API key missing.**\n\n"
            "Get a free key at [fred.stlouisfed.org](https://fred.stlouisfed.org/docs/api/api_key.html).\n\n"
            "Add `FRED_API_KEY=your_key` to a `.env` file in the project folder, then restart."
        )

if not fred_key_available():
    st.error(
        "FRED API key not configured. All charts on this page require a free FRED API key. "
        "See the sidebar for setup instructions."
    )
    st.stop()

# ── Fetch universal FRED series ───────────────────────────────────────────
with st.spinner("Fetching FRED data…"):
    cpi_all      = get_fred_series("CPIAUCSL", start=start_date)
    recession    = get_fred_series("USREC", start=start_date)
    sentiment    = get_fred_series("UMCSENT", start=start_date)
    unemployment = get_fred_series("UNRATE", start=start_date)
    fed_funds    = get_fred_series("FEDFUNDS", start=start_date)

    # Industry-specific series
    ind_1 = get_fred_series(fs["cpi_industry_1"], start=start_date) if fs.get("cpi_industry_1") else pd.Series(dtype=float)
    ind_2 = get_fred_series(fs["cpi_industry_2"], start=start_date) if fs.get("cpi_industry_2") else pd.Series(dtype=float)
    wages_data = get_fred_series(fs["wages"], start=start_date) if fs.get("wages") else pd.Series(dtype=float)
    ind_emp = get_fred_series(fs["industry_employment"], start=start_date) if fs.get("industry_employment") else pd.Series(dtype=float)
    job_open = get_fred_series(fs["job_openings"], start=start_date) if fs.get("job_openings") else pd.Series(dtype=float)

# ── KPI cards — Row 1 ─────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)

if not ind_1.empty:
    yoy_1 = ind_1.pct_change(12).dropna() * 100
    if not yoy_1.empty:
        c1.metric(
            f"{lbl['cpi_industry_1_label']} — {yoy_1.index[-1].strftime('%b %Y')}",
            f"{yoy_1.iloc[-1]:.1f}% YoY",
            f"{yoy_1.iloc[-1] - yoy_1.iloc[-2]:.1f}pp MoM" if len(yoy_1) > 1 else None,
        )

if not ind_2.empty and lbl.get("cpi_industry_2_label"):
    yoy_2 = ind_2.pct_change(12).dropna() * 100
    if not yoy_2.empty:
        c2.metric(
            f"{lbl['cpi_industry_2_label']} — {yoy_2.index[-1].strftime('%b %Y')}",
            f"{yoy_2.iloc[-1]:.1f}% YoY",
            f"{yoy_2.iloc[-1] - yoy_2.iloc[-2]:.1f}pp MoM" if len(yoy_2) > 1 else None,
        )

if not wages_data.empty:
    yoy_w = wages_data.pct_change(12).dropna() * 100
    if not yoy_w.empty:
        c3.metric(
            f"{lbl['wages_label']} — {yoy_w.index[-1].strftime('%b %Y')}",
            f"{yoy_w.iloc[-1]:.1f}% YoY",
            f"{yoy_w.iloc[-1] - yoy_w.iloc[-2]:.1f}pp MoM" if len(yoy_w) > 1 else None,
        )

if not unemployment.empty:
    c4.metric(
        f"Unemployment — {unemployment.index[-1].strftime('%b %Y')}",
        f"{unemployment.iloc[-1]:.1f}%",
        f"{unemployment.iloc[-1] - unemployment.iloc[-2]:.1f}pp MoM" if len(unemployment) > 1 else None,
        delta_color="inverse",
    )

# ── KPI cards — Row 2 ─────────────────────────────────────────────────────
c5, c6, c7, c8 = st.columns(4)

if not sentiment.empty:
    c5.metric(
        f"Consumer Sentiment — {sentiment.index[-1].strftime('%b %Y')}",
        f"{sentiment.iloc[-1]:.1f}",
        f"{sentiment.iloc[-1] - sentiment.iloc[-2]:.1f} MoM" if len(sentiment) > 1 else None,
    )

if not fed_funds.empty:
    c6.metric(
        f"Fed Funds Rate — {fed_funds.index[-1].strftime('%b %Y')}",
        f"{fed_funds.iloc[-1]:.2f}%",
        f"{fed_funds.iloc[-1] - fed_funds.iloc[-2]:.1f}pp MoM" if len(fed_funds) > 1 else None,
        delta_color="inverse",
    )

if not ind_emp.empty:
    c7.metric(
        f"{lbl['employment_label']} — {ind_emp.index[-1].strftime('%b %Y')}",
        f"{ind_emp.iloc[-1]:,.0f}",
        f"{ind_emp.iloc[-1] - ind_emp.iloc[-2]:+,.0f} MoM" if len(ind_emp) > 1 else None,
    )

if not cpi_all.empty:
    yoy_cpi = cpi_all.pct_change(12).dropna() * 100
    if not yoy_cpi.empty:
        c8.metric(
            f"CPI All Items — {yoy_cpi.index[-1].strftime('%b %Y')}",
            f"{yoy_cpi.iloc[-1]:.1f}% YoY",
            f"{yoy_cpi.iloc[-1] - yoy_cpi.iloc[-2]:.1f}pp MoM" if len(yoy_cpi) > 1 else None,
        )

st.divider()

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1: INDUSTRY-SPECIFIC PRICING
# ═══════════════════════════════════════════════════════════════════════════
st.subheader(lbl["industry_section_title"])
st.caption(lbl["cpi_chart_caption"])

# ── Dual chart (if two series) or single chart ────────────────────────────
if not ind_1.empty and not ind_2.empty:
    st.plotly_chart(
        dual_cpi_chart(
            ind_1, ind_2, recession,
            title=lbl.get("cpi_chart_title", "Industry Pricing (YoY %)"),
            label_1=lbl.get("cpi_label_1", "Series 1"),
            label_2=lbl.get("cpi_label_2", "Series 2"),
        ),
        width="stretch",
    )
elif not ind_1.empty:
    # Single series — show as YoY line chart
    yoy_chart = ind_1.pct_change(12).dropna() * 100
    fig_single = go.Figure(go.Scatter(
        x=yoy_chart.index, y=yoy_chart.values,
        name=lbl.get("cpi_label_1", "Industry Index"),
        line=dict(color="#e67e22", width=2),
    ))
    fig_single.add_hline(y=0, line_color="rgba(0,0,0,0.2)", line_width=1, opacity=0.6)
    fig_single.update_layout(
        **_base_layout(title=lbl.get("cpi_chart_title", "Industry Pricing (YoY %)")),
        yaxis_title="YoY %", height=400,
    )
    st.plotly_chart(fig_single, width="stretch")
else:
    st.warning("Industry pricing data unavailable.")

# ── Absolute index levels (expander) ──────────────────────────────────────
with st.expander("Show Index Level (Absolute)"):
    fig_abs = go.Figure()
    if not ind_1.empty:
        fig_abs.add_trace(go.Scatter(
            x=ind_1.index, y=ind_1.values,
            name=lbl.get("cpi_label_1", "Series 1"), line=dict(color="#e67e22", width=2),
        ))
    if not ind_2.empty and lbl.get("cpi_label_2"):
        fig_abs.add_trace(go.Scatter(
            x=ind_2.index, y=ind_2.values,
            name=lbl.get("cpi_label_2", "Series 2"), line=dict(color="#3498db", width=2),
        ))
    if not cpi_all.empty:
        fig_abs.add_trace(go.Scatter(
            x=cpi_all.index, y=cpi_all.values,
            name="CPI All Items", line=dict(color="#95a5a6", width=1.5, dash="dot"),
        ))
    fig_abs.update_layout(
        **_base_layout(title="Index Level"),
        yaxis_title="Index",
        legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="left", x=0),
        height=360,
    )
    st.plotly_chart(fig_abs, width="stretch")

# ── Spread (if two series) ────────────────────────────────────────────────
if not ind_1.empty and not ind_2.empty:
    st.caption(
        f"**Spread:** {lbl.get('cpi_label_1', 'Series 1')} minus "
        f"{lbl.get('cpi_label_2', 'Series 2')} (YoY percentage points)"
    )
    yoy_s1 = ind_1.pct_change(12).dropna() * 100
    yoy_s2 = ind_2.pct_change(12).dropna() * 100
    spread = (yoy_s1 - yoy_s2).dropna()

    fig_s = go.Figure(go.Bar(
        x=spread.index,
        y=spread.values,
        marker_color=["#e74c3c" if v > 0 else "#2ecc71" for v in spread.values],
        hovertemplate="%{x|%b %Y}: %{y:.2f}pp<extra></extra>",
    ))
    fig_s.add_hline(y=0, line_color="rgba(0,0,0,0.2)", line_width=1, opacity=0.6)
    fig_s.update_layout(
        **_base_layout(title=f"{lbl.get('cpi_label_1', '')} \u2212 {lbl.get('cpi_label_2', '')} (YoY pp Spread)"),
        yaxis_title="Percentage Points",
        height=320,
    )
    st.plotly_chart(fig_s, width="stretch")

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: LABOR MARKET
# ═══════════════════════════════════════════════════════════════════════════
st.subheader(lbl.get("employment_section_title", "Labor Market"))
st.caption(lbl.get("employment_caption", ""))

# ── Wages + Employment side by side ───────────────────────────────────────
col_w, col_e = st.columns(2)

with col_w:
    if not wages_data.empty:
        st.plotly_chart(
            wages_chart(wages_data, recession, title=lbl.get("wages_chart_title", "Wages (YoY %)")),
            width="stretch",
        )
    else:
        st.warning("Wage data unavailable.")

with col_e:
    if not ind_emp.empty:
        st.plotly_chart(
            employment_chart(
                ind_emp, recession,
                title=lbl.get("employment_chart_title", "Industry Employment"),
                y_title=lbl.get("employment_y_title", "Thousands"),
            ),
            width="stretch",
        )
    else:
        st.warning("Employment data unavailable.")

# ── Absolute wages + Job openings side by side ───────────────────────────
col_wa, col_jo = st.columns(2)

with col_wa:
    if not wages_data.empty:
        with st.expander("Show Absolute Wage Level ($/hr)"):
            fig_w = go.Figure(go.Scatter(
                x=wages_data.index, y=wages_data.values,
                name="Avg Hourly Earnings",
                line=dict(color="#2ecc71", width=2),
            ))
            fig_w.update_layout(
                **_base_layout(title=f"{lbl.get('wages_label', 'Wages')} ($/hr)"),
                yaxis_title="$/hr", height=340,
            )
            st.plotly_chart(fig_w, width="stretch")

with col_jo:
    if not job_open.empty and lbl.get("job_openings_chart_title"):
        with st.expander(f"Show {lbl['job_openings_chart_title']}"):
            st.plotly_chart(
                job_openings_chart(job_open, recession, title=lbl["job_openings_chart_title"]),
                width="stretch",
            )

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3: CONSUMER HEALTH & MACRO
# ═══════════════════════════════════════════════════════════════════════════
st.subheader("Consumer Health & Macro Backdrop")
st.caption(
    "Consumer sentiment is a leading indicator of spending intent. "
    "Unemployment and the Fed Funds rate frame the broader macro environment."
)

# ── Sentiment + Unemployment side by side ─────────────────────────────────
col_s, col_u = st.columns(2)

with col_s:
    if not sentiment.empty:
        st.plotly_chart(sentiment_chart(sentiment), width="stretch")
    else:
        st.warning("Consumer sentiment data unavailable.")

with col_u:
    if not unemployment.empty:
        st.plotly_chart(unemployment_chart(unemployment, recession), width="stretch")
    else:
        st.warning("Unemployment data unavailable.")

# ── Fed Funds Rate ────────────────────────────────────────────────────────
if not fed_funds.empty:
    st.plotly_chart(fed_funds_chart(fed_funds, recession), width="stretch")
    st.caption(
        "Higher rates increase borrowing costs for expansion and capital projects. "
        "Rate cuts signal easing financial conditions — positive for growth."
    )

st.divider()
st.caption(
    "**Sources:** FRED — CPIAUCSL, UNRATE, FEDFUNDS, USREC, UMCSENT, "
    + ", ".join(v for v in [fs.get("cpi_industry_1"), fs.get("cpi_industry_2"),
                            fs.get("wages"), fs.get("industry_employment"),
                            fs.get("job_openings")] if v)
    + "."
)
