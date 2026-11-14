import pandas as pd
from crewai.tools import tool


# ==========================================
# FINANCIAL DATA ANALYSIS
# ==========================================

def analyze_financial_data(file_path: str) -> dict:
    """
    Read financial CSV data and calculate summary statistics.
    """

    try:
        # Read CSV using Pandas
        df = pd.read_csv(file_path)

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

        # Remove invalid financial records
        df = df.dropna(subset=numeric_columns)

        if df.empty:
            raise ValueError("No valid financial records found.")

        # Calculate statistical metrics
        statistics = {}

        for column in numeric_columns:
            statistics[column] = {
                "mean": float(df[column].mean()),
                "minimum": float(df[column].min()),
                "maximum": float(df[column].max()),
                "standard_deviation": float(df[column].std())
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