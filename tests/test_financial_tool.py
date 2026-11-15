from crew.financial_parser import financial_analysis_tool


def test_financial_analysis_tool():
    """Verify that the CrewAI financial tool processes the CSV."""

    result = financial_analysis_tool.run(
        file_path="data/sample_financial_data.csv"
    )

    assert result
    assert "success" in result.lower()
    assert "Revenue" in result
    assert "Profit" in result
    assert "Market_Share" in result


def test_financial_analysis_tool_resolves_csv_from_any_working_directory(tmp_path, monkeypatch):
    """The tool should resolve a CSV basename from the project data directory."""
    monkeypatch.chdir(tmp_path)

    result = financial_analysis_tool.run(file_path="sample_financial_data.csv")

    assert "success" in result.lower()
    assert "660.0" in result
    assert "124.0" in result
    assert "17.0" in result


def test_financial_analysis_tool_reports_missing_csv_without_fabricating_data(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = financial_analysis_tool.run(file_path="missing_financial_data.csv")

    assert "Financial analysis failed:" in result
    assert "missing_financial_data.csv" in result
    assert "success" not in result.lower()
