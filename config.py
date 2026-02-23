"""
Central configuration for the Restaurant KPI Dashboard.
Thin shim that re-exports restaurant config for backward compatibility.
"""

from industry_configs.restaurants import CONFIG as _R

COMPANIES = _R["companies"]
TICKERS = list(_R["companies"].keys())

SEGMENTS = _R["segments"]

SEGMENT_COLORS = _R["segment_colors"]

# FRED series IDs (kept as original keys for backward compat with data_fetchers, sss_data, etc.)
FRED_SERIES = {
    "cpi_food_away":       "CUSR0000SEFV",
    "cpi_food_home":       "CUSR0000SAF11",
    "cpi_all":             "CPIAUCSL",
    "wages_leisure":       "CES7000000008",
    "beef_price":          "APU0000703112",
    "chicken_price":       "APU0000FF1101",
    "recession":           "USREC",
    "consumer_sentiment":  "UMCSENT",
    "unemployment":        "UNRATE",
    "food_services_emp":   "CES7072200001",
    "fed_funds":           "FEDFUNDS",
    "job_openings_food":   "JTS7200JOL",
}

COMMODITY_FUTURES = _R["commodity_futures"]

COMMODITY_UNITS = _R["commodity_units"]

COMMODITY_META = _R["commodity_meta"]

RETURN_PERIODS = {
    "1D":  "1d",
    "1W":  "5d",
    "1M":  "1mo",
    "3M":  "3mo",
    "YTD": "ytd",
    "1Y":  "1y",
}
