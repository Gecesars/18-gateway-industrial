#!/usr/bin/env python3
"""Validate committed EDGE-18 release artifacts without CAD dependencies."""

from __future__ import annotations

import csv
from pathlib import Path
import struct


ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "release/edge18-rev-a"


def require(path: Path, minimum_size: int = 1) -> None:
    if not path.is_file() or path.stat().st_size < minimum_size:
        raise RuntimeError(f"missing or undersized artifact: {path}")


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if len(data) != 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"invalid PNG: {path}")
    return struct.unpack(">II", data[16:24])


def main() -> int:
    required = (
        ROOT / "hardware/edge18-main/edge18-main-rev-a.kicad_sch",
        ROOT / "hardware/edge18-main/edge18-main-rev-a.kicad_pcb",
        ROOT / "mechanical/native/edge18-rev-a-assembly.FCStd",
        ROOT / "mechanical/step/edge18-rev-a-assembly.step",
        ROOT / "docs/EDGE-18-projeto-completo-rev-a.pdf",
        ROOT / "release/edge18-rev-a.zip",
        RELEASE / "manifest.sha256",
        RELEASE / "documents/edge18-main-rev-a-erc.rpt",
        RELEASE / "documents/edge18-main-rev-a-drc.rpt",
        RELEASE / "documents/edge18-main-rev-a-schematic.pdf",
        RELEASE / "documents/edge18-main-rev-a-assembly.pdf",
        RELEASE / "assembly/edge18-main-rev-a.ipc",
        RELEASE / "assembly/edge18-main-rev-a-position.csv",
        RELEASE / "assembly/edge18-main-rev-a-bom-source.csv",
        RELEASE / "assembly/edge18-main-rev-a-bom-grouped.csv",
        RELEASE / "mechanical/edge18-main-rev-a.step",
    )
    for path in required:
        require(path, 64)

    erc = required[7].read_text(encoding="utf-8")
    drc = required[8].read_text(encoding="utf-8")
    if "ERC messages: 0  Errors 0  Warnings 0" not in erc:
        raise RuntimeError("ERC report is not clean")
    if (
        "** Found 0 DRC violations **" not in drc
        or "** Found 0 unconnected pads **" not in drc
    ):
        raise RuntimeError("DRC report is not clean")

    with (
        ROOT / "hardware/bom/edge18-main-rev-a-source.csv"
    ).open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 181:
        raise RuntimeError(f"expected 181 BOM placements, found {len(rows)}")
    references = [row["Reference"] for row in rows]
    if len(set(references)) != len(references):
        raise RuntimeError("duplicate BOM reference")
    for row in rows:
        for field in ("Reference", "Value", "Footprint", "Manufacturer", "MPN"):
            if not row[field]:
                raise RuntimeError(f"empty BOM {field} for {row['Reference']}")
    if sum(row["DNP"] == "yes" for row in rows) != 4:
        raise RuntimeError("unexpected DNP count")

    images = sorted((ROOT / "docs/images").glob("*.png"))
    if len(images) != 15:
        raise RuntimeError(f"expected 15 documentation images, found {len(images)}")
    for image in images:
        width, height = png_dimensions(image)
        if width < 1100 or height < 650:
            raise RuntimeError(f"undersized image: {image} {width}x{height}")

    pdf = ROOT / "docs/EDGE-18-projeto-completo-rev-a.pdf"
    if pdf.read_bytes()[:5] != b"%PDF-":
        raise RuntimeError("invalid consolidated PDF")
    pinout = (
        ROOT / "docs/13-pinout-stm32h563-rev-a.md"
    ).read_text(encoding="utf-8")
    pin_rows = sum(
        line.startswith("| ") and line.split("|")[1].strip().isdigit()
        for line in pinout.splitlines()
    )
    if pin_rows != 144:
        raise RuntimeError(f"expected 144 pinout rows, found {pin_rows}")

    gerbers = list((RELEASE / "gerbers").glob("*"))
    if len(gerbers) < 12:
        raise RuntimeError("incomplete Gerber/drill set")
    print("EDGE-18 release validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
