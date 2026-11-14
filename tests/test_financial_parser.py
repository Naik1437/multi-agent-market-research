import pandas as pd

from crew.financial_parser import analyze_financial_data


def test_financial_parser_calculations(tmp_path):
    """Verify financial calculations using sample CSV data."""

    csv_file = tmp_path / "financial_data.csv"

    data = {
        "Company": ["A", "B", "C"],
        "Revenue": [100, 200, 300],
        "Profit": [10, 20, 30],
        "Market_Share": [10, 20, 30]
    }

    pd.DataFrame(data).to_csv(csv_file, index=False)

    result = analyze_financial_data(str(csv_file))

    assert result["status"] == "success"
    assert result["total_companies"] == 3
    assert result["statistics"]["Revenue"]["mean"] == 200
    assert result["statistics"]["Profit"]["mean"] == 20
    assert result["statistics"]["Market_Share"]["mean"] == 20


def test_financial_parser_missing_column(tmp_path):
    """Verify that missing required columns are handled."""

    csv_file = tmp_path / "invalid_data.csv"

    pd.DataFrame({
        "Company": ["A"],
        "Revenue": [100]
    }).to_csv(csv_file, index=False)

    result = analyze_financial_data(str(csv_file))

    assert result["status"] == "error"
    assert "Missing required column" in result["message"]