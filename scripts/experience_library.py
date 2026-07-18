from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


EMPTY_LIBRARY = {"schema_version": 1, "profile": {"name_zh": "", "name_en": "", "contact": {}}, "experiences": []}
REQUIRED_RECORD_FIELDS = {"id", "type", "verified_facts", "sources", "open_questions", "status"}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate(library: dict) -> list[str]:
    errors = []
    if library.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    records = library.get("experiences")
    if not isinstance(records, list):
        return errors + ["experiences must be a list"]
    seen = set()
    for index, record in enumerate(records):
        missing = REQUIRED_RECORD_FIELDS - set(record)
        if missing:
            errors.append(f"record {index} missing: {', '.join(sorted(missing))}")
        record_id = record.get("id")
        if record_id in seen:
            errors.append(f"duplicate id: {record_id}")
        seen.add(record_id)
        if record.get("status") not in {"draft", "needs_confirmation", "verified"}:
            errors.append(f"record {record_id} has invalid status")
        if record.get("status") == "verified" and record.get("open_questions"):
            errors.append(f"verified record {record_id} still has open questions")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage a dynamic resume experience library")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("init", "list", "validate"):
        sub = subparsers.add_parser(command)
        sub.add_argument("library", type=Path)
    upsert = subparsers.add_parser("upsert")
    upsert.add_argument("library", type=Path)
    upsert.add_argument("record", type=Path)
    args = parser.parse_args()

    if args.command == "init":
        if args.library.exists():
            print(f"Library already exists: {args.library}")
        else:
            write_json(args.library, EMPTY_LIBRARY)
            print(f"Created: {args.library}")
        return 0

    library = read_json(args.library)
    if args.command == "list":
        for record in library.get("experiences", []):
            print(f"{record.get('id')}\t{record.get('type')}\t{record.get('status')}\t{record.get('title_en') or record.get('title_zh') or ''}")
        return 0
    if args.command == "upsert":
        record = read_json(args.record)
        missing = REQUIRED_RECORD_FIELDS - set(record)
        if missing:
            raise ValueError(f"record missing: {', '.join(sorted(missing))}")
        records = library.setdefault("experiences", [])
        for index, existing in enumerate(records):
            if existing.get("id") == record["id"]:
                records[index] = record
                break
        else:
            records.append(record)
        write_json(args.library, library)
        print(f"Upserted: {record['id']}")
        return 0
    errors = validate(library)
    if errors:
        print("\n".join(f"error: {error}" for error in errors), file=sys.stderr)
        return 1
    print(f"Valid library with {len(library.get('experiences', []))} experiences")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

