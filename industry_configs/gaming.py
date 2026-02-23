"""
Gaming (Casino / iGaming / Sports Betting) industry configuration.
"""

CONFIG = {
    "name": "Gaming",
    "icon": "\U0001f3b0",  # slot machine

    "companies": {
        # Destination Resorts
        "LVS":    {"name": "Las Vegas Sands",        "segment": "Destination Resorts",      "color": "#C0392B"},
        "MGM":    {"name": "MGM Resorts",             "segment": "Destination Resorts",      "color": "#2C3E50"},
        "WYNN":   {"name": "Wynn Resorts",            "segment": "Destination Resorts",      "color": "#8E44AD"},
        # Regional / Diversified
        "CZR":    {"name": "Caesars Entertainment",   "segment": "Regional/Diversified",     "color": "#1ABC9C"},
        "BYD":    {"name": "Boyd Gaming",             "segment": "Regional/Diversified",     "color": "#27AE60"},
        "PENN":   {"name": "PENN Entertainment",      "segment": "Regional/Diversified",     "color": "#F39C12"},
        # Digital / Sports Betting
        "DKNG":   {"name": "DraftKings",              "segment": "Digital/Sports Betting",   "color": "#00A651"},
        "FLUT":   {"name": "Flutter Entertainment",   "segment": "Digital/Sports Betting",   "color": "#003087"},
        "GAMB":   {"name": "Gambling.com Group",      "segment": "Digital/Sports Betting",   "color": "#FF6B00"},
        "ENT.L":  {"name": "Entain",                  "segment": "Digital/Sports Betting",   "color": "#0F6338"},
        # Gaming Technology
        "LNW":    {"name": "Light & Wonder",          "segment": "Gaming Technology",        "color": "#7B2D8E"},
        "ALL.AX": {"name": "Aristocrat Leisure",      "segment": "Gaming Technology",        "color": "#E52B2B"},
    },

    "segments": {
        "Destination Resorts":    ["LVS", "MGM", "WYNN"],
        "Regional/Diversified":   ["CZR", "BYD", "PENN"],
        "Digital/Sports Betting": ["DKNG", "FLUT", "GAMB", "ENT.L"],
        "Gaming Technology":      ["LNW", "ALL.AX"],
    },

    "segment_colors": {
        "Destination Resorts":    "#C0392B",
        "Regional/Diversified":   "#1ABC9C",
        "Digital/Sports Betting": "#003087",
        "Gaming Technology":      "#7B2D8E",
    },

    "fred_series": {
        # Universal
        "cpi_all":             "CPIAUCSL",
        "recession":           "USREC",
        "consumer_sentiment":  "UMCSENT",
        "unemployment":        "UNRATE",
        "fed_funds":           "FEDFUNDS",
        # Industry-specific
        "cpi_industry_1":      "PCU7211207211205",  # Casino Hotels Gaming Receipts PPI
        "cpi_industry_2":      None,
        "wages":               "CES7000000008",     # Avg Hourly Earnings: L&H
        "industry_employment": "CES7071300001",     # Amusement, Gambling & Recreation Employment
        "job_openings":        None,
        "industry_kpi":        None,
        "gambling_revenue":    "REV7132TAXABL144QNSA",   # Quarterly Gambling Industry Revenue
        "gambling_pce":        "DGAMRX1A020NBEA",         # Real Personal Consumption: Gambling
        "amusement_revenue":   "REV713AMSA",              # Total Revenue: Amusement, Gambling & Rec
    },

    "commodity_futures": {},
    "commodity_units": {},
    "commodity_meta": {},

    # FRED PPI series for gaming input costs
    "input_cost_fred": {
        "Industrial Electricity":  "WPU0543",       # PPI Industrial Electric Power
        "Industrial Nat Gas":      "WPU05532101",   # PPI Industrial Natural Gas
        "Food Away from Home CPI": "CUSR0000SEFV",  # CPI Food Away from Home
    },

    # Impact notes: how each input cost affects companies in coverage
    "input_cost_notes": {
        "Industrial Electricity": (
            "Casino floors run 24/7 with massive lighting, HVAC, and electronic gaming "
            "machines. MGM, CZR, and WYNN operate some of the largest energy-consuming "
            "properties on the Las Vegas Strip. BYD and PENN regional casinos are also "
            "material energy consumers. Rising electricity costs compress property-level EBITDA."
        ),
        "Industrial Nat Gas": (
            "Heating and cooling for large casino-hotel complexes. LVS (Venetian/Palazzo), "
            "MGM (Bellagio, MGM Grand), WYNN, and CZR (Caesars Palace, Harrah's) all "
            "operate multi-million sq ft properties where nat gas is a significant utility cost."
        ),
        "Food Away from Home CPI": (
            "Casino F&B operations are a major revenue and cost center. MGM, WYNN, and LVS "
            "operate high-end restaurants. CZR and BYD run buffets and casual dining. "
            "Rising food costs affect F&B margins across all land-based operators."
        ),
    },

    "has_sss": False,
    "has_commodities": False,
    "has_beef_chicken": False,

    "macro_labels": {
        "cpi_industry_1_label": "Casino Hotels Gaming Receipts PPI",
        "cpi_industry_2_label": None,
        "wages_label":          "L&H Wages",
        "employment_label":     "Amusement/Gambling Employment",
        "industry_section_title": "Gaming Revenue Environment",
        "cpi_chart_title":      "Casino Hotels Gaming Receipts PPI (YoY %)",
        "cpi_label_1":          "Casino Hotels Gaming Receipts",
        "cpi_label_2":          None,
        "cpi_chart_caption":    (
            "Casino Hotels Gaming Receipts PPI tracks pricing trends "
            "in the destination resort and casino hotel segment."
        ),
        "wages_chart_title":    "Avg Hourly Earnings \u2013 Leisure & Hospitality (YoY %)",
        "employment_chart_title": "Amusement, Gambling & Recreation Employment",
        "employment_y_title":   "Thousands",
        "job_openings_chart_title": None,
        "employment_section_title": "Labor Market",
        "employment_caption":   (
            "Amusement, gambling, and recreation employment tracks staffing levels "
            "across casino properties and related entertainment venues."
        ),
        "industry_kpi_label":   None,
        "industry_kpi_chart_title": None,
        "industry_kpi_caption": None,
        "gambling_revenue_label": "Quarterly Gambling Industry Revenue",
        "gambling_revenue_chart_title": "U.S. Gambling Industry Revenue (Quarterly)",
        "gambling_revenue_caption": (
            "FRED series REV7132TAXABL144QNSA tracks total quarterly revenue "
            "for the U.S. gambling industry — a direct GGR proxy covering casinos, "
            "sports betting, and other legal wagering."
        ),
    },

    "news": {
        "rss_feeds": {
            "CDC Gaming Reports":   "https://cdcgamingreports.com/feed/",
            "Legal Sports Report":  "https://www.legalsportsreport.com/feed/",
            "Reuters Business":     "https://feeds.reuters.com/reuters/businessNews",
            "MarketWatch":          "https://feeds.marketwatch.com/marketwatch/topstories/",
            "Seeking Alpha":        "https://seekingalpha.com/feed.xml",
            "CNBC":                 "https://www.cnbc.com/id/10000664/device/rss/rss.html",
            "Forbes Business":      "https://www.forbes.com/business/feed/",
        },
        "industry_sources": {"CDC Gaming Reports", "Legal Sports Report"},
        "title_keywords": [
            "casino", "gaming", "gambling", "sports betting", "iGaming",
            "online betting", "sportsbook", "GGR", "gross gaming revenue",
            "Macau", "Las Vegas Strip", "regional casino", "igaming",
            "online casino", "mobile betting", "handle", "hold",
            "slot machine", "gaming technology", "poker",
        ],
        "company_name_keywords": [
            "Las Vegas Sands", "MGM Resorts", "MGM", "Wynn Resorts", "Wynn",
            "Caesars", "Boyd Gaming", "PENN Entertainment",
            "DraftKings", "Flutter", "FanDuel", "BetMGM",
            "Gambling.com", "Entain", "Ladbrokes", "bwin",
            "Light & Wonder", "Scientific Games", "Aristocrat",
            "Bally's", "Hard Rock", "Station Casinos",
        ],
        "earnings_keywords": [
            "earnings", "quarterly results", "EPS", "revenue", "guidance",
            "GGR", "gaming revenue", "beats estimates", "misses estimates",
            "profit", "RevPAR", "occupancy",
        ],
        "ticker_map": {
            "las vegas sands": "LVS", "mgm resorts": "MGM", "mgm": "MGM",
            "wynn resorts": "WYNN", "wynn": "WYNN",
            "caesars": "CZR", "boyd gaming": "BYD",
            "penn entertainment": "PENN", "penn": "PENN",
            "draftkings": "DKNG", "flutter": "FLUT", "fanduel": "FLUT",
            "betmgm": "MGM",
            "gambling.com": "GAMB",
            "entain": "ENT.L", "ladbrokes": "ENT.L", "bwin": "ENT.L",
            "light & wonder": "LNW", "light and wonder": "LNW",
            "scientific games": "LNW",
            "aristocrat": "ALL.AX",
        },
        "private_companies": {
            "Hard Rock":      ["Hard Rock International", "Hard Rock"],
            "Station Casinos": ["Station Casinos"],
        },
    },
}
