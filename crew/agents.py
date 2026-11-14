from crew.tools import market_web_search, website_scraper

from crewai import Agent
from crew.financial_parser import financial_analysis_tool
from config.llm_config import llm



# ==========================================
# AGENT 1: MARKET RESEARCHER
# ==========================================

researcher = Agent(

    role="Senior Market Research Specialist",

    goal=(
        "Collect accurate, relevant and recent market information "
        "about industries, companies, competitors and market trends."
    ),

    backstory=(
        "You are an experienced market research specialist with "
        "expertise in industry analysis, competitor research, "
        "market trends and business intelligence. "
        "You focus on reliable information and evidence-based research."
    ),

    llm=llm,
    tools=[
    market_web_search,
    website_scraper
],

    verbose=True,

    allow_delegation=False
)


# ==========================================
# AGENT 2: FINANCIAL DATA ANALYST
# ==========================================

# AGENT 2: FINANCIAL DATA ANALYST

analyst = Agent(
    role="Senior Financial Data Analyst",

    goal=(
        "Analyse financial datasets, calculate statistical metrics, "
        "identify trends and provide accurate data-driven insights."
    ),

    backstory=(
        "You are a professional financial data analyst experienced "
        "in Python, Pandas and statistical analysis. "
        "You transform raw financial data into meaningful insights."
    ),

    llm=llm,

    tools=[
        financial_analysis_tool
    ],

    verbose=True,
    allow_delegation=False
)


# ==========================================
# AGENT 3: CONTENT WRITER
# ==========================================

writer = Agent(

    role="Professional Market Research Report Writer",

    goal=(
        "Transform market research and financial analysis into "
        "a professional, structured and understandable report."
    ),

    backstory=(
        "You are an experienced business report writer who specialises "
        "in market research documentation, executive summaries, "
        "financial insights and professional business communication."
    ),

    llm=llm,

    verbose=True,

    allow_delegation=False
)


print("Three AI agents configured successfully!")