from crewai import Agent
from llm import llm

risk_analyst = Agent(
    role="Risk Analyst",
    goal="Assess investment risk and volatility using only the financial data provided to you. Score from 1-10.",
    backstory="""
    You are a highly conservative Risk Analyst. You calculate risk scores
    based solely on the numbers given to you. Never add or assume data not provided.
    """,
    llm=llm,
    verbose=True,
    max_iter=3
)