"""
Input Costs / Las Vegas Market Page
- Gaming: Las Vegas tourism & gaming dashboard (LVCVA data + FRED)
- All other industries: Commodity futures, PPI/CPI series
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils.industry_selector import render_industry_selector
from utils.data_fetchers import (
    get_commodity_prices, get_usda_beef_chicken, get_fred_series,
    fred_key_available, get_lvcva_vegas_data,
)
from utils.charts import commodity_normalized_chart, commodity_detail_chart, _base_layout
from utils.style import inject_css

st.set_page_config(page_title="Input Costs", layout="wide")
st.logo(os.path.join(os.path.dirname(__file__), "..", "assets", "arini_logo.svg"))
inject_css()

# ── Industry selector (very top) ─────────────────────────────────────────
cfg = render_industry_selector()
is_gaming = cfg["name"] == "Gaming"

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


# ═══════════════════════════════════════════════════════════════════════════
# GAMING: LAS VEGAS MARKET DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════
if is_gaming:
    st.title(cfg.get("page_titles", {}).get("market", "Las Vegas Market"))
    st.caption("LVCVA Research Center (monthly) \u00b7 FRED employment data \u00b7 2019\u2013present")

    vegas = get_lvcva_vegas_data()

    if vegas.empty:
        st.warning("Unable to load LVCVA data. Please try again later.")
        st.stop()

    # ── Latest month summary metrics ─────────────────────────────────────
    latest = vegas.dropna(subset=["Visitor Volume"]).iloc[-1]
    latest_dt = latest.name
    prev_year_dt = latest_dt - pd.DateOffset(years=1)
    prev_year = vegas.loc[vegas.index <= prev_year_dt]
    py = prev_year.iloc[-1] if not prev_year.empty else pd.Series(dtype=float)

    def _delta(cur, prev, fmt="pct"):
        if pd.isna(cur) or pd.isna(prev) or prev == 0:
            return None
        if fmt == "pct":
            return round((cur / prev - 1) * 100, 1)
        return round(cur - prev, 1)

    st.markdown(f"**Latest data: {latest_dt.strftime('%B %Y')}**")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric(
        "Visitor Volume",
        f"{latest.get('Visitor Volume', 0)/1e6:.1f}M",
        delta=f"{_delta(latest.get('Visitor Volume'), py.get('Visitor Volume')):+.1f}% YoY" if _delta(latest.get('Visitor Volume'), py.get('Visitor Volume')) is not None else None,
    )
    m2.metric(
        "Strip Occupancy",
        f"{latest.get('Strip Occupancy', 0)*100:.1f}%",
        delta=f"{_delta(latest.get('Strip Occupancy'), py.get('Strip Occupancy'), 'pp'):.1f}pp" if _delta(latest.get('Strip Occupancy'), py.get('Strip Occupancy'), 'pp') is not None else None,
    )
    m3.metric(
        "Strip RevPAR",
        f"${latest.get('Strip RevPAR', 0):,.0f}",
        delta=f"{_delta(latest.get('Strip RevPAR'), py.get('Strip RevPAR')):+.1f}% YoY" if _delta(latest.get('Strip RevPAR'), py.get('Strip RevPAR')) is not None else None,
    )
    m4.metric(
        "Clark County GGR",
        f"${latest.get('Clark County GGR', 0)/1e9:.2f}B",
        delta=f"{_delta(latest.get('Clark County GGR'), py.get('Clark County GGR')):+.1f}% YoY" if _delta(latest.get('Clark County GGR'), py.get('Clark County GGR')) is not None else None,
    )
    m5.metric(
        "Convention Attendance",
        f"{latest.get('Convention Attendance', 0)/1e3:.0f}K",
        delta=f"{_delta(latest.get('Convention Attendance'), py.get('Convention Attendance')):+.1f}% YoY" if _delta(latest.get('Convention Attendance'), py.get('Convention Attendance')) is not None else None,
    )

    st.divider()

    # ══════════════════════════════════════════════════════════════════════
    # Section 1: Visitor Volume
    # ══════════════════════════════════════════════════════════════════════
    st.header("Visitor Volume")

    # Monthly visitor volume bars + YoY growth line
    vis = vegas[["Visitor Volume"]].dropna()
    vis["YoY %"] = vis["Visitor Volume"].pct_change(12) * 100

    fig_vis = make_subplots(specs=[[{"secondary_y": True}]])
    fig_vis.add_trace(
        go.Bar(
            x=vis.index, y=vis["Visitor Volume"] / 1e6,
            name="Visitors (M)",
            marker_color="#2C3E50",
            hovertemplate="%{x|%b %Y}: %{y:.2f}M<extra></extra>",
        ),
        secondary_y=False,
    )
    fig_vis.add_trace(
        go.Scatter(
            x=vis.index, y=vis["YoY %"],
            name="YoY %",
            line=dict(color="#E74C3C", width=2),
            hovertemplate="%{x|%b %Y}: %{y:.1f}%<extra></extra>",
        ),
        secondary_y=True,
    )
    fig_vis.add_hline(y=0, line_color="rgba(0,0,0,0.2)", line_width=1, secondary_y=True)
    fig_vis.update_layout(
        **_base_layout(title="Monthly Visitor Volume & YoY Growth"),
        height=420,
        legend=dict(orientation="h", yanchor="top", y=-0.10, xanchor="left", x=0),
    )
    fig_vis.update_yaxes(title_text="Visitors (Millions)", secondary_y=False)
    fig_vis.update_yaxes(title_text="YoY %", secondary_y=True)
    st.plotly_chart(fig_vis, use_container_width=True)

    # Convention Attendance
    conv = vegas[["Convention Attendance"]].dropna()
    conv["YoY %"] = conv["Convention Attendance"].pct_change(12) * 100

    fig_conv = make_subplots(specs=[[{"secondary_y": True}]])
    fig_conv.add_trace(
        go.Bar(
            x=conv.index, y=conv["Convention Attendance"] / 1e3,
            name="Attendance (K)",
            marker_color="#8E44AD",
            hovertemplate="%{x|%b %Y}: %{y:,.0f}K<extra></extra>",
        ),
        secondary_y=False,
    )
    fig_conv.add_trace(
        go.Scatter(
            x=conv.index, y=conv["YoY %"],
            name="YoY %",
            line=dict(color="#E74C3C", width=2),
            hovertemplate="%{x|%b %Y}: %{y:.1f}%<extra></extra>",
        ),
        secondary_y=True,
    )
    fig_conv.add_hline(y=0, line_color="rgba(0,0,0,0.2)", line_width=1, secondary_y=True)
    fig_conv.update_layout(
        **_base_layout(title="Convention Attendance & YoY Growth"),
        height=400,
        legend=dict(orientation="h", yanchor="top", y=-0.10, xanchor="left", x=0),
    )
    fig_conv.update_yaxes(title_text="Attendance (Thousands)", secondary_y=False)
    fig_conv.update_yaxes(title_text="YoY %", secondary_y=True)
    st.plotly_chart(fig_conv, use_container_width=True)
    st.caption(
        "Convention and meeting attendance is a key demand driver for midweek hotel "
        "occupancy and F&B revenue across MGM, CZR, WYNN, and LVS properties."
    )

    st.divider()

    # ══════════════════════════════════════════════════════════════════════
    # Section 2: Gaming Revenue
    # ══════════════════════════════════════════════════════════════════════
    st.header("Gaming Revenue")

    ggr_cols = ["Strip GGR", "Downtown GGR", "Boulder Strip GGR"]
    ggr = vegas[ggr_cols].dropna(how="all")
    if not ggr.empty:
        # Stacked area chart of GGR by area
        fig_ggr = go.Figure()
        colors = {"Strip GGR": "#C0392B", "Downtown GGR": "#2C3E50", "Boulder Strip GGR": "#F39C12"}
        labels = {"Strip GGR": "Strip", "Downtown GGR": "Downtown", "Boulder Strip GGR": "Boulder Strip"}
        for col in ggr_cols:
            if col in ggr.columns:
                fig_ggr.add_trace(go.Scatter(
                    x=ggr.index, y=ggr[col] / 1e9,
                    name=labels.get(col, col),
                    stackgroup="one",
                    line=dict(color=colors.get(col, "#3498db"), width=0.5),
                    hovertemplate="%{x|%b %Y}: $%{y:.2f}B<extra>" + labels.get(col, col) + "</extra>",
                ))
        fig_ggr.update_layout(
            **_base_layout(title="Clark County Gaming Revenue by Area (Monthly)"),
            yaxis_title="GGR ($B)", height=420,
            legend=dict(orientation="h", yanchor="top", y=-0.10, xanchor="left", x=0),
        )
        st.plotly_chart(fig_ggr, use_container_width=True)

    # Clark County GGR YoY growth
    cc_ggr = vegas[["Clark County GGR"]].dropna()
    if not cc_ggr.empty:
        cc_ggr["YoY %"] = cc_ggr["Clark County GGR"].pct_change(12) * 100
        yoy = cc_ggr["YoY %"].dropna()

        fig_ggr_yoy = go.Figure(go.Bar(
            x=yoy.index, y=yoy.values,
            marker_color=[("#27AE60" if v >= 0 else "#E74C3C") for v in yoy.values],
            hovertemplate="%{x|%b %Y}: %{y:.1f}%<extra></extra>",
        ))
        fig_ggr_yoy.add_hline(y=0, line_color="rgba(0,0,0,0.3)", line_width=1)
        fig_ggr_yoy.update_layout(
            **_base_layout(title="Clark County GGR \u2014 YoY Growth"),
            yaxis_title="YoY %", height=360,
        )
        st.plotly_chart(fig_ggr_yoy, use_container_width=True)

    st.caption(
        "Gaming revenue from the Nevada Gaming Control Board via LVCVA. Strip GGR is the "
        "primary revenue driver for LVS, MGM, WYNN, and CZR. Downtown and Boulder Strip "
        "are more relevant for regional operators like BYD and PENN."
    )

    st.divider()

    # ══════════════════════════════════════════════════════════════════════
    # Section 3: Hotel Performance (Occupancy, ADR, RevPAR)
    # ══════════════════════════════════════════════════════════════════════
    st.header("Hotel Performance")

    # Occupancy comparison: Strip vs Downtown vs Total
    occ_cols = ["Strip Occupancy", "Downtown Occupancy", "Total Occupancy"]
    occ = vegas[occ_cols].dropna(how="all")
    if not occ.empty:
        fig_occ = go.Figure()
        occ_colors = {"Strip Occupancy": "#C0392B", "Downtown Occupancy": "#2C3E50", "Total Occupancy": "#7F8C8D"}
        occ_labels = {"Strip Occupancy": "Strip", "Downtown Occupancy": "Downtown", "Total Occupancy": "Total"}
        for col in occ_cols:
            if col in occ.columns:
                fig_occ.add_trace(go.Scatter(
                    x=occ.index, y=occ[col] * 100,
                    name=occ_labels.get(col, col),
                    line=dict(color=occ_colors.get(col), width=2),
                    hovertemplate="%{x|%b %Y}: %{y:.1f}%<extra>" + occ_labels.get(col, col) + "</extra>",
                ))
        fig_occ.update_layout(
            **_base_layout(title="Hotel Occupancy Rate (%)"),
            yaxis_title="Occupancy %", height=400,
            legend=dict(orientation="h", yanchor="top", y=-0.10, xanchor="left", x=0),
        )
        st.plotly_chart(fig_occ, use_container_width=True)

    # ADR: Strip vs Downtown
    col_l, col_r = st.columns(2)
    adr_cols = ["Strip ADR", "Downtown ADR"]
    adr = vegas[adr_cols].dropna(how="all")
    if not adr.empty:
        with col_l:
            fig_adr = go.Figure()
            adr_colors = {"Strip ADR": "#C0392B", "Downtown ADR": "#2C3E50"}
            adr_labels = {"Strip ADR": "Strip", "Downtown ADR": "Downtown"}
            for col in adr_cols:
                if col in adr.columns:
                    fig_adr.add_trace(go.Scatter(
                        x=adr.index, y=adr[col],
                        name=adr_labels.get(col, col),
                        line=dict(color=adr_colors.get(col), width=2),
                        hovertemplate="%{x|%b %Y}: $%{y:.0f}<extra>" + adr_labels.get(col, col) + "</extra>",
                    ))
            fig_adr.update_layout(
                **_base_layout(title="Average Daily Rate (ADR)"),
                yaxis_title="ADR ($)", height=380,
                yaxis_tickprefix="$",
                legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="left", x=0),
            )
            st.plotly_chart(fig_adr, use_container_width=True)

    # RevPAR: Strip vs Downtown
    revpar_cols = ["Strip RevPAR", "Downtown RevPAR"]
    revpar = vegas[revpar_cols].dropna(how="all")
    if not revpar.empty:
        with col_r:
            fig_rev = go.Figure()
            rev_colors = {"Strip RevPAR": "#C0392B", "Downtown RevPAR": "#2C3E50"}
            rev_labels = {"Strip RevPAR": "Strip", "Downtown RevPAR": "Downtown"}
            for col in revpar_cols:
                if col in revpar.columns:
                    fig_rev.add_trace(go.Scatter(
                        x=revpar.index, y=revpar[col],
                        name=rev_labels.get(col, col),
                        line=dict(color=rev_colors.get(col), width=2),
                        hovertemplate="%{x|%b %Y}: $%{y:.0f}<extra>" + rev_labels.get(col, col) + "</extra>",
                    ))
            fig_rev.update_layout(
                **_base_layout(title="Revenue Per Available Room (RevPAR)"),
                yaxis_title="RevPAR ($)", height=380,
                yaxis_tickprefix="$",
                legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="left", x=0),
            )
            st.plotly_chart(fig_rev, use_container_width=True)

    # Weekend vs Midweek occupancy spread
    wk_cols = ["Weekend Occupancy", "Midweek Occupancy"]
    wk = vegas[wk_cols].dropna(how="all")
    if not wk.empty:
        wk["Spread"] = (wk["Weekend Occupancy"] - wk["Midweek Occupancy"]) * 100
        fig_wk = go.Figure()
        fig_wk.add_trace(go.Scatter(
            x=wk.index, y=wk["Weekend Occupancy"] * 100,
            name="Weekend", line=dict(color="#E67E22", width=2),
            hovertemplate="%{x|%b %Y}: %{y:.1f}%<extra>Weekend</extra>",
        ))
        fig_wk.add_trace(go.Scatter(
            x=wk.index, y=wk["Midweek Occupancy"] * 100,
            name="Midweek", line=dict(color="#3498DB", width=2),
            hovertemplate="%{x|%b %Y}: %{y:.1f}%<extra>Midweek</extra>",
        ))
        fig_wk.add_trace(go.Bar(
            x=wk.index, y=wk["Spread"],
            name="Spread (pp)",
            marker_color="rgba(52,152,219,0.2)",
            hovertemplate="%{x|%b %Y}: %{y:.1f}pp<extra>Spread</extra>",
            yaxis="y2",
        ))
        fig_wk.update_layout(
            **_base_layout(title="Weekend vs Midweek Occupancy"),
            yaxis_title="Occupancy %", height=400,
            yaxis2=dict(overlaying="y", side="right", title="Spread (pp)", showgrid=False),
            legend=dict(orientation="h", yanchor="top", y=-0.10, xanchor="left", x=0),
        )
        st.plotly_chart(fig_wk, use_container_width=True)
        st.caption(
            "Weekend/midweek spread reflects leisure vs. convention/business demand mix. "
            "Narrowing spread indicates strengthening midweek demand (positive for CZR, MGM convention business)."
        )

    st.divider()

    # ══════════════════════════════════════════════════════════════════════
    # Section 4: Airport & Transportation
    # ══════════════════════════════════════════════════════════════════════
    st.header("Airport Traffic")

    pax = vegas[["Airport Passengers"]].dropna()
    if not pax.empty:
        pax["YoY %"] = pax["Airport Passengers"].pct_change(12) * 100

        fig_pax = make_subplots(specs=[[{"secondary_y": True}]])
        fig_pax.add_trace(
            go.Bar(
                x=pax.index, y=pax["Airport Passengers"] / 1e6,
                name="Passengers (M)",
                marker_color="#1ABC9C",
                hovertemplate="%{x|%b %Y}: %{y:.1f}M<extra></extra>",
            ),
            secondary_y=False,
        )
        fig_pax.add_trace(
            go.Scatter(
                x=pax.index, y=pax["YoY %"],
                name="YoY %",
                line=dict(color="#E74C3C", width=2),
                hovertemplate="%{x|%b %Y}: %{y:.1f}%<extra></extra>",
            ),
            secondary_y=True,
        )
        fig_pax.add_hline(y=0, line_color="rgba(0,0,0,0.2)", line_width=1, secondary_y=True)
        fig_pax.update_layout(
            **_base_layout(title="Harry Reid International Airport \u2014 Monthly Passengers"),
            height=400,
            legend=dict(orientation="h", yanchor="top", y=-0.10, xanchor="left", x=0),
        )
        fig_pax.update_yaxes(title_text="Passengers (Millions)", secondary_y=False)
        fig_pax.update_yaxes(title_text="YoY %", secondary_y=True)
        st.plotly_chart(fig_pax, use_container_width=True)
        st.caption("Airport enplanements/deplanements are a leading indicator for visitor volume.")

    st.divider()

    # ══════════════════════════════════════════════════════════════════════
    # Section 5: Vegas Employment (FRED)
    # ══════════════════════════════════════════════════════════════════════
    vegas_fred = cfg.get("vegas_fred", {})
    if vegas_fred and fred_key_available():
        st.header("Las Vegas Employment")

        emp_col_l, emp_col_r = st.columns(2)

        # L&H Employment
        lh_id = vegas_fred.get("lv_lh_employment")
        if lh_id:
            lh = get_fred_series(lh_id, start="2015-01-01", silent=True)
            if not lh.empty:
                with emp_col_l:
                    fig_lh = go.Figure(go.Scatter(
                        x=lh.index, y=lh.values,
                        name="L&H Employment",
                        line=dict(color="#2C3E50", width=2),
                        fill="tozeroy",
                        fillcolor="rgba(44,62,80,0.1)",
                        hovertemplate="%{x|%b %Y}: %{y:,.0f}K<extra></extra>",
                    ))
                    fig_lh.update_layout(
                        **_base_layout(title="Leisure & Hospitality Employment (LV MSA)"),
                        yaxis_title="Thousands", height=380,
                    )
                    st.plotly_chart(fig_lh, use_container_width=True)

        # Gambling Employment
        gamb_id = vegas_fred.get("lv_gambling_employment")
        if gamb_id:
            gamb = get_fred_series(gamb_id, start="2015-01-01", silent=True)
            if not gamb.empty:
                with emp_col_r:
                    fig_gamb = go.Figure(go.Scatter(
                        x=gamb.index, y=gamb.values,
                        name="Gambling Employment",
                        line=dict(color="#C0392B", width=2),
                        fill="tozeroy",
                        fillcolor="rgba(192,57,43,0.1)",
                        hovertemplate="%{x|%b %Y}: %{y:,.1f}K<extra></extra>",
                    ))
                    fig_gamb.update_layout(
                        **_base_layout(title="Gambling Industries Employment (LV MSA)"),
                        yaxis_title="Thousands", height=380,
                    )
                    st.plotly_chart(fig_gamb, use_container_width=True)

        # Unemployment
        ur_id = vegas_fred.get("lv_unemployment")
        if ur_id:
            ur = get_fred_series(ur_id, start="2015-01-01", silent=True)
            if not ur.empty:
                fig_ur = go.Figure(go.Scatter(
                    x=ur.index, y=ur.values,
                    name="Unemployment Rate",
                    line=dict(color="#E74C3C", width=2),
                    fill="tozeroy",
                    fillcolor="rgba(231,76,60,0.08)",
                    hovertemplate="%{x|%b %Y}: %{y:.1f}%<extra></extra>",
                ))
                fig_ur.update_layout(
                    **_base_layout(title="Las Vegas MSA Unemployment Rate"),
                    yaxis_title="%", height=360,
                )
                st.plotly_chart(fig_ur, use_container_width=True)

        st.caption(
            "Employment data from FRED (BLS). Leisure & hospitality employment is a proxy for "
            "the overall health of the Las Vegas tourism economy. Gambling industries employment "
            "tracks headcount at casinos specifically."
        )

    st.divider()

    # ══════════════════════════════════════════════════════════════════════
    # Section 6: Monthly Data Table
    # ══════════════════════════════════════════════════════════════════════
    with st.expander("Show Full Monthly Data Table"):
        display = vegas.copy()
        # Format columns for readability
        fmt_map = {}
        for c in display.columns:
            if "GGR" in c:
                display[c] = display[c] / 1e6
                fmt_map[c] = "${:,.0f}M"
            elif "Occupancy" in c:
                display[c] = display[c] * 100
                fmt_map[c] = "{:.1f}%"
            elif "ADR" in c or "RevPAR" in c:
                fmt_map[c] = "${:,.0f}"
            elif "Volume" in c or "Attendance" in c or "Passengers" in c or "Room Nights" in c:
                display[c] = display[c] / 1e3
                fmt_map[c] = "{:,.0f}K"
        st.dataframe(
            display.style.format(fmt_map, na_rep="\u2014"),
            use_container_width=True,
            height=500,
        )

    st.caption(
        "**Las Vegas Market** \u2014 Data from LVCVA Research Center "
        "(lvcva.com/research) and FRED. Updated monthly."
    )

# ═══════════════════════════════════════════════════════════════════════════
# ALL OTHER INDUSTRIES: INPUT COSTS (original behavior)
# ═══════════════════════════════════════════════════════════════════════════
else:
    st.title(cfg.get("page_titles", {}).get("market", "Input Costs"))
    COMMODITY_FUTURES = cfg["commodity_futures"]
    COMMODITY_UNITS = cfg["commodity_units"]
    COMMODITY_META = cfg["commodity_meta"]
    has_commodities = cfg["has_commodities"]
    has_beef_chicken = cfg.get("has_beef_chicken", False)
    fs = cfg["fred_series"]

    st.caption(f"{cfg['name']} \u00b7 Futures via Yahoo Finance \u00b7 Pricing indices via FRED")

    # ── Sidebar ──────────────────────────────────────────────────────────
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

    # ── Fetch futures data ───────────────────────────────────────────────
    futures_map = {k: COMMODITY_FUTURES[k] for k in futures_selected} if futures_selected else {}
    futures_df = pd.DataFrame()
    if futures_map:
        with st.spinner("Fetching commodity futures\u2026"):
            futures_df = get_commodity_prices(futures_map, period=period)

    meat_df = pd.DataFrame()
    if show_beef_chicken:
        with st.spinner("Fetching beef & chicken prices\u2026"):
            meat_df = get_usda_beef_chicken(lookback_years=5)

    # ── Merge all prices ─────────────────────────────────────────────────
    all_prices = futures_df.copy()
    if not meat_df.empty:
        for col in meat_df.columns:
            if col not in all_prices.columns:
                all_prices[col] = meat_df[col]

    # ── Fetch FRED pricing series ────────────────────────────────────────
    fred_pricing_series = {}
    fred_pricing_raw = {}
    for key in ["cpi_industry_1", "cpi_industry_2", "industry_kpi"]:
        series_id = fs.get(key)
        if series_id and fred_key_available():
            lbl_key = key.replace("cpi_", "").replace("industry_", "")
            label = cfg["macro_labels"].get(f"cpi_{lbl_key}_label") or cfg["macro_labels"].get(f"{lbl_key}_label") or key
            s = get_fred_series(series_id, start="2015-01-01")
            if not s.empty:
                fred_pricing_series[label] = s
                fred_pricing_raw[key] = s

    # ═════════════════════════════════════════════════════════════════════
    # MAIN CONTENT
    # ═════════════════════════════════════════════════════════════════════

    has_any_content = False

    if not all_prices.empty:
        has_any_content = True
        # ── Commodity Price Overview ─────────────────────────────────────
        st.subheader("Commodity Price Overview")
        futures_prices = futures_df.copy() if not futures_df.empty else pd.DataFrame()
        meat_cols = [c for c in meat_df.columns if not meat_df[c].dropna().empty] if not meat_df.empty else []
        meat_prices = meat_df[meat_cols] if meat_cols else pd.DataFrame()

        tab_idx, tab_nom = st.tabs(["Indexed (Rebased to 100)", "Nominal Prices"])
        with tab_idx:
            if not futures_prices.empty:
                st.plotly_chart(
                    commodity_normalized_chart(futures_prices, meta=COMMODITY_META, normalize=True),
                    use_container_width=True,
                )
            else:
                st.info("No futures data available.")
        with tab_nom:
            if not futures_prices.empty:
                st.plotly_chart(
                    commodity_normalized_chart(futures_prices, meta=COMMODITY_META, normalize=False),
                    use_container_width=True,
                )
            else:
                st.info("No futures data available.")

        # ── Beef & Chicken (restaurants only) ────────────────────────────
        if not meat_prices.empty:
            st.subheader("Beef & Chicken Prices")
            st.caption("USDA AMS Market News (weekly wholesale) \u00b7 FRED BLS fallback (monthly retail)")
            bc_idx, bc_nom = st.tabs(["Indexed (Rebased to 100)", "Nominal Prices"])
            with bc_idx:
                st.plotly_chart(
                    commodity_normalized_chart(meat_prices, meta=COMMODITY_META, normalize=True),
                    use_container_width=True,
                )
            with bc_nom:
                st.plotly_chart(
                    commodity_normalized_chart(meat_prices, meta=COMMODITY_META, normalize=False),
                    use_container_width=True,
                )

        # ── Summary metrics table ────────────────────────────────────────
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
                use_container_width=True,
            )
            st.caption("Red = cost pressure (rising prices) \u00b7 Green = favorable (falling prices)")

        # ── Individual commodity detail cards ─────────────────────────────
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

                if rendered % 2 == 0:
                    card_cols = st.columns(2)
                col = card_cols[rendered % 2]
                rendered += 1

                meta = COMMODITY_META.get(name, {})
                emoji = meta.get("emoji", "")
                cat = meta.get("category", "\u2014")
                color = meta.get("color", "#3498db")
                unit = COMMODITY_UNITS.get(name, "")
                chg = compute_changes(series)

                with col:
                    st.markdown(
                        f"**{emoji} {name}** &nbsp; <span style='color:#888;font-size:0.8rem'>{cat} \u00b7 {unit}</span>",
                        unsafe_allow_html=True,
                    )
                    st.plotly_chart(
                        commodity_detail_chart(series, name, unit, color=color),
                        use_container_width=True,
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

    # ── FRED-based Input Cost Indices ─────────────────────────────────────
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

            if rendered_fred % 2 == 0:
                fred_cols = st.columns(2)
            col = fred_cols[rendered_fred % 2]
            rendered_fred += 1

            with col:
                st.markdown(f"**{label}**")
                st.plotly_chart(
                    commodity_detail_chart(s, label, "Index", color="#3498db"),
                    use_container_width=True,
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

    # ── FRED-only pricing series (fallback) ──────────────────────────────
    if not has_any_content:
        if fred_pricing_series:
            st.subheader("Industry Pricing Indicators")
            st.caption("Price indices from FRED \u2014 no commodity futures tracked for this industry.")

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
                        use_container_width=True,
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

    # ── Industry Pricing Indices (YoY % charts) ──────────────────────────
    lbl = cfg.get("macro_labels", {})

    if fred_pricing_raw:
        has_any_content = True
        st.divider()
        st.header(lbl.get("industry_section_title", "Industry Pricing"))

        def _yoy(s):
            return s.pct_change(12).dropna() * 100

        if "industry_kpi" in fred_pricing_raw:
            kpi_label = lbl.get("industry_kpi_label", "Industry KPI Index")
            kpi_s = fred_pricing_raw["industry_kpi"]
            yoy_kpi = _yoy(kpi_s)

            st.subheader(lbl.get("industry_kpi_chart_title", f"{kpi_label} (YoY %)"))
            if lbl.get("industry_kpi_caption"):
                st.caption(lbl["industry_kpi_caption"])

            fig_kpi = go.Figure()
            fig_kpi.add_trace(go.Scatter(
                x=yoy_kpi.index, y=yoy_kpi.values,
                name=kpi_label,
                line=dict(color="#C0392B", width=2.5),
                fill="tozeroy",
                fillcolor="rgba(192, 57, 43, 0.1)",
            ))
            fig_kpi.add_hline(y=0, line_color="rgba(0,0,0,0.3)", line_width=1)
            fig_kpi.update_layout(
                **_base_layout(title=lbl.get("industry_kpi_chart_title", f"{kpi_label} (YoY %)")),
                yaxis_title="YoY %", height=380,
            )
            st.plotly_chart(fig_kpi, use_container_width=True)

            with st.expander(f"Show {kpi_label} \u2014 Absolute Index Level"):
                fig_kpi_abs = go.Figure(go.Scatter(
                    x=kpi_s.index, y=kpi_s.values,
                    name=kpi_label,
                    line=dict(color="#C0392B", width=2),
                ))
                fig_kpi_abs.update_layout(
                    **_base_layout(title=f"{kpi_label} \u2014 Index Level"),
                    yaxis_title="Index", height=340,
                )
                st.plotly_chart(fig_kpi_abs, use_container_width=True)

        if "cpi_industry_1" in fred_pricing_raw:
            s1 = fred_pricing_raw["cpi_industry_1"]
            s2 = fred_pricing_raw.get("cpi_industry_2", pd.Series(dtype=float))
            yoy_1 = _yoy(s1)
            label_1 = lbl.get("cpi_label_1", "Series 1")
            label_2 = lbl.get("cpi_label_2", "Series 2")

            st.subheader(lbl.get("cpi_chart_title", "Industry Pricing (YoY %)"))
            st.caption(lbl.get("cpi_chart_caption", ""))

            fig_cpi = go.Figure()
            fig_cpi.add_trace(go.Scatter(
                x=yoy_1.index, y=yoy_1.values,
                name=label_1,
                line=dict(color="#e67e22", width=2.5),
            ))

            if s2 is not None and not s2.empty and label_2:
                yoy_2 = _yoy(s2)
                fig_cpi.add_trace(go.Scatter(
                    x=yoy_2.index, y=yoy_2.values,
                    name=label_2,
                    line=dict(color="#3498db", width=2.5),
                ))

            fig_cpi.add_hline(y=0, line_color="rgba(0,0,0,0.2)", line_width=1)
            fig_cpi.update_layout(
                **_base_layout(title=lbl.get("cpi_chart_title", "Industry Pricing (YoY %)")),
                yaxis_title="YoY %", height=400,
                legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="left", x=0),
            )
            st.plotly_chart(fig_cpi, use_container_width=True)

            with st.expander("Show Index Level (Absolute)"):
                fig_abs = go.Figure()
                fig_abs.add_trace(go.Scatter(
                    x=s1.index, y=s1.values,
                    name=label_1, line=dict(color="#e67e22", width=2),
                ))
                if s2 is not None and not s2.empty and label_2:
                    fig_abs.add_trace(go.Scatter(
                        x=s2.index, y=s2.values,
                        name=label_2, line=dict(color="#3498db", width=2),
                    ))
                fig_abs.update_layout(
                    **_base_layout(title="Index Level"),
                    yaxis_title="Index", height=360,
                    legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="left", x=0),
                )
                st.plotly_chart(fig_abs, use_container_width=True)

            if s2 is not None and not s2.empty and label_2:
                yoy_s1 = _yoy(s1)
                yoy_s2 = _yoy(s2)
                spread = (yoy_s1 - yoy_s2).dropna()
                if not spread.empty:
                    st.caption(f"**Spread:** {label_1} minus {label_2} (YoY pp)")
                    fig_spread = go.Figure(go.Bar(
                        x=spread.index, y=spread.values,
                        marker_color=["#e74c3c" if v > 0 else "#2ecc71" for v in spread.values],
                        hovertemplate="%{x|%b %Y}: %{y:.1f}pp<extra></extra>",
                    ))
                    fig_spread.add_hline(y=0, line_color="rgba(0,0,0,0.2)", line_width=1)
                    fig_spread.update_layout(
                        **_base_layout(title=f"{label_1} \u2212 {label_2} (YoY pp Spread)"),
                        yaxis_title="Percentage Points", height=320,
                    )
                    st.plotly_chart(fig_spread, use_container_width=True)

    st.divider()
    st.caption(
        f"**{cfg['name']}** \u2014 "
        "Futures via Yahoo Finance (front-month continuous contracts). "
        "Pricing indices via FRED. "
        "Red = rising costs (pressure) \u00b7 Green = falling costs (relief)."
    )
