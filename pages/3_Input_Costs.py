"""
Input Costs Page — Commodity futures, PPI/CPI series by industry
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import numpy as np

from utils.industry_selector import render_industry_selector
from utils.data_fetchers import (
    get_commodity_prices, get_usda_beef_chicken, get_fred_series,
    fred_key_available,
)
from utils.charts import commodity_normalized_chart, commodity_detail_chart
from utils.style import inject_css

st.set_page_config(page_title="Input Costs", layout="wide")
st.logo(os.path.join(os.path.dirname(__file__), "..", "assets", "arini_logo.svg"))
inject_css()

# ── Industry selector (very top) ─────────────────────────────────────────
cfg = render_industry_selector()

st.title("Input Costs")
COMMODITY_FUTURES = cfg["commodity_futures"]
COMMODITY_UNITS = cfg["commodity_units"]
COMMODITY_META = cfg["commodity_meta"]
has_commodities = cfg["has_commodities"]
has_beef_chicken = cfg.get("has_beef_chicken", False)
fs = cfg["fred_series"]

st.caption(f"{cfg['name']} · Futures via Yahoo Finance · Pricing indices via FRED")

# ── Helper: compute change stats ─────────────────────────────────────────
def compute_changes(s: pd.Series) -> dict:
    s = s.dropna()
    if s.empty:
        return {"mom": None, "yoy": None, "ytd": None, "last": None, "last_date": None}
    last_val  = s.iloc[-1]
    last_date = s.index[-1]

    def _pct(old):
        if old is None or np.isnan(old) or old == 0:
            return None
        return round((last_val / old - 1) * 100, 1)

    idx_1m = s.index.searchsorted(last_date - pd.DateOffset(months=1))
    val_1m = s.iloc[min(idx_1m, len(s) - 1)] if idx_1m < len(s) else np.nan
    idx_1y = s.index.searchsorted(last_date - pd.DateOffset(years=1))
    val_1y = s.iloc[min(idx_1y, len(s) - 1)] if idx_1y < len(s) else np.nan
    ytd_start = pd.Timestamp(f"{last_date.year}-01-01")
    idx_ytd = s.index.searchsorted(ytd_start)
    val_ytd = s.iloc[min(idx_ytd, len(s) - 1)] if idx_ytd < len(s) else np.nan

    return {
        "last": round(last_val, 2), "last_date": last_date,
        "mom": _pct(val_1m), "yoy": _pct(val_1y), "ytd": _pct(val_ytd),
    }

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Settings")
    period = st.selectbox(
        "Lookback Period",
        ["6mo", "1y", "2y", "3y", "5y"],
        index=1,
        format_func=lambda x: {"6mo": "6 Months", "1y": "1 Year", "2y": "2 Years",
                                "3y": "3 Years", "5y": "5 Years"}[x],
    )
    if COMMODITY_FUTURES:
        futures_selected = st.multiselect(
            "Futures to display",
            list(COMMODITY_FUTURES.keys()),
            default=list(COMMODITY_FUTURES.keys()),
        )
    else:
        futures_selected = []

    if has_beef_chicken:
        show_beef_chicken = st.checkbox("Show beef & chicken prices", value=True)
    else:
        show_beef_chicken = False

# ── Fetch futures data ────────────────────────────────────────────────────
futures_map = {k: COMMODITY_FUTURES[k] for k in futures_selected} if futures_selected else {}
futures_df = pd.DataFrame()
if futures_map:
    with st.spinner("Fetching commodity futures…"):
        futures_df = get_commodity_prices(futures_map, period=period)

meat_df = pd.DataFrame()
if show_beef_chicken:
    with st.spinner("Fetching beef & chicken prices…"):
        meat_df = get_usda_beef_chicken(lookback_years=5)

# ── Merge all prices ──────────────────────────────────────────────────────
all_prices = futures_df.copy()
if not meat_df.empty:
    for col in meat_df.columns:
        if col not in all_prices.columns:
            all_prices[col] = meat_df[col]

# ── Fetch FRED pricing series for industries without commodity futures ─────
fred_pricing_series = {}
if not has_commodities or not futures_map:
    # Fetch industry-specific FRED pricing series
    for key in ["cpi_industry_1", "cpi_industry_2", "industry_kpi"]:
        series_id = fs.get(key)
        if series_id and fred_key_available():
            lbl_key = key.replace("cpi_", "").replace("industry_", "")
            label = cfg["macro_labels"].get(f"cpi_{lbl_key}_label") or cfg["macro_labels"].get(f"{lbl_key}_label") or key
            s = get_fred_series(series_id, start=f"{2015}-01-01")
            if not s.empty:
                fred_pricing_series[label] = s

# ═══════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ═══════════════════════════════════════════════════════════════════════════

has_any_content = False

if not all_prices.empty:
    has_any_content = True
    # ── Commodity Price Overview ──────────────────────────────────────────
    st.subheader("Commodity Price Overview")
    futures_prices = futures_df.copy() if not futures_df.empty else pd.DataFrame()
    meat_cols = [c for c in meat_df.columns if not meat_df[c].dropna().empty] if not meat_df.empty else []
    meat_prices = meat_df[meat_cols] if meat_cols else pd.DataFrame()

    tab_idx, tab_nom = st.tabs(["Indexed (Rebased to 100)", "Nominal Prices"])
    with tab_idx:
        if not futures_prices.empty:
            st.plotly_chart(
                commodity_normalized_chart(futures_prices, meta=COMMODITY_META, normalize=True),
                width="stretch",
            )
        else:
            st.info("No futures data available.")
    with tab_nom:
        if not futures_prices.empty:
            st.plotly_chart(
                commodity_normalized_chart(futures_prices, meta=COMMODITY_META, normalize=False),
                width="stretch",
            )
        else:
            st.info("No futures data available.")

    # ── Beef & Chicken (restaurants only) ─────────────────────────────────
    if not meat_prices.empty:
        st.subheader("Beef & Chicken Prices")
        st.caption("USDA AMS Market News (weekly wholesale) · FRED BLS fallback (monthly retail)")
        bc_idx, bc_nom = st.tabs(["Indexed (Rebased to 100)", "Nominal Prices"])
        with bc_idx:
            st.plotly_chart(
                commodity_normalized_chart(meat_prices, meta=COMMODITY_META, normalize=True),
                width="stretch",
            )
        with bc_nom:
            st.plotly_chart(
                commodity_normalized_chart(meat_prices, meta=COMMODITY_META, normalize=False),
                width="stretch",
            )

    # ── Summary metrics table ─────────────────────────────────────────────
    st.subheader("Change Summary")
    summary_rows = []
    for col in all_prices.columns:
        chg = compute_changes(all_prices[col])
        meta = COMMODITY_META.get(col, {})
        emoji = meta.get("emoji", "")
        cat = meta.get("category", "")
        unit = COMMODITY_UNITS.get(col, "")
        summary_rows.append({
            "Commodity": f"{emoji} {col}",
            "Category": cat,
            "Last Price": f"{chg['last']:.2f} {unit}" if chg["last"] is not None else "N/A",
            "MoM %": chg["mom"], "YoY %": chg["yoy"], "YTD %": chg["ytd"],
            "As of": chg["last_date"].strftime("%Y-%m-%d") if chg["last_date"] else "N/A",
        })

    if summary_rows:
        summary_df = pd.DataFrame(summary_rows).set_index("Commodity")

        def color_chg(val):
            if isinstance(val, float):
                return f"color: {'#e74c3c' if val > 0 else '#2ecc71'}; font-weight: bold"
            return ""

        st.dataframe(
            summary_df.style
                .map(color_chg, subset=["MoM %", "YoY %", "YTD %"])
                .format({
                    "MoM %": lambda v: f"{v:+.1f}%" if v is not None and pd.notna(v) else "N/A",
                    "YoY %": lambda v: f"{v:+.1f}%" if v is not None and pd.notna(v) else "N/A",
                    "YTD %": lambda v: f"{v:+.1f}%" if v is not None and pd.notna(v) else "N/A",
                }),
            width="stretch",
        )
        st.caption("Red = cost pressure (rising prices) · Green = favorable (falling prices)")

    # ── Individual commodity detail cards (row-aligned) ──────────────────
    st.subheader("Individual Commodity Charts")
    all_commodity_names = list(all_prices.columns) if not all_prices.empty else []
    if all_commodity_names:
        impact_notes = cfg.get("input_cost_notes", {})
        rendered = 0
        for i, name in enumerate(all_commodity_names):
            if name in futures_df.columns:
                series = futures_df[name].dropna()
            elif not meat_df.empty and name in meat_df.columns:
                series = meat_df[name].dropna()
            else:
                continue
            if series.empty:
                continue

            # Create new column pair every 2 items for alignment
            if rendered % 2 == 0:
                card_cols = st.columns(2)
            col = card_cols[rendered % 2]
            rendered += 1

            meta = COMMODITY_META.get(name, {})
            emoji = meta.get("emoji", "")
            cat = meta.get("category", "—")
            color = meta.get("color", "#3498db")
            unit = COMMODITY_UNITS.get(name, "")
            chg = compute_changes(series)

            with col:
                st.markdown(
                    f"**{emoji} {name}** &nbsp; <span style='color:#888;font-size:0.8rem'>{cat} · {unit}</span>",
                    unsafe_allow_html=True,
                )
                st.plotly_chart(
                    commodity_detail_chart(series, name, unit, color=color),
                    width="stretch",
                )
                m1, m2, m3 = st.columns(3)
                m1.metric("MoM", f"{chg['mom']:+.1f}%" if chg["mom"] is not None else "N/A",
                          delta=f"{chg['mom']:+.1f}%" if chg["mom"] is not None else None, delta_color="inverse")
                m2.metric("YoY", f"{chg['yoy']:+.1f}%" if chg["yoy"] is not None else "N/A",
                          delta=f"{chg['yoy']:+.1f}%" if chg["yoy"] is not None else None, delta_color="inverse")
                m3.metric("YTD", f"{chg['ytd']:+.1f}%" if chg["ytd"] is not None else "N/A",
                          delta=f"{chg['ytd']:+.1f}%" if chg["ytd"] is not None else None, delta_color="inverse")
                if name in impact_notes:
                    st.caption(f"**Impact:** {impact_notes[name]}")

# ── FRED-based Input Cost Indices (any industry) ─────────────────────────
input_cost_fred = cfg.get("input_cost_fred", {})
if input_cost_fred and fred_key_available():
    has_any_content = True
    st.subheader("Additional Input Cost Indices")
    st.caption(
        f"Producer Price Index series tracking key input costs for {cfg['name']}."
    )

    input_cost_notes = cfg.get("input_cost_notes", {})
    rendered_fred = 0
    for label, series_id in input_cost_fred.items():
        s = get_fred_series(series_id, start="2015-01-01", silent=True)
        if s.empty:
            continue
        chg = compute_changes(s)

        # Create new column pair every 2 items for alignment
        if rendered_fred % 2 == 0:
            fred_cols = st.columns(2)
        col = fred_cols[rendered_fred % 2]
        rendered_fred += 1

        with col:
            st.markdown(f"**{label}**")
            st.plotly_chart(
                commodity_detail_chart(s, label, "Index", color="#3498db"),
                width="stretch",
            )
            fm1, fm2, fm3 = st.columns(3)
            fm1.metric("MoM", f"{chg['mom']:+.1f}%" if chg["mom"] is not None else "N/A",
                       delta=f"{chg['mom']:+.1f}%" if chg["mom"] is not None else None, delta_color="inverse")
            fm2.metric("YoY", f"{chg['yoy']:+.1f}%" if chg["yoy"] is not None else "N/A",
                       delta=f"{chg['yoy']:+.1f}%" if chg["yoy"] is not None else None, delta_color="inverse")
            fm3.metric("YTD", f"{chg['ytd']:+.1f}%" if chg["ytd"] is not None else "N/A",
                       delta=f"{chg['ytd']:+.1f}%" if chg["ytd"] is not None else None, delta_color="inverse")
            if label in input_cost_notes:
                st.caption(f"**Impact:** {input_cost_notes[label]}")

# ── FRED-only pricing series (fallback for industries without other data) ──
if not has_any_content:
    if fred_pricing_series:
        st.subheader("Industry Pricing Indicators")
        st.caption("Price indices from FRED — no commodity futures tracked for this industry.")

        input_cost_notes = cfg.get("input_cost_notes", {})
        rendered_fp = 0
        for i, (label, series) in enumerate(fred_pricing_series.items()):
            if series.empty:
                continue
            chg = compute_changes(series)

            if rendered_fp % 2 == 0:
                card_cols = st.columns(2)
            col = card_cols[rendered_fp % 2]
            rendered_fp += 1

            with col:
                st.markdown(f"**{label}**")
                st.plotly_chart(
                    commodity_detail_chart(series, label, "Index", color="#3498db"),
                    width="stretch",
                )
                m1, m2, m3 = st.columns(3)
                m1.metric("MoM", f"{chg['mom']:+.1f}%" if chg["mom"] is not None else "N/A",
                          delta=f"{chg['mom']:+.1f}%" if chg["mom"] is not None else None, delta_color="inverse")
                m2.metric("YoY", f"{chg['yoy']:+.1f}%" if chg["yoy"] is not None else "N/A",
                          delta=f"{chg['yoy']:+.1f}%" if chg["yoy"] is not None else None, delta_color="inverse")
                m3.metric("YTD", f"{chg['ytd']:+.1f}%" if chg["ytd"] is not None else "N/A",
                          delta=f"{chg['ytd']:+.1f}%" if chg["ytd"] is not None else None, delta_color="inverse")
                if label in input_cost_notes:
                    st.caption(f"**Impact:** {input_cost_notes[label]}")
    else:
        st.info("No input cost data available for this industry. Check sidebar settings or FRED API key.")

st.divider()
st.caption(
    f"**{cfg['name']}** — "
    "Futures via Yahoo Finance (front-month continuous contracts). "
    "Pricing indices via FRED. "
    "Red = rising costs (pressure) · Green = falling costs (relief)."
)
