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

st.set_page_config(page_title="Industry KPIs", layout="wide")
st.logo(os.path.join(os.path.dirname(__file__), "..", "assets", "arini_logo.svg"))
inject_css()

# ── Industry selector (very top) ─────────────────────────────────────────
cfg = render_industry_selector()

st.title("Industry KPIs")

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
        get_annual_box_office, get_release_schedule,
        get_distributor_share_multi_year,
    )
    from utils.charts import weekly_bo_chart, annual_bo_chart, ytd_pacing_chart

    COMPANIES = cfg["companies"]
    fs = cfg["fred_series"]
    lbl = cfg["macro_labels"]

    st.header("Box Office Dashboard")
    st.caption("Live data from The Numbers · FRED pricing & employment data · Updated hourly")

    # ── Sidebar ───────────────────────────────────────────────────────────
    with st.sidebar:
        st.header("Settings")
        bo_lookback = st.selectbox(
            "Box Office Lookback",
            ["YTD", "1M", "3M", "6M", "52W", "1Y", "3Y"],
            index=4,
            help="Controls the weekly box office trend chart period",
        )
        bo_compare_year = st.selectbox(
            "Compare current year to",
            [2025, 2024, 2023, 2019],
            index=0,
            format_func=lambda y: f"{y}" + (" (pre-COVID)" if y == 2019 else ""),
        )
        start_year = st.slider("FRED History Start Year", 2010, 2022, 2015)
        start_date = f"{start_year}-01-01"

    current_year = 2026

    # ── Determine years needed based on lookback ─────────────────────────
    lookback_years_map = {"YTD": [current_year], "1M": [current_year],
                          "3M": [current_year], "6M": [current_year, current_year - 1],
                          "52W": [current_year, current_year - 1],
                          "1Y": [current_year, current_year - 1],
                          "3Y": [current_year, current_year - 1, current_year - 2, current_year - 3]}
    years_needed = set(lookback_years_map.get(bo_lookback, [current_year]))
    years_needed.add(bo_compare_year)
    years_needed.add(current_year)
    years_needed.add(2025)  # Always fetch 2025 for detail table

    # ── Fetch box office data ─────────────────────────────────────────────
    with st.spinner("Fetching box office data…"):
        weekly_chart_df = get_weekly_box_office()
        all_weekly_data = {}
        for yr in sorted(years_needed):
            all_weekly_data[yr] = get_weekly_box_office_trend(yr)
        weekly_trend_current = all_weekly_data.get(current_year, pd.DataFrame())
        weekly_trend_prior = all_weekly_data.get(bo_compare_year, pd.DataFrame())
        annual_df = get_annual_box_office()
        release_df = get_release_schedule()

    # ── Section 1: Box Office Snapshot (metric cards) ─────────────────────
    c1, c2, c3, c4 = st.columns(4)

    if not weekly_trend_current.empty:
        latest_wk = weekly_trend_current.iloc[-1]
        prev_wk = weekly_trend_current.iloc[-2] if len(weekly_trend_current) > 1 else None
        wk_date_label = latest_wk["weekend_date"].strftime("%b %d") if pd.notna(latest_wk.get("weekend_date")) else ""
        c1.metric(
            f"Weekend Box Office ({wk_date_label})" if wk_date_label else "Weekend Box Office",
            f"${latest_wk['combined_gross']:,.0f}" if latest_wk["combined_gross"] else "N/A",
        )
        if prev_wk is not None and latest_wk["combined_gross"] and prev_wk["combined_gross"]:
            pct_chg = (latest_wk["combined_gross"] / prev_wk["combined_gross"] - 1) * 100
            c2.metric(
                "vs. Prior Weekend",
                f"{pct_chg:+.1f}%",
                delta=f"{pct_chg:+.1f}%",
                delta_color="normal",
            )
        # YTD total
        ytd_total = weekly_trend_current["combined_gross"].sum()
        ytd_delta = None
        if not weekly_trend_prior.empty:
            n_weeks = len(weekly_trend_current)
            prior_ytd = weekly_trend_prior.head(n_weeks)["combined_gross"].sum()
            if prior_ytd > 0:
                ytd_pct = (ytd_total / prior_ytd - 1) * 100
                ytd_delta = f"{ytd_pct:+.1f}% vs {bo_compare_year}"
        c3.metric("YTD Box Office", f"${ytd_total:,.0f}", delta=ytd_delta, delta_color="normal")

    if not annual_df.empty:
        latest_year = annual_df.iloc[0]
        yr_label = int(latest_year["Year"]) if "Year" in latest_year.index else ""
        if latest_year.get("Avg Ticket Price"):
            c4.metric(f"Avg Ticket Price ({yr_label})" if yr_label else "Avg Ticket Price",
                      f"${latest_year['Avg Ticket Price']:.2f}")

    # ── #1 Movie callout ──────────────────────────────────────────────────
    if not weekly_trend_current.empty:
        latest = weekly_trend_current.iloc[-1]
        st.info(
            f"**#1 Movie:** {latest['no1_movie']} — "
            f"${latest['no1_gross']:,.0f} weekend gross"
            if latest["no1_gross"] else f"**#1 Movie:** {latest['no1_movie']}"
        )

    st.divider()

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 2: WEEKLY BOX OFFICE TREND (with lookback filter)
    # ══════════════════════════════════════════════════════════════════════
    st.subheader(f"Weekly Combined Weekend Box Office ({bo_lookback})")

    # Build the combined weekly BO DataFrame for the selected lookback
    def _build_lookback_df(lookback, all_data, current_yr):
        """Combine weekly data across years for the chosen lookback window."""
        today = pd.Timestamp.now().normalize()
        frames = []
        for yr in sorted(all_data.keys()):
            df = all_data[yr]
            if not df.empty:
                frames.append(df)
        if not frames:
            return pd.DataFrame()
        combined = pd.concat(frames, ignore_index=True).sort_values("weekend_date")
        combined = combined.drop_duplicates(subset=["weekend_date"])

        if lookback == "YTD":
            start = pd.Timestamp(f"{current_yr}-01-01")
        elif lookback == "1M":
            start = today - pd.DateOffset(months=1)
        elif lookback == "3M":
            start = today - pd.DateOffset(months=3)
        elif lookback == "6M":
            start = today - pd.DateOffset(months=6)
        elif lookback == "52W":
            start = today - pd.DateOffset(weeks=52)
        elif lookback == "1Y":
            start = today - pd.DateOffset(years=1)
        elif lookback == "3Y":
            start = today - pd.DateOffset(years=3)
        else:
            start = pd.Timestamp(f"{current_yr}-01-01")

        return combined[combined["weekend_date"] >= start].reset_index(drop=True)

    lookback_df = _build_lookback_df(bo_lookback, all_weekly_data, current_year)

    if not lookback_df.empty:
        # Build the lookback chart
        fig_lb = go.Figure()
        fig_lb.add_trace(go.Bar(
            x=lookback_df["weekend_date"],
            y=lookback_df["combined_gross"],
            marker_color="#1565C0",
            hovertemplate="%{x|%b %d, %Y}: $%{y:,.0f}<extra></extra>",
            name="Weekend BO",
        ))

        # Add comparison year overlay if applicable
        if not weekly_trend_prior.empty and bo_lookback in ("YTD", "52W", "1Y"):
            prior = weekly_trend_prior.copy()
            if bo_lookback == "YTD":
                n_weeks = len(lookback_df[lookback_df["weekend_date"].dt.year == current_year])
                prior_slice = prior.head(n_weeks)
            else:
                prior_slice = prior
            if not prior_slice.empty:
                year_diff = current_year - bo_compare_year
                prior_slice = prior_slice.copy()
                prior_slice["weekend_date"] = prior_slice["weekend_date"] + pd.DateOffset(years=year_diff)
                fig_lb.add_trace(go.Scatter(
                    x=prior_slice["weekend_date"],
                    y=prior_slice["combined_gross"],
                    name=f"{bo_compare_year}",
                    line=dict(color="#e67e22", width=2.5, dash="dot"),
                    hovertemplate=f"{bo_compare_year} " + "%{x|%b %d}: $%{y:,.0f}<extra></extra>",
                ))

        fig_lb.update_layout(
            **_base_layout(title=f"Weekly Weekend BO — {bo_lookback}"),
            yaxis_title="Weekend BO ($)",
            yaxis_tickformat="$,.0s",
            height=440,
            legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="left", x=0),
        )
        st.plotly_chart(fig_lb, width="stretch")
        st.caption(
            f"Showing {len(lookback_df)} weekends · "
            f"Total: ${lookback_df['combined_gross'].sum():,.0f} · "
            f"Avg: ${lookback_df['combined_gross'].mean():,.0f}/weekend"
        )
    else:
        st.warning("Weekly box office trend data unavailable.")

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 2B: WEEKLY BOX OFFICE — YoY TRACKING + #1 MOVIE
    # ══════════════════════════════════════════════════════════════════════
    st.subheader("Weekly Box Office — YoY Tracking")

    # Get 2025 data for the detail table (always included)
    weekly_trend_2025 = all_weekly_data.get(2025, pd.DataFrame())

    if not weekly_trend_current.empty and not weekly_trend_prior.empty:
        # Build week-by-week comparison
        current_wk = weekly_trend_current.copy()
        prior_wk = weekly_trend_prior.copy()
        current_wk["week_num"] = range(1, len(current_wk) + 1)
        prior_wk["week_num"] = range(1, len(prior_wk) + 1)

        # Use full year (52 weeks) of data for YoY comparison
        n_weeks = min(len(current_wk), len(prior_wk), 52)
        comp_df = current_wk.head(n_weeks).copy()
        comp_df["prior_gross"] = prior_wk.head(n_weeks)["combined_gross"].values
        comp_df["prior_movie"] = prior_wk.head(n_weeks)["no1_movie"].values
        comp_df["yoy_pct"] = (
            (comp_df["combined_gross"] / comp_df["prior_gross"] - 1) * 100
        ).where(comp_df["prior_gross"] > 0, None)

        # Also merge 2025 data if compare year is not 2025
        if bo_compare_year != 2025 and not weekly_trend_2025.empty:
            wk_2025 = weekly_trend_2025.copy()
            wk_2025["week_num"] = range(1, len(wk_2025) + 1)
            n_2025 = min(n_weeks, len(wk_2025))
            comp_df["gross_2025"] = pd.Series(
                wk_2025.head(n_2025)["combined_gross"].values, index=comp_df.index[:n_2025]
            )
            comp_df["movie_2025"] = pd.Series(
                wk_2025.head(n_2025)["no1_movie"].values, index=comp_df.index[:n_2025]
            )

        st.caption(f"Full year comparison: {current_year} vs {bo_compare_year} vs 2025 | #1 movie shown for each weekend")

        # Dual-axis chart: bars = current BO, lines = prior years, YoY %
        from plotly.subplots import make_subplots
        fig_yoy = make_subplots(specs=[[{"secondary_y": True}]])
        fig_yoy.add_trace(
            go.Bar(
                x=comp_df["weekend_date"],
                y=comp_df["combined_gross"],
                name=f"{current_year} Weekend BO",
                marker_color="#1565C0",
                hovertemplate="<b>%{x|%b %d, %Y}</b><br>BO: $%{y:,.0f}<extra></extra>",
            ),
            secondary_y=False,
        )
        fig_yoy.add_trace(
            go.Scatter(
                x=comp_df["weekend_date"],
                y=comp_df["prior_gross"],
                name=f"{bo_compare_year} Weekend BO",
                line=dict(color="#e67e22", width=2, dash="dot"),
                hovertemplate=f"{bo_compare_year}" + ": $%{y:,.0f}<extra></extra>",
            ),
            secondary_y=False,
        )
        # Add 2025 overlay if not already the comparison year
        if "gross_2025" in comp_df.columns:
            fig_yoy.add_trace(
                go.Scatter(
                    x=comp_df["weekend_date"],
                    y=comp_df["gross_2025"],
                    name="2025 Weekend BO",
                    line=dict(color="#9b59b6", width=2, dash="dash"),
                    hovertemplate="2025: $%{y:,.0f}<extra></extra>",
                ),
                secondary_y=False,
            )
        fig_yoy.add_trace(
            go.Scatter(
                x=comp_df["weekend_date"],
                y=comp_df["yoy_pct"],
                name=f"YoY % vs {bo_compare_year}",
                line=dict(color="#2ecc71", width=2.5),
                hovertemplate="YoY: %{y:+.1f}%<extra></extra>",
            ),
            secondary_y=True,
        )
        fig_yoy.add_hline(y=0, line_color="rgba(0,0,0,0.2)", line_width=1, secondary_y=True)
        fig_yoy.update_layout(
            **_base_layout(title=f"Weekly BO: {current_year} vs {bo_compare_year} with YoY %"),
            height=460,
            legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="left", x=0),
        )
        fig_yoy.update_yaxes(title_text="Weekend BO ($)", tickformat="$,.0s", secondary_y=False)
        fig_yoy.update_yaxes(title_text="YoY %", tickformat="+.0f%", secondary_y=True)
        st.plotly_chart(fig_yoy, width="stretch")

        # Weekly detail table with #1 movie — includes 2025 column
        st.markdown("**Week-by-Week Detail**")
        detail_rows = []
        for _, row in comp_df.iterrows():
            r = {
                "Weekend": row["weekend_date"].strftime("%b %d, %Y") if pd.notna(row["weekend_date"]) else "",
                "Wk #": int(row["week_num"]),
                f"{current_year} BO": f"${row['combined_gross']:,.0f}" if row["combined_gross"] else "N/A",
                "2025 BO": f"${row['gross_2025']:,.0f}" if pd.notna(row.get("gross_2025")) else "N/A",
                f"{bo_compare_year} BO": f"${row['prior_gross']:,.0f}" if row["prior_gross"] else "N/A",
                f"YoY % vs {bo_compare_year}": round(row["yoy_pct"], 1) if pd.notna(row.get("yoy_pct")) else None,
                f"#1 Movie ({current_year})": row.get("no1_movie", ""),
                "#1 Movie (2025)": row.get("movie_2025", "") if pd.notna(row.get("movie_2025")) else "",
                f"#1 Movie ({bo_compare_year})": row.get("prior_movie", ""),
            }
            # Remove duplicate 2025 columns if compare year is 2025
            if bo_compare_year == 2025:
                r.pop("2025 BO", None)
                r.pop("#1 Movie (2025)", None)
            detail_rows.append(r)
        if detail_rows:
            detail_df = pd.DataFrame(detail_rows)
            yoy_col = f"YoY % vs {bo_compare_year}"

            def _color_yoy(val):
                if isinstance(val, (int, float)):
                    return f"color: {'#2ecc71' if val >= 0 else '#e74c3c'}; font-weight: bold"
                return ""

            st.dataframe(
                detail_df.style
                    .map(_color_yoy, subset=[yoy_col])
                    .format({yoy_col: lambda v: f"{v:+.1f}%" if v is not None and pd.notna(v) else "N/A"}),
                width="stretch",
                height=500,
                hide_index=True,
            )

    elif not weekly_trend_current.empty:
        st.info(f"Comparison data for {bo_compare_year} not available.")
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

    years_to_compare = [current_year, 2025, 2024, 2019]
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
    # SECTION 7: CPI MOVIE ADMISSIONS + EMPLOYMENT (FRED)
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
        # ═══════════════════════════════════════════════════════════════════
        st.header(lbl.get("industry_section_title", "Industry Pricing"))

        # ── Industry KPI series (e.g. PPI Corrugated Shipping Containers) ──
        if "industry_kpi" in series_data:
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
        if "cpi_industry_1" in series_data:
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
                   "box_inventories", "capacity_util", "occ_ppi", "recycled_paperboard",
                   "kraft_linerboard", "corrugated_output", "cass_freight"]
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

            # ── Row 1: Box Production + Capacity Utilization ─────────────
            col_bp, col_cu = st.columns(2)

            with col_bp:
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

            with col_cu:
                if "capacity_util" in pp_data:
                    cu = pp_data["capacity_util"]
                    st.subheader(lbl.get("capacity_util_chart_title", "Capacity Utilization"))
                    fig_cu = go.Figure(go.Scatter(
                        x=cu.index, y=cu.values,
                        name="Capacity Utilization %",
                        line=dict(color="#8B4513", width=2.5),
                    ))
                    # Add reference bands
                    fig_cu.add_hline(y=95, line_color="rgba(231,76,60,0.5)", line_width=1,
                                     line_dash="dash", annotation_text="Tight (95%)")
                    fig_cu.add_hline(y=90, line_color="rgba(46,204,113,0.5)", line_width=1,
                                     line_dash="dash", annotation_text="Normal (90%)")
                    fig_cu.update_layout(
                        **_base_layout(title=lbl.get("capacity_util_chart_title", "Capacity Util %")),
                        yaxis_title="Percent", height=380,
                    )
                    st.plotly_chart(fig_cu, width="stretch")
                    st.caption(lbl.get("capacity_util_caption", ""))

            # ── Row 2: OCC (Recycled Fiber) + Shipment Value ─────────────
            col_occ, col_sv = st.columns(2)

            with col_occ:
                if "occ_ppi" in pp_data:
                    occ = pp_data["occ_ppi"]
                    yoy_occ = yoy(occ)
                    if not yoy_occ.empty:
                        st.subheader(lbl.get("occ_chart_title", "OCC Price Index (YoY %)"))
                        fig_occ = go.Figure(go.Scatter(
                            x=yoy_occ.index, y=yoy_occ.values,
                            name="OCC PPI",
                            line=dict(color="#C0392B", width=2.5),
                            fill="tozeroy", fillcolor="rgba(192, 57, 43, 0.08)",
                        ))
                        fig_occ.add_hline(y=0, line_color="rgba(0,0,0,0.3)", line_width=1)
                        fig_occ.update_layout(
                            **_base_layout(title=lbl.get("occ_chart_title", "OCC (YoY %)")),
                            yaxis_title="YoY %", height=380,
                        )
                        st.plotly_chart(fig_occ, width="stretch")
                        st.caption(lbl.get("occ_caption", ""))

                    with st.expander("Show OCC Absolute Index Level"):
                        fig_occ_abs = go.Figure(go.Scatter(
                            x=occ.index, y=occ.values,
                            name="OCC PPI", line=dict(color="#C0392B", width=2),
                        ))
                        fig_occ_abs.update_layout(
                            **_base_layout(title="OCC (Corrugated Recyclable Paper) — Index Level"),
                            yaxis_title="Index", height=340,
                        )
                        st.plotly_chart(fig_occ_abs, width="stretch")

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

            # ── Row 3: Inventories ─────────────────────────────────────
            if "box_inventories" in pp_data:
                with st.expander("Paperboard Container Inventories ($M, SA)"):
                    inv = pp_data["box_inventories"]
                    fig_inv = go.Figure(go.Scatter(
                        x=inv.index, y=inv.values,
                        name="Inventories ($M)",
                        line=dict(color="#884EA0", width=2.5),
                        fill="tozeroy", fillcolor="rgba(136, 78, 160, 0.08)",
                    ))
                    fig_inv.update_layout(
                        **_base_layout(title="Total Inventories: Paperboard Container ($M, SA)"),
                        yaxis_title="Millions $", height=380,
                    )
                    st.plotly_chart(fig_inv, width="stretch")

            # ── Row 4: Volume & Shipments ──────────────────────────────
            col_co, col_cf = st.columns(2)

            with col_co:
                if "corrugated_output" in pp_data:
                    co = pp_data["corrugated_output"]
                    st.subheader(lbl.get("corrugated_output_chart_title", "Corrugated Box Output"))
                    fig_co = go.Figure(go.Scatter(
                        x=co.index, y=co.values,
                        name="Real Output",
                        line=dict(color="#2980B9", width=2.5),
                        fill="tozeroy", fillcolor="rgba(41, 128, 185, 0.08)",
                    ))
                    fig_co.update_layout(
                        **_base_layout(title=lbl.get("corrugated_output_chart_title", "Output")),
                        yaxis_title="Index", height=380,
                    )
                    st.plotly_chart(fig_co, width="stretch")
                    st.caption(lbl.get("corrugated_output_caption", ""))

            with col_cf:
                if "cass_freight" in pp_data:
                    cf = pp_data["cass_freight"]
                    st.subheader(lbl.get("cass_freight_chart_title", "Cass Freight Shipments"))
                    fig_cf = go.Figure(go.Scatter(
                        x=cf.index, y=cf.values,
                        name="Shipment Index",
                        line=dict(color="#E67E22", width=2.5),
                        fill="tozeroy", fillcolor="rgba(230, 126, 34, 0.08)",
                    ))
                    fig_cf.update_layout(
                        **_base_layout(title=lbl.get("cass_freight_chart_title", "Cass Freight")),
                        yaxis_title="Index", height=380,
                    )
                    st.plotly_chart(fig_cf, width="stretch")
                    st.caption(lbl.get("cass_freight_caption", ""))

            # ── OCC vs Containerboard Spread ─────────────────────────────
            if "occ_ppi" in pp_data and "cpi_industry_1" in series_data:
                occ_yoy = yoy(pp_data["occ_ppi"])
                cb_yoy = yoy(series_data["cpi_industry_1"])
                spread_occ = (cb_yoy - occ_yoy).dropna()
                if not spread_occ.empty:
                    with st.expander("Containerboard PPI vs OCC Spread (YoY pp) — Margin Proxy"):
                        fig_sp = go.Figure(go.Bar(
                            x=spread_occ.index, y=spread_occ.values,
                            marker_color=["#2ecc71" if v > 0 else "#e74c3c" for v in spread_occ.values],
                            hovertemplate="%{x|%b %Y}: %{y:.2f}pp<extra></extra>",
                        ))
                        fig_sp.add_hline(y=0, line_color="rgba(0,0,0,0.2)", line_width=1)
                        fig_sp.update_layout(
                            **_base_layout(title="Containerboard PPI \u2212 OCC PPI (YoY pp Spread)"),
                            yaxis_title="Percentage Points", height=320,
                        )
                        st.plotly_chart(fig_sp, width="stretch")
                        st.caption(
                            "Green = containerboard prices rising faster than OCC (margin expansion). "
                            "Red = OCC rising faster (margin compression for recycled mills)."
                        )

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
