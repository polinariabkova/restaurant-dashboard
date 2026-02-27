"""
Movie Theaters industry configuration.
"""

CONFIG = {
    "name": "Movie Theaters",
    "icon": "\U0001f3ac",  # clapper board

    "page_titles": {
        "stocks":       "Stock Performance",
        "kpis":         "Box Office & KPIs",
        "market":       "Market Drivers",
        "fundamentals": "Fundamentals",
        "macro":        "Movie Industry & Macro",
        "news":         "Movie Industry News",
    },

    "companies": {
        "CNK":  {"name": "Cinemark",       "segment": "Exhibitors", "color": "#E74C3C"},
        "IMAX": {"name": "IMAX Corp",      "segment": "Technology", "color": "#2C3E50"},
        "AMC":  {"name": "AMC Entertainment", "segment": "Exhibitors", "color": "#F39C12"},
    },

    "segments": {
        "Exhibitors": ["CNK", "AMC"],
        "Technology": ["IMAX"],
    },

    "segment_colors": {
        "Exhibitors": "#E74C3C",
        "Technology": "#2C3E50",
    },

    "fred_series": {
        # Universal
        "cpi_all":             "CPIAUCSL",
        "recession":           "USREC",
        "consumer_sentiment":  "UMCSENT",
        "unemployment":        "UNRATE",
        "fed_funds":           "FEDFUNDS",
        # Industry-specific
        "cpi_industry_1":      "CUSR0000SS62031",   # CPI Movie Admissions
        "cpi_industry_2":      None,
        "wages":               "CES7000000008",     # Avg Hourly Earnings: L&H
        "industry_employment": "CES5051200001",     # Motion Picture & Sound Recording Employment
        "job_openings":        None,
        "industry_kpi":        None,
    },

    "commodity_futures": {
        "Corn":        "ZC=F",
        "Soybean Oil": "ZL=F",
    },

    "commodity_units": {
        "Corn":        "\u00a2/bu",
        "Soybean Oil": "\u00a2/lb",
    },

    "commodity_meta": {
        "Corn":        {"emoji": "\U0001f33d", "category": "Concessions", "color": "#F4D03F"},
        "Soybean Oil": {"emoji": "\U0001fad8", "category": "Concessions", "color": "#A8B820"},
    },

    # FRED PPI series for theater input costs
    "input_cost_fred": {
        "Industrial Electricity":  "WPU0543",       # PPI Industrial Electric Power
        "Confectionery Products":  "WPU0213",       # PPI Confectionery & Cocoa Products
    },

    # Impact notes: how each input cost affects companies in coverage
    "input_cost_notes": {
        "Corn": (
            "Primary raw material for popcorn — the single highest-margin concession "
            "item for all exhibitors. Popcorn is 60-80% gross margin for CNK and AMC. "
            "Corn price spikes compress concession margins but the impact is modest "
            "relative to ticket revenue."
        ),
        "Soybean Oil": (
            "Cooking/popping oil for concession items. CNK and AMC use it for popcorn "
            "preparation and other hot concession items. IMAX is less exposed as it "
            "licenses technology rather than operating concessions directly."
        ),
        "Industrial Electricity": (
            "Theaters are energy-intensive (projection, HVAC, lighting). CNK operates "
            "~500+ theaters and AMC ~900+ locations — utility costs are a material "
            "component of facility operating expenses for both. IMAX projector systems "
            "are also high-wattage."
        ),
        "Confectionery Products": (
            "Candy and chocolate are top concession items by volume. CNK and AMC "
            "purchase from major confectionery distributors. Rising cocoa/sugar prices "
            "flow through to wholesale confectionery costs."
        ),
    },

    "has_sss": False,
    "has_commodities": True,
    "has_beef_chicken": False,

    "macro_labels": {
        "cpi_industry_1_label": "CPI Movie Admissions",
        "cpi_industry_2_label": None,
        "wages_label":          "L&H Wages",
        "employment_label":     "Motion Picture Employment",
        "industry_section_title": "Box Office & Admissions",
        "cpi_chart_title":      "CPI: Movie, Theater & Concert Admissions (YoY %)",
        "cpi_label_1":          "Movie Admissions",
        "cpi_label_2":          None,
        "cpi_chart_caption":    (
            "CPI Movie Admissions tracks ticket price inflation. "
            "Rising admissions CPI can signal pricing power or "
            "reflect premium format (IMAX, Dolby) mix shift."
        ),
        "wages_chart_title":    "Avg Hourly Earnings \u2013 Leisure & Hospitality (YoY %)",
        "employment_chart_title": "Motion Picture & Sound Recording Employment",
        "employment_y_title":   "Thousands",
        "job_openings_chart_title": None,
        "employment_section_title": "Labor Market",
        "employment_caption":   (
            "Motion picture employment tracks staffing in entertainment "
            "production and exhibition. Seasonal patterns reflect release calendars."
        ),
    },

    "news": {
        "rss_feeds": {
            "Deadline Hollywood":  "https://deadline.com/feed/",
            "Variety":             "https://variety.com/feed/",
            "THR":                 "https://www.hollywoodreporter.com/feed/",
            "Reuters Business":    "https://feeds.reuters.com/reuters/businessNews",
            "MarketWatch":         "https://feeds.marketwatch.com/marketwatch/topstories/",
            "Seeking Alpha":       "https://seekingalpha.com/feed.xml",
            "CNBC":                "https://www.cnbc.com/id/10000664/device/rss/rss.html",
        },
        "industry_sources": {"Deadline Hollywood", "Variety", "THR"},
        "title_keywords": [
            "box office", "movie theater", "cinema", "multiplex", "exhibitor",
            "ticket sales", "movie admissions", "blockbuster", "film release",
            "streaming", "theatrical window", "IMAX", "premium large format",
            "concession", "screen count",
        ],
        "company_name_keywords": [
            "Cinemark", "IMAX", "AMC", "AMC Entertainment",
            "Regal", "Cineworld", "Marcus Theaters",
            "Alamo Drafthouse",
        ],
        "earnings_keywords": [
            "earnings", "quarterly results", "EPS", "revenue", "guidance",
            "box office", "attendance", "admissions", "profit",
            "beats estimates", "misses estimates",
        ],
        "ticker_map": {
            "cinemark": "CNK",
            "imax": "IMAX",
            "amc": "AMC", "amc entertainment": "AMC",
        },
        "private_companies": {
            "Regal":     ["Regal Cinemas", "Regal Entertainment"],
            "Cineworld": ["Cineworld"],
        },
    },
}
