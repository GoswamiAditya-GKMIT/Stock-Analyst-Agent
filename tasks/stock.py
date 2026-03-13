from crewai import Task
from agents.intent_parser import intent_parser
from agents.financial_analyst import financial_analyst
from agents.risk_analyst import risk_analyst
from agents.investment_advisor import investment_advisor


def create_tasks(prompt: str):

    # ── Task 1: Intent Parsing ─────────────────────────────────────────────────
    parse_intent = Task(
        description=(
            f"The user said: \"{prompt.strip()}\"\n\n"
            f"Your job:\n"
            f"1. Determine if this is a stock/company/investment-related query.\n"
            f"   - If NO → respond with exactly: NOT_STOCK_RELATED\n"
            f"2. If YES → extract the company name and call the 'Ticker Search' "
            f"   tool to get the ticker symbol.\n"
            f"3. Return ONLY the ticker symbol (e.g. TSLA, AAPL, RELIANCE.NS). "
            f"   No extra text, no explanation.\n"
            f"   If the Ticker Search returns NOT_FOUND → respond with: TICKER_NOT_FOUND"
        ),
        agent=intent_parser,
        expected_output=(
            "Exactly one of:\n"
            "- A ticker symbol like TSLA or AAPL.NS\n"
            "- NOT_STOCK_RELATED\n"
            "- TICKER_NOT_FOUND"
        )
    )

    # ── Task 2: SWOT Analysis + Quant Score ────────────────────────────────────
    research_and_analysis = Task(
        description=(
            f"The previous task resolved the user's request to a stock ticker.\n\n"
            f"IMPORTANT: If the previous task returned NOT_STOCK_RELATED or "
            f"TICKER_NOT_FOUND, stop immediately and output: "
            f"'Cannot process: this is not a valid stock query.'\n\n"
            f"Otherwise:\n"
            f"STEP 1 — Call the 'Stock Data Fetcher' tool with the ticker from "
            f"the previous task to get live financial data.\n\n"
            f"STEP 2 — Call the 'Stock Scorer' tool with the same ticker to get "
            f"a deterministic quantitative score. Include the FULL score report "
            f"in your output verbatim.\n\n"
            f"STEP 3 — Produce a detailed SWOT analysis using ONLY the fetched numbers.\n\n"
            f"Key signals:\n"
            f"- net_income: Negative = losing money\n"
            f"- free_cash_flow: Negative = burning cash\n"
            f"- profit_margin_pct: Negative = unprofitable\n"
            f"- revenue_growth_yoy: Negative = shrinking\n"
            f"- price_position_in_52w_range_pct: Near 100% = near 52-wk high\n"
            f"- debt_to_equity_ratio: >100 = overleveraged\n"
            f"- beta: >1.5 = high volatility"
        ),
        agent=financial_analyst,
        context=[parse_intent],
        expected_output=(
            "1) The full Quantitative Score Report from the Stock Scorer tool.\n"
            "2) A detailed SWOT analysis based strictly on the live fetched data."
        )
    )

    # ── Task 3: Risk Analysis ─────────────────────────────────────────────────
    risk_analysis = Task(
        description=(
            "Based on the SWOT analysis and the Quantitative Score Report above, "
            "calculate a risk score from 1 to 10. Use only the data provided.\n\n"
            "If the previous task output was 'Cannot process', output the same."
        ),
        agent=risk_analyst,
        context=[research_and_analysis],
        expected_output="A risk assessment report with a clear risk score from 1 to 10."
    )

    # ── Task 4: Investment Decision ───────────────────────────────────────────
    investment_decision = Task(
        description=(
            f"Based on the full analysis above, provide a final investment recommendation.\n\n"
            f"If any previous task output was 'Cannot process' or NOT_STOCK_RELATED, "
            f"output ONLY this message:\n"
            f"\"I can't perform this action. Please ask about a specific stock.\"\n\n"
            f"Otherwise, the Quantitative Score Report is your PRIMARY anchor:\n"
            f"  • Score ≥ 60  → default to BUY\n"
            f"  • Score 40–59 → default to HOLD\n"
            f"  • Score < 40  → default to SELL\n\n"
            f"You MUST format your response EXACTLY as follows:\n\n"
            f"STOCK: {{ticker name}}\n"
            f"RECOMMENDATION: {{BUY / HOLD / SELL}}\n"
            f"QUANT SCORE: {{score}} / 100\n\n"
            f"SUMMARY\n"
            f"{{2–3 sentences explaining the core reason.}}\n\n"
            f"KEY STRENGTHS\n"
            f"• {{strength 1}}\n"
            f"• {{strength 2}}\n"
            f"• {{strength 3 if any}}\n\n"
            f"KEY RISKS\n"
            f"• {{risk 1}}\n"
            f"• {{risk 2}}\n"
            f"• {{risk 3 if any}}\n\n"
            f"RISK SCORE: {{risk score}} / 10\n"
            f"DEVIATION FROM QUANT SCORE: {{Yes / No}} — {{reason or 'None'}}"
        ),
        agent=investment_advisor,
        context=[research_and_analysis, risk_analysis],
        expected_output=(
            "Either: I can't perform this action. Please ask about a specific stock.\n"

            "Or the structured report:\n"
            "STOCK: <name>\nRECOMMENDATION: <BUY/HOLD/SELL>\nQUANT SCORE: <score>/100\n..."
        )
    )

    return [parse_intent, research_and_analysis, risk_analysis, investment_decision]
