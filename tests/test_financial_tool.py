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