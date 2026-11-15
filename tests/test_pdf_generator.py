from reportlab.pdfgen.canvas import Canvas

from crew.pdf_generator import generate_pdf


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


def test_cli_pdf_path_matches_assessment():
    from main import PDF_PATH, report_paths

    markdown_path, pdf_path = report_paths("Market Topic")

    assert PDF_PATH.as_posix().endswith("output/market_report.pdf")
    assert markdown_path.name.startswith("market-topic-")
    assert pdf_path == PDF_PATH
