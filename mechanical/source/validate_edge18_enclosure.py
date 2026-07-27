#!/usr/bin/env python3
"""Validate the generated EDGE-18 P0 FreeCAD assembly."""

from __future__ import annotations

from pathlib import Path
import os
import sys

import FreeCAD as App

freecad_root = os.environ.get("FREECAD_LOCAL_ROOT")
if freecad_root:
    sys.path.insert(0, f"{freecad_root}/usr/lib/freecad-python3/lib")

import Part  # noqa: F401


ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / "mechanical/native/edge18-p0-assembly.FCStd"


def close(actual: float, expected: float, tolerance: float = 0.05) -> bool:
    return abs(actual - expected) <= tolerance


def main() -> int:
    if not MODEL.exists():
        raise FileNotFoundError(MODEL)
    document = App.openDocument(str(MODEL))

    required = {
        "EnclosureBase",
        "EnclosureLid",
        "MainPCB",
        "PowerZone",
        "AnalogZone",
        "DigitalInputZone",
        "ControllerZone",
        "IsolatedBusZone",
        "EthernetZone",
        "WiFiKeepout",
        "Parameters",
    }
    present = {obj.Name for obj in document.Objects}
    missing = required - present
    if missing:
        raise RuntimeError(f"missing objects: {sorted(missing)}")

    board = document.getObject("MainPCB").Shape.BoundBox
    if not close(board.XLength, 180.0) or not close(board.YLength, 120.0):
        raise RuntimeError(
            f"unexpected board envelope {board.XLength} x {board.YLength}"
        )

    parameters = document.getObject("Parameters")
    if not close(parameters.EnclosureWidth.Value, 210.0):
        raise RuntimeError("unexpected enclosure width")
    if not close(parameters.EnclosureDepth.Value, 150.0):
        raise RuntimeError("unexpected enclosure depth")
    if not close(parameters.EnclosureHeight.Value, 65.0):
        raise RuntimeError("unexpected enclosure height")

    App.closeDocument(document.Name)
    print("EDGE-18 mechanical validation: PASS")
    return 0


if __name__ == "__main__":
    main()
