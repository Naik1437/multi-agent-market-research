from reportlab.pdfgen.canvas import Canvas

from crew.pdf_generator import clean_inline_markdown, generate_pdf


def test_markdown_source_links_show_the_actual_url():
    url = "https://example.com/market-source"

    rendered = clean_inline_markdown(f"[Market source]({url})")

    assert f'href="{url}"' in rendered
    assert url in rendered


def test_pdf_generation(tmp_path, monkeypatch):
    source = tmp_path / "query-report.md"
    output = tmp_path / "query-report.pdf"
    source.write_text("# Renewable Energy Market Outlook\n\n" + ("A test report paragraph. " * 500), encoding="utf-8")

    page_labels = []
    original_draw_right_string = Canvas.drawRightString

    def capture_page_label(canvas, x, y, text, *args, **kwargs):
        if isinstance(text, str) and text.startswith("Page "):
            page_labels.append(text)
        return original_draw_right_string(canvas, x, y, text, *args, **kwargs)

    monkeypatch.setattr(Canvas, "drawRightString", capture_page_label)
    generate_pdf(input_file=source, output_file=output, report_title="Renewable Energy Market Outlook")

    assert output.exists()
    assert output.stat().st_size > 0

    with open(output, "rb") as pdf_file:
        assert pdf_file.read(5) == b"%PDF-"

    assert len(page_labels) > 1
    assert page_labels == [f"Page {number} of {len(page_labels)}" for number in range(1, len(page_labels) + 1)]


def test_cli_uses_query_specific_markdown_and_pdf_paths():
    from main import report_paths

    markdown_path, pdf_path = report_paths("Tech Sector Q3 Analysis")
    other_markdown_path, other_pdf_path = report_paths("Renewable Energy Storage")

    assert markdown_path.name == "tech-sector-q3-analysis-9fbf91c0.md"
    assert pdf_path.name == "tech-sector-q3-analysis-9fbf91c0.pdf"
    assert pdf_path.parent == markdown_path.parent
    assert other_pdf_path.name.endswith(".pdf")
    assert other_pdf_path.stem == other_markdown_path.stem
    assert other_pdf_path != pdf_path
