from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from render_resume import parse_markdown


NUMBER_PATTERN = re.compile(r"(?<![A-Za-z])\d+(?:\.\d+)?%?")
DATE_PATTERN = re.compile(r"\b(?:19|20)\d{2}[.\-/]\d{1,2}(?:\s*[-–—]\s*(?:(?:19|20)\d{2}[.\-/]\d{1,2}|Present|至今))?", re.I)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check structural and factual alignment of English and Chinese resume Markdown")
    parser.add_argument("english", type=Path)
    parser.add_argument("chinese", type=Path)
    args = parser.parse_args()
    english = parse_markdown(args.english)
    chinese = parse_markdown(args.chinese)
    errors = []
    if len(english.sections) != len(chinese.sections):
        errors.append("section counts differ")
    for section_index, (en_section, zh_section) in enumerate(zip(english.sections, chinese.sections), start=1):
        if len(en_section.entries) != len(zh_section.entries):
            errors.append(f"section {section_index}: entry counts differ")
        for entry_index, (en_entry, zh_entry) in enumerate(zip(en_section.entries, zh_section.entries), start=1):
            if len(en_entry.bullets) != len(zh_entry.bullets):
                errors.append(f"section {section_index} entry {entry_index}: bullet counts differ")
            en_text = " ".join([*en_entry.organization, *(en_entry.role or ()), *en_entry.bullets])
            zh_text = " ".join([*zh_entry.organization, *(zh_entry.role or ()), *zh_entry.bullets])
            en_dates = set(DATE_PATTERN.findall(en_text))
            zh_dates = set(DATE_PATTERN.findall(zh_text))
            if en_dates != zh_dates:
                errors.append(f"section {section_index} entry {entry_index}: dates differ: {en_dates} vs {zh_dates}")
            en_numbers = set(NUMBER_PATTERN.findall(en_text)) - {"1", "2", "3", "4"}
            zh_numbers = set(NUMBER_PATTERN.findall(zh_text)) - {"1", "2", "3", "4"}
            if en_numbers != zh_numbers:
                errors.append(f"section {section_index} entry {entry_index}: numeric claims differ: {en_numbers} vs {zh_numbers}")
    if errors:
        print("\n".join(f"error: {error}" for error in errors), file=sys.stderr)
        return 1
    print("Bilingual structure, dates, and numeric claims are aligned")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

