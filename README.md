# AI Stock Analysis

A sophisticated multi-agent system built with **CrewAI** that performs deep financial analysis, quantitative scoring, and risk assessment for any given stock.

## About the Project
AI Stock Analysis is a CrewAI-powered system that uses specialized agents and real-time financial data to provide objective investment ratings. It eliminates AI hallucinations by using deterministic scoring tools to evaluate stock fundamentals and risk metrics.

## Key Features
- **Natural Language Parsing**: Understands conversational queries (e.g., "What do you think about Apple?") and resolves them to stock tickers.
- **Real-Time Data Fetching**: Pulls live financial statements and market data using `yfinance`.
- **Quantitative Scoring**: Computes a deterministic "Stock Score" based on fundamental metrics like profitability, growth, and leverage.
- **SWOT Analysis**: Generates a detailed Strengths, Weaknesses, Opportunities, and Threats report based strictly on fetched data.
- **Risk Assessment**: Assigns a risk score (1-10) using volatility and financial health indicators.
- **Final Recommendation**: Provides a structured Buy/Hold/Sell advice based on predefined quantitative thresholds.

##  How It Works
The system follows a sequential process involving four specialized agents:
1. **Stock Intent Parser**: Identifies the stock ticker from user input.
2. **Financial Analyst**: Fetches data and performs SWOT analysis.
3. **Risk Analyst**: Evaluates financial risks and volatility.
4. **Investment Advisor**: Aggregates all findings into a final recommendation.

##  Tech Stack
- **Framework**: [CrewAI](https://github.com/joaomadorno/crewAI)
- **Model**: `groq/llama-3.3-70b-versatile` (via LiteLLM)
- **Data Source**: Yahoo Finance (`yfinance`)
- **Language**: Python 3.13+
- **Environment Management**: `uv`

##  Setup & Usage
1. **Clone the repository.**
2. **Install dependencies**:
   ```bash
   uv sync
   ```
3. **Configure Environment**: Create a `.env` file with your `GROQ_API_KEY`.
4. **Run the analysis**-
   ```bash
   python main.py
   ```
