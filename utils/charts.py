"""
Reusable Plotly chart builders for the Restaurant KPI Dashboard.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


CHART_TEMPLATE = "plotly_white"
GRID_COLOR     = "rgba(0,0,0,0.07)"
FONT_COLOR     = "#0D2B55"


def _base_layout(**kwargs) -> dict:
    # Build defaults only for keys the caller hasn't explicitly provided,
    # so passing e.g. margin=... to _base_layout() always wins.
    base = dict(
        template=CHART_TEMPLATE,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Arial, sans-serif", size=12, color=FONT_COLOR),
        hovermode="x unified",
    )
    if "xaxis" not in kwargs:
        base["xaxis"] = dict(gridcolor=GRID_COLOR, showgrid=True)
    if "yaxis" not in kwargs:
        base["yaxis"] = dict(gridcolor=GRID_COLOR, showgrid=True)
    if "margin" not in kwargs:
        base["margin"] = dict(l=50, r=20, t=40, b=40)
    if "bargap" not in kwargs:
        base["bargap"] = 0.08
    base.update(kwargs)
    return base


# ── Normalized price chart ─────────────────────────────────────────────────

def normalized_price_chart(
    prices: pd.DataFrame,
    colors: dict,
    title: str = "Normalized Price (rebased to 100)",
) -> go.Figure:
    """
    Line chart with all series rebased to 100 at the first available date.
    prices: DataFrame with date index, ticker columns.
    colors: {ticker: hex_color}
    """
    fig = go.Figure()
    for col in prices.columns:
        s = prices[col].dropna()
        if s.empty:
            continue
        rebased = s / s.iloc[0] * 100
        fig.add_trace(go.Scatter(
            x=rebased.index,
            y=rebased.values,
            name=col,
            line=dict(color=colors.get(col, None), width=1.8),
            hovertemplate=f"<b>{col}</b>: %{{y:.1f}}<extra></extra>",
        ))
    fig.update_layout(
        **_base_layout(title=title),
        legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="left", x=0),
        yaxis_title="Index (100 = start)",
    )
    return fig


# ── Returns heatmap table ──────────────────────────────────────────────────

def returns_heatmap(returns_df: pd.DataFrame, company_names: dict) -> go.Figure:
    """
    Heatmap-style table of returns. Green = positive, red = negative.
    returns_df: DataFrame with tickers as index, period columns.
    """
    df = returns_df.copy()
    df.index = [f"{t} – {company_names.get(t, t)}" for t in df.index]

    x_labels = df.columns.tolist()
    y_labels = df.index.tolist()
    z = df.values.astype(float)

    max_abs = np.nanmax(np.abs(z)) or 1
    threshold = max_abs * 0.45

    fig = go.Figure(go.Heatmap(
        z=z,
        x=x_labels,
        y=y_labels,
        colorscale=[
            [0.0, "#c0392b"],
            [0.25, "#f5b7b1"],
            [0.5, "#ffffff"],
            [0.75, "#abebc6"],
            [1.0, "#1e8449"],
        ],
        zmid=0,
        zmin=-max_abs,
        zmax=max_abs,
        showscale=False,
        hovertemplate="<b>%{y}</b><br>%{x}: %{z:.1f}%<extra></extra>",
    ))

    # Use annotations for per-cell text color (white on dark, navy on light)
    annotations = []
    for i, y_val in enumerate(y_labels):
        for j, x_val in enumerate(x_labels):
            v = z[i][j]
            label = f"{v:.1f}%" if not np.isnan(v) else "N/A"
            font_color = "#ffffff" if not np.isnan(v) and abs(v) > threshold else FONT_COLOR
            annotations.append(dict(
                x=x_val, y=y_val, text=label, showarrow=False,
                font=dict(color=font_color, size=12),
            ))

    fig.update_layout(
        **_base_layout(
            title="Total Return (%)",
            xaxis=dict(side="top", gridcolor=GRID_COLOR),
            margin=dict(l=200, r=20, t=60, b=20),
            height=max(300, len(df) * 35 + 80),
        ),
        annotations=annotations,
    )
    return fig


# ── OHLCV / price + volume ─────────────────────────────────────────────────

def price_volume_chart(ohlcv: pd.DataFrame, ticker: str, company_name: str) -> go.Figure:
    """Candlestick + volume chart for a single ticker."""
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        row_heights=[0.75, 0.25],
        vertical_spacing=0.02,
    )
    fig.add_trace(go.Candlestick(
        x=ohlcv.index,
        open=ohlcv["Open"],
        high=ohlcv["High"],
        low=ohlcv["Low"],
        close=ohlcv["Close"],
        name=ticker,
        increasing_line_color="#2ecc71",
        decreasing_line_color="#e74c3c",
    ), row=1, col=1)
    colors = ["#2ecc71" if c >= o else "#e74c3c"
              for c, o in zip(ohlcv["Close"], ohlcv["Open"])]
    fig.add_trace(go.Bar(
        x=ohlcv.index,
        y=ohlcv["Volume"],
        name="Volume",
        marker_color=colors,
        opacity=0.6,
    ), row=2, col=1)
    fig.update_layout(
        **_base_layout(title=f"{ticker} – {company_name}"),
        xaxis_rangeslider_visible=False,
        showlegend=False,
        height=500,
    )
    fig.update_yaxes(title_text="Price ($)", row=1, col=1,
                     gridcolor=GRID_COLOR)
    fig.update_yaxes(title_text="Volume", row=2, col=1,
                     gridcolor=GRID_COLOR)
    return fig


# ── SSS bar chart ──────────────────────────────────────────────────────────

def sss_grouped_bar(df: pd.DataFrame, colors: dict, title: str = "Same-Store Sales (%)") -> go.Figure:
    """
    Grouped bar chart.
    df: pivot table with quarters as index, tickers as columns, SSS % as values.
    """
    fig = go.Figure()
    for ticker in df.columns:
        fig.add_trace(go.Bar(
            x=df.index,
            y=df[ticker],
            name=ticker,
            marker_color=colors.get(ticker, None),
            hovertemplate=f"<b>{ticker}</b>: %{{y:.1f}}%<extra></extra>",
        ))
    fig.add_hline(y=0, line_color="rgba(0,0,0,0.2)", line_width=1, opacity=0.6)
    fig.update_layout(
        **_base_layout(title=title),
        barmode="group",
        yaxis_title="SSS %",
        legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="left", x=0),
        height=420,
    )
    return fig


def sss_line_chart(df: pd.DataFrame, colors: dict, title: str = "SSS Trend") -> go.Figure:
    """Line chart of SSS over time."""
    fig = go.Figure()
    for ticker in df.columns:
        s = df[ticker].dropna()
        fig.add_trace(go.Scatter(
            x=s.index, y=s.values, name=ticker,
            mode="lines+markers",
            line=dict(color=colors.get(ticker), width=2),
            marker=dict(size=6),
            hovertemplate=f"<b>{ticker}</b> %{{x}}: %{{y:.1f}}%<extra></extra>",
        ))
    fig.add_hline(y=0, line_color="rgba(0,0,0,0.2)", line_width=1, opacity=0.6)
    fig.update_layout(
        **_base_layout(title=title),
        yaxis_title="SSS %",
        legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="left", x=0),
        height=420,
    )
    return fig


def traffic_ticket_chart(
    df: pd.DataFrame, ticker: str, color: str,
    quarters: list | None = None,
) -> go.Figure:
    """Stacked bar: traffic vs. ticket contribution to SSS.
    If *quarters* is provided, the x-axis is locked to that list so all
    charts share the same range regardless of per-ticker data availability.
    """
    valid = df.dropna(subset=["traffic", "ticket"])
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=valid["quarter"], y=valid["traffic"],
        name="Traffic", marker_color="#e67e22", opacity=0.85,
    ))
    fig.add_trace(go.Bar(
        x=valid["quarter"], y=valid["ticket"],
        name="Avg Ticket", marker_color="#95a5a6",
    ))
    fig.add_hline(y=0, line_color="rgba(0,0,0,0.2)", line_width=1, opacity=0.6)
    layout_kw = {
        **_base_layout(title=f"{ticker} – Traffic vs. Ticket (ppts)"),
        "barmode": "stack",
        "yaxis_title": "ppts",
        "height": 360,
    }
    if quarters:
        layout_kw["xaxis"] = dict(
            categoryorder="array",
            categoryarray=quarters,
            type="category",
        )
    fig.update_layout(**layout_kw)
    return fig


# ── Commodity charts ───────────────────────────────────────────────────────

def commodity_normalized_chart(
    prices: pd.DataFrame,
    meta: dict = None,
    normalize: bool = True,
) -> go.Figure:
    """
    Commodity price overview chart.
    normalize=True  → rebased to 100 at period start (indexed view)
    normalize=False → nominal prices as-is
    meta: optional dict keyed by column name with 'emoji' and 'color' keys.
    """
    fig = go.Figure()
    palette = px.colors.qualitative.Plotly
    for i, col in enumerate(prices.columns):
        s = prices[col].dropna()
        if s.empty:
            continue
        y_vals = (s / s.iloc[0] * 100).values if normalize else s.values

        if meta and col in meta:
            color = meta[col].get("color", palette[i % len(palette)])
            emoji = meta[col].get("emoji", "")
            label = f"{emoji} {col}" if emoji else col
        else:
            color = palette[i % len(palette)]
            label = col

        hover = "%{y:.1f}" if normalize else "%{y:.2f}"
        fig.add_trace(go.Scatter(
            x=s.index, y=y_vals, name=label,
            line=dict(color=color, width=1.8),
            hovertemplate=f"<b>{col}</b>: {hover}<extra></extra>",
        ))

    y_title = "Index (100 = period start)" if normalize else "Price"
    fig.update_layout(
        **_base_layout(margin=dict(l=50, r=20, t=10, b=90)),
        yaxis_title=y_title,
        legend=dict(
            orientation="h",
            yanchor="top", y=-0.12,
            xanchor="left", x=0,
            font=dict(size=12),
        ),
        height=460,
    )
    return fig


def commodity_detail_chart(
    series: pd.Series,
    name: str,
    unit: str,
    color: str = "#3498db",
) -> go.Figure:
    """
    Two-panel chart: nominal price on top, month-over-month % change bars on bottom.
    Series may be daily (futures) or monthly (FRED); resampled to month-end for MoM bars.
    """
    monthly  = series.resample("ME").last().dropna()
    mom_pct  = monthly.pct_change() * 100

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.68, 0.32],
        vertical_spacing=0.03,
    )

    # Top: price line
    try:
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        fill_color = f"rgba({r},{g},{b},0.10)"
    except Exception:
        fill_color = "rgba(52,152,219,0.10)"

    fig.add_trace(go.Scatter(
        x=series.index, y=series.values, name=name,
        line=dict(color=color, width=2),
        fill="tozeroy", fillcolor=fill_color,
        hovertemplate=f"<b>{name}</b>: %{{y:.2f}} {unit}<extra></extra>",
    ), row=1, col=1)

    # Bottom: MoM % change bars
    bar_colors = ["#2ecc71" if (v or 0) >= 0 else "#e74c3c"
                  for v in mom_pct.fillna(0)]
    fig.add_trace(go.Bar(
        x=mom_pct.index, y=mom_pct.values,
        name="MoM %", marker_color=bar_colors, opacity=0.80,
        hovertemplate="MoM: %{y:.1f}%<extra></extra>",
    ), row=2, col=1)

    fig.update_layout(
        **_base_layout(margin=dict(l=55, r=15, t=20, b=30)),
        showlegend=False,
        height=340,
    )
    fig.update_yaxes(title_text=unit,    row=1, col=1, gridcolor=GRID_COLOR)
    fig.update_yaxes(title_text="MoM %", row=2, col=1, gridcolor=GRID_COLOR,
                     zeroline=True, zerolinecolor="rgba(128,128,128,0.4)")
    return fig


def commodity_single_chart(series: pd.Series, name: str, unit: str) -> go.Figure:
    """Absolute price chart for a single commodity."""
    fig = go.Figure(go.Scatter(
        x=series.index, y=series.values, name=name,
        line=dict(color="#3498db", width=2),
        fill="tozeroy",
        fillcolor="rgba(52,152,219,0.1)",
        hovertemplate=f"<b>{name}</b>: %{{y:.2f}} {unit}<extra></extra>",
    ))
    fig.update_layout(
        **_base_layout(title=f"{name} ({unit})"),
        yaxis_title=unit,
        height=380,
    )
    return fig


# ── Macro charts ───────────────────────────────────────────────────────────

def dual_cpi_chart(series_1: pd.Series, series_2: pd.Series,
                   recession: pd.Series = None,
                   title: str = "CPI: Food Away from Home vs. Food at Home (YoY %)",
                   label_1: str = "Food Away from Home",
                   label_2: str = "Food at Home") -> go.Figure:
    """Two CPI/PPI series plotted as YoY%."""
    def yoy(s):
        return s.pct_change(12) * 100

    yoy_1 = yoy(series_1).dropna()
    yoy_2 = yoy(series_2).dropna()

    fig = go.Figure()
    if recession is not None and not recession.empty:
        _add_recession_shading(fig, recession, yoy_1.index)

    fig.add_trace(go.Scatter(
        x=yoy_1.index, y=yoy_1.values,
        name=label_1, line=dict(color="#e67e22", width=2),
    ))
    fig.add_trace(go.Scatter(
        x=yoy_2.index, y=yoy_2.values,
        name=label_2, line=dict(color="#3498db", width=2),
    ))
    fig.add_hline(y=0, line_color="rgba(0,0,0,0.2)", line_width=1, opacity=0.6)
    fig.update_layout(
        **_base_layout(title=title),
        yaxis_title="YoY %",
        legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="left", x=0),
        height=400,
    )
    return fig


def wages_chart(wages: pd.Series, recession: pd.Series = None,
                title: str = "Avg Hourly Earnings \u2013 Leisure & Hospitality (YoY %)") -> go.Figure:
    """Average Hourly Earnings YoY%."""
    yoy = wages.pct_change(12).dropna() * 100
    fig = go.Figure()
    if recession is not None and not recession.empty:
        _add_recession_shading(fig, recession, yoy.index)
    fig.add_trace(go.Scatter(
        x=yoy.index, y=yoy.values,
        name="Wages YoY %", line=dict(color="#2ecc71", width=2),
    ))
    fig.add_hline(y=0, line_color="rgba(0,0,0,0.2)", line_width=1, opacity=0.6)
    fig.update_layout(
        **_base_layout(title=title),
        yaxis_title="YoY %", height=360,
    )
    return fig


def sentiment_chart(sentiment: pd.Series) -> go.Figure:
    fig = go.Figure(go.Scatter(
        x=sentiment.index, y=sentiment.values,
        name="U of M Consumer Sentiment",
        line=dict(color="#9b59b6", width=2),
    ))
    fig.update_layout(
        **_base_layout(title="University of Michigan Consumer Sentiment"),
        yaxis_title="Index", height=340,
    )
    return fig


def unemployment_chart(unemp: pd.Series, recession: pd.Series = None) -> go.Figure:
    """Unemployment rate line chart with recession shading."""
    fig = go.Figure()
    if recession is not None and not recession.empty:
        _add_recession_shading(fig, recession, unemp.index)
    fig.add_trace(go.Scatter(
        x=unemp.index, y=unemp.values,
        name="Unemployment Rate", line=dict(color="#e74c3c", width=2),
        fill="tozeroy", fillcolor="rgba(231,76,60,0.08)",
    ))
    fig.update_layout(
        **_base_layout(title="U.S. Unemployment Rate (%)"),
        yaxis_title="%", height=360,
    )
    return fig


def employment_chart(emp: pd.Series, recession: pd.Series = None,
                     title: str = "Food Services & Drinking Places Employment",
                     y_title: str = "Thousands") -> go.Figure:
    """Industry employment chart."""
    fig = go.Figure()
    if recession is not None and not recession.empty:
        _add_recession_shading(fig, recession, emp.index)
    fig.add_trace(go.Scatter(
        x=emp.index, y=emp.values,
        name="Employment",
        line=dict(color="#2980b9", width=2),
        fill="tozeroy", fillcolor="rgba(41,128,185,0.08)",
    ))
    fig.update_layout(
        **_base_layout(title=title),
        yaxis_title=y_title, height=360,
    )
    return fig


def fed_funds_chart(fed: pd.Series, recession: pd.Series = None) -> go.Figure:
    """Federal Funds effective rate."""
    fig = go.Figure()
    if recession is not None and not recession.empty:
        _add_recession_shading(fig, recession, fed.index)
    fig.add_trace(go.Scatter(
        x=fed.index, y=fed.values,
        name="Fed Funds Rate",
        line=dict(color="#8e44ad", width=2),
    ))
    fig.add_hline(y=0, line_color="rgba(0,0,0,0.2)", line_width=1, opacity=0.6)
    fig.update_layout(
        **_base_layout(title="Federal Funds Effective Rate (%)"),
        yaxis_title="%", height=340,
    )
    return fig


def job_openings_chart(openings: pd.Series, recession: pd.Series = None,
                       title: str = "Job Openings: Accommodation & Food Services") -> go.Figure:
    """Job openings chart."""
    fig = go.Figure()
    if recession is not None and not recession.empty:
        _add_recession_shading(fig, recession, openings.index)
    fig.add_trace(go.Bar(
        x=openings.index, y=openings.values,
        name="Job Openings",
        marker_color="#1abc9c", opacity=0.8,
        hovertemplate="%{x|%b %Y}: %{y:.0f}K<extra></extra>",
    ))
    fig.update_layout(
        **_base_layout(title=title),
        yaxis_title="Thousands", height=340,
    )
    return fig


def _add_recession_shading(fig: go.Figure, recession: pd.Series, ref_index: pd.DatetimeIndex):
    """Add NBER recession bands to a figure."""
    rec = recession.reindex(ref_index, method="ffill").fillna(0)
    in_rec = False
    start = None
    for date, val in rec.items():
        if val == 1 and not in_rec:
            in_rec = True
            start = date
        elif val == 0 and in_rec:
            in_rec = False
            fig.add_vrect(
                x0=start, x1=date,
                fillcolor="rgba(200,200,200,0.12)",
                layer="below", line_width=0,
                annotation_text="Recession", annotation_position="top left",
                annotation_font_size=9,
            )
    if in_rec and start:
        fig.add_vrect(
            x0=start, x1=rec.index[-1],
            fillcolor="rgba(200,200,200,0.12)",
            layer="below", line_width=0,
        )


# ── Revenue / margin charts ────────────────────────────────────────────────

def revenue_bar_chart(df: pd.DataFrame, colors: dict) -> go.Figure:
    """Horizontal bar chart of TTM revenue by company."""
    df_s = df.sort_values("Revenue ($B)", ascending=True)
    bar_colors = [colors.get(t, "#888") for t in df_s.index]
    fig = go.Figure(go.Bar(
        x=df_s["Revenue ($B)"],
        y=df_s.index,
        orientation="h",
        marker_color=bar_colors,
        hovertemplate="<b>%{y}</b>: $%{x:.1f}B<extra></extra>",
    ))
    fig.update_layout(
        **_base_layout(title="TTM Revenue ($B)"),
        xaxis_title="Revenue ($B)", height=420,
    )
    return fig


def margin_chart(df: pd.DataFrame, colors: dict, metric: str, title: str) -> go.Figure:
    """Bar chart of a margin metric by company."""
    df_s = df.sort_values(metric, ascending=True).dropna(subset=[metric])
    bar_colors = [colors.get(t, "#888") for t in df_s.index]
    fig = go.Figure(go.Bar(
        x=df_s[metric],
        y=df_s.index,
        orientation="h",
        marker_color=bar_colors,
        hovertemplate=f"<b>%{{y}}</b>: %{{x:.1f}}%<extra></extra>",
    ))
    fig.update_layout(
        **_base_layout(title=title),
        xaxis_title="%", height=420,
    )
    return fig


# ── Box Office charts ─────────────────────────────────────────────────────

def weekly_bo_chart(
    current: pd.DataFrame,
    prior: pd.DataFrame | None = None,
    title: str = "Weekly Combined Weekend Box Office",
) -> go.Figure:
    """
    Bar chart of weekly combined weekend BO with optional prior-year line overlay.
    current/prior: DataFrames with 'weekend_date' and 'combined_gross' columns.
    """
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=current["weekend_date"],
        y=current["combined_gross"],
        name=str(current["weekend_date"].dt.year.iloc[0]) if not current.empty else "Current",
        marker_color="#1565C0",
        hovertemplate="%{x|%b %d}: $%{y:,.0f}<extra></extra>",
    ))

    if prior is not None and not prior.empty:
        # Shift prior year dates forward by ~52 weeks to align on same x-axis position
        prior_shifted = prior.copy()
        year_diff = current["weekend_date"].dt.year.iloc[0] - prior["weekend_date"].dt.year.iloc[0]
        prior_shifted["weekend_date"] = prior["weekend_date"] + pd.DateOffset(years=year_diff)
        fig.add_trace(go.Scatter(
            x=prior_shifted["weekend_date"],
            y=prior_shifted["combined_gross"],
            name=str(prior["weekend_date"].dt.year.iloc[0]),
            line=dict(color="#e67e22", width=2.5, dash="dot"),
            hovertemplate="%{x|%b %d}: $%{y:,.0f}<extra></extra>",
        ))

    fig.update_layout(
        **_base_layout(title=title),
        yaxis_title="Weekend BO ($)",
        yaxis_tickformat="$,.0s",
        height=440,
        legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="left", x=0),
    )
    return fig


def annual_bo_chart(df: pd.DataFrame, title: str = "Annual Domestic Box Office") -> go.Figure:
    """
    Bar chart of annual domestic BO with tickets sold line overlay.
    df: DataFrame with 'Year', 'Total BO', 'Tickets Sold', 'Avg Ticket Price'.
    """
    from plotly.subplots import make_subplots

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(
            x=df["Year"], y=df["Total BO"],
            name="Total Box Office",
            marker_color="#1565C0",
            hovertemplate="%{x}: $%{y:,.0f}<extra></extra>",
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=df["Year"], y=df["Tickets Sold"],
            name="Tickets Sold",
            line=dict(color="#e67e22", width=2.5),
            hovertemplate="%{x}: %{y:,.0f}<extra></extra>",
        ),
        secondary_y=True,
    )

    base = _base_layout(title=title)
    base.pop("yaxis", None)
    fig.update_layout(
        **base,
        height=440,
        legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="left", x=0),
    )
    fig.update_yaxes(title_text="Total Box Office ($)", tickformat="$,.0s", secondary_y=False)
    fig.update_yaxes(title_text="Tickets Sold", tickformat=",.0s", secondary_y=True)
    return fig


def ytd_pacing_chart(
    years_data: dict,
    title: str = "YTD Box Office Pacing",
) -> go.Figure:
    """
    Cumulative weekly BO for multiple years plotted on the same week-number axis.
    years_data: {year_int: DataFrame with 'weekend_date' and 'combined_gross'}.
    """
    colors = {2026: "#1565C0", 2025: "#e67e22", 2024: "#2ecc71", 2019: "#95a5a6",
              2023: "#9b59b6", 2022: "#e74c3c", 2021: "#34495e"}
    fig = go.Figure()

    for year, df in sorted(years_data.items(), reverse=True):
        if df.empty:
            continue
        df_sorted = df.sort_values("weekend_date")
        cumulative = df_sorted["combined_gross"].cumsum()
        week_nums = range(1, len(cumulative) + 1)
        color = colors.get(year, "#888888")
        width = 3 if year == max(years_data.keys()) else 2
        dash = None if year == max(years_data.keys()) else "dot" if year < 2020 else None

        fig.add_trace(go.Scatter(
            x=list(week_nums),
            y=cumulative.values,
            name=str(year),
            line=dict(color=color, width=width, dash=dash),
            hovertemplate=f"{year} Week %{{x}}: $%{{y:,.0f}}<extra></extra>",
        ))

    fig.update_layout(
        **_base_layout(title=title),
        xaxis_title="Week of Year",
        yaxis_title="Cumulative BO ($)",
        yaxis_tickformat="$,.0s",
        height=440,
        legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="left", x=0),
    )
    return fig


# ── Gaming GGR charts ─────────────────────────────────────────────────────

def ggr_trend_chart(
    revenue: pd.Series,
    title: str = "US Gambling Industry Revenue (Quarterly)",
) -> go.Figure:
    """
    Quarterly gambling revenue bar chart with YoY% line overlay.
    revenue: pd.Series with DatetimeIndex and dollar values.
    """
    from plotly.subplots import make_subplots

    yoy = revenue.pct_change(4).dropna() * 100  # 4 quarters = 1 year
    # Align to common dates
    common = yoy.index.intersection(revenue.index)
    rev_aligned = revenue.loc[common]
    yoy_aligned = yoy.loc[common]

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(
            x=rev_aligned.index, y=rev_aligned.values,
            name="Revenue ($)",
            marker_color="#1ABC9C",
            hovertemplate="%{x|%Y Q}: $%{y:,.0f}<extra></extra>",
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=yoy_aligned.index, y=yoy_aligned.values,
            name="YoY %",
            line=dict(color="#e74c3c", width=2.5),
            hovertemplate="%{x|%Y Q}: %{y:.1f}%<extra></extra>",
        ),
        secondary_y=True,
    )

    base = _base_layout(title=title)
    base.pop("yaxis", None)
    fig.update_layout(
        **base,
        height=440,
        legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="left", x=0),
    )
    fig.update_yaxes(title_text="Revenue ($)", tickformat="$,.0s", secondary_y=False)
    fig.update_yaxes(title_text="YoY %", secondary_y=True)
    fig.add_hline(y=0, line_color="rgba(0,0,0,0.2)", line_width=1, secondary_y=True)
    return fig


def state_ggr_bar_chart(
    df: pd.DataFrame,
    value_col: str,
    title: str = "Revenue by State",
    color: str = "#003087",
) -> go.Figure:
    """Horizontal bar chart of state-level gaming revenue, sorted descending."""
    df_sorted = df.sort_values(value_col, ascending=True).tail(20)  # Top 20

    fig = go.Figure(go.Bar(
        x=df_sorted[value_col],
        y=df_sorted.iloc[:, 0],  # First column = state name
        orientation="h",
        marker_color=color,
        hovertemplate="<b>%{y}</b>: $%{x:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        **_base_layout(title=title),
        xaxis_title="Revenue ($)",
        xaxis_tickformat="$,.0s",
        height=max(400, len(df_sorted) * 28),
    )
    return fig


# ── Hotel KPI charts ─────────────────────────────────────────────────────

def hotel_revpar_grouped_bar(df: pd.DataFrame, colors: dict,
                             title: str = "RevPAR by Company ($)") -> go.Figure:
    """Grouped bar chart of RevPAR by quarter and company."""
    fig = go.Figure()
    for ticker in df.columns:
        fig.add_trace(go.Bar(
            x=df.index, y=df[ticker], name=ticker,
            marker_color=colors.get(ticker, None),
            hovertemplate=f"<b>{ticker}</b>: $%{{y:.0f}}<extra></extra>",
        ))
    fig.update_layout(
        **_base_layout(title=title),
        barmode="group", yaxis_title="RevPAR ($)", yaxis_tickprefix="$",
        legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="left", x=0),
        height=420,
    )
    return fig


def hotel_revpar_yoy_chart(df: pd.DataFrame, colors: dict,
                           title: str = "RevPAR YoY Change (%)") -> go.Figure:
    """Grouped bar chart of RevPAR YoY % change."""
    fig = go.Figure()
    for ticker in df.columns:
        fig.add_trace(go.Bar(
            x=df.index, y=df[ticker], name=ticker,
            marker_color=colors.get(ticker, None),
            hovertemplate=f"<b>{ticker}</b>: %{{y:+.1f}}%<extra></extra>",
        ))
    fig.add_hline(y=0, line_color="rgba(0,0,0,0.2)", line_width=1, opacity=0.6)
    fig.update_layout(
        **_base_layout(title=title),
        barmode="group", yaxis_title="YoY %",
        legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="left", x=0),
        height=420,
    )
    return fig


def hotel_occ_line_chart(df: pd.DataFrame, colors: dict,
                         title: str = "Occupancy Rate (%)") -> go.Figure:
    """Line chart of occupancy rate over time."""
    fig = go.Figure()
    for ticker in df.columns:
        s = df[ticker].dropna()
        fig.add_trace(go.Scatter(
            x=s.index, y=s.values, name=ticker,
            mode="lines+markers",
            line=dict(color=colors.get(ticker), width=2),
            marker=dict(size=6),
            hovertemplate=f"<b>{ticker}</b> %{{x}}: %{{y:.1f}}%<extra></extra>",
        ))
    fig.update_layout(
        **_base_layout(title=title),
        yaxis_title="Occupancy %",
        legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="left", x=0),
        height=400,
    )
    return fig


def hotel_adr_occ_chart(
    df: pd.DataFrame, ticker: str, color: str,
    quarters: list | None = None,
) -> go.Figure:
    """Stacked bar: ADR vs occupancy contribution to RevPAR change."""
    valid = df.dropna(subset=["adr_yoy", "occ_chg"])
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=valid["quarter"], y=valid["adr_yoy"],
        name="ADR", marker_color=color, opacity=0.85,
        hovertemplate="ADR: %{y:+.1f}%<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=valid["quarter"], y=valid["occ_chg"],
        name="Occupancy (pp)", marker_color="#95a5a6",
        hovertemplate="Occ: %{y:+.1f}pp<extra></extra>",
    ))
    fig.add_hline(y=0, line_color="rgba(0,0,0,0.2)", line_width=1, opacity=0.6)
    layout_kw = {
        **_base_layout(title=f"{ticker} \u2013 ADR vs. Occupancy Contribution"),
        "barmode": "group",
        "yaxis_title": "YoY Change",
        "height": 360,
    }
    if quarters:
        layout_kw["xaxis"] = dict(
            categoryorder="array", categoryarray=quarters, type="category",
        )
    fig.update_layout(**layout_kw)
    return fig
