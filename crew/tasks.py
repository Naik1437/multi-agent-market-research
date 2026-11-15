from crewai import Task


research_task = Task(
    description=(
        "Delegate this task to the Market Research Specialist. "
        "Research the following market topic: {query}. "
        "Identify industry trends, major companies, competitors, "
        "market opportunities and challenges. "
        "Use Market Search and Page Scraper to search with Tavily and "
        "read the actual content of relevant result pages. "
        "Include relevant source URLs and avoid inventing facts."
    ),
    expected_output=(
        "A structured market research report containing "
        "industry overview, major players, market trends, "
        "opportunities, challenges and source URLs."
    )
)


analysis_task = Task(
    description=(
        "Delegate this task to the Financial Data Analyst. "
        "Analyse data/sample_financial_data.csv using the "
        "Financial Data Analysis Tool. Calculate revenue, "
        "profit and market-share statistics. Compare the sample "
        "metrics with the market findings from the research task where "
        "company names overlap. Clearly label the CSV values as illustrative."
    ),
    expected_output=(
        "Financial statistics containing average, minimum, "
        "maximum and standard deviation for each numeric column, "
        "a Markdown table and business insights."
    ),
    context=[research_task]
)


writing_task = Task(
    description=(
        "Delegate this task to the Professional Report Writer. "
        "Prepare a professional market research report using "
        "the market research findings and financial analysis. "
        "Include executive summary, industry overview, trends, "
        "competitor analysis, financial analysis, opportunities, "
        "risks and conclusion. Clearly distinguish illustrative "
        "financial data from verified market information."
    ),
    expected_output=(
        "A comprehensive, professionally structured market "
        "research report in Markdown format."
    ),
    context=[research_task, analysis_task]
)
