import os
from dotenv import load_dotenv
from crewai import LLM

# Load environment variables
load_dotenv()

# Read API key
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY is missing from .env")

# Configure Gemini LLM
llm = LLM(
    model=os.getenv("MODEL", "gemini/gemini-3.8-flash"),
    api_key=api_key
)

print("Gemini LLM configured successfully!")