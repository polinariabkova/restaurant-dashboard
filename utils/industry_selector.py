"""
Industry selector widget — renders a full-width button bar at the top of every page.
Uses st.columns + st.button for reliable layout control.
"""

import streamlit as st
from industry_configs import INDUSTRY_NAMES, get_industry_config, INDUSTRIES


def render_industry_selector() -> dict:
    """
    Render the industry selector as equal-width buttons across the full page
    width at the very top of the page.  Persists selection via st.session_state.
    Returns the active industry's full config dict.
    """
    if "active_industry" not in st.session_state:
        st.session_state.active_industry = "Restaurants"

    cols = st.columns(len(INDUSTRY_NAMES), gap="small")

    for i, name in enumerate(INDUSTRY_NAMES):
        icon = INDUSTRIES[name]["icon"]
        is_active = (st.session_state.active_industry == name)
        btn_type = "primary" if is_active else "secondary"
        with cols[i]:
            if st.button(
                f"{icon} {name}",
                key=f"ind_btn_{name}",
                width="stretch",
                type=btn_type,
            ):
                st.session_state.active_industry = name
                st.rerun()

    return get_industry_config(st.session_state.active_industry)
