from types import SimpleNamespace

from main import append_research_sources


def test_appends_actual_research_urls_when_writer_omits_sources():
    research_output = SimpleNamespace(
        description=(
            "Research the following market topic and include relevant source URLs."
        ),
        raw=(
            "Research summary.\n"
            "## Source URLs\n"
            "* [Example source](https://example.com/research)\n"
            "* https://example.org/market-report"
        ),
    )
    unrelated_output = SimpleNamespace(
        description="Analyze the financial dataset.",
        raw="Do not include this unrelated URL: https://example.net/not-a-source",
    )

    report = append_research_sources(
        "# Market Report\n\nReport content.",
        [research_output, unrelated_output],
    )

    assert "## Sources" in report
    assert "<https://example.com/research>" in report
    assert "<https://example.org/market-report>" in report
    assert "example.net/not-a-source" not in report


def test_preserves_existing_sources_without_duplicate_urls():
    research_output = SimpleNamespace(
        description="Research this market topic and provide source URLs.",
        raw="https://example.com/existing\nhttps://example.com/new",
    )
    report = (
        "# Market Report\n\n"
        "## Sources\n\n"
        "* [Existing source](https://example.com/existing)\n"
    )

    updated = append_research_sources(report, [research_output])

    assert updated.count("https://example.com/existing") == 1
    assert "<https://example.com/new>" in updated


def test_does_not_invent_sources_when_research_returns_no_urls():
    research_output = SimpleNamespace(
        description="Research this market topic and provide source URLs.",
        raw="The research output did not include any URLs.",
    )
    report = "# Market Report\n\nResearch summary."

    assert append_research_sources(report, [research_output]) == report
