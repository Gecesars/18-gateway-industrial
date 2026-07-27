#!/usr/bin/env python3
"""Generate the EDGE-18 P0 dimensional assembly in FreeCAD."""

from __future__ import annotations

import os
from pathlib import Path
import sys

import FreeCAD as App

freecad_root = os.environ.get("FREECAD_LOCAL_ROOT")
if freecad_root:
    sys.path.insert(0, f"{freecad_root}/usr/lib/freecad-python3/lib")

import Part


ROOT = Path(__file__).resolve().parents[2]
NATIVE = ROOT / "mechanical/native"
STEP = ROOT / "mechanical/step"

ENCLOSURE_W = 210.0
ENCLOSURE_D = 150.0
ENCLOSURE_H = 65.0
WALL = 3.0
BOARD_W = 180.0
BOARD_D = 120.0
BOARD_T = 1.6
BOARD_X = 15.0
BOARD_Y = 15.0
BOARD_Z = 10.0


def add_feature(document, name: str, label: str, shape, color, transparency=0):
    obj = document.addObject("Part::Feature", name)
    obj.Label = label
    obj.Shape = shape
    obj.addProperty("App::PropertyString", "Status", "EDGE18")
    obj.Status = "P0 dimensional envelope; not released for fabrication"
    if obj.ViewObject is not None:
        obj.ViewObject.ShapeColor = color
        obj.ViewObject.Transparency = transparency
    return obj


def enclosure_base():
    outer = Part.makeBox(ENCLOSURE_W, ENCLOSURE_D, ENCLOSURE_H - WALL)
    cavity = Part.makeBox(
        ENCLOSURE_W - 2.0 * WALL,
        ENCLOSURE_D - 2.0 * WALL,
        ENCLOSURE_H,
        App.Vector(WALL, WALL, WALL),
    )
    shell = outer.cut(cavity)

    # Service openings are deliberately oversized P0 envelopes.
    ethernet = Part.makeBox(18.0, WALL + 2.0, 16.0, App.Vector(160.0, -1.0, 24.0))
    usb = Part.makeBox(12.0, WALL + 2.0, 8.0, App.Vector(184.0, -1.0, 27.0))
    terminal_slot = Part.makeBox(
        150.0,
        WALL + 2.0,
        18.0,
        App.Vector(20.0, ENCLOSURE_D - WALL - 1.0, 20.0),
    )
    shell = shell.cut(ethernet).cut(usb).cut(terminal_slot)

    for x, y in (
        (BOARD_X + 5.0, BOARD_Y + 5.0),
        (BOARD_X + BOARD_W - 5.0, BOARD_Y + 5.0),
        (BOARD_X + 5.0, BOARD_Y + BOARD_D - 5.0),
        (BOARD_X + BOARD_W - 5.0, BOARD_Y + BOARD_D - 5.0),
        (BOARD_X + BOARD_W / 2.0, BOARD_Y + 5.0),
        (BOARD_X + BOARD_W / 2.0, BOARD_Y + BOARD_D - 5.0),
    ):
        outer_standoff = Part.makeCylinder(4.5, BOARD_Z - WALL, App.Vector(x, y, WALL))
        hole = Part.makeCylinder(1.65, BOARD_Z, App.Vector(x, y, WALL - 1.0))
        shell = shell.fuse(outer_standoff.cut(hole))
    return shell


def board_shape():
    board = Part.makeBox(
        BOARD_W,
        BOARD_D,
        BOARD_T,
        App.Vector(BOARD_X, BOARD_Y, BOARD_Z),
    )
    for x, y in (
        (BOARD_X + 5.0, BOARD_Y + 5.0),
        (BOARD_X + BOARD_W - 5.0, BOARD_Y + 5.0),
        (BOARD_X + 5.0, BOARD_Y + BOARD_D - 5.0),
        (BOARD_X + BOARD_W - 5.0, BOARD_Y + BOARD_D - 5.0),
        (BOARD_X + BOARD_W / 2.0, BOARD_Y + 5.0),
        (BOARD_X + BOARD_W / 2.0, BOARD_Y + BOARD_D - 5.0),
    ):
        board = board.cut(
            Part.makeCylinder(
                1.6,
                BOARD_T + 2.0,
                App.Vector(x, y, BOARD_Z - 1.0),
            )
        )
    return board


def zone(x, y, width, depth, height=12.0):
    return Part.makeBox(
        width,
        depth,
        height,
        App.Vector(BOARD_X + x, BOARD_Y + y, BOARD_Z + BOARD_T),
    )


def normalize_step(path: Path) -> None:
    """Remove exporter-only trailing blanks while preserving STEP content."""
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text(
        "\n".join(line.rstrip() for line in lines) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    NATIVE.mkdir(parents=True, exist_ok=True)
    STEP.mkdir(parents=True, exist_ok=True)

    document = App.newDocument("EDGE18P0Assembly")
    features = []
    base = add_feature(
        document,
        "EnclosureBase",
        "EDGE-18 P0 aluminum base",
        enclosure_base(),
        (0.72, 0.74, 0.77),
        25,
    )
    features.append(base)
    lid = add_feature(
        document,
        "EnclosureLid",
        "EDGE-18 P0 removable lid",
        Part.makeBox(
            ENCLOSURE_W,
            ENCLOSURE_D,
            WALL,
            App.Vector(0.0, 0.0, ENCLOSURE_H - WALL),
        ),
        (0.82, 0.84, 0.87),
        35,
    )
    features.append(lid)
    board = add_feature(
        document,
        "MainPCB",
        "EDGE-18 P0 PCB 180 x 120 mm",
        board_shape(),
        (0.06, 0.36, 0.16),
    )
    features.append(board)

    zone_specs = (
        ("PowerZone", "Power/protection envelope", 0.0, 0.0, 40.0, 35.0, (0.78, 0.20, 0.12)),
        ("AnalogZone", "Analog input envelope", 0.0, 42.0, 55.0, 58.0, (0.20, 0.45, 0.82)),
        ("DigitalInputZone", "Digital input envelope", 60.0, 65.0, 42.0, 35.0, (0.65, 0.35, 0.82)),
        ("ControllerZone", "STM32 and storage envelope", 60.0, 5.0, 62.0, 52.0, (0.15, 0.60, 0.32)),
        ("IsolatedBusZone", "RS-485 and CAN isolation envelope", 108.0, 65.0, 68.0, 35.0, (0.90, 0.58, 0.10)),
        ("EthernetZone", "Ethernet PHY and magnetics envelope", 128.0, 5.0, 48.0, 35.0, (0.10, 0.62, 0.70)),
        ("WiFiKeepout", "Wi-Fi antenna keep-out envelope", 155.0, 42.0, 21.0, 18.0, (0.82, 0.78, 0.10)),
    )
    for name, label, x, y, width, depth, color in zone_specs:
        features.append(
            add_feature(
                document,
                name,
                label,
                zone(x, y, width, depth),
                color,
                45,
            )
        )

    parameters = document.addObject("App::FeaturePython", "Parameters")
    for name, value in (
        ("EnclosureWidth", ENCLOSURE_W),
        ("EnclosureDepth", ENCLOSURE_D),
        ("EnclosureHeight", ENCLOSURE_H),
        ("WallThickness", WALL),
        ("BoardWidth", BOARD_W),
        ("BoardDepth", BOARD_D),
        ("BoardThickness", BOARD_T),
    ):
        parameters.addProperty("App::PropertyLength", name, "Dimensions")
        setattr(parameters, name, value)
    parameters.addProperty("App::PropertyString", "Revision", "EDGE18")
    parameters.Revision = "P0 dimensional baseline"

    document.recompute()
    document.saveAs(str(NATIVE / "edge18-p0-assembly.FCStd"))
    base_step = STEP / "edge18-p0-enclosure-base.step"
    lid_step = STEP / "edge18-p0-enclosure-lid.step"
    assembly_step = STEP / "edge18-p0-assembly.step"
    Part.export([base], str(base_step))
    Part.export([lid], str(lid_step))
    Part.export(features, str(assembly_step))
    for step_path in (base_step, lid_step, assembly_step):
        normalize_step(step_path)
    App.closeDocument(document.Name)
    print("Generated EDGE-18 FreeCAD and STEP artifacts")
    return 0


if __name__ == "__main__":
    main()
