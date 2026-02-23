"""
Industry News — Multi-industry RSS news aggregator
Run with: streamlit run Industry_News.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import feedparser
import html as html_lib
from datetime import datetime, timezone, timedelta
import time
import re

from utils.industry_selector import render_industry_selector
from utils.style import inject_css

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Industry News",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.logo(os.path.join(os.path.dirname(__file__), "assets", "arini_logo.svg"))
inject_css()

# ── Industry selector (very top of page) ─────────────────────────────────
cfg = render_industry_selector()

COMPANIES = cfg["companies"]
TICKERS = list(COMPANIES.keys())
news_cfg = cfg["news"]

# ── Derive keyword lists from config ──────────────────────────────────────
RSS_FEEDS        = news_cfg["rss_feeds"]
INDUSTRY_SOURCES = news_cfg["industry_sources"]
PRIVATE_COMPANIES = news_cfg.get("private_companies", {})
TITLE_KEYWORDS    = news_cfg["title_keywords"]
COMPANY_NAME_KEYWORDS = (
    news_cfg["company_name_keywords"]
    + [kw for kws in PRIVATE_COMPANIES.values() for kw in kws]
)
EARNINGS_KEYWORDS = news_cfg.get("earnings_keywords", [
    "earnings", "quarterly results", "EPS", "revenue", "guidance",
    "beats estimates", "misses estimates", "profit",
])
TICKER_MAP = news_cfg.get("ticker_map", {})

COMPANY_LOWER  = [k.lower() for k in COMPANY_NAME_KEYWORDS]
TITLE_KW_LOWER = [k.lower() for k in TITLE_KEYWORDS]
EARNINGS_LOWER = [k.lower() for k in EARNINGS_KEYWORDS]


# ── Helpers ────────────────────────────────────────────────────────────────
def strip_html(raw: str) -> str:
    raw = re.sub(r"<(script|style)[^>]*>.*?</(script|style)>", "", raw,
                 flags=re.DOTALL | re.IGNORECASE)
    raw = re.sub(r"<!\[CDATA\[.*?\]\]>", "", raw, flags=re.DOTALL)
    raw = re.sub(r"<!--.*?-->", "", raw, flags=re.DOTALL)
    raw = re.sub(r"<[^>]+>", " ", raw)
    raw = html_lib.unescape(raw)
    raw = re.sub(r"\s+", " ", raw).strip()
    return raw


def is_relevant(title: str, summary: str) -> bool:
    tl = title.lower()
    sl = summary.lower()
    for kw in COMPANY_LOWER:
        if kw in tl or kw in sl:
            return True
    for kw in TITLE_KW_LOWER:
        if kw in tl:
            return True
    return False


def is_earnings(title: str, summary: str) -> bool:
    text = (title + " " + summary).lower()
    has_earnings = any(kw in text for kw in EARNINGS_LOWER)
    has_company  = any(kw in text for kw in COMPANY_LOWER)
    return has_earnings and has_company


def tag_tickers(title: str, summary: str) -> list:
    text = (title + " " + summary).lower()
    tags = []
    for kw, ticker in TICKER_MAP.items():
        if kw in text and ticker not in tags:
            tags.append(ticker)
    return tags


def parse_date(entry) -> int:
    for field in ("published_parsed", "updated_parsed", "created_parsed"):
        t = getattr(entry, field, None)
        if t:
            try:
                return int(time.mktime(t))
            except Exception:
                pass
    return 0


def time_ago(ts: int) -> str:
    if not ts:
        return ""
    diff = datetime.now(timezone.utc) - datetime.fromtimestamp(ts, tz=timezone.utc)
    s = diff.total_seconds()
    if s < 3600:
        return f"{max(1, int(s / 60))}m ago"
    elif s < 86400:
        return f"{int(s / 3600)}h ago"
    elif s < 86400 * 7:
        return f"{int(s / 86400)}d ago"
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%b %d")


# ── Fetch ──────────────────────────────────────────────────────────────────
@st.cache_data(ttl=1800, show_spinner=False)
def fetch_rss_news(feed_names: tuple, feed_urls: tuple) -> list[dict]:
    feeds = dict(zip(feed_names, feed_urls))
    seen = set()
    articles = []
    for source, url in feeds.items():
        if not url:
            continue
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                title   = strip_html(getattr(entry, "title",   "")).strip()
                summary = strip_html(getattr(entry, "summary", ""))
                link    = getattr(entry, "link", "")
                key     = title.lower()[:80]
                if not title or key in seen or not is_relevant(title, summary):
                    continue
                seen.add(key)
                articles.append({
                    "source":    source,
                    "title":     title,
                    "url":       link,
                    "summary":   summary[:300].strip(),
                    "timestamp": parse_date(entry),
                    "tickers":   tag_tickers(title, summary),
                    "earnings":  is_earnings(title, summary),
                })
        except Exception:
            continue
    articles.sort(key=lambda x: x["timestamp"], reverse=True)
    return articles


# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title(f"{cfg['icon']} {cfg['name']} Dashboard")
    st.caption("Hedge Fund Analytics")
    st.divider()
    selected_sources = st.multiselect(
        "News sources", list(RSS_FEEDS.keys()), default=list(RSS_FEEDS.keys()),
    )
    ticker_filter = st.multiselect(
        "Filter by company",
        TICKERS, default=[],
        format_func=lambda t: f"{t} – {COMPANIES[t]['name']}",
    )
    st.divider()
    st.caption(f"Refreshes every 30 min · {len(RSS_FEEDS)} sources")
    if st.button("Refresh now", width="stretch"):
        st.cache_data.clear()
        st.rerun()

# ── Fetch data ─────────────────────────────────────────────────────────────
st.title(f"📰 {cfg['name']} News")
st.caption(f"{cfg['name']} sector · {datetime.now().strftime('%A, %B %d %Y  %H:%M')}")

if not selected_sources:
    st.info("Select at least one source in the sidebar.")
    st.stop()

# Build feed tuples for cache key
feed_names = tuple(selected_sources)
feed_urls = tuple(RSS_FEEDS.get(s, "") for s in selected_sources)

with st.spinner("Scanning sources…"):
    all_articles = fetch_rss_news(feed_names, feed_urls)

if ticker_filter:
    all_articles = [a for a in all_articles if any(t in a["tickers"] for t in ticker_filter)]

if not all_articles:
    st.warning("No articles found. Sources may be temporarily unavailable.")
    st.stop()

two_weeks_ago = datetime.now(timezone.utc) - timedelta(days=14)
recent = [a for a in all_articles if a["timestamp"] and
          datetime.fromtimestamp(a["timestamp"], tz=timezone.utc) > two_weeks_ago]
earnings_articles = [a for a in all_articles if a["earnings"]]

# ── Layout ─────────────────────────────────────────────────────────────────
left_col, right_col = st.columns([3, 2], gap="large")

# ════════════════════════════════════════════════════════════
# LEFT — Bloomberg-style headline feed
# ════════════════════════════════════════════════════════════
with left_col:
    st.subheader(f"All Headlines  ({len(all_articles)})")
    st.caption("Click any headline to open the full article")
    st.markdown("---")

    def src_color(source):
        if source in INDUSTRY_SOURCES:
            return "#1a7a45"
        return "#1a4a7a"

    for a in all_articles:
        safe_title  = html_lib.escape(a["title"])
        safe_source = html_lib.escape(a["source"])
        url         = a["url"]
        ta          = time_ago(a["timestamp"])
        sc          = src_color(a["source"])

        badge_html = ""
        for t in a["tickers"]:
            c = COMPANIES.get(t, {}).get("color", "#555")
            badge_html += (
                f'<span style="background:{c};color:#fff;padding:0 5px;'
                f'border-radius:2px;font-size:0.65rem;font-weight:700;'
                f'margin-left:4px;">{t}</span>'
            )

        st.markdown(
            f"""<div style="padding:5px 0 5px 0;
                            border-bottom:1px solid rgba(128,128,128,0.2);
                            display:flex;align-items:flex-start;gap:8px;">
                  <span style="background:{sc};color:#fff;padding:1px 6px;
                               border-radius:2px;font-size:0.65rem;font-weight:700;
                               white-space:nowrap;margin-top:2px;flex-shrink:0;">
                    {safe_source[:20]}
                  </span>
                  <span style="flex:1;line-height:1.4;">
                    <a href="{url}" target="_blank"
                       style="color:#000000;text-decoration:none;font-size:0.9rem;
                              font-weight:600;">
                      {safe_title}
                    </a>{badge_html}
                  </span>
                  <span style="color:#333;font-size:0.72rem;white-space:nowrap;
                               margin-top:2px;flex-shrink:0;">{ta}</span>
                </div>""",
            unsafe_allow_html=True,
        )

# ════════════════════════════════════════════════════════════
# RIGHT — Earnings box + Recent headlines box
# ════════════════════════════════════════════════════════════
with right_col:

    with st.container(border=True):
        st.markdown("**Earnings & Company Results**")
        if not earnings_articles:
            st.caption("No earnings articles in the current feed.")
        else:
            st.caption(f"{len(earnings_articles)} articles")
            for a in earnings_articles[:20]:
                safe_title  = html_lib.escape(a["title"])
                safe_source = html_lib.escape(a["source"])
                safe_summary = html_lib.escape(a["summary"])
                url = a["url"]
                ta  = time_ago(a["timestamp"])

                badge_html = ""
                for t in a["tickers"]:
                    c = COMPANIES.get(t, {}).get("color", "#555")
                    badge_html += (
                        f'<span style="background:{c};color:#fff;padding:0 5px;'
                        f'border-radius:2px;font-size:0.63rem;font-weight:700;'
                        f'margin-right:3px;">{t}</span>'
                    )

                st.markdown(
                    f"""<div style="padding:7px 0;border-bottom:1px solid rgba(128,128,128,0.15);">
                          <div style="margin-bottom:3px;">{badge_html}</div>
                          <a href="{url}" target="_blank"
                             style="color:#000000;text-decoration:none;
                                    font-size:0.88rem;font-weight:700;line-height:1.4;">
                            {safe_title}
                          </a>
                          <p style="color:#111111;font-size:0.78rem;margin:4px 0 0 0;
                                    line-height:1.4;">
                            {safe_summary[:180]}{"…" if len(safe_summary) > 180 else ""}
                          </p>
                          <div style="color:#333;font-size:0.72rem;margin-top:3px;">
                            <b style="color:#222;">{safe_source}</b> · {ta}
                          </div>
                        </div>""",
                    unsafe_allow_html=True,
                )

    st.markdown("")

    with st.container(border=True):
        st.markdown("**Top Stories — Last 2 Weeks**")
        if not recent:
            st.caption("No articles from the past 14 days found.")
        else:
            st.caption(f"{len(recent)} articles in the past 14 days")
            for a in recent[:25]:
                safe_title   = html_lib.escape(a["title"])
                safe_source  = html_lib.escape(a["source"])
                safe_summary = html_lib.escape(a["summary"])
                url = a["url"]
                ta  = time_ago(a["timestamp"])

                badge_html = ""
                for t in a["tickers"]:
                    c = COMPANIES.get(t, {}).get("color", "#555")
                    badge_html += (
                        f'<span style="background:{c};color:#fff;padding:0 5px;'
                        f'border-radius:2px;font-size:0.63rem;font-weight:700;'
                        f'margin-right:3px;">{t}</span>'
                    )

                st.markdown(
                    f"""<div style="padding:7px 0;border-bottom:1px solid rgba(128,128,128,0.15);">
                          <div style="margin-bottom:3px;">{badge_html}</div>
                          <a href="{url}" target="_blank"
                             style="color:#000000;text-decoration:none;
                                    font-size:0.88rem;font-weight:700;line-height:1.4;">
                            {safe_title}
                          </a>
                          <p style="color:#111111;font-size:0.78rem;margin:4px 0 0 0;
                                    line-height:1.4;">
                            {safe_summary[:180]}{"…" if len(safe_summary) > 180 else ""}
                          </p>
                          <div style="color:#333;font-size:0.72rem;margin-top:3px;">
                            <b style="color:#222;">{safe_source}</b> · {ta}
                          </div>
                        </div>""",
                    unsafe_allow_html=True,
                )
