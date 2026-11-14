import re
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable
)


# =====================================================
# PROJECT PATHS
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "output" / "market_research_report.md"
OUTPUT_FILE = BASE_DIR / "output" / "market_research_report.pdf"


# =====================================================
# COLORS
# =====================================================

NAVY = colors.HexColor("#163A5F")
BLUE = colors.HexColor("#2563A6")
LIGHT_BLUE = colors.HexColor("#EAF1F8")
DARK = colors.HexColor("#344054")
GREY = colors.HexColor("#D0D5DD")
WHITE = colors.white


# =====================================================
# MARKDOWN CLEANER
# =====================================================

def normalize_text(text):

    text = text.strip()

    text = text.replace("&#x20;", " ")
    text = text.replace("&nbsp;", " ")

    # Remove escaped Markdown characters.
    text = re.sub(
        r"\\([\\`*_{}\[\]()#+.!|>-])",
        r"\1",
        text
    )

    return text


def clean_inline_markdown(text):

    text = normalize_text(text)

    links = []

    def save_link(label, url):

        url = url.strip().rstrip(".,;")

        if not url.startswith(("http://", "https://")):
            return escape(label)

        token = f"LINKTOKEN{len(links)}END"

        safe_url = escape(url, {'"': "&quot;"})
        safe_label = escape(label)

        links.append(
            f'<link href="{safe_url}" color="#2563A6">'
            f'{safe_label}</link>'
        )

        return token

    # Handle malformed nested links.
    nested_pattern = re.compile(
        r"\[([^\]]+)\]\(\s*\[(https?://[^\]]+)\]"
        r"\((https?://[^)]+)\)\s*\)"
    )

    text = nested_pattern.sub(
        lambda m: save_link(m.group(1), m.group(3)),
        text
    )

    # Handle normal Markdown links.
    normal_pattern = re.compile(
        r"\[([^\]]+)\]\((https?://[^)\s]+)\)"
    )

    text = normal_pattern.sub(
        lambda m: save_link(m.group(1), m.group(2)),
        text
    )

    # Escape normal text.
    text = escape(text)

    # Restore clickable links.
    for index, link in enumerate(links):
        text = text.replace(
            f"LINKTOKEN{index}END",
            link
        )

    # Bold.
    text = re.sub(
        r"\*\*(.+?)\*\*",
        r"<b>\1</b>",
        text
    )

    # Italic.
    text = re.sub(
        r"(?<!\*)\*([^*]+)\*(?!\*)",
        r"<i>\1</i>",
        text
    )

    # Inline code.
    text = re.sub(
        r"`([^`]+)`",
        r'<font name="Courier">\1</font>',
        text
    )

    return text


# =====================================================
# PDF STYLES
# =====================================================

def create_styles():

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="ReportTitleCustom",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=25,
        alignment=TA_CENTER,
        textColor=NAVY,
        spaceAfter=10
    ))

    styles.add(ParagraphStyle(
        name="SectionCustom",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=NAVY,
        spaceBefore=12,
        spaceAfter=7,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        name="SubsectionCustom",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=BLUE,
        spaceBefore=7,
        spaceAfter=5,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        name="BodyCustom",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=14,
        textColor=DARK,
        spaceAfter=6
    ))

    styles.add(ParagraphStyle(
        name="BulletCustom",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        leftIndent=14,
        firstLineIndent=-9,
        textColor=DARK,
        spaceAfter=4
    ))

    styles.add(ParagraphStyle(
        name="TableHeaderCustom",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=NAVY
    ))

    styles.add(ParagraphStyle(
        name="TableCellCustom",
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=DARK
    ))

    return styles


# =====================================================
# PROFESSIONAL HEADER
# =====================================================

def create_header():

    title = Paragraph(
        "MARKET RESEARCH REPORT",
        ParagraphStyle(
            "BannerTitle",
            fontName="Helvetica-Bold",
            fontSize=17,
            textColor=WHITE,
            alignment=TA_CENTER
        )
    )

    subtitle = Paragraph(
        "Indian Smartphone Market Analysis | 2026",
        ParagraphStyle(
            "BannerSubtitle",
            fontName="Helvetica",
            fontSize=9,
            textColor=WHITE,
            alignment=TA_CENTER
        )
    )

    header = Table(
        [[title], [subtitle]],
        colWidths=[170 * mm]
    )

    header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10)
    ]))

    return header


# =====================================================
# PAGE FOOTER
# =====================================================

def add_page_number(canvas, document):

    canvas.saveState()

    width, _ = A4

    canvas.setStrokeColor(GREY)

    canvas.line(
        20 * mm,
        16 * mm,
        width - 20 * mm,
        16 * mm
    )

    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(DARK)

    canvas.drawString(
        20 * mm,
        10 * mm,
        "Indian Smartphone Market Research | 2026"
    )

    canvas.drawRightString(
        width - 20 * mm,
        10 * mm,
        f"Page {document.page}"
    )

    canvas.restoreState()


# =====================================================
# MARKDOWN TABLE PROCESSOR
# =====================================================

def parse_markdown_table(table_lines, styles):

    rows = []

    for line in table_lines:

        line = line.strip()

        # Remove escaped pipes.
        line = line.replace(r"\|", "PIPEPLACEHOLDER")

        cells = [
            cell.strip()
            for cell in line.strip("|").split("|")
        ]

        cells = [
            cell.replace("PIPEPLACEHOLDER", "|")
            for cell in cells
        ]

        # Skip Markdown separator row.
        if cells and all(
            re.fullmatch(
                r":?-{3,}:?",
                cell.replace(" ", "")
            )
            for cell in cells
        ):
            continue

        if cells:
            rows.append(cells)

    if not rows:
        return None

    column_count = max(len(row) for row in rows)

    for row in rows:
        while len(row) < column_count:
            row.append("")

    formatted_rows = []

    for row_index, row in enumerate(rows):

        style = (
            styles["TableHeaderCustom"]
            if row_index == 0
            else styles["TableCellCustom"]
        )

        formatted_rows.append([
            Paragraph(
                clean_inline_markdown(cell),
                style
            )
            for cell in row
        ])

    available_width = 170 * mm

    if column_count == 4:

        widths = [
            available_width * 0.30,
            available_width * 0.2333,
            available_width * 0.2333,
            available_width * 0.2334
        ]

    else:

        widths = [
            available_width / column_count
        ] * column_count

    table = Table(
        formatted_rows,
        colWidths=widths,
        repeatRows=1
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT_BLUE),
        ("GRID", (0, 0), (-1, -1), 0.5, GREY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6)
    ]))

    return table


# =====================================================
# MARKDOWN TO PDF CONVERTER
# =====================================================

def convert_markdown_to_story(markdown, styles):

    story = []

    lines = markdown.splitlines()

    index = 0

    while index < len(lines):

        original = lines[index].strip()

        if not original:
            index += 1
            continue

        # Remove wrapping bold from headings:
        # **## Executive Summary** -> ## Executive Summary
        line = normalize_text(original)

        while (
            line.startswith("**")
            and line.endswith("**")
            and len(line) > 4
        ):
            line = line[2:-2].strip()

        # Ignore horizontal separators.
        if line in ("---", r"\---", "___", "***"):
            index += 1
            continue

        # Markdown table.
        if line.startswith("|") or line.startswith(r"\|"):

            table_lines = []

            while index < len(lines):

                current = lines[index].strip()

                if not (
                    current.startswith("|")
                    or current.startswith(r"\|")
                ):
                    break

                table_lines.append(current)
                index += 1

            table = parse_markdown_table(
                table_lines,
                styles
            )

            if table:
                story.append(Spacer(1, 6))
                story.append(table)
                story.append(Spacer(1, 10))

            continue

        # Headings.
        heading_match = re.match(
            r"^(#{1,6})\s+(.*)$",
            line
        )

        if heading_match:

            level = len(heading_match.group(1))

            heading = clean_inline_markdown(
                heading_match.group(2)
            )

            if level == 1:

                story.append(Paragraph(
                    heading,
                    styles["ReportTitleCustom"]
                ))

                story.append(HRFlowable(
                    width="100%",
                    thickness=0.8,
                    color=GREY
                ))

            elif level == 2:

                story.append(Paragraph(
                    heading,
                    styles["SectionCustom"]
                ))

            else:

                story.append(Paragraph(
                    heading,
                    styles["SubsectionCustom"]
                ))

            index += 1
            continue

        # Bullet points.
        bullet_match = re.match(
            r"^[-*+]\s+(.*)$",
            line
        )

        if bullet_match:

            content = clean_inline_markdown(
                bullet_match.group(1)
            )

            story.append(Paragraph(
                f"&bull;&nbsp;&nbsp;{content}",
                styles["BulletCustom"]
            ))

            index += 1
            continue

        # Numbered lists.
        numbered_match = re.match(
            r"^(\d+[.)])\s+(.*)$",
            line
        )

        if numbered_match:

            number = escape(numbered_match.group(1))

            content = clean_inline_markdown(
                numbered_match.group(2)
            )

            story.append(Paragraph(
                f"<b>{number}</b>&nbsp;&nbsp;{content}",
                styles["BulletCustom"]
            ))

            index += 1
            continue

        # Normal paragraph.
        content = clean_inline_markdown(line)

        if content:

            story.append(Paragraph(
                content,
                styles["BodyCustom"]
            ))

        index += 1

    return story


# =====================================================
# MAIN PDF GENERATOR
# =====================================================

def generate_pdf():

    print("\nStarting PDF generation...")

    # Check input file.
    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Markdown report not found: {INPUT_FILE}"
        )

    markdown = INPUT_FILE.read_text(
        encoding="utf-8"
    )

    if not markdown.strip():

        raise ValueError(
            "Markdown report is empty."
        )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    styles = create_styles()

    document = SimpleDocTemplate(
        str(OUTPUT_FILE),
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=18 * mm,
        bottomMargin=23 * mm,
        title="Indian Smartphone Market Research Report 2026",
        author="Multi-Agent Market Research System",
        subject="Indian Smartphone Market Analysis"
    )

    story = [
        create_header(),
        Spacer(1, 12)
    ]

    story.extend(
        convert_markdown_to_story(
            markdown,
            styles
        )
    )

    if len(story) <= 2:

        raise ValueError(
            "No printable content found in the report."
        )

    # Generate PDF.
    document.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number
    )

    # Validate generated PDF.
    if not OUTPUT_FILE.exists():

        raise RuntimeError(
            "PDF file was not created."
        )

    if OUTPUT_FILE.stat().st_size == 0:

        raise RuntimeError(
            "Generated PDF is empty."
        )

    with open(OUTPUT_FILE, "rb") as pdf_file:

        if not pdf_file.read(5).startswith(b"%PDF-"):

            raise RuntimeError(
                "Invalid PDF file."
            )

    print("\n==========================================")
    print("       PDF GENERATED SUCCESSFULLY")
    print("==========================================")

    print(f"Input file : {INPUT_FILE}")
    print(f"Output file: {OUTPUT_FILE}")
    print(f"File size  : {OUTPUT_FILE.stat().st_size:,} bytes")

    print("PDF validation: PASS")

    print("==========================================")


# =====================================================
# APPLICATION ENTRY POINT
# =====================================================

if __name__ == "__main__":

    generate_pdf()