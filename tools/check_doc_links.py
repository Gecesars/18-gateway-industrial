#!/usr/bin/env python3
"""Check local Markdown links in the EDGE-18 repository."""

from __future__ import annotations

from pathlib import Path
import re
import sys
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"!?\[[^\]]*]\((<[^>]+>|[^)\s]+)")
REMOTE_SCHEMES = (
    "http://",
    "https://",
    "mailto:",
    "tel:",
)


def markdown_files() -> list[Path]:
    roots = (
        ROOT / "README.md",
        ROOT / "docs",
        ROOT / "firmware",
        ROOT / "mechanical",
        ROOT / "project-management",
        ROOT / "tools",
    )
    files: list[Path] = []
    for item in roots:
        if item.is_file():
            files.append(item)
        elif item.is_dir():
            files.extend(item.rglob("*.md"))
    return sorted(files)


def local_targets(document: Path) -> list[tuple[int, Path]]:
    targets: list[tuple[int, Path]] = []
    in_fence = False
    for line_number, line in enumerate(
        document.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        for match in LINK.finditer(line):
            raw = match.group(1).strip("<>")
            if raw.startswith("#") or raw.startswith(REMOTE_SCHEMES):
                continue
            without_fragment = raw.split("#", maxsplit=1)[0]
            without_query = without_fragment.split("?", maxsplit=1)[0]
            if not without_query:
                continue
            target = (document.parent / unquote(without_query)).resolve()
            targets.append((line_number, target))
    return targets


def main() -> int:
    failures: list[str] = []
    checked = 0
    for document in markdown_files():
        for line_number, target in local_targets(document):
            checked += 1
            if not target.exists():
                source = document.relative_to(ROOT)
                failures.append(f"{source}:{line_number}: missing {target}")

    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1

    print(f"Markdown local links: PASS ({checked} checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
