from crewai import Agent
from llm import llm

investment_advisor = Agent(
    role="Investment Advisor",
    goal="Provide investment advice based strictly on the analysis and risk reports from your colleagues.",
    backstory="""
    You are a senior investment advisor. Your reputation is built on advice grounded in reality.
    Synthesize the reports from your colleagues without adding any fabricated data.
    """,
    llm=llm,
    verbose=True,
    max_iter=3
)