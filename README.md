# Multi-Agent Market Research & Report Generator

An AI-powered multi-agent market research and report generation system built using Python, CrewAI, Gemini, Pandas and ReportLab.

The system uses a hierarchical multi-agent architecture in which a Manager LLM coordinates three specialized agents: Researcher, Financial Analyst and Report Writer. It collects market information, analyzes financial datasets and generates professional market research reports in Markdown and PDF formats.

## 1. Project Overview

The Multi-Agent Market Research & Report Generator automates the process of market research and report preparation.

Instead of performing all tasks through a single AI agent, the system divides the work among specialized agents. A hierarchical Manager LLM coordinates their activities and delegates tasks.

### Key Features

- Hierarchical multi-agent orchestration using CrewAI.
- Manager LLM with dynamic task delegation.
- Market research using web search.
- Website content extraction using web scraping.
- Financial data analysis using Pandas.
- Revenue, profit and market-share calculations.
- Markdown report generation.
- Professional PDF report generation using ReportLab.
- Execution logging and benchmark tracking.
- Automated testing using Pytest.

## 2. System Architecture

The project uses a hierarchical CrewAI architecture.

### Agents

**1. Lead Researcher**
- Researches the requested market or industry.
- Identifies major companies and competitors.
- Finds market trends, opportunities and challenges.
- Uses web search and website scraping tools.

**2. Financial Data Analyst**
- Reads financial CSV datasets.
- Processes financial information using Pandas.
- Calculates average, minimum, maximum and standard deviation.
- Generates Markdown tables and financial insights.

**3. Content Writer**
- Combines research findings and financial analysis.
- Prepares structured market research reports.
- Produces professional Markdown content.

**4. Manager LLM**
- Coordinates the agents.
- Delegates tasks through hierarchical execution.
- Manages task execution and workflow coordination.

### Workflow

User Query → Manager LLM → Researcher → Financial Analyst → Content Writer → Markdown Report → PDF Report

The Manager LLM coordinates task delegation throughout the workflow.

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| CrewAI | Multi-agent orchestration |
| Gemini | Large Language Model |
| Pandas | Financial data processing |
| DDGS | Web search |
| BeautifulSoup | Website scraping |
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
│   └── execution.log
│
├── output/
│   ├── market_research_report.md
│   └── market_research_report.pdf
│
├── tests/
│
├── config/
│
├── main.py
├── requirements.txt
├── README.md
├── .env
└── .gitignore
```

## 5. Installation and Setup

### Prerequisites

- Python 3.11 or higher.
- Visual Studio Code.
- Gemini API key.

### Step 1: Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### Step 2: Navigate to the project directory

```bash
cd multi-agent-market-research
```

### Step 3: Create a virtual environment

```bash
python -m venv .venv
```

### Step 4: Activate the virtual environment

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### Step 5: Install dependencies

```bash
pip install -r requirements.txt
```

## 6. API Configuration

The project uses Gemini as its LLM provider.

Create a `.env` file in the project root directory.

Add the following configuration:

```env
GOOGLE_API_KEY=your_google_api_key
MODEL=gemini/gemini-3.1-flash-lite
```

Replace `your_google_api_key` with your own Gemini API key.

Keep the `.env` file private. Never upload API keys to GitHub.

## 7. Running the Application

Run the following command from the project root:

```bash
python main.py --query "Indian Smartphone Market Analysis 2026"
```

The system performs market research, financial analysis and report preparation through the hierarchical multi-agent workflow.

### Generated Outputs

The system generates:

```text
output/
├── market_research_report.md
└── market_research_report.pdf
```

The Markdown report contains the structured research findings.

The PDF report presents the research in a professionally formatted document with tables and page numbering.

## 8. Financial Data Analysis

The project uses Pandas to process financial information from:

```text
data/sample_financial_data.csv
```

The dataset contains:

- Company
- Revenue
- Profit
- Market Share

The system calculates:

- Mean
- Minimum
- Maximum
- Standard deviation

**Note:** The included sample financial dataset is illustrative and is not verified real-world company financial information.

## 9. Benchmark Tracking

Execution information is maintained in:

```text
benchmarks/benchmarks.json
```

The benchmark file records project execution status, model configuration, agent configuration, verified delegation information and output validation.

Execution logs are maintained separately.

## 10. Running Automated Tests

The project uses Pytest to validate financial calculations and PDF generation.

Run all project tests:

```bash
pytest -q
```

Run tests inside the dedicated test directory:

```bash
pytest -q tests/
```

## 11. Expected Results

A successful test execution should display a passing test summary.

Example:

```text
3 passed
```

The exact number of tests depends on the test files included in the project.

## 12. Security

- API credentials are stored in `.env`.
- `.env` should be excluded from Git tracking.
- Do not publish private API keys.
- Financial sample data is clearly identified as illustrative.

## 13. Future Enhancements

- Support for multiple financial datasets.
- More advanced market intelligence.
- Improved source verification.
- Interactive research dashboard.
- Enhanced execution monitoring.
- Additional automated tests.

## 14. Conclusion

The Multi-Agent Market Research & Report Generator demonstrates how multiple specialized AI agents can collaborate through hierarchical orchestration to automate market research, financial analysis and professional report generation.

The project combines CrewAI, Gemini, Pandas and ReportLab to create an extensible AI-powered research workflow.