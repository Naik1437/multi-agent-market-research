import math
from pathlib import Path

import pandas as pd
from crewai.tools import tool


# ==========================================
# FINANCIAL DATA ANALYSIS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = (BASE_DIR / "data").resolve()

def analyze_financial_data(file_path: str) -> dict:
    """
    Read financial CSV data and calculate summary statistics.
    """

    try:
        candidate = Path(file_path)
        if not candidate.is_absolute():
            project_candidate = BASE_DIR / candidate
            # CrewAI may call the tool with only the CSV basename, even though
            # the task names it relative to the project root as ``data/...``.
            # Resolve such paths against the data directory when no project
            # root file exists. This keeps behavior independent of process CWD.
            if project_candidate.exists():
                candidate = project_candidate
            else:
                candidate = DATA_DIR / candidate
        candidate = candidate.resolve(strict=True)
        if not candidate.is_relative_to(DATA_DIR):
            raise ValueError("CSV file must be located inside the project data directory.")

        # Read only validated files from the project data directory.
        df = pd.read_csv(candidate)

        # Check required columns
        required_columns = [
            "Company",
            "Revenue",
            "Profit",
            "Market_Share"
        ]

        for column in required_columns:
            if column not in df.columns:
                raise ValueError(
                    f"Missing required column: {column}"
                )

        # Convert financial columns into numeric values
        numeric_columns = [
            "Revenue",
            "Profit",
            "Market_Share"
        ]

        for column in numeric_columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

        if df["Company"].isna().any() or df["Company"].astype(str).str.strip().eq("").any():
            raise ValueError("Company values must be present and non-empty.")

        # Reject malformed numeric values instead of silently hiding records.
        if df[numeric_columns].isna().any().any():
            raise ValueError("Financial CSV contains missing or invalid numeric values.")
        df = df.dropna(subset=numeric_columns)

        if df.empty:
            raise ValueError("No valid financial records found.")

        if not all(math.isfinite(float(value)) for column in numeric_columns
                   for value in df[column]):
            raise ValueError("Financial values must be finite numbers.")
        if (df["Revenue"] < 0).any():
            raise ValueError("Revenue cannot be negative.")
        if ((df["Market_Share"] < 0) | (df["Market_Share"] > 100)).any():
            raise ValueError("Market_Share must be between 0 and 100.")

        # Calculate statistical metrics
        statistics = {}

        for column in numeric_columns:
            statistics[column] = {
                "mean": float(df[column].mean()),
                "minimum": float(df[column].min()),
                "maximum": float(df[column].max()),
                "standard_deviation": (
                    float(df[column].std()) if len(df) > 1 else None
                )
            }

        # Generate Markdown table
        markdown_table = df.to_markdown(index=False)

        return {
            "status": "success",
            "total_companies": len(df),
            "statistics": statistics,
            "markdown_table": markdown_table
        }

    except Exception as error:
        return {
            "status": "error",
            "message": str(error)
        }


def build_illustrative_financial_section(result: dict) -> str:
    """Build report financial content from parser output, never LLM-supplied figures."""
    if result.get("status") != "success":
        raise ValueError(result.get("message", "Financial analysis failed."))

    labels = {
        "Revenue": "Revenue",
        "Profit": "Profit",
        "Market_Share": "Market Share (%)",
    }
    lines = [
        "## 5. Financial Analysis",
        "",
        "**Illustrative sample data:** The following figures are calculated directly from `data/sample_financial_data.csv`; they are not audited company results or verified market benchmarks.",
        "",
        "### 5.1 Statistical Summary",
        "",
        "| Metric | Mean | Minimum | Maximum | Standard Deviation |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for column, label in labels.items():
        stats = result["statistics"][column]
        std_dev = "N/A (one row)" if stats["standard_deviation"] is None else f"{stats['standard_deviation']:.2f}"
        lines.append(
            f"| {label} | {stats['mean']:.2f} | {stats['minimum']:.2f} | "
            f"{stats['maximum']:.2f} | {std_dev} |"
        )

    lines.extend([
        "",
        "### 5.2 Sample Records",
        "",
        "These company rows are illustrative inputs from the supplied CSV. The market research discusses a different set of companies, so no company-level financial comparison is inferred.",
        "",
        result["markdown_table"],
        "",
    ])
    return "\n".join(lines)


# ==========================================
# CREWAI FINANCIAL ANALYSIS TOOL
# ==========================================

@tool("Financial Data Analysis Tool")
def financial_analysis_tool(file_path: str) -> str:
    """
    Analyse financial CSV data using Pandas.

    Input: Path to a financial CSV file.
    Output: Financial statistics and a Markdown table.
    """

    result = analyze_financial_data(file_path)

    if result["status"] == "error":
        return f"Financial analysis failed: {result['message']}"

    return str(result)
