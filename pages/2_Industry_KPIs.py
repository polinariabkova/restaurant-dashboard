"""
Industry KPIs Page — Same-Store Sales for restaurants, FRED-based KPIs for other industries
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from utils.industry_selector import render_industry_selector
from utils.data_fetchers import get_fred_series, fred_key_available
from utils.charts import _base_layout
from utils.style import inject_css
from utils.export import (
    reset_export_state, add_export_figure, add_export_table,
    add_export_metric, render_export_sidebar,
)

st.set_page_config(page_title="Industry KPIs", layout="wide")
st.logo(os.path.join(os.path.dirname(__file__), "..", "assets", "arini_logo.svg"))
inject_css()

# ── Industry selector (very top) ─────────────────────────────────────────
cfg = render_industry_selector()

st.title("Industry KPIs")
reset_export_state()

if cfg["has_sss"]:
    # ═══════════════════════════════════════════════════════════════════════
    # RESTAURANT SSS PAGE (full existing functionality)
    # ═══════════════════════════════════════════════════════════════════════
    from config import COMPANIES, TICKERS, SEGMENTS
    from data.sss_data import SSS_DATA, HAS_TRAFFIC_TICKET, SSS_LABEL, SSS_LAST_UPDATED, SSS_NEXT_UPDATE
    from utils.charts import sss_grouped_bar, sss_line_chart, traffic_ticket_chart

    st.header("Same-Store Sales (SSS) Tracker")

    col_hdr1, col_hdr2 = st.columns([3, 1])
    with col_hdr1:
        st.caption(
            "Data sourced from public earnings releases. "
            "Metric definitions vary by company — see the 'Label' column. "
            "Stock prices, commodities, and macro data refresh automatically every hour/day."
        )
    with col_hdr2:
        st.info(f"SSS data: **{SSS_LAST_UPDATED}**\nNext update: {SSS_NEXT_UPDATE}", icon=None)

    # ── Sorted quarter list (chronological) ───────────────────────────────
    def quarter_key(q: str) -> tuple:
        parts = q.split()
        return (int(parts[1]), int(parts[0][1]))

    quarters_all = sorted(
        {row["quarter"] for t in SSS_DATA for row in SSS_DATA[t]},
        key=quarter_key,
    )
    latest_quarter = quarters_all[-1]

    PRESETS = {
        "1 Year":   4,
        "2 Years":  8,
        "3 Years":  12,
        "5 Years":  20,
        "All Data": len(quarters_all),
    }

    # ── Sidebar ───────────────────────────────────────────────────────────
    with st.sidebar:
        st.header("Filters")

        preset = st.selectbox("Timeframe", list(PRESETS.keys()), index=3)
        n_quarters = PRESETS[preset]
        default_start = quarters_all[max(0, len(quarters_all) - n_quarters)]

        q_range = st.select_slider(
            "Custom quarter range",
            options=quarters_all,
            value=(default_start, latest_quarter),
        )

        st.divider()

        segments_sel = st.multiselect(
            "Segments", list(SEGMENTS.keys()), default=list(SEGMENTS.keys()),
        )
        all_tickers = [t for seg in segments_sel for t in SEGMENTS[seg] if t in SSS_DATA]
        selected = st.multiselect(
            "Companies", options=all_tickers, default=all_tickers,
            format_func=lambda t: f"{t} - {COMPANIES[t]['name']}",
        )

    if not selected:
        st.info("Select at least one company from the sidebar.")
        st.stop()

    q_start, q_end = q_range
    q_list = [q for q in quarters_all
              if quarter_key(q) >= quarter_key(q_start)
              and quarter_key(q) <= quarter_key(q_end)]

    def build_sss_df(tickers, q_list):
        rows = []
        for t in tickers:
            for row in SSS_DATA.get(t, []):
                if row["quarter"] in q_list:
                    rows.append({"ticker": t, **row})
        return pd.DataFrame(rows)

    df_raw = build_sss_df(selected, q_list)

    if df_raw.empty:
        st.warning("No SSS data available for the selected filters.")
        st.stop()

    pivot = df_raw.pivot_table(index="quarter", columns="ticker", values="sss", aggfunc="first")
    pivot = pivot.reindex([q for q in q_list if q in pivot.index])
    colors = {t: COMPANIES[t]["color"] for t in TICKERS}

    st.caption(
        f"Showing **{len(q_list)} quarters**: {q_start} to {q_end}  |  "
        f"Latest SSS data: **{latest_quarter}**"
    )

    st.subheader("SSS by Company and Quarter")
    st.plotly_chart(sss_grouped_bar(pivot, colors), width="stretch")

    st.subheader("SSS Trend Over Time")
    st.plotly_chart(sss_line_chart(pivot, colors), width="stretch")

    # ── Data table ────────────────────────────────────────────────────────
    st.subheader("SSS Data Table")
    table_df = df_raw[["quarter", "ticker", "sss"]].copy()
    table_df["company"] = table_df["ticker"].map(lambda t: COMPANIES[t]["name"])
    table_df["segment"] = table_df["ticker"].map(lambda t: COMPANIES[t]["segment"])
    table_df["label"]   = table_df["ticker"].map(SSS_LABEL)
    table_df["_sort"]   = table_df["quarter"].map(quarter_key)
    table_df = table_df.sort_values(["_sort", "segment", "ticker"]).drop(columns="_sort")
    table_df = table_df.rename(columns={
        "quarter": "Quarter", "ticker": "Ticker",
        "company": "Company", "segment": "Segment",
        "sss": "SSS %", "label": "Metric",
    })

    def color_sss(val):
        if isinstance(val, (int, float)):
            return f"color: {'#2ecc71' if val > 0 else '#e74c3c'}; font-weight: bold"
        return ""

    st.dataframe(
        table_df.style.map(color_sss, subset=["SSS %"])
                      .format({"SSS %": "{:.1f}%"}),
        width="stretch", height=420,
    )

    # ── Traffic vs Ticket ─────────────────────────────────────────────────
    tt_candidates = [t for t in selected if t in HAS_TRAFFIC_TICKET]
    if tt_candidates:
        st.subheader("Traffic vs. Average Ticket Contribution (ppts)")
        st.caption("Only companies that disclose this breakdown are shown.")
        cols = st.columns(min(len(tt_candidates), 2))
        for i, t in enumerate(tt_candidates):
            t_df = pd.DataFrame(SSS_DATA[t])
            t_df = t_df[t_df["quarter"].isin(q_list)]
            valid = t_df.dropna(subset=["traffic", "ticket"])
            if valid.empty:
                continue
            with cols[i % 2]:
                st.plotly_chart(
                    traffic_ticket_chart(valid, t, COMPANIES[t]["color"]),
                    width="stretch",
                )

    # ── Latest quarter summary ────────────────────────────────────────────
    st.subheader(f"Most Recent Quarter ({latest_quarter}) - Quick Reference")
    latest_rows = []
    for t in selected:
        data = SSS_DATA.get(t, [])
        if not data:
            continue
        latest = data[-1]
        latest_rows.append({
            "Ticker": t, "Company": COMPANIES[t]["name"],
            "Segment": COMPANIES[t]["segment"], "Quarter": latest["quarter"],
            "SSS %": latest["sss"],
            "Traffic (ppts)": latest.get("traffic"),
            "Ticket (ppts)": latest.get("ticket"),
        })
    if latest_rows:
        ldf = pd.DataFrame(latest_rows).set_index("Ticker").sort_values("SSS %", ascending=False)
        st.dataframe(
            ldf.style.map(color_sss, subset=["SSS %"])
                     .format({
                         "SSS %": "{:.1f}%",
                         "Traffic (ppts)": lambda v: f"{v:.1f}" if v is not None and pd.notna(v) else "N/A",
                         "Ticket (ppts)": lambda v: f"{v:.1f}" if v is not None and pd.notna(v) else "N/A",
                     }),
            width="stretch",
        )

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════
    # RESTAURANT — QSR vs CASUAL DINING SSS SPREAD
    # ═══════════════════════════════════════════════════════════════════════
    st.subheader("QSR vs Casual Dining SSS Spread")
    st.caption(
        "Average SSS for Quick Service (QSR) minus Casual Dining — a proxy for drive-thru/convenience demand. "
        "Positive spread = QSR outperforming, suggesting drive-thru demand strength."
    )

    # Compute segment averages by quarter
    qsr_tickers = SEGMENTS.get("Quick Service (QSR)", [])
    casual_tickers = SEGMENTS.get("Casual Dining", [])

    if qsr_tickers and casual_tickers:
        spread_rows = []
        for q in quarters:
            qsr_vals = [
                next((d["sss"] for d in SSS_DATA.get(t, []) if d["quarter"] == q), None)
                for t in qsr_tickers
            ]
            casual_vals = [
                next((d["sss"] for d in SSS_DATA.get(t, []) if d["quarter"] == q), None)
                for t in casual_tickers
            ]
            qsr_avg = np.nanmean([v for v in qsr_vals if v is not None]) if any(v is not None for v in qsr_vals) else None
            casual_avg = np.nanmean([v for v in casual_vals if v is not None]) if any(v is not None for v in casual_vals) else None

            if qsr_avg is not None and casual_avg is not None:
                spread_rows.append({
                    "Quarter": q,
                    "QSR Avg SSS": round(qsr_avg, 1),
                    "Casual Avg SSS": round(casual_avg, 1),
                    "Spread": round(qsr_avg - casual_avg, 1),
                })

        if spread_rows:
            spread_df = pd.DataFrame(spread_rows)

            fig_spread = go.Figure()
            fig_spread.add_trace(go.Bar(
                x=spread_df["Quarter"],
                y=spread_df["Spread"],
                name="QSR − Casual Spread",
                marker_color=[
                    "#2ecc71" if v >= 0 else "#e74c3c" for v in spread_df["Spread"]
                ],
                hovertemplate="%{x}: %{y:.1f}pp<extra></extra>",
            ))
            fig_spread.add_trace(go.Scatter(
                x=spread_df["Quarter"], y=spread_df["QSR Avg SSS"],
                name="QSR Avg SSS", mode="lines+markers",
                line=dict(color="#e67e22", width=2),
            ))
            fig_spread.add_trace(go.Scatter(
                x=spread_df["Quarter"], y=spread_df["Casual Avg SSS"],
                name="Casual Avg SSS", mode="lines+markers",
                line=dict(color="#3498db", width=2),
            ))
            fig_spread.add_hline(y=0, line_color="rgba(0,0,0,0.3)", line_width=1)
            fig_spread.update_layout(
                **_base_layout(title="QSR vs Casual Dining SSS Spread (pp)"),
                yaxis_title="SSS (%)", height=420,
                legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="left", x=0),
                barmode="relative",
            )
            st.plotly_chart(fig_spread, width="stretch")
            add_export_figure("QSR vs Casual SSS Spread", fig_spread)

            with st.expander("Spread Data"):
                st.dataframe(spread_df.set_index("Quarter"), width="stretch")
                add_export_table("SSS Spread Data", spread_df.set_index("Quarter"))
        else:
            st.info("Insufficient data to compute QSR vs Casual spread.")
    else:
        st.info("QSR and Casual Dining segments not available for spread calculation.")

    st.divider()

    # ═══════════════════════════════════════════════════════════════════════
    # RESTAURANT — UNIT GROWTH TRACKER
    # ═══════════════════════════════════════════════════════════════════════
    st.subheader("Restaurant Unit Growth")
    st.caption(
        "Quarterly net unit openings/closures by chain — key driver of revenue growth beyond SSS. "
        "Data sourced from company earnings reports (curated)."
    )

    # Curated quarterly unit counts from recent 10-Q/10-K filings
    # Format: ticker -> list of {quarter, units}
    UNIT_COUNTS = {
        "MCD": [
            {"quarter": "Q3 2024", "units": 41822}, {"quarter": "Q2 2024", "units": 41596},
            {"quarter": "Q1 2024", "units": 41411}, {"quarter": "Q4 2023", "units": 41198},
            {"quarter": "Q3 2023", "units": 40714}, {"quarter": "Q2 2023", "units": 40457},
        ],
        "SBUX": [
            {"quarter": "Q3 2024", "units": 39477}, {"quarter": "Q2 2024", "units": 39038},
            {"quarter": "Q1 2024", "units": 38587}, {"quarter": "Q4 2023", "units": 38038},
            {"quarter": "Q3 2023", "units": 37222}, {"quarter": "Q2 2023", "units": 36634},
        ],
        "CMG": [
            {"quarter": "Q3 2024", "units": 3615}, {"quarter": "Q2 2024", "units": 3530},
            {"quarter": "Q1 2024", "units": 3479}, {"quarter": "Q4 2023", "units": 3437},
            {"quarter": "Q3 2023", "units": 3370}, {"quarter": "Q2 2023", "units": 3317},
        ],
        "YUM": [
            {"quarter": "Q3 2024", "units": 59652}, {"quarter": "Q2 2024", "units": 59290},
            {"quarter": "Q1 2024", "units": 58838}, {"quarter": "Q4 2023", "units": 58275},
            {"quarter": "Q3 2023", "units": 57221}, {"quarter": "Q2 2023", "units": 56617},
        ],
        "DPZ": [
            {"quarter": "Q3 2024", "units": 20879}, {"quarter": "Q2 2024", "units": 20713},
            {"quarter": "Q1 2024", "units": 20561}, {"quarter": "Q4 2023", "units": 20349},
            {"quarter": "Q3 2023", "units": 20117}, {"quarter": "Q2 2023", "units": 19906},
        ],
        "WEN": [
            {"quarter": "Q3 2024", "units": 7165}, {"quarter": "Q2 2024", "units": 7142},
            {"quarter": "Q1 2024", "units": 7120}, {"quarter": "Q4 2023", "units": 7095},
            {"quarter": "Q3 2023", "units": 7067}, {"quarter": "Q2 2023", "units": 7050},
        ],
        "DRI": [
            {"quarter": "Q3 2024", "units": 2031}, {"quarter": "Q2 2024", "units": 2013},
            {"quarter": "Q1 2024", "units": 1998}, {"quarter": "Q4 2023", "units": 1985},
            {"quarter": "Q3 2023", "units": 1963}, {"quarter": "Q2 2023", "units": 1949},
        ],
        "SHAK": [
            {"quarter": "Q3 2024", "units": 552}, {"quarter": "Q2 2024", "units": 530},
            {"quarter": "Q1 2024", "units": 510}, {"quarter": "Q4 2023", "units": 495},
            {"quarter": "Q3 2023", "units": 474}, {"quarter": "Q2 2023", "units": 453},
        ],
    }

    if UNIT_COUNTS:
        # Build net growth DataFrame
        growth_rows = []
        for tkr, data in UNIT_COUNTS.items():
            sorted_data = sorted(data, key=lambda d: d["quarter"])
            for i in range(1, len(sorted_data)):
                net_change = sorted_data[i]["units"] - sorted_data[i-1]["units"]
                growth_rows.append({
                    "Ticker": tkr,
                    "Company": COMPANIES.get(tkr, {}).get("name", tkr),
                    "Quarter": sorted_data[i]["quarter"],
                    "Total Units": sorted_data[i]["units"],
                    "Net New Units": net_change,
                })

        if growth_rows:
            growth_df = pd.DataFrame(growth_rows)

            # Net new units grouped bar
            fig_growth = go.Figure()
            growth_colors = ["#e67e22", "#3498db", "#2ecc71", "#e74c3c", "#9b59b6",
                             "#1abc9c", "#f39c12", "#8e44ad"]
            for i, tkr in enumerate(UNIT_COUNTS.keys()):
                tkr_data = growth_df[growth_df["Ticker"] == tkr]
                fig_growth.add_trace(go.Bar(
                    x=tkr_data["Quarter"],
                    y=tkr_data["Net New Units"],
                    name=tkr,
                    marker_color=growth_colors[i % len(growth_colors)],
                    hovertemplate=f"<b>{tkr}</b><br>" + "%{x}: %{y:+,d} units<extra></extra>",
                ))
            fig_growth.update_layout(
                **_base_layout(title="Net New Restaurant Units by Quarter"),
                barmode="group",
                yaxis_title="Net New Units",
                height=440,
                legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="left", x=0),
            )
            st.plotly_chart(fig_growth, width="stretch")
            add_export_figure("Net New Restaurant Units", fig_growth)

            # Latest unit count table
            with st.expander("Current Unit Counts"):
                latest_units = []
                for tkr, data in UNIT_COUNTS.items():
                    latest = max(data, key=lambda d: d["quarter"])
                    earliest = min(data, key=lambda d: d["quarter"])
                    yoy_change = latest["units"] - earliest["units"]
                    latest_units.append({
                        "Ticker": tkr,
                        "Company": COMPANIES.get(tkr, {}).get("name", tkr),
                        "Latest Units": f"{latest['units']:,}",
                        "Quarter": latest["quarter"],
                        "Net Change (Period)": f"{yoy_change:+,}",
                        "Growth %": f"{(yoy_change/earliest['units']*100):.1f}%",
                    })
                units_df = pd.DataFrame(latest_units).set_index("Ticker")
                st.dataframe(units_df, width="stretch")
                add_export_table("Restaurant Unit Counts", units_df)

    st.divider()
    st.caption(
        f"**SSS data last updated:** {SSS_LAST_UPDATED} earnings cycle  |  "
        f"**Next manual update:** {SSS_NEXT_UPDATE}  |  "
        "**Stock prices / commodities / macro:** auto-refresh every 1-24 hours via yfinance & FRED"
    )

elif cfg["name"] == "Movie Theaters":
    # ═══════════════════════════════════════════════════════════════════════
    # MOVIE THEATERS — BOX OFFICE KPIs
    # ═══════════════════════════════════════════════════════════════════════
    from utils.data_fetchers import (
        get_weekly_box_office, get_weekly_box_office_trend,
        get_weekly_box_office_52w, get_annual_box_office,
        get_release_schedule, get_distributor_share_multi_year,
        get_franchise_box_office,
    )
    from utils.charts import weekly_bo_chart, annual_bo_chart, ytd_pacing_chart

    COMPANIES = cfg["companies"]
    fs = cfg["fred_series"]
    lbl = cfg["macro_labels"]

    st.header("Box Office Dashboard")
    st.caption("Live data from The Numbers · Updates daily · FRED pricing & employment data")

    # ── Sidebar ───────────────────────────────────────────────────────────
    current_year = pd.Timestamp.now().year
    py_options = [current_year - 1, current_year - 2, current_year - 3, 2019]
    # Deduplicate while preserving order
    py_options = list(dict.fromkeys(py_options))

    with st.sidebar:
        st.header("Settings")
        bo_compare_year = st.selectbox(
            "Prior Year (PY)",
            py_options,
            index=0,
            format_func=lambda y: f"{y}" + (" (pre-COVID)" if y == 2019 else ""),
        )
        start_year = st.slider("FRED History Start Year", 2010, 2022, 2015)
        start_date = f"{start_year}-01-01"

    # ── Fetch box office data ─────────────────────────────────────────────
    with st.spinner("Fetching box office data (may be slow on first load)…"):
        weekly_chart_df = get_weekly_box_office()
        # 52-week rolling data (current + prior year combined)
        weekly_52w = get_weekly_box_office_52w()
        # Current + PY for YoY
        weekly_trend_current = get_weekly_box_office_trend(current_year)
        weekly_trend_prior = get_weekly_box_office_trend(bo_compare_year)
        annual_df = get_annual_box_office()
        release_df = get_release_schedule()

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 1: WTD / MTD / YTD SNAPSHOT + VS PRIOR YEAR
    # ══════════════════════════════════════════════════════════════════════

    today = pd.Timestamp.now().normalize()

    # Current year & prior year data for metrics
    cy_data = weekly_trend_current if not weekly_trend_current.empty else pd.DataFrame()
    py_data = weekly_trend_prior if not weekly_trend_prior.empty else pd.DataFrame()

    # Compute WTD, MTD, YTD
    def _period_total(df, start_date):
        if df.empty:
            return 0
        mask = df["weekend_date"] >= pd.Timestamp(start_date)
        return df.loc[mask, "combined_gross"].sum()

    # Current month start
    month_start = today.replace(day=1)
    # Current week start (Monday)
    week_start = today - pd.Timedelta(days=today.weekday())
    # Year start
    year_start = pd.Timestamp(f"{current_year}-01-01")

    wtd_cy = _period_total(cy_data, week_start)
    mtd_cy = _period_total(cy_data, month_start)
    ytd_cy = _period_total(cy_data, year_start)

    # Same periods in prior year (shifted)
    year_diff = current_year - bo_compare_year
    py_week_start = week_start - pd.DateOffset(years=year_diff)
    py_month_start = month_start - pd.DateOffset(years=year_diff)
    py_year_start = pd.Timestamp(f"{bo_compare_year}-01-01")

    # For PY YTD, match the same number of weeks
    n_cy_weeks = len(cy_data)
    ytd_py = py_data.head(n_cy_weeks)["combined_gross"].sum() if not py_data.empty else 0
    mtd_py = _period_total(py_data, py_month_start)

    # Latest weekend data
    latest_wk_gross = None
    latest_wk_date = ""
    prev_wk_gross = None

    if not cy_data.empty:
        latest = cy_data.iloc[-1]
        latest_wk_gross = latest.get("combined_gross")
        latest_wk_date = latest["weekend_date"].strftime("%b %d") if pd.notna(latest.get("weekend_date")) else ""
        if len(cy_data) > 1:
            prev_wk_gross = cy_data.iloc[-2].get("combined_gross")

    # Display metric cards — Row 1
    c1, c2, c3 = st.columns(3)

    if latest_wk_gross:
        wow_delta = None
        if prev_wk_gross and prev_wk_gross > 0:
            wow_pct = (latest_wk_gross / prev_wk_gross - 1) * 100
            wow_delta = f"{wow_pct:+.1f}% WoW"
        c1.metric(
            f"Weekend BO ({latest_wk_date})" if latest_wk_date else "Latest Weekend BO",
            f"${latest_wk_gross:,.0f}",
            delta=wow_delta, delta_color="normal",
        )
        add_export_metric("Weekend BO", f"${latest_wk_gross:,.0f}", wow_delta or "")

    if mtd_cy > 0:
        mtd_delta = None
        if mtd_py > 0:
            mtd_pct = (mtd_cy / mtd_py - 1) * 100
            mtd_delta = f"{mtd_pct:+.1f}% vs PY"
        c2.metric(
            f"MTD ({today.strftime('%B')})",
            f"${mtd_cy:,.0f}",
            delta=mtd_delta, delta_color="normal",
        )
        add_export_metric("MTD BO", f"${mtd_cy:,.0f}", mtd_delta or "")

    if ytd_cy > 0:
        ytd_delta = None
        if ytd_py > 0:
            ytd_pct = (ytd_cy / ytd_py - 1) * 100
            ytd_delta = f"{ytd_pct:+.1f}% vs PY"
        c3.metric("YTD Box Office", f"${ytd_cy:,.0f}", delta=ytd_delta, delta_color="normal")
        add_export_metric("YTD BO", f"${ytd_cy:,.0f}", ytd_delta or "")

    # Row 2: Avg ticket price
    if not annual_df.empty:
        latest_year = annual_df.iloc[0]
        yr_label = int(latest_year["Year"]) if "Year" in latest_year.index else ""
        if latest_year.get("Avg Ticket Price"):
            c4_col, _ = st.columns([1, 3])
            c4_col.metric(
                f"Avg Ticket Price ({yr_label})" if yr_label else "Avg Ticket Price",
                f"${latest_year['Avg Ticket Price']:.2f}",
            )

    # Top 5 movies this weekend
    if not weekly_chart_df.empty:
        top5 = weekly_chart_df.head(5).copy()
        st.markdown("**Top 5 Movies This Weekend**")
        top5_display = []
        for _, row in top5.iterrows():
            top5_display.append({
                "#": int(row["Rank"]) if pd.notna(row.get("Rank")) else "",
                "Movie": row.get("Title", ""),
                "Distributor": row.get("Distributor", ""),
                "Weekend Gross": f"${row['Gross']:,.0f}" if pd.notna(row.get("Gross")) and row["Gross"] else "N/A",
                "Total Gross": f"${row['Total Gross']:,.0f}" if pd.notna(row.get("Total Gross")) and row["Total Gross"] else "N/A",
                "Theaters": f"{row['Theaters']:,}" if pd.notna(row.get("Theaters")) and row["Theaters"] else "N/A",
            })
        st.dataframe(pd.DataFrame(top5_display), width="stretch", hide_index=True)

    st.divider()

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 2: 52-WEEK ROLLING BOX OFFICE TRACKER
    # ══════════════════════════════════════════════════════════════════════
    st.subheader("Weekly Box Office — Last 52 Weeks")

    if not weekly_52w.empty and "combined_gross" in weekly_52w.columns:
        fig_52w = go.Figure()
        fig_52w.add_trace(go.Bar(
            x=weekly_52w["weekend_date"],
            y=weekly_52w["combined_gross"],
            marker_color=[
                "#1565C0" if d.year == current_year else "#90CAF9"
                for d in weekly_52w["weekend_date"]
            ],
            hovertemplate=(
                "<b>%{x|%b %d, %Y}</b><br>"
                "Weekend BO: $%{y:,.0f}<extra></extra>"
            ),
            name="Weekend BO",
        ))

        # 4-week moving average
        if len(weekly_52w) >= 4:
            ma4 = weekly_52w["combined_gross"].rolling(4).mean()
            fig_52w.add_trace(go.Scatter(
                x=weekly_52w["weekend_date"],
                y=ma4,
                name="4-Wk Avg",
                line=dict(color="#e67e22", width=2.5),
                hovertemplate="4-Wk Avg: $%{y:,.0f}<extra></extra>",
            ))

        fig_52w.update_layout(
            **_base_layout(title="Weekly Combined Weekend Box Office — Last 52 Weeks"),
            yaxis_title="Weekend BO ($)",
            yaxis_tickformat="$,.0s",
            height=460,
            legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="left", x=0),
        )
        st.plotly_chart(fig_52w, width="stretch")
        add_export_figure("52-Week Box Office", fig_52w)

        total_52w = weekly_52w["combined_gross"].sum()
        avg_52w = weekly_52w["combined_gross"].mean()
        max_wk = weekly_52w.loc[weekly_52w["combined_gross"].idxmax()]
        max_movie = max_wk.get("no1_movie", "")
        max_date = max_wk["weekend_date"].strftime("%b %d, %Y") if pd.notna(max_wk.get("weekend_date")) else ""
        st.caption(
            f"{len(weekly_52w)} weekends | "
            f"Total: ${total_52w:,.0f} | "
            f"Avg: ${avg_52w:,.0f}/wk | "
            f"Best: ${max_wk['combined_gross']:,.0f} ({max_date}, {max_movie})"
        )

        # Full 52-week data table
        with st.expander("52-Week Data Table"):
            tbl_52w = weekly_52w[["weekend_date", "no1_movie", "combined_gross"]].copy()
            tbl_52w = tbl_52w.sort_values("weekend_date", ascending=False)
            tbl_52w.columns = ["Weekend", "#1 Movie", "Combined BO"]
            tbl_52w["Weekend"] = tbl_52w["Weekend"].dt.strftime("%b %d, %Y")
            tbl_52w["Combined BO"] = tbl_52w["Combined BO"].apply(
                lambda v: f"${v:,.0f}" if pd.notna(v) else "N/A"
            )
            st.dataframe(tbl_52w, width="stretch", height=500, hide_index=True)
            add_export_table("52-Week Box Office", tbl_52w)
    else:
        st.warning(
            "Weekly box office data unavailable. The Numbers may be temporarily slow. "
            "Data will auto-retry on next page load."
        )

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 2B: WEEKLY BOX OFFICE — CY vs PY TRACKING
    # ══════════════════════════════════════════════════════════════════════
    st.subheader("Weekly Box Office — CY vs PY")

    if not weekly_trend_prior.empty:
        # Build full 52-week comparison using PY as backbone.
        # CY data overlaid for weeks reported so far.
        prior_wk = weekly_trend_prior.head(52).copy()
        prior_wk["week_num"] = range(1, len(prior_wk) + 1)

        current_wk = weekly_trend_current.copy() if not weekly_trend_current.empty else pd.DataFrame()
        if not current_wk.empty:
            current_wk["week_num"] = range(1, len(current_wk) + 1)

        # PY as the 52-week scaffold
        comp_df = prior_wk[["week_num", "weekend_date", "no1_movie", "combined_gross"]].copy()
        comp_df.rename(columns={
            "weekend_date": "py_weekend_date",
            "no1_movie": "py_movie",
            "combined_gross": "py_gross",
        }, inplace=True)

        # Merge CY by week_num
        if not current_wk.empty:
            cy_cols = current_wk[["week_num", "weekend_date", "no1_movie", "combined_gross"]].copy()
            cy_cols.rename(columns={
                "weekend_date": "cy_weekend_date",
                "no1_movie": "cy_movie",
                "combined_gross": "cy_gross",
            }, inplace=True)
            comp_df = comp_df.merge(cy_cols, on="week_num", how="left")
        else:
            comp_df["cy_weekend_date"] = pd.NaT
            comp_df["cy_movie"] = None
            comp_df["cy_gross"] = np.nan

        # YoY %
        comp_df["yoy_pct"] = np.where(
            (comp_df["cy_gross"].notna()) & (comp_df["py_gross"] > 0),
            (comp_df["cy_gross"] / comp_df["py_gross"] - 1) * 100,
            np.nan,
        )

        # Display date: CY date where available, else shift PY date forward
        year_offset = current_year - bo_compare_year
        comp_df["display_date"] = comp_df["cy_weekend_date"].fillna(
            comp_df["py_weekend_date"] + pd.DateOffset(years=year_offset)
        )

        n_cy_weeks = int(comp_df["cy_gross"].notna().sum())
        st.caption(
            f"CY = {current_year} | PY = {bo_compare_year} | "
            f"{n_cy_weeks} of 52 weeks reported"
        )

        # Dual-axis chart: bars = CY BO, line = PY BO, line = YoY %
        from plotly.subplots import make_subplots
        fig_yoy = make_subplots(specs=[[{"secondary_y": True}]])

        cy_mask = comp_df["cy_gross"].notna()
        fig_yoy.add_trace(
            go.Bar(
                x=comp_df.loc[cy_mask, "display_date"],
                y=comp_df.loc[cy_mask, "cy_gross"],
                name="CY Weekend BO",
                marker_color="#1565C0",
                hovertemplate="<b>%{x|%b %d, %Y}</b><br>CY: $%{y:,.0f}<extra></extra>",
            ),
            secondary_y=False,
        )
        fig_yoy.add_trace(
            go.Scatter(
                x=comp_df["display_date"],
                y=comp_df["py_gross"],
                name="PY Weekend BO",
                line=dict(color="#e67e22", width=2, dash="dot"),
                hovertemplate="PY: $%{y:,.0f}<extra></extra>",
            ),
            secondary_y=False,
        )
        fig_yoy.add_trace(
            go.Scatter(
                x=comp_df.loc[cy_mask, "display_date"],
                y=comp_df.loc[cy_mask, "yoy_pct"],
                name="YoY %",
                line=dict(color="#2ecc71", width=2.5),
                hovertemplate="YoY: %{y:+.1f}%<extra></extra>",
            ),
            secondary_y=True,
        )
        # Vertical divider between reported and upcoming
        if 0 < n_cy_weeks < len(comp_df):
            last_reported = comp_df.loc[cy_mask, "display_date"].iloc[-1]
            fig_yoy.add_vline(
                x=last_reported.timestamp() * 1000,
                line_color="rgba(0,0,0,0.3)", line_width=1, line_dash="dash",
                annotation_text="Latest", annotation_position="top",
            )
        fig_yoy.add_hline(y=0, line_color="rgba(0,0,0,0.2)", line_width=1, secondary_y=True)
        fig_yoy.update_layout(
            **_base_layout(title=f"Weekly BO — CY vs PY (Full Year)"),
            height=460,
            legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="left", x=0),
        )
        fig_yoy.update_yaxes(title_text="Weekend BO ($)", tickformat="$,.0s", secondary_y=False)
        fig_yoy.update_yaxes(title_text="YoY %", tickformat="+.0f%", secondary_y=True)
        st.plotly_chart(fig_yoy, width="stretch")

        # Weekly detail table — all 52 weeks
        st.markdown("**Week-by-Week Detail (52 Weeks)**")
        detail_rows = []
        for _, row in comp_df.iterrows():
            has_cy = pd.notna(row.get("cy_gross"))
            detail_rows.append({
                "Wk": int(row["week_num"]),
                "Weekend": row["display_date"].strftime("%b %d, %Y") if pd.notna(row.get("display_date")) else "",
                "CY BO": f"${row['cy_gross']:,.0f}" if has_cy else "",
                "PY BO": f"${row['py_gross']:,.0f}" if row["py_gross"] else "N/A",
                "YoY %": round(row["yoy_pct"], 1) if pd.notna(row.get("yoy_pct")) else None,
                "#1 (CY)": row.get("cy_movie", "") if has_cy else "",
                "#1 (PY)": row.get("py_movie", ""),
            })

        if detail_rows:
            detail_df = pd.DataFrame(detail_rows)

            def _color_yoy(val):
                if isinstance(val, (int, float)):
                    return f"color: {'#2ecc71' if val >= 0 else '#e74c3c'}; font-weight: bold"
                return ""

            def _dim_future(row):
                """Gray out rows where CY data hasn't arrived yet."""
                if row["CY BO"] == "":
                    return ["color: #aaa"] * len(row)
                return [""] * len(row)

            styled = (
                detail_df.style
                    .apply(_dim_future, axis=1)
                    .map(_color_yoy, subset=["YoY %"])
                    .format({"YoY %": lambda v: f"{v:+.1f}%" if v is not None and pd.notna(v) else ""})
            )
            st.dataframe(styled, width="stretch", height=700, hide_index=True)

    elif not weekly_trend_current.empty:
        st.info(f"PY ({bo_compare_year}) data not available.")
    else:
        st.warning("Weekly trend data unavailable.")

    st.divider()

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 3: THIS WEEK'S TOP MOVIES
    # ══════════════════════════════════════════════════════════════════════
    st.subheader("This Week's Top Movies")

    if not weekly_chart_df.empty:
        display_df = weekly_chart_df.copy()
        # Format money columns
        for col in ["Gross", "Per Theater", "Total Gross"]:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(
                    lambda v: f"${v:,.0f}" if pd.notna(v) and v else "N/A"
                )
        if "Theaters" in display_df.columns:
            display_df["Theaters"] = display_df["Theaters"].apply(
                lambda v: f"{v:,}" if pd.notna(v) and v else "N/A"
            )
        if "New" in display_df.columns:
            display_df["New"] = display_df["New"].apply(lambda v: "🆕" if v else "")
        display_cols = [c for c in ["Rank", "New", "Title", "Distributor", "Gross",
                                     "% vs LW", "Theaters", "Per Theater", "Total Gross"]
                        if c in display_df.columns]
        st.dataframe(display_df[display_cols], width="stretch", height=500, hide_index=True)

        # ── Holdover performance ─────────────────────────────────────────
        holdovers = weekly_chart_df[~weekly_chart_df.get("New", pd.Series([False]*len(weekly_chart_df)))].copy()
        new_releases = weekly_chart_df[weekly_chart_df.get("New", pd.Series([False]*len(weekly_chart_df)))].copy()

        col_new, col_hold = st.columns(2)
        with col_new:
            if not new_releases.empty:
                st.markdown("**New Openers This Weekend**")
                for _, row in new_releases.head(5).iterrows():
                    gross = f"${row['Gross']:,.0f}" if pd.notna(row.get('Gross')) and row['Gross'] else "N/A"
                    thtr = f"{row['Theaters']:,}" if pd.notna(row.get('Theaters')) and row['Theaters'] else "N/A"
                    st.markdown(f"- **{row['Title']}** ({row.get('Distributor','')}) — {gross} in {thtr} theaters")

        with col_hold:
            if not holdovers.empty:
                st.markdown("**Top Holdovers**")
                for _, row in holdovers.head(5).iterrows():
                    gross = f"${row['Gross']:,.0f}" if pd.notna(row.get('Gross')) and row['Gross'] else "N/A"
                    pct = row.get('% vs LW', '')
                    st.markdown(f"- **{row['Title']}** — {gross} ({pct} vs LW)")

        # ── Distributor market share ──────────────────────────────────────
        if "Distributor" in weekly_chart_df.columns and "Gross" in weekly_chart_df.columns:
            dist_share = weekly_chart_df.groupby("Distributor")["Gross"].sum().sort_values(ascending=False)
            dist_share = dist_share[dist_share > 0].head(10)
            if not dist_share.empty:
                st.subheader("Distributor Market Share")
                st.caption(
                    "Left: this weekend's box office split by distributor (top 10). "
                    "Right: 5-year annual gross by top 6 studios (remaining grouped as 'Other')."
                )

                col_pie, col_bar5 = st.columns(2)

                # Pie chart — this weekend
                with col_pie:
                    st.markdown("**This Weekend — Top 10 Distributors**")
                    fig_pie = go.Figure(go.Pie(
                        labels=dist_share.index,
                        values=dist_share.values,
                        textinfo="percent",
                        textfont=dict(size=11),
                        hovertemplate="<b>%{label}</b><br>$%{value:,.0f}<br>%{percent}<extra></extra>",
                        marker=dict(colors=[
                            "#1565C0", "#e67e22", "#2ecc71", "#e74c3c", "#9b59b6",
                            "#f39c12", "#1abc9c", "#3498db", "#c0392b", "#7f8c8d",
                        ]),
                    ))
                    fig_pie.update_layout(
                        **_base_layout(title="Weekend BO by Distributor"),
                        height=460,
                        showlegend=True,
                        legend=dict(
                            orientation="v", yanchor="middle", y=0.5,
                            xanchor="left", x=1.02, font=dict(size=10),
                        ),
                    )
                    st.plotly_chart(fig_pie, width="stretch")

                # 5-year stacked bar chart
                with col_bar5:
                    st.markdown("**Annual Market Share — Top 6 Distributors**")
                    with st.spinner("Fetching distributor history…"):
                        dist_hist = get_distributor_share_multi_year(
                            list(range(current_year - 4, current_year + 1))
                        )
                    if not dist_hist.empty:
                        # Get top 6 distributors by total gross across all years
                        top_dist = (
                            dist_hist.groupby("Distributor")["Total Gross"]
                            .sum().nlargest(6).index.tolist()
                        )
                        # Group remaining as "Other"
                        plot_df = dist_hist.copy()
                        plot_df["Distributor"] = plot_df["Distributor"].where(
                            plot_df["Distributor"].isin(top_dist), "Other"
                        )
                        pivot = plot_df.groupby(["Year", "Distributor"])["Total Gross"].sum().unstack(fill_value=0)
                        # Sort columns by total
                        pivot = pivot[pivot.sum().sort_values(ascending=False).index]

                        dist_colors = [
                            "#1565C0", "#e67e22", "#2ecc71", "#e74c3c",
                            "#9b59b6", "#f39c12", "#95a5a6",
                        ]
                        fig_bar5 = go.Figure()
                        for i, col in enumerate(pivot.columns):
                            fig_bar5.add_trace(go.Bar(
                                x=pivot.index.astype(str),
                                y=pivot[col],
                                name=col,
                                marker_color=dist_colors[i % len(dist_colors)],
                                hovertemplate=f"<b>{col}</b><br>" + "%{x}: $%{y:,.0f}<extra></extra>",
                            ))
                        fig_bar5.update_layout(
                            **_base_layout(title="Annual Gross by Distributor"),
                            barmode="stack",
                            yaxis_title="Total Gross ($)",
                            yaxis_tickformat="$,.0s",
                            height=460,
                            legend=dict(
                                orientation="h", yanchor="top", y=-0.13,
                                xanchor="left", x=0, font=dict(size=11),
                            ),
                        )
                        st.plotly_chart(fig_bar5, width="stretch")
                    else:
                        st.info("Historical distributor data unavailable.")
    else:
        st.warning("Weekly box office chart data unavailable.")

    st.divider()

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 4: ANNUAL BOX OFFICE COMPARISON
    # ══════════════════════════════════════════════════════════════════════
    st.subheader("Annual Domestic Box Office")
    st.caption("Total domestic BO revenue (bars) and tickets sold (line) from 2010–present")

    if not annual_df.empty:
        # Filter to last 15 years
        annual_recent = annual_df[annual_df["Year"] >= 2010].sort_values("Year")
        if not annual_recent.empty:
            st.plotly_chart(
                annual_bo_chart(annual_recent, title="Annual Domestic Box Office"),
                width="stretch",
            )
    else:
        st.warning("Annual box office data unavailable.")

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 5: YTD PACING vs PRIOR YEARS
    # ══════════════════════════════════════════════════════════════════════
    st.subheader("YTD Box Office Pacing")
    st.caption("Cumulative weekend BO by week number — compare recovery trajectory")

    years_to_compare = list(dict.fromkeys([
        current_year, current_year - 1, current_year - 2, 2019,
    ]))
    years_data = {}
    for yr in years_to_compare:
        if yr == current_year:
            years_data[yr] = weekly_trend_current
        elif yr == bo_compare_year:
            years_data[yr] = weekly_trend_prior
        else:
            with st.spinner(f"Fetching {yr} data…"):
                years_data[yr] = get_weekly_box_office_trend(yr)

    non_empty = {yr: df for yr, df in years_data.items() if not df.empty}
    if non_empty:
        st.plotly_chart(
            ytd_pacing_chart(non_empty, title="YTD Cumulative Weekend BO"),
            width="stretch",
        )
    else:
        st.warning("Insufficient data for YTD pacing comparison.")

    st.divider()

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 6: RELEASE CALENDAR
    # ══════════════════════════════════════════════════════════════════════
    st.subheader("Upcoming Release Calendar")
    st.caption("Major releases from The Numbers release schedule")

    if not release_df.empty:
        # Filter to future dates and major distributors
        today = pd.Timestamp.now().normalize()
        upcoming = release_df[release_df["Date"] >= today].copy()
        major_distributors = [
            "Walt Disney", "Disney", "Warner Bros", "Universal", "Sony",
            "Paramount", "Lionsgate", "20th Century", "Columbia",
            "Marvel", "Pixar", "Searchlight", "Focus", "A24",
        ]

        if not upcoming.empty:
            upcoming["Date"] = upcoming["Date"].dt.strftime("%b %d, %Y")
            upcoming["Studio"] = upcoming["Distributor"].apply(
                lambda d: "Major" if any(m.lower() in d.lower() for m in major_distributors) else ""
            )
            display_cols = ["Date", "Studio", "Movie", "Distributor"]
            st.dataframe(upcoming[display_cols].head(50), width="stretch", height=400)
            st.caption("Studio = 'Major' indicates a major studio release")
        else:
            st.info("No upcoming releases found in the schedule.")
    else:
        st.warning("Release schedule data unavailable.")

    st.divider()

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 7: FRANCHISE TRACKER
    # ══════════════════════════════════════════════════════════════════════
    st.subheader("Franchise Box Office Tracker")
    st.caption("All-time top franchises by domestic box office — data from The Numbers")

    with st.spinner("Fetching franchise data…"):
        franchise_df = get_franchise_box_office()

    if not franchise_df.empty and "Domestic BO" in franchise_df.columns:
        top_n = st.slider("Top N Franchises", 10, 40, 20, key="franchise_n")
        top_fran = franchise_df.head(top_n).copy()
        top_fran = top_fran.sort_values("Domestic BO", ascending=True)

        # Determine active vs dormant (last release within 3 years)
        current_yr = pd.Timestamp.now().year
        if "Last Year" in top_fran.columns:
            top_fran["Status"] = top_fran["Last Year"].apply(
                lambda y: "Active" if pd.notna(y) and y >= current_yr - 3 else "Dormant"
            )
            colors = top_fran["Status"].map({"Active": "#2ecc71", "Dormant": "#95a5a6"}).tolist()
        else:
            colors = "#003087"

        fig_fran = go.Figure(go.Bar(
            y=top_fran["Franchise"],
            x=top_fran["Domestic BO"],
            orientation="h",
            marker_color=colors,
            hovertemplate="<b>%{y}</b><br>$%{x:,.0f}<extra></extra>",
            text=[f"${v/1e9:.1f}B" if v >= 1e9 else f"${v/1e6:.0f}M"
                  for v in top_fran["Domestic BO"]],
            textposition="outside",
            textfont=dict(size=9),
        ))
        fig_fran.update_layout(
            **_base_layout(title=f"Top {top_n} Movie Franchises — All-Time Domestic BO"),
            xaxis_title="Domestic Box Office ($)",
            xaxis_tickformat="$,.0s",
            height=max(500, top_n * 28),
        )
        st.plotly_chart(fig_fran, width="stretch")
        add_export_figure("Top Franchises - Domestic BO", fig_fran)

        if "Last Year" in top_fran.columns:
            st.caption("Green = active franchise (release within last 3 years) | Gray = dormant")

        # Franchise comparison table
        with st.expander("Franchise Comparison Table"):
            table_fran = franchise_df.head(top_n).copy()
            if "Domestic BO" in table_fran.columns:
                table_fran["Avg BO per Movie"] = (
                    table_fran["Domestic BO"] / table_fran["Movies"].replace(0, pd.NA)
                ).round(0)
            display_cols = [c for c in ["Franchise", "Movies", "Domestic BO", "Worldwide BO",
                                         "Avg BO per Movie", "First Year", "Last Year"]
                           if c in table_fran.columns]
            st.dataframe(
                table_fran[display_cols].style.format({
                    "Domestic BO": lambda v: f"${v:,.0f}" if pd.notna(v) else "N/A",
                    "Worldwide BO": lambda v: f"${v:,.0f}" if pd.notna(v) else "N/A",
                    "Avg BO per Movie": lambda v: f"${v:,.0f}" if pd.notna(v) else "N/A",
                }),
                width="stretch", height=500,
            )
            add_export_table("Franchise Comparison", table_fran[display_cols])

        # Sequels vs Originals analysis
        if "Movies" in franchise_df.columns and "Domestic BO" in franchise_df.columns:
            with st.expander("Franchise Share of Total Box Office"):
                # Calculate total franchise BO and compare to annual BO
                total_franchise_bo = franchise_df["Domestic BO"].sum()
                try:
                    annual_df = get_annual_box_office()
                    if not annual_df.empty:
                        total_cols = [c for c in annual_df.columns if "total" in c.lower() or "gross" in c.lower() or "box" in c.lower()]
                        if total_cols:
                            all_time_bo = annual_df[total_cols[0]].sum()
                            franchise_share = (total_franchise_bo / all_time_bo * 100) if all_time_bo > 0 else 0
                            st.metric(
                                "Franchise Share of All-Time Domestic BO",
                                f"{franchise_share:.1f}%",
                            )
                            st.caption(
                                f"The top {len(franchise_df)} franchises account for "
                                f"${total_franchise_bo/1e9:.1f}B of total domestic BO. "
                                "Franchise films increasingly dominate the box office."
                            )
                except Exception:
                    pass
    else:
        st.info("Franchise data not available.")

    st.divider()

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 7B: STREAMING WINDOW ANALYSIS
    # ══════════════════════════════════════════════════════════════════════
    st.subheader("Theatrical-to-Streaming Window Analysis")
    st.caption("Days between theatrical release and streaming debut — curated dataset, last updated Feb 2026")

    STREAMING_WINDOWS = [
        {"title": "Avengers: Endgame", "studio": "Disney", "theatrical": "2019-04-26", "streaming": "2019-11-12", "window_days": 200, "domestic_bo": 858},
        {"title": "Spider-Man: No Way Home", "studio": "Sony", "theatrical": "2021-12-17", "streaming": "2022-07-15", "window_days": 210, "domestic_bo": 805},
        {"title": "Top Gun: Maverick", "studio": "Paramount", "theatrical": "2022-05-27", "streaming": "2022-12-22", "window_days": 209, "domestic_bo": 719},
        {"title": "Barbie", "studio": "WBD", "theatrical": "2023-07-21", "streaming": "2023-09-12", "window_days": 53, "domestic_bo": 636},
        {"title": "The Super Mario Bros.", "studio": "Universal", "theatrical": "2023-04-05", "streaming": "2023-08-03", "window_days": 120, "domestic_bo": 575},
        {"title": "Inside Out 2", "studio": "Disney", "theatrical": "2024-06-14", "streaming": "2024-09-25", "window_days": 103, "domestic_bo": 653},
        {"title": "Deadpool & Wolverine", "studio": "Disney", "theatrical": "2024-07-26", "streaming": "2024-10-01", "window_days": 67, "domestic_bo": 637},
        {"title": "Oppenheimer", "studio": "Universal", "theatrical": "2023-07-21", "streaming": "2023-11-21", "window_days": 123, "domestic_bo": 326},
        {"title": "Dune: Part Two", "studio": "WBD", "theatrical": "2024-03-01", "streaming": "2024-05-21", "window_days": 81, "domestic_bo": 282},
        {"title": "Wicked", "studio": "Universal", "theatrical": "2024-11-22", "streaming": "2025-02-25", "window_days": 95, "domestic_bo": 467},
        {"title": "Moana 2", "studio": "Disney", "theatrical": "2024-11-27", "streaming": "2025-03-19", "window_days": 112, "domestic_bo": 449},
        {"title": "Guardians of Galaxy 3", "studio": "Disney", "theatrical": "2023-05-05", "streaming": "2023-08-02", "window_days": 89, "domestic_bo": 359},
        {"title": "The Batman", "studio": "WBD", "theatrical": "2022-03-04", "streaming": "2022-04-19", "window_days": 46, "domestic_bo": 369},
        {"title": "Black Panther: Wakanda", "studio": "Disney", "theatrical": "2022-11-11", "streaming": "2023-02-01", "window_days": 82, "domestic_bo": 181},
        {"title": "Avatar: Way of Water", "studio": "Disney", "theatrical": "2022-12-16", "streaming": "2023-06-07", "window_days": 173, "domestic_bo": 684},
        {"title": "Tenet", "studio": "WBD", "theatrical": "2020-09-03", "streaming": "2020-12-15", "window_days": 103, "domestic_bo": 58},
        {"title": "No Time to Die", "studio": "Universal", "theatrical": "2021-10-08", "streaming": "2021-12-20", "window_days": 73, "domestic_bo": 161},
        {"title": "Godzilla x Kong", "studio": "WBD", "theatrical": "2024-03-29", "streaming": "2024-06-11", "window_days": 74, "domestic_bo": 196},
        {"title": "Despicable Me 4", "studio": "Universal", "theatrical": "2024-07-03", "streaming": "2024-09-24", "window_days": 83, "domestic_bo": 361},
        {"title": "Kingdom of Planet of Apes", "studio": "Disney", "theatrical": "2024-05-10", "streaming": "2024-08-02", "window_days": 84, "domestic_bo": 172},
        {"title": "Beetlejuice Beetlejuice", "studio": "WBD", "theatrical": "2024-09-06", "streaming": "2024-11-06", "window_days": 61, "domestic_bo": 294},
        {"title": "Wonka", "studio": "WBD", "theatrical": "2023-12-15", "streaming": "2024-02-27", "window_days": 74, "domestic_bo": 218},
        {"title": "The Wild Robot", "studio": "Universal", "theatrical": "2024-09-27", "streaming": "2024-12-03", "window_days": 67, "domestic_bo": 144},
    ]

    sw_df = pd.DataFrame(STREAMING_WINDOWS)
    sw_df["theatrical"] = pd.to_datetime(sw_df["theatrical"])
    sw_df = sw_df.sort_values("theatrical")

    # Scatter: window days over time, colored by studio
    studio_colors = {
        "Disney": "#003087", "WBD": "#7B2D8E", "Universal": "#e67e22",
        "Sony": "#e74c3c", "Paramount": "#1ABC9C", "Lionsgate": "#F39C12",
    }

    fig_sw = go.Figure()
    for studio in sw_df["studio"].unique():
        sdf = sw_df[sw_df["studio"] == studio]
        fig_sw.add_trace(go.Scatter(
            x=sdf["theatrical"], y=sdf["window_days"],
            name=studio, mode="markers+text",
            marker=dict(size=10, color=studio_colors.get(studio, "#888")),
            text=sdf["title"].apply(lambda t: t[:15]),
            textposition="top center",
            textfont=dict(size=7),
            hovertemplate="<b>%{text}</b><br>Released: %{x|%b %Y}<br>Window: %{y} days<extra></extra>",
            customdata=sdf["title"],
        ))
    fig_sw.update_layout(
        **_base_layout(title="Theatrical-to-Streaming Window (Days)"),
        yaxis_title="Days to Streaming",
        height=450,
        legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="left", x=0),
    )
    st.plotly_chart(fig_sw, width="stretch")
    add_export_figure("Streaming Window Analysis", fig_sw)

    # Average window by studio
    col_sw1, col_sw2 = st.columns(2)
    with col_sw1:
        avg_by_studio = sw_df.groupby("studio")["window_days"].mean().sort_values(ascending=True)
        fig_avg = go.Figure(go.Bar(
            y=avg_by_studio.index,
            x=avg_by_studio.values,
            orientation="h",
            marker_color=[studio_colors.get(s, "#888") for s in avg_by_studio.index],
            text=[f"{v:.0f} days" for v in avg_by_studio.values],
            textposition="outside",
        ))
        fig_avg.update_layout(
            **_base_layout(title="Avg Streaming Window by Studio"),
            xaxis_title="Days", height=350,
        )
        st.plotly_chart(fig_avg, width="stretch")

    with col_sw2:
        # Window vs BO scatter
        fig_corr = go.Figure(go.Scatter(
            x=sw_df["window_days"], y=sw_df["domestic_bo"],
            mode="markers",
            marker=dict(
                size=12,
                color=[studio_colors.get(s, "#888") for s in sw_df["studio"]],
            ),
            text=sw_df["title"],
            hovertemplate="<b>%{text}</b><br>Window: %{x} days<br>BO: $%{y}M<extra></extra>",
        ))
        fig_corr.update_layout(
            **_base_layout(title="Streaming Window vs Domestic BO"),
            xaxis_title="Window (Days)", yaxis_title="Domestic BO ($M)",
            height=350,
        )
        st.plotly_chart(fig_corr, width="stretch")

    st.caption(
        "Shorter windows may reduce theatrical revenue but drive streaming subscriber growth. "
        "Trend: average windows have compressed from 100+ days (2019) to ~70-90 days (2024-25)."
    )

    st.divider()

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 8: CPI MOVIE ADMISSIONS + EMPLOYMENT (FRED)
    # ══════════════════════════════════════════════════════════════════════
    if fred_key_available():
        st.subheader("Admissions Pricing & Employment (FRED)")

        with st.spinner("Fetching FRED data…"):
            ind_1 = get_fred_series(fs["cpi_industry_1"], start=start_date) if fs.get("cpi_industry_1") else pd.Series(dtype=float)
            wages_data = get_fred_series(fs["wages"], start=start_date) if fs.get("wages") else pd.Series(dtype=float)
            ind_emp = get_fred_series(fs["industry_employment"], start=start_date) if fs.get("industry_employment") else pd.Series(dtype=float)

        def yoy(s):
            return s.pct_change(12).dropna() * 100

        col_a, col_b = st.columns(2)
        with col_a:
            if not ind_1.empty:
                yoy_1 = yoy(ind_1)
                if not yoy_1.empty:
                    fig_cpi = go.Figure(go.Scatter(
                        x=yoy_1.index, y=yoy_1.values,
                        name=lbl.get("cpi_label_1", "Movie Admissions"),
                        line=dict(color="#e67e22", width=2.5),
                        fill="tozeroy", fillcolor="rgba(230, 126, 34, 0.1)",
                    ))
                    fig_cpi.add_hline(y=0, line_color="rgba(0,0,0,0.2)", line_width=1)
                    fig_cpi.update_layout(
                        **_base_layout(title=lbl.get("cpi_chart_title", "CPI Movie Admissions (YoY %)")),
                        yaxis_title="YoY %", height=380,
                    )
                    st.plotly_chart(fig_cpi, width="stretch")
                    st.caption(lbl.get("cpi_chart_caption", ""))

        with col_b:
            if not ind_emp.empty:
                fig_emp = go.Figure(go.Scatter(
                    x=ind_emp.index, y=ind_emp.values,
                    name=lbl.get("employment_label", "Employment"),
                    line=dict(color="#3498db", width=2.5),
                    fill="tozeroy", fillcolor="rgba(52, 152, 219, 0.1)",
                ))
                fig_emp.update_layout(
                    **_base_layout(title=lbl.get("employment_chart_title", "Motion Picture Employment")),
                    yaxis_title=lbl.get("employment_y_title", "Thousands"), height=380,
                )
                st.plotly_chart(fig_emp, width="stretch")

    st.divider()

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 8: TRACKED COMPANIES
    # ══════════════════════════════════════════════════════════════════════
    st.subheader("Tracked Companies")
    comp_rows = []
    for ticker, info in COMPANIES.items():
        comp_rows.append({"Ticker": ticker, "Company": info["name"], "Segment": info["segment"]})
    if comp_rows:
        st.dataframe(pd.DataFrame(comp_rows).set_index("Ticker"), width="stretch")

    st.divider()
    st.caption(
        "**Movie Theaters** — Box office data from The Numbers (updated hourly). "
        "FRED data: CPI Movie Admissions, Motion Picture Employment. "
        "Stock prices auto-refresh via yfinance."
    )

elif cfg["name"] == "Gaming":
    # ═══════════════════════════════════════════════════════════════════════
    # GAMING — GGR KPIs
    # ═══════════════════════════════════════════════════════════════════════
    from utils.data_fetchers import (
        get_gambling_revenue_fred, get_state_igaming_revenue,
        get_sports_betting_by_state, get_gaming_kpi_reference,
        get_gaming_company_financials, get_pa_gaming_revenue,
    )
    from utils.charts import ggr_trend_chart, state_ggr_bar_chart
    from plotly.subplots import make_subplots

    COMPANIES = cfg["companies"]
    fs = cfg["fred_series"]
    lbl = cfg["macro_labels"]

    st.header("Gaming Revenue Dashboard")
    st.caption("GGR & revenue data from FRED · State-level data from PlayUSA · Employment & pricing indices")

    # ── Sidebar ───────────────────────────────────────────────────────────
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

    # ── Fetch data ────────────────────────────────────────────────────────
    gambling_rev = pd.Series(dtype=float)
    series_data = {}

    if fred_key_available():
        with st.spinner("Fetching FRED data…"):
            gambling_rev = get_gambling_revenue_fred(start=start_date)
            for key in ["cpi_industry_1", "wages", "industry_employment",
                        "gambling_pce", "amusement_revenue"]:
                sid = fs.get(key)
                if sid:
                    s = get_fred_series(sid, start=start_date, silent=True)
                    if not s.empty:
                        series_data[key] = s

    with st.spinner("Fetching state-level revenue data…"):
        state_rev_df = get_state_igaming_revenue()
        sports_betting_df = get_sports_betting_by_state()

    with st.spinner("Fetching company financials…"):
        company_fin_df = get_gaming_company_financials()

    with st.spinner("Fetching PA gaming revenue…"):
        pa_gaming_df = get_pa_gaming_revenue()

    def yoy_q(s):
        return s.pct_change(4).dropna() * 100

    def yoy(s):
        return s.pct_change(12).dropna() * 100

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 1: GGR SNAPSHOT (metric cards)
    # ══════════════════════════════════════════════════════════════════════
    c1, c2, c3, c4 = st.columns(4)

    if not gambling_rev.empty:
        latest_rev = gambling_rev.iloc[-1]
        c1.metric(
            f"Quarterly Gambling Revenue",
            f"${latest_rev:,.0f}",
        )
        yoy_rev = yoy_q(gambling_rev)
        if not yoy_rev.empty:
            c2.metric(
                f"GGR YoY Change",
                f"{yoy_rev.iloc[-1]:+.1f}%",
                delta=f"{yoy_rev.iloc[-1]:+.1f}%",
                delta_color="normal",
            )

    if "cpi_industry_1" in series_data:
        yoy_ppi = yoy(series_data["cpi_industry_1"])
        if not yoy_ppi.empty:
            c3.metric(
                lbl.get("cpi_industry_1_label", "Casino PPI"),
                f"{yoy_ppi.iloc[-1]:.1f}% YoY",
            )

    if "industry_employment" in series_data:
        emp = series_data["industry_employment"]
        c4.metric(
            lbl.get("employment_label", "Gaming Employment"),
            f"{emp.iloc[-1]:,.0f}K",
            f"{emp.iloc[-1] - emp.iloc[-2]:+,.1f}K MoM" if len(emp) > 1 else None,
        )

    st.divider()

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 2: NATIONAL GAMBLING REVENUE TREND
    # ══════════════════════════════════════════════════════════════════════
    st.subheader("U.S. Gambling Industry Revenue (Quarterly)")
    st.caption(
        lbl.get("gambling_revenue_caption",
                "FRED series tracking total quarterly revenue for the U.S. gambling industry.")
    )

    if not gambling_rev.empty:
        st.plotly_chart(
            ggr_trend_chart(
                gambling_rev,
                title=lbl.get("gambling_revenue_chart_title", "U.S. Gambling Industry Revenue"),
            ),
            width="stretch",
        )

        # Summary stats
        with st.expander("Revenue Details"):
            rev_df = pd.DataFrame({
                "Quarter": [f"{d.year} Q{(d.month-1)//3+1}" for d in gambling_rev.index],
                "Revenue ($)": gambling_rev.values,
            }).tail(12)
            rev_df["Revenue ($)"] = rev_df["Revenue ($)"].apply(lambda v: f"${v:,.0f}")
            st.dataframe(rev_df.set_index("Quarter"), width="stretch")
    else:
        st.warning("Gambling revenue data unavailable. Check FRED API key.")

    # ── Consumer Spending on Gambling (if available) ──────────────────
    if "gambling_pce" in series_data:
        with st.expander("Consumer Spending on Gambling (Real PCE)"):
            pce = series_data["gambling_pce"]
            fig_pce = go.Figure(go.Scatter(
                x=pce.index, y=pce.values,
                name="Real PCE: Gambling",
                line=dict(color="#8E44AD", width=2.5),
                fill="tozeroy", fillcolor="rgba(142, 68, 173, 0.08)",
            ))
            fig_pce.update_layout(
                **_base_layout(title="Real Personal Consumption on Gambling (Billions $)"),
                yaxis_title="Billions $", height=380,
            )
            st.plotly_chart(fig_pce, width="stretch")
            st.caption(
                "FRED DGAMRX1A020NBEA — Real personal consumption expenditures on gambling. "
                "Annual data showing long-term consumer spending trend."
            )

    st.divider()

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 3: STATE-BY-STATE iGAMING & SPORTS BETTING
    # ══════════════════════════════════════════════════════════════════════
    st.subheader("State-by-State iGaming & Sports Betting Revenue")
    st.caption("Data scraped from PlayUSA — may not be available if the source structure changes")

    if not state_rev_df.empty and len(state_rev_df.columns) >= 2:
        # Identify numeric columns for charting
        numeric_cols = [c for c in state_rev_df.columns
                        if c.lower() not in ("state", "launch", "status")
                        and state_rev_df[c].dtype in ("float64", "int64")]

        if numeric_cols:
            tab_labels = numeric_cols[:4]  # Show up to 4 tabs
            tabs = st.tabs(tab_labels)
            for tab, col in zip(tabs, tab_labels):
                with tab:
                    valid = state_rev_df.dropna(subset=[col])
                    if not valid.empty:
                        st.plotly_chart(
                            state_ggr_bar_chart(
                                valid, col,
                                title=f"{col} by State",
                                color="#003087",
                            ),
                            width="stretch",
                        )

        # Full data table
        with st.expander("Full State Revenue Table"):
            st.dataframe(state_rev_df, width="stretch", height=400)
    else:
        st.info(
            "State-level revenue data not available. "
            "This data is scraped from PlayUSA and may occasionally be unavailable."
        )

    st.divider()

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 3B: SPORTS BETTING HANDLE vs HOLD RATE
    # ══════════════════════════════════════════════════════════════════════
    st.subheader("Sports Betting — Handle vs Hold Rate by State")
    st.caption(
        "Handle = total amount wagered | Revenue = operator gross revenue | "
        "Hold % = revenue / handle (the house edge). Data from Legal Sports Report."
    )

    if not sports_betting_df.empty and len(sports_betting_df.columns) >= 2:
        # Find handle, revenue, and hold columns
        sb_cols = sports_betting_df.columns.tolist()
        handle_col = next((c for c in sb_cols if "handle" in c.lower()), None)
        rev_col = next((c for c in sb_cols if "revenue" in c.lower() or "rev" in c.lower()), None)
        hold_col = next((c for c in sb_cols if "hold" in c.lower()), None)
        state_col = next((c for c in sb_cols if c.lower() in ("state", "name")), sb_cols[0])

        if handle_col:
            sb_valid = sports_betting_df.dropna(subset=[handle_col]).copy()
            sb_valid = sb_valid.sort_values(handle_col, ascending=True).tail(20)

            fig_hh = make_subplots(specs=[[{"secondary_y": True}]])
            fig_hh.add_trace(go.Bar(
                y=sb_valid[state_col],
                x=sb_valid[handle_col],
                name="Handle ($)",
                orientation="h",
                marker_color="#003087",
                hovertemplate="<b>%{y}</b><br>Handle: $%{x:,.0f}<extra></extra>",
            ), secondary_y=False)

            if hold_col and hold_col in sb_valid.columns:
                hold_vals = pd.to_numeric(sb_valid[hold_col].astype(str).str.rstrip('%'), errors="coerce")
                fig_hh.add_trace(go.Scatter(
                    y=sb_valid[state_col],
                    x=hold_vals,
                    name="Hold %",
                    mode="markers+text",
                    marker=dict(color="#e74c3c", size=10, symbol="diamond"),
                    text=[f"{v:.1f}%" if pd.notna(v) else "" for v in hold_vals],
                    textposition="middle right",
                    textfont=dict(size=9),
                    hovertemplate="<b>%{y}</b><br>Hold: %{x:.1f}%<extra></extra>",
                ), secondary_y=True)

            fig_hh.update_layout(
                **_base_layout(title="Sports Betting Handle ($) & Hold Rate (%) by State"),
                height=max(450, len(sb_valid) * 25),
                legend=dict(orientation="h", yanchor="top", y=-0.08, xanchor="left", x=0),
            )
            fig_hh.update_xaxes(title_text="Handle ($)", tickformat="$,.0s", secondary_y=False)
            if hold_col:
                fig_hh.update_xaxes(title_text="Hold %", secondary_y=True)
            st.plotly_chart(fig_hh, width="stretch")
            add_export_figure("Sports Betting Handle vs Hold", fig_hh)

            # Summary metrics
            total_handle = sb_valid[handle_col].sum()
            sc1, sc2, sc3 = st.columns(3)
            sc1.metric("Total Handle (Top States)", f"${total_handle/1e9:,.1f}B" if total_handle > 1e6 else f"${total_handle:,.0f}")
            if rev_col and rev_col in sb_valid.columns:
                total_rev = sb_valid[rev_col].sum()
                sc2.metric("Total Revenue", f"${total_rev/1e9:,.1f}B" if total_rev > 1e6 else f"${total_rev:,.0f}")
            if hold_col and hold_col in sb_valid.columns:
                avg_hold = pd.to_numeric(sb_valid[hold_col].astype(str).str.rstrip('%'), errors="coerce").mean()
                sc3.metric("Avg Hold %", f"{avg_hold:.1f}%" if pd.notna(avg_hold) else "N/A")

        # Full sports betting table
        with st.expander("Full Sports Betting Data Table"):
            st.dataframe(sports_betting_df, width="stretch", height=400)
            add_export_table("Sports Betting by State", sports_betting_df)
    else:
        st.info("Sports betting data not available. The data source may be temporarily unavailable.")

    st.divider()

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 3C: iGAMING PENETRATION BY STATE
    # ══════════════════════════════════════════════════════════════════════
    st.subheader("iGaming Revenue per Capita by State")
    st.caption(
        "iGaming revenue divided by adult (18+) population — a measure of market maturity. "
        "Higher penetration = more established online gambling market."
    )

    # Census 2024 estimates: 18+ population by iGaming-legal state (thousands)
    STATE_ADULT_POP = {
        "New Jersey": 7_340, "Pennsylvania": 10_430, "Michigan": 7_920,
        "Connecticut": 2_920, "West Virginia": 1_420, "Delaware": 800,
        "Rhode Island": 880, "New York": 16_180, "Illinois": 10_080,
        "Nevada": 2_500, "Indiana": 5_350, "Iowa": 2_450,
        "Colorado": 4_650, "Virginia": 6_870, "Arizona": 5_850,
        "Ohio": 9_400, "Maryland": 4_870, "Louisiana": 3_660,
        "Tennessee": 5_550, "Kansas": 2_280, "Massachusetts": 5_730,
        "Kentucky": 3_580, "North Carolina": 8_480, "Maine": 1_130,
        "Vermont": 530, "Oregon": 3_360, "Washington": 6_190,
    }

    if not state_rev_df.empty:
        rev_numeric = [c for c in state_rev_df.columns
                       if c.lower() not in ("state", "launch", "status")
                       and state_rev_df[c].dtype in ("float64", "int64")]

        if rev_numeric:
            rev_col_name = rev_numeric[0]  # Use first revenue column
            penetration_rows = []
            state_col_name = "State" if "State" in state_rev_df.columns else state_rev_df.columns[0]

            for _, row in state_rev_df.iterrows():
                state_name = str(row[state_col_name]).strip()
                rev_val = row[rev_col_name]
                adult_pop = STATE_ADULT_POP.get(state_name)
                if pd.notna(rev_val) and adult_pop and adult_pop > 0 and rev_val > 0:
                    penetration_rows.append({
                        "State": state_name,
                        "Revenue": rev_val,
                        "Adult Pop (K)": adult_pop,
                        "Revenue per Capita": rev_val / (adult_pop * 1000),
                    })

            if penetration_rows:
                pen_df = pd.DataFrame(penetration_rows).sort_values("Revenue per Capita", ascending=True)

                fig_pen = go.Figure(go.Bar(
                    y=pen_df["State"],
                    x=pen_df["Revenue per Capita"],
                    orientation="h",
                    marker_color="#00A651",
                    hovertemplate="<b>%{y}</b><br>$%{x:,.0f} per adult<extra></extra>",
                    text=[f"${v:,.0f}" for v in pen_df["Revenue per Capita"]],
                    textposition="outside",
                    textfont=dict(size=10),
                ))
                fig_pen.update_layout(
                    **_base_layout(title=f"iGaming {rev_col_name} per Adult Capita by State"),
                    xaxis_title="Revenue per Capita ($)",
                    xaxis_tickformat="$,.0f",
                    height=max(400, len(pen_df) * 30),
                )
                st.plotly_chart(fig_pen, width="stretch")
                add_export_figure("iGaming Penetration per Capita", fig_pen)
            else:
                st.info("Could not compute penetration — state names may not match Census data.")
        else:
            st.info("No numeric revenue columns found in state data.")
    else:
        st.info("iGaming state revenue data not available.")

    st.divider()

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 4: CASINO HOTELS GAMING RECEIPTS PPI
    # ══════════════════════════════════════════════════════════════════════
    if "cpi_industry_1" in series_data:
        st.subheader(lbl.get("cpi_chart_title", "Casino Hotels Gaming Receipts PPI (YoY %)"))
        st.caption(lbl.get("cpi_chart_caption", ""))

        ppi_s = series_data["cpi_industry_1"]
        yoy_ppi = yoy(ppi_s)
        if not yoy_ppi.empty:
            fig_ppi = go.Figure(go.Scatter(
                x=yoy_ppi.index, y=yoy_ppi.values,
                name=lbl.get("cpi_label_1", "Casino PPI"),
                line=dict(color="#C0392B", width=2.5),
                fill="tozeroy", fillcolor="rgba(192, 57, 43, 0.1)",
            ))
            fig_ppi.add_hline(y=0, line_color="rgba(0,0,0,0.3)", line_width=1)
            fig_ppi.update_layout(
                **_base_layout(title=lbl.get("cpi_chart_title", "Casino PPI (YoY %)")),
                yaxis_title="YoY %", height=380,
            )
            st.plotly_chart(fig_ppi, width="stretch")

            with st.expander("Show Absolute Index Level"):
                fig_abs = go.Figure(go.Scatter(
                    x=ppi_s.index, y=ppi_s.values,
                    name=lbl.get("cpi_label_1", "Casino PPI"),
                    line=dict(color="#C0392B", width=2),
                ))
                fig_abs.update_layout(
                    **_base_layout(title=f"{lbl.get('cpi_label_1', 'Casino PPI')} — Index Level"),
                    yaxis_title="Index", height=340,
                )
                st.plotly_chart(fig_abs, width="stretch")

    st.divider()

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 5: EMPLOYMENT & WAGES
    # ══════════════════════════════════════════════════════════════════════
    st.subheader(lbl.get("employment_section_title", "Labor Market"))
    st.caption(lbl.get("employment_caption", ""))

    col_w, col_e = st.columns(2)
    with col_w:
        if "wages" in series_data:
            wages_s = series_data["wages"]
            yoy_w = yoy(wages_s)
            if not yoy_w.empty:
                fig_w = go.Figure(go.Scatter(
                    x=yoy_w.index, y=yoy_w.values,
                    name=lbl.get("wages_label", "Wages"),
                    line=dict(color="#2ecc71", width=2.5),
                    fill="tozeroy", fillcolor="rgba(46, 204, 113, 0.1)",
                ))
                fig_w.add_hline(y=0, line_color="rgba(0,0,0,0.2)", line_width=1)
                fig_w.update_layout(
                    **_base_layout(title=lbl.get("wages_chart_title", "Wages (YoY %)")),
                    yaxis_title="YoY %", height=380,
                )
                st.plotly_chart(fig_w, width="stretch")
        else:
            st.info("Wage data not available.")

    with col_e:
        if "industry_employment" in series_data:
            emp_s = series_data["industry_employment"]
            fig_e = go.Figure(go.Scatter(
                x=emp_s.index, y=emp_s.values,
                name=lbl.get("employment_label", "Employment"),
                line=dict(color="#3498db", width=2.5),
                fill="tozeroy", fillcolor="rgba(52, 152, 219, 0.1)",
            ))
            fig_e.update_layout(
                **_base_layout(title=lbl.get("employment_chart_title", "Gaming Employment")),
                yaxis_title=lbl.get("employment_y_title", "Thousands"), height=380,
            )
            st.plotly_chart(fig_e, width="stretch")
        else:
            st.info("Employment data not available.")

    st.divider()

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 5.5: SPORTS BETTING DATA (Legal Sports Report)
    # ══════════════════════════════════════════════════════════════════════
    if not sports_betting_df.empty and len(sports_betting_df.columns) >= 2:
        st.subheader("State Sports Betting — Handle, Revenue & Hold %")
        st.caption("Data from Legal Sports Report · Handle = total wagered · Hold % = operator win rate")

        sb_numeric_cols = [c for c in sports_betting_df.columns
                          if c.lower() not in ("state", "launch", "status", "year")
                          and sports_betting_df[c].dtype in ("float64", "int64")]
        if sb_numeric_cols:
            sb_tab_labels = sb_numeric_cols[:4]
            sb_tabs = st.tabs(sb_tab_labels)
            for tab, col in zip(sb_tabs, sb_tab_labels):
                with tab:
                    valid = sports_betting_df.dropna(subset=[col])
                    if not valid.empty:
                        st.plotly_chart(
                            state_ggr_bar_chart(
                                valid, col,
                                title=f"Sports Betting: {col} by State",
                                color="#00A651",
                            ),
                            width="stretch",
                        )

        with st.expander("Full Sports Betting Data Table"):
            st.dataframe(sports_betting_df, width="stretch", height=400)
        st.divider()

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 6: COMPANY QUARTERLY FINANCIALS
    # ══════════════════════════════════════════════════════════════════════
    st.subheader("Company Quarterly Financials")
    st.caption(
        "Revenue, EBITDA, and margins for tracked gaming operators · "
        "Data from stockanalysis.com (quarterly earnings)"
    )

    if not company_fin_df.empty:
        fin_tickers = sorted(company_fin_df["Ticker"].unique())

        # ── Revenue comparison chart ────────────────────────────────────
        st.markdown("**Quarterly Revenue Comparison**")
        fig_rev = go.Figure()
        rev_colors = ["#C0392B", "#2C3E50", "#8E44AD", "#1ABC9C", "#00A651", "#F39C12"]
        for i, tkr in enumerate(fin_tickers):
            tkr_df = company_fin_df[company_fin_df["Ticker"] == tkr].copy()
            tkr_df = tkr_df.dropna(subset=["Revenue"]).tail(8)  # Last 8 quarters
            if tkr_df.empty:
                continue
            fig_rev.add_trace(go.Bar(
                x=tkr_df["Quarter"].apply(lambda d: f"{d.year}-Q{(d.month-1)//3+1}") if pd.api.types.is_datetime64_any_dtype(tkr_df["Quarter"]) else tkr_df["Quarter"].astype(str),
                y=tkr_df["Revenue"] / 1e9,
                name=tkr,
                marker_color=rev_colors[i % len(rev_colors)],
                hovertemplate=f"<b>{tkr}</b><br>" + "%{x}: $%{y:.2f}B<extra></extra>",
            ))
        fig_rev.update_layout(
            **_base_layout(title="Quarterly Revenue ($B)"),
            barmode="group",
            yaxis_title="Revenue ($B)",
            yaxis_tickformat="$.2f",
            height=440,
            legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="left", x=0),
        )
        st.plotly_chart(fig_rev, width="stretch")

        # ── EBITDA comparison chart ─────────────────────────────────────
        col_ebitda, col_margin = st.columns(2)
        with col_ebitda:
            st.markdown("**Quarterly EBITDA**")
            fig_ebitda = go.Figure()
            for i, tkr in enumerate(fin_tickers):
                tkr_df = company_fin_df[company_fin_df["Ticker"] == tkr].copy()
                tkr_df = tkr_df.dropna(subset=["EBITDA"]).tail(8)
                if tkr_df.empty:
                    continue
                fig_ebitda.add_trace(go.Bar(
                    x=tkr_df["Quarter"].apply(lambda d: f"{d.year}-Q{(d.month-1)//3+1}") if pd.api.types.is_datetime64_any_dtype(tkr_df["Quarter"]) else tkr_df["Quarter"].astype(str),
                    y=tkr_df["EBITDA"] / 1e6,
                    name=tkr,
                    marker_color=rev_colors[i % len(rev_colors)],
                    hovertemplate=f"<b>{tkr}</b><br>" + "%{x}: $%{y:,.0f}M<extra></extra>",
                ))
            fig_ebitda.update_layout(
                **_base_layout(title="Quarterly EBITDA ($M)"),
                barmode="group",
                yaxis_title="EBITDA ($M)",
                yaxis_tickformat="$,.0f",
                height=400,
                legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="left", x=0),
            )
            st.plotly_chart(fig_ebitda, width="stretch")

        # ── EBITDA Margin trend ─────────────────────────────────────────
        with col_margin:
            st.markdown("**EBITDA Margin Trend**")
            fig_margin = go.Figure()
            for i, tkr in enumerate(fin_tickers):
                tkr_df = company_fin_df[company_fin_df["Ticker"] == tkr].copy()
                tkr_df = tkr_df.dropna(subset=["EBITDA Margin"]).tail(8)
                if tkr_df.empty:
                    continue
                fig_margin.add_trace(go.Scatter(
                    x=tkr_df["Quarter"],
                    y=tkr_df["EBITDA Margin"] * 100 if tkr_df["EBITDA Margin"].max() < 1 else tkr_df["EBITDA Margin"],
                    name=tkr,
                    mode="lines+markers",
                    line=dict(color=rev_colors[i % len(rev_colors)], width=2),
                    hovertemplate=f"<b>{tkr}</b><br>" + "%{x|%b %Y}: %{y:.1f}%<extra></extra>",
                ))
            fig_margin.add_hline(y=0, line_color="rgba(0,0,0,0.2)", line_width=1)
            fig_margin.update_layout(
                **_base_layout(title="EBITDA Margin (%)"),
                yaxis_title="Margin (%)",
                yaxis_tickformat=".0f%",
                height=400,
                legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="left", x=0),
            )
            st.plotly_chart(fig_margin, width="stretch")

        # ── EPS comparison ──────────────────────────────────────────────
        with st.expander("Quarterly EPS (Diluted)"):
            fig_eps = go.Figure()
            for i, tkr in enumerate(fin_tickers):
                tkr_df = company_fin_df[company_fin_df["Ticker"] == tkr].copy()
                tkr_df = tkr_df.dropna(subset=["EPS"]).tail(8)
                if tkr_df.empty:
                    continue
                fig_eps.add_trace(go.Scatter(
                    x=tkr_df["Quarter"],
                    y=tkr_df["EPS"],
                    name=tkr,
                    mode="lines+markers",
                    line=dict(color=rev_colors[i % len(rev_colors)], width=2),
                    hovertemplate=f"<b>{tkr}</b><br>" + "%{x|%b %Y}: $%{y:.2f}<extra></extra>",
                ))
            fig_eps.add_hline(y=0, line_color="rgba(0,0,0,0.3)", line_width=1)
            fig_eps.update_layout(
                **_base_layout(title="Diluted EPS by Quarter"),
                yaxis_title="EPS ($)",
                height=380,
                legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="left", x=0),
            )
            st.plotly_chart(fig_eps, width="stretch")

        # ── Full financials data table ──────────────────────────────────
        with st.expander("Full Financials Data Table"):
            display_fin = company_fin_df.copy()
            display_fin["Quarter"] = display_fin["Quarter"].dt.strftime("%Y-%m-%d")
            for col in ["Revenue", "EBITDA", "Net Income"]:
                if col in display_fin.columns:
                    display_fin[col] = display_fin[col].apply(
                        lambda v: f"${v/1e6:,.0f}M" if pd.notna(v) and v else "N/A"
                    )
            for col in ["EPS"]:
                if col in display_fin.columns:
                    display_fin[col] = display_fin[col].apply(
                        lambda v: f"${v:.2f}" if pd.notna(v) else "N/A"
                    )
            for col in ["EBITDA Margin", "Profit Margin"]:
                if col in display_fin.columns:
                    display_fin[col] = display_fin[col].apply(
                        lambda v: f"{v*100:.1f}%" if pd.notna(v) and abs(v) < 1 else (f"{v:.1f}%" if pd.notna(v) else "N/A")
                    )
            st.dataframe(display_fin, width="stretch", height=500, hide_index=True)
    else:
        st.info(
            "Company financial data not available. "
            "This data is scraped from stockanalysis.com and may occasionally be unavailable."
        )

    st.divider()

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 7: PA GAMING CONTROL BOARD DATA
    # ══════════════════════════════════════════════════════════════════════
    st.subheader("Pennsylvania Gaming Revenue")
    st.caption("Data from the PA Gaming Control Board — the most transparent state gaming regulator")

    if not pa_gaming_df.empty:
        # Identify numeric columns
        pa_numeric = [c for c in pa_gaming_df.columns if pa_gaming_df[c].dtype in ("float64", "int64")]
        pa_text_cols = [c for c in pa_gaming_df.columns if c not in pa_numeric]

        if pa_numeric:
            # Show a bar chart of the first numeric column by the first text column
            label_col = pa_text_cols[0] if pa_text_cols else pa_gaming_df.columns[0]
            value_col = pa_numeric[0]

            fig_pa = go.Figure(go.Bar(
                x=pa_gaming_df[label_col],
                y=pa_gaming_df[value_col],
                marker_color="#003087",
                hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>",
            ))
            fig_pa.update_layout(
                **_base_layout(title=f"PA Gaming — {value_col}"),
                yaxis_title=value_col,
                yaxis_tickformat="$,.0s",
                height=420,
            )
            st.plotly_chart(fig_pa, width="stretch")

            # Show additional numeric columns as tabs if more than one
            if len(pa_numeric) > 1:
                pa_tabs = st.tabs(pa_numeric[:5])
                for tab, col in zip(pa_tabs, pa_numeric[:5]):
                    with tab:
                        fig_tab = go.Figure(go.Bar(
                            x=pa_gaming_df[label_col],
                            y=pa_gaming_df[col],
                            marker_color="#1ABC9C",
                            hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>",
                        ))
                        fig_tab.update_layout(
                            **_base_layout(title=f"PA Gaming — {col}"),
                            yaxis_title=col,
                            yaxis_tickformat="$,.0s",
                            height=400,
                        )
                        st.plotly_chart(fig_tab, width="stretch")

        with st.expander("Full PA Gaming Data Table"):
            st.dataframe(pa_gaming_df, width="stretch", height=400)
    else:
        st.info(
            "PA Gaming Control Board data not available. "
            "The data source may have changed or be temporarily unavailable."
        )

    st.divider()

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 8: KEY KPIs REFERENCE GUIDE
    # ══════════════════════════════════════════════════════════════════════
    st.subheader("Gaming KPI Reference Guide")
    st.caption("Key metrics from earnings reports and state filings — what to track and who reports it")

    kpi_ref = get_gaming_kpi_reference()
    for kpi_name, info in kpi_ref.items():
        with st.expander(f"**{kpi_name}**"):
            st.markdown(f"**Definition:** {info['definition']}")
            st.markdown(f"**Who reports:** {info['who_reports']}")
            st.markdown(f"**Frequency:** {info['frequency']}")
            st.markdown(f"**Segments:** {info['segments']}")

    st.divider()
    st.subheader("Tracked Companies")
    comp_rows = []
    for ticker, info in COMPANIES.items():
        comp_rows.append({"Ticker": ticker, "Company": info["name"], "Segment": info["segment"]})
    if comp_rows:
        st.dataframe(pd.DataFrame(comp_rows).set_index("Ticker"), width="stretch")

    st.divider()
    st.caption(
        "**Gaming** — National GGR from FRED (REV7132TAXABL144QNSA). "
        "State-level data from PlayUSA & Legal Sports Report. "
        "Company financials from stockanalysis.com. "
        "PA Gaming Control Board revenue data. "
        "Casino Hotels PPI & employment via FRED. "
        "Stock prices auto-refresh via yfinance."
    )

else:
    # ═══════════════════════════════════════════════════════════════════════
    # NON-RESTAURANT INDUSTRY — FRED-BASED KPIs (Paper & Packaging, Leisure, etc.)
    # ═══════════════════════════════════════════════════════════════════════
    industry_name = cfg["name"]
    COMPANIES = cfg["companies"]
    fs = cfg["fred_series"]
    lbl = cfg["macro_labels"]

    # ── Sidebar ───────────────────────────────────────────────────────────
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
        st.warning(
            "FRED API key not configured. KPI charts require a free FRED API key. "
            "See the sidebar for setup instructions."
        )

    # ── Fetch all available FRED series ───────────────────────────────────
    series_data = {}
    series_keys = ["cpi_industry_1", "cpi_industry_2", "industry_kpi",
                   "wages", "industry_employment", "job_openings"]

    fetched_any = False
    if fred_key_available():
        with st.spinner("Fetching FRED data…"):
            for key in series_keys:
                sid = fs.get(key)
                if sid:
                    s = get_fred_series(sid, start=start_date)
                    if not s.empty:
                        series_data[key] = s
                        fetched_any = True

    # ── Helper: compute YoY ───────────────────────────────────────────────
    def yoy(s: pd.Series) -> pd.Series:
        return s.pct_change(12).dropna() * 100

    def color_delta(val):
        if isinstance(val, (int, float)):
            return f"color: {'#e74c3c' if val > 0 else '#2ecc71'}; font-weight: bold"
        return ""

    # ═══════════════════════════════════════════════════════════════════════
    # KPI METRIC CARDS
    # ═══════════════════════════════════════════════════════════════════════
    if fetched_any:
        st.header(f"{industry_name} — Key Performance Indicators")
        st.caption(
            "Data via FRED (Federal Reserve Economic Data). "
            "Indices, producer prices, and employment data updated monthly."
        )

        # Build metric cards from available data
        metric_cols = st.columns(4)
        col_idx = 0

        if "cpi_industry_1" in series_data:
            yoy_1 = yoy(series_data["cpi_industry_1"])
            if not yoy_1.empty:
                metric_cols[col_idx % 4].metric(
                    lbl.get("cpi_industry_1_label", "Industry Index 1"),
                    f"{yoy_1.iloc[-1]:.1f}% YoY",
                    f"{yoy_1.iloc[-1] - yoy_1.iloc[-2]:.2f}pp" if len(yoy_1) > 1 else None,
                )
                col_idx += 1

        if "cpi_industry_2" in series_data and lbl.get("cpi_industry_2_label"):
            yoy_2 = yoy(series_data["cpi_industry_2"])
            if not yoy_2.empty:
                metric_cols[col_idx % 4].metric(
                    lbl.get("cpi_industry_2_label", "Industry Index 2"),
                    f"{yoy_2.iloc[-1]:.1f}% YoY",
                    f"{yoy_2.iloc[-1] - yoy_2.iloc[-2]:.2f}pp" if len(yoy_2) > 1 else None,
                )
                col_idx += 1

        if "industry_kpi" in series_data:
            yoy_kpi = yoy(series_data["industry_kpi"])
            if not yoy_kpi.empty:
                kpi_label = lbl.get("industry_kpi_label", "Industry KPI")
                metric_cols[col_idx % 4].metric(
                    kpi_label,
                    f"{yoy_kpi.iloc[-1]:.1f}% YoY",
                    f"{yoy_kpi.iloc[-1] - yoy_kpi.iloc[-2]:.2f}pp" if len(yoy_kpi) > 1 else None,
                )
                col_idx += 1

        if "industry_employment" in series_data:
            emp = series_data["industry_employment"]
            metric_cols[col_idx % 4].metric(
                lbl.get("employment_label", "Industry Employment"),
                f"{emp.iloc[-1]:,.1f}",
                f"{emp.iloc[-1] - emp.iloc[-2]:+,.1f} MoM" if len(emp) > 1 else None,
            )
            col_idx += 1

        st.divider()

        # ═══════════════════════════════════════════════════════════════════
        # SECTION 1: INDUSTRY PRICING
        # (Skipped for Paper & Packaging — shown on Input Costs page instead)
        # ═══════════════════════════════════════════════════════════════════
        if industry_name == "Paper & Packaging":
            pass  # Industry pricing charts moved to Input Costs page
        elif True:
            st.header(lbl.get("industry_section_title", "Industry Pricing"))

        # ── Industry KPI series (e.g. PPI Corrugated Shipping Containers) ──
        if industry_name != "Paper & Packaging" and "industry_kpi" in series_data:
            kpi_label = lbl.get("industry_kpi_label", "Industry KPI Index")
            kpi_s = series_data["industry_kpi"]
            yoy_kpi = yoy(kpi_s)

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
            st.plotly_chart(fig_kpi, width="stretch")

            # Absolute level in expander
            with st.expander(f"Show {kpi_label} — Absolute Index Level"):
                fig_kpi_abs = go.Figure(go.Scatter(
                    x=kpi_s.index, y=kpi_s.values,
                    name=kpi_label,
                    line=dict(color="#C0392B", width=2),
                ))
                fig_kpi_abs.update_layout(
                    **_base_layout(title=f"{kpi_label} — Index Level"),
                    yaxis_title="Index", height=340,
                )
                st.plotly_chart(fig_kpi_abs, width="stretch")

        # ── Dual pricing series (e.g. PPI Corrugated Paperboard vs Wood Pulp) ──
        if industry_name != "Paper & Packaging" and "cpi_industry_1" in series_data:
            s1 = series_data["cpi_industry_1"]
            s2 = series_data.get("cpi_industry_2", pd.Series(dtype=float))
            yoy_1 = yoy(s1)
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

            if not s2.empty and label_2:
                yoy_2 = yoy(s2)
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
            st.plotly_chart(fig_cpi, width="stretch")

            # Absolute index levels
            with st.expander("Show Index Level (Absolute)"):
                fig_abs = go.Figure()
                fig_abs.add_trace(go.Scatter(
                    x=s1.index, y=s1.values,
                    name=label_1, line=dict(color="#e67e22", width=2),
                ))
                if not s2.empty and label_2:
                    fig_abs.add_trace(go.Scatter(
                        x=s2.index, y=s2.values,
                        name=label_2, line=dict(color="#3498db", width=2),
                    ))
                fig_abs.update_layout(
                    **_base_layout(title="Index Level"),
                    yaxis_title="Index", height=360,
                    legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="left", x=0),
                )
                st.plotly_chart(fig_abs, width="stretch")

            # Spread chart (if two series)
            if not s2.empty and label_2:
                yoy_s1 = yoy(s1)
                yoy_s2 = yoy(s2)
                spread = (yoy_s1 - yoy_s2).dropna()
                if not spread.empty:
                    st.caption(f"**Spread:** {label_1} minus {label_2} (YoY pp)")
                    fig_spread = go.Figure(go.Bar(
                        x=spread.index, y=spread.values,
                        marker_color=["#e74c3c" if v > 0 else "#2ecc71" for v in spread.values],
                        hovertemplate="%{x|%b %Y}: %{y:.2f}pp<extra></extra>",
                    ))
                    fig_spread.add_hline(y=0, line_color="rgba(0,0,0,0.2)", line_width=1)
                    fig_spread.update_layout(
                        **_base_layout(title=f"{label_1} \u2212 {label_2} (YoY pp Spread)"),
                        yaxis_title="Percentage Points", height=320,
                    )
                    st.plotly_chart(fig_spread, width="stretch")

        st.divider()

        # ═══════════════════════════════════════════════════════════════════
        # SECTION 2: PRODUCTION & LABOR
        # ═══════════════════════════════════════════════════════════════════
        st.header(lbl.get("employment_section_title", "Production & Labor"))
        st.caption(lbl.get("employment_caption", ""))

        col_w, col_e = st.columns(2)

        with col_w:
            if "wages" in series_data:
                wages_s = series_data["wages"]
                yoy_w = yoy(wages_s)
                if not yoy_w.empty:
                    st.subheader(lbl.get("wages_chart_title", "Wages (YoY %)"))
                    fig_w = go.Figure(go.Scatter(
                        x=yoy_w.index, y=yoy_w.values,
                        name=lbl.get("wages_label", "Wages"),
                        line=dict(color="#2ecc71", width=2.5),
                        fill="tozeroy",
                        fillcolor="rgba(46, 204, 113, 0.1)",
                    ))
                    fig_w.add_hline(y=0, line_color="rgba(0,0,0,0.2)", line_width=1)
                    fig_w.update_layout(
                        **_base_layout(title=lbl.get("wages_chart_title", "Wages (YoY %)")),
                        yaxis_title="YoY %", height=380,
                    )
                    st.plotly_chart(fig_w, width="stretch")

                    with st.expander("Show Absolute Wage Level ($/hr)"):
                        fig_wa = go.Figure(go.Scatter(
                            x=wages_s.index, y=wages_s.values,
                            name="Avg Hourly Earnings",
                            line=dict(color="#2ecc71", width=2),
                        ))
                        fig_wa.update_layout(
                            **_base_layout(title=f"{lbl.get('wages_label', 'Wages')} ($/hr)"),
                            yaxis_title="$/hr", height=340,
                        )
                        st.plotly_chart(fig_wa, width="stretch")
            else:
                st.info("Wage data not available for this industry.")

        with col_e:
            if "industry_employment" in series_data:
                emp_s = series_data["industry_employment"]
                y_title = lbl.get("employment_y_title", "Thousands")
                st.subheader(lbl.get("employment_chart_title", "Industry Employment"))
                fig_e = go.Figure(go.Scatter(
                    x=emp_s.index, y=emp_s.values,
                    name=lbl.get("employment_label", "Employment"),
                    line=dict(color="#3498db", width=2.5),
                    fill="tozeroy",
                    fillcolor="rgba(52, 152, 219, 0.1)",
                ))
                fig_e.update_layout(
                    **_base_layout(title=lbl.get("employment_chart_title", "Industry Employment")),
                    yaxis_title=y_title, height=380,
                )
                st.plotly_chart(fig_e, width="stretch")
            else:
                st.info("Employment data not available for this industry.")

        # ── Job Openings (if available) ───────────────────────────────────
        if "job_openings" in series_data and lbl.get("job_openings_chart_title"):
            st.subheader(lbl["job_openings_chart_title"])
            jo_s = series_data["job_openings"]
            fig_jo = go.Figure(go.Scatter(
                x=jo_s.index, y=jo_s.values,
                name="Job Openings",
                line=dict(color="#9b59b6", width=2),
                fill="tozeroy",
                fillcolor="rgba(155, 89, 182, 0.1)",
            ))
            fig_jo.update_layout(
                **_base_layout(title=lbl["job_openings_chart_title"]),
                yaxis_title="Thousands", height=360,
            )
            st.plotly_chart(fig_jo, width="stretch")

        st.divider()

        # ═══════════════════════════════════════════════════════════════════
        # SECTION 2.5: P&P-SPECIFIC — Supply, Demand & Recycled Fiber
        # ═══════════════════════════════════════════════════════════════════
        pp_keys = ["box_production", "box_shipment_value",
                   "box_inventories", "occ_ppi", "recycled_paperboard",
                   "kraft_linerboard", "containerboard_ppi"]
        pp_data = {}
        if fred_key_available() and industry_name == "Paper & Packaging":
            with st.spinner("Fetching additional P&P data…"):
                for key in pp_keys:
                    sid = fs.get(key)
                    if sid:
                        s = get_fred_series(sid, start=start_date, silent=True)
                        if not s.empty:
                            pp_data[key] = s

        if pp_data:
            st.header(lbl.get("supply_demand_section_title", "Supply, Demand & Recycled Fiber"))
            st.caption(lbl.get("supply_demand_caption", ""))

            # ══════════════════════════════════════════════════════════════
            # CONTAINERBOARD & OCC PRICING DASHBOARD (RISI proxy)
            # ══════════════════════════════════════════════════════════════
            pricing_series = {}
            pricing_labels = {
                "containerboard_ppi": ("Corrugated Paperboard (Sub)", "#1565C0"),
                "kraft_linerboard":   ("Kraft Linerboard",            "#E67E22"),
                "recycled_paperboard": ("Recycled Paperboard",        "#2ECC71"),
                "occ_ppi":            ("OCC (Recycled Fiber)",         "#C0392B"),
            }
            for key, (label, _color) in pricing_labels.items():
                if key in pp_data:
                    pricing_series[key] = pp_data[key]

            if pricing_series:
                st.subheader("Containerboard & OCC Pricing (FRED PPI)")
                st.caption(
                    "FRED PPI series as proxies for RISI/Fastmarkets benchmark prices. "
                    "Kraft Linerboard and Recycled Paperboard track containerboard grades; "
                    "OCC tracks the recycled fiber input cost."
                )

                # ── Combined YoY % chart — all pricing series ──────────
                fig_cb = go.Figure()
                for key, series in pricing_series.items():
                    label, color = pricing_labels[key]
                    yoy_s = yoy(series)
                    if not yoy_s.empty:
                        fig_cb.add_trace(go.Scatter(
                            x=yoy_s.index, y=yoy_s.values,
                            name=label,
                            line=dict(color=color, width=2.5),
                            hovertemplate=f"<b>{label}</b><br>" + "%{x|%b %Y}: %{y:.1f}%<extra></extra>",
                        ))
                fig_cb.add_hline(y=0, line_color="rgba(0,0,0,0.3)", line_width=1)
                fig_cb.update_layout(
                    **_base_layout(title="Containerboard & OCC Pricing Indices (YoY %)"),
                    yaxis_title="YoY %", height=440,
                    legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="left", x=0),
                )
                st.plotly_chart(fig_cb, width="stretch")

                # ── Estimated OCC $/ton from PPI calibration ──────────
                if "occ_ppi" in pricing_series:
                    occ_index = pricing_series["occ_ppi"]
                    # Base period: Dec 2003 = 100. Industry reference: OCC #11 ≈ $95/short ton in Dec 2003
                    OCC_BASE_PRICE = 95.0  # $/short ton at index = 100
                    occ_est_price = occ_index * (OCC_BASE_PRICE / 100.0)

                    st.markdown("**Estimated OCC #11 Price ($/short ton)**")
                    st.caption(
                        "Derived from FRED PPI for corrugated recyclable paper (PCU42993042993033). "
                        "Calibrated using Dec 2003 base = $95/ton. This is an estimate — "
                        "actual spot prices from Fastmarkets/RISI may differ."
                    )
                    fig_occ_price = go.Figure()
                    fig_occ_price.add_trace(go.Scatter(
                        x=occ_est_price.index, y=occ_est_price.values,
                        name="OCC #11 Est. $/ton",
                        line=dict(color="#C0392B", width=2.5),
                        fill="tozeroy", fillcolor="rgba(192, 57, 43, 0.06)",
                        hovertemplate="<b>%{x|%b %Y}</b><br>$%{y:.0f}/ton<extra></extra>",
                    ))
                    # Add reference lines for key thresholds
                    fig_occ_price.add_hline(
                        y=100, line_color="rgba(0,0,0,0.15)", line_width=1,
                        line_dash="dash", annotation_text="$100/ton",
                    )
                    latest_price = occ_est_price.iloc[-1]
                    fig_occ_price.update_layout(
                        **_base_layout(title=f"OCC #11 Estimated Price — Latest: ${latest_price:.0f}/ton"),
                        yaxis_title="$/short ton",
                        yaxis_tickprefix="$",
                        height=400,
                    )
                    st.plotly_chart(fig_occ_price, width="stretch")

                # ── Combined Absolute Index chart ──────────────────────
                with st.expander("Show Absolute Index Levels"):
                    fig_cb_abs = go.Figure()
                    for key, series in pricing_series.items():
                        label, color = pricing_labels[key]
                        fig_cb_abs.add_trace(go.Scatter(
                            x=series.index, y=series.values,
                            name=label,
                            line=dict(color=color, width=2),
                            hovertemplate=f"<b>{label}</b><br>" + "%{x|%b %Y}: %{y:.1f}<extra></extra>",
                        ))
                    fig_cb_abs.update_layout(
                        **_base_layout(title="Containerboard & OCC — Index Level"),
                        yaxis_title="Index", height=400,
                        legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="left", x=0),
                    )
                    st.plotly_chart(fig_cb_abs, width="stretch")

                # ── Kraft Linerboard vs Recycled Paperboard ────────────
                if "kraft_linerboard" in pricing_series and "recycled_paperboard" in pricing_series:
                    col_kl, col_rp = st.columns(2)
                    with col_kl:
                        kl = pricing_series["kraft_linerboard"]
                        yoy_kl = yoy(kl)
                        if not yoy_kl.empty:
                            st.markdown("**Kraft Linerboard PPI (YoY %)**")
                            fig_kl = go.Figure(go.Scatter(
                                x=yoy_kl.index, y=yoy_kl.values,
                                name="Kraft Linerboard",
                                line=dict(color="#E67E22", width=2.5),
                                fill="tozeroy", fillcolor="rgba(230, 126, 34, 0.08)",
                            ))
                            fig_kl.add_hline(y=0, line_color="rgba(0,0,0,0.2)", line_width=1)
                            fig_kl.update_layout(
                                **_base_layout(title="PPI Kraft Linerboard (YoY %)"),
                                yaxis_title="YoY %", height=360,
                            )
                            st.plotly_chart(fig_kl, width="stretch")
                            st.caption(
                                "PPI for unbleached kraft packaging paperboard — tracks virgin "
                                "containerboard pricing. Key benchmark for IP, PKG, SW."
                            )

                    with col_rp:
                        rp = pricing_series["recycled_paperboard"]
                        yoy_rp = yoy(rp)
                        if not yoy_rp.empty:
                            st.markdown("**Recycled Paperboard PPI (YoY %)**")
                            fig_rp = go.Figure(go.Scatter(
                                x=yoy_rp.index, y=yoy_rp.values,
                                name="Recycled Paperboard",
                                line=dict(color="#2ECC71", width=2.5),
                                fill="tozeroy", fillcolor="rgba(46, 204, 113, 0.08)",
                            ))
                            fig_rp.add_hline(y=0, line_color="rgba(0,0,0,0.2)", line_width=1)
                            fig_rp.update_layout(
                                **_base_layout(title="PPI Recycled Paperboard (YoY %)"),
                                yaxis_title="YoY %", height=360,
                            )
                            st.plotly_chart(fig_rp, width="stretch")
                            st.caption(
                                "PPI for recycled paperboard — tracks the output price "
                                "for mills using recycled fiber (GEF, CAS.TO, GPK)."
                            )

                    # ── Virgin vs Recycled Spread ──────────────────────
                    yoy_kraft = yoy(pricing_series["kraft_linerboard"])
                    yoy_recycled = yoy(pricing_series["recycled_paperboard"])
                    vr_spread = (yoy_kraft - yoy_recycled).dropna()
                    if not vr_spread.empty:
                        with st.expander("Kraft vs Recycled Paperboard Spread (YoY pp) — Grade Premium"):
                            fig_vr = go.Figure(go.Bar(
                                x=vr_spread.index, y=vr_spread.values,
                                marker_color=["#E67E22" if v > 0 else "#2ECC71" for v in vr_spread.values],
                                hovertemplate="%{x|%b %Y}: %{y:.2f}pp<extra></extra>",
                            ))
                            fig_vr.add_hline(y=0, line_color="rgba(0,0,0,0.2)", line_width=1)
                            fig_vr.update_layout(
                                **_base_layout(title="Kraft Linerboard − Recycled Paperboard (YoY pp)"),
                                yaxis_title="Percentage Points", height=320,
                            )
                            st.plotly_chart(fig_vr, width="stretch")
                            st.caption(
                                "Orange = kraft rising faster (virgin premium widening). "
                                "Green = recycled rising faster (recycled catching up). "
                                "A widening spread favors recycled mills on relative cost."
                            )

                st.divider()

            # ── Row 1: Box Production ──────────────────────────────────
            if "box_production" in pp_data:
                bp = pp_data["box_production"]
                st.subheader(lbl.get("box_production_chart_title", "Box Production Index"))
                fig_bp = go.Figure(go.Scatter(
                    x=bp.index, y=bp.values,
                    name=lbl.get("box_production_label", "Production Index"),
                    line=dict(color="#1565C0", width=2.5),
                    fill="tozeroy", fillcolor="rgba(21, 101, 192, 0.08)",
                ))
                fig_bp.update_layout(
                    **_base_layout(title=lbl.get("box_production_chart_title", "Box Production")),
                    yaxis_title="Index (2017=100)", height=380,
                )
                st.plotly_chart(fig_bp, width="stretch")

            # ── Row 2: Box Shipment Value + Inventories ──────────────────
            col_sv, col_inv = st.columns(2)

            with col_sv:
                if "box_shipment_value" in pp_data:
                    sv = pp_data["box_shipment_value"]
                    st.subheader(lbl.get("box_shipment_chart_title", "Box Shipment Value"))
                    fig_sv = go.Figure(go.Scatter(
                        x=sv.index, y=sv.values,
                        name="Shipment Value ($M)",
                        line=dict(color="#17A589", width=2.5),
                        fill="tozeroy", fillcolor="rgba(23, 165, 137, 0.08)",
                    ))
                    fig_sv.update_layout(
                        **_base_layout(title=lbl.get("box_shipment_chart_title", "Shipments ($M)")),
                        yaxis_title="Millions $", height=380,
                    )
                    st.plotly_chart(fig_sv, width="stretch")

            with col_inv:
                if "box_inventories" in pp_data:
                    inv = pp_data["box_inventories"]
                    st.subheader("Paperboard Container Inventories")
                    fig_inv = go.Figure(go.Scatter(
                        x=inv.index, y=inv.values,
                        name="Inventories ($M)",
                        line=dict(color="#884EA0", width=2.5),
                        fill="tozeroy", fillcolor="rgba(136, 78, 160, 0.08)",
                    ))
                    fig_inv.update_layout(
                        **_base_layout(title="Inventories: Paperboard Container ($M, SA)"),
                        yaxis_title="Millions $", height=380,
                    )
                    st.plotly_chart(fig_inv, width="stretch")

            st.divider()

        # ═══════════════════════════════════════════════════════════════════
        # SECTION 3: DATA TABLE
        # ═══════════════════════════════════════════════════════════════════
        st.header("Latest FRED Data Summary")

        # Combine all series for the summary table
        all_data_keys = list(series_data.keys())
        if pp_data:
            all_data_keys += list(pp_data.keys())

        summary_rows = []
        label_map = {
            "cpi_industry_1": lbl.get("cpi_industry_1_label"),
            "cpi_industry_2": lbl.get("cpi_industry_2_label"),
            "industry_kpi": lbl.get("industry_kpi_label"),
            "wages": lbl.get("wages_label"),
            "industry_employment": lbl.get("employment_label"),
            "job_openings": lbl.get("job_openings_chart_title"),
            "box_production": lbl.get("box_production_label"),
            "box_shipment_value": lbl.get("box_shipment_value_label"),
            "box_new_orders": lbl.get("box_new_orders_label"),
            "box_inventories": lbl.get("box_inventories_label"),
            "capacity_util": lbl.get("capacity_util_label"),
            "occ_ppi": lbl.get("occ_ppi_label"),
            "recycled_paperboard": lbl.get("recycled_paperboard_label"),
            "kraft_linerboard": lbl.get("kraft_linerboard_label"),
            "containerboard_ppi": lbl.get("containerboard_ppi_label"),
            "corrugated_output": lbl.get("corrugated_output_label"),
            "cass_freight": lbl.get("cass_freight_label"),
        }
        combined_data = {**series_data, **pp_data}

        for key in all_data_keys:
            sid = fs.get(key)
            if not sid or key not in combined_data:
                continue
            s = combined_data[key]
            yoy_s = yoy(s)
            last_val = s.iloc[-1]
            last_date = s.index[-1].strftime("%b %Y")
            yoy_val = yoy_s.iloc[-1] if not yoy_s.empty else None

            summary_rows.append({
                "Indicator": label_map.get(key) or sid,
                "FRED ID": sid,
                "Latest Value": f"{last_val:,.2f}",
                "As of": last_date,
                "YoY %": round(yoy_val, 2) if yoy_val is not None else None,
            })

        if summary_rows:
            sdf = pd.DataFrame(summary_rows).set_index("Indicator")
            st.dataframe(
                sdf.style.map(color_delta, subset=["YoY %"])
                    .format({"YoY %": lambda v: f"{v:+.1f}%" if v is not None and pd.notna(v) else "N/A"}),
                width="stretch",
            )

        # ── FRED source list ──────────────────────────────────────────────
        all_keys = series_keys + (pp_keys if pp_data else [])
        used_series = [fs[k] for k in all_keys if fs.get(k) and k in combined_data]
        if used_series:
            st.caption(f"**Sources:** FRED — {', '.join(used_series)}")

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 4: RELEVANT KPIs (qualitative) + COMPANY TABLE
    # ═══════════════════════════════════════════════════════════════════════
    kpi_info = {
        "Paper & Packaging": [
            "Containerboard price realization ($/ton)",
            "Box shipments (MSF or short tons)",
            "Integration rate (%)",
            "OCC (recycled fiber) costs",
            "EBITDA margin by segment",
        ],
        "Gaming": [
            "Gross Gaming Revenue (GGR)",
            "Net Gaming Revenue (NGR)",
            "Handle & Hold % (sports betting)",
            "RevPAR (casino hotels)",
            "iGaming GGR by state",
        ],
        "Movie Theaters": [
            "Domestic box office revenue",
            "Attendance (admissions)",
            "Average Ticket Price (ATP)",
            "Concession spend per head (SPH)",
            "Premium Large Format (PLF) mix %",
        ],
        "Leisure": [
            "Park attendance",
            "Per capita spending (admissions + in-park)",
            "Season pass penetration %",
            "Hotel/resort occupancy & RevPAR",
            "Cruise net yield & onboard revenue",
            "Event revenue & ticket count",
        ],
    }

    # ═══════════════════════════════════════════════════════════════════════
    # INDUSTRY-SPECIFIC FEATURES
    # ═══════════════════════════════════════════════════════════════════════

    if industry_name == "Paper & Packaging":
        # ── P&P: Containerboard Price Increase Tracker ────────────────────
        st.divider()
        st.subheader("Containerboard Price Increase Tracker")
        st.caption(
            "Monitoring RSS feeds (BusinessWire, PR Newswire, Reuters) for containerboard "
            "and corrugated price increase announcements."
        )

        from utils.data_fetchers import get_containerboard_price_increases, get_pp_curtailment_news

        with st.spinner("Scanning news feeds for price increase announcements…"):
            price_inc_df = get_containerboard_price_increases()

        if not price_inc_df.empty:
            st.success(f"Found {len(price_inc_df)} price-related announcement(s)")

            # Timeline scatter
            if "Date" in price_inc_df.columns and price_inc_df["Date"].notna().any():
                fig_pi = go.Figure(go.Scatter(
                    x=price_inc_df["Date"],
                    y=[1] * len(price_inc_df),
                    mode="markers+text",
                    marker=dict(size=14, color="#e74c3c", symbol="triangle-up"),
                    text=price_inc_df["Headline"].str[:40],
                    textposition="top center",
                    textfont=dict(size=8),
                    hovertemplate="<b>%{text}</b><br>%{x|%b %d, %Y}<extra></extra>",
                    customdata=price_inc_df["Headline"],
                ))
                fig_pi.update_layout(
                    **_base_layout(title="Price Increase Announcements Timeline"),
                    yaxis=dict(visible=False),
                    height=250,
                )
                st.plotly_chart(fig_pi, width="stretch")
                add_export_figure("Price Increase Timeline", fig_pi)

            # News table
            display_cols = [c for c in ["Date", "Headline", "Source"] if c in price_inc_df.columns]
            if display_cols:
                show_df = price_inc_df[display_cols].copy()
                if "Date" in show_df.columns:
                    show_df["Date"] = show_df["Date"].dt.strftime("%Y-%m-%d")
                st.dataframe(show_df.head(20), width="stretch", hide_index=True)
                add_export_table("Price Increase Announcements", show_df)
        else:
            st.info(
                "No containerboard price increase announcements found in recent RSS feeds. "
                "This tracker monitors BusinessWire, PR Newswire, and Reuters for keywords like "
                "'containerboard', 'price increase', 'linerboard', 'corrugating medium'."
            )

        # ── P&P: Downtime / Curtailment Calendar ─────────────────────────
        st.divider()
        st.subheader("Mill Downtime & Curtailment Monitor")
        st.caption(
            "Scanning news feeds for mill downtime, curtailment, and capacity reduction announcements."
        )

        with st.spinner("Scanning news feeds for curtailment announcements…"):
            curtail_df = get_pp_curtailment_news()

        if not curtail_df.empty:
            st.warning(f"Found {len(curtail_df)} downtime/curtailment mention(s)")
            display_cols = [c for c in ["Date", "Headline", "Source"] if c in curtail_df.columns]
            if display_cols:
                show_df = curtail_df[display_cols].copy()
                if "Date" in show_df.columns:
                    show_df["Date"] = show_df["Date"].dt.strftime("%Y-%m-%d")
                st.dataframe(show_df.head(15), width="stretch", hide_index=True)
                add_export_table("Curtailment News", show_df)
        else:
            st.info(
                "No recent downtime/curtailment mentions found. "
                "This monitors for keywords like 'downtime', 'curtailment', 'mill closure', "
                "'capacity reduction' in industry news feeds."
            )

    elif industry_name == "Leisure":
        # ── Leisure: Hotel & Cruise Metrics ───────────────────────────────
        st.divider()
        st.subheader("Hotel & Cruise Line Company Metrics")
        st.caption(
            "Quarterly financials for hotel chains (MAR, HLT, H) and cruise lines (RCL, CCL, NCLH) — "
            "revenue and EBITDA comparison. Data from stockanalysis.com."
        )

        from utils.data_fetchers import get_company_quarterly_financials

        # Hotel companies
        hotel_tickers = ["MAR", "HLT", "H", "WH", "CHH"]
        cruise_tickers = ["RCL", "CCL", "NCLH"]

        hotel_tab, cruise_tab = st.tabs(["Hotels", "Cruise Lines"])

        with hotel_tab:
            with st.spinner("Fetching hotel company financials…"):
                hotel_fin_df = get_company_quarterly_financials(hotel_tickers)

            if not hotel_fin_df.empty:
                hotel_colors = ["#003087", "#1ABC9C", "#e67e22", "#8E44AD", "#e74c3c"]
                fin_hotel_tickers = hotel_fin_df["Ticker"].unique()

                fig_hotel_rev = go.Figure()
                for i, tkr in enumerate(fin_hotel_tickers):
                    tkr_df = hotel_fin_df[hotel_fin_df["Ticker"] == tkr].dropna(subset=["Revenue"]).tail(8)
                    if tkr_df.empty:
                        continue
                    fig_hotel_rev.add_trace(go.Bar(
                        x=tkr_df["Quarter"].apply(lambda d: f"{d.year}-Q{(d.month-1)//3+1}") if pd.api.types.is_datetime64_any_dtype(tkr_df["Quarter"]) else tkr_df["Quarter"].astype(str),
                        y=tkr_df["Revenue"] / 1e9,
                        name=tkr,
                        marker_color=hotel_colors[i % len(hotel_colors)],
                    ))
                fig_hotel_rev.update_layout(
                    **_base_layout(title="Hotel Company Quarterly Revenue ($B)"),
                    barmode="group", yaxis_title="Revenue ($B)", height=420,
                    legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="left", x=0),
                )
                st.plotly_chart(fig_hotel_rev, width="stretch")
                add_export_figure("Hotel Quarterly Revenue", fig_hotel_rev)

                with st.expander("Hotel Financials Data"):
                    st.dataframe(hotel_fin_df, width="stretch", height=400)
                    add_export_table("Hotel Financials", hotel_fin_df)
            else:
                st.info("Hotel company financial data not available.")

        with cruise_tab:
            with st.spinner("Fetching cruise line financials…"):
                cruise_fin_df = get_company_quarterly_financials(cruise_tickers)

            if not cruise_fin_df.empty:
                cruise_colors = ["#003087", "#e74c3c", "#2ecc71"]
                fin_cruise_tickers = cruise_fin_df["Ticker"].unique()

                fig_cruise_rev = go.Figure()
                for i, tkr in enumerate(fin_cruise_tickers):
                    tkr_df = cruise_fin_df[cruise_fin_df["Ticker"] == tkr].dropna(subset=["Revenue"]).tail(8)
                    if tkr_df.empty:
                        continue
                    fig_cruise_rev.add_trace(go.Bar(
                        x=tkr_df["Quarter"].apply(lambda d: f"{d.year}-Q{(d.month-1)//3+1}") if pd.api.types.is_datetime64_any_dtype(tkr_df["Quarter"]) else tkr_df["Quarter"].astype(str),
                        y=tkr_df["Revenue"] / 1e9,
                        name=tkr,
                        marker_color=cruise_colors[i % len(cruise_colors)],
                    ))
                fig_cruise_rev.update_layout(
                    **_base_layout(title="Cruise Line Quarterly Revenue ($B)"),
                    barmode="group", yaxis_title="Revenue ($B)", height=420,
                    legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="left", x=0),
                )
                st.plotly_chart(fig_cruise_rev, width="stretch")
                add_export_figure("Cruise Line Quarterly Revenue", fig_cruise_rev)

                # Fuel cost overlay: crude oil vs cruise stocks
                if fred_key_available():
                    crude_oil = get_fred_series("DCOILWTICO", start=start_date)
                    if not crude_oil.empty:
                        fig_fuel = go.Figure()
                        fig_fuel.add_trace(go.Scatter(
                            x=crude_oil.index, y=crude_oil.values,
                            name="WTI Crude Oil ($/bbl)",
                            line=dict(color="#e74c3c", width=2),
                            fill="tozeroy", fillcolor="rgba(231, 76, 60, 0.08)",
                        ))
                        fig_fuel.update_layout(
                            **_base_layout(title="Crude Oil (WTI) — Key Cruise Line Cost Driver"),
                            yaxis_title="$/barrel", height=350,
                        )
                        st.plotly_chart(fig_fuel, width="stretch")
                        st.caption(
                            "Bunker fuel (derived from crude oil) is the largest variable cost for cruise lines. "
                            "RCL, CCL, and NCLH spend $1-2B+ annually on fuel."
                        )

                with st.expander("Cruise Line Financials Data"):
                    st.dataframe(cruise_fin_df, width="stretch", height=400)
                    add_export_table("Cruise Financials", cruise_fin_df)
            else:
                st.info("Cruise line financial data not available.")

    if industry_name in kpi_info:
        st.divider()
        st.subheader(f"Key Earnings KPIs to Monitor — {industry_name}")
        st.caption("These metrics are typically disclosed in quarterly earnings reports:")
        for kpi in kpi_info[industry_name]:
            st.markdown(f"- {kpi}")

    st.divider()
    st.subheader("Tracked Companies")
    comp_rows = []
    for ticker, info in COMPANIES.items():
        comp_rows.append({
            "Ticker": ticker,
            "Company": info["name"],
            "Segment": info["segment"],
        })
    if comp_rows:
        st.dataframe(pd.DataFrame(comp_rows).set_index("Ticker"), width="stretch")

# ── Export sidebar (all industries) ────────────────────────────────────
render_export_sidebar(cfg["name"])
