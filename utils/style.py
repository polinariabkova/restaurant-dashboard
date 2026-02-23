"""
Global CSS injection for the Arini Restaurant KPI Dashboard.
Call inject_css() once per page, right after st.set_page_config().
"""

import streamlit as st


def inject_css() -> None:
    st.markdown("""
<style>
/* ── Section headers (st.header → h2, st.subheader → h3) ────────────────── */
h2 {
    background-color: #0D2B55 !important;
    color: #ffffff !important;
    padding: 8px 18px !important;
    border-radius: 7px !important;
    margin-top: 1.2rem !important;
    margin-bottom: 0.8rem !important;
    font-size: 1.25rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.02em;
}

h3 {
    background-color: #0D2B55 !important;
    color: #ffffff !important;
    padding: 6px 16px !important;
    border-radius: 6px !important;
    margin-top: 1rem !important;
    margin-bottom: 0.6rem !important;
    font-size: 1.05rem !important;
    font-weight: 600 !important;
}

/* ── Page title (st.title → h1) — keep dark navy text, no background ──────── */
h1 {
    color: #0D2B55 !important;
    font-weight: 800 !important;
    margin-top: 0.4rem !important;
    margin-bottom: 0.4rem !important;
}

/* ── Sidebar header ────────────────────────────────────────────────────────── */
[data-testid="stSidebarHeader"] h2,
section[data-testid="stSidebar"] h2 {
    background-color: transparent !important;
    color: #0D2B55 !important;
    padding: 0 !important;
    border-radius: 0 !important;
}

/* ── Tab labels ────────────────────────────────────────────────────────────── */
button[data-baseweb="tab"] {
    color: #0D2B55 !important;
    font-weight: 600 !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #1565C0 !important;
    border-bottom: 3px solid #1565C0 !important;
}

/* ── Dataframe / table header cells ───────────────────────────────────────── */
th {
    background-color: #E3EDF7 !important;
    color: #0D2B55 !important;
    font-weight: 700 !important;
    border-bottom: 2px solid #B8D4ED !important;
}

/* ── st.metric label ──────────────────────────────────────────────────────── */
[data-testid="stMetricLabel"] {
    color: #0D2B55 !important;
    font-weight: 600 !important;
}

/* ── st.caption ────────────────────────────────────────────────────────────── */
[data-testid="stCaptionContainer"] p {
    color: #1A3A6B !important;
}

/* ── Container borders ────────────────────────────────────────────────────── */
[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1.5px solid #B8D4ED !important;
    border-radius: 8px !important;
}

/* ══════════════════════════════════════════════════════════════════════════ */
/* Industry navigation — full-width button bar (st.columns + st.button)    */
/* ══════════════════════════════════════════════════════════════════════════ */

/* ── Reduce top padding in main content area ──────────────────────────── */
.block-container {
    padding-top: 4.2rem !important;
}

/* ── Sticky industry nav bar ─────────────────────────────────────────── */
/* Target the wrapper div that contains a 5-column horizontal block      */
/* (the industry selector always renders 5 columns — one per industry).  */
/* Uses :has() to positively identify the nav row vs other column groups. */
div:has(> [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(5)) {
    position: sticky !important;
    top: 3.75rem !important;
    z-index: 999 !important;
    background: white !important;
    padding: 0.3rem 0 0.5rem 0 !important;
}

/* ── Logo: fill full navbar / sidebar header height ───────────────────── */
[data-testid="stSidebarHeader"] {
    min-height: 72px !important;
    display: flex !important;
    align-items: center !important;
    padding: 8px 16px !important;
}

[data-testid="stSidebarHeader"] img,
[data-testid="stLogo"] img {
    height: 60px !important;
    max-height: 72px !important;
    width: auto !important;
    object-fit: contain !important;
}

/* Main header logo (top bar) */
[data-testid="stHeader"] [data-testid="stLogo"] {
    display: flex !important;
    align-items: center !important;
    height: 100% !important;
}

[data-testid="stHeader"] [data-testid="stLogo"] img {
    height: 48px !important;
    width: auto !important;
    object-fit: contain !important;
}

/* ── Industry nav row: the first horizontal block of columns ──────────── */
/* Target the column container that holds our industry buttons.           */
/* These are Streamlit's native st.button elements inside st.columns.     */

/* ── Make all industry buttons same height and styled ─────────────────── */
/* Primary (active) button */
[data-testid="stButton"] button[kind="primary"] {
    background-color: #1565C0 !important;
    border: 2px solid #42a5f5 !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 1.0rem !important;
    letter-spacing: 0.02em !important;
    padding: 12px 8px !important;
    border-radius: 7px !important;
    box-shadow: 0 2px 10px rgba(21, 101, 192, 0.4) !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}

/* Secondary (inactive) button */
[data-testid="stButton"] button[kind="secondary"] {
    background-color: #0D2B55 !important;
    border: 2px solid #1a3d6e !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 1.0rem !important;
    letter-spacing: 0.02em !important;
    padding: 12px 8px !important;
    border-radius: 7px !important;
    opacity: 0.7 !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    transition: opacity 0.15s ease, border-color 0.15s ease,
                box-shadow 0.15s ease !important;
}

[data-testid="stButton"] button[kind="secondary"]:hover {
    opacity: 0.9 !important;
    border-color: #2a5f9e !important;
    box-shadow: 0 2px 8px rgba(13, 43, 85, 0.3) !important;
}

/* ── Tighten gap between columns holding nav buttons ──────────────────── */
[data-testid="stHorizontalBlock"]:first-child {
    gap: 0.4rem !important;
}
</style>
""", unsafe_allow_html=True)
