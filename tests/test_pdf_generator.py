from crew.pdf_generator import generate_pdf, OUTPUT_FILE


def test_pdf_generation():
    # Run the existing PDF generator
    generate_pdf()

    # Verify that the PDF was created
    assert OUTPUT_FILE.exists()
    assert OUTPUT_FILE.stat().st_size > 0

    # Verify that the generated file is a valid PDF
    with open(OUTPUT_FILE, "rb") as pdf_file:
        assert pdf_file.read(5) == b"%PDF-"