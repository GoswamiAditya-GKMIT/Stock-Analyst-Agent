from crewai import LLM
import os
from dotenv import load_dotenv

load_dotenv()

import litellm
# Properly disable proxy-related logging that triggers ImportErrors
litellm.turn_off_message_logging = True
litellm.disable_spend_logging = True
litellm._turn_off_debug_setup = True

llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.0
)