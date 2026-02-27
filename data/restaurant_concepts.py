"""
Restaurant concept/brand mapping for companies in coverage.
Data from latest 10-K filings, earnings releases, and investor presentations.

New fields:
  auv_m       - Average Unit Volume in $M (annual systemwide sales / unit count)
  royalty_pct  - Franchise royalty rate (% of sales); None for 100% company-operated
  unit_growth_pct - Net new unit growth YoY % (latest fiscal year)
  pct_parent_rev  - Approximate % of parent company total revenue; None for single-brand
"""

RESTAURANT_CONCEPTS = [
    # ── MCD ──────────────────────────────────────────────────────────────
    {
        "ticker": "MCD", "concept": "McDonald's",
        "cuisine": "Burgers / QSR",
        "units": 42_000, "unit_type": "global",
        "ownership": "~95% franchised, ~5% company-operated",
        "avg_check": "$9-11",
        "auv_m": 3.7, "royalty_pct": 4.0, "unit_growth_pct": 3.7, "pct_parent_rev": None,
        "description": (
            "World's largest QSR chain. Iconic menu (Big Mac, McNuggets, fries). "
            "Highly franchised model generates royalty + rent income. "
            "Strong drive-thru and digital/delivery mix."
        ),
    },
    # ── YUM ──────────────────────────────────────────────────────────────
    {
        "ticker": "YUM", "concept": "Taco Bell",
        "cuisine": "Mexican QSR",
        "units": 8_700, "unit_type": "global",
        "ownership": "~94% franchised",
        "avg_check": "$8-10",
        "auv_m": 2.1, "royalty_pct": 5.5, "unit_growth_pct": 4.5, "pct_parent_rev": 35,
        "description": (
            "YUM's strongest growth engine in the U.S. Value-oriented Mexican-inspired QSR. "
            "Industry-leading menu innovation (Crunchwrap, Baja Blast). "
            "Highest margins among YUM brands."
        ),
    },
    {
        "ticker": "YUM", "concept": "KFC",
        "cuisine": "Chicken QSR",
        "units": 29_000, "unit_type": "global",
        "ownership": "~99% franchised",
        "avg_check": "$10-13",
        "auv_m": 1.3, "royalty_pct": 5.0, "unit_growth_pct": 2.8, "pct_parent_rev": 38,
        "description": (
            "World's largest chicken QSR. Dominant in international markets "
            "(China, UK, Africa, SE Asia). Original Recipe and bucket model. "
            "U.S. business turnaround ongoing."
        ),
    },
    {
        "ticker": "YUM", "concept": "Pizza Hut",
        "cuisine": "Pizza QSR",
        "units": 19_500, "unit_type": "global",
        "ownership": "~99% franchised",
        "avg_check": "$12-18",
        "auv_m": 0.9, "royalty_pct": 6.0, "unit_growth_pct": -0.5, "pct_parent_rev": 23,
        "description": (
            "Global pizza chain. Shifted from dine-in to delivery/carryout model. "
            "Competes with DPZ and independent pizzerias. "
            "International strength, U.S. share losses."
        ),
    },
    {
        "ticker": "YUM", "concept": "Habit Burger Grill",
        "cuisine": "Burgers / Fast Casual",
        "units": 380, "unit_type": "U.S.",
        "ownership": "~60% company-operated",
        "avg_check": "$11-14",
        "auv_m": 1.8, "royalty_pct": 4.5, "unit_growth_pct": 6.0, "pct_parent_rev": 4,
        "description": (
            "Charburger-focused fast casual. West Coast concentration. "
            "Acquired by YUM in 2020. Smallest brand in YUM portfolio. "
            "Growth focus on franchising expansion."
        ),
    },
    # ── QSR (Restaurant Brands International) ────────────────────────────
    {
        "ticker": "QSR", "concept": "Burger King",
        "cuisine": "Burgers / QSR",
        "units": 18_900, "unit_type": "global",
        "ownership": "~100% franchised",
        "avg_check": "$8-10",
        "auv_m": 1.6, "royalty_pct": 4.5, "unit_growth_pct": 1.2, "pct_parent_rev": 38,
        "description": (
            "Second-largest burger QSR globally. Flame-grilled Whopper platform. "
            "Reclaim the Flame turnaround underway in U.S. ($400M+ investment). "
            "Strong international footprint."
        ),
    },
    {
        "ticker": "QSR", "concept": "Tim Hortons",
        "cuisine": "Coffee / Baked Goods",
        "units": 5_700, "unit_type": "global",
        "ownership": "~100% franchised",
        "avg_check": "$5-7",
        "auv_m": 1.9, "royalty_pct": 4.5, "unit_growth_pct": 2.5, "pct_parent_rev": 33,
        "description": (
            "Iconic Canadian coffee & donut chain. Dominant in Canada (~80% share of "
            "brewed coffee). Growing in international markets (India, Middle East). "
            "Breakfast and lunch daypart focus."
        ),
    },
    {
        "ticker": "QSR", "concept": "Popeyes",
        "cuisine": "Chicken QSR",
        "units": 3_800, "unit_type": "global",
        "ownership": "~100% franchised",
        "avg_check": "$10-13",
        "auv_m": 1.7, "royalty_pct": 5.0, "unit_growth_pct": 5.5, "pct_parent_rev": 18,
        "description": (
            "Louisiana-style fried chicken QSR. Chicken sandwich launch (2019) was "
            "a category-defining moment. Strong U.S. growth runway. "
            "Expanding internationally (UK, Europe, Asia)."
        ),
    },
    {
        "ticker": "QSR", "concept": "Firehouse Subs",
        "cuisine": "Subs / Sandwiches",
        "units": 1_250, "unit_type": "U.S./Canada",
        "ownership": "~100% franchised",
        "avg_check": "$10-13",
        "auv_m": 0.9, "royalty_pct": 6.0, "unit_growth_pct": 2.0, "pct_parent_rev": 11,
        "description": (
            "Premium sub sandwich chain. Acquired by RBI in 2021 for $1B. "
            "Specialty hot subs, founded by firefighters. "
            "Growth opportunity through RBI's franchisee network."
        ),
    },
    # ── WEN ──────────────────────────────────────────────────────────────
    {
        "ticker": "WEN", "concept": "Wendy's",
        "cuisine": "Burgers / QSR",
        "units": 7_200, "unit_type": "global",
        "ownership": "~95% franchised",
        "avg_check": "$9-11",
        "auv_m": 2.0, "royalty_pct": 4.0, "unit_growth_pct": 1.5, "pct_parent_rev": None,
        "description": (
            "Third-largest U.S. burger chain. Fresh never-frozen beef positioning. "
            "Strong breakfast daypart growth. Digital sales ~18% of mix. "
            "International expansion accelerating."
        ),
    },
    # ── DPZ ──────────────────────────────────────────────────────────────
    {
        "ticker": "DPZ", "concept": "Domino's",
        "cuisine": "Pizza Delivery/Carryout",
        "units": 21_000, "unit_type": "global",
        "ownership": "~98% franchised",
        "avg_check": "$15-22",
        "auv_m": 1.4, "royalty_pct": 5.5, "unit_growth_pct": 4.2, "pct_parent_rev": None,
        "description": (
            "World's largest pizza company by sales. Tech-driven delivery model. "
            "Fortressing strategy (dense store clustering). "
            "Strong digital ordering (>80% of U.S. sales). Uber Eats partnership."
        ),
    },
    # ── CMG ──────────────────────────────────────────────────────────────
    {
        "ticker": "CMG", "concept": "Chipotle Mexican Grill",
        "cuisine": "Mexican Fast Casual",
        "units": 3_700, "unit_type": "North America",
        "ownership": "100% company-operated",
        "avg_check": "$13-16",
        "auv_m": 3.2, "royalty_pct": None, "unit_growth_pct": 8.5, "pct_parent_rev": None,
        "description": (
            "Pioneer of fast casual. Fresh, customizable burritos/bowls. "
            "All company-owned stores = higher margins per unit but capital intensive. "
            "Chipotlane (drive-thru) driving new unit growth. Long runway to 7,000+ units."
        ),
    },
    # ── SHAK ─────────────────────────────────────────────────────────────
    {
        "ticker": "SHAK", "concept": "Shake Shack",
        "cuisine": "Burgers / Fast Casual",
        "units": 550, "unit_type": "global",
        "ownership": "~50% company / ~50% licensed",
        "avg_check": "$15-18",
        "auv_m": 4.0, "royalty_pct": 5.0, "unit_growth_pct": 14.0, "pct_parent_rev": None,
        "description": (
            "Premium burger and shake fast casual. Urban-focused with high AUVs (~$4M). "
            "Company-owned domestic, licensed international. "
            "Drive-thru and Shack Track (digital pickup) expansion."
        ),
    },
    # ── WING ─────────────────────────────────────────────────────────────
    {
        "ticker": "WING", "concept": "Wingstop",
        "cuisine": "Chicken Wings",
        "units": 2_400, "unit_type": "global",
        "ownership": "~98% franchised",
        "avg_check": "$16-20",
        "auv_m": 2.0, "royalty_pct": 6.0, "unit_growth_pct": 16.0, "pct_parent_rev": None,
        "description": (
            "Chicken wing-focused fast casual. Asset-light franchise model with "
            "industry-leading unit economics (AUV ~$2M, ~35% cash-on-cash returns). "
            "Digital-first (~65% of sales). Rapid international expansion."
        ),
    },
    # ── DRI ──────────────────────────────────────────────────────────────
    {
        "ticker": "DRI", "concept": "Olive Garden",
        "cuisine": "Italian Casual Dining",
        "units": 920, "unit_type": "U.S.",
        "ownership": "100% company-operated",
        "avg_check": "$18-23",
        "auv_m": 5.6, "royalty_pct": None, "unit_growth_pct": 0.5, "pct_parent_rev": 47,
        "description": (
            "Largest Italian casual dining chain in the U.S. Known for breadsticks "
            "and Never Ending Pasta Bowl. Consistent same-restaurant sales performer. "
            "DRI's largest brand by revenue (~47% of total)."
        ),
    },
    {
        "ticker": "DRI", "concept": "LongHorn Steakhouse",
        "cuisine": "Steak Casual Dining",
        "units": 580, "unit_type": "U.S.",
        "ownership": "100% company-operated",
        "avg_check": "$22-28",
        "auv_m": 5.3, "royalty_pct": None, "unit_growth_pct": 3.5, "pct_parent_rev": 28,
        "description": (
            "Second-largest casual steakhouse chain. Outperformed casual dining peers "
            "on SSS consistently. Quality-focused positioning. "
            "DRI's growth engine (~28% of total revenue)."
        ),
    },
    {
        "ticker": "DRI", "concept": "Ruth's Chris Steak House",
        "cuisine": "Fine Dining / Steak",
        "units": 160, "unit_type": "global",
        "ownership": "~55% company / ~45% franchised",
        "avg_check": "$75-100",
        "auv_m": 6.5, "royalty_pct": 5.0, "unit_growth_pct": 1.0, "pct_parent_rev": 9,
        "description": (
            "Upscale steakhouse chain. Acquired by DRI in 2023 for $715M. "
            "Sizzling butter finish on 1,800F plates. Higher-end customer base. "
            "Franchise + company-owned mix."
        ),
    },
    {
        "ticker": "DRI", "concept": "Other (Yard House, Cheddar's, etc.)",
        "cuisine": "Various Casual",
        "units": 340, "unit_type": "U.S.",
        "ownership": "100% company-operated",
        "avg_check": "$18-25",
        "auv_m": 5.0, "royalty_pct": None, "unit_growth_pct": 1.5, "pct_parent_rev": 16,
        "description": (
            "Includes Yard House (craft beer & American), Cheddar's Scratch Kitchen "
            "(value casual), Seasons 52, Eddie V's, Capital Grille. "
            "Diverse portfolio covering value to fine dining."
        ),
    },
    # ── EAT ──────────────────────────────────────────────────────────────
    {
        "ticker": "EAT", "concept": "Chili's Grill & Bar",
        "cuisine": "Casual Dining",
        "units": 1_230, "unit_type": "global",
        "ownership": "~58% company / ~42% franchised",
        "avg_check": "$16-20",
        "auv_m": 3.8, "royalty_pct": 4.5, "unit_growth_pct": -1.0, "pct_parent_rev": 96,
        "description": (
            "Major casual dining chain undergoing a value-driven renaissance. "
            "Big Smasher Burger and Triple Dipper driving traffic surges. "
            "Strongest SSS in casual dining in 2024-25. Digital/off-premise ~30%."
        ),
    },
    {
        "ticker": "EAT", "concept": "Maggiano's Little Italy",
        "cuisine": "Italian Casual Dining",
        "units": 49, "unit_type": "U.S.",
        "ownership": "100% company-operated",
        "avg_check": "$28-35",
        "auv_m": 7.5, "royalty_pct": None, "unit_growth_pct": 0.0, "pct_parent_rev": 4,
        "description": (
            "Upscale Italian-American casual dining. Family-style portions. "
            "Small but profitable. Catering & banquet business is a meaningful "
            "revenue driver. ~4% of EAT total revenue."
        ),
    },
    # ── TXRH ─────────────────────────────────────────────────────────────
    {
        "ticker": "TXRH", "concept": "Texas Roadhouse",
        "cuisine": "Steak Casual Dining",
        "units": 770, "unit_type": "global",
        "ownership": "~88% company / ~12% franchised",
        "avg_check": "$20-25",
        "auv_m": 7.5, "royalty_pct": 4.0, "unit_growth_pct": 3.5, "pct_parent_rev": 90,
        "description": (
            "Largest casual steakhouse chain by unit count. Hand-cut steaks, "
            "made-from-scratch sides, fresh-baked bread. Consistently top SSS in "
            "casual dining. High AUV (~$7.5M). Mostly company-operated."
        ),
    },
    {
        "ticker": "TXRH", "concept": "Bubba's 33",
        "cuisine": "Sports Bar / Pizza",
        "units": 50, "unit_type": "U.S.",
        "ownership": "100% company-operated",
        "avg_check": "$18-22",
        "auv_m": 5.5, "royalty_pct": None, "unit_growth_pct": 12.0, "pct_parent_rev": 7,
        "description": (
            "Family sports bar concept. Pizza, burgers, and wings. "
            "Smaller growth concept within TXRH. Testing and expanding selectively. "
            "Similar hospitality-driven culture as Texas Roadhouse."
        ),
    },
    {
        "ticker": "TXRH", "concept": "Jaggers",
        "cuisine": "Burgers & Chicken / Fast Casual",
        "units": 15, "unit_type": "U.S.",
        "ownership": "100% company-operated",
        "avg_check": "$12-15",
        "auv_m": 2.5, "royalty_pct": None, "unit_growth_pct": 25.0, "pct_parent_rev": 3,
        "description": (
            "Newer fast casual concept from TXRH. Burgers and chicken tenders. "
            "Early-stage growth, testing unit economics. "
            "Potential for franchising down the road."
        ),
    },
    # ── CAKE ─────────────────────────────────────────────────────────────
    {
        "ticker": "CAKE", "concept": "The Cheesecake Factory",
        "cuisine": "Upscale Casual Dining",
        "units": 210, "unit_type": "global",
        "ownership": "~80% company / ~20% licensed (intl)",
        "avg_check": "$25-35",
        "auv_m": 12.0, "royalty_pct": 5.0, "unit_growth_pct": 2.0, "pct_parent_rev": 78,
        "description": (
            "Iconic upscale casual dining with 250+ menu items. Highest AUVs in "
            "casual dining (~$12M). Known for cheesecakes and large portions. "
            "Domestic company-owned, international licensed."
        ),
    },
    {
        "ticker": "CAKE", "concept": "North Italia",
        "cuisine": "Italian Polished Casual",
        "units": 40, "unit_type": "U.S.",
        "ownership": "100% company-operated",
        "avg_check": "$30-40",
        "auv_m": 7.0, "royalty_pct": None, "unit_growth_pct": 18.0, "pct_parent_rev": 13,
        "description": (
            "Upscale Italian restaurant brand acquired via Fox Restaurant Concepts. "
            "Growth vehicle for CAKE. Chef-driven menu, scratch kitchen. "
            "Targeting 75+ locations over time."
        ),
    },
    {
        "ticker": "CAKE", "concept": "Other (FRC brands)",
        "cuisine": "Various Upscale Casual",
        "units": 25, "unit_type": "U.S.",
        "ownership": "100% company-operated",
        "avg_check": "$25-40",
        "auv_m": 4.5, "royalty_pct": None, "unit_growth_pct": 10.0, "pct_parent_rev": 9,
        "description": (
            "Fox Restaurant Concepts portfolio: Flower Child (healthy fast casual), "
            "Culinary Dropout, Blanco Tacos + Tequila. Small but growing "
            "stable of chef-driven concepts."
        ),
    },
    # ── SBUX ─────────────────────────────────────────────────────────────
    {
        "ticker": "SBUX", "concept": "Starbucks",
        "cuisine": "Coffee / Beverages",
        "units": 40_000, "unit_type": "global",
        "ownership": "~52% company / ~48% licensed",
        "avg_check": "$6-8",
        "auv_m": 2.0, "royalty_pct": None, "unit_growth_pct": 5.0, "pct_parent_rev": None,
        "description": (
            "World's largest coffeehouse chain. Premium coffee, espresso, and "
            "cold beverages. Cold platform (~75% of beverage mix in U.S.). "
            "Loyalty program with 34M+ active members. Triple Shot reinvention plan."
        ),
    },
    # ── DENN ─────────────────────────────────────────────────────────────
    {
        "ticker": "DENN", "concept": "Denny's",
        "cuisine": "Family Dining / Breakfast",
        "units": 1_530, "unit_type": "global",
        "ownership": "~96% franchised",
        "avg_check": "$12-15",
        "auv_m": 1.5, "royalty_pct": 4.5, "unit_growth_pct": -2.5, "pct_parent_rev": 90,
        "description": (
            "Iconic 24/7 family dining chain. Breakfast-heavy but serves all dayparts. "
            "Grand Slam and value-focused promotions. Asset-light franchise model. "
            "Keke's Breakfast Cafe brand acquired 2023."
        ),
    },
    {
        "ticker": "DENN", "concept": "Keke's Breakfast Cafe",
        "cuisine": "Breakfast / Brunch",
        "units": 65, "unit_type": "U.S. (Southeast)",
        "ownership": "~100% franchised",
        "avg_check": "$13-16",
        "auv_m": 2.0, "royalty_pct": 5.0, "unit_growth_pct": 15.0, "pct_parent_rev": 10,
        "description": (
            "Breakfast and brunch focused concept. Acquired by DENN in 2023 for $82.5M. "
            "Florida-based, expanding regionally. Breakfast-only daypart (7am-2:30pm). "
            "Growth concept for DENN's portfolio."
        ),
    },
]
