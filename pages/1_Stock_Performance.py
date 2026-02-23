"""
Stock Performance Page
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import numpy as np

from utils.industry_selector import render_industry_selector
from utils.data_fetchers import get_prices, get_ohlcv, get_returns_table
from utils.charts import normalized_price_chart, returns_heatmap, price_volume_chart
from utils.style import inject_css

st.set_page_config(page_title="Stock Performance", layout="wide")
st.logo(os.path.join(os.path.dirname(__file__), "..", "assets", "arini_logo.svg"))
inject_css()

# ── Industry selector (very top) ─────────────────────────────────────────
cfg = render_industry_selector()

st.title("Stock Performance")
COMPANIES = cfg["companies"]
TICKERS = list(COMPANIES.keys())
SEGMENTS = cfg["segments"]

# ── Sidebar controls ───────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")
    period = st.selectbox(
        "Time Period",
        ["3mo", "6mo", "1y", "2y", "5y"],
        index=2,
        format_func=lambda x: {"3mo": "3 Months", "6mo": "6 Months",
                                "1y": "1 Year", "2y": "2 Years", "5y": "5 Years"}[x],
    )
    segments_sel = st.multiselect(
        "Filter by Segment",
        options=list(SEGMENTS.keys()),
        default=list(SEGMENTS.keys()),
    )
    include_spy = st.checkbox("Include S&P 500 (SPY) benchmark", value=True)

# Build selected ticker list
selected = []
for seg in segments_sel:
    selected.extend(SEGMENTS[seg])
# Deduplicate while preserving order
selected = list(dict.fromkeys(selected))
if include_spy:
    selected_with_spy = selected + ["SPY"]
else:
    selected_with_spy = selected

# ── Returns heatmap ────────────────────────────────────────────────────────
st.subheader("Returns Heatmap")
with st.spinner("Fetching returns…"):
    ret_df = get_returns_table(selected_with_spy)

if not ret_df.empty:
    names = {t: COMPANIES[t]["name"] for t in TICKERS if t in COMPANIES}
    names["SPY"] = "S&P 500 ETF"
    st.plotly_chart(returns_heatmap(ret_df, names), width="stretch")
else:
    st.warning("Could not load return data.")

# ── Normalized price chart ─────────────────────────────────────────────────
st.subheader("Normalized Price Chart")
with st.spinner("Loading prices…"):
    prices = get_prices(selected_with_spy, period=period)

colors = {t: COMPANIES[t]["color"] for t in TICKERS if t in COMPANIES}
colors["SPY"] = "#888888"

if not prices.empty:
    st.plotly_chart(
        normalized_price_chart(prices, colors, f"Normalized Performance — {period}"),
        width="stretch",
    )

# ── 52-week high / low table ───────────────────────────────────────────────
st.subheader("52-Week High / Low")
with st.spinner("Calculating 52-week range…"):
    prices_52 = get_prices(selected, period="1y")

if not prices_52.empty:
    rows_52 = []
    for t in selected:
        if t not in prices_52.columns:
            continue
        s = prices_52[t].dropna()
        if s.empty:
            continue
        last   = s.iloc[-1]
        hi_52  = s.max()
        lo_52  = s.min()
        pct_hi = (last / hi_52 - 1) * 100
        rows_52.append({
            "Ticker":    t,
            "Company":   COMPANIES[t]["name"],
            "Segment":   COMPANIES[t]["segment"],
            "Last":      round(last, 2),
            "52W High":  round(hi_52, 2),
            "52W Low":   round(lo_52, 2),
            "% from High": round(pct_hi, 1),
            "% from Low":  round((last / lo_52 - 1) * 100, 1),
        })
    if rows_52:
        df_52 = pd.DataFrame(rows_52).set_index("Ticker")

        def color_from_high(val):
            if isinstance(val, float):
                return f"color: {'#e74c3c' if val < -20 else '#f39c12' if val < -10 else '#2ecc71'}"
            return ""

        st.dataframe(
            df_52.style.map(color_from_high, subset=["% from High"])
                       .format({"Last": "${:.2f}", "52W High": "${:.2f}",
                                "52W Low": "${:.2f}", "% from High": "{:.1f}%",
                                "% from Low": "{:.1f}%"}),
            width="stretch",
        )

# ── Individual stock chart ─────────────────────────────────────────────────
st.subheader("Individual Stock — Price & Volume")
ticker_sel = st.selectbox(
    "Select ticker",
    options=selected,
    format_func=lambda t: f"{t} – {COMPANIES[t]['name']}",
)
period_ind = st.selectbox(
    "Period", ["3mo", "6mo", "1y", "2y"], index=2,
    format_func=lambda x: {"3mo": "3M", "6mo": "6M", "1y": "1Y", "2y": "2Y"}[x],
    key="ind_period",
)

with st.spinner(f"Loading {ticker_sel}…"):
    ohlcv = get_ohlcv(ticker_sel, period=period_ind)

if not ohlcv.empty:
    st.plotly_chart(
        price_volume_chart(ohlcv, ticker_sel, COMPANIES[ticker_sel]["name"]),
        width="stretch",
    )

    # Quick stats
    c1, c2, c3, c4, c5 = st.columns(5)
    last_close = ohlcv["Close"].iloc[-1]
    prev_close = ohlcv["Close"].iloc[-2] if len(ohlcv) > 1 else last_close
    info_cols = [
        ("Last Close",  f"${last_close:.2f}"),
        ("1D Change",   f"{(last_close/prev_close - 1)*100:.2f}%"),
        ("52W High",    f"${ohlcv['High'].max():.2f}"),
        ("52W Low",     f"${ohlcv['Low'].min():.2f}"),
        ("Avg Vol (30D)", f"{ohlcv['Volume'].tail(30).mean()/1e6:.1f}M"),
    ]
    for col, (label, val) in zip([c1, c2, c3, c4, c5], info_cols):
        col.metric(label, val)
