from __future__ import annotations

import argparse
import io
import re
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, Frame, HRFlowable, Image, KeepTogether, PageTemplate, Paragraph, Spacer, Table, TableStyle
from xml.sax.saxutils import escape


@dataclass
class Entry:
    organization: tuple[str, str]
    role: tuple[str, str] | None = None
    bullets: list[str] = field(default_factory=list)


@dataclass
class Section:
    title: str
    entries: list[Entry] = field(default_factory=list)


@dataclass
class Resume:
    meta: dict[str, object]
    name: str
    sections: list[Section]


def split_columns(text: str) -> tuple[str, str]:
    left, separator, right = text.partition("||")
    return left.strip(), right.strip() if separator else ""


def parse_markdown(path: Path) -> Resume:
    text = path.read_text(encoding="utf-8-sig")
    if not text.startswith("+++"):
        raise ValueError("Markdown must start with TOML front matter delimited by +++")
    _, front_matter, body = text.split("+++", 2)
    meta = tomllib.loads(front_matter)
    name = ""
    sections: list[Section] = []
    current_entry: Entry | None = None
    current_bullet: list[str] = []

    def flush_bullet() -> None:
        nonlocal current_bullet
        if current_entry and current_bullet:
            current_entry.bullets.append(" ".join(current_bullet).strip())
        current_bullet = []

    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("# "):
            name = line[2:].strip()
        elif line.startswith("## "):
            flush_bullet()
            sections.append(Section(line[3:].strip()))
            current_entry = None
        elif line.startswith("### "):
            flush_bullet()
            if not sections:
                raise ValueError("Entry appears before a section")
            current_entry = Entry(split_columns(line[4:].strip()))
            sections[-1].entries.append(current_entry)
        elif line.startswith("#### "):
            flush_bullet()
            if not current_entry:
                raise ValueError("Role row appears before an entry")
            current_entry.role = split_columns(line[5:].strip())
        elif line.startswith("- "):
            flush_bullet()
            if not current_entry:
                raise ValueError("Bullet appears before an entry")
            current_bullet = [line[2:].strip()]
        elif current_bullet:
            current_bullet.append(line)
        else:
            raise ValueError(f"Unsupported Markdown line: {raw_line}")
    flush_bullet()
    if not name or not sections:
        raise ValueError("Resume requires a name and at least one section")
    return Resume(meta, name, sections)


def first_existing(candidates: list[str]) -> Path | None:
    for candidate in candidates:
        path = Path(candidate).expanduser()
        if path.is_file():
            return path
    return None


def configured_font(meta: dict[str, object], key: str, candidates: list[str]) -> Path | None:
    configured = str(meta.get(key, "")).strip()
    return first_existing([configured]) if configured else first_existing(candidates)


def register_fonts(meta: dict[str, object], chinese: bool) -> tuple[str, str]:
    if not chinese:
        regular = configured_font(meta, "font_regular", [
            "C:/Windows/Fonts/times.ttf",
            "/Library/Fonts/Times New Roman.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf",
        ])
        bold = configured_font(meta, "font_bold", [
            "C:/Windows/Fonts/timesbd.ttf",
            "/Library/Fonts/Times New Roman Bold.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSerif-Bold.ttf",
        ])
        if regular and bold:
            pdfmetrics.registerFont(TTFont("ResumeLatin", str(regular)))
            pdfmetrics.registerFont(TTFont("ResumeLatin-Bold", str(bold)))
            return "ResumeLatin", "ResumeLatin-Bold"
        return "Times-Roman", "Times-Bold"

    regular = configured_font(meta, "font_zh_regular", [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simsun.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Supplemental/Songti.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
    ])
    bold = configured_font(meta, "font_zh_bold", [
        "C:/Windows/Fonts/msyhbd.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Supplemental/Songti.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc",
    ])
    if not regular or not bold:
        raise RuntimeError(
            "No embeddable Chinese font was found. Install Microsoft YaHei, PingFang, or Noto CJK, "
            "or set font_zh_regular and font_zh_bold in the Markdown front matter."
        )
    pdfmetrics.registerFont(TTFont("ResumeChinese", str(regular)))
    pdfmetrics.registerFont(TTFont("ResumeChinese-Bold", str(bold)))
    return "ResumeChinese", "ResumeChinese-Bold"


LATIN_PHRASE = re.compile(
    r"(?<![A-Za-z0-9])([A-Za-z][A-Za-z0-9+./²-]*(?: [A-Za-z0-9][A-Za-z0-9+./²-]*)*)(?![A-Za-z0-9])"
)


def formatted_text(text: str, protect_latin: bool) -> str:
    safe = escape(text)
    return LATIN_PHRASE.sub(r"<nobr>\1</nobr>", safe) if protect_latin else safe


def paragraph(text: str, style: ParagraphStyle, protect_latin: bool = False) -> Paragraph:
    return Paragraph(formatted_text(text, protect_latin), style)


def build_pdf(resume: Resume, source_path: Path, scale: float) -> bytes:
    language = str(resume.meta.get("language", "en")).lower()
    chinese = language.startswith("zh")
    regular, bold = register_fonts(resume.meta, chinese)
    page_width, page_height = A4
    margin_x = float(resume.meta.get("margin_x_mm", 14 if chinese else 15)) * mm
    margin_top = float(resume.meta.get("margin_top_mm", 12 if chinese else 13)) * mm
    margin_bottom = float(resume.meta.get("margin_bottom_mm", 10)) * mm
    buffer = io.BytesIO()
    document = BaseDocTemplate(buffer, pagesize=A4, leftMargin=margin_x, rightMargin=margin_x, topMargin=margin_top, bottomMargin=margin_bottom)
    frame = Frame(margin_x, margin_bottom, page_width - 2 * margin_x, page_height - margin_top - margin_bottom, id="resume", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    document.addPageTemplates(PageTemplate(id="one-page", frames=[frame]))

    base_size = (8.45 if chinese else 8.75) * scale
    leading = base_size * (1.30 if chinese else 1.08)
    styles = {
        "name": ParagraphStyle("name", fontName=bold, fontSize=(17 if chinese else 18) * scale, leading=20 * scale, textColor=colors.HexColor("#353535") if chinese else colors.black, spaceAfter=1.2 * mm * scale),
        "contact": ParagraphStyle("contact", fontName=regular, fontSize=base_size * 0.94, leading=leading * 0.96, textColor=colors.HexColor("#555555") if chinese else colors.black, wordWrap="CJK" if chinese else None, splitLongWords=0),
        "section": ParagraphStyle("section", fontName=bold, fontSize=(10.5 if chinese else 10.8) * scale, leading=12 * scale, spaceBefore=2.0 * mm * scale, spaceAfter=0.6 * mm * scale, textColor=colors.HexColor("#333333") if chinese else colors.black),
        "entry": ParagraphStyle("entry", fontName=bold, fontSize=base_size, leading=leading, spaceAfter=0, wordWrap="CJK" if chinese else None, splitLongWords=0),
        "right": ParagraphStyle("right", fontName=bold, fontSize=base_size, leading=leading, alignment=TA_RIGHT, wordWrap="CJK" if chinese else None, splitLongWords=0),
        "bullet": ParagraphStyle("bullet", fontName=regular, fontSize=base_size, leading=leading, leftIndent=4.2 * mm, firstLineIndent=-2.8 * mm, bulletIndent=1.0 * mm, spaceBefore=0, spaceAfter=0, wordWrap="CJK" if chinese else None, splitLongWords=0),
    }

    story = []
    location = str(resume.meta.get("location", "")).strip()
    phone = str(resume.meta.get("phone", "")).strip()
    email = str(resume.meta.get("email", "")).strip()
    contact_layout = str(resume.meta.get("contact_layout", "single-line")).strip().lower()
    photo_value = str(resume.meta.get("photo", "")).strip()
    photo_path = (source_path.parent / photo_value).resolve() if photo_value else None
    header_left = [paragraph(resume.name, styles["name"], chinese)]
    if contact_layout == "two-line":
        location_label = "所在地：" if chinese else "Location: "
        phone_label = "电话：" if chinese else "Phone: "
        email_label = "邮箱：" if chinese else "Email: "
        contact_separator = "　　" if chinese else "    "
        first_line = contact_separator.join(
            value for value in (
                f"{location_label}{location}" if location else "",
                f"{phone_label}{phone}" if phone else "",
            ) if value
        )
        if first_line:
            header_left.append(paragraph(first_line, styles["contact"], chinese))
        if email:
            header_left.append(paragraph(f"{email_label}{email}", styles["contact"], chinese))
    else:
        contact = "    ".join(value for value in (location, phone, email) if value)
        if contact:
            header_left.append(paragraph(contact, styles["contact"], chinese))
    if photo_path and photo_path.exists():
        photo_width = float(resume.meta.get("photo_width_mm", 12)) * mm
        photo_height = float(resume.meta.get("photo_height_mm", 16.8)) * mm
        photo_column = float(resume.meta.get("photo_column_mm", 15)) * mm
        header = Table([[header_left, Image(str(photo_path), width=photo_width, height=photo_height)]], colWidths=[page_width - 2 * margin_x - photo_column, photo_column])
        header.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("ALIGN", (1, 0), (1, 0), "RIGHT"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
        story.append(header)
        header_gap = float(resume.meta.get("header_gap_mm", 0.4)) * mm
        if header_gap:
            story.append(Spacer(1, header_gap))
    else:
        story.extend(header_left)
        story.append(HRFlowable(width="100%", thickness=0.75, color=colors.black, spaceBefore=0.3 * mm, spaceAfter=0.7 * mm))

    for section in resume.sections:
        story.append(paragraph(section.title, styles["section"]))
        story.append(HRFlowable(width="100%", thickness=0.35, color=colors.HexColor("#777777") if chinese else colors.black, dash=(3, 2) if chinese else None, spaceBefore=0, spaceAfter=0.7 * mm * scale))
        for entry in section.entries:
            rows = [[paragraph(entry.organization[0], styles["entry"]), paragraph(entry.organization[1], styles["right"])]]
            if entry.role:
                rows.append([paragraph(entry.role[0], styles["entry"]), paragraph(entry.role[1], styles["right"])])
            table = Table(rows, colWidths=[page_width - 2 * margin_x - 42 * mm, 42 * mm], hAlign="LEFT")
            table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
            block = [table]
            for bullet in entry.bullets:
                block.append(Paragraph("&#8226; " + formatted_text(bullet, chinese), styles["bullet"]))
            block.append(Spacer(1, 0.45 * mm * scale))
            story.append(KeepTogether(block))
    document.build(story)
    return buffer.getvalue()


def render(source: Path, output: Path) -> float:
    resume = parse_markdown(source)
    max_scale = float(resume.meta.get("max_scale", 1.25))
    candidates = [round(max_scale - step * 0.025, 3) for step in range(18)]
    candidates = [scale for scale in candidates if scale >= 0.85]
    for scale in candidates:
        pdf_data = build_pdf(resume, source, scale)
        if len(PdfReader(io.BytesIO(pdf_data)).pages) == 1:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(pdf_data)
            return scale
    raise RuntimeError("Content does not fit one readable A4 page. Shorten or prioritize the Markdown content.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a structured Markdown resume to a one-page A4 PDF")
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        scale = render(args.source.resolve(), args.output.resolve())
    except Exception as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"Created one-page PDF: {args.output} (layout scale {scale:.2f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
