"""
Leisure (Hotels, Cruise Lines, Theme Parks, Entertainment) industry configuration.
"""

CONFIG = {
    "name": "Leisure",
    "icon": "\U0001f3a1",  # ferris wheel

    "page_titles": {
        "stocks":       "Stock Performance",
        "kpis":         "Travel & Leisure KPIs",
        "market":       "Market Drivers",
        "fundamentals": "Fundamentals",
        "macro":        "Travel & Leisure Macro",
        "news":         "Leisure News",
    },

    "companies": {
        # Hotels & Lodging
        "MAR":    {"name": "Marriott International",   "segment": "Hotels & Lodging",       "color": "#A4123F"},
        "HLT":    {"name": "Hilton Worldwide",         "segment": "Hotels & Lodging",       "color": "#003B73"},
        "H":      {"name": "Hyatt Hotels",             "segment": "Hotels & Lodging",       "color": "#C8A962"},
        "WH":     {"name": "Wyndham Hotels & Resorts", "segment": "Hotels & Lodging",       "color": "#00A1E4"},
        "CHH":    {"name": "Choice Hotels",            "segment": "Hotels & Lodging",       "color": "#004B8D"},
        "PK":     {"name": "Park Hotels & Resorts",    "segment": "Hotels & Lodging",       "color": "#6B4C3B"},
        # Cruise Lines
        "RCL":    {"name": "Royal Caribbean",          "segment": "Cruise Lines",           "color": "#00205B"},
        "CCL":    {"name": "Carnival Corporation",     "segment": "Cruise Lines",           "color": "#0054A6"},
        "NCLH":   {"name": "Norwegian Cruise Line",    "segment": "Cruise Lines",           "color": "#003366"},
        "VIK":    {"name": "Viking Holdings",          "segment": "Cruise Lines",           "color": "#8B0000"},
        # Theme Parks & Attractions
        "DIS":    {"name": "Walt Disney",              "segment": "Theme Parks & Attractions", "color": "#0057B8"},
        "FUN":    {"name": "Six Flags Entertainment",  "segment": "Theme Parks & Attractions", "color": "#E31837"},
        "PRKS":   {"name": "United Parks & Resorts",   "segment": "Theme Parks & Attractions", "color": "#0077C8"},
        "MTN":    {"name": "Vail Resorts",             "segment": "Theme Parks & Attractions", "color": "#005A9E"},
        # Vacation & Travel
        "VAC":    {"name": "Marriott Vacations",       "segment": "Vacation & Travel",      "color": "#9C1B2E"},
        "TNL":    {"name": "Travel + Leisure Co",      "segment": "Vacation & Travel",      "color": "#E85B24"},
        "HGV":    {"name": "Hilton Grand Vacations",   "segment": "Vacation & Travel",      "color": "#1A3C6E"},
        "TRIP":   {"name": "TripAdvisor",              "segment": "Vacation & Travel",      "color": "#00AF87"},
        # Entertainment
        "LYV":    {"name": "Live Nation",              "segment": "Entertainment",          "color": "#E3032E"},
        "SPHR":   {"name": "Sphere Entertainment",     "segment": "Entertainment",          "color": "#6C2DC7"},
        "PLAY":   {"name": "Dave & Buster's",          "segment": "Entertainment",          "color": "#D2232A"},
        "LUCK":   {"name": "Lucky Strike Entertainment", "segment": "Entertainment",        "color": "#1C8841"},
        "SHCO":   {"name": "Soho House",               "segment": "Entertainment",          "color": "#2D2D2D"},
    },

    "segments": {
        "Hotels & Lodging":          ["MAR", "HLT", "H", "WH", "CHH", "PK"],
        "Cruise Lines":              ["RCL", "CCL", "NCLH", "VIK"],
        "Theme Parks & Attractions": ["DIS", "FUN", "PRKS", "MTN"],
        "Vacation & Travel":         ["VAC", "TNL", "HGV", "TRIP"],
        "Entertainment":             ["LYV", "SPHR", "PLAY", "LUCK", "SHCO"],
    },

    "segment_colors": {
        "Hotels & Lodging":          "#003B73",
        "Cruise Lines":              "#00205B",
        "Theme Parks & Attractions": "#0057B8",
        "Vacation & Travel":         "#E85B24",
        "Entertainment":             "#E3032E",
    },

    "fred_series": {
        # Universal
        "cpi_all":             "CPIAUCSL",
        "recession":           "USREC",
        "consumer_sentiment":  "UMCSENT",
        "unemployment":        "UNRATE",
        "fed_funds":           "FEDFUNDS",
        # Industry-specific
        "cpi_industry_1":      "PCU7131107131101",  # PPI Theme Park Admissions
        "cpi_industry_2":      "CUSR0000SEHC01",    # CPI Lodging Away from Home
        "wages":               "CES7000000008",     # Avg Hourly Earnings: L&H
        "industry_employment": "CES7071000001",     # Arts, Entertainment & Recreation Employment
        "job_openings":        None,
        "industry_kpi":        None,
    },

    "commodity_futures": {
        "Crude Oil":   "CL=F",
        "Natural Gas": "NG=F",
    },

    "commodity_units": {
        "Crude Oil":   "$/bbl",
        "Natural Gas": "$/MMBtu",
    },

    "commodity_meta": {
        "Crude Oil":   {"emoji": "\U0001f6e2\ufe0f", "category": "Energy", "color": "#2C3E50"},
        "Natural Gas": {"emoji": "\U0001f525",        "category": "Energy", "color": "#E74C3C"},
    },

    # FRED PPI series for leisure input costs
    "input_cost_fred": {
        "Diesel Fuel":             "WPU057303",      # PPI No. 2 Diesel Fuel
        "Industrial Electricity":  "WPU0543",        # PPI Industrial Electric Power
        "Food Away from Home CPI": "CUSR0000SEFV",   # CPI Food Away from Home
    },

    # Impact notes: how each input cost affects companies in coverage
    "input_cost_notes": {
        "Crude Oil": (
            "Bunker fuel is the largest single operating cost for cruise lines. "
            "RCL, CCL, NCLH, and VIK each spend $1-2B+ annually on fuel. "
            "Also indirectly affects travel demand — higher gas prices reduce "
            "drive-to visitation at theme parks (DIS, FUN, PRKS) and resorts."
        ),
        "Natural Gas": (
            "Major utility cost for hotels (MAR, HLT, H, WH, CHH) for heating "
            "and water systems. Theme parks (DIS, FUN, PRKS) also use nat gas for "
            "facility operations. Ski resorts (MTN/Vail) use it for snowmaking support."
        ),
        "Diesel Fuel": (
            "Drives transportation costs for cruise line logistics, tour buses, "
            "and theme park fleet operations. Also a component of cruise ship fuel "
            "mix. CCL, RCL, and NCLH exposure is significant."
        ),
        "Industrial Electricity": (
            "Theme parks (DIS, FUN, PRKS) operate rides, lighting, and HVAC across "
            "massive footprints. Hotels (MAR, HLT) consume electricity for guest rooms "
            "and common areas. Live venues (LYV, SPHR) have intensive event-day power needs."
        ),
        "Food Away from Home CPI": (
            "F&B is a major revenue and cost line for cruise lines (RCL, CCL, NCLH), "
            "theme parks (DIS, FUN), and hotels (MAR, HLT, H). Rising food costs "
            "compress margins in on-site dining, buffets, and room service operations."
        ),
    },

    "has_sss": False,
    "has_commodities": True,
    "has_beef_chicken": False,

    "macro_labels": {
        "cpi_industry_1_label": "PPI Theme Park Admissions",
        "cpi_industry_2_label": "CPI Lodging Away from Home",
        "wages_label":          "L&H Wages",
        "employment_label":     "Arts/Entertainment Employment",
        "industry_section_title": "Pricing & Attendance",
        "cpi_chart_title":      "Theme Park Admissions PPI vs. Lodging CPI (YoY %)",
        "cpi_label_1":          "Theme Park Admissions",
        "cpi_label_2":          "Lodging Away from Home",
        "cpi_chart_caption":    (
            "**Theme park admission PPI** measures pricing trends for parks and attractions. "
            "**CPI Lodging** tracks hotel room pricing \u2014 a key indicator for hotel & resort operators."
        ),
        "wages_chart_title":    "Avg Hourly Earnings \u2013 Leisure & Hospitality (YoY %)",
        "employment_chart_title": "Arts, Entertainment & Recreation Employment",
        "employment_y_title":   "Thousands",
        "job_openings_chart_title": None,
        "employment_section_title": "Labor Market",
        "employment_caption":   (
            "Arts, entertainment, and recreation employment tracks staffing "
            "across theme parks, hotels, cruise lines, venues, and live events."
        ),
    },

    "news": {
        "rss_feeds": {
            "Theme Park Insider": "https://www.themeparkinsider.com/flume/rss",
            "Blooloop":           "https://blooloop.com/feed/",
            "Skift":              "https://skift.com/feed/",
            "Reuters Business":   "https://feeds.reuters.com/reuters/businessNews",
            "MarketWatch":        "https://feeds.marketwatch.com/marketwatch/topstories/",
            "Seeking Alpha":      "https://seekingalpha.com/feed.xml",
            "CNBC":               "https://www.cnbc.com/id/10000664/device/rss/rss.html",
        },
        "industry_sources": {"Theme Park Insider", "Blooloop", "Skift"},
        "title_keywords": [
            "theme park", "amusement park", "live entertainment", "live music",
            "concert", "ticket sales", "attendance", "venue", "resort",
            "season pass", "per capita spending", "roller coaster",
            "water park", "festival", "touring",
            "hotel", "lodging", "RevPAR", "occupancy", "ADR",
            "cruise", "cruise line", "cruise ship", "booking",
            "timeshare", "vacation ownership", "ski resort",
            "travel", "tourism",
        ],
        "company_name_keywords": [
            # Hotels
            "Marriott", "Hilton", "Hyatt", "Wyndham", "Choice Hotels",
            "Park Hotels",
            # Cruises
            "Royal Caribbean", "Carnival", "Norwegian Cruise", "Viking",
            # Theme Parks
            "Walt Disney", "Disney Parks", "Six Flags", "Cedar Fair",
            "United Parks", "SeaWorld", "Busch Gardens", "Vail Resorts",
            # Vacation
            "Marriott Vacations", "Travel + Leisure", "Hilton Grand Vacations",
            "TripAdvisor",
            # Entertainment
            "Live Nation", "Ticketmaster", "Sphere Entertainment",
            "Dave & Buster", "Lucky Strike", "Soho House",
            # Private
            "Universal Studios", "Merlin Entertainments",
        ],
        "earnings_keywords": [
            "earnings", "quarterly results", "EPS", "revenue", "guidance",
            "attendance", "per capita", "RevPAR", "occupancy", "ADR",
            "beats estimates", "misses estimates", "profit",
            "season pass", "booking", "yield",
        ],
        "ticker_map": {
            # Hotels
            "marriott": "MAR", "hilton": "HLT", "hyatt": "H",
            "wyndham": "WH", "choice hotels": "CHH", "park hotels": "PK",
            # Cruises
            "royal caribbean": "RCL", "carnival": "CCL",
            "norwegian cruise": "NCLH", "viking": "VIK",
            # Theme Parks
            "disney": "DIS", "walt disney": "DIS", "disney parks": "DIS",
            "six flags": "FUN", "cedar fair": "FUN",
            "seaworld": "PRKS", "united parks": "PRKS", "busch gardens": "PRKS",
            "vail resorts": "MTN", "vail": "MTN",
            # Vacation
            "marriott vacations": "VAC", "travel + leisure": "TNL",
            "hilton grand vacations": "HGV", "tripadvisor": "TRIP",
            # Entertainment
            "live nation": "LYV", "ticketmaster": "LYV",
            "sphere entertainment": "SPHR", "sphere": "SPHR",
            "dave & buster": "PLAY", "dave and buster": "PLAY",
            "lucky strike": "LUCK", "soho house": "SHCO",
        },
        "private_companies": {
            "Universal Studios": ["Universal Studios", "Universal Parks"],
            "Merlin":            ["Merlin Entertainments", "Legoland"],
        },
    },
}
