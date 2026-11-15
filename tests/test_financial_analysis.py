import pandas as pd
import pytest

from crew.financial_parser import analyze_financial_data


def test_financial_calculations(tmp_path, monkeypatch):
    monkeypatch.setattr("crew.financial_parser.DATA_DIR", tmp_path.resolve())
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


def test_missing_column(tmp_path, monkeypatch):
    monkeypatch.setattr("crew.financial_parser.DATA_DIR", tmp_path.resolve())
    data = {
        "Company": ["A", "B"],
        "Revenue": [100, 200]
    }

    csv_file = tmp_path / "invalid_data.csv"
    pd.DataFrame(data).to_csv(csv_file, index=False)

    result = analyze_financial_data(str(csv_file))

    assert result["status"] == "error"
    assert "Missing required column" in result["message"]


def test_rejects_file_outside_data_directory(tmp_path):
    csv_file = tmp_path / "outside.csv"
    pd.DataFrame({"Company": ["A"], "Revenue": [10], "Profit": [1],
                  "Market_Share": [10]}).to_csv(csv_file, index=False)

    result = analyze_financial_data(str(csv_file))

    assert result["status"] == "error"
    assert "inside the project data directory" in result["message"]


def test_rejects_invalid_and_out_of_range_values(tmp_path, monkeypatch):
    monkeypatch.setattr("crew.financial_parser.DATA_DIR", tmp_path.resolve())
    csv_file = tmp_path / "bad_data.csv"
    pd.DataFrame({"Company": ["A"], "Revenue": [10], "Profit": [1],
                  "Market_Share": [120]}).to_csv(csv_file, index=False)

    result = analyze_financial_data(str(csv_file))

    assert result["status"] == "error"
    assert "Market_Share" in result["message"]
