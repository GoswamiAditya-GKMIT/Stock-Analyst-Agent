from crewai import Crew, Process
from tasks.stock import create_tasks
from agents.intent_parser import intent_parser
from agents.financial_analyst import financial_analyst
from agents.risk_analyst import risk_analyst
from agents.investment_advisor import investment_advisor


def run_crew(prompt: str):

    tasks = create_tasks(prompt)

    crew = Crew(
        agents=[
            intent_parser,
            financial_analyst,
            risk_analyst,
            investment_advisor,
        ],
        tasks=tasks,
        process=Process.sequential,
        verbose=True
    )

    return crew.kickoff()