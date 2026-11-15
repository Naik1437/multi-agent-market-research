import pandas as pd
import pytest

from crew.financial_parser import analyze_financial_data, build_illustrative_financial_section


def test_financial_parser_calculations(tmp_path, monkeypatch):
    """Verify financial calculations using sample CSV data."""
    monkeypatch.setattr("crew.financial_parser.DATA_DIR", tmp_path.resolve())

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


def test_financial_parser_missing_column(tmp_path, monkeypatch):
    """Verify that missing required columns are handled."""
    monkeypatch.setattr("crew.financial_parser.DATA_DIR", tmp_path.resolve())

    csv_file = tmp_path / "invalid_data.csv"

    pd.DataFrame({
        "Company": ["A"],
        "Revenue": [100]
    }).to_csv(csv_file, index=False)

    result = analyze_financial_data(str(csv_file))

    assert result["status"] == "error"
    assert "Missing required column" in result["message"]


def test_sample_csv_statistics_and_report_section_match_source_data():
    from main import FINANCIAL_DATA_PATH

    result = analyze_financial_data(str(FINANCIAL_DATA_PATH))
    assert result["status"] == "success"
    assert result["statistics"]["Revenue"]["mean"] == 660.0
    assert result["statistics"]["Revenue"]["minimum"] == 400.0
    assert result["statistics"]["Revenue"]["maximum"] == 1000.0
    assert result["statistics"]["Revenue"]["standard_deviation"] == pytest.approx(240.8318915758459)
    assert result["statistics"]["Profit"]["mean"] == 124.0
    assert result["statistics"]["Market_Share"]["mean"] == 17.0

    section = build_illustrative_financial_section(result)
    assert "Illustrative sample data" in section
    assert "| Revenue | 660.00 | 400.00 | 1000.00 | 240.83 |" in section
    assert "| Profit | 124.00 | 80.00 | 200.00 | 50.30 |" in section
    assert "| Market Share (%) | 17.00 | 12.00 | 25.00 | 5.43 |" in section
    assert "Apple" in section and "Samsung" in section

    from main import replace_financial_section

    revised = replace_financial_section(
        "# Report\n\n## 5. Financial Analysis\n\nInvented mean 42.5.\n\n## 6. Conclusion\n\nDone.",
        result,
    )
    assert "Invented mean 42.5" not in revised
    assert "| Revenue | 660.00 | 400.00 | 1000.00 | 240.83 |" in revised
    assert "## 6. Conclusion" in revised
