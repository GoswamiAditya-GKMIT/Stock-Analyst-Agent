"""
tools/ticker_search.py

@tool wrapping yf.Search — given a company name, returns the best matching
equity ticker from Yahoo Finance.
"""

import yfinance as yf
from crewai.tools import tool


@tool("Ticker Search")
def ticker_search(company_name: str) -> str:
    """
    Search Yahoo Finance for a stock ticker given a company name or partial name.
    Returns the best matching equity ticker symbol (e.g. 'TSLA' for 'Tesla'),
    or 'NOT_FOUND' if nothing matches.

    Only returns results of type EQUITY — not futures, crypto, or indexes.
    """
    if isinstance(company_name, dict):
        company_name = company_name.get("company_name", "")

    company_name = str(company_name).strip()
    if not company_name:
        return "NOT_FOUND"

    try:
        results = yf.Search(company_name, max_results=10).quotes
        if not results:
            return "NOT_FOUND"

        for r in results:
            symbol = r.get("symbol", "").strip()
            quote_type = r.get("quoteType", "").upper()

            # Only accept equities
            if quote_type != "EQUITY":
                continue

            if symbol:
                name = r.get("longname") or r.get("shortname") or symbol
                return f"{symbol} ({name})"

        return "NOT_FOUND"

    except Exception as e:
        return f"NOT_FOUND"
