from crewai import Agent
from llm import llm
from tools.yahoo_finance import get_stock_data
from tools.stock_scorer import score_stock

financial_analyst = Agent(
    role="Financial Analyst",
    goal=(
        "Fetch live stock data using the 'Stock Data Fetcher' tool, "
        "run the 'Stock Scorer' tool to get an objective quantitative score, "
        "then produce a SWOT analysis strictly from the fetched numbers."
    ),
    backstory="""
    You are a professional Wall Street financial analyst known for accuracy.
    You have two tools:
    1. 'Stock Data Fetcher' — call this first to get live financial data.
    2. 'Stock Scorer'       — call this second to compute a deterministic quantitative score.
    Use ONLY the numbers returned by these tools. Never invent figures from memory.
    """,
    tools=[get_stock_data, score_stock],
    llm=llm,
    verbose=True,
    max_iter=5
)


