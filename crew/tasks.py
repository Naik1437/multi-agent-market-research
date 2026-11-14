from crewai import Task


# ==========================================
# TASK 1: MARKET RESEARCH
# ==========================================

research_task = Task(
    description=(
        "Research the following market topic: {query}. "
        "Identify industry trends, major companies, competitors, "
        "market opportunities and challenges. "
        "Use web search and website scraping tools. "
        "Include relevant source URLs and avoid inventing facts."
    ),

    expected_output=(
        "A structured market research report containing "
        "industry overview, major players, market trends, "
        "opportunities, challenges and source URLs."
    )
)


# ==========================================
# TASK 2: FINANCIAL ANALYSIS
# ==========================================

analysis_task = Task(
    description=(
        "Analyse the financial dataset located at "
        "data/sample_financial_data.csv. "
        "Use the Financial Data Analysis Tool to calculate "
        "revenue, profit and market-share statistics. "
        "Explain the important findings."
    ),

    expected_output=(
        "A financial analysis containing average, minimum, "
        "maximum and standard deviation for each numeric column, "
        "along with a Markdown table and business insights."
    )
)


# ==========================================
# TASK 3: FINAL REPORT WRITING
# ==========================================

writing_task = Task(
    description=(
        "Prepare a professional market research report using "
        "the market research findings and financial analysis. "
        "Include an executive summary, industry overview, "
        "market trends, competitor analysis, financial analysis, "
        "opportunities, risks and conclusion. "
        "Clearly distinguish illustrative sample financial data "
        "from verified market information."
    ),

    expected_output=(
        "A comprehensive, professionally structured market "
        "research report in Markdown format."
    ),

    context=[research_task, analysis_task]
)