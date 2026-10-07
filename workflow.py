"""Clean a CSV export while retaining ambiguous rows for review."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

FIELDS = ("record_id", "name", "category", "status", "reference", "note")
CATEGORIES = {"hardware": "Hardware", "design": "Design", "food": "Food", "data": "Data"}
STATUSES = {"active": "Active", "pending": "Pending", "inactive": "Inactive"}


def tidy(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def transform(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    cleaned: list[dict[str, str]] = []
    flags: list[dict[str, str]] = []
    seen: dict[tuple[str, str], str] = {}

    for number, row in enumerate(rows, 2):
        missing = [field for field in FIELDS if field not in row or row[field] is None]
        if missing:
            raise ValueError(f"CSV row {number} is missing values: {', '.join(missing)}")
        item = {field: tidy(row[field]) for field in FIELDS}
        if not item["record_id"]:
            raise ValueError(f"CSV row {number} has an empty record_id")

        category_key = item["category"].casefold()
        status_key = item["status"].casefold()
        if category_key in CATEGORIES:
            item["category"] = CATEGORIES[category_key]
        else:
            flags.append({"record_id": item["record_id"], "reason": "Unknown category", "detail": item["category"]})
        if status_key in STATUSES:
            item["status"] = STATUSES[status_key]
        else:
            flags.append({"record_id": item["record_id"], "reason": "Unknown status", "detail": item["status"]})

        duplicate_key = (item["name"].casefold(), item["reference"].casefold())
        if duplicate_key in seen:
            flags.append({"record_id": item["record_id"], "reason": "Possible duplicate", "detail": f"Matches {seen[duplicate_key]}"})
        else:
            seen[duplicate_key] = item["record_id"]
        cleaned.append(item)

    return cleaned, flags


def write_csv(path: Path, fields: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def run(source: Path, destination: Path) -> dict[str, object]:
    with source.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames is None or any(field not in reader.fieldnames for field in FIELDS):
            raise ValueError(f"CSV needs columns: {', '.join(FIELDS)}")
        rows = list(reader)

    cleaned, flags = transform(rows)
    destination.mkdir(parents=True, exist_ok=True)
    write_csv(destination / "cleaned.csv", FIELDS, cleaned)
    write_csv(destination / "review_flags.csv", ("record_id", "reason", "detail"), flags)
    summary: dict[str, object] = {
        "source_rows": len(rows),
        "output_rows": len(cleaned),
        "review_flags": len(flags),
        "statuses": dict(sorted(Counter(row["status"] for row in cleaned).items())),
    }
    (destination / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.source, args.destination), indent=2))

