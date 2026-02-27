"""
Hotel KPI data hardcoded from public 8-K earnings releases.
Update this file manually after each earnings season.

Fields:
  quarter    : "Q1 2024" format
  revpar     : Comparable systemwide RevPAR ($), U.S./domestic where available
  revpar_yoy : RevPAR YoY % change
  adr        : Average Daily Rate ($)
  adr_yoy    : ADR YoY % change
  occ        : Occupancy rate (%), expressed as percentage (e.g. 72.2 = 72.2%)
  occ_chg    : Occupancy YoY change in percentage points (e.g. -0.9)

Coverage: Q1 2024 - Q4 2025 (8 quarters)
Last updated: Q4 2025 earnings cycle (February 2026).
Next update:  After Q1 2026 earnings (est. May 2026).
Sources: Company 8-K earnings releases and investor presentations.

NOTE: Marriott, Hilton = U.S. & Canada comparable systemwide.
      Hyatt = global comparable systemwide (U.S.-only not consistently disclosed).
      Wyndham = U.S. comparable systemwide.
      Choice Hotels = U.S. domestic comparable.
      PK (Park Hotels) = comparable consolidated portfolio.
"""

HOTEL_KPI_LAST_UPDATED = "Q4 2025"
HOTEL_KPI_NEXT_UPDATE  = "Q1 2026 (est. May 2026)"

HOTEL_KPI_DATA = {
    # ── Marriott: U.S. & Canada comparable systemwide ─────────────────────
    "MAR": [
        # 2024
        {"quarter": "Q1 2024", "revpar": 119.57, "revpar_yoy":  1.5, "adr": 182.27, "adr_yoy":  1.8, "occ": 65.5, "occ_chg": -0.2},
        {"quarter": "Q2 2024", "revpar": 142.78, "revpar_yoy":  3.9, "adr": 191.04, "adr_yoy":  2.6, "occ": 74.8, "occ_chg":  0.9},
        {"quarter": "Q3 2024", "revpar": 136.35, "revpar_yoy":  2.1, "adr": 186.74, "adr_yoy":  1.3, "occ": 73.0, "occ_chg":  0.6},
        {"quarter": "Q4 2024", "revpar": 126.05, "revpar_yoy":  4.1, "adr": 188.13, "adr_yoy":  3.0, "occ": 67.0, "occ_chg":  0.7},
        # 2025
        {"quarter": "Q1 2025", "revpar": 123.40, "revpar_yoy":  3.3, "adr": 187.37, "adr_yoy":  2.7, "occ": 65.9, "occ_chg":  0.4},
        {"quarter": "Q2 2025", "revpar": 142.78, "revpar_yoy":  0.0, "adr": 193.29, "adr_yoy":  1.2, "occ": 73.9, "occ_chg": -0.9},
        {"quarter": "Q3 2025", "revpar": 135.85, "revpar_yoy": -0.4, "adr": 188.25, "adr_yoy":  0.8, "occ": 72.2, "occ_chg": -0.8},
        {"quarter": "Q4 2025", "revpar": 128.83, "revpar_yoy": -0.1, "adr": 192.00, "adr_yoy":  2.1, "occ": 67.1, "occ_chg": -0.9},
    ],
    # ── Hilton: U.S. comparable systemwide ────────────────────────────────
    "HLT": [
        # 2024
        {"quarter": "Q1 2024", "revpar": 109.11, "revpar_yoy":  2.0, "adr": 161.82, "adr_yoy":  1.2, "occ": 67.5, "occ_chg":  0.5},
        {"quarter": "Q2 2024", "revpar": 133.54, "revpar_yoy":  3.5, "adr": 173.96, "adr_yoy":  1.9, "occ": 76.8, "occ_chg":  1.2},
        {"quarter": "Q3 2024", "revpar": 127.88, "revpar_yoy":  1.4, "adr": 170.30, "adr_yoy":  1.0, "occ": 75.1, "occ_chg":  0.3},
        {"quarter": "Q4 2024", "revpar": 112.28, "revpar_yoy":  3.5, "adr": 164.97, "adr_yoy":  2.1, "occ": 68.1, "occ_chg":  0.8},
        # 2025
        {"quarter": "Q1 2025", "revpar": 111.39, "revpar_yoy":  2.1, "adr": 164.58, "adr_yoy":  1.7, "occ": 67.7, "occ_chg":  0.2},
        {"quarter": "Q2 2025", "revpar": 131.66, "revpar_yoy": -1.5, "adr": 173.61, "adr_yoy": -0.2, "occ": 75.8, "occ_chg": -1.0},
        {"quarter": "Q3 2025", "revpar": 126.09, "revpar_yoy": -1.4, "adr": 170.13, "adr_yoy": -0.1, "occ": 74.1, "occ_chg": -1.0},
        {"quarter": "Q4 2025", "revpar": 110.38, "revpar_yoy": -1.7, "adr": 163.87, "adr_yoy": -0.7, "occ": 67.4, "occ_chg": -0.7},
    ],
    # ── Hyatt: Global comparable systemwide ───────────────────────────────
    "H": [
        # 2024
        {"quarter": "Q1 2024", "revpar": 127.23, "revpar_yoy":  5.5, "adr": 195.52, "adr_yoy":  3.8, "occ": 65.1, "occ_chg":  1.0},
        {"quarter": "Q2 2024", "revpar": 150.34, "revpar_yoy":  4.7, "adr": 204.73, "adr_yoy":  2.4, "occ": 73.4, "occ_chg":  1.6},
        {"quarter": "Q3 2024", "revpar": 151.99, "revpar_yoy":  3.0, "adr": 208.30, "adr_yoy":  1.2, "occ": 73.0, "occ_chg":  1.3},
        {"quarter": "Q4 2024", "revpar": 130.68, "revpar_yoy":  5.0, "adr": 204.40, "adr_yoy":  3.5, "occ": 63.9, "occ_chg":  0.9},
        # 2025
        {"quarter": "Q1 2025", "revpar": 134.55, "revpar_yoy":  5.7, "adr": 202.83, "adr_yoy":  3.7, "occ": 66.3, "occ_chg":  1.2},
        {"quarter": "Q2 2025", "revpar": 152.75, "revpar_yoy":  1.6, "adr": 206.96, "adr_yoy":  1.1, "occ": 73.6, "occ_chg":  0.3},
        {"quarter": "Q3 2025", "revpar": 149.44, "revpar_yoy": -1.6, "adr": 207.49, "adr_yoy": -0.4, "occ": 72.0, "occ_chg": -0.9},
        {"quarter": "Q4 2025", "revpar": 135.28, "revpar_yoy":  4.0, "adr": 210.08, "adr_yoy":  2.8, "occ": 64.4, "occ_chg":  0.5},
    ],
    # ── Wyndham: U.S. comparable systemwide ───────────────────────────────
    "WH": [
        # 2024
        {"quarter": "Q1 2024", "revpar": 41.54, "revpar_yoy": -5.0, "adr": 79.90, "adr_yoy": -0.5, "occ": 52.0, "occ_chg": -4.4},
        {"quarter": "Q2 2024", "revpar": 55.54, "revpar_yoy":  0.0, "adr": 87.20, "adr_yoy": -0.5, "occ": 63.7, "occ_chg":  0.9},
        {"quarter": "Q3 2024", "revpar": 55.80, "revpar_yoy": -1.0, "adr": 87.50, "adr_yoy": -0.3, "occ": 63.8, "occ_chg": -0.5},
        {"quarter": "Q4 2024", "revpar": 46.64, "revpar_yoy":  5.0, "adr": 84.40, "adr_yoy":  2.5, "occ": 55.3, "occ_chg":  1.4},
        # 2025
        {"quarter": "Q1 2025", "revpar": 42.37, "revpar_yoy":  2.0, "adr": 80.70, "adr_yoy":  1.0, "occ": 52.5, "occ_chg":  0.5},
        {"quarter": "Q2 2025", "revpar": 53.32, "revpar_yoy": -4.0, "adr": 85.30, "adr_yoy": -2.2, "occ": 62.5, "occ_chg": -1.2},
        {"quarter": "Q3 2025", "revpar": 53.52, "revpar_yoy": -4.1, "adr": 85.10, "adr_yoy": -2.7, "occ": 62.9, "occ_chg": -0.9},
        {"quarter": "Q4 2025", "revpar": 42.91, "revpar_yoy": -8.0, "adr": 81.90, "adr_yoy": -2.5, "occ": 52.4, "occ_chg": -3.6},
    ],
    # ── Choice Hotels: U.S. domestic comparable ───────────────────────────
    "CHH": [
        # 2024
        {"quarter": "Q1 2024", "revpar": 45.24, "revpar_yoy": -5.9, "adr": 89.25, "adr_yoy": -1.0, "occ": 50.7, "occ_chg": -2.7},
        {"quarter": "Q2 2024", "revpar": 59.95, "revpar_yoy": -0.5, "adr": 99.40, "adr_yoy":  0.3, "occ": 60.3, "occ_chg": -0.5},
        {"quarter": "Q3 2024", "revpar": 59.53, "revpar_yoy": -2.5, "adr": 96.47, "adr_yoy": -0.8, "occ": 61.7, "occ_chg": -1.1},
        {"quarter": "Q4 2024", "revpar": 50.51, "revpar_yoy":  4.5, "adr": 94.32, "adr_yoy":  3.1, "occ": 53.6, "occ_chg":  0.8},
        # 2025
        {"quarter": "Q1 2025", "revpar": 46.28, "revpar_yoy":  2.3, "adr": 90.78, "adr_yoy":  1.7, "occ": 51.0, "occ_chg":  0.3},
        {"quarter": "Q2 2025", "revpar": 58.22, "revpar_yoy": -2.9, "adr": 97.65, "adr_yoy": -1.8, "occ": 59.6, "occ_chg": -0.7},
        {"quarter": "Q3 2025", "revpar": 57.64, "revpar_yoy": -3.2, "adr": 95.20, "adr_yoy": -1.3, "occ": 60.5, "occ_chg": -1.2},
        {"quarter": "Q4 2025", "revpar": 46.64, "revpar_yoy": -7.6, "adr": 90.57, "adr_yoy": -3.9, "occ": 51.5, "occ_chg": -2.0},
    ],
}

# Metric label per company (what they call it in their filings)
HOTEL_KPI_LABEL = {
    "MAR": "U.S. & Canada Comparable Systemwide",
    "HLT": "U.S. Comparable Systemwide",
    "H":   "Global Comparable Systemwide",
    "WH":  "U.S. Comparable Systemwide",
    "CHH": "U.S. Domestic Comparable",
}

# Chain scale positioning (for segment analysis)
HOTEL_CHAIN_SCALE = {
    "MAR": "Luxury / Upper Upscale",
    "HLT": "Upper Upscale / Upscale",
    "H":   "Luxury / Upper Upscale",
    "WH":  "Midscale / Economy",
    "CHH": "Midscale / Economy",
}
