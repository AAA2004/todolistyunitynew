from pathlib import Path

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor


REPORT_PATH = Path("/Users/ahmedashraf/todolistapp/TaskFlow_Report.docx")


def set_paragraph_numbering(paragraph, num_id: int, level: int) -> None:
    p_pr = paragraph._p.get_or_add_pPr()
    for child in list(p_pr):
        if child.tag == qn("w:numPr"):
            p_pr.remove(child)

    num_pr = OxmlElement("w:numPr")

    ilvl = OxmlElement("w:ilvl")
    ilvl.set(qn("w:val"), str(level))
    num_pr.append(ilvl)

    num = OxmlElement("w:numId")
    num.set(qn("w:val"), str(num_id))
    num_pr.append(num)

    p_pr.append(num_pr)


def create_decimal_multilevel_numbering(doc: Document) -> int:
    numbering = doc.part.numbering_part.element

    abstract_ids = [
        int(node.get(qn("w:abstractNumId")))
        for node in numbering.findall(qn("w:abstractNum"))
        if node.get(qn("w:abstractNumId")) is not None
    ]
    num_ids = [
        int(node.get(qn("w:numId")))
        for node in numbering.findall(qn("w:num"))
        if node.get(qn("w:numId")) is not None
    ]

    abstract_id = max(abstract_ids, default=0) + 1
    num_id = max(num_ids, default=0) + 1

    abstract = OxmlElement("w:abstractNum")
    abstract.set(qn("w:abstractNumId"), str(abstract_id))

    nsid = OxmlElement("w:nsid")
    nsid.set(qn("w:val"), "1A2B3C4D")
    abstract.append(nsid)

    multi = OxmlElement("w:multiLevelType")
    multi.set(qn("w:val"), "multilevel")
    abstract.append(multi)

    level_defs = [
        (0, "1", "decimal", "%1.", 0, 360),
        (1, "1", "decimal", "%1.%2", 720, 360),
        (2, "1", "decimal", "%1.%2.%3", 1440, 360),
    ]

    for ilvl_value, start_value, fmt_value, text_value, left_indent, hanging in level_defs:
        lvl = OxmlElement("w:lvl")
        lvl.set(qn("w:ilvl"), str(ilvl_value))

        start = OxmlElement("w:start")
        start.set(qn("w:val"), start_value)
        lvl.append(start)

        num_fmt = OxmlElement("w:numFmt")
        num_fmt.set(qn("w:val"), fmt_value)
        lvl.append(num_fmt)

        lvl_text = OxmlElement("w:lvlText")
        lvl_text.set(qn("w:val"), text_value)
        lvl.append(lvl_text)

        lvl_jc = OxmlElement("w:lvlJc")
        lvl_jc.set(qn("w:val"), "left")
        lvl.append(lvl_jc)

        p_pr = OxmlElement("w:pPr")
        ind = OxmlElement("w:ind")
        ind.set(qn("w:left"), str(left_indent))
        ind.set(qn("w:hanging"), str(hanging))
        p_pr.append(ind)
        lvl.append(p_pr)

        if ilvl_value > 0:
            restart = OxmlElement("w:lvlRestart")
            restart.set(qn("w:val"), "1")
            lvl.append(restart)

        abstract.append(lvl)

    numbering.append(abstract)

    num = OxmlElement("w:num")
    num.set(qn("w:numId"), str(num_id))
    abstract_ref = OxmlElement("w:abstractNumId")
    abstract_ref.set(qn("w:val"), str(abstract_id))
    num.append(abstract_ref)
    numbering.append(num)

    return num_id


def main() -> None:
    doc = Document(str(REPORT_PATH))

    for section in doc.sections:
        section.top_margin = Pt(72)
        section.bottom_margin = Pt(72)
        section.left_margin = Pt(72)
        section.right_margin = Pt(72)

    styles = doc.styles

    normal = styles["Normal"]
    normal.font.name = "Times New Roman"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    normal.font.size = Pt(12)

    body = styles["Body Text"]
    body.font.name = "Times New Roman"
    body._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    body.font.size = Pt(12)

    heading1 = styles["Heading 1"]
    heading1.font.name = "Cambria"
    heading1._element.rPr.rFonts.set(qn("w:eastAsia"), "Cambria")
    heading1.font.size = Pt(20)
    heading1.font.bold = True
    heading1.font.color.rgb = RGBColor(31, 78, 121)

    heading2 = styles["Heading 2"]
    heading2.font.name = "Cambria"
    heading2._element.rPr.rFonts.set(qn("w:eastAsia"), "Cambria")
    heading2.font.size = Pt(15)
    heading2.font.bold = True
    heading2.font.color.rgb = RGBColor(47, 84, 150)

    heading3 = styles["Heading 3"]
    heading3.font.name = "Cambria"
    heading3._element.rPr.rFonts.set(qn("w:eastAsia"), "Cambria")
    heading3.font.size = Pt(12)
    heading3.font.bold = True
    heading3.font.color.rgb = RGBColor(68, 114, 196)

    num_id = create_decimal_multilevel_numbering(doc)

    first_heading1_seen = False
    first_heading3_seen = False

    for paragraph in doc.paragraphs:
        style_name = paragraph.style.name if paragraph.style else ""

        fmt = paragraph.paragraph_format
        if style_name == "Body Text":
            fmt.line_spacing = 1.5
            fmt.space_after = Pt(8)
            fmt.space_before = Pt(0)
            paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            for run in paragraph.runs:
                run.font.name = "Times New Roman"
                run._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
                run.font.size = Pt(12)

        elif style_name == "Heading 1":
            fmt.space_before = Pt(18)
            fmt.space_after = Pt(12)
            fmt.line_spacing = 1.15
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER if not first_heading1_seen else WD_ALIGN_PARAGRAPH.LEFT
            set_paragraph_numbering(paragraph, num_id, 0)
            first_heading1_seen = True
            for run in paragraph.runs:
                run.font.name = "Cambria"
                run._element.rPr.rFonts.set(qn("w:eastAsia"), "Cambria")
                run.font.size = Pt(20)
                run.font.bold = True
                run.font.color.rgb = RGBColor(31, 78, 121)

        elif style_name == "Heading 2":
            fmt.space_before = Pt(14)
            fmt.space_after = Pt(8)
            fmt.line_spacing = 1.15
            paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
            set_paragraph_numbering(paragraph, num_id, 1)
            for run in paragraph.runs:
                run.font.name = "Cambria"
                run._element.rPr.rFonts.set(qn("w:eastAsia"), "Cambria")
                run.font.size = Pt(15)
                run.font.bold = True
                run.font.color.rgb = RGBColor(47, 84, 150)

        elif style_name == "Heading 3":
            fmt.space_before = Pt(10)
            fmt.space_after = Pt(6)
            fmt.line_spacing = 1.15
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER if not first_heading3_seen else WD_ALIGN_PARAGRAPH.LEFT
            if first_heading3_seen:
                set_paragraph_numbering(paragraph, num_id, 2)
            first_heading3_seen = True
            for run in paragraph.runs:
                run.font.name = "Cambria"
                run._element.rPr.rFonts.set(qn("w:eastAsia"), "Cambria")
                run.font.size = Pt(12)
                run.font.bold = True
                run.font.color.rgb = RGBColor(68, 114, 196)

        elif paragraph.text.strip().startswith("Figure "):
            fmt.space_before = Pt(4)
            fmt.space_after = Pt(10)
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in paragraph.runs:
                run.font.name = "Times New Roman"
                run._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
                run.font.size = Pt(10)
                run.font.italic = True

    doc.save(str(REPORT_PATH))
    print(f"Formatted report saved to {REPORT_PATH}")


if __name__ == "__main__":
    main()
