# Multi-Agent Market Research & Report Generator

An AI-powered market research and report generation system built using **Python, CrewAI, Google Gemini, Pandas, and ReportLab**.

The application uses a hierarchical multi-agent architecture in which a Manager LLM coordinates three specialized AI agents: Market Researcher, Financial Data Analyst, and Content Writer.

The system automates market research, financial data analysis, and professional report generation in Markdown and PDF formats.

---

## 1. Project Overview

The Multi-Agent Market Research & Report Generator automates the process of researching a market or industry and preparing a structured research report.

Instead of relying on a single AI agent, the application separates responsibilities among specialized agents. A hierarchical Manager LLM coordinates task execution and delegation.

### Key Features

- Hierarchical multi-agent orchestration using CrewAI.
- Manager LLM for agent coordination and task delegation.
- Web search for market research.
- Website scraping and content extraction.
- Financial data processing using Pandas.
- Revenue, profit, and market-share analysis.
- Statistical calculations: mean, minimum, maximum, and standard deviation.
- Markdown report generation.
- Professional PDF generation using ReportLab.
- Execution logging and benchmark tracking.
- Automated testing using Pytest.

## 2. System Architecture

The project uses CrewAI's hierarchical process.

### AI Agents

**1. Lead Researcher – Market Research Specialist**

- Researches the requested market or industry.
- Identifies major companies and competitors.
- Finds industry trends, opportunities, and challenges.
- Uses web search and website scraping tools.

**2. Financial Data Analyst**

- Reads financial CSV datasets.
- Processes financial information using Pandas.
- Calculates statistical measurements.
- Generates Markdown tables and financial insights.

**3. Content Writer – Technical Report Writer**

- Combines market research and financial analysis.
- Prepares structured research reports.
- Produces professional Markdown content.

**4. Manager LLM**

- Coordinates the hierarchical workflow.
- Assigns and delegates tasks.
- Manages the execution of specialist tasks.

### Workflow

```text
              User Query
                  |
                  v
              Manager LLM
                  |
          Hierarchical Crew
                  |
        +---------+---------+
        |         |         |
        v         v         v
    Researcher  Analyst   Writer
        |         |         |
        v         v         v
    Market     Financial  Report
    Research   Analysis   Writing
        |         |         |
        +---------+---------+
                  |
                  v
            Markdown Report
                  |
                  v
              PDF Report
```

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| CrewAI | Multi-agent orchestration |
| Google Gemini | Large Language Model |
| Pandas | Financial data processing |
| Tavily Search API | Search result discovery and source URLs |
| BeautifulSoup | Website content extraction |
| Requests | HTTP requests |
| ReportLab | PDF generation |
| Pytest | Automated testing |
| Python-dotenv | Environment configuration |

## 4. Project Structure

```text
multi-agent-market-research/
│
├── config/
│   └── llm_config.py
│
├── crew/
│   ├── __init__.py
│   ├── agents.py
│   ├── tools.py
│   ├── financial_parser.py
│   ├── tasks.py
│   ├── crew.py
│   └── pdf_generator.py
│
├── data/
│   └── sample_financial_data.csv
│
├── benchmarks/
│   ├── benchmarks.json
│   └── execution.log.txt
│
├── monitoring/
│   ├── __init__.py
│   └── execution_tracker.py
│
├── output/
│   ├── <query-slug>-<query-hash>.md
│   └── market_report.pdf
│
├── tests/
│   ├── test_agents.py
│   ├── test_crew_setup.py
│   ├── test_financial_analysis.py
│   ├── test_financial_parser.py
│   ├── test_financial_tool.py
│   ├── test_llm.py
│   ├── test_pdf_generator.py
│   └── test_tools.py
│
├── main.py
├── requirements.txt
├── README.md
├── .env.example
└── .gitignore
```

## 5. Installation and Setup

### Prerequisites

- Python 3.11 or higher.
- Visual Studio Code or another Python IDE.
- Google Gemini API key.
- Git.

### Step 1: Clone the Repository

```bash
git clone https://github.com/Naik1437/multi-agent-market-research.git
```

### Step 2: Navigate to the Project

```bash
cd multi-agent-market-research
```

### Step 3: Create a Virtual Environment

```bash
python -m venv .venv
```

### Step 4: Activate the Virtual Environment

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

## 6. API Configuration

The application uses Google Gemini as its LLM provider.

Create a `.env` file in the project root directory.

You can copy the example configuration:

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Set the required search and model API keys:

```env
GOOGLE_API_KEY=your_google_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
MODEL=gemini/gemini-3.1-flash-lite
```

Replace the placeholder with your own API key.

**Security:** Never upload `.env` or API credentials to GitHub. The `.env` file is excluded through `.gitignore`.

## 7. Running the Application

Execute the following command from the project root:

```bash
python main.py --query "Tech Sector Q3 Analysis"
```

The application will:

1. Initialize the hierarchical CrewAI system.
2. Coordinate the specialist agents.
3. Perform market research.
4. Analyze financial data.
5. Generate a structured Markdown report.
6. Generate a professionally formatted PDF.
7. Update execution benchmarks.

### Generated Outputs

Each run uses Tavily search results and scrapes up to three public result pages. Configure `TAVILY_API_KEY` and `GOOGLE_API_KEY` in `.env`; the application stops before starting the crew if Tavily is not configured. The scraper connects directly to a validated public IP, verifies HTTPS certificates against the original hostname, revalidates redirects, and limits page downloads to 2 MB.

Each run creates a query-specific Markdown file and writes the PDF to the assessment-required path `output/market_report.pdf`. The Markdown query is converted to a lowercase filename slug and followed by an 8-character SHA-256 suffix to prevent filename collisions.

For example, running `python main.py --query "Tech Sector Q3 Analysis"` produces:

```text
output/tech-sector-q3-analysis-<query-hash>.md
output/market_report.pdf
```

Run the command from the project root so relative CrewAI log paths resolve to the project folders. Each run appends its CrewAI trace to `benchmarks/execution.log.txt` and updates `benchmarks/benchmarks.json` with the query, run ID, report paths, status, and current run metrics. The prior sample artifacts are retained; new runs use the paths shown above.

## 8. Financial Data Analysis

The application processes financial information from:

```text
data/sample_financial_data.csv
```

The sample dataset contains:

- Company
- Revenue
- Profit
- Market Share

Using Pandas, the application calculates:

- Mean
- Minimum
- Maximum
- Standard deviation

**Note:** The included financial dataset is illustrative sample data and does not represent verified real-world company financial information.

## 9. Benchmark and Execution Monitoring

Execution information is maintained in:

```text
benchmarks/benchmarks.json
```

The monitoring component records:

- Agent execution metrics.
- Task execution durations.
- Task assignment observations.
- Execution status.
- Benchmark information.

Execution logs are maintained separately in:

```text
benchmarks/execution.log.txt
```

The execution tracker uses CrewAI event listeners to collect workflow execution information.

## 10. PDF Report Generation

The project uses ReportLab to generate professional PDF reports.

The generated PDF includes:

- A4 page layout.
- Professional report header.
- Structured report sections.
- Financial statistics tables.
- Page numbering.
- Footer information.

The generated PDF is saved in the `output/` directory.

## 11. Automated Testing

The project uses Pytest to validate its components.

Run the complete test suite:

```bash
pytest -q
```

Alternatively:

```bash
pytest -q tests/
```

The normal test suite does not make live LLM requests. To run the optional Gemini integration check explicitly, set `RUN_LLM_INTEGRATION=1` before running pytest. Search and scraping tests use mocked API and page responses.

## 12. Security

- API credentials are stored in `.env`.
- `.env` is excluded from Git tracking.
- `.env.example` provides a safe configuration template.
- API keys should never be published.
- Sample financial data is identified as illustrative.

## 13. Future Enhancements

- Support for multiple financial datasets.
- Additional market research sources.
- Improved source verification.
- Interactive research dashboard.
- Enhanced execution monitoring.
- Additional automated tests.
- More advanced financial analysis.

## 14. Conclusion

The Multi-Agent Market Research & Report Generator demonstrates how specialized AI agents can collaborate through hierarchical orchestration to automate market research, financial analysis, and professional report generation.

By combining CrewAI, Google Gemini, Pandas, and ReportLab, the project provides an extensible foundation for AI-powered market intelligence and automated reporting.

---

**Developed as an AI Agent Engineering Assessment Project.**
