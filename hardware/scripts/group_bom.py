#!/usr/bin/env python3
"""Group the source BOM into purchasing lines without losing references."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
import re


def natural(reference: str) -> tuple[str, int, str]:
    match = re.fullmatch(r"([A-Za-z#]+)([0-9]+)(.*)", reference)
    if match is None:
        return reference, 0, ""
    return match.group(1), int(match.group(2)), match.group(3)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    with args.source.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    groups: dict[tuple[str, ...], list[str]] = defaultdict(list)
    fields = (
        "Value",
        "Footprint",
        "Manufacturer",
        "MPN",
        "Block",
        "DNP",
        "Description",
    )
    for row in rows:
        groups[tuple(row[field] for field in fields)].append(row["Reference"])

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(("Quantity", "References", *fields))
        for key, references in sorted(
            groups.items(),
            key=lambda item: natural(sorted(item[1], key=natural)[0]),
        ):
            ordered = sorted(references, key=natural)
            writer.writerow((len(ordered), " ".join(ordered), *key))
    print(f"Grouped {len(rows)} placements into {len(groups)} BOM lines")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
