#!/usr/bin/env python3
"""Validate the committed frozen EDGE-18 Rev. A review without CAD tools."""

from __future__ import annotations

import csv
from pathlib import Path
import re
import struct


ROOT = Path(__file__).resolve().parents[1]


def require(path: Path, minimum_size: int = 1) -> None:
    if not path.is_file() or path.stat().st_size < minimum_size:
        raise RuntimeError(f"missing or undersized artifact: {path}")


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if len(data) != 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"invalid PNG: {path}")
    return struct.unpack(">II", data[16:24])


def main() -> int:
    schematic = (
        ROOT / "hardware/edge18-main/edge18-main-rev-a.kicad_sch"
    )
    board = ROOT / "hardware/edge18-main/edge18-main-rev-a.kicad_pcb"
    erc_report = ROOT / "docs/reports/edge18-main-rev-a-erc.rpt"
    drc_report = ROOT / "docs/reports/edge18-main-rev-a-drc.rpt"
    pdf = ROOT / "docs/EDGE-18-projeto-completo-rev-a.pdf"
    pcb_step = ROOT / "mechanical/step/edge18-main-rev-a.step"
    assembly_step = ROOT / "mechanical/step/edge18-rev-a-assembly.step"
    native_model = ROOT / "mechanical/native/edge18-rev-a-assembly.FCStd"
    required = (
        (schematic, 100_000),
        (board, 1_000_000),
        (erc_report, 64),
        (drc_report, 1_000),
        (pdf, 1_000_000),
        (pcb_step, 1_000_000),
        (assembly_step, 1_000_000),
        (native_model, 100_000),
    )
    for path, minimum_size in required:
        require(path, minimum_size)

    erc = erc_report.read_text(encoding="utf-8")
    if "ERC messages: 0  Errors 0  Warnings 0" not in erc:
        raise RuntimeError("committed ERC report is not clean")

    drc = drc_report.read_text(encoding="utf-8")
    expected_drc_markers = (
        "** Found 43 DRC violations **",
        "** Found 24 unconnected pads **",
        "** Found 0 Footprint errors **",
    )
    for marker in expected_drc_markers:
        if marker not in drc:
            raise RuntimeError(f"unexpected frozen DRC state: missing {marker}")
    expected_categories = {
        "hole_to_hole": 4,
        "copper_edge_clearance": 7,
        "clearance": 1,
        "track_dangling": 17,
        "via_dangling": 14,
        "unconnected_items": 24,
    }
    for category, count in expected_categories.items():
        actual = drc.count(f"[{category}]:")
        if actual != count:
            raise RuntimeError(
                f"unexpected {category} count: expected {count}, got {actual}"
            )

    board_text = board.read_text(encoding="utf-8")
    widths = [
        float(value)
        for value in re.findall(
            r"\(segment\b.*?\(width ([0-9.]+)\)",
            board_text,
            flags=re.DOTALL,
        )
    ]
    if not widths or min(widths) < 0.25:
        raise RuntimeError(
            f"unexpected track minimum: {min(widths) if widths else 'none'}"
        )

    bom_path = ROOT / "hardware/bom/edge18-main-rev-a-source.csv"
    require(bom_path, 1_000)
    with bom_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 181:
        raise RuntimeError(f"expected 181 BOM placements, found {len(rows)}")
    if len({row["Reference"] for row in rows}) != len(rows):
        raise RuntimeError("duplicate BOM reference")
    if sum(row["DNP"] == "yes" for row in rows) != 4:
        raise RuntimeError("unexpected DNP count")
    for row in rows:
        for field in ("Reference", "Value", "Footprint", "Manufacturer", "MPN"):
            if not row[field]:
                raise RuntimeError(
                    f"empty BOM {field} for {row['Reference']}"
                )

    images = sorted((ROOT / "docs/images").glob("*.png"))
    if len(images) != 15:
        raise RuntimeError(f"expected 15 images, found {len(images)}")
    for image in images:
        width, height = png_dimensions(image)
        if width < 1100 or height < 650:
            raise RuntimeError(f"undersized image: {image} {width}x{height}")

    if pdf.read_bytes()[:5] != b"%PDF-":
        raise RuntimeError("invalid consolidated PDF")
    if native_model.read_bytes()[:2] != b"PK":
        raise RuntimeError("invalid FCStd container")

    pinout = (
        ROOT / "docs/13-pinout-stm32h563-rev-a.md"
    ).read_text(encoding="utf-8")
    pin_rows = sum(
        line.startswith("| ") and line.split("|")[1].strip().isdigit()
        for line in pinout.splitlines()
    )
    if pin_rows != 144:
        raise RuntimeError(f"expected 144 pinout rows, found {pin_rows}")

    print(
        "EDGE-18 frozen review validation: PASS "
        "(ERC clean; PCB intentionally 43 DRC / 24 unconnected)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
