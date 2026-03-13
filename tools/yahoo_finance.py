import yfinance as yf
from crewai.tools import tool


def fetch_stock_data(ticker: str) -> str:
    """Raw function to fetch comprehensive stock data — callable directly from Python code."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1mo")
        info = stock.info

        if not info or info.get("trailingPegRatio") is None and not info.get("currentPrice") and not info.get("regularMarketPrice"):
            return f"Error: Invalid or unknown ticker '{ticker}'. Please verify the symbol."

        # Core price metrics
        current_price = info.get("currentPrice")
        week_52_high = info.get("fiftyTwoWeekHigh")
        week_52_low = info.get("fiftyTwoWeekLow")

        # Price vs 52-week range (as a percentage: 0% = at low, 100% = at high)
        price_position_in_range = None
        if week_52_high and week_52_low and week_52_high != week_52_low:
            price_position_in_range = round(
                (current_price - week_52_low) / (week_52_high - week_52_low) * 100, 1
            )

        # Valuation metrics
        pe_ratio = info.get("trailingPE")
        forward_pe = info.get("forwardPE")
        price_to_book = info.get("priceToBook")
        price_to_sales = info.get("priceToSalesTrailing12Months")

        # Profitability metrics
        revenue = info.get("totalRevenue")
        net_income = info.get("netIncomeToCommon")
        profit_margin = info.get("profitMargins")
        operating_margin = info.get("operatingMargins")
        return_on_equity = info.get("returnOnEquity")

        # Growth metrics
        revenue_growth = info.get("revenueGrowth")       # YoY revenue growth rate
        earnings_growth = info.get("earningsGrowth")     # YoY earnings growth rate

        # Cash flow & debt
        free_cash_flow = info.get("freeCashflow")
        operating_cash_flow = info.get("operatingCashflow")
        total_debt = info.get("totalDebt")
        debt_to_equity = info.get("debtToEquity")
        current_ratio = info.get("currentRatio")          # Liquidity

        # Market data
        market_cap = info.get("marketCap")
        beta = info.get("beta")                           # Volatility vs market

        data = {
            # Price info
            "current_price": current_price,
            "52_week_high": week_52_high,
            "52_week_low": week_52_low,
            "price_position_in_52w_range_pct": price_position_in_range,  # 0=at low, 100=at high
            "price_history_last_month": hist["Close"].tolist() if not hist.empty else [],

            # Valuation
            "market_cap": market_cap,
            "pe_ratio_trailing": pe_ratio,
            "pe_ratio_forward": forward_pe,
            "price_to_book": price_to_book,
            "price_to_sales": price_to_sales,

            # Profitability
            "revenue_annual": revenue,
            "net_income": net_income,                     # Negative = losing money
            "profit_margin_pct": profit_margin,           # Negative = unprofitable
            "operating_margin_pct": operating_margin,
            "return_on_equity": return_on_equity,

            # Growth
            "revenue_growth_yoy": revenue_growth,         # e.g. 0.12 = 12% growth
            "earnings_growth_yoy": earnings_growth,

            # Cash flow & debt
            "free_cash_flow": free_cash_flow,             # Negative = burning cash
            "operating_cash_flow": operating_cash_flow,
            "total_debt": total_debt,
            "debt_to_equity_ratio": debt_to_equity,
            "current_ratio": current_ratio,               # <1 means liquidity risk

            # Risk
            "beta": beta,                                 # >1 = more volatile than market
        }

        print(f"\n[DEBUG] Tool fetched data for {ticker}: {data}\n")
        return str(data)

    except Exception as e:
        return f"Error fetching data for {ticker}: {str(e)}"


@tool("Stock Data Fetcher")
def get_stock_data(ticker: str) -> str:
    """Fetch comprehensive stock data and financial metrics using yfinance."""
    return fetch_stock_data(ticker)