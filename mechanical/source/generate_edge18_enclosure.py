#!/usr/bin/env python3
"""Generate the EDGE-18 Rev. A enclosure and PCB assembly in FreeCAD."""

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
PCB_STEP_CANDIDATES = (
    ROOT / "release/edge18-rev-a/mechanical/edge18-main-rev-a.step",
    STEP / "edge18-main-rev-a.step",
)

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
    obj.Status = "Rev. A digital model; physical validation required"
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

    # Openings follow the connector envelopes from the KiCad placement.
    ethernet = Part.makeBox(
        28.0,
        WALL + 2.0,
        20.0,
        App.Vector(166.0, -1.0, BOARD_Z - 1.0),
    )
    usb = Part.makeBox(
        21.0,
        WALL + 2.0,
        11.0,
        App.Vector(132.5, -1.0, BOARD_Z - 1.0),
    )
    power = Part.makeBox(
        WALL + 2.0,
        32.0,
        20.0,
        App.Vector(-1.0, BOARD_Y + 4.0, BOARD_Z - 1.0),
    )
    terminal_slot = Part.makeBox(
        174.0,
        WALL + 2.0,
        22.0,
        App.Vector(18.0, ENCLOSURE_D - WALL - 1.0, BOARD_Z - 1.0),
    )
    shell = shell.cut(ethernet).cut(usb).cut(power).cut(terminal_slot)

    for x, y in (
        (BOARD_X + 5.0, BOARD_Y + 5.0),
        (BOARD_X + BOARD_W - 5.0, BOARD_Y + 5.0),
        (BOARD_X + 5.0, BOARD_Y + BOARD_D - 5.0),
        (BOARD_X + BOARD_W - 5.0, BOARD_Y + BOARD_D - 5.0),
    ):
        outer_standoff = Part.makeCylinder(4.5, BOARD_Z - WALL, App.Vector(x, y, WALL))
        hole = Part.makeCylinder(1.65, BOARD_Z, App.Vector(x, y, WALL - 1.0))
        shell = shell.fuse(outer_standoff.cut(hole))
    # Two underside clips represent the DIN-rail adapter interface. Their
    # geometry is intentionally replaceable without modifying the enclosure.
    for x in (55.0, 145.0):
        bridge = Part.makeBox(
            24.0,
            10.0,
            3.0,
            App.Vector(x - 12.0, 70.0, -3.0),
        )
        hook = Part.makeBox(
            24.0,
            3.0,
            7.0,
            App.Vector(x - 12.0, 77.0, -7.0),
        )
        shell = shell.fuse(bridge).fuse(hook)
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
    ):
        board = board.cut(
            Part.makeCylinder(
                1.6,
                BOARD_T + 2.0,
                App.Vector(x, y, BOARD_Z - 1.0),
            )
        )
    return board


def imported_board_shape():
    for path in PCB_STEP_CANDIDATES:
        if not path.exists():
            continue
        shape = Part.Shape()
        shape.read(str(path))
        if shape.isNull():
            continue
        # KiCad exports the board at the design origin. Place it on the four
        # enclosure standoffs and preserve its full component geometry. STEP
        # uses a Y-up Cartesian frame, while the KiCad board runs from Y=0 to
        # Y=120 in screen coordinates; translating by BOARD_Y + BOARD_D maps
        # the exported -120..0 mm envelope to the 15..135 mm standoff area.
        shape.Placement.Base = App.Vector(
            BOARD_X,
            BOARD_Y + BOARD_D,
            BOARD_Z + BOARD_T,
        )
        return shape, path
    return board_shape(), None


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

    document = App.newDocument("EDGE18RevAAssembly")
    features = []
    base = add_feature(
        document,
        "EnclosureBase",
        "EDGE-18 Rev. A aluminum base",
        enclosure_base(),
        (0.72, 0.74, 0.77),
        25,
    )
    features.append(base)
    lid = add_feature(
        document,
        "EnclosureLid",
        "EDGE-18 Rev. A removable lid",
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
    board_geometry, board_source = imported_board_shape()
    board = add_feature(
        document,
        "MainPCB",
        "EDGE-18 Rev. A PCB assembly",
        board_geometry,
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
    parameters.Revision = "Rev. A digital engineering model"
    parameters.addProperty("App::PropertyString", "PCBSource", "EDGE18")
    parameters.PCBSource = (
        str(board_source.relative_to(ROOT))
        if board_source is not None
        else "parametric fallback"
    )

    document.recompute()
    document.saveAs(str(NATIVE / "edge18-rev-a-assembly.FCStd"))
    base_step = STEP / "edge18-rev-a-enclosure-base.step"
    lid_step = STEP / "edge18-rev-a-enclosure-lid.step"
    assembly_step = STEP / "edge18-rev-a-assembly.step"
    Part.export([base], str(base_step))
    Part.export([lid], str(lid_step))
    Part.export(features, str(assembly_step))
    for step_path in (base_step, lid_step, assembly_step):
        normalize_step(step_path)
    App.closeDocument(document.Name)
    print("Generated EDGE-18 Rev. A FreeCAD and STEP artifacts")
    return 0


if __name__ == "__main__":
    main()
