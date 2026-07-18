from __future__ import annotations

import argparse
from pathlib import Path

import pdfplumber


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract a page-labeled evidence transcript from a resume or project PDF")
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    parts = [f"# Extracted evidence: {args.source.name}", "", "> Draft transcript only. Verify layout and claims against the source PDF.", ""]
    with pdfplumber.open(args.source) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            parts.extend([f"## Page {page_number}", "", page.extract_text(x_tolerance=2, y_tolerance=3) or "[No extractable text]", ""])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(parts), encoding="utf-8")
    print(f"Extracted {len(pdf.pages)} pages to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

