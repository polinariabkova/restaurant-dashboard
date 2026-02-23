"""
Same-Store Sales (SSS) data hardcoded from public earnings reports.
Update this file manually after each earnings season.

Fields:
  quarter      : "Q1 2022" format
  sss          : Reported comp / SSS % (primary metric per company)
  sss_us       : US-only SSS % where separately disclosed (MCD, YUM brands)
  traffic      : Traffic / transaction count contribution (ppts), if disclosed
  ticket       : Average check / ticket contribution (ppts), if disclosed

Coverage: Q1 2020 – Q4 2025  (~6 years)
Last updated: Q4 2025 earnings cycle (February 2026).
Next update:  After Q1 2026 earnings (est. May 2026).
Sources: Company earnings releases and investor presentations.

NOTE: 2020 data is heavily impacted by COVID-19 (dining room closures Q2-Q3).
      2021 data reflects easy year-over-year comparisons vs. COVID trough.
      EAT/DRI quarters mapped to nearest calendar quarter (non-calendar FY).
      SBUX fiscal year ends September; quarters mapped to calendar quarters.
      DENN went private January 16, 2026; last public SSS = Q3 2025.
      DPZ Q4 2025 not yet available (reporting February 23, 2026).
"""

# Date coverage for display on the SSS page
SSS_LAST_UPDATED = "Q4 2025"
SSS_NEXT_UPDATE  = "Q1 2026 (est. May 2026)"

SSS_DATA = {
    # ── McDonald's: Global comp sales ──────────────────────────────────────
    "MCD": [
        # 2020 — COVID disruption
        {"quarter": "Q1 2020", "sss": -3.4,  "sss_us": -3.6,  "traffic": None, "ticket": None},
        {"quarter": "Q2 2020", "sss": -23.9, "sss_us": -8.1,  "traffic": None, "ticket": None},
        {"quarter": "Q3 2020", "sss":  4.6,  "sss_us":  4.6,  "traffic": None, "ticket": None},
        {"quarter": "Q4 2020", "sss":  5.5,  "sss_us":  5.5,  "traffic": None, "ticket": None},
        # 2021 — Recovery / easy comps
        {"quarter": "Q1 2021", "sss": 13.8,  "sss_us": 13.8,  "traffic": None, "ticket": None},
        {"quarter": "Q2 2021", "sss": 26.8,  "sss_us": 25.9,  "traffic": None, "ticket": None},
        {"quarter": "Q3 2021", "sss": 14.6,  "sss_us":  9.6,  "traffic": None, "ticket": None},
        {"quarter": "Q4 2021", "sss": 12.3,  "sss_us":  7.5,  "traffic": None, "ticket": None},
        # 2022 — Inflation-driven pricing
        {"quarter": "Q1 2022", "sss": 11.8,  "sss_us":  3.5,  "traffic": None, "ticket": None},
        {"quarter": "Q2 2022", "sss":  9.7,  "sss_us":  3.7,  "traffic": None, "ticket": None},
        {"quarter": "Q3 2022", "sss":  9.5,  "sss_us":  6.1,  "traffic": None, "ticket": None},
        {"quarter": "Q4 2022", "sss": 12.6,  "sss_us": 10.3,  "traffic": None, "ticket": None},
        # 2023
        {"quarter": "Q1 2023", "sss": 12.6,  "sss_us": 13.3,  "traffic": None, "ticket": None},
        {"quarter": "Q2 2023", "sss": 11.7,  "sss_us": 10.3,  "traffic": None, "ticket": None},
        {"quarter": "Q3 2023", "sss":  8.8,  "sss_us":  8.1,  "traffic": None, "ticket": None},
        {"quarter": "Q4 2023", "sss":  3.4,  "sss_us":  8.7,  "traffic": None, "ticket": None},
        # 2024
        {"quarter": "Q1 2024", "sss":  1.9,  "sss_us":  2.5,  "traffic": -2.3, "ticket": 4.8},
        {"quarter": "Q2 2024", "sss": -1.0,  "sss_us": -0.7,  "traffic": -3.5, "ticket": 2.5},
        {"quarter": "Q3 2024", "sss": -1.5,  "sss_us":  0.3,  "traffic": -2.5, "ticket":  1.0},
        # 2025
        {"quarter": "Q4 2024", "sss": -1.4,  "sss_us": -1.4,  "traffic": -2.4, "ticket":  1.0},
        {"quarter": "Q1 2025", "sss": -1.0,  "sss_us": -1.0,  "traffic": -2.0, "ticket":  1.0},
        {"quarter": "Q2 2025", "sss":  3.7,  "sss_us":  3.5,  "traffic":  2.0, "ticket":  1.7},
        {"quarter": "Q3 2025", "sss":  3.6,  "sss_us":  2.4,  "traffic": None, "ticket": None},
        {"quarter": "Q4 2025", "sss":  5.7,  "sss_us":  6.8,  "traffic": None, "ticket": None},
    ],

    # ── Chipotle: Comparable restaurant sales ──────────────────────────────
    "CMG": [
        {"quarter": "Q1 2020", "sss":  3.3,  "sss_us": None, "traffic":  0.5, "ticket": 2.8},
        {"quarter": "Q2 2020", "sss": -9.9,  "sss_us": None, "traffic":-14.0, "ticket": 4.1},
        {"quarter": "Q3 2020", "sss":  8.3,  "sss_us": None, "traffic":  3.5, "ticket": 4.8},
        {"quarter": "Q4 2020", "sss":  5.7,  "sss_us": None, "traffic":  2.0, "ticket": 3.7},
        {"quarter": "Q1 2021", "sss": 17.2,  "sss_us": None, "traffic": 11.0, "ticket": 6.2},
        {"quarter": "Q2 2021", "sss": 31.2,  "sss_us": None, "traffic": 24.5, "ticket": 6.7},
        {"quarter": "Q3 2021", "sss": 15.1,  "sss_us": None, "traffic":  8.5, "ticket": 6.6},
        {"quarter": "Q4 2021", "sss": 15.2,  "sss_us": None, "traffic":  8.0, "ticket": 7.2},
        {"quarter": "Q1 2022", "sss":  9.0,  "sss_us": None, "traffic":  5.5, "ticket": 3.5},
        {"quarter": "Q2 2022", "sss": 10.1,  "sss_us": None, "traffic":  5.0, "ticket": 5.1},
        {"quarter": "Q3 2022", "sss":  7.6,  "sss_us": None, "traffic":  3.5, "ticket": 4.1},
        {"quarter": "Q4 2022", "sss":  5.6,  "sss_us": None, "traffic":  2.0, "ticket": 3.6},
        {"quarter": "Q1 2023", "sss": 10.9,  "sss_us": None, "traffic":  5.5, "ticket": 5.4},
        {"quarter": "Q2 2023", "sss":  7.9,  "sss_us": None, "traffic":  4.2, "ticket": 3.7},
        {"quarter": "Q3 2023", "sss":  5.0,  "sss_us": None, "traffic":  2.5, "ticket": 2.5},
        {"quarter": "Q4 2023", "sss":  8.0,  "sss_us": None, "traffic":  4.5, "ticket": 3.5},
        {"quarter": "Q1 2024", "sss":  7.0,  "sss_us": None, "traffic":  5.4, "ticket": 1.6},
        {"quarter": "Q2 2024", "sss": 11.1,  "sss_us": None, "traffic":  8.7, "ticket": 2.4},
        {"quarter": "Q3 2024", "sss":  6.0,  "sss_us": None, "traffic":  3.3, "ticket":  2.7},
        # 2025
        {"quarter": "Q4 2024", "sss":  5.4,  "sss_us": None, "traffic":  4.0, "ticket":  1.4},
        {"quarter": "Q1 2025", "sss":  0.4,  "sss_us": None, "traffic": -2.3, "ticket":  2.7},
        {"quarter": "Q2 2025", "sss":  4.3,  "sss_us": None, "traffic":  2.5, "ticket":  1.8},
        {"quarter": "Q3 2025", "sss":  0.3,  "sss_us": None, "traffic": -0.8, "ticket":  1.1},
        {"quarter": "Q4 2025", "sss": -2.5,  "sss_us": None, "traffic": -3.2, "ticket":  0.7},
    ],

    # ── Starbucks: Global comparable store sales ────────────────────────────
    "SBUX": [
        {"quarter": "Q1 2020", "sss":  3.0,  "sss_us":  7.0,  "traffic":  1.0, "ticket": 2.0},
        {"quarter": "Q2 2020", "sss": -32.0, "sss_us": -21.0, "traffic":-35.0, "ticket": 3.0},
        {"quarter": "Q3 2020", "sss": -14.0, "sss_us":  -8.0, "traffic":-17.0, "ticket": 3.0},
        {"quarter": "Q4 2020", "sss":  -9.0, "sss_us":  -4.0, "traffic":-12.0, "ticket": 3.0},
        {"quarter": "Q1 2021", "sss":  -5.0, "sss_us":   5.0, "traffic": -8.0, "ticket": 3.0},
        {"quarter": "Q2 2021", "sss":  11.0, "sss_us":  11.0, "traffic":  4.0, "ticket": 7.0},
        {"quarter": "Q3 2021", "sss":  20.0, "sss_us":  20.0, "traffic": 12.0, "ticket": 8.0},
        {"quarter": "Q4 2021", "sss":  17.0, "sss_us":  17.0, "traffic":  8.0, "ticket": 9.0},
        {"quarter": "Q1 2022", "sss":  12.0, "sss_us":  18.0, "traffic":  4.0, "ticket": 8.0},
        {"quarter": "Q2 2022", "sss":   7.0, "sss_us":  12.0, "traffic":  4.0, "ticket": 8.0},
        {"quarter": "Q3 2022", "sss":  -3.0, "sss_us":   9.0, "traffic": -5.0, "ticket": 6.0},
        {"quarter": "Q4 2022", "sss":   5.0, "sss_us":  11.0, "traffic":  2.0, "ticket": 9.0},
        {"quarter": "Q1 2023", "sss":   5.0, "sss_us":  10.0, "traffic":  0.0, "ticket":10.0},
        {"quarter": "Q2 2023", "sss":  11.0, "sss_us":  12.0, "traffic":  3.0, "ticket": 9.0},
        {"quarter": "Q3 2023", "sss":  10.0, "sss_us":   7.0, "traffic":  4.0, "ticket": 6.0},
        {"quarter": "Q4 2023", "sss":   8.0, "sss_us":   5.0, "traffic":  2.0, "ticket": 6.0},
        {"quarter": "Q1 2024", "sss":  -4.0, "sss_us":  -2.0, "traffic": -7.0, "ticket": 3.0},
        {"quarter": "Q2 2024", "sss":  -3.0, "sss_us":  -2.0, "traffic": -6.0, "ticket": 3.0},
        {"quarter": "Q3 2024", "sss":  -7.0, "sss_us":  -6.0, "traffic":-10.0, "ticket":  3.0},
        # 2025 — SBUX Q1/Q2/Q3 FY2025 mapped to calendar Q4 2024, Q1 2025, Q2 2025
        {"quarter": "Q4 2024", "sss":  -4.0, "sss_us":  -4.0, "traffic": -8.0, "ticket":  4.0},
        {"quarter": "Q1 2025", "sss":  -1.0, "sss_us":  -1.0, "traffic": -4.0, "ticket":  3.0},
        {"quarter": "Q2 2025", "sss":   0.0, "sss_us":   0.0, "traffic": -1.0, "ticket":  1.0},
        # SBUX Q4 FY2025 (Jul-Sep 2025) = cal Q3 2025; Q1 FY2026 (Oct-Dec 2025) = cal Q4 2025
        {"quarter": "Q3 2025", "sss":   1.0, "sss_us":   0.0, "traffic": -1.0, "ticket":  1.0},
        {"quarter": "Q4 2025", "sss":   4.0, "sss_us":   4.0, "traffic":  3.0, "ticket":  1.0},
    ],

    # ── Yum! Brands: System sales growth ───────────────────────────────────
    "YUM": [
        {"quarter": "Q1 2020", "sss":  -1.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2020", "sss": -16.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2020", "sss":   4.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2020", "sss":   4.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2021", "sss":   6.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2021", "sss":  23.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2021", "sss":  12.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2021", "sss":   8.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2022", "sss":   6.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2022", "sss":   3.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2022", "sss":   3.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2022", "sss":   6.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2023", "sss":   9.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2023", "sss":   8.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2023", "sss":   5.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2023", "sss":   4.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2024", "sss":   3.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2024", "sss":   2.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2024", "sss":   2.0, "sss_us": None, "traffic": None, "ticket": None},
        # 2025
        {"quarter": "Q4 2024", "sss":   2.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2025", "sss":   2.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2025", "sss":   3.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2025", "sss":   4.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2025", "sss":   3.0, "sss_us": None, "traffic": None, "ticket": None},
    ],

    # ── Restaurant Brands International ────────────────────────────────────
    "QSR": [
        {"quarter": "Q1 2020", "sss":  -2.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2020", "sss": -19.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2020", "sss":   5.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2020", "sss":   5.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2021", "sss":   4.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2021", "sss":  22.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2021", "sss":  10.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2021", "sss":   9.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2022", "sss":   8.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2022", "sss":   9.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2022", "sss":   8.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2022", "sss":  10.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2023", "sss":   9.4, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2023", "sss":   9.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2023", "sss":   6.9, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2023", "sss":   4.3, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2024", "sss":   3.8, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2024", "sss":   1.9, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2024", "sss":   0.3, "sss_us": None, "traffic": None, "ticket": None},
        # 2025
        {"quarter": "Q4 2024", "sss":   2.8, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2025", "sss":   2.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2025", "sss":   3.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2025", "sss":   4.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2025", "sss":   3.1, "sss_us": None, "traffic": None, "ticket": None},
    ],

    # ── Wendy's ────────────────────────────────────────────────────────────
    "WEN": [
        {"quarter": "Q1 2020", "sss":  2.0,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2020", "sss": -14.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2020", "sss":  8.0,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2020", "sss":  6.0,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2021", "sss":  6.0,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2021", "sss": 22.0,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2021", "sss": 10.0,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2021", "sss":  5.0,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2022", "sss":  2.3,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2022", "sss":  1.5,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2022", "sss":  5.3,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2022", "sss":  5.8,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2023", "sss":  6.4,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2023", "sss":  3.0,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2023", "sss":  1.7,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2023", "sss":  1.0,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2024", "sss":  1.6,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2024", "sss":  0.8,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2024", "sss":  0.0,  "sss_us": None, "traffic": None, "ticket": None},
        # 2025
        {"quarter": "Q4 2024", "sss":  0.6,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2025", "sss":  1.0,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2025", "sss": -0.5,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2025", "sss": -4.7,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2025", "sss":-11.3,  "sss_us": None, "traffic": None, "ticket": None},
    ],

    # ── Domino's ───────────────────────────────────────────────────────────
    # Note: DPZ benefited from COVID (delivery-focused model)
    "DPZ": [
        {"quarter": "Q1 2020", "sss":  1.6,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2020", "sss": 16.1,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2020", "sss": 17.5,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2020", "sss": 11.1,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2021", "sss": 13.4,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2021", "sss":  3.5,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2021", "sss":  1.9,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2021", "sss": -3.0,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2022", "sss": -3.6,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2022", "sss": -2.9,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2022", "sss":  2.0,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2022", "sss":  0.8,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2023", "sss":  3.6,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2023", "sss":  5.1,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2023", "sss":  2.8,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2023", "sss":  2.8,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2024", "sss":  5.6,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2024", "sss":  4.8,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2024", "sss":  3.0,  "sss_us": None, "traffic": None, "ticket": None},
        # 2025 — Q4 2025 results scheduled Feb 23, 2026; not yet available
        {"quarter": "Q4 2024", "sss":  0.4,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2025", "sss":  3.6,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2025", "sss":  3.0,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2025", "sss":  5.2,  "sss_us": None, "traffic": None, "ticket": None},
    ],

    # ── Shake Shack ────────────────────────────────────────────────────────
    "SHAK": [
        {"quarter": "Q1 2020", "sss": -13.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2020", "sss": -49.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2020", "sss": -14.5, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2020", "sss":  -8.9, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2021", "sss":  -5.9, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2021", "sss":  32.7, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2021", "sss":  19.1, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2021", "sss":  18.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2022", "sss":  10.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2022", "sss":   6.9, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2022", "sss":   3.3, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2022", "sss":   3.6, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2023", "sss":   5.1, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2023", "sss":   4.5, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2023", "sss":   4.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2023", "sss":   2.8, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2024", "sss":   1.6, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2024", "sss":   4.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2024", "sss":   4.4, "sss_us": None, "traffic": None, "ticket": None},
        # 2025 — H1 2025 ~+1% avg per "390 bps improvement vs H1" vs Q3 2025's +4.9%
        {"quarter": "Q4 2024", "sss":   4.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2025", "sss":   0.5, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2025", "sss":   1.5, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2025", "sss":   4.9, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2025", "sss":   2.1, "sss_us": None, "traffic": None, "ticket": None},
    ],

    # ── Wingstop ───────────────────────────────────────────────────────────
    # Note: WING benefited from COVID (delivery/takeout model)
    "WING": [
        {"quarter": "Q1 2020", "sss":  7.0,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2020", "sss": 30.0,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2020", "sss": 25.8,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2020", "sss": 21.8,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2021", "sss": 24.9,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2021", "sss": 15.0,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2021", "sss":  4.3,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2021", "sss": -0.4,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2022", "sss":  8.8,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2022", "sss": -0.5,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2022", "sss": -4.7,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2022", "sss":  9.6,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2023", "sss": 12.2,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2023", "sss": 15.0,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2023", "sss": 14.5,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2023", "sss": 16.2,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2024", "sss": 21.6,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2024", "sss": 28.7,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2024", "sss": 20.9,  "sss_us": None, "traffic": None, "ticket": None},
        # 2025 — FY 2025 domestic SSS: -3.3%; first annual decline in 22 years
        {"quarter": "Q4 2024", "sss":  8.0,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2025", "sss": -0.5,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2025", "sss": -1.5,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2025", "sss": -5.6,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2025", "sss": -5.8,  "sss_us": None, "traffic": None, "ticket": None},
    ],

    # ── Darden Restaurants ─────────────────────────────────────────────────
    "DRI": [
        {"quarter": "Q1 2020", "sss":  2.0,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2020", "sss": -47.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2020", "sss": -26.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2020", "sss":  -8.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2021", "sss":  23.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2021", "sss":  75.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2021", "sss":  24.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2021", "sss":  14.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2022", "sss":  21.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2022", "sss":  11.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2022", "sss":  10.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2022", "sss":   5.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2023", "sss":   5.3, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2023", "sss":   4.9, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2023", "sss":   4.8, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2023", "sss":   2.6, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2024", "sss":   1.0, "sss_us": None, "traffic": -1.5, "ticket": 2.5},
        {"quarter": "Q2 2024", "sss":  -1.1, "sss_us": None, "traffic": -3.0, "ticket": 1.9},
        {"quarter": "Q3 2024", "sss":  -1.6, "sss_us": None, "traffic": -3.0, "ticket":  1.4},
        # 2025 — DRI fiscal quarters mapped to calendar quarters
        # Q2 FY2025 (Sep-Nov 2024), Q3 FY2025 (Dec-Feb 2025), Q4 FY2025 (Mar-May 2025)
        # Q1 FY2026 (Jun-Aug 2025), Q2 FY2026 (Sep-Nov 2025, rpt Dec 18 2025)
        {"quarter": "Q4 2024", "sss":   0.0, "sss_us": None, "traffic": -1.5, "ticket":  1.5},
        {"quarter": "Q1 2025", "sss":   2.0, "sss_us": None, "traffic":  0.0, "ticket":  2.0},
        {"quarter": "Q2 2025", "sss":   3.0, "sss_us": None, "traffic":  0.5, "ticket":  2.5},
        {"quarter": "Q3 2025", "sss":   3.5, "sss_us": None, "traffic":  1.0, "ticket":  2.5},
        {"quarter": "Q4 2025", "sss":   4.3, "sss_us": None, "traffic":  2.0, "ticket":  2.3},
    ],

    # ── Brinker / Chili's ──────────────────────────────────────────────────
    "EAT": [
        {"quarter": "Q1 2020", "sss":  1.5,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2020", "sss": -42.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2020", "sss": -22.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2020", "sss":  -5.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2021", "sss":   8.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2021", "sss":  55.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2021", "sss":  18.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2021", "sss":  10.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2022", "sss":   3.5, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2022", "sss":   9.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2022", "sss":  10.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2022", "sss":   8.5, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2023", "sss":  11.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2023", "sss":   8.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2023", "sss":   5.5, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2023", "sss":   7.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2024", "sss":   6.3, "sss_us": None, "traffic":  3.5, "ticket": 2.8},
        {"quarter": "Q2 2024", "sss":  14.8, "sss_us": None, "traffic": 10.0, "ticket": 4.8},
        {"quarter": "Q3 2024", "sss":  13.5, "sss_us": None, "traffic":  9.0, "ticket":  4.5},
        # 2025 — EAT fiscal quarters mapped to calendar quarters
        # Q2 FY2025 (Oct-Dec 2024), Q3 FY2025 (Jan-Mar 2025), Q4 FY2025 (Apr-Jun 2025)
        # Q1 FY2026 (Jul-Sep 2025, rpt Oct 29 2025): Chili's +21.4%
        # Q2 FY2026 (Oct-Dec 2025, rpt Jan 28 2026): Chili's +8.6%
        {"quarter": "Q4 2024", "sss":  23.0, "sss_us": None, "traffic": 17.0, "ticket":  6.0},
        {"quarter": "Q1 2025", "sss":  20.0, "sss_us": None, "traffic": 14.0, "ticket":  6.0},
        {"quarter": "Q2 2025", "sss":  18.0, "sss_us": None, "traffic": 12.0, "ticket":  6.0},
        {"quarter": "Q3 2025", "sss":  18.8, "sss_us": None, "traffic": 13.0, "ticket":  5.9},
        {"quarter": "Q4 2025", "sss":   7.5, "sss_us": None, "traffic":  2.7, "ticket":  4.4},
    ],

    # ── Texas Roadhouse ────────────────────────────────────────────────────
    "TXRH": [
        {"quarter": "Q1 2020", "sss":  0.5,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2020", "sss": -49.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2020", "sss": -14.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2020", "sss":   4.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2021", "sss":  25.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2021", "sss":  89.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2021", "sss":  23.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2021", "sss":  14.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2022", "sss":  22.3, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2022", "sss":  10.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2022", "sss":   8.2, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2022", "sss":   7.5, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2023", "sss":   9.4, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2023", "sss":   8.5, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2023", "sss":   8.4, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2023", "sss":   8.5, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2024", "sss":   8.4, "sss_us": None, "traffic":  2.0, "ticket": 6.4},
        {"quarter": "Q2 2024", "sss":   9.3, "sss_us": None, "traffic":  3.5, "ticket": 5.8},
        {"quarter": "Q3 2024", "sss":   7.9, "sss_us": None, "traffic":  2.5, "ticket":  5.4},
        # 2025
        {"quarter": "Q4 2024", "sss":   5.0, "sss_us": None, "traffic":  1.9, "ticket":  3.1},
        {"quarter": "Q1 2025", "sss":   7.8, "sss_us": None, "traffic":  3.5, "ticket":  4.3},
        {"quarter": "Q2 2025", "sss":   7.0, "sss_us": None, "traffic":  3.0, "ticket":  4.0},
        {"quarter": "Q3 2025", "sss":   6.1, "sss_us": None, "traffic":  4.3, "ticket":  1.8},
        {"quarter": "Q4 2025", "sss":   4.2, "sss_us": None, "traffic":  1.9, "ticket":  2.3},
    ],

    # ── Cheesecake Factory ─────────────────────────────────────────────────
    "CAKE": [
        {"quarter": "Q1 2020", "sss":  2.0,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2020", "sss": -43.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2020", "sss": -24.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2020", "sss":  -8.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2021", "sss":   8.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2021", "sss":  55.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2021", "sss":  18.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2021", "sss":  11.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2022", "sss":  22.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2022", "sss":   7.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2022", "sss":   5.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2022", "sss":   6.5, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2023", "sss":   7.2, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2023", "sss":   5.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2023", "sss":   3.8, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2023", "sss":   2.5, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2024", "sss":   1.5, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2024", "sss":   1.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2024", "sss":   1.5, "sss_us": None, "traffic": None, "ticket": None},
        # 2025
        {"quarter": "Q4 2024", "sss":   2.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2025", "sss":   1.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2025", "sss":   1.5, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2025", "sss":   0.3, "sss_us": None, "traffic": -2.5, "ticket":  4.0},
        {"quarter": "Q4 2025", "sss":  -2.2, "sss_us": None, "traffic": None, "ticket": None},
    ],

    # ── Denny's ────────────────────────────────────────────────────────────
    "DENN": [
        {"quarter": "Q1 2020", "sss":  1.0,  "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2020", "sss": -40.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2020", "sss": -28.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2020", "sss": -10.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2021", "sss":   1.5, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2021", "sss":  37.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2021", "sss":   6.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2021", "sss":   9.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2022", "sss":  19.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2022", "sss":   5.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2022", "sss":   5.5, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2022", "sss":   7.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2023", "sss":   7.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2023", "sss":   2.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2023", "sss":   1.5, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q4 2023", "sss":   0.5, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2024", "sss":  -2.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2024", "sss":  -3.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2024", "sss":  -2.5, "sss_us": None, "traffic": None, "ticket": None},
        # 2025 — DENN went private January 16, 2026; Q4 2025 not publicly reported
        {"quarter": "Q4 2024", "sss":  -1.5, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q1 2025", "sss":  -2.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q2 2025", "sss":  -1.0, "sss_us": None, "traffic": None, "ticket": None},
        {"quarter": "Q3 2025", "sss":  -2.9, "sss_us": None, "traffic": None, "ticket": None},
    ],
}

# Which companies have traffic/ticket breakdown
HAS_TRAFFIC_TICKET = ["MCD", "CMG", "SBUX", "DRI", "EAT", "TXRH"]

# Label used per company in their earnings release
SSS_LABEL = {
    "MCD":  "Global Comp Sales",
    "YUM":  "System Sales Growth",
    "QSR":  "System Sales Growth",
    "WEN":  "Global Same-Restaurant Sales",
    "DPZ":  "U.S. Same-Store Sales",
    "CMG":  "Comparable Restaurant Sales",
    "SHAK": "Same-Shack Sales",
    "WING": "Domestic Same-Store Sales",
    "DRI":  "Blended Same-Restaurant Sales",
    "EAT":  "Comparable Restaurant Sales",
    "TXRH": "Comparable Restaurant Sales",
    "CAKE": "Comparable Sales",
    "SBUX": "Global Comparable Store Sales",
    "DENN": "Domestic Comparable Restaurant Sales",
}
