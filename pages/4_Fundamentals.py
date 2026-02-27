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

st.set_page_config(page_title="Fundamentals", layout="wide")
st.logo(os.path.join(os.path.dirname(__file__), "..", "assets", "arini_logo.svg"))
inject_css()

# ── Industry selector (very top) ─────────────────────────────────────────
cfg = render_industry_selector()

st.title(cfg.get("page_titles", {}).get("fundamentals", "Fundamentals"))
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
                "Mkt Cap ($B)": lambda v: f"${v:,.1f}B" if pd.notna(v) else "N/A",
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
        "Revenue ($B)": round(ttm_rev / 1e9, 1) if ttm_rev else np.nan,
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
        "TTM Rev ($B)": round(ttm / 1e9, 1) if ttm and not np.isnan(ttm) else np.nan,
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
                      "TTM Rev ($B)": lambda v: f"${v:.1f}B" if pd.notna(v) else "N/A",
                      "YoY Rev Growth %": lambda v: f"{v:.1f}%" if pd.notna(v) else "N/A",
                  }),
        width="stretch",
    )

st.divider()

# ── Restaurant Concept Map (restaurants only) ────────────────────────────
if cfg["name"] == "Restaurants":
    st.subheader("Restaurant Concept Map")
    st.caption(
        "Brands and concepts owned by each public company in coverage. "
        "Unit counts are approximate (latest 10-K / investor presentation). "
        "Avg check is estimated U.S. per-person spend."
    )

    from data.restaurant_concepts import RESTAURANT_CONCEPTS

    # Filter to selected tickers
    concepts = [c for c in RESTAURANT_CONCEPTS if c["ticker"] in selected]

    if concepts:
        import plotly.express as px

        # ── Summary table ────────────────────────────────────────────────
        concept_df = pd.DataFrame(concepts)
        concept_df["company"] = concept_df["ticker"].map(
            lambda t: COMPANIES.get(t, {}).get("name", t)
        )

        display_df = concept_df[[
            "ticker", "company", "concept", "cuisine", "units",
            "unit_type", "avg_check", "auv_m", "royalty_pct",
            "unit_growth_pct", "pct_parent_rev", "ownership",
        ]].rename(columns={
            "ticker": "Ticker", "company": "Parent",
            "concept": "Concept / Brand", "cuisine": "Cuisine",
            "units": "Units", "unit_type": "Scope",
            "ownership": "Ownership Model", "avg_check": "Avg Check",
            "auv_m": "AUV ($M)", "royalty_pct": "Royalty %",
            "unit_growth_pct": "Unit Growth %", "pct_parent_rev": "% of Parent Rev",
        })

        def _color_growth(val):
            if isinstance(val, (int, float)) and not np.isnan(val):
                return f"color: {'#2ecc71' if val > 0 else '#e74c3c'}; font-weight: bold"
            return ""

        st.dataframe(
            display_df.style
                .map(_color_growth, subset=["Unit Growth %"])
                .format({
                    "Units": "{:,.0f}",
                    "AUV ($M)": lambda v: f"${v:.1f}M" if pd.notna(v) else "N/A",
                    "Royalty %": lambda v: f"{v:.1f}%" if pd.notna(v) else "N/A",
                    "Unit Growth %": lambda v: f"{v:+.1f}%" if pd.notna(v) else "N/A",
                    "% of Parent Rev": lambda v: f"{v:.0f}%" if pd.notna(v) else "-",
                }),
            use_container_width=True,
            height=min(45 * len(display_df) + 40, 800),
            hide_index=True,
        )

        # ── AUV horizontal bar chart ────────────────────────────────────
        auv_df = concept_df[["concept", "ticker", "auv_m"]].dropna(subset=["auv_m"]).copy()
        auv_df = auv_df.sort_values("auv_m", ascending=True)
        auv_df["label"] = auv_df["concept"] + " (" + auv_df["ticker"] + ")"
        auv_df["color"] = auv_df["ticker"].map(
            lambda t: COMPANIES.get(t, {}).get("color", "#3498db")
        )

        fig_auv = go.Figure(go.Bar(
            y=auv_df["label"], x=auv_df["auv_m"],
            orientation="h",
            marker_color=auv_df["color"],
            text=[f"${v:.1f}M" for v in auv_df["auv_m"]],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>AUV: $%{x:.1f}M<extra></extra>",
        ))
        fig_auv.update_layout(
            **_base_layout(title="Average Unit Volume (AUV) by Concept", margin=dict(l=200, r=20, t=40, b=40)),
            xaxis_title="AUV ($M)", xaxis_tickprefix="$", xaxis_ticksuffix="M",
            height=max(len(auv_df) * 32, 400),
        )
        st.plotly_chart(fig_auv, use_container_width=True)

        # ── Unit growth vs AUV scatter ──────────────────────────────────
        scatter_df = concept_df.dropna(subset=["auv_m", "unit_growth_pct"]).copy()
        if not scatter_df.empty:
            st.markdown("**Unit Growth vs. AUV**")
            scatter_df["label"] = scatter_df["concept"] + " (" + scatter_df["ticker"] + ")"
            scatter_df["color"] = scatter_df["ticker"].map(
                lambda t: COMPANIES.get(t, {}).get("color", "#3498db")
            )
            # Log-scale bubble size to tame the MCD-42k vs Jaggers-15 range
            log_units = np.log10(scatter_df["units"].clip(lower=1))
            size_min, size_max = 12, 55
            log_min, log_max = log_units.min(), log_units.max()
            if log_max > log_min:
                scatter_df["bubble_size"] = size_min + (log_units - log_min) / (log_max - log_min) * (size_max - size_min)
            else:
                scatter_df["bubble_size"] = (size_min + size_max) / 2

            # Quadrant medians
            x_med = scatter_df["auv_m"].median()
            y_med = scatter_df["unit_growth_pct"].median()

            fig_scatter = go.Figure()
            for _, row in scatter_df.iterrows():
                fig_scatter.add_trace(go.Scatter(
                    x=[row["auv_m"]], y=[row["unit_growth_pct"]],
                    mode="markers",
                    marker=dict(
                        size=row["bubble_size"],
                        color=row["color"], opacity=0.75,
                        line=dict(width=1.5, color="white"),
                    ),
                    name=row["label"],
                    hovertemplate=(
                        f"<b>{row['concept']}</b> ({row['ticker']})<br>"
                        f"AUV: ${row['auv_m']:.1f}M<br>"
                        f"Unit Growth: {row['unit_growth_pct']:+.1f}%<br>"
                        f"Units: {row['units']:,}<extra></extra>"
                    ),
                ))

            # Smart label placement — offset labels that would overlap
            positions = []
            for _, row in scatter_df.iterrows():
                pos = "top center"
                for px_, py_ in positions:
                    if abs(row["auv_m"] - px_) < 1.0 and abs(row["unit_growth_pct"] - py_) < 3.0:
                        pos = "bottom center"
                        break
                positions.append((row["auv_m"], row["unit_growth_pct"]))
                fig_scatter.add_annotation(
                    x=row["auv_m"], y=row["unit_growth_pct"],
                    text=row["concept"],
                    showarrow=False,
                    yshift=20 if pos == "top center" else -20,
                    font=dict(size=9, color="#555"),
                )

            # Quadrant reference lines at median
            fig_scatter.add_hline(
                y=y_med, line_color="rgba(0,0,0,0.12)", line_width=1, line_dash="dot",
            )
            fig_scatter.add_vline(
                x=x_med, line_color="rgba(0,0,0,0.12)", line_width=1, line_dash="dot",
            )

            # Quadrant labels
            x_range = scatter_df["auv_m"].max() - scatter_df["auv_m"].min()
            y_range = scatter_df["unit_growth_pct"].max() - scatter_df["unit_growth_pct"].min()
            quadrant_labels = [
                (x_med + x_range * 0.25, y_med + y_range * 0.35, "High AUV + High Growth"),
                (x_med - x_range * 0.25, y_med + y_range * 0.35, "Low AUV + High Growth"),
                (x_med + x_range * 0.25, y_med - y_range * 0.35, "High AUV + Low Growth"),
                (x_med - x_range * 0.25, y_med - y_range * 0.35, "Low AUV + Low Growth"),
            ]
            for qx, qy, qlabel in quadrant_labels:
                fig_scatter.add_annotation(
                    x=qx, y=qy, text=f"<i>{qlabel}</i>",
                    showarrow=False,
                    font=dict(size=10, color="rgba(0,0,0,0.2)"),
                )

            fig_scatter.update_layout(
                **_base_layout(title="Unit Growth (%) vs. AUV ($M)"),
                xaxis_title="AUV ($M)", xaxis_tickprefix="$", xaxis_ticksuffix="M",
                yaxis_title="Net Unit Growth YoY %", yaxis_ticksuffix="%",
                showlegend=False, height=550,
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
            st.caption(
                "Bubble size = unit count (log-scaled). Dashed lines = median AUV / median growth. "
                "Top-right quadrant = strongest concepts (high revenue per unit + expanding rapidly)."
            )

        # ── Unit count treemap ───────────────────────────────────────────
        st.markdown("**Unit Count by Parent Company & Brand**")
        tree_df = concept_df[["ticker", "concept", "units", "cuisine"]].copy()
        tree_df["parent"] = tree_df["ticker"].map(
            lambda t: f"{t} - {COMPANIES.get(t, {}).get('name', t)}"
        )
        fig_tree = px.treemap(
            tree_df,
            path=["parent", "concept"],
            values="units",
            color="parent",
            color_discrete_map={
                f"{t} - {COMPANIES[t]['name']}": COMPANIES[t]["color"]
                for t in COMPANIES
            },
            hover_data={"cuisine": True, "units": ":,.0f"},
        )
        fig_tree.update_layout(
            margin=dict(t=30, l=10, r=10, b=10),
            height=500,
        )
        fig_tree.update_traces(
            hovertemplate="<b>%{label}</b><br>Units: %{value:,.0f}<br>%{customdata[0]}<extra></extra>",
        )
        st.plotly_chart(fig_tree, use_container_width=True)

        # ── Royalty rate comparison (franchised brands only) ─────────────
        roy_df = concept_df.dropna(subset=["royalty_pct"]).copy()
        if not roy_df.empty:
            roy_df = roy_df.sort_values("royalty_pct", ascending=True)
            roy_df["label"] = roy_df["concept"] + " (" + roy_df["ticker"] + ")"
            roy_df["color"] = roy_df["ticker"].map(
                lambda t: COMPANIES.get(t, {}).get("color", "#3498db")
            )
            fig_roy = go.Figure(go.Bar(
                y=roy_df["label"], x=roy_df["royalty_pct"],
                orientation="h",
                marker_color=roy_df["color"],
                text=[f"{v:.1f}%" for v in roy_df["royalty_pct"]],
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>Royalty: %{x:.1f}%<extra></extra>",
            ))
            fig_roy.update_layout(
                **_base_layout(title="Franchise Royalty Rate by Concept", margin=dict(l=200, r=20, t=40, b=40)),
                xaxis_title="Royalty Rate (%)", xaxis_ticksuffix="%",
                height=max(len(roy_df) * 32, 350),
            )
            st.plotly_chart(fig_roy, use_container_width=True)
            st.caption(
                "Royalty rate is the % of franchisee gross sales paid to the franchisor. "
                "Company-operated concepts (CMG, DRI brands, etc.) show N/A. "
                "Some franchisors also collect advertising fund contributions (typically 3-5% additional)."
            )

        # ── Concept details (expandable) ─────────────────────────────────
        with st.expander("Concept Details & Descriptions"):
            for ticker in dict.fromkeys(c["ticker"] for c in concepts):
                t_concepts = [c for c in concepts if c["ticker"] == ticker]
                st.markdown(
                    f"**{ticker} - {COMPANIES.get(ticker, {}).get('name', ticker)}**"
                )
                for c in t_concepts:
                    total_units = f"{c['units']:,}"
                    auv_str = f" | AUV: ${c['auv_m']:.1f}M" if c.get("auv_m") else ""
                    roy_str = f" | Royalty: {c['royalty_pct']:.1f}%" if c.get("royalty_pct") else ""
                    growth_str = f" | Unit Growth: {c['unit_growth_pct']:+.1f}%" if c.get("unit_growth_pct") is not None else ""
                    pct_str = f" | {c['pct_parent_rev']:.0f}% of parent rev" if c.get("pct_parent_rev") else ""
                    st.markdown(
                        f"- **{c['concept']}** ({c['cuisine']}) - "
                        f"{total_units} units ({c['unit_type']}) | "
                        f"Check: {c['avg_check']} | {c['ownership']}"
                        f"{auv_str}{roy_str}{growth_str}{pct_str}"
                    )
                    st.caption(f"  {c['description']}")
                st.markdown("---")
    else:
        st.info("Select at least one restaurant company to see concepts.")

st.caption(
    "**Data note:** Yahoo Finance data may lag by 1-2 quarters. "
    "Revenue/margins from yfinance `.info` are TTM (trailing twelve months)."
)
