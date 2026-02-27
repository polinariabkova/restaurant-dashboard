"""
Paper & Packaging industry configuration.
"""

CONFIG = {
    "name": "Paper & Packaging",
    "icon": "\U0001f4e6",  # package

    "page_titles": {
        "stocks":       "Stock Performance",
        "kpis":         "Pricing & Capacity",
        "market":       "Input Costs",
        "fundamentals": "Fundamentals",
        "macro":        "P&P Industry & Macro",
        "news":         "P&P News",
    },

    "companies": {
        # Containerboard & Corrugated
        "IP":      {"name": "International Paper",     "segment": "Containerboard",         "color": "#1B4F72"},
        "PKG":     {"name": "Packaging Corp",           "segment": "Containerboard",         "color": "#2E86C1"},
        "SW":      {"name": "Smurfit WestRock",         "segment": "Containerboard",         "color": "#5DADE2"},
        "GEF":     {"name": "Greif Inc",                "segment": "Containerboard",         "color": "#1F4E79"},
        "CAS.TO":  {"name": "Cascades",                 "segment": "Containerboard",         "color": "#148F77"},
        # Consumer & Rigid Packaging
        "GPK":     {"name": "Graphic Packaging",        "segment": "Consumer Packaging",     "color": "#F39C12"},
        "AMCR":    {"name": "Amcor",                    "segment": "Consumer Packaging",     "color": "#0072CE"},
        "SLGN":    {"name": "Silgan Holdings",          "segment": "Consumer Packaging",     "color": "#4A90D9"},
        "ATR":     {"name": "Aptargroup",               "segment": "Consumer Packaging",     "color": "#2E8B57"},
        "BALL":    {"name": "Ball Corporation",          "segment": "Consumer Packaging",     "color": "#CC0000"},
        "CCK":     {"name": "Crown Holdings",            "segment": "Consumer Packaging",     "color": "#1A5276"},
        "OI":      {"name": "O-I Glass",                 "segment": "Consumer Packaging",     "color": "#D4AC0D"},
        "SEE":     {"name": "Sealed Air",                "segment": "Consumer Packaging",     "color": "#E67E22"},
        # Pulp & Specialty Paper
        "SLVM":    {"name": "Sylvamo",                   "segment": "Pulp & Paper",           "color": "#17A589"},
        "MERC":    {"name": "Mercer International",      "segment": "Pulp & Paper",           "color": "#8B4513"},
        "RYAM":    {"name": "Rayonier Advanced Materials","segment": "Pulp & Paper",           "color": "#2C6B2F"},
        "SUZ":     {"name": "Suzano",                    "segment": "Pulp & Paper",           "color": "#00843D"},
        "CLW":     {"name": "Clearwater Paper",          "segment": "Pulp & Paper",           "color": "#5B2C6F"},
        "CFX.TO":  {"name": "Canfor Pulp",               "segment": "Pulp & Paper",           "color": "#C0392B"},
        # Diversified / Specialty
        "SON":     {"name": "Sonoco Products",           "segment": "Diversified",            "color": "#884EA0"},
        "MAGN":    {"name": "Magnera Corporation",       "segment": "Diversified",            "color": "#E67E22"},
    },

    "segments": {
        "Containerboard":      ["IP", "PKG", "SW", "GEF", "CAS.TO"],
        "Consumer Packaging":  ["GPK", "AMCR", "SLGN", "ATR", "BALL", "CCK", "OI", "SEE"],
        "Pulp & Paper":        ["SLVM", "MERC", "RYAM", "SUZ", "CLW", "CFX.TO"],
        "Diversified":         ["SON", "MAGN"],
    },

    "segment_colors": {
        "Containerboard":      "#1B4F72",
        "Consumer Packaging":  "#F39C12",
        "Pulp & Paper":        "#17A589",
        "Diversified":         "#884EA0",
    },

    "fred_series": {
        # Universal
        "cpi_all":             "CPIAUCSL",
        "recession":           "USREC",
        "consumer_sentiment":  "UMCSENT",
        "unemployment":        "UNRATE",
        "fed_funds":           "FEDFUNDS",
        # Industry-specific
        "cpi_industry_1":      "WPU091405",         # PPI Corrugated Paperboard
        "cpi_industry_2":      "WPU0911",           # PPI Wood Pulp
        "wages":               "CES3200000008",     # Avg Hourly Earnings: Manufacturing
        "industry_employment": "IPG322N",            # Industrial Production: Paper
        "job_openings":        None,
        "industry_kpi":        "PCU32221132221102",  # PPI Corrugated Shipping Containers
        # Additional P&P KPIs
        "containerboard_ppi":  "WPU09140551",         # PPI Corrugated Paperboard (sub-commodity)
        "kraft_linerboard":    "PCU3221303221301",     # PPI Unbleached Kraft Packaging Paperboard
        "box_production":      "IPN32221S",            # Industrial Production: Paperboard Container
        "box_shipment_value":  "A22BVS",               # Manufacturers' Shipments: Paperboard Container ($M)
        "box_inventories":     "A22BTI",               # Manufacturers' Inventories: Paperboard Container
        "capacity_util":       "CAPUTLG322S",          # Capacity Utilization: Paper (NAICS 322)
        "occ_ppi":             "PCU42993042993033",    # PPI Material Recyclers: Corrugated Recyclable Paper
        "recycled_paperboard": "WPU09141105",          # PPI Recycled Paperboard
        # Volume & shipment data
        "corrugated_output":   "IPUEN322211T011000000", # Real Sectoral Output: Corrugated Boxes (NAICS 322211)
        "cass_freight":        "FRGSHPUSM649NCIS",      # Cass Freight Index: Shipments (logistics proxy)
    },

    "commodity_futures": {
        "Lumber":      "LBR=F",
        "Natural Gas":  "NG=F",
        "Aluminum":     "ALI=F",
        "Crude Oil":    "CL=F",
        "Corn":         "ZC=F",
    },

    "commodity_units": {
        "Lumber":      "$/1000 bd ft",
        "Natural Gas":  "$/MMBtu",
        "Aluminum":     "\u00a2/lb",
        "Crude Oil":    "$/bbl",
        "Corn":         "\u00a2/bu",
    },

    "commodity_meta": {
        "Lumber":      {"emoji": "\U0001fab5", "category": "Wood Products",     "color": "#8B4513"},
        "Natural Gas":  {"emoji": "\U0001f525", "category": "Energy",            "color": "#E74C3C"},
        "Aluminum":     {"emoji": "\U0001f4a0", "category": "Metals",            "color": "#7F8C8D"},
        "Crude Oil":    {"emoji": "\U0001f6e2\ufe0f",  "category": "Energy",     "color": "#2C3E50"},
        "Corn":         {"emoji": "\U0001f33d", "category": "Agricultural",      "color": "#F1C40F"},
    },

    # FRED PPI series for additional input costs (charted on Input Costs page)
    "input_cost_fred": {
        "Plastic Resins":         "WPU066",             # PPI Plastic Resins & Materials
        "Caustic Soda":           "PCU3251803251804",    # PPI Sodium Hydroxide (Caustic Soda)
        "Steel Mill Products":    "WPU1017",             # PPI Iron & Steel: Steel Mill Products
        "Aluminum Mill Shapes":   "WPU102501",           # PPI Metals: Aluminum Mill Shapes
        "Industrial Nat Gas":     "WPU05532101",         # PPI Industrial Natural Gas
        "Industrial Electricity": "WPU0543",             # PPI Industrial Electric Power
        "Diesel Fuel":            "WPU057303",           # PPI No. 2 Diesel Fuel
        "Corn Starch":            "WPU02140907",         # PPI Manufactured Starch (Wet Milling)
    },

    # Impact notes: how each input cost affects companies in coverage
    "input_cost_notes": {
        "Lumber": (
            "Proxy for virgin wood fiber costs. Affects kraft linerboard mills (IP, PKG, SW) "
            "that use virgin wood chips. Also impacts Pulp & Paper segment (SLVM, MERC, SUZ)."
        ),
        "Natural Gas": (
            "Major energy input for all paper/packaging manufacturing. Paper mills use nat gas "
            "for drying, steam generation, and lime kilns. Glass melting (OI) is highly nat gas "
            "intensive. Metal can curing ovens (BALL, CCK) also consume significant volumes."
        ),
        "Aluminum": (
            "Primary raw material for aluminum beverage cans (BALL, CCK). Also used in "
            "flexible packaging foil laminates (AMCR, SEE) and closures (SLGN, ATR). "
            "~60% of aluminum cost typically passes through to customers via contracts."
        ),
        "Crude Oil": (
            "Upstream feedstock for polyethylene, polypropylene, and PET resins — key inputs "
            "for flexible packaging (AMCR, SEE) and plastic closures (SLGN, ATR). "
            "Also drives diesel/transportation costs across all segments."
        ),
        "Corn": (
            "Proxy for corn starch costs. Starch is used as a dry-strength additive in "
            "papermaking and as the adhesive in the corrugating process (IP, PKG, SW, GEF). "
            "Especially critical for recycled containerboard mills."
        ),
        "Plastic Resins": (
            "Broad PPI for all plastic resins (PE, PP, PET). Directly impacts flexible "
            "packaging (AMCR, SEE), plastic containers & closures (SLGN, ATR), "
            "and coatings used in metal cans and paperboard."
        ),
        "Caustic Soda": (
            "Essential chemical in kraft pulping (white liquor) and recycled fiber deinking. "
            "Affects all containerboard (IP, PKG, SW, GEF, CAS.TO) and pulp producers "
            "(SLVM, MERC, SUZ). Also used in glass manufacturing (OI)."
        ),
        "Steel Mill Products": (
            "Drives tinplate and tin-free steel costs for food can manufacturing (SLGN, CCK). "
            "Steel closures and industrial packaging (GEF) are also impacted."
        ),
        "Aluminum Mill Shapes": (
            "More specific than raw aluminum — tracks the rolled/extruded aluminum sheet "
            "that BALL and CCK purchase for can manufacturing. Includes the conversion "
            "premium above LME ingot price."
        ),
        "Industrial Nat Gas": (
            "FRED PPI for industrial natural gas specifically. Directly reflects the "
            "price paper mills, glass furnaces, and metal can plants pay. Complements "
            "the futures-based NG=F price."
        ),
        "Industrial Electricity": (
            "Tracks industrial power costs. Paper machines, refiners, and extrusion lines "
            "are electricity-intensive. Pulp mills (MERC, SUZ) that generate surplus "
            "green electricity may benefit from rising grid prices."
        ),
        "Diesel Fuel": (
            "Drives logistics and transportation costs across the entire value chain. "
            "Wood chip hauling, finished goods delivery, and OCC collection are all "
            "diesel-dependent. Affects all companies in coverage."
        ),
        "Corn Starch": (
            "FRED PPI for manufactured starch from wet corn milling. Starch is a key "
            "additive in corrugating and papermaking. Rising starch costs compress "
            "containerboard margins (IP, PKG, SW, GEF, CAS.TO, GPK)."
        ),
    },

    "has_sss": False,
    "has_commodities": True,
    "has_beef_chicken": False,

    "macro_labels": {
        "cpi_industry_1_label": "PPI Corrugated Paperboard",
        "cpi_industry_2_label": "PPI Wood Pulp",
        "wages_label":          "Manufacturing Wages",
        "employment_label":     "Industrial Production: Paper",
        "industry_section_title": "Input Cost Pressures",
        "cpi_chart_title":      "PPI: Corrugated Paperboard vs. Wood Pulp (YoY %)",
        "cpi_label_1":          "Corrugated Paperboard",
        "cpi_label_2":          "Wood Pulp",
        "cpi_chart_caption":    (
            "**PPI Corrugated Paperboard** is the direct packaging input cost index. "
            "**Wood Pulp** is the key upstream raw material \u2014 "
            "rising pulp prices signal margin compression for recycled mills."
        ),
        "wages_chart_title":    "Avg Hourly Earnings \u2013 Manufacturing (YoY %)",
        "employment_chart_title": "Industrial Production: Paper (Index)",
        "employment_y_title":   "Index",
        "job_openings_chart_title": None,
        "employment_section_title": "Production & Labor",
        "employment_caption":   (
            "Industrial production of paper tracks operating rates and capacity utilization. "
            "Manufacturing wages affect conversion costs across the paper & packaging value chain."
        ),
        "industry_kpi_label":   "PPI Corrugated Shipping Containers",
        "industry_kpi_chart_title": "PPI Corrugated Shipping Containers (YoY %)",
        "industry_kpi_caption": (
            "PPI for corrugated shipping containers tracks the price that mills receive "
            "for finished boxes \u2014 the single most direct revenue proxy for containerboard producers."
        ),
        # Additional P&P KPI labels
        "containerboard_ppi_label": "PPI Corrugated Paperboard (Sub-Commodity)",
        "kraft_linerboard_label": "PPI Kraft Linerboard",
        "box_production_label": "Box Production Index",
        "box_production_chart_title": "Paperboard Container Production (Index, 2017=100)",
        "box_shipment_value_label": "Box Shipment Value ($M)",
        "box_shipment_chart_title": "Paperboard Container Shipments ($M, SA)",
        "box_inventories_label": "Box Inventories ($M)",
        "capacity_util_label": "Paper Sector Capacity Utilization",
        "capacity_util_chart_title": "Paper Sector Capacity Utilization (%)",
        "capacity_util_caption": (
            "Federal Reserve capacity utilization for NAICS 322 (all paper). "
            "A proxy for containerboard operating rates \u2014 above 95% signals tight supply "
            "and pricing power; below 90% suggests overcapacity."
        ),
        "occ_ppi_label": "OCC (Recycled Fiber) PPI",
        "occ_chart_title": "OCC (Recycled Fiber) Price Index (YoY %)",
        "occ_caption": (
            "PPI for corrugated recyclable paper sold by material recyclers \u2014 "
            "the closest free proxy to OCC #11 spot pricing. Rising OCC costs compress "
            "margins for mills reliant on recycled fiber."
        ),
        "recycled_paperboard_label": "PPI Recycled Paperboard",
        "corrugated_output_label": "Corrugated Box Output (Real)",
        "corrugated_output_chart_title": "Real Sectoral Output: Corrugated Boxes (NAICS 322211)",
        "corrugated_output_caption": (
            "FRED IPUEN322211T011000000 \u2014 real (inflation-adjusted) output for corrugated "
            "and solid fiber box manufacturing. A volume proxy for industry shipments."
        ),
        "cass_freight_label": "Cass Freight Index: Shipments",
        "cass_freight_chart_title": "Cass Freight Index: Shipments",
        "cass_freight_caption": (
            "Monthly freight shipment volume index from Cass Information Systems. "
            "A leading indicator of packaging demand \u2014 more freight = more boxes shipped."
        ),
        "supply_demand_section_title": "Supply, Demand & Recycled Fiber",
        "supply_demand_caption": (
            "Box production and shipments track corrugated demand. "
            "Capacity utilization measures how tight supply is. "
            "OCC pricing reflects recycled fiber input costs."
        ),
    },

    "news": {
        "rss_feeds": {
            "Packaging Digest":     "https://www.packagingdigest.com/rss.xml",
            "Packaging World":      "https://www.packworld.com/rss.xml",
            "Reuters Business":     "https://feeds.reuters.com/reuters/businessNews",
            "MarketWatch":          "https://feeds.marketwatch.com/marketwatch/topstories/",
            "Seeking Alpha":        "https://seekingalpha.com/feed.xml",
            "CNBC":                 "https://www.cnbc.com/id/10000664/device/rss/rss.html",
            "Forbes Business":      "https://www.forbes.com/business/feed/",
        },
        "industry_sources": {"Packaging Digest", "Packaging World"},
        "title_keywords": [
            "packaging", "containerboard", "corrugated", "paperboard",
            "wood pulp", "linerboard", "kraft", "carton", "box shipment",
            "fiber", "recycled fiber", "OCC", "old corrugated",
            "paper mill", "pulp mill", "paper price",
            "aluminum can", "glass container", "rigid packaging",
            "flexible packaging", "closure", "dispenser",
        ],
        "company_name_keywords": [
            "International Paper", "Packaging Corporation", "Packaging Corp",
            "Smurfit WestRock", "Smurfit Kappa", "WestRock",
            "Greif", "Cascades",
            "Graphic Packaging", "Amcor", "Berry Global",
            "Silgan", "Aptargroup", "Ball Corporation",
            "Crown Holdings", "O-I Glass", "Sealed Air",
            "Sylvamo", "Mercer International", "Rayonier Advanced",
            "Suzano", "Clearwater Paper", "Canfor Pulp",
            "Sonoco", "Magnera",
        ],
        "earnings_keywords": [
            "earnings", "quarterly results", "EPS", "revenue", "guidance",
            "beats estimates", "misses estimates", "profit",
            "containerboard price", "box shipment", "pulp price",
        ],
        "ticker_map": {
            "international paper": "IP",
            "packaging corp": "PKG", "packaging corporation": "PKG",
            "smurfit westrock": "SW", "smurfit kappa": "SW", "westrock": "SW",
            "greif": "GEF",
            "cascades": "CAS.TO",
            "graphic packaging": "GPK",
            "amcor": "AMCR", "berry global": "AMCR",
            "silgan": "SLGN",
            "aptargroup": "ATR",
            "ball corporation": "BALL", "ball corp": "BALL",
            "crown holdings": "CCK",
            "o-i glass": "OI",
            "sealed air": "SEE",
            "sylvamo": "SLVM",
            "mercer international": "MERC",
            "rayonier advanced": "RYAM",
            "suzano": "SUZ",
            "clearwater paper": "CLW",
            "canfor pulp": "CFX.TO",
            "sonoco": "SON",
            "magnera": "MAGN",
        },
        "private_companies": {},
    },
}
