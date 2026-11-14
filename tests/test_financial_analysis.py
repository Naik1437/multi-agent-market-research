import pandas as pd
import pytest

from crew.financial_parser import analyze_financial_data


def test_financial_calculations(tmp_path):
    data = {
        "Company": ["A", "B", "C"],
        "Revenue": [100, 200, 300],
        "Profit": [20, 40, 60],
        "Market_Share": [10, 20, 30]
    }

    csv_file = tmp_path / "mock_data.csv"
    pd.DataFrame(data).to_csv(csv_file, index=False)

    result = analyze_financial_data(str(csv_file))

    assert result["status"] == "success"
    assert result["total_companies"] == 3

    assert result["statistics"]["Revenue"]["mean"] == pytest.approx(200)
    assert result["statistics"]["Profit"]["mean"] == pytest.approx(40)
    assert result["statistics"]["Market_Share"]["mean"] == pytest.approx(20)

    assert result["statistics"]["Revenue"]["minimum"] == 100
    assert result["statistics"]["Revenue"]["maximum"] == 300


def test_missing_column(tmp_path):
    data = {
        "Company": ["A", "B"],
        "Revenue": [100, 200]
    }

    csv_file = tmp_path / "invalid_data.csv"
    pd.DataFrame(data).to_csv(csv_file, index=False)

    result = analyze_financial_data(str(csv_file))

    assert result["status"] == "error"
    assert "Missing required column" in result["message"]