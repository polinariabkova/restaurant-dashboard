"""
Restaurant industry configuration.
"""

CONFIG = {
    "name": "Restaurants",
    "icon": "\U0001f354",  # hamburger

    "companies": {
        "MCD":  {"name": "McDonald's",             "segment": "QSR",           "color": "#FFC72C"},
        "YUM":  {"name": "Yum! Brands",            "segment": "QSR",           "color": "#E31837"},
        "QSR":  {"name": "Restaurant Brands Intl",  "segment": "QSR",          "color": "#D62300"},
        "WEN":  {"name": "Wendy's",                "segment": "QSR",           "color": "#E2203C"},
        "DPZ":  {"name": "Domino's Pizza",          "segment": "QSR",          "color": "#006491"},
        "CMG":  {"name": "Chipotle",               "segment": "Fast Casual",   "color": "#441000"},
        "SHAK": {"name": "Shake Shack",            "segment": "Fast Casual",   "color": "#5BAD92"},
        "WING": {"name": "Wingstop",               "segment": "Fast Casual",   "color": "#C8102E"},
        "DRI":  {"name": "Darden Restaurants",      "segment": "Casual Dining", "color": "#00573F"},
        "EAT":  {"name": "Brinker / Chili's",      "segment": "Casual Dining", "color": "#C41230"},
        "TXRH": {"name": "Texas Roadhouse",        "segment": "Casual Dining", "color": "#8B0000"},
        "CAKE": {"name": "Cheesecake Factory",     "segment": "Casual Dining", "color": "#B8860B"},
        "SBUX": {"name": "Starbucks",              "segment": "Coffee/Bfast",  "color": "#00704A"},
        "DENN": {"name": "Denny's",                "segment": "Coffee/Bfast",  "color": "#FFD700"},
    },

    "segments": {
        "QSR":           ["MCD", "YUM", "QSR", "WEN", "DPZ"],
        "Fast Casual":   ["CMG", "SHAK", "WING"],
        "Casual Dining": ["DRI", "EAT", "TXRH", "CAKE"],
        "Coffee/Bfast":  ["SBUX", "DENN"],
    },

    "segment_colors": {
        "QSR":           "#E31837",
        "Fast Casual":   "#441000",
        "Casual Dining": "#00573F",
        "Coffee/Bfast":  "#00704A",
    },

    "fred_series": {
        # Universal
        "cpi_all":             "CPIAUCSL",
        "recession":           "USREC",
        "consumer_sentiment":  "UMCSENT",
        "unemployment":        "UNRATE",
        "fed_funds":           "FEDFUNDS",
        # Industry-specific
        "cpi_industry_1":      "CUSR0000SEFV",     # CPI Food Away from Home
        "cpi_industry_2":      "CUSR0000SAF11",    # CPI Food at Home
        "wages":               "CES7000000008",    # Avg Hourly Earnings: Leisure & Hospitality
        "industry_employment": "CES7072200001",    # Food Services & Drinking Places Employment
        "job_openings":        "JTS7200JOL",       # Job Openings: Accommodation & Food Services
        "industry_kpi":        None,
    },

    "commodity_futures": {
        "Corn":        "ZC=F",
        "Wheat":       "ZW=F",
        "Coffee":      "KC=F",
        "Soybean Oil": "ZL=F",
        "Lean Cattle": "LE=F",
        "Lean Hogs":   "HE=F",
    },

    "commodity_units": {
        "Corn":        "\u00a2/bu",
        "Wheat":       "\u00a2/bu",
        "Coffee":      "\u00a2/lb",
        "Soybean Oil": "\u00a2/lb",
        "Lean Cattle": "\u00a2/lb",
        "Lean Hogs":   "\u00a2/lb",
        "Beef":        "$/lb",
        "Chicken":     "$/lb",
    },

    "commodity_meta": {
        "Corn":        {"emoji": "\U0001f33d", "category": "Grains",    "color": "#F4D03F"},
        "Wheat":       {"emoji": "\U0001f33e", "category": "Grains",    "color": "#E8C07D"},
        "Coffee":      {"emoji": "\u2615",     "category": "Beverages", "color": "#6F4E37"},
        "Soybean Oil": {"emoji": "\U0001fad8", "category": "Oils",      "color": "#A8B820"},
        "Lean Cattle": {"emoji": "\U0001f404", "category": "Beef",      "color": "#8B4513"},
        "Lean Hogs":   {"emoji": "\U0001f437", "category": "Pork",      "color": "#C1698A"},
        "Beef":        {"emoji": "\U0001f969", "category": "Beef",      "color": "#B22222"},
        "Chicken":     {"emoji": "\U0001f414", "category": "Chicken",   "color": "#DAA520"},
    },

    # Impact notes: how each input cost affects companies in coverage
    "input_cost_notes": {
        "Corn": (
            "Feed-cost driver for beef and chicken supply chains — indirectly impacts "
            "MCD, WEN, TXRH, SHAK (burger proteins) and WING, YUM/KFC (chicken). "
            "Also corn tortillas at CMG and YUM/Taco Bell. High-fructose corn syrup "
            "affects beverage costs across all operators."
        ),
        "Wheat": (
            "Key ingredient in buns, bread, pizza dough, and tortillas. DPZ is most "
            "directly exposed (pizza crust is ~30% of COGS). Also impacts MCD, WEN, "
            "QSR/Burger King (buns), CMG (flour tortillas), CAKE (pasta, bread), "
            "and DRI/Olive Garden (breadsticks, pasta)."
        ),
        "Coffee": (
            "SBUX is the most exposed operator — coffee beans are ~25-30% of product "
            "COGS. Also impacts MCD (McCafé line), DENN (breakfast/all-day coffee), "
            "and DRI (Olive Garden, LongHorn after-meal coffee). "
            "Arabica prices directly affect menu pricing and margin."
        ),
        "Soybean Oil": (
            "Primary frying oil for most QSR operators. MCD (fries, McNuggets), "
            "YUM/KFC (fried chicken), QSR/Burger King (fries, chicken), WEN, "
            "and WING (wing frying) are most exposed. DPZ uses it for pizza prep. "
            "Some operators hedge via fixed-price contracts 6-12 months out."
        ),
        "Lean Cattle": (
            "Front-month live cattle futures — upstream indicator for beef costs. "
            "MCD (Big Mac, Quarter Pounder), WEN (fresh beef patties), SHAK (premium "
            "burgers), TXRH (steaks — highest beef COGS exposure in coverage), "
            "EAT/Chili's (burgers, fajitas), and CAKE are most affected."
        ),
        "Lean Hogs": (
            "Drives pork input costs including bacon, ham, and sausage. WEN "
            "(Baconator — bacon is a top COGS item), MCD (bacon offerings, breakfast "
            "sausage), DPZ (pepperoni, ham toppings), EAT, and DRI are key operators. "
            "DENN relies on breakfast pork products."
        ),
        "Beef": (
            "Wholesale beef prices (USDA). TXRH has the highest beef exposure in "
            "coverage (~35% of COGS). Also critical for MCD, WEN (fresh never-frozen "
            "beef), SHAK, QSR/Burger King, EAT/Chili's, and DRI/LongHorn Steakhouse. "
            "Rising beef costs are the #1 margin headwind for burger-focused QSRs."
        ),
        "Chicken": (
            "WING is the most directly exposed — chicken wings are the core product "
            "and wing price volatility drives margin swings. YUM (KFC, Popeyes via QSR) "
            "is heavily exposed to bone-in and boneless chicken. CMG (chicken burritos/bowls), "
            "MCD (McNuggets, McChicken), and EAT (Chili's chicken) also affected."
        ),
    },

    "has_sss": True,
    "has_commodities": True,
    "has_beef_chicken": True,

    "macro_labels": {
        "cpi_industry_1_label": "CPI Food Away",
        "cpi_industry_2_label": "CPI Food at Home",
        "wages_label":          "L&H Wages",
        "employment_label":     "Food Services Jobs",
        "industry_section_title": "Inflation & Restaurant Pricing",
        "cpi_chart_title":      "CPI: Food Away from Home vs. Food at Home (YoY %)",
        "cpi_label_1":          "Food Away from Home",
        "cpi_label_2":          "Food at Home",
        "cpi_chart_caption":    (
            "**Food Away from Home** is the direct restaurant price index \u2014 "
            "rising rapidly signals pricing power. "
            "**Food at Home** (grocery) captures the consumer trade-down risk."
        ),
        "wages_chart_title":    "Avg Hourly Earnings \u2013 Leisure & Hospitality (YoY %)",
        "employment_chart_title": "Food Services & Drinking Places Employment",
        "employment_y_title":   "Thousands",
        "job_openings_chart_title": "Job Openings: Accommodation & Food Services",
        "employment_section_title": "Labor Market",
        "employment_caption":   (
            "Restaurant labor is captured in the Leisure & Hospitality supersector. "
            "Wage growth above ~3-4% typically pressures restaurant-level margins. "
            "Food Services & Drinking Places employment tracks industry hiring directly."
        ),
    },

    "news": {
        "rss_feeds": {
            "Nation's Restaurant News":   "https://www.nrn.com/rss.xml",
            "Restaurant Business Online": "https://www.restaurantbusinessonline.com/rss/all",
            "QSR Magazine":               "https://www.qsrmagazine.com/rss.xml",
            "FSR Magazine":               "https://www.fsrmagazine.com/rss.xml",
            "Food Business News":         "https://www.foodbusinessnews.net/rss",
            "Food Dive":                  "https://www.fooddive.com/feeds/news/",
            "The Food Institute":         "https://foodinstitute.com/feed/",
            "Eater":                      "https://www.eater.com/rss/index.xml",
            "Reuters Business":           "https://feeds.reuters.com/reuters/businessNews",
            "CNBC Consumer":              "https://www.cnbc.com/id/10000664/device/rss/rss.html",
            "MarketWatch":                "https://feeds.marketwatch.com/marketwatch/topstories/",
            "Fortune":                    "https://fortune.com/feed/",
            "Forbes Business":            "https://www.forbes.com/business/feed/",
            "Business Insider":           "https://feeds.businessinsider.com/custom/all",
            "NY Post Business":           "https://nypost.com/business/feed/",
            "The Street":                 "https://www.thestreet.com/rss/00000000-0000-0000-0000-000000000000.rss",
            "Seeking Alpha":              "https://seekingalpha.com/feed.xml",
            "Food & Wine":                "https://www.foodandwine.com/rss",
            "Grub Street":                "https://www.grubstreet.com/rss/index.xml",
            "Grocery Dive":               "https://www.grocerydive.com/feeds/news/",
        },
        "industry_sources": {
            "Nation's Restaurant News", "Restaurant Business Online", "QSR Magazine",
            "FSR Magazine", "Food Business News", "Food Dive", "The Food Institute", "Eater",
            "Food & Wine", "Grub Street", "Grocery Dive",
        },
        "title_keywords": [
            "restaurant", "fast food", "quick service", "QSR", "casual dining",
            "fast casual", "same-store sales", "comp sales", "comparable sales",
            "menu price", "food cost", "food inflation", "foodservice", "food service",
            "drive-through", "drive thru", "food delivery", "unit growth",
            "DoorDash", "Uber Eats", "Grubhub",
        ],
        "company_name_keywords": [
            "McDonald", "Yum Brands", "Yum!", "Restaurant Brands", "Burger King",
            "Tim Hortons", "Popeyes", "Wendy's", "Domino's", "Chipotle",
            "Shake Shack", "Wingstop", "Darden", "Olive Garden", "LongHorn",
            "Chili's", "Brinker", "Texas Roadhouse", "Cheesecake Factory",
            "Starbucks", "Denny's", "Taco Bell", "KFC", "Pizza Hut",
            "Arby's", "Buffalo Wild Wings", "Dunkin'", "Raising Cane",
            "Flynn Restaurant", "Inspire Brands", "Whataburger", "Tacala",
            "Sizzling Platter", "Fogo de Chao", "K-MAC", "Jack in the Box",
            "Panera", "Five Guys", "Applebee's", "IHOP", "Cracker Barrel",
            "Sweetgreen", "Dutch Bros",
        ],
        "earnings_keywords": [
            "earnings", "quarterly results", "same-store sales", "comp sales",
            "comparable sales", "EPS", "revenue", "guidance", "beats estimates",
            "misses estimates", "profit", "annual results", "full year",
        ],
        "ticker_map": {
            "mcdonald": "MCD", "yum brands": "YUM", "yum!": "YUM",
            "restaurant brands": "QSR", "burger king": "QSR",
            "tim hortons": "QSR", "popeyes": "QSR",
            "wendy": "WEN", "domino's": "DPZ", "chipotle": "CMG",
            "shake shack": "SHAK", "wingstop": "WING",
            "darden": "DRI", "olive garden": "DRI", "longhorn": "DRI",
            "chili's": "EAT", "brinker": "EAT",
            "texas roadhouse": "TXRH", "cheesecake factory": "CAKE",
            "starbucks": "SBUX", "denny's": "DENN",
            "taco bell": "YUM", "kfc": "YUM", "pizza hut": "YUM",
        },
        "private_companies": {
            "Flynn Restaurant":  ["Flynn Restaurant", "Flynn Group"],
            "Inspire Brands":    ["Inspire Brands"],
            "BWW":               ["Buffalo Wild Wings"],
            "Sonic":             ["Sonic Drive-In", "Sonic Drive"],
            "Dunkin'":           ["Dunkin'", "Dunkin Donuts"],
            "Whataburger":       ["Whataburger"],
            "Tacala":            ["Tacala"],
            "Raising Cane's":    ["Raising Cane", "Cane's Chicken"],
            "Sizzling Platter":  ["Sizzling Platter"],
            "Fogo de Chao":      ["Fogo de Chao"],
            "K-MAC":             ["K-MAC Enterprises", "K-MAC"],
            "Jack in the Box":   ["Jack in the Box"],
            "Panera":            ["Panera Bread", "Panera"],
            "Five Guys":         ["Five Guys"],
            "Applebee's":        ["Applebee's", "Applebees"],
            "IHOP":              ["IHOP"],
            "Cracker Barrel":    ["Cracker Barrel"],
            "Sweetgreen":        ["Sweetgreen"],
            "Dutch Bros":        ["Dutch Bros"],
        },
    },
}
