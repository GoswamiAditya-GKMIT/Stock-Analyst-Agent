import ast
from crewai.tools import tool


# ──────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────────────────────

def _safe(data: dict, key: str):
    """Return the numeric value for key, or None if missing / NaN / Inf."""
    val = data.get(key)
    if val is None:
        return None
    try:
        f = float(val)
        if f != f or f == float("inf") or f == float("-inf"):
            return None
        return f
    except (TypeError, ValueError):
        return None


# ──────────────────────────────────────────────────────────────────────────────
# Core scoring logic — plain Python function, always callable from anywhere
# ──────────────────────────────────────────────────────────────────────────────

def calculate_stock_score(ticker: str, raw_data: str | None = None) -> str:
    """
    Pure-Python quantitative scorer. Accepts either:
      • ticker only  — fetches data internally via yahoo_finance.fetch_stock_data
      • ticker + raw_data string — uses the pre-fetched string (avoids double API call)

    Returns a formatted score report string.
    Null / missing fields are skipped gracefully.
    """
    ticker = str(ticker).strip().upper()

    # ── 1. Get raw data ────────────────────────────────────────────────────────
    if raw_data is None:
        from tools.yahoo_finance import fetch_stock_data
        raw_data = fetch_stock_data(ticker)

    if isinstance(raw_data, str) and raw_data.startswith("Error"):
        return raw_data

    try:
        data = ast.literal_eval(raw_data)
    except Exception as e:
        return f"Error: Could not parse stock data — {e}"

    # ── 2. Score each signal (−2 … +2 scale) ──────────────────────────────────
    score = 0
    max_score = 0
    breakdown: list[str] = []

    def signal(label: str, key: str, scorer_fn):
        nonlocal score, max_score
        val = _safe(data, key)
        if val is None:
            breakdown.append(f"  {label:<28} N/A  (missing — skipped)")
            return
        pts, reason = scorer_fn(val)
        max_score += 2
        score += pts
        arrow = f"+{pts}" if pts >= 0 else str(pts)
        breakdown.append(f"  {label:<28} {arrow:>3}  ({reason})")

    # Signal 1 — Net income
    def s_net_income(v):
        return (+2, f"Positive  ${v:,.0f}") if v > 0 else (-2, f"NEGATIVE  ${v:,.0f}")
    signal("net_income", "net_income", s_net_income)

    # Signal 2 — Profit margin
    def s_margin(v):
        p = v * 100
        if v > 0.15: return +2, f"Excellent  {p:.1f}%"
        if v > 0:    return +1, f"Healthy    {p:.1f}%"
        if v > -0.05: return -1, f"Slight loss  {p:.1f}%"
        return -2, f"Very negative  {p:.1f}%"
    signal("profit_margin_pct", "profit_margin_pct", s_margin)

    # Signal 3 — Free cash flow
    def s_fcf(v):
        return (+2, f"Positive  ${v:,.0f}") if v > 0 else (-2, f"Burning cash  ${v:,.0f}")
    signal("free_cash_flow", "free_cash_flow", s_fcf)

    # Signal 4 — Revenue growth YoY
    def s_rev(v):
        p = v * 100
        if v > 0.10: return +2, f"Strong    {p:.1f}%"
        if v > 0:    return +1, f"Positive  {p:.1f}%"
        if v > -0.10: return -1, f"Slightly negative  {p:.1f}%"
        return -2, f"Strongly negative  {p:.1f}%"
    signal("revenue_growth_yoy", "revenue_growth_yoy", s_rev)

    # Signal 5 — Earnings growth YoY
    def s_earn(v):
        p = v * 100
        if v > 0.10: return +2, f"Strong    {p:.1f}%"
        if v > 0:    return +1, f"Positive  {p:.1f}%"
        if v > -0.20: return -1, f"Negative  {p:.1f}%"
        return -2, f"Severely negative  {p:.1f}%"
    signal("earnings_growth_yoy", "earnings_growth_yoy", s_earn)

    # Signal 6 — Debt-to-equity
    def s_de(v):
        if v < 50:  return +2, f"Healthy    {v:.1f}"
        if v < 100: return +1, f"Moderate   {v:.1f}"
        if v < 200: return -1, f"High       {v:.1f}"
        return -2, f"Very high  {v:.1f}"
    signal("debt_to_equity_ratio", "debt_to_equity_ratio", s_de)

    # Signal 7 — Beta
    def s_beta(v):
        if v < 0.8: return +2, f"Low volatility    {v:.2f}"
        if v < 1.5: return +1, f"Moderate          {v:.2f}"
        if v < 2.5: return -1, f"High volatility   {v:.2f}"
        return -2, f"Very high vol.    {v:.2f}"
    signal("beta", "beta", s_beta)

    # Signal 8 — 52-week price position
    def s_52w(v):
        if v < 30: return +2, f"Near 52-wk low  — value zone  {v:.1f}%"
        if v < 60: return +1, f"Mid-range                      {v:.1f}%"
        if v < 85: return -1, f"Upper range — caution          {v:.1f}%"
        return -2, f"Near 52-wk high — overvalued   {v:.1f}%"
    signal("52w_range_position", "price_position_in_52w_range_pct", s_52w)

    # ── 3. Normalise → 0–100 & map to recommendation ──────────────────────────
    if max_score == 0:
        return f"Error: No valid data fields found to score for {ticker}."

    signals_evaluated = max_score // 2
    normalised = round((score + max_score) / (2 * max_score) * 100)

    if normalised >= 60:
        recommendation = "BUY"
    elif normalised >= 40:
        recommendation = "HOLD"
    else:
        recommendation = "SELL"

    report = (
        f"\n{'='*54}\n"
        f"  QUANTITATIVE SCORE REPORT — {ticker}\n"
        f"{'='*54}\n"
        f"  Signals evaluated : {signals_evaluated} / 8\n"
        f"  Raw score         : {score:+d}  (range: {-max_score} to +{max_score})\n"
        f"  Normalised score  : {normalised} / 100\n"
        f"\n  Signal Breakdown:\n"
        + "\n".join(breakdown)
        + f"\n\n  ► Quantitative Recommendation: {recommendation}\n"
        f"    (BUY ≥ 60 | HOLD 40–59 | SELL < 40)\n"
        f"{'='*54}\n"
    )
    return report


# ──────────────────────────────────────────────────────────────────────────────
# @tool wrapper — kept for agent use if the model supports function calling
# ──────────────────────────────────────────────────────────────────────────────

@tool("Stock Scorer")
def score_stock(ticker: str) -> str:
    """
    Fetch live stock data for `ticker` and return a deterministic
    quantitative score (0-100) with a BUY / HOLD / SELL recommendation.
    Scoring is pure arithmetic — no LLM opinion.
    Missing fields are skipped gracefully.
    """
    # Handle dict input from direct .run() calls
    if isinstance(ticker, dict):
        ticker = ticker.get("ticker", "")
    return calculate_stock_score(ticker)
