# Multi-Agent Market Research & Report Generator

An AI-assisted market research application built with Python, CrewAI, Google Gemini, Tavily, Pandas, and ReportLab. It accepts a market query and creates query-specific Markdown and PDF reports.

## Project Overview

Market research involves collecting information from multiple sources, reviewing relevant data, and presenting findings clearly. This project demonstrates a hierarchical multi-agent workflow that coordinates research, financial analysis, and report writing.

### Problem Statement

Preparing a structured market report manually can require repeated searching, source review, data calculations, and document formatting. This application automates those steps while keeping the work divided among specialist agents.

### Objectives

- Coordinate research, financial analysis, and report writing through CrewAI.
- Search the web with Tavily and retain research source URLs.
- Calculate statistics from the supplied financial CSV using Pandas.
- Generate readable Markdown and formatted A4 PDF reports.
- Record execution, task, agent, and provider telemetry.

## Key Features

- Hierarchical CrewAI workflow with a Gemini manager and three specialist agents.
- Tavily web search and scraping of up to three result pages.
- URL validation, public-address checks, pinned connections, redirect validation, HTTPS certificate checks, and bounded page downloads.
- CSV validation and Pandas mean, minimum, maximum, sample standard deviation, and Markdown table output.
- Explicit labeling of sample financial data as illustrative.
- Query-specific Markdown and PDF filenames.
- A4 PDF layout with a report header, styled sections, financial tables, footer, and Page X of Y numbering.
- Benchmark records, execution logs, task/agent routing observations, and key-free Tavily telemetry.

## Multi-Agent Architecture

CrewAI uses `Process.hierarchical`. The manager LLM coordinates the workflow and delegates tasks to the specialists. The specialist agents have delegation disabled so coordination remains with the manager.

| Component | Responsibility | Tools |
|---|---|---|
| Crew Manager | Coordinates the tasks and delegates work using the Gemini LLM. | CrewAI hierarchical manager |
| Senior Market Research Specialist | Researches the query, identifies trends, major players, opportunities, and risks, and provides source URLs. | Tavily web search, market search and page scraper, website content scraper |
| Senior Financial Data Analyst | Validates the supplied CSV and calculates financial summary statistics. | Financial Data Analysis Tool using Pandas |
| Professional Market Research Report Writer | Combines research and financial analysis into a structured Markdown report and preserves research URLs. | Gemini LLM and task context |

## Workflow

1. The CLI accepts a required market research query.
2. The hierarchical manager coordinates the research, analysis, and writing tasks.
3. The researcher uses Tavily and can scrape up to three public result pages. Search results provide URLs and page content.
4. The analyst reads `data/sample_financial_data.csv`, validates it, and calculates statistics. These values are illustrative, not audited company data.
5. The writer prepares the report. Post-processing preserves URLs from the research task if they are missing and replaces generated financial figures with the CSV calculations.
6. The application writes query-specific Markdown and PDF files.
7. Execution and benchmark records are updated; the CrewAI trace is appended to the execution log.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.11+ | Application and test runtime |
| CrewAI | Agent, task, tool, and hierarchical workflow orchestration |
| crewai-tools | Declared dependency in `requirements.txt` |
| Google Gemini | LLM provider for agents and manager |
| Tavily Search API | Web search and source discovery |
| Requests and Python `http.client` | HTTP requests and webpage retrieval |
| BeautifulSoup | HTML text extraction |
| Pandas | CSV processing and financial statistics |
| ReportLab | PDF layout and generation |
| python-dotenv | Loading local environment variables |
| pytest | Automated tests |
| tabulate | Pandas Markdown table formatting |

## Project Structure

```text
multi-agent-market-research/
├── benchmarks/
│   ├── benchmarks.json
│   └── execution.log.txt
├── config/
│   └── llm_config.py
├── crew/
│   ├── __init__.py
│   ├── agents.py
│   ├── crew.py
│   ├── financial_parser.py
│   ├── pdf_generator.py
│   ├── tasks.py
│   └── tools.py
├── data/
│   └── sample_financial_data.csv
├── monitoring/
│   ├── __init__.py
│   └── execution_tracker.py
├── output/
│   ├── <query-slug>-<query-hash>.md
│   ├── <query-slug>-<query-hash>.pdf
│   ├── tech-sector-q3-analysis-9fbf91c0.md
│   └── tech-sector-q3-analysis-9fbf91c0.pdf
├── tests/
│   ├── __init__.py
│   ├── test_agents.py
│   ├── test_benchmarks.py
│   ├── test_crew_setup.py
│   ├── test_execution_tracker.py
│   ├── test_financial_analysis.py
│   ├── test_financial_parser.py
│   ├── test_financial_tool.py
│   ├── test_llm.py
│   ├── test_pdf_generator.py
│   ├── test_report_sources.py
│   └── test_tools.py
├── .env.example
├── .gitignore
├── main.py
├── README.md
├── requirements.txt
└── test-results.txt
```

The `.env` file and `.venv/` directory are local and ignored by Git. The output directory can also contain reports from other previous runs.

## Prerequisites

- Windows with PowerShell or another supported Python environment.
- Python 3.11 or later.
- Git.
- A Google Gemini API key.
- A Tavily API key.
- Internet access for API calls and public webpage retrieval.

No database or separate local service is required.

## Installation (Windows PowerShell)

Run these commands from the directory where you want the project:

```powershell
git clone https://github.com/Naik1437/multi-agent-market-research.git
Set-Location multi-agent-market-research
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Optionally activate the environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Activation is not required; you can continue to invoke the virtual environment's Python executable directly.

## Gemini and Tavily Configuration

Configure these variables in the project-root `.env` file:

| Variable | Required | Purpose |
|---|---|---|
| `GOOGLE_API_KEY` | Yes | Authenticates Gemini through CrewAI. |
| `TAVILY_API_KEY` | Yes | Authenticates Tavily search. The application records a clear failure and stops before starting the crew if it is missing. |
| `MODEL` | No | Selects a Gemini model in CrewAI's model format. `.env.example` contains a model example; the application also has a Gemini default. |

The example values are:

```env
GOOGLE_API_KEY=your_google_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
MODEL=gemini/gemini-3.1-flash-lite
```

The API-key values above are placeholders, not credentials. Put your own keys only in `.env`. Do not hard-code or commit secrets. `.gitignore` excludes `.env` and `.venv/`.

## Run the Application

Run from the project root:

```powershell
.\.venv\Scripts\python.exe main.py --query "Tech Sector Q3 Analysis"
```

Replace the quoted text with a different industry or market query as needed. A run contacts Gemini and Tavily and may use API quota.

### Query-Specific Reports

The CLI derives a lowercase filename slug from the query and adds an 8-character SHA-256 suffix. Markdown and PDF use the same stem. For example:

```text
output/tech-sector-q3-analysis-9fbf91c0.md
output/tech-sector-q3-analysis-9fbf91c0.pdf
```

Different queries produce different paths. Re-running the exact same query replaces that query's Markdown and PDF.

## Markdown and PDF Reports

The Markdown report contains the research findings, source URLs, and financial analysis. A deterministic step inserts source URLs from the research task if the writer omitted them and replaces generated financial figures with calculations from the sample CSV.

The PDF is generated from the Markdown and uses A4 pages, a dynamic report title, styled sections, financial tables, a footer, and total page numbering.

### Tech Sector Q3 Assessment Samples

- [Historical Technology Sector Q3 2024 Markdown report](output/tech-sector-q3-analysis-9fbf91c0.md)
- [Historical Technology Sector Q3 2024 PDF report](output/tech-sector-q3-analysis-9fbf91c0.pdf)

The report identifies Q3 2024 as its historical research period and November 15, 2026 as its generation date. Its financial CSV values are illustrative.

## Financial Data

The analyst reads `data/sample_financial_data.csv`, which requires the columns `Company`, `Revenue`, `Profit`, and `Market_Share`. The parser validates the file path, required columns, numeric and finite values, non-negative revenue, and market share between 0 and 100.

Pandas calculates mean, minimum, maximum, and sample standard deviation and generates a Markdown table. The supplied values are illustrative sample data, not audited company results or verified market benchmarks. Company-level financial comparisons are not inferred when the CSV companies do not match the research findings.

## Benchmarks and Execution Logs

- `benchmarks/benchmarks.json` stores the latest execution summary and tracked agent/task metrics, including the query, run ID, artifact paths, status, and durations.
- `benchmarks/execution.log.txt` contains the CrewAI trace and provider events. The log is appended during runs.

The tracker uses CrewAI events. Tavily telemetry records provider, timestamp, success/failure status, run ID when available, result count, and error type. API keys and sensitive headers are not recorded.

## Automated Tests

Run the test suite with the project's virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --ignore=test-results.txt
```

Search and scraping tests use mocked responses; the normal suite does not make live Gemini or Tavily requests. The Gemini integration test is skipped unless `RUN_LLM_INTEGRATION=1` is explicitly set.

Most recent full suite result before this README update: **36 passed, 1 skipped, 10 warnings**. The warnings were CrewAI deprecation warnings. Re-run the command above to verify the current checkout.

## Screenshots

No screenshot files are currently included in the repository. Genuine captures of a terminal run, Markdown report, PDF, or benchmark summary can be added here later. Do not present mock output as execution evidence, and avoid showing API credentials or personal information.

## Limitations

- Research quality depends on the model output, available sources, API availability, and rate limits.
- Scraping is limited to public HTTP(S) pages, up to three search-result pages, and a bounded response size. Some sites may block retrieval or return little readable content.
- Financial analysis uses a fixed illustrative CSV schema; it is not an audited financial-data feed.
- Sample companies may differ from those in the market research, so unsupported company-level comparisons are avoided.
- The project provides a CLI and report files; it has no web dashboard or database.
- Generated claims and sources should be reviewed before business or investment use.

## Future Enhancements

- Support additional user-selected financial datasets while preserving path and schema validation.
- Add source-quality checks and stronger claim-to-source traceability.
- Expand non-LLM unit coverage for report structure and failure paths.
- Add an optional interface for query entry and report browsing.
- Compare benchmark history across runs.
