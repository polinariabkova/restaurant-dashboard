"""
Data fetching utilities with Streamlit caching.
All external API calls go through here.
"""

import os
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


# ── FRED client (lazy init) ────────────────────────────────────────────────

def _get_fred():
    """Return a fredapi.Fred instance, or None if key is missing."""
    api_key = os.getenv("FRED_API_KEY") or st.secrets.get("FRED_API_KEY", None)
    if not api_key:
        return None
    try:
        from fredapi import Fred
        return Fred(api_key=api_key)
    except ImportError:
        return None


# ── Stock / price data ─────────────────────────────────────────────────────

@st.cache_data(ttl=86400, show_spinner=False)
def get_prices(tickers: list[str], period: str = "1y") -> pd.DataFrame:
    """
    Return daily adjusted close prices for a list of tickers.
    Returns a DataFrame with dates as index, tickers as columns.
    """
    try:
        raw = yf.download(tickers, period=period, auto_adjust=True, progress=False)
        if isinstance(raw.columns, pd.MultiIndex):
            prices = raw["Close"]
        else:
            prices = raw[["Close"]]
            prices.columns = tickers
        return prices.dropna(how="all")
    except Exception as e:
        st.error(f"Error fetching prices: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=86400, show_spinner=False)
def get_ohlcv(ticker: str, period: str = "1y") -> pd.DataFrame:
    """Return OHLCV data for a single ticker."""
    try:
        df = yf.download(ticker, period=period, auto_adjust=True, progress=False)
        # yfinance >= 0.2.38 returns MultiIndex columns even for single tickers
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)
        return df
    except Exception as e:
        st.error(f"Error fetching OHLCV for {ticker}: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=86400, show_spinner=False)
def get_returns_table(tickers: list[str]) -> pd.DataFrame:
    """
    Build a returns table with periods: 1D, 1W, 1M, 3M, YTD, 1Y.
    Returns a DataFrame with tickers as index.
    """
    periods = {"1D": "5d", "1W": "1mo", "1M": "3mo", "3M": "6mo", "1Y": "2y"}
    result = {}

    # Use 2y of data to cover all periods
    prices = get_prices(tickers, period="2y")
    if prices.empty:
        return pd.DataFrame()

    today = prices.index[-1]
    ytd_start = pd.Timestamp(today.year, 1, 1)

    for ticker in tickers:
        if ticker not in prices.columns:
            continue
        s = prices[ticker].dropna()
        if s.empty:
            continue
        row = {}
        last = s.iloc[-1]

        def pct(n_days=None, from_date=None):
            if from_date is not None:
                idx = s.index.searchsorted(from_date)
                if idx >= len(s):
                    return None
                start_price = s.iloc[idx]
            else:
                if len(s) < n_days + 1:
                    return None
                start_price = s.iloc[-(n_days + 1)]
            return (last / start_price - 1) * 100

        row["1D"]  = pct(1)
        row["1W"]  = pct(5)
        row["1M"]  = pct(21)
        row["3M"]  = pct(63)
        row["YTD"] = pct(from_date=ytd_start)
        row["1Y"]  = pct(252)
        result[ticker] = row

    return pd.DataFrame(result).T


# ── Commodity futures ──────────────────────────────────────────────────────

@st.cache_data(ttl=86400, show_spinner=False)
def get_commodity_prices(futures_map: dict, period: str = "2y") -> pd.DataFrame:
    """
    Fetch commodity futures prices.
    futures_map: {display_name: yfinance_ticker}
    Returns DataFrame with display names as columns.
    """
    tickers = list(futures_map.values())
    names   = list(futures_map.keys())
    try:
        raw = yf.download(tickers, period=period, auto_adjust=True, progress=False)
        if isinstance(raw.columns, pd.MultiIndex):
            prices = raw["Close"]
        else:
            prices = raw[["Close"]]
            prices.columns = [names[0]] if len(names) == 1 else names
            return prices

        # Rename yfinance tickers to display names
        rename = {v: k for k, v in futures_map.items()}
        prices = prices.rename(columns=rename)
        return prices.dropna(how="all")
    except Exception as e:
        st.error(f"Error fetching commodity prices: {e}")
        return pd.DataFrame()


# ── FRED data ──────────────────────────────────────────────────────────────

@st.cache_data(ttl=86400, show_spinner=False)
def get_fred_series(series_id: str, start: str = "2015-01-01", silent: bool = False) -> pd.Series:
    """
    Fetch a FRED data series.
    Returns a pandas Series with DatetimeIndex, or empty Series on failure.
    Set silent=True to suppress warning messages on fetch errors.
    """
    fred = _get_fred()
    if fred is None:
        return pd.Series(dtype=float, name=series_id)
    try:
        s = fred.get_series(series_id, observation_start=start)
        s.name = series_id
        return s.dropna()
    except Exception as e:
        if not silent:
            st.warning(f"Could not fetch FRED series {series_id}: {e}")
        return pd.Series(dtype=float, name=series_id)


@st.cache_data(ttl=86400, show_spinner=False)
def get_fred_beef_chicken(start: str = "2015-01-01") -> pd.DataFrame:
    """Return FRED beef and chicken price series as a DataFrame."""
    from config import FRED_SERIES
    beef    = get_fred_series(FRED_SERIES["beef_price"], start=start)
    chicken = get_fred_series(FRED_SERIES["chicken_price"], start=start)
    df = pd.DataFrame({"Beef": beef, "Chicken": chicken})
    return df.dropna(how="all")


@st.cache_data(ttl=86400, show_spinner=False)
def get_usda_beef_chicken(lookback_years: int = 5) -> pd.DataFrame:
    """
    Fetch beef and chicken prices from USDA AMS Market News (no API key required).
    Updates weekly — significantly more current than FRED's monthly BLS retail series.

      Beef:    LM_XB459 – National Weekly Boxed Beef Cutout, Choice grade ($/cwt → $/lb)
      Chicken: NW_LS755 / PY_LS421 fallback chain; falls back to FRED if all USDA slugs fail.

    Returns DataFrame with DatetimeIndex and 'Beef' / 'Chicken' columns (both $/lb).
    """
    import requests

    end_dt    = datetime.today()
    start_dt  = end_dt - timedelta(days=lookback_years * 365)
    start_str = start_dt.strftime("%m/%d/%Y")
    end_str   = end_dt.strftime("%m/%d/%Y")
    MARS      = "https://marsapi.ams.usda.gov/services/v1.2/reports"

    def _mars_series(slug: str,
                     filter_key: str = None,
                     filter_val: str = None,
                     scale: float = 1.0) -> pd.Series:
        """Fetch one USDA AMS MARS report and return a price Series."""
        try:
            resp = requests.get(
                f"{MARS}/{slug}",
                params={"q": f"report_begin_date={start_str};report_end_date={end_str}"},
                timeout=20,
            )
            resp.raise_for_status()
            data    = resp.json()
            records = data.get("results", data) if isinstance(data, dict) else data
        except Exception:
            return pd.Series(dtype=float)

        if filter_key and filter_val:
            records = [r for r in records
                       if str(r.get(filter_key, "")).strip().lower() == filter_val.lower()]

        # Try common price field names in order of preference
        for price_field in ("weighted_average", "price", "cutout_value",
                            "avg_price", "value", "wtd_avg"):
            rows: dict = {}
            for rec in records:
                try:
                    raw_date = rec.get("report_date") or rec.get("published_date", "")
                    raw_val  = str(rec.get(price_field, "")).replace(",", "").strip()
                    val      = float(raw_val) * scale
                    if val > 0:
                        rows[pd.to_datetime(raw_date)] = val
                except (ValueError, TypeError):
                    continue
            if rows:
                return pd.Series(rows).sort_index()

        return pd.Series(dtype=float)

    # ── Beef: National Weekly Boxed Beef Cutout (Choice, $/cwt → $/lb) ───────
    beef = _mars_series("LM_XB459", filter_key="class_desc",
                        filter_val="Choice", scale=1 / 100)
    if beef.empty:
        # Retry without class filter in case field name differs
        beef = _mars_series("LM_XB459", scale=1 / 100)

    # ── Chicken: try known USDA AMS broiler/chicken weekly report slugs ───────
    chicken = pd.Series(dtype=float)
    for slug in ("NW_LS755", "PY_LS421", "PY_GR110", "PY_LS711"):
        chicken = _mars_series(slug)
        if not chicken.empty:
            break

    # ── Fallback to FRED for any series USDA couldn't supply ─────────────────
    start_iso = start_dt.strftime("%Y-%m-%d")
    if beef.empty or chicken.empty:
        try:
            fred_df = get_fred_beef_chicken(start=start_iso)
            if beef.empty and "Beef" in fred_df.columns:
                beef = fred_df["Beef"].rename("Beef")
            if chicken.empty and "Chicken" in fred_df.columns:
                chicken = fred_df["Chicken"].rename("Chicken")
        except Exception:
            pass

    beef    = beef.rename("Beef")
    chicken = chicken.rename("Chicken")
    return pd.DataFrame({"Beef": beef, "Chicken": chicken}).dropna(how="all")


# ── Fundamentals ───────────────────────────────────────────────────────────

@st.cache_data(ttl=86400, show_spinner=False)
def get_info(ticker: str) -> dict:
    """Return yfinance .info dict for a ticker."""
    try:
        return yf.Ticker(ticker).info
    except Exception:
        return {}


@st.cache_data(ttl=86400, show_spinner=False)
def get_financials(ticker: str) -> dict:
    """
    Return quarterly income statement, balance sheet, and cash flow
    as a dict of DataFrames.
    """
    try:
        t = yf.Ticker(ticker)
        return {
            "income_q":    t.quarterly_income_stmt,
            "income_a":    t.income_stmt,
            "balance_q":   t.quarterly_balance_sheet,
            "cashflow_q":  t.quarterly_cashflow,
        }
    except Exception:
        return {}


@st.cache_data(ttl=86400, show_spinner=False)
def get_valuation_table(tickers: list[str]) -> pd.DataFrame:
    """
    Build a valuation multiples table from yfinance .info.
    Columns: P/E (TTM), Forward P/E, EV/EBITDA, Market Cap, Div Yield
    """
    rows = []
    for ticker in tickers:
        info = get_info(ticker)
        mcap = info.get("marketCap", None)
        rows.append({
            "Ticker":      ticker,
            "P/E (TTM)":   info.get("trailingPE", None),
            "Fwd P/E":     info.get("forwardPE", None),
            "EV/EBITDA":   info.get("enterpriseToEbitda", None),
            "Mkt Cap ($B)": round(mcap / 1e9, 1) if mcap else None,
            "Div Yield %": round(info.get("dividendYield", 0) * 100, 2)
                           if info.get("dividendYield") else None,
        })
    return pd.DataFrame(rows).set_index("Ticker")


def fred_key_available() -> bool:
    """Check if a FRED API key is configured."""
    return bool(os.getenv("FRED_API_KEY") or st.secrets.get("FRED_API_KEY", None))


# ── Box Office data (The Numbers) ─────────────────────────────────────────

_NUMBERS_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def _parse_money(text: str) -> float | None:
    """Parse '$123,456,789' → 123456789.0"""
    text = text.strip().replace("$", "").replace(",", "")
    try:
        return float(text)
    except (ValueError, TypeError):
        return None


def _parse_int(text: str) -> int | None:
    text = text.strip().replace(",", "")
    try:
        return int(text)
    except (ValueError, TypeError):
        return None


@st.cache_data(ttl=86400, show_spinner=False)
def get_weekly_box_office() -> pd.DataFrame:
    """
    Scrape the current weekly (Fri-Thu) box office chart from The Numbers.
    Returns DataFrame: rank, new, title, distributor, gross, pct_lw, theaters,
                       theaters_chg, per_theater, total_gross
    """
    import requests
    from bs4 import BeautifulSoup

    try:
        r = requests.get(
            "https://www.the-numbers.com/weekly-box-office-chart",
            headers=_NUMBERS_HEADERS, timeout=15,
        )
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")

        # Table with class containing 'dataTable' is the main chart
        table = soup.find("table", class_="dataTable")
        if not table:
            tables = soup.find_all("table")
            table = next((t for t in tables if len(t.find_all("tr")) > 10), None)
        if not table:
            return pd.DataFrame()

        rows = []
        for tr in table.find_all("tr")[1:]:  # skip header
            cells = [td.text.strip() for td in tr.find_all("td")]
            if len(cells) < 10:
                continue
            rows.append({
                "Rank": _parse_int(cells[0]),
                "New": cells[1].strip() == "N",
                "Title": cells[2].strip().strip("\u201c\u201d\""),
                "Distributor": cells[3],
                "Gross": _parse_money(cells[4]),
                "% vs LW": cells[5].strip(),
                "Theaters": _parse_int(cells[6]),
                "Per Theater": _parse_money(cells[8]),
                "Total Gross": _parse_money(cells[9]),
            })
        return pd.DataFrame(rows)
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=86400, show_spinner=False)
def get_weekly_box_office_trend(year: int) -> pd.DataFrame:
    """
    Scrape weekly combined weekend BO totals from The Numbers /market/{year}/summary.
    Table 2 has: Weekend, No.1 Movie, Weeks in Release, No.1 BO, Combined Weekend BO.
    """
    import requests
    from bs4 import BeautifulSoup

    try:
        r = requests.get(
            f"https://www.the-numbers.com/market/{year}/summary",
            headers=_NUMBERS_HEADERS, timeout=15,
        )
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        tables = soup.find_all("table")

        # Table 2 is the weekly summary
        if len(tables) < 3:
            return pd.DataFrame()
        table = tables[2]

        rows = []
        for tr in table.find_all("tr")[1:]:
            cells = [td.text.strip() for td in tr.find_all("td")]
            if len(cells) < 6:
                continue
            try:
                wk_date = pd.to_datetime(cells[0])
            except Exception:
                continue
            rows.append({
                "weekend_date": wk_date,
                "no1_movie": cells[1],
                "no1_gross": _parse_money(cells[3]),
                "combined_gross": _parse_money(cells[4]),
            })
        df = pd.DataFrame(rows)
        if not df.empty:
            df = df.sort_values("weekend_date").reset_index(drop=True)
        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=86400, show_spinner=False)
def get_annual_box_office() -> pd.DataFrame:
    """
    Scrape annual domestic BO totals from The Numbers /market/.
    Table 0: Year, Tickets Sold, Total Box Office, Inflation Adjusted, Avg Ticket Price.
    """
    import requests
    from bs4 import BeautifulSoup

    try:
        r = requests.get(
            "https://www.the-numbers.com/market/",
            headers=_NUMBERS_HEADERS, timeout=15,
        )
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        tables = soup.find_all("table")
        if not tables:
            return pd.DataFrame()

        table = tables[0]
        rows = []
        for tr in table.find_all("tr")[1:]:
            cells = [td.text.strip() for td in tr.find_all("td")]
            if len(cells) < 5:
                continue
            rows.append({
                "Year": _parse_int(cells[0]),
                "Tickets Sold": _parse_int(cells[1]),
                "Total BO": _parse_money(cells[2]),
                "Avg Ticket Price": _parse_money(cells[4]) if len(cells) > 4 else None,
            })
        return pd.DataFrame(rows)
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=86400, show_spinner=False)
def get_release_schedule() -> pd.DataFrame:
    """
    Scrape upcoming movie release schedule from The Numbers.
    Returns: date, movie, distributor, bo_to_date
    """
    import requests
    from bs4 import BeautifulSoup

    try:
        r = requests.get(
            "https://www.the-numbers.com/movies/release-schedule",
            headers=_NUMBERS_HEADERS, timeout=15,
        )
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        table = soup.find("table")
        if not table:
            return pd.DataFrame()

        rows = []
        current_month = ""
        for tr in table.find_all("tr")[1:]:
            cells = tr.find_all("td")
            if len(cells) == 1:
                # Month header row
                current_month = cells[0].text.strip()
                continue
            if len(cells) < 4:
                continue

            date_text = cells[0].text.strip()
            if not date_text:
                continue

            movie = cells[1].text.strip()
            distributor = cells[2].text.strip()
            bo = cells[3].text.strip()

            # Parse date: "February 21" → full date using current_month's year
            try:
                full_date = f"{date_text}, {current_month.split()[-1]}" if current_month else date_text
                parsed_date = pd.to_datetime(full_date, format="mixed", dayfirst=False)
            except Exception:
                try:
                    parsed_date = pd.to_datetime(f"{current_month.split()[0]} {date_text}, {current_month.split()[-1]}")
                except Exception:
                    continue

            rows.append({
                "Date": parsed_date,
                "Movie": movie,
                "Distributor": distributor,
                "BO to Date": _parse_money(bo) if bo else None,
            })

        df = pd.DataFrame(rows)
        if not df.empty:
            df = df.sort_values("Date").reset_index(drop=True)
        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=86400, show_spinner=False)
def get_annual_distributor_share(year: int) -> pd.DataFrame:
    """
    Scrape annual studio market share from The Numbers /market/{year}/summary.
    Table 3 has: Distributor, Movies, Total Gross, Market Share.
    """
    import requests
    from bs4 import BeautifulSoup

    try:
        r = requests.get(
            f"https://www.the-numbers.com/market/{year}/summary",
            headers=_NUMBERS_HEADERS, timeout=15,
        )
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        tables = soup.find_all("table")

        # Table 3 is the studio market share table
        if len(tables) < 4:
            return pd.DataFrame()
        table = tables[3]

        rows = []
        for tr in table.find_all("tr")[1:]:
            cells = [td.text.strip() for td in tr.find_all("td")]
            if len(cells) < 4:
                continue
            distributor = cells[0].strip()
            if not distributor or distributor.lower() in ("total", ""):
                continue
            rows.append({
                "Distributor": distributor,
                "Movies": _parse_int(cells[1]),
                "Total Gross": _parse_money(cells[2]),
                "Market Share": cells[3].strip().replace("%", ""),
            })
        df = pd.DataFrame(rows)
        if not df.empty:
            df["Market Share"] = pd.to_numeric(df["Market Share"], errors="coerce")
            df["Year"] = year
        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=86400, show_spinner=False)
def get_distributor_share_multi_year(years: list[int]) -> pd.DataFrame:
    """Fetch annual distributor market share for multiple years and combine."""
    frames = []
    for yr in years:
        df = get_annual_distributor_share(yr)
        if not df.empty:
            frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


# ── Gaming company financials (stockanalysis.com) ─────────────────────────

@st.cache_data(ttl=86400, show_spinner=False)
def get_gaming_company_financials(tickers: list[str] = None) -> pd.DataFrame:
    """
    Scrape quarterly financial data from stockanalysis.com for gaming companies.
    Returns DataFrame with columns: ticker, quarter, revenue, ebitda, net_income,
    eps, ebitda_margin, profit_margin.
    """
    import requests, json, re

    if tickers is None:
        tickers = ["MGM", "LVS", "WYNN", "CZR", "DKNG", "PENN"]

    _SA_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    all_rows = []
    for ticker in tickers:
        try:
            url = f"https://stockanalysis.com/stocks/{ticker.lower()}/financials/?p=quarterly"
            resp = requests.get(url, headers=_SA_HEADERS, timeout=20)
            if resp.status_code != 200:
                continue

            # Extract JSON data from Svelte kit.start() call
            # Look for financialData in the page's embedded data
            match = re.search(
                r'"financialData"\s*:\s*(\{[^}]*"datekey"[^}]*\})',
                resp.text,
            )
            if not match:
                # Try broader pattern
                match = re.search(r'"datekey"\s*:\s*\[(.*?)\]', resp.text)
                if not match:
                    continue

                # Parse individual arrays
                def _extract_array(key):
                    m = re.search(rf'"{key}"\s*:\s*\[(.*?)\]', resp.text)
                    if m:
                        try:
                            return json.loads(f"[{m.group(1)}]")
                        except Exception:
                            return []
                    return []

                dates = _extract_array("datekey")
                revenues = _extract_array("revenue")
                ebitdas = _extract_array("ebitda")
                net_incomes = _extract_array("netinc")
                eps_vals = _extract_array("epsdil")
                ebitda_margins = _extract_array("ebitdaMargin")
                profit_margins = _extract_array("profitMargin")

                for i, date in enumerate(dates):
                    if not date:
                        continue
                    all_rows.append({
                        "Ticker": ticker,
                        "Quarter": date,
                        "Revenue": revenues[i] if i < len(revenues) else None,
                        "EBITDA": ebitdas[i] if i < len(ebitdas) else None,
                        "Net Income": net_incomes[i] if i < len(net_incomes) else None,
                        "EPS": eps_vals[i] if i < len(eps_vals) else None,
                        "EBITDA Margin": ebitda_margins[i] if i < len(ebitda_margins) else None,
                        "Profit Margin": profit_margins[i] if i < len(profit_margins) else None,
                    })
            else:
                try:
                    fin_data = json.loads(match.group(1))
                    dates = fin_data.get("datekey", [])
                    for i, date in enumerate(dates):
                        if not date:
                            continue
                        all_rows.append({
                            "Ticker": ticker,
                            "Quarter": date,
                            "Revenue": fin_data.get("revenue", [None]*20)[i] if i < len(fin_data.get("revenue", [])) else None,
                            "EBITDA": fin_data.get("ebitda", [None]*20)[i] if i < len(fin_data.get("ebitda", [])) else None,
                            "Net Income": fin_data.get("netinc", [None]*20)[i] if i < len(fin_data.get("netinc", [])) else None,
                            "EPS": fin_data.get("epsdil", [None]*20)[i] if i < len(fin_data.get("epsdil", [])) else None,
                            "EBITDA Margin": fin_data.get("ebitdaMargin", [None]*20)[i] if i < len(fin_data.get("ebitdaMargin", [])) else None,
                            "Profit Margin": fin_data.get("profitMargin", [None]*20)[i] if i < len(fin_data.get("profitMargin", [])) else None,
                        })
                except Exception:
                    continue
        except Exception:
            continue

    if not all_rows:
        return pd.DataFrame()

    df = pd.DataFrame(all_rows)
    df["Quarter"] = pd.to_datetime(df["Quarter"], errors="coerce")
    df = df.sort_values(["Ticker", "Quarter"]).reset_index(drop=True)
    return df


@st.cache_data(ttl=86400, show_spinner=False)
def get_pa_gaming_revenue() -> pd.DataFrame:
    """
    Scrape Pennsylvania Gaming Control Board revenue data.
    Tries to find and parse the revenue summary page.
    Falls back to empty DataFrame.
    """
    import requests
    from bs4 import BeautifulSoup

    _PA_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
    }

    try:
        r = requests.get(
            "https://gamingcontrolboard.pa.gov/news-and-transparency/revenue",
            headers=_PA_HEADERS, timeout=20,
        )
        if r.status_code != 200:
            return pd.DataFrame()

        soup = BeautifulSoup(r.text, "lxml")
        tables = soup.find_all("table")
        if not tables:
            # Try to find Excel download links
            links = soup.find_all("a", href=True)
            xlsx_links = [
                a["href"] for a in links
                if a["href"].endswith(".xlsx") or a["href"].endswith(".xls")
            ]
            if xlsx_links:
                # Try to download and parse the first Excel file
                for link in xlsx_links[:3]:
                    if not link.startswith("http"):
                        link = f"https://gamingcontrolboard.pa.gov{link}"
                    try:
                        xr = requests.get(link, headers=_PA_HEADERS, timeout=20)
                        if xr.status_code == 200:
                            import io
                            df = pd.read_excel(io.BytesIO(xr.content), engine="openpyxl")
                            if not df.empty and len(df.columns) > 2:
                                return df
                    except Exception:
                        continue
            return pd.DataFrame()

        # Parse HTML tables if available
        main_table = max(tables, key=lambda t: len(t.find_all("tr")))
        header_row = main_table.find("tr")
        if not header_row:
            return pd.DataFrame()
        col_names = [th.text.strip() for th in header_row.find_all(["th", "td"])]

        rows = []
        for tr in main_table.find_all("tr")[1:]:
            cells = [td.text.strip() for td in tr.find_all(["td", "th"])]
            if len(cells) >= 2:
                row = {}
                for i, name in enumerate(col_names):
                    if i < len(cells):
                        row[name] = cells[i]
                rows.append(row)

        df = pd.DataFrame(rows)
        for col in df.columns:
            if any(kw in col.lower() for kw in ("revenue", "gross", "tax", "total", "slots", "table")):
                df[col] = df[col].apply(lambda x: _parse_money(str(x)) if x else None)
        return df
    except Exception:
        return pd.DataFrame()


# ── Gaming GGR data ───────────────────────────────────────────────────────

@st.cache_data(ttl=86400, show_spinner=False)
def get_gambling_revenue_fred(start: str = "2015-01-01") -> pd.Series:
    """Fetch FRED Quarterly Gambling Industry Revenue (REV7132TAXABL144QNSA)."""
    return get_fred_series("REV7132TAXABL144QNSA", start=start)


@st.cache_data(ttl=86400, show_spinner=False)
def get_state_igaming_revenue() -> pd.DataFrame:
    """
    Scrape state-by-state iGaming/sports betting revenue from PlayUSA.
    Falls back to empty DataFrame if scraping fails.
    """
    import requests
    from bs4 import BeautifulSoup

    try:
        r = requests.get(
            "https://www.playusa.com/revenue/",
            headers=_NUMBERS_HEADERS, timeout=15,
        )
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")

        # PlayUSA has tables with state revenue data
        tables = soup.find_all("table")
        if not tables:
            return pd.DataFrame()

        # Find the largest table (main revenue table)
        main_table = max(tables, key=lambda t: len(t.find_all("tr")))

        headers_row = main_table.find("tr")
        if not headers_row:
            return pd.DataFrame()
        col_names = [th.text.strip() for th in headers_row.find_all(["th", "td"])]

        rows = []
        for tr in main_table.find_all("tr")[1:]:
            cells = [td.text.strip() for td in tr.find_all(["td", "th"])]
            if len(cells) >= 2 and cells[0]:
                row = {}
                for i, name in enumerate(col_names):
                    if i < len(cells):
                        row[name] = cells[i]
                rows.append(row)

        df = pd.DataFrame(rows)
        # Convert money columns
        for col in df.columns:
            if col.lower() != "state" and col.lower() != "launch":
                df[col] = df[col].apply(lambda x: _parse_money(str(x)) if x else None)
        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=86400, show_spinner=False)
def get_sports_betting_by_state() -> pd.DataFrame:
    """
    Scrape state-by-state sports betting handle, revenue, and hold %
    from Legal Sports Report.  Falls back to empty DataFrame.
    """
    import requests
    from bs4 import BeautifulSoup

    _HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        r = requests.get(
            "https://www.legalsportsreport.com/sports-betting/revenue/",
            headers=_HEADERS, timeout=15,
        )
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        tables = soup.find_all("table")
        if not tables:
            return pd.DataFrame()

        main_table = max(tables, key=lambda t: len(t.find_all("tr")))
        header_row = main_table.find("tr")
        if not header_row:
            return pd.DataFrame()
        col_names = [th.text.strip() for th in header_row.find_all(["th", "td"])]

        rows = []
        for tr in main_table.find_all("tr")[1:]:
            cells = [td.text.strip() for td in tr.find_all(["td", "th"])]
            if len(cells) >= 2 and cells[0]:
                row = {}
                for i, name in enumerate(col_names):
                    if i < len(cells):
                        row[name] = cells[i]
                rows.append(row)

        df = pd.DataFrame(rows)
        for col in df.columns:
            if col.lower() not in ("state", "launch", "status", "year"):
                df[col] = df[col].apply(lambda x: _parse_money(str(x)) if x else None)
        return df
    except Exception:
        return pd.DataFrame()


# ── Curated gaming KPI reference data ──────────────────────────────────

def get_gaming_kpi_reference() -> dict:
    """
    Return a curated dict of gaming KPI descriptions, organized by
    metric type.  Used for the Industry KPIs reference section.
    """
    return {
        "GGR (Gross Gaming Revenue)": {
            "definition": (
                "Total amount retained by gaming operators after paying out "
                "winnings but before deducting expenses. The top-line revenue "
                "measure for the gaming industry."
            ),
            "who_reports": "All tracked companies (MGM, LVS, WYNN, CZR, BYD, PENN, DKNG, FLUT)",
            "frequency": "Quarterly (earnings) + monthly (state commissions)",
            "segments": "Land-based casino, online casino (iGaming), sports betting",
        },
        "NGR (Net Gaming Revenue)": {
            "definition": (
                "GGR minus promotional costs, bonuses, and free bets. "
                "More meaningful profitability indicator than GGR, especially "
                "for digital operators with heavy promotional spend."
            ),
            "who_reports": "DKNG, FLUT, GAMB, ENT.L (digital-first operators)",
            "frequency": "Quarterly earnings",
            "segments": "Online sports betting, iGaming",
        },
        "Handle & Hold %": {
            "definition": (
                "Handle = total amount wagered. Hold % = revenue retained as "
                "a percentage of handle (GGR / Handle). Typical hold for sports "
                "betting: 7-10%. Higher hold indicates operator-favorable "
                "outcomes or structural advantages."
            ),
            "who_reports": "DKNG, FLUT, PENN, CZR (sports betting divisions)",
            "frequency": "Quarterly earnings + monthly (state commissions)",
            "segments": "Sports betting only",
        },
        "RevPAR (Revenue Per Available Room)": {
            "definition": (
                "ADR x Occupancy Rate. The key hotel performance metric for "
                "casino resort operators. Tracks pricing power and demand for "
                "resort rooms alongside gaming revenue."
            ),
            "who_reports": "LVS, MGM, WYNN, CZR (destination resort operators)",
            "frequency": "Quarterly earnings",
            "segments": "Destination resorts",
        },
        "Occupancy Rate & ADR": {
            "definition": (
                "Occupancy = % of available rooms sold. ADR (Average Daily Rate) = "
                "avg revenue per occupied room. Convention and event calendars "
                "strongly influence these for Las Vegas properties."
            ),
            "who_reports": "LVS, MGM, WYNN, CZR",
            "frequency": "Quarterly earnings",
            "segments": "Destination resorts",
        },
        "EBITDA Margin by Segment": {
            "definition": (
                "EBITDA as a percentage of net revenue, reported by business "
                "segment. Useful for comparing operational efficiency across "
                "Las Vegas, regional, and digital segments."
            ),
            "who_reports": "All tracked companies (varies by segment breakdown)",
            "frequency": "Quarterly earnings",
            "segments": "Las Vegas, Regional, Macau, Digital/Interactive",
        },
        "iGaming GGR by State": {
            "definition": (
                "Online casino revenue by state. Currently legal in NJ, PA, MI, "
                "CT, WV, DE, RI. NJ and PA dominate with ~$150-200M+ monthly. "
                "Key growth metric for DKNG, FLUT, MGM (BetMGM), CZR."
            ),
            "who_reports": "State gaming commissions (monthly reports)",
            "frequency": "Monthly (state-published, ~2-3 week lag)",
            "segments": "Digital/iGaming",
        },
    }


# ── Movie franchise box office data ───────────────────────────────────

@st.cache_data(ttl=86400, show_spinner=False)
def get_franchise_box_office() -> pd.DataFrame:
    """
    Scrape top movie franchises from the-numbers.com/movies/franchises.
    Returns DataFrame with franchise name, movie count, domestic BO, worldwide BO, etc.
    """
    import requests
    from bs4 import BeautifulSoup

    _HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
    }
    try:
        r = requests.get(
            "https://www.the-numbers.com/movies/franchises",
            headers=_HEADERS, timeout=20,
        )
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        tables = soup.find_all("table")
        if not tables:
            return pd.DataFrame()

        main_table = max(tables, key=lambda t: len(t.find_all("tr")))
        rows_data = []
        for tr in main_table.find_all("tr")[1:]:
            cells = tr.find_all(["td", "th"])
            if len(cells) < 4:
                continue
            # Extract franchise name and link
            link_tag = cells[0].find("a")
            name = link_tag.text.strip() if link_tag else cells[0].text.strip()
            slug = link_tag["href"].split("/")[-1] if link_tag and link_tag.get("href") else ""

            row = {"Franchise": name, "Slug": slug}
            texts = [c.text.strip() for c in cells]

            # Parse columns: Franchise, Movies, Domestic BO, Infl Adj, Worldwide BO, First, Last, Years
            if len(texts) >= 2:
                row["Movies"] = _parse_int(texts[1]) if len(texts) > 1 else None
            if len(texts) >= 3:
                row["Domestic BO"] = _parse_money(texts[2]) if len(texts) > 2 else None
            if len(texts) >= 5:
                row["Worldwide BO"] = _parse_money(texts[4]) if len(texts) > 4 else None
            if len(texts) >= 6:
                row["First Year"] = _parse_int(texts[5]) if len(texts) > 5 else None
            if len(texts) >= 7:
                row["Last Year"] = _parse_int(texts[6]) if len(texts) > 6 else None

            if name and row.get("Domestic BO"):
                rows_data.append(row)

        df = pd.DataFrame(rows_data)
        if not df.empty and "Domestic BO" in df.columns:
            df = df.sort_values("Domestic BO", ascending=False).head(50).reset_index(drop=True)
        return df
    except Exception:
        return pd.DataFrame()


# ── Containerboard price increase tracker (RSS) ──────────────────────

@st.cache_data(ttl=86400, show_spinner=False)
def get_containerboard_price_increases() -> pd.DataFrame:
    """
    Scrape RSS feeds for containerboard / corrugated price increase announcements.
    Returns DataFrame with date, headline, source.
    """
    import requests
    from bs4 import BeautifulSoup

    _FEEDS = {
        "BusinessWire": "https://feed.businesswire.com/rss/home/?rss=G1QFDERJbWJg",
        "PR Newswire": "https://www.prnewswire.com/rss/news-releases-list.rss",
        "Reuters Business": "https://feeds.reuters.com/reuters/businessNews",
    }
    _KEYWORDS = [
        "containerboard", "price increase", "linerboard",
        "corrugating medium", "corrugated", "price hike",
        "packaging price", "box price",
    ]

    rows = []
    for source, url in _FEEDS.items():
        try:
            r = requests.get(url, timeout=15,
                             headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "xml")
            items = soup.find_all("item")[:100]  # scan up to 100 items per feed
            for item in items:
                title_text = (item.title.text if item.title else "").strip()
                desc_text = (item.description.text if item.description else "").strip()
                combined = (title_text + " " + desc_text).lower()

                if any(kw in combined for kw in _KEYWORDS):
                    pub_date = item.pubDate.text.strip() if item.pubDate else ""
                    link = item.link.text.strip() if item.link else ""
                    rows.append({
                        "Date": pub_date,
                        "Headline": title_text[:200],
                        "Source": source,
                        "Link": link,
                    })
        except Exception:
            continue

    df = pd.DataFrame(rows)
    if not df.empty and "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce", utc=True)
        df = df.dropna(subset=["Date"]).sort_values("Date", ascending=False)
    return df


@st.cache_data(ttl=86400, show_spinner=False)
def get_pp_curtailment_news() -> pd.DataFrame:
    """
    Scrape RSS feeds for P&P downtime / curtailment announcements.
    Returns DataFrame with date, headline, source.
    """
    import requests
    from bs4 import BeautifulSoup

    _FEEDS = {
        "BusinessWire": "https://feed.businesswire.com/rss/home/?rss=G1QFDERJbWJg",
        "Reuters Business": "https://feeds.reuters.com/reuters/businessNews",
    }
    _KEYWORDS = [
        "downtime", "curtailment", "maintenance outage", "capacity reduction",
        "mill closure", "idled", "containerboard shutdown", "paper mill",
        "pulp mill", "capacity curtail",
    ]

    rows = []
    for source, url in _FEEDS.items():
        try:
            r = requests.get(url, timeout=15,
                             headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "xml")
            items = soup.find_all("item")[:100]
            for item in items:
                title_text = (item.title.text if item.title else "").strip()
                desc_text = (item.description.text if item.description else "").strip()
                combined = (title_text + " " + desc_text).lower()

                if any(kw in combined for kw in _KEYWORDS):
                    pub_date = item.pubDate.text.strip() if item.pubDate else ""
                    rows.append({
                        "Date": pub_date,
                        "Headline": title_text[:200],
                        "Source": source,
                    })
        except Exception:
            continue

    df = pd.DataFrame(rows)
    if not df.empty and "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce", utc=True)
        df = df.dropna(subset=["Date"]).sort_values("Date", ascending=False)
    return df


# ── Generic company quarterly financials (reusable for any industry) ──

@st.cache_data(ttl=86400, show_spinner=False)
def get_company_quarterly_financials(tickers: list) -> pd.DataFrame:
    """
    Scrape quarterly financials from stockanalysis.com for any list of tickers.
    Returns a long-format DataFrame with Ticker, Quarter, Revenue, EBITDA, EPS, etc.
    Same pattern as get_gaming_company_financials but generalized.
    """
    import requests, re, json

    _HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    all_rows = []
    for ticker in tickers:
        try:
            url = f"https://www.stockanalysis.com/stocks/{ticker.lower()}/financials/?p=quarterly"
            r = requests.get(url, headers=_HEADERS, timeout=20)
            r.raise_for_status()
            text = r.text

            # Extract JSON from Svelte kit.start()
            match = re.search(r'type="application/json"[^>]*>(.*?)</script>', text, re.DOTALL)
            if not match:
                continue
            raw_json = match.group(1)
            data = json.loads(raw_json)

            # Navigate the nested structure
            nodes = data
            if isinstance(nodes, dict):
                # Try common Svelte paths
                for path_attempt in [
                    lambda d: d.get("props", {}).get("pageProps", {}).get("data", {}),
                    lambda d: d.get("data", [{}])[0] if isinstance(d.get("data"), list) else {},
                ]:
                    try:
                        nodes = path_attempt(data)
                        if nodes:
                            break
                    except (KeyError, IndexError, TypeError):
                        continue

            # Find the financials data array
            fin_data = None
            if isinstance(nodes, dict):
                for key in ["data", "financials", "quarterlyData", "results"]:
                    if key in nodes and isinstance(nodes[key], list):
                        fin_data = nodes[key]
                        break
            if not fin_data:
                continue

            for row in fin_data[:12]:  # Last 12 quarters
                if not isinstance(row, dict):
                    continue
                date_str = row.get("date") or row.get("period") or row.get("quarter")
                if not date_str:
                    continue
                all_rows.append({
                    "Ticker": ticker.upper(),
                    "Quarter": pd.to_datetime(date_str, errors="coerce"),
                    "Revenue": row.get("revenue"),
                    "EBITDA": row.get("ebitda"),
                    "Net Income": row.get("netIncome") or row.get("netincome"),
                    "EPS": row.get("eps") or row.get("epsDiluted"),
                    "EBITDA Margin": row.get("ebitdaMargin"),
                    "Profit Margin": row.get("profitMargin") or row.get("netMargin"),
                })
        except Exception:
            continue

    df = pd.DataFrame(all_rows)
    if not df.empty:
        df = df.dropna(subset=["Quarter"]).sort_values(["Ticker", "Quarter"])
    return df
