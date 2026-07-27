#!/usr/bin/env python3
"""Generate the native EDGE-18 KiCad schematic, PCB and BOM source data.

The generated KiCad files remain editable. Intentional CAD changes must be
incorporated here because regeneration replaces the native schematic and PCB.
"""

from __future__ import annotations

import argparse
import copy
import csv
import json
import math
import os
from pathlib import Path
import re
import sys
import uuid
from dataclasses import dataclass, field

import pcbnew
from kiutils.items.common import (
    Effects,
    Font,
    Justify,
    PageSettings,
    Position,
    Property,
    TitleBlock,
)
from kiutils.items.schitems import (
    Connection,
    LocalLabel,
    NoConnect,
    SchematicSymbol,
    SymbolProjectInstance,
    SymbolProjectPath,
    Text,
)
from kiutils.schematic import Schematic
from kiutils.symbol import SymbolLib


ROOT = Path(__file__).resolve().parents[2]
HARDWARE = ROOT / "hardware"
KICAD_DIR = HARDWARE / "edge18-main"
LIBRARY_DIR = HARDWARE / "libraries"
OUTPUT_STEM = "edge18-main-rev-a"
TOOL_ROOT = Path(
    os.environ.get(
        "EDGE18_TOOL_ROOT",
        "/mnt/eftx-data/cache/antenna-coupler-tools",
    )
)
KICAD_ROOT = Path(
    os.environ.get("KICAD_LOCAL_ROOT", TOOL_ROOT / "kicad/root")
)
SYMBOL_DIR = KICAD_ROOT / "usr/share/kicad/symbols"
FOOTPRINT_DIR = KICAD_ROOT / "usr/share/kicad/footprints"


def uid() -> str:
    return str(uuid.uuid4())


@dataclass
class SymbolSpec:
    library: str
    entry: str
    reference: str
    value: str
    footprint: str
    x: float
    y: float
    nets: dict[str, str | None]
    block: str
    pcb_x: float | None = None
    pcb_y: float | None = None
    pcb_rotation: float = 0.0
    datasheet: str = ""
    manufacturer: str = ""
    mpn: str = ""
    description: str = ""
    in_bom: bool = True
    on_board: bool = True
    dnp: bool = False
    label_length: float = 6.35
    label_size: float = 0.82
    property_offsets: dict[
        str, tuple[float, float, float, bool]
    ] = field(default_factory=dict)


class SchematicBuilder:
    def __init__(self) -> None:
        self.project = OUTPUT_STEM
        self.sch = Schematic.create_new()
        self.sch.version = "20231120"
        self.sch.generator = "eeschema"
        self.sch.uuid = uid()
        self.sch.paper = PageSettings(paperSize="A0")
        self.sch.titleBlock = TitleBlock(
            title="EDGE-18 industrial gateway — complete electrical design",
            date="2026-07-27",
            revision="REV A — FROZEN DIGITAL REVIEW",
            company="Gecesars / EDGE-18",
            comments={
                1: "9–36 VDC • STM32H563 • Ethernet • isolated RS-485/CAN",
                2: "NOT FOR FABRICATION — PCB DRC/connectivity remains open",
                3: "Labels replace long wires to preserve schematic readability",
            },
        )
        self.specs: list[SymbolSpec] = []
        self._libraries: dict[str, SymbolLib] = {}
        self._embedded: set[str] = set()
        self._wire_segments: list[
            tuple[str, tuple[float, float], tuple[float, float], str]
        ] = []

    def _library(self, name: str) -> SymbolLib:
        if name not in self._libraries:
            local = LIBRARY_DIR / f"{name}.kicad_sym"
            source = local if local.exists() else SYMBOL_DIR / f"{name}.kicad_sym"
            self._libraries[name] = SymbolLib.from_file(str(source))
        return self._libraries[name]

    def _raw_symbol(self, library: str, entry: str):
        return next(
            symbol
            for symbol in self._library(library).symbols
            if symbol.entryName == entry
        )

    def _pin_source(self, library: str, entry: str):
        symbol = self._raw_symbol(library, entry)
        if symbol.extends:
            return self._pin_source(library, symbol.extends)
        return symbol

    @staticmethod
    def _pins(symbol) -> list:
        pins = list(symbol.pins)
        for unit in symbol.units:
            if unit.unitId in (None, 0, 1):
                pins.extend(unit.pins)
        return pins

    @staticmethod
    def _between(value: float, end_a: float, end_b: float) -> bool:
        tolerance = 1e-6
        return min(end_a, end_b) - tolerance <= value <= max(
            end_a,
            end_b,
        ) + tolerance

    @classmethod
    def _segments_intersect(
        cls,
        start_a: tuple[float, float],
        end_a: tuple[float, float],
        start_b: tuple[float, float],
        end_b: tuple[float, float],
    ) -> bool:
        tolerance = 1e-6
        a_vertical = abs(start_a[0] - end_a[0]) < tolerance
        b_vertical = abs(start_b[0] - end_b[0]) < tolerance
        if a_vertical and b_vertical:
            return (
                abs(start_a[0] - start_b[0]) < tolerance
                and (
                    cls._between(start_a[1], start_b[1], end_b[1])
                    or cls._between(end_a[1], start_b[1], end_b[1])
                    or cls._between(start_b[1], start_a[1], end_a[1])
                )
            )
        if not a_vertical and not b_vertical:
            return (
                abs(start_a[1] - start_b[1]) < tolerance
                and (
                    cls._between(start_a[0], start_b[0], end_b[0])
                    or cls._between(end_a[0], start_b[0], end_b[0])
                    or cls._between(start_b[0], start_a[0], end_a[0])
                )
            )
        if a_vertical:
            vertical_start, vertical_end = start_a, end_a
            horizontal_start, horizontal_end = start_b, end_b
        else:
            vertical_start, vertical_end = start_b, end_b
            horizontal_start, horizontal_end = start_a, end_a
        return cls._between(
            vertical_start[0],
            horizontal_start[0],
            horizontal_end[0],
        ) and cls._between(
            horizontal_start[1],
            vertical_start[1],
            vertical_end[1],
        )

    def _guard_wire(
        self,
        net: str,
        start: Position,
        end: Position,
        owner: str,
    ) -> None:
        start_xy = (start.X, start.Y)
        end_xy = (end.X, end.Y)
        for other_net, other_start, other_end, other_owner in self._wire_segments:
            if other_net == net:
                continue
            if self._segments_intersect(
                start_xy,
                end_xy,
                other_start,
                other_end,
            ):
                raise ValueError(
                    "schematic wire collision: "
                    f"{owner} ({net}) intersects "
                    f"{other_owner} ({other_net})"
                )
        self._wire_segments.append((net, start_xy, end_xy, owner))

    def _embed(self, library: str, entry: str) -> None:
        lib_id = f"{library}:{entry}"
        if lib_id in self._embedded:
            return
        source = self._raw_symbol(library, entry)
        if source.extends:
            symbol = copy.deepcopy(self._pin_source(library, entry))
            symbol.properties = copy.deepcopy(source.properties)
        else:
            symbol = copy.deepcopy(source)
        symbol.libId = lib_id
        symbol.extends = None
        self.sch.libSymbols.append(symbol)
        self._embedded.add(lib_id)

    def add(self, spec: SymbolSpec) -> None:
        grid = 1.27
        spec.x = round(spec.x / grid) * grid
        spec.y = round(spec.y / grid) * grid
        self.specs.append(spec)
        self._embed(spec.library, spec.entry)
        library_symbol = self._raw_symbol(spec.library, spec.entry)
        source = self._pin_source(spec.library, spec.entry)
        pins = self._pins(source)
        known_pins = {pin.number for pin in pins}
        unknown = set(spec.nets) - known_pins
        if unknown:
            raise ValueError(
                f"{spec.reference} {spec.library}:{spec.entry}: "
                f"unknown pins {sorted(unknown)}; valid={sorted(known_pins)}"
            )

        sheet_y = [spec.y - pin.position.Y for pin in pins] or [spec.y]
        top = min(sheet_y)
        bottom = max(sheet_y)
        default_properties = {
            "Reference": (0.0, top - spec.y - 3.0, 0.0, False),
            "Value": (0.0, bottom - spec.y + 3.0, 0.0, False),
        }
        properties = copy.deepcopy(library_symbol.properties)
        if not properties and library_symbol.extends:
            properties = copy.deepcopy(source.properties)
        wanted = {
            "Reference": spec.reference,
            "Value": spec.value,
            "Footprint": spec.footprint,
            "Datasheet": spec.datasheet,
            "Manufacturer": spec.manufacturer,
            "MPN": spec.mpn,
            "Block": spec.block,
            "Description": spec.description,
        }
        found: set[str] = set()
        for prop in properties:
            if prop.key in wanted:
                prop.value = wanted[prop.key]
                found.add(prop.key)
            if prop.effects is None:
                prop.effects = Effects(font=Font(width=1.0, height=1.0))
            placement = spec.property_offsets.get(
                prop.key,
                default_properties.get(
                    prop.key,
                    (0.0, 0.0, 0.0, prop.key not in {"Reference", "Value"}),
                ),
            )
            dx, dy, angle, hide = placement
            prop.position = Position(spec.x + dx, spec.y + dy, angle)
            prop.effects.hide = hide
            if prop.key in {"Reference", "Value"}:
                prop.effects.font = Font(width=1.0, height=1.0)
        for key, value in wanted.items():
            if key in found:
                continue
            dx, dy, angle, hide = spec.property_offsets.get(
                key,
                default_properties.get(
                    key,
                    (0.0, 0.0, 0.0, key not in {"Reference", "Value"}),
                ),
            )
            properties.append(
                Property(
                    key=key,
                    value=value,
                    position=Position(spec.x + dx, spec.y + dy, angle),
                    effects=Effects(
                        font=Font(width=1.0, height=1.0),
                        hide=hide,
                    ),
                )
            )

        instance = SchematicSymbol(
            libraryNickname=spec.library,
            entryName=spec.entry,
            position=Position(spec.x, spec.y, 0),
            unit=1,
            inBom=spec.in_bom,
            onBoard=spec.on_board,
            dnp=spec.dnp,
            uuid=uid(),
            properties=properties,
            pins={pin.number: uid() for pin in pins},
            instances=[
                SymbolProjectInstance(
                    name=self.project,
                    paths=[
                        SymbolProjectPath(
                            sheetInstancePath=f"/{self.sch.uuid}",
                            reference=spec.reference,
                            unit=1,
                        )
                    ],
                )
            ],
        )
        self.sch.schematicSymbols.append(instance)

        for pin in pins:
            position = Position(
                spec.x + pin.position.X,
                spec.y - pin.position.Y,
                0,
            )
            net = spec.nets.get(pin.number)
            if net:
                outward = {
                    0: (-spec.label_length, 0.0),
                    90: (0.0, spec.label_length),
                    180: (spec.label_length, 0.0),
                    270: (0.0, -spec.label_length),
                }.get(
                    int(pin.position.angle or 0) % 360,
                    (-spec.label_length, 0.0),
                )
                direction = (
                    int(math.copysign(1, outward[0])) if outward[0] else 0,
                    int(math.copysign(1, outward[1])) if outward[1] else 0,
                )
                label_angle = {
                    (-1, 0): 0,
                    (1, 0): 180,
                    (0, 1): 90,
                    (0, -1): 270,
                }[direction]
                label_position = Position(
                    position.X + outward[0],
                    position.Y + outward[1],
                    label_angle,
                )
                self._guard_wire(
                    net,
                    position,
                    label_position,
                    f"{spec.reference}.{pin.number}",
                )
                self.sch.graphicalItems.append(
                    Connection(
                        type="wire",
                        points=[position, label_position],
                        uuid=uid(),
                    )
                )
                self.sch.labels.append(
                    LocalLabel(
                        text=net,
                        position=label_position,
                        effects=Effects(
                            font=Font(
                                width=spec.label_size,
                                height=spec.label_size,
                            )
                        ),
                        uuid=uid(),
                    )
                )
            else:
                self.sch.noConnects.append(
                    NoConnect(position=position, uuid=uid())
                )

    def note(self, text: str, x: float, y: float, size: float = 1.6) -> None:
        self.sch.texts.append(
            Text(
                text=text,
                position=Position(x, y, 0),
                effects=Effects(
                    font=Font(width=size, height=size, bold=True),
                    justify=Justify(horizontally="left"),
                ),
                uuid=uid(),
            )
        )

    def write(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.sch.to_file(str(path), encoding="utf-8")


def spec(
    library: str,
    entry: str,
    reference: str,
    value: str,
    footprint: str,
    x: float,
    y: float,
    nets: dict[str, str | None],
    block: str,
    pcb: tuple[float, float, float] | None = None,
    **kwargs,
) -> SymbolSpec:
    pcb_x = pcb[0] if pcb else None
    pcb_y = pcb[1] if pcb else None
    pcb_rotation = pcb[2] if pcb else 0.0
    return SymbolSpec(
        library=library,
        entry=entry,
        reference=reference,
        value=value,
        footprint=footprint,
        x=x,
        y=y,
        nets=nets,
        block=block,
        pcb_x=pcb_x,
        pcb_y=pcb_y,
        pcb_rotation=pcb_rotation,
        **kwargs,
    )


def passive(
    entry: str,
    reference: str,
    value: str,
    footprint: str,
    x: float,
    y: float,
    net1: str,
    net2: str,
    block: str,
    pcb: tuple[float, float, float],
    **kwargs,
) -> SymbolSpec:
    # KiCad's default Device symbols are vertical in this drawing. Keeping the
    # reference/value above and below them competes with the vertical net
    # labels. Put the two visible properties on opposite sides and extend the
    # label stubs so text never sits on the symbol body.
    kwargs.setdefault("label_length", 3.81)
    kwargs.setdefault(
        "property_offsets",
        {
            "Reference": (-2.8, 0.0, 90.0, False),
            "Value": (2.8, 0.0, 90.0, False),
        },
    )
    return spec(
        "Device",
        entry,
        reference,
        value,
        footprint,
        x,
        y,
        {"1": net1, "2": net2},
        block,
        pcb,
        **kwargs,
    )


def connector(
    count: int,
    reference: str,
    value: str,
    footprint: str,
    x: float,
    y: float,
    nets: list[str | None],
    block: str,
    pcb: tuple[float, float, float],
    **kwargs,
) -> SymbolSpec:
    kwargs.setdefault("label_length", 3.81)
    return spec(
        "Connector_Generic",
        f"Conn_01x{count:02d}",
        reference,
        value,
        footprint,
        x,
        y,
        {str(index): net for index, net in enumerate(nets, start=1)},
        block,
        pcb,
        **kwargs,
    )


def write_custom_symbols() -> None:
    """Create the exact 20-pin ISOW1412 symbol from a matching TI package."""
    source = SymbolLib.from_file(
        str(SYMBOL_DIR / "Interface_CAN_LIN.kicad_sym")
    )
    symbol = copy.deepcopy(
        next(item for item in source.symbols if item.entryName == "ISOW1044")
    )
    symbol.entryName = "ISOW1412"
    symbol.libId = "ISOW1412"
    for unit in symbol.units:
        unit.entryName = "ISOW1412"
        unit.libId = re.sub(r"^ISOW1044", "ISOW1412", unit.libId)
    pin_names = {
        "1": "VIO",
        "2": "D",
        "3": "DE",
        "4": "R",
        "5": "~{RE}",
        "6": "GNDIO",
        "7": "OUT",
        "8": "EN/FLT",
        "9": "VDD",
        "10": "GND1",
        "11": "GND2",
        "12": "VISOOUT",
        "13": "MODE",
        "14": "IN",
        "15": "GISOIN",
        "16": "VISOIN",
        "17": "Y",
        "18": "Z",
        "19": "B",
        "20": "A",
    }
    pin_types = {
        "1": "power_in",
        "2": "input",
        "3": "input",
        "4": "output",
        "5": "input",
        "6": "power_in",
        "7": "output",
        "8": "bidirectional",
        "9": "power_in",
        "10": "power_in",
        "11": "power_in",
        "12": "power_out",
        "13": "input",
        "14": "input",
        "15": "power_in",
        "16": "power_in",
        "17": "output",
        "18": "output",
        "19": "input",
        "20": "input",
    }
    field_positions = {
        "13": Position(15.24, -5.08, 180),
        "14": Position(15.24, -7.62, 180),
        "15": Position(2.54, -17.78, 90),
        "16": Position(2.54, 17.78, 270),
        "17": Position(15.24, 7.62, 180),
        "18": Position(15.24, 5.08, 180),
        "19": Position(15.24, 2.54, 180),
        "20": Position(15.24, 0.0, 180),
    }
    for unit in symbol.units:
        for pin in unit.pins:
            pin.name = pin_names[pin.number]
            pin.electricalType = pin_types[pin.number]
            if pin.number in field_positions:
                pin.position = field_positions[pin.number]
    replacements = {
        "Reference": "U",
        "Value": "ISOW1412",
        "Footprint": "Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm",
        "Datasheet": "https://www.ti.com/lit/ds/symlink/isow1412.pdf",
        "Description": (
            "500 kbps isolated RS-485/RS-422 transceiver with integrated "
            "reinforced isolated DC/DC, SOIC-20W"
        ),
    }
    for prop in symbol.properties:
        if prop.key in replacements:
            prop.value = replacements[prop.key]
    LIBRARY_DIR.mkdir(parents=True, exist_ok=True)
    SymbolLib(
        version="20231120",
        generator="edge18",
        symbols=[symbol],
    ).to_file(
        str(LIBRARY_DIR / "EDGE18.kicad_sym"),
        encoding="utf-8",
    )


def add_power_block(builder: SchematicBuilder) -> None:
    block = "POWER"
    builder.note(
        "1 — POWER INPUT, PROTECTION AND REGULATION (9–36 VDC)",
        18,
        18,
        2.0,
    )
    builder.add(
        connector(
            3,
            "J1",
            "POWER 9–36V / RETURN / CHASSIS",
            "TerminalBlock_Phoenix:"
            "TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal",
            30,
            60,
            ["VIN_RAW", "GND", "CHASSIS"],
            block,
            (12, 17, 90),
            manufacturer="Phoenix Contact",
            mpn="1715035 equivalent",
            description="Field power terminal, 5.08 mm pitch",
        )
    )
    builder.add(
        passive(
            "Fuse",
            "F1",
            "2A resettable",
            "Fuse:Fuse_1812_4532Metric",
            58,
            48,
            "VIN_RAW",
            "VIN_FUSED",
            block,
            (24, 18, 0),
            manufacturer="Littelfuse",
            mpn="1812L200/33",
        )
    )
    builder.add(
        passive(
            "D_TVS",
            "D1",
            "SMBJ36A",
            "Diode_SMD:D_SMB",
            76,
            72,
            "VIN_FUSED",
            "GND",
            block,
            (31, 24, 90),
            manufacturer="Littelfuse",
            mpn="SMBJ36A",
        )
    )
    builder.add(
        passive(
            "D_Schottky",
            "D2",
            "SS56 60V/5A",
            "Diode_SMD:D_SMB",
            88,
            48,
            "VIN_FUSED",
            "VIN_PROTECTED",
            block,
            (36, 18, 0),
            manufacturer="Diodes Inc.",
            mpn="SS56-13-F",
            description="Series reverse-polarity protection",
        )
    )
    builder.add(
        passive(
            "L",
            "L1",
            "10uH input EMI",
            "Inductor_SMD:L_12x12mm_H6mm",
            113,
            48,
            "VIN_PROTECTED",
            "VIN_FILTERED",
            block,
            (45, 18, 0),
            manufacturer="Bourns",
            mpn="SRP1265A-100M",
        )
    )
    for reference, value, x, y, pcb_x, pcb_y in (
        ("C1", "100uF 63V", 105, 76, 42, 27),
        ("C2", "1uF 100V X7R", 124, 76, 49, 27),
    ):
        builder.add(
            passive(
                "C",
                reference,
                value,
                "Capacitor_SMD:C_1210_3225Metric",
                x,
                y,
                "VIN_FILTERED",
                "GND",
                block,
                (pcb_x, pcb_y, 90),
                manufacturer="TDK",
                mpn="X7R industrial equivalent",
            )
        )

    lm_nets = {
        "1": "SW_5V",
        "2": "SW_5V",
        "3": "SW_5V",
        "4": "SW_5V",
        "5": "SW_5V",
        "6": "BOOT_5V",
        "8": "VCC_5V",
        "9": "5V",
        "10": "RT_5V",
        "11": "SS_5V",
        "12": "FB_5V",
        "13": "GND",
        "14": "GND",
        "15": "GND",
        "16": "PGOOD_5V",
        "17": "GND",
        "18": "EN_5V",
        "19": "GND",
        "20": "VIN_FILTERED",
        "21": "VIN_FILTERED",
        "22": "VIN_FILTERED",
        "24": "GND",
        "25": "GND",
        "26": "GND",
        "27": "GND",
        "28": "GND",
        "29": "GND",
        "30": "GND",
        "31": "GND",
    }
    builder.add(
        spec(
            "Regulator_Switching",
            "LM76002",
            "U1",
            "LM76002RNPR",
            "Package_DFN_QFN:"
            "Texas_RNP0030B_WQFN-30-1EP_4x6mm_P0.5mm_"
            "EP1.8x4.5mm_ThermalVias",
            158,
            62,
            lm_nets,
            block,
            (57, 22, 0),
            datasheet="https://www.ti.com/lit/ds/symlink/lm76002.pdf",
            manufacturer="Texas Instruments",
            mpn="LM76002RNPR",
            description="60 V, 2.5 A synchronous buck regulator",
        )
    )
    builder.add(
        passive(
            "L",
            "L2",
            "10uH / 4.5A",
            "Inductor_SMD:L_10.4x10.4_H4.8",
            194,
            52,
            "SW_5V",
            "5V",
            block,
            (69, 22, 0),
            manufacturer="Coilcraft",
            mpn="XAL1010-103",
        )
    )
    for args in (
        ("C3", "100nF 100V", 183, 37, "BOOT_5V", "SW_5V", 63, 17),
        ("C4", "10uF 16V", 205, 76, "5V", "GND", 76, 27),
        ("C5", "10uF 16V", 221, 76, "5V", "GND", 80, 27),
        ("C6", "4.7nF", 142, 102, "SS_5V", "GND", 54, 29),
        ("C33", "1uF 10V", 230, 112, "VCC_5V", "GND", 66, 29),
    ):
        reference, value, x, y, net1, net2, px, py = args
        builder.add(
            passive(
                "C",
                reference,
                value,
                "Capacitor_SMD:C_0603_1608Metric",
                x,
                y,
                net1,
                net2,
                block,
                (px, py, 0),
                manufacturer="TDK",
                mpn="C1608 X7R series",
            )
        )
    for args in (
        ("R1", "40.2k 1%", 203, 98, "5V", "FB_5V", 72, 31),
        ("R2", "10.0k 1%", 220, 98, "FB_5V", "GND", 77, 31),
        ("R3", "150k 1%", 116, 112, "VIN_FILTERED", "EN_5V", 50, 33),
        ("R4", "33k 1%", 133, 112, "EN_5V", "GND", 55, 33),
        ("R5", "100k 1%", 157, 112, "RT_5V", "GND", 61, 33),
        ("R6", "10k", 178, 112, "5V", "PGOOD_5V", 66, 33),
    ):
        reference, value, x, y, net1, net2, px, py = args
        builder.add(
            passive(
                "R",
                reference,
                value,
                "Resistor_SMD:R_0603_1608Metric",
                x,
                y,
                net1,
                net2,
                block,
                (px, py, 0),
                manufacturer="Yageo",
                mpn="RC0603FR series",
            )
        )

    tps_nets = {
        "1": "SW_3V3",
        "2": "SW_3V3",
        "3": "SW_3V3",
        "4": "PGOOD_3V3",
        "5": "3V3",
        "6": "GND",
        "7": "GND",
        "8": "GND",
        "9": "SS_3V3",
        "10": "5V",
        "11": "5V",
        "12": "5V",
        "13": "5V",
        "14": "3V3",
        "15": "GND",
        "16": "GND",
        "17": "GND",
    }
    builder.add(
        spec(
            "Regulator_Switching",
            "TPS62132",
            "U2",
            "TPS62132RGTR",
            "Package_DFN_QFN:"
            "VQFN-16-1EP_3x3mm_P0.5mm_EP1.68x1.68mm_ThermalVias",
            158,
            142,
            tps_nets,
            block,
            (88, 22, 0),
            manufacturer="Texas Instruments",
            mpn="TPS62132RGTR",
            datasheet="https://www.ti.com/lit/ds/symlink/tps62130.pdf",
            description="3 A fixed 3.3 V synchronous buck regulator",
        )
    )
    builder.add(
        passive(
            "L",
            "L3",
            "2.2uH / 4A",
            "Inductor_SMD:L_6.3x6.3_H3",
            193,
            136,
            "SW_3V3",
            "3V3",
            block,
            (98, 22, 0),
            manufacturer="Coilcraft",
            mpn="XFL6030-222",
        )
    )
    for args in (
        ("C7", "22uF 10V", 204, 154, "3V3", "GND", 103, 27),
        ("C8", "22uF 10V", 219, 154, "3V3", "GND", 107, 27),
        ("C9", "10nF", 137, 161, "SS_3V3", "GND", 84, 29),
        ("C10", "10uF 10V", 132, 136, "5V", "GND", 83, 17),
    ):
        reference, value, x, y, net1, net2, px, py = args
        builder.add(
            passive(
                "C",
                reference,
                value,
                "Capacitor_SMD:C_0603_1608Metric",
                x,
                y,
                net1,
                net2,
                block,
                (px, py, 0),
                manufacturer="TDK",
                mpn="C1608 X7R series",
            )
        )

    for index, (rail, x) in enumerate(
        (
            ("VIN_FILTERED", 28),
            ("5V", 50),
            ("3V3", 72),
            ("GND", 94),
            ("AGND", 116),
            ("CHASSIS", 138),
        ),
        start=1,
    ):
        builder.add(
            spec(
                "power",
                "PWR_FLAG",
                f"#FLG0{index}",
                "PWR_FLAG",
                "",
                x,
                178,
                {"1": rail},
                block,
                on_board=False,
                in_bom=False,
                label_length=3.81,
            )
        )


def add_controller_block(builder: SchematicBuilder) -> None:
    block = "CONTROLLER"
    builder.note(
        "2 — SECURE CONTROLLER, CLOCKS, DEBUG AND SUPERVISION",
        255,
        18,
        2.0,
    )
    mcu_nets: dict[str, str | None] = {
        "4": "DI1",
        "5": "DI2",
        "6": "3V3_RTC",
        "8": "LSE_IN",
        "9": "LSE_OUT",
        "10": "RTC_INT",
        "17": "3V3",
        "23": "HSE_IN",
        "24": "HSE_OUT",
        "25": "NRST",
        "26": "VIN_MON",
        "27": "ETH_MDC",
        "28": "5V_MON",
        "29": "3V3_MON",
        "30": "3V3",
        "31": "AGND",
        "32": "3V3_A",
        "33": "3V3_A",
        "35": "ETH_REF_CLK",
        "36": "ETH_MDIO",
        "39": "3V3",
        "40": "ADC_CS",
        "41": "ADC_SCK",
        "42": "ADC_MISO",
        "43": "ETH_CRS_DV",
        "44": "ETH_RXD0",
        "45": "ETH_RXD1",
        "46": "ADC_RESET",
        "51": "GND",
        "52": "3V3",
        "56": "LED_RUN",
        "57": "LED_FAULT",
        "58": "WIFI_UART_RX",
        "59": "WIFI_UART_TX",
        "60": "DI3",
        "61": "GND",
        "62": "3V3",
        "63": "WIFI_EN",
        "64": "DI4",
        "66": "WIFI_BOOT",
        "69": "EXP_UART_TX",
        "70": "VCAP1",
        "71": "GND",
        "72": "3V3",
        "73": "FLASH_CS",
        "74": "FLASH_SCK",
        "75": "FLASH_MISO",
        "76": "FLASH_MOSI",
        "77": "RS485B_TX",
        "78": "RS485B_RX",
        "81": "RS485B_DIR",
        "83": "GND",
        "84": "3V3",
        "87": "PGOOD_3V3",
        "88": "PGOOD_5V",
        "94": "GND",
        "95": "3V3",
        "98": "SD_D0",
        "99": "SD_D1",
        "101": "USB_VBUS_SENSE",
        "103": "USB_DM",
        "104": "USB_DP",
        "105": "SWDIO",
        "106": "3V3",
        "107": "GND",
        "108": "3V3",
        "109": "SWCLK",
        "111": "SD_D2",
        "112": "SD_D3",
        "113": "SD_CLK",
        "114": "CAN_RX",
        "115": "CAN_TX",
        "116": "SD_CMD",
        "117": "CAN_STB",
        "118": "RS485A_DIR",
        "119": "RS485A_TX",
        "120": "GND",
        "121": "3V3",
        "122": "RS485A_RX",
        "123": "EXP_GPIO",
        "126": "ETH_TX_EN",
        "128": "ETH_TXD0",
        "129": "ETH_TXD1",
        "130": "GND",
        "131": "3V3",
        "133": "SWO",
        "135": "ADC_MOSI",
        "138": "BOOT0",
        "139": "I2C_SCL",
        "140": "I2C_SDA",
        "142": "VCAP2",
        "143": "GND",
        "144": "3V3",
    }
    # Remaining duplicated power pins use the same rail.
    for pin in ("16", "38", "51", "61", "71", "83", "94", "107", "120", "130", "143"):
        mcu_nets[pin] = "GND"
    for pin in ("17", "30", "39", "52", "62", "72", "84", "95", "108", "131", "144"):
        mcu_nets[pin] = "3V3"
    builder.add(
        spec(
            "MCU_ST_STM32H5",
            "STM32H563ZITx",
            "U3",
            "STM32H563ZIT6",
            "Package_QFP:LQFP-144_20x20mm_P0.5mm",
            340,
            142,
            mcu_nets,
            block,
            (89, 58, 0),
            manufacturer="STMicroelectronics",
            mpn="STM32H563ZIT6",
            datasheet=(
                "https://www.st.com/resource/en/datasheet/stm32h563zi.pdf"
            ),
            description="Cortex-M33 MCU, 2 MB flash, 640 KB RAM, LQFP-144",
            label_length=7.62,
            label_size=0.72,
        )
    )

    for reference, value, x, y, n1, n2, px, py in (
        ("Y1", "25MHz 10pF", 260, 72, "HSE_IN", "HSE_OUT", 70, 53),
        ("Y2", "32.768kHz 12.5pF", 260, 101, "LSE_IN", "LSE_OUT", 70, 63),
    ):
        builder.add(
            passive(
                "Crystal",
                reference,
                value,
                "Crystal:Crystal_SMD_3215-2Pin_3.2x1.5mm",
                x,
                y,
                n1,
                n2,
                block,
                (px, py, 0),
                manufacturer="Abracon",
                mpn="industrial crystal equivalent",
            )
        )
    for args in (
        ("C11", "12pF C0G", 246, 86, "HSE_IN", "GND", 67, 55),
        ("C12", "12pF C0G", 275, 86, "HSE_OUT", "GND", 73, 55),
        ("C13", "12pF C0G", 246, 116, "LSE_IN", "GND", 67, 65),
        ("C14", "12pF C0G", 275, 116, "LSE_OUT", "GND", 73, 65),
        ("C15", "100nF", 447, 55, "3V3", "GND", 80, 46),
        ("C16", "100nF", 462, 55, "3V3", "GND", 84, 46),
        ("C17", "100nF", 477, 55, "3V3", "GND", 88, 46),
        ("C18", "100nF", 492, 55, "3V3", "GND", 92, 46),
        ("C19", "100nF", 507, 55, "3V3", "GND", 96, 46),
        ("C20", "100nF", 522, 55, "3V3", "GND", 100, 46),
        ("C21", "100nF", 537, 55, "3V3", "GND", 104, 46),
        ("C22", "100nF", 552, 55, "3V3", "GND", 108, 46),
        ("C23", "4.7uF", 447, 77, "3V3", "GND", 80, 50),
        ("C24", "2.2uF low-ESR", 466, 77, "VCAP1", "GND", 84, 50),
        ("C25", "2.2uF low-ESR", 486, 77, "VCAP2", "GND", 88, 50),
        ("C26", "100nF", 505, 77, "3V3_A", "AGND", 96, 50),
        ("C27", "1uF", 522, 77, "3V3_A", "AGND", 100, 50),
        ("C28", "100nF", 539, 77, "3V3_RTC", "GND", 104, 50),
        ("C29", "100nF", 558, 77, "NRST", "GND", 108, 50),
    ):
        reference, value, x, y, net1, net2, px, py = args
        builder.add(
            passive(
                "C",
                reference,
                value,
                "Capacitor_SMD:C_0603_1608Metric",
                x,
                y,
                net1,
                net2,
                block,
                (px, py, 0),
                manufacturer="TDK",
                mpn="C1608 series",
            )
        )
    builder.add(
        passive(
            "FerriteBead",
            "FB1",
            "600R@100MHz",
            "Inductor_SMD:L_0603_1608Metric",
            462,
            102,
            "3V3",
            "3V3_A",
            block,
            (96, 54, 0),
            manufacturer="Murata",
            mpn="BLM18AG601SN1D",
        )
    )
    builder.add(
        passive(
            "R",
            "R10",
            "10k",
            "Resistor_SMD:R_0603_1608Metric",
            447,
            119,
            "3V3",
            "NRST",
            block,
            (78, 56, 0),
            manufacturer="Yageo",
            mpn="RC0603FR-0710KL",
        )
    )
    builder.add(
        passive(
            "R",
            "R11",
            "100k",
            "Resistor_SMD:R_0603_1608Metric",
            462,
            136,
            "BOOT0",
            "GND",
            block,
            (78, 61, 0),
            manufacturer="Yageo",
            mpn="RC0603FR-07100KL",
        )
    )
    for args in (
        ("R14", "330k 1%", 402, 258, "VIN_FILTERED", "VIN_MON", 74, 39),
        ("R15", "33k 1%", 402, 276, "VIN_MON", "GND", 74, 43),
        ("R16", "100k 1%", 430, 258, "5V", "5V_MON", 80, 39),
        ("R17", "200k 1%", 430, 276, "5V_MON", "GND", 80, 43),
        ("R18", "10k 1%", 458, 258, "3V3", "3V3_MON", 86, 39),
        ("R19", "100k 1%", 458, 276, "3V3_MON", "GND", 86, 43),
    ):
        reference, value, x, y, net1, net2, px, py = args
        builder.add(
            passive(
                "R",
                reference,
                value,
                "Resistor_SMD:R_0603_1608Metric",
                x,
                y,
                net1,
                net2,
                block,
                (px, py, 0),
                manufacturer="Yageo",
                mpn="RC0603FR series",
            )
        )
    for index, (rail, x) in enumerate(
        (("3V3_A", 400), ("3V3_RTC", 422)),
        start=20,
    ):
        builder.add(
            spec(
                "power",
                "PWR_FLAG",
                f"#FLG{index}",
                "PWR_FLAG",
                "",
                x,
                300,
                {"1": rail},
                block,
                on_board=False,
                in_bom=False,
                label_length=3.81,
            )
        )
    for reference, value, x, y, net in (
        ("SW1", "RESET", 488, 119, "NRST"),
        ("SW2", "BOOT", 488, 136, "BOOT0"),
    ):
        builder.add(
            spec(
                "Switch",
                "SW_Push",
                reference,
                value,
                "Button_Switch_SMD:SW_SPST_TL3342",
                x,
                y,
                {
                    "1": net,
                    "2": "GND" if reference == "SW1" else "3V3",
                },
                block,
                (111, 47 if reference == "SW1" else 53, 0),
                manufacturer="E-Switch",
                mpn="TL3342F160QG",
            )
        )
    swd_nets = {
        "1": "3V3",
        "2": "SWDIO",
        "3": "GND",
        "4": "SWCLK",
        "5": "GND",
        "6": "SWO",
        "9": "GND",
        "10": "NRST",
    }
    builder.add(
        spec(
            "Connector_Generic",
            "Conn_02x05_Odd_Even",
            "J2",
            "ARM SWD 10-pin",
            "Connector_PinHeader_1.27mm:"
            "PinHeader_2x05_P1.27mm_Vertical_SMD",
            270,
            280,
            swd_nets,
            block,
            (112, 61, 90),
            manufacturer="Samtec",
            mpn="FTSH-105-01-L-DV-K",
        )
    )
    for reference, value, net, color, x, pcb_y in (
        ("D3", "RUN GREEN", "LED_RUN_A", "green", 454, 69),
        ("D4", "FAULT RED", "LED_FAULT_A", "red", 474, 69),
    ):
        builder.add(
            passive(
                "LED",
                reference,
                value,
                "LED_SMD:LED_0603_1608Metric",
                x,
                166,
                net,
                "GND",
                block,
                (111, pcb_y, 0),
                manufacturer="Wurth",
                mpn=f"0603 {color} LED",
            )
        )
    builder.add(
        passive(
            "R",
            "R12",
            "1k",
            "Resistor_SMD:R_0603_1608Metric",
            454,
            150,
            "LED_RUN",
            "LED_RUN_A",
            block,
            (106, 69, 0),
        )
    )
    builder.add(
        passive(
            "R",
            "R13",
            "1k",
            "Resistor_SMD:R_0603_1608Metric",
            474,
            150,
            "LED_FAULT",
            "LED_FAULT_A",
            block,
            (106, 73, 0),
        )
    )
    builder.add(
        connector(
            8,
            "J6",
            "SERVICE / EXPANSION",
            "Connector_PinHeader_2.54mm:"
            "PinHeader_1x08_P2.54mm_Vertical",
            330,
            285,
            [
                "3V3",
                "GND",
                "I2C_SCL",
                "I2C_SDA",
                "EXP_UART_TX",
                "WIFI_UART_RX",
                "EXP_GPIO",
                "NRST",
            ],
            block,
            (117, 72, 0),
        )
    )


def add_storage_service_block(builder: SchematicBuilder) -> None:
    block = "STORAGE_SERVICE"
    builder.note(
        "3 — RTC, FLASH, MICROSD AND USB-C SERVICE",
        430,
        205,
        2.0,
    )
    builder.add(
        spec(
            "Timer_RTC",
            "RV-3028-C7",
            "U4",
            "RV-3028-C7",
            "Package_SON:MicroCrystal_C7_SON-8_1.5x3.2mm_P0.9mm",
            465,
            245,
            {
                "2": "RTC_INT",
                "3": "I2C_SCL",
                "4": "I2C_SDA",
                "5": "GND",
                "6": "3V3_RTC",
                "7": "3V3",
                "8": "GND",
            },
            block,
            (104, 83, 0),
            manufacturer="Micro Crystal",
            mpn="RV-3028-C7",
            datasheet="https://www.microcrystal.com/en/products/real-time-clock-rtc-modules/rv-3028-c7/",
        )
    )
    builder.add(
        passive(
            "Battery_Cell",
            "BT1",
            "CR1220",
            "Battery:BatteryHolder_Keystone_3000_1x12mm",
            440,
            270,
            "3V3_RTC",
            "GND",
            block,
            (121, 88, 0),
            manufacturer="Keystone",
            mpn="3000",
        )
    )
    for args in (
        ("R20", "4.7k", 445, 225, "3V3", "I2C_SCL", 100, 80),
        ("R21", "4.7k", 490, 225, "3V3", "I2C_SDA", 104, 80),
    ):
        reference, value, x, y, net1, net2, px, py = args
        builder.add(
            passive(
                "R",
                reference,
                value,
                "Resistor_SMD:R_0603_1608Metric",
                x,
                y,
                net1,
                net2,
                block,
                (px, py, 0),
                manufacturer="Yageo",
                mpn="RC0603FR series",
            )
        )
    builder.add(
        passive(
            "C",
            "C30",
            "100nF",
            "Capacitor_SMD:C_0603_1608Metric",
            488,
            272,
            "3V3",
            "GND",
            block,
            (108, 83, 0),
        )
    )

    builder.add(
        spec(
            "Memory_Flash",
            "W25Q128JVS",
            "U5",
            "W25Q128JVSIQ",
            "Package_SO:SOIC-8_5.3x5.3mm_P1.27mm",
            525,
            245,
            {
                "1": "FLASH_CS",
                "2": "FLASH_MISO",
                "3": "FLASH_WP",
                "4": "GND",
                "5": "FLASH_MOSI",
                "6": "FLASH_SCK",
                "7": "FLASH_HOLD",
                "8": "3V3",
            },
            block,
            (117, 83, 0),
            manufacturer="Winbond",
            mpn="W25Q128JVSIQ",
            datasheet="https://www.winbond.com/resource-files/w25q128jv%20revf%2003272018%20plus.pdf",
        )
    )
    builder.add(
        passive(
            "C",
            "C31",
            "100nF",
            "Capacitor_SMD:C_0603_1608Metric",
            545,
            270,
            "3V3",
            "GND",
            block,
            (122, 80, 0),
        )
    )
    for reference, net, x, px in (
        ("R27", "FLASH_WP", 510, 115),
        ("R28", "FLASH_HOLD", 530, 119),
    ):
        builder.add(
            passive(
                "R",
                reference,
                "10k",
                "Resistor_SMD:R_0603_1608Metric",
                x,
                275,
                "3V3",
                net,
                block,
                (px, 78, 0),
            )
        )

    builder.add(
        spec(
            "Connector",
            "Micro_SD_Card_Det1",
            "J3",
            "MICROSD INDUSTRIAL",
            "Connector_Card:microSD_HC_Molex_104031-0811",
            585,
            245,
            {
                "1": "SD_D2",
                "2": "SD_D3",
                "3": "SD_CMD",
                "4": "3V3",
                "5": "SD_CLK",
                "6": "GND",
                "7": "SD_D0",
                "8": "SD_D1",
                "9": "SD_DETECT",
                "10": "CHASSIS",
            },
            block,
            (139, 107, 180),
            manufacturer="Molex",
            mpn="104031-0811",
        )
    )
    builder.add(
        passive(
            "R",
            "R22",
            "10k",
            "Resistor_SMD:R_0603_1608Metric",
            567,
            274,
            "3V3",
            "SD_DETECT",
            block,
            (128, 96, 0),
        )
    )

    builder.add(
        spec(
            "Connector",
            "USB_C_Receptacle_USB2.0_16P",
            "J4",
            "USB-C SERVICE DEVICE",
            "Connector_USB:"
            "USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal",
            680,
            245,
            {
                "S1": "CHASSIS",
                "A1": "GND",
                "A12": "GND",
                "B1": "GND",
                "B12": "GND",
                "A4": "USB_VBUS",
                "A9": "USB_VBUS",
                "B4": "USB_VBUS",
                "B9": "USB_VBUS",
                "A5": "USB_CC1",
                "B5": "USB_CC2",
                "A7": "USB_DM_RAW",
                "B7": "USB_DM_RAW",
                "A6": "USB_DP_RAW",
                "B6": "USB_DP_RAW",
            },
            block,
            (128, 8, 0),
            manufacturer="GCT",
            mpn="USB4105-GF-A",
            label_length=5.08,
        )
    )
    builder.add(
        spec(
            "Power_Protection",
            "USBLC6-2SC6",
            "U6",
            "USBLC6-2SC6",
            "Package_TO_SOT_SMD:SOT-23-6",
            635,
            245,
            {
                "1": "USB_DM_RAW",
                "2": "GND",
                "3": "USB_DP_RAW",
                "4": "USB_DP",
                "5": "USB_VBUS",
                "6": "USB_DM",
            },
            block,
            (121, 13, 0),
            manufacturer="STMicroelectronics",
            mpn="USBLC6-2SC6",
        )
    )
    for args in (
        ("R23", "5.1k", 652, 279, "USB_CC1", "GND", 133, 13),
        ("R24", "5.1k", 712, 279, "USB_CC2", "GND", 136, 13),
        ("R25", "100k", 618, 279, "USB_VBUS", "USB_VBUS_SENSE", 117, 10),
        ("R26", "33k", 618, 294, "USB_VBUS_SENSE", "GND", 117, 14),
    ):
        reference, value, x, y, net1, net2, px, py = args
        builder.add(
            passive(
                "R",
                reference,
                value,
                "Resistor_SMD:R_0603_1608Metric",
                x,
                y,
                net1,
                net2,
                block,
                (px, py, 0),
            )
        )
    builder.add(
        passive(
            "C",
            "C32",
            "100nF",
            "Capacitor_SMD:C_0603_1608Metric",
            640,
            294,
            "USB_VBUS_SENSE",
            "GND",
            block,
            (120, 16, 0),
        )
    )


def add_network_block(builder: SchematicBuilder) -> None:
    block = "NETWORK"
    builder.note(
        "4 — ETHERNET 10/100 RMII AND OPTIONAL WI-FI COPROCESSOR",
        500,
        18,
        2.0,
    )
    builder.add(
        spec(
            "Interface_Ethernet",
            "LAN8742A",
            "U7",
            "LAN8742Ai-CZ-TR",
            "Package_DFN_QFN:"
            "VQFN-24-1EP_4x4mm_P0.5mm_EP2.5x2.5mm_ThermalVias",
            595,
            82,
            {
                "1": "3V3_ETH",
                "2": "ETH_LED2",
                "3": "ETH_LED1",
                "4": "ETH_XTAL_OUT",
                "5": "ETH_XTAL_IN",
                "6": "ETH_VDDCR",
                "7": "ETH_RXD1",
                "8": "ETH_RXD0",
                "9": "3V3",
                "11": "ETH_CRS_DV",
                "12": "ETH_MDIO",
                "13": "ETH_MDC",
                "14": "ETH_REF_CLK",
                "15": "ETH_PHY_RESET",
                "16": "ETH_TX_EN",
                "17": "ETH_TXD0",
                "18": "ETH_TXD1",
                "19": "3V3_ETH",
                "20": "ETH_TX_N",
                "21": "ETH_TX_P",
                "22": "ETH_RX_N",
                "23": "ETH_RX_P",
                "24": "ETH_RBIAS",
                "25": "GND",
            },
            block,
            (140, 30, 0),
            manufacturer="Microchip",
            mpn="LAN8742Ai-CZ-TR",
            datasheet="https://ww1.microchip.com/downloads/en/DeviceDoc/8742a.pdf",
        )
    )
    builder.add(
        spec(
            "Connector",
            "RJ45_Hanrun_HR911105A_Horizontal",
            "J5",
            "RJ45 MAGJACK 10/100",
            "Connector_RJ:RJ45_Hanrun_HR911105A_Horizontal",
            680,
            83,
            {
                "1": "ETH_TX_P",
                "2": "ETH_TX_N",
                "3": "ETH_RX_P",
                "4": "3V3_ETH",
                "5": "3V3_ETH",
                "6": "ETH_RX_N",
                "8": "CHASSIS",
                "SH": "CHASSIS",
                "9": "ETH_LED2_K",
                "10": "3V3",
                "11": "ETH_LED1_K",
                "12": "3V3",
            },
            block,
            (168, 25, 90),
            manufacturer="HanRun",
            mpn="HR911105A",
        )
    )
    builder.add(
        passive(
            "Crystal",
            "Y3",
            "25MHz 10pF",
            "Crystal:Crystal_SMD_3215-2Pin_3.2x1.5mm",
            545,
            101,
            "ETH_XTAL_IN",
            "ETH_XTAL_OUT",
            block,
            (128, 29, 0),
            manufacturer="Abracon",
            mpn="ABM8-25.000MHZ series",
        )
    )
    for args in (
        ("C40", "12pF C0G", 530, 115, "ETH_XTAL_IN", "GND", 126, 32),
        ("C41", "12pF C0G", 558, 115, "ETH_XTAL_OUT", "GND", 130, 32),
        ("C42", "1uF", 570, 132, "ETH_VDDCR", "GND", 136, 34),
        ("C43", "100nF", 590, 132, "3V3", "GND", 140, 34),
        ("C44", "100nF", 610, 132, "3V3_ETH", "GND", 144, 34),
        ("C45", "10uF", 630, 132, "3V3_ETH", "GND", 148, 34),
    ):
        reference, value, x, y, net1, net2, px, py = args
        builder.add(
            passive(
                "C",
                reference,
                value,
                "Capacitor_SMD:C_0603_1608Metric",
                x,
                y,
                net1,
                net2,
                block,
                (px, py, 0),
            )
        )
    for args in (
        ("R40", "12.1k 1%", 650, 126, "ETH_RBIAS", "GND", 153, 34),
        ("R41", "49.9R 1%", 620, 48, "3V3_ETH", "ETH_TX_P", 147, 25),
        ("R42", "49.9R 1%", 635, 48, "3V3_ETH", "ETH_TX_N", 151, 25),
        ("R43", "49.9R 1%", 650, 48, "3V3_ETH", "ETH_RX_P", 155, 25),
        ("R44", "49.9R 1%", 665, 48, "3V3_ETH", "ETH_RX_N", 159, 25),
        ("R45", "10k", 555, 50, "3V3", "ETH_PHY_RESET", 132, 24),
        ("R46", "1k", 650, 145, "ETH_LED1", "ETH_LED1_K", 155, 32),
        ("R47", "1k", 670, 145, "ETH_LED2", "ETH_LED2_K", 159, 32),
    ):
        reference, value, x, y, net1, net2, px, py = args
        builder.add(
            passive(
                "R",
                reference,
                value,
                "Resistor_SMD:R_0603_1608Metric",
                x,
                y,
                net1,
                net2,
                block,
                (px, py, 0),
            )
        )
    builder.add(
        passive(
            "FerriteBead",
            "FB2",
            "600R@100MHz",
            "Inductor_SMD:L_0603_1608Metric",
            620,
            150,
            "3V3",
            "3V3_ETH",
            block,
            (136, 26, 0),
            manufacturer="Murata",
            mpn="BLM18AG601SN1D",
        )
    )
    for index, (rail, x) in enumerate(
        (("3V3_ETH", 520), ("ETH_VDDCR", 545)),
        start=30,
    ):
        builder.add(
            spec(
                "power",
                "PWR_FLAG",
                f"#FLG{index}",
                "PWR_FLAG",
                "",
                x,
                190,
                {"1": rail},
                block,
                on_board=False,
                in_bom=False,
                label_length=3.81,
            )
        )

    builder.add(
        spec(
            "RF_Module",
            "ESP32-C3-WROOM-02",
            "U8",
            "ESP32-C3-WROOM-02",
            "RF_Module:ESP32-C3-WROOM-02",
            680,
            165,
            {
                "1": "3V3",
                "2": "WIFI_EN",
                "8": "WIFI_BOOT",
                "9": "GND",
                "11": "WIFI_UART_TX",
                "12": "WIFI_UART_RX",
                "19": "GND",
            },
            block,
            (164, 57, 90),
            manufacturer="Espressif",
            mpn="ESP32-C3-WROOM-02-N4",
            datasheet="https://www.espressif.com/sites/default/files/documentation/esp32-c3-wroom-02_datasheet_en.pdf",
            dnp=True,
            description="Optional Wi-Fi coprocessor; STM32 remains authority",
        )
    )
    for args in (
        ("R48", "10k", 640, 168, "3V3", "WIFI_EN", 150, 52),
        ("R49", "10k", 640, 184, "3V3", "WIFI_BOOT", 150, 56),
    ):
        reference, value, x, y, net1, net2, px, py = args
        builder.add(
            passive(
                "R",
                reference,
                value,
                "Resistor_SMD:R_0603_1608Metric",
                x,
                y,
                net1,
                net2,
                block,
                (px, py, 0),
                dnp=True,
            )
        )
    builder.add(
        passive(
            "C",
            "C46",
            "10uF",
            "Capacitor_SMD:C_0805_2012Metric",
            660,
            195,
            "3V3",
            "GND",
            block,
            (153, 60, 0),
            dnp=True,
        )
    )


def add_analog_block(builder: SchematicBuilder) -> None:
    block = "ANALOG"
    builder.note(
        "5 — FOUR 0–10 V / 4–20 mA ANALOG INPUTS",
        18,
        318,
        2.0,
    )
    for channel, y, board_x in (
        (1, 350, 18),
        (2, 395, 36),
        (3, 440, 54),
        (4, 485, 72),
    ):
        field = f"AI{channel}_FIELD"
        shunt = f"AI{channel}_SHUNT"
        adc = f"AI{channel}_ADC"
        builder.add(
            connector(
                2,
                f"J{9 + channel}",
                f"AI{channel} / AGND",
                "TerminalBlock_Phoenix:"
                "TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_"
                "Horizontal",
                30,
                y,
                [field, "AGND"],
                block,
                (board_x, 112, 0),
                manufacturer="Phoenix Contact",
                mpn="MKDS 1,5/2-5,08",
            )
        )
        builder.add(
            passive(
                "D_TVS",
                f"D{9 + channel}",
                "SMAJ12A",
                "Diode_SMD:D_SMA",
                60,
                y + 14,
                field,
                "AGND",
                block,
                (board_x, 102, 90),
                manufacturer="Littelfuse",
                mpn="SMAJ12A",
            )
        )
        builder.add(
            spec(
                "Jumper",
                "Jumper_2_Open",
                f"JP{channel}",
                f"AI{channel} CURRENT MODE",
                "Jumper:SolderJumper-2_P1.3mm_Open_Pad1.0x1.5mm",
                83,
                y + 17,
                {"1": field, "2": shunt},
                block,
                (board_x + 4, 96, 0),
                description="Close only for 4–20 mA mode",
            )
        )
        builder.add(
            passive(
                "R",
                f"R{58 + 2 * channel}",
                "249R 0.1% 25ppm",
                "Resistor_SMD:R_0805_2012Metric",
                112,
                y + 17,
                shunt,
                "AGND",
                block,
                (board_x + 8, 96, 0),
                manufacturer="Vishay",
                mpn="TNPW0805249RBEEN",
            )
        )
        builder.add(
            passive(
                "R",
                f"R{59 + 2 * channel}",
                "1k 0.1%",
                "Resistor_SMD:R_0603_1608Metric",
                98,
                y - 6,
                field,
                adc,
                block,
                (board_x + 4, 88, 0),
                manufacturer="Vishay",
                mpn="TNPW06031K00BEEA",
            )
        )
        builder.add(
            passive(
                "C",
                f"C{59 + channel}",
                "10nF C0G",
                "Capacitor_SMD:C_0603_1608Metric",
                132,
                y + 4,
                adc,
                "AGND",
                block,
                (board_x + 8, 88, 0),
                manufacturer="TDK",
                mpn="C1608C0G1H103J080AA",
            )
        )

    adc_nets = {
        "1": "ADC_MOSI",
        "2": "ADC_RESET",
        "3": "GND",
        "4": "GND",
        "5": "ADC_REFIO",
        "6": "AGND",
        "7": "ADC_REFCAP",
        "8": "AGND",
        "9": "5V_A",
        "11": "AGND",
        "16": "AI1_ADC",
        "17": "AGND",
        "18": "AI2_ADC",
        "19": "AGND",
        "20": "AGND",
        "21": "AI3_ADC",
        "22": "AGND",
        "23": "AI4_ADC",
        "28": "AGND",
        "29": "AGND",
        "30": "5V_A",
        "31": "AGND",
        "32": "AGND",
        "33": "GND",
        "34": "3V3",
        "36": "ADC_MISO",
        "37": "ADC_SCK",
        "38": "ADC_CS",
    }
    builder.add(
        spec(
            "Analog_ADC",
            "ADS8684",
            "U9",
            "ADS8684IDBT",
            "Package_SO:TSSOP-38_4.4x9.7mm_P0.5mm",
            205,
            418,
            adc_nets,
            block,
            (55, 76, 0),
            manufacturer="Texas Instruments",
            mpn="ADS8684IDBT",
            datasheet="https://www.ti.com/lit/ds/symlink/ads8684.pdf",
            description="4-channel 16-bit 500 kSPS bipolar-input SAR ADC",
        )
    )
    builder.add(
        passive(
            "FerriteBead",
            "FB3",
            "600R@100MHz",
            "Inductor_SMD:L_0603_1608Metric",
            174,
            350,
            "5V",
            "5V_A",
            block,
            (47, 66, 0),
            manufacturer="Murata",
            mpn="BLM18AG601SN1D",
        )
    )
    for args in (
        ("C64", "10uF", 160, 375, "5V_A", "AGND", 48, 72),
        ("C65", "100nF", 177, 375, "5V_A", "AGND", 52, 72),
        ("C66", "10uF low-ESR", 245, 452, "ADC_REFCAP", "AGND", 62, 82),
        ("C67", "10uF low-ESR", 245, 475, "ADC_REFIO", "AGND", 66, 82),
    ):
        reference, value, x, y, net1, net2, px, py = args
        builder.add(
            passive(
                "C",
                reference,
                value,
                "Capacitor_SMD:C_0603_1608Metric",
                x,
                y,
                net1,
                net2,
                block,
                (px, py, 0),
            )
        )
    builder.add(
        spec(
            "power",
            "PWR_FLAG",
            "#FLG40",
            "PWR_FLAG",
            "",
            260,
            350,
            {"1": "5V_A"},
            block,
            on_board=False,
            in_bom=False,
            label_length=3.81,
        )
    )
    builder.add(
        passive(
            "R",
            "R68",
            "0R star link",
            "Resistor_SMD:R_0805_2012Metric",
            192,
            500,
            "AGND",
            "GND",
            block,
            (70, 72, 0),
            description="Single controlled analog/digital ground link",
        )
    )


def add_digital_input_block(builder: SchematicBuilder) -> None:
    block = "DIGITAL_INPUT"
    builder.note(
        "6 — FOUR ISOLATED IEC 61131-2 TYPE 3 DIGITAL INPUTS",
        285,
        318,
        2.0,
    )
    builder.add(
        connector(
            5,
            "J14",
            "DI1 / DI2 / DI3 / DI4 / FIELD COM",
            "TerminalBlock_Phoenix:"
            "TerminalBlock_Phoenix_MKDS-1,5-5-5.08_1x05_P5.08mm_Horizontal",
            310,
            370,
            [
                "DI1_FIELD",
                "DI2_FIELD",
                "DI3_FIELD",
                "DI4_FIELD",
                "DI_FIELD_GND",
            ],
            block,
            (95, 112, 0),
            manufacturer="Phoenix Contact",
            mpn="MKDS 1,5/5-5,08",
        )
    )
    for channel, x, y, px in (
        (1, 340, 350, 78),
        (2, 340, 405, 88),
        (3, 450, 350, 102),
        (4, 450, 405, 112),
    ):
        field = f"DI{channel}_FIELD"
        sense = f"DI{channel}_SENSE"
        input_net = f"DI{channel}_IN"
        builder.add(
            passive(
                "R",
                f"R{78 + 2 * channel}",
                "1.00k 1% RTHR",
                "Resistor_SMD:R_1206_3216Metric",
                x,
                y,
                field,
                sense,
                block,
                (px, 101, 0),
                manufacturer="Yageo",
                mpn="RC1206FR-071KL",
            )
        )
        builder.add(
            passive(
                "R",
                f"R{79 + 2 * channel}",
                "562R 1% RSENSE",
                "Resistor_SMD:R_1206_3216Metric",
                x + 30,
                y,
                sense,
                input_net,
                block,
                (px, 96, 0),
                manufacturer="Yageo",
                mpn="RC1206FR-07562RL",
            )
        )
        builder.add(
            passive(
                "C",
                f"C{79 + channel}",
                "10nF 100V",
                "Capacitor_SMD:C_1206_3216Metric",
                x + 15,
                y + 19,
                sense,
                "DI_FIELD_GND",
                block,
                (px + 4, 101, 90),
                manufacturer="TDK",
                mpn="C3216X7R2A103K160AA",
            )
        )
        builder.add(
            passive(
                "D_TVS",
                f"D{13 + channel}",
                "SMAJ33A",
                "Diode_SMD:D_SMA",
                x - 12,
                y + 19,
                field,
                "DI_FIELD_GND",
                block,
                (px - 4, 103, 90),
                manufacturer="Littelfuse",
                mpn="SMAJ33A",
            )
        )

    for index, x, px in ((1, 405, 83), (2, 515, 107)):
        channel_a = 1 if index == 1 else 3
        channel_b = channel_a + 1
        builder.add(
            spec(
                "Isolator",
                "ISO1212",
                f"U{9 + index}",
                "ISO1212DBQ",
                "Package_SO:SSOP-16_3.9x4.9mm_P0.635mm",
                x,
                450,
                {
                    "1": "GND",
                    "2": "3V3",
                    "3": "3V3",
                    "4": f"DI{channel_a}",
                    "5": f"DI{channel_b}",
                    "8": "GND",
                    "9": "DI_FIELD_GND",
                    "10": f"DI{channel_b}_IN",
                    "11": f"DI{channel_b}_SENSE",
                    "12": "DI_FIELD_GND",
                    "13": "DI_FIELD_GND",
                    "14": "DI_FIELD_GND",
                    "15": f"DI{channel_a}_IN",
                    "16": f"DI{channel_a}_SENSE",
                },
                block,
                (px, 88, 0),
                manufacturer="Texas Instruments",
                mpn="ISO1212DBQ",
                datasheet="https://www.ti.com/lit/ds/symlink/iso1212.pdf",
            )
        )
        builder.add(
            passive(
                "C",
                f"C{83 + index}",
                "100nF",
                "Capacitor_SMD:C_0603_1608Metric",
                x,
                490,
                "3V3",
                "GND",
                block,
                (px + 5, 88, 0),
            )
        )
    builder.add(
        spec(
            "power",
            "PWR_FLAG",
            "#FLG50",
            "PWR_FLAG",
            "",
            545,
            510,
            {"1": "DI_FIELD_GND"},
            block,
            on_board=False,
            in_bom=False,
            label_length=3.81,
        )
    )


def add_isolated_bus_block(builder: SchematicBuilder) -> None:
    block = "ISOLATED_BUSES"
    builder.note(
        "7 — TWO ISOLATED RS-485 PORTS AND ISOLATED CAN-FD",
        555,
        318,
        2.0,
    )
    for port, x, pcb_x, terminal_ref, unit_ref in (
        ("A", 605, 128, "J15", "U12"),
        ("B", 700, 150, "J16", "U13"),
    ):
        prefix = f"RS485{port}"
        field_ground = f"{prefix}_GND"
        viso = f"{prefix}_VISO"
        plus = f"{prefix}_P"
        minus = f"{prefix}_N"
        builder.add(
            spec(
                "EDGE18",
                "ISOW1412",
                unit_ref,
                "ISOW1412DFMR",
                "Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm",
                x,
                390,
                {
                    "1": "3V3",
                    "2": f"{prefix}_TX",
                    "3": f"{prefix}_DIR",
                    "4": f"{prefix}_RX",
                    "5": f"{prefix}_DIR",
                    "6": "GND",
                    "8": f"{prefix}_EN",
                    "9": "5V",
                    "10": "GND",
                    "11": field_ground,
                    "12": viso,
                    "13": field_ground,
                    "15": field_ground,
                    "16": viso,
                    "17": plus,
                    "18": minus,
                    "19": minus,
                    "20": plus,
                },
                block,
                (pcb_x, 91, 0),
                manufacturer="Texas Instruments",
                mpn="ISOW1412DFMR",
                datasheet="https://www.ti.com/lit/ds/symlink/isow1412.pdf",
            )
        )
        builder.add(
            connector(
                3,
                terminal_ref,
                f"RS-485 {port}: A+ / B- / ISO GND",
                "TerminalBlock_Phoenix:"
                "TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_"
                "Horizontal",
                x + 43,
                390,
                [plus, minus, field_ground],
                block,
                (pcb_x + 4, 112, 0),
                manufacturer="Phoenix Contact",
                mpn="MKDS 1,5/3-5,08",
            )
        )
        builder.add(
            spec(
                "Diode",
                "SM712_SOT23",
                f"D{18 if port == 'A' else 19}",
                "SM712",
                "Package_TO_SOT_SMD:SOT-23",
                x + 42,
                430,
                {"1": plus, "2": minus, "3": field_ground},
                block,
                (pcb_x + 4, 102, 0),
                manufacturer="Littelfuse",
                mpn="SM712-02HTG",
            )
        )
        builder.add(
            spec(
                "Jumper",
                "Jumper_2_Open",
                f"JP{5 if port == 'A' else 6}",
                "120R TERMINATION ENABLE",
                "Jumper:SolderJumper-2_P1.3mm_Open_Pad1.0x1.5mm",
                x,
                447,
                {"1": plus, "2": f"{prefix}_TERM"},
                block,
                (pcb_x - 4, 103, 0),
            )
        )
        builder.add(
            passive(
                "R",
                f"R{90 if port == 'A' else 92}",
                "120R 1%",
                "Resistor_SMD:R_1206_3216Metric",
                x + 29,
                447,
                f"{prefix}_TERM",
                minus,
                block,
                (pcb_x, 103, 0),
            )
        )
        builder.add(
            passive(
                "R",
                f"R{91 if port == 'A' else 93}",
                "10k",
                "Resistor_SMD:R_0603_1608Metric",
                x - 35,
                355,
                "3V3",
                f"{prefix}_EN",
                block,
                (pcb_x - 5, 82, 0),
            )
        )
        builder.add(
            passive(
                "C",
                f"C{90 if port == 'A' else 92}",
                "100nF",
                "Capacitor_SMD:C_0603_1608Metric",
                x - 26,
                470,
                "3V3",
                "GND",
                block,
                (pcb_x - 5, 87, 0),
            )
        )
        builder.add(
            passive(
                "C",
                f"C{91 if port == 'A' else 93}",
                "2.2uF 10V",
                "Capacitor_SMD:C_0805_2012Metric",
                x + 20,
                470,
                viso,
                field_ground,
                block,
                (pcb_x + 5, 96, 0),
            )
        )

    builder.add(
        spec(
            "Interface_CAN_LIN",
            "ISOW1044",
            "U14",
            "ISOW1044DFMR",
            "Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm",
            790,
            390,
            {
                "1": "3V3",
                "2": "GND",
                "3": "CAN_TX",
                "4": "CAN_STB",
                "5": "CAN_RX",
                "6": "GND",
                "8": "CAN_EN",
                "9": "5V",
                "10": "GND",
                "11": "CAN_GND",
                "12": "CAN_VISO",
                "13": "CAN_VISO",
                "15": "CAN_GND",
                "16": "CAN_GND",
                "17": "CAN_GND",
                "18": "CAN_L",
                "19": "CAN_H",
                "20": "CAN_VISO",
            },
            block,
            (169, 91, 0),
            manufacturer="Texas Instruments",
            mpn="ISOW1044DFMR",
            datasheet="https://www.ti.com/lit/ds/symlink/isow1044.pdf",
            description="Isolated CAN-FD transceiver with integrated power",
        )
    )
    builder.add(
        connector(
            3,
            "J17",
            "CAN-H / CAN-L / ISO GND",
            "TerminalBlock_Phoenix:"
            "TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal",
            835,
            390,
            ["CAN_H", "CAN_L", "CAN_GND"],
            block,
            (169, 112, 0),
            manufacturer="Phoenix Contact",
            mpn="MKDS 1,5/3-5,08",
        )
    )
    builder.add(
        spec(
            "Diode",
            "SM712_SOT23",
            "D20",
            "SM712",
            "Package_TO_SOT_SMD:SOT-23",
            835,
            430,
            {"1": "CAN_H", "2": "CAN_L", "3": "CAN_GND"},
            block,
            (169, 102, 0),
            manufacturer="Littelfuse",
            mpn="SM712-02HTG",
        )
    )
    builder.add(
        spec(
            "Jumper",
            "Jumper_2_Open",
            "JP7",
            "CAN 120R TERMINATION",
            "Jumper:SolderJumper-2_P1.3mm_Open_Pad1.0x1.5mm",
            770,
            448,
            {"1": "CAN_H", "2": "CAN_TERM"},
            block,
            (164, 103, 0),
        )
    )
    builder.add(
        passive(
            "R",
            "R94",
            "120R 1%",
            "Resistor_SMD:R_1206_3216Metric",
            805,
            448,
            "CAN_TERM",
            "CAN_L",
            block,
            (169, 103, 0),
        )
    )
    builder.add(
        passive(
            "R",
            "R95",
            "10k",
            "Resistor_SMD:R_0603_1608Metric",
            760,
            355,
            "3V3",
            "CAN_EN",
            block,
            (163, 82, 0),
        )
    )
    for reference, value, n1, n2, x, px, py in (
        ("C94", "100nF", "3V3", "GND", 760, 164, 87),
        ("C95", "2.2uF", "CAN_VISO", "CAN_GND", 815, 174, 96),
    ):
        builder.add(
            passive(
                "C",
                reference,
                value,
                "Capacitor_SMD:C_0805_2012Metric",
                x,
                475,
                n1,
                n2,
                block,
                (px, py, 0),
            )
        )
    for index, (rail, x) in enumerate(
        (("RS485A_GND", 585), ("RS485B_GND", 685)),
        start=60,
    ):
        builder.add(
            spec(
                "power",
                "PWR_FLAG",
                f"#FLG{index}",
                "PWR_FLAG",
                "",
                x,
                515,
                {"1": rail},
                block,
                on_board=False,
                in_bom=False,
                label_length=3.81,
            )
        )


def build_schematic(path: Path | None) -> SchematicBuilder:
    builder = SchematicBuilder()
    add_power_block(builder)
    add_controller_block(builder)
    add_storage_service_block(builder)
    add_network_block(builder)
    add_analog_block(builder)
    add_digital_input_block(builder)
    add_isolated_bus_block(builder)
    builder.note(
        "DESIGN LIMITS: monitoring only; no safety outputs; "
        "close current-mode jumpers only for 4–20 mA.",
        18,
        540,
        1.5,
    )
    builder.note(
        "Isolation barriers and chassis bonding must be reviewed against the "
        "installation category before field deployment.",
        18,
        550,
        1.5,
    )
    if path is not None:
        builder.write(path)
    return builder


class BoardBuilder:
    def __init__(self) -> None:
        self.width = 180.0
        self.height = 120.0
        self.board = pcbnew.BOARD()
        self.board.SetCopperLayerCount(4)
        self.nets: dict[str, pcbnew.NETINFO_ITEM] = {}
        self.footprints: dict[str, pcbnew.FOOTPRINT] = {}
        settings = self.board.GetDesignSettings()
        settings.m_TrackMinWidth = pcbnew.FromMM(0.25)
        settings.m_MinClearance = pcbnew.FromMM(0.18)
        settings.m_CopperEdgeClearance = pcbnew.FromMM(0.50)
        settings.m_HoleClearance = pcbnew.FromMM(0.18)
        settings.m_ViasMinSize = pcbnew.FromMM(0.70)
        # Exposed pads on the regulators/PHY use the manufacturer's 0.20 mm
        # thermal-via pattern. Signal and routing vias remain at least 0.35 mm.
        settings.m_MinThroughDrill = pcbnew.FromMM(0.20)
        self._configure_netclasses()
        self._outline()
        self.text(
            "EDGE-18 INDUSTRIAL GATEWAY",
            90,
            5,
            pcbnew.F_SilkS,
            1.8,
        )
        self.text(
            "REV A • 9–36 VDC • MONITORING ONLY",
            90,
            116,
            pcbnew.B_SilkS,
            1.35,
        )
        self.text(
            "POWER",
            42,
            9,
            pcbnew.F_SilkS,
            1.1,
        )
        self.text(
            "ANALOG INPUTS",
            45,
            108,
            pcbnew.B_SilkS,
            1.1,
        )
        self.text(
            "ISOLATED FIELD I/O",
            145,
            79,
            pcbnew.F_SilkS,
            1.1,
        )

    def _configure_netclasses(self) -> None:
        net_settings = self.board.GetDesignSettings().m_NetSettings
        classes = {
            "Default": (0.18, 0.30, 0.80, 0.40),
            "POWER": (0.18, 0.80, 1.20, 0.60),
            "VIN": (0.18, 1.20, 1.60, 0.80),
            "ANALOG": (0.18, 0.35, 0.90, 0.45),
            "FIELD": (0.18, 0.50, 1.00, 0.50),
            "HIGHSPEED": (0.18, 0.25, 0.70, 0.35),
        }
        for name, (clearance, width, via, drill) in classes.items():
            item = pcbnew.NETCLASS(name)
            item.SetClearance(pcbnew.FromMM(clearance))
            item.SetTrackWidth(pcbnew.FromMM(width))
            item.SetViaDiameter(pcbnew.FromMM(via))
            item.SetViaDrill(pcbnew.FromMM(drill))
            if name == "HIGHSPEED":
                item.SetDiffPairWidth(pcbnew.FromMM(0.25))
                item.SetDiffPairGap(pcbnew.FromMM(0.20))
            if name == "Default":
                net_settings.SetDefaultNetclass(item)
            else:
                net_settings.SetNetclass(name, item)

    def assign_netclass(self, net_name: str) -> None:
        if net_name.startswith(("VIN_", "SW_5V", "BOOT_5V")):
            class_name = "VIN"
        elif net_name in {
            "3V3",
            "3V3_A",
            "3V3_ETH",
            "3V3_RTC",
            "5V",
            "5V_A",
            "GND",
            "PGOOD_3V3",
            "PGOOD_5V",
        } or net_name.startswith(("VCAP", "SW_3V3")):
            class_name = "POWER"
        elif net_name.startswith(("AI", "ADC_", "AGND")):
            class_name = "ANALOG"
        elif net_name.startswith(
            (
                "DI_FIELD",
                "DI1_FIELD",
                "DI2_FIELD",
                "DI3_FIELD",
                "DI4_FIELD",
                "RS485",
                "CAN_",
            )
        ):
            class_name = "FIELD"
        elif net_name.startswith(("ETH_", "USB_", "SD_", "FLASH_")):
            class_name = "HIGHSPEED"
        else:
            return
        labels = pcbnew.STRINGSET()
        labels.add(class_name)
        self.board.GetDesignSettings().m_NetSettings.SetNetclassLabelAssignment(
            net_name,
            labels,
        )

    def _outline(self) -> None:
        corners = (
            (0.0, 0.0),
            (self.width, 0.0),
            (self.width, self.height),
            (0.0, self.height),
        )
        for start, end in zip(corners, corners[1:] + corners[:1]):
            shape = pcbnew.PCB_SHAPE(self.board)
            shape.SetShape(pcbnew.SHAPE_T_SEGMENT)
            shape.SetStart(pcbnew.VECTOR2I_MM(*start))
            shape.SetEnd(pcbnew.VECTOR2I_MM(*end))
            shape.SetWidth(pcbnew.FromMM(0.25))
            shape.SetLayer(pcbnew.Edge_Cuts)
            self.board.Add(shape)

    def isolation_slot(
        self,
        center_x: float,
        center_y: float,
        length: float = 8.0,
        width: float = 1.0,
    ) -> None:
        left = center_x - width / 2.0
        right = center_x + width / 2.0
        top = center_y - length / 2.0
        bottom = center_y + length / 2.0
        # A native rectangle is one closed Edge.Cuts primitive. Four separate
        # segments can be treated as an open outline by the Specctra exporter.
        shape = pcbnew.PCB_SHAPE(self.board)
        shape.SetShape(pcbnew.SHAPE_T_RECT)
        shape.SetStart(pcbnew.VECTOR2I_MM(left, top))
        shape.SetEnd(pcbnew.VECTOR2I_MM(right, bottom))
        shape.SetWidth(pcbnew.FromMM(0.15))
        shape.SetLayer(pcbnew.Edge_Cuts)
        self.board.Add(shape)

    def text(
        self,
        content: str,
        x: float,
        y: float,
        layer: int,
        size: float,
    ) -> None:
        text = pcbnew.PCB_TEXT(self.board)
        text.SetText(content)
        text.SetPosition(pcbnew.VECTOR2I_MM(x, y))
        text.SetLayer(layer)
        text.SetTextSize(pcbnew.VECTOR2I_MM(size, size))
        text.SetTextThickness(pcbnew.FromMM(max(0.18, size / 6.0)))
        text.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
        if layer == pcbnew.B_SilkS:
            text.SetMirrored(True)
        self.board.Add(text)

    def net(self, name: str) -> pcbnew.NETINFO_ITEM:
        if name not in self.nets:
            item = pcbnew.NETINFO_ITEM(self.board, name)
            self.board.Add(item)
            self.nets[name] = item
            self.assign_netclass(name)
        return self.nets[name]

    @staticmethod
    def _footprint_parts(identifier: str) -> tuple[str, str]:
        if ":" not in identifier:
            raise ValueError(f"invalid footprint identifier {identifier!r}")
        library, entry = identifier.split(":", 1)
        return library, entry

    def add(self, item: SymbolSpec) -> None:
        if not item.on_board or not item.footprint:
            return
        if item.pcb_x is None or item.pcb_y is None:
            raise ValueError(f"missing PCB placement for {item.reference}")
        library, entry = self._footprint_parts(item.footprint)
        library_path = FOOTPRINT_DIR / f"{library}.pretty"
        footprint = pcbnew.FootprintLoad(str(library_path), entry)
        if footprint is None:
            raise FileNotFoundError(f"footprint {item.footprint}")
        footprint.SetReference(item.reference)
        footprint.SetValue(item.value)
        footprint.SetPosition(
            pcbnew.VECTOR2I_MM(item.pcb_x, item.pcb_y)
        )
        footprint.SetOrientationDegrees(item.pcb_rotation)
        if item.dnp and hasattr(footprint, "SetDNP"):
            footprint.SetDNP(True)
        # Reference-to-part mapping is carried by the BOM and fabrication
        # drawing. Hiding the footprint property on production silk prevents
        # dense designators from colliding with pads and block labels.
        footprint.Reference().SetVisible(False)
        self.board.Add(footprint)
        for pad in footprint.Pads():
            net_name = item.nets.get(str(pad.GetNumber()))
            if net_name:
                pad.SetNet(self.net(net_name))
        self.footprints[item.reference] = footprint

    @staticmethod
    def _courtyard_rect(
        footprint: pcbnew.FOOTPRINT,
    ) -> tuple[float, float, float, float]:
        footprint.BuildCourtyardCaches()
        courtyard = footprint.GetCourtyard(pcbnew.F_CrtYd)
        box = courtyard.BBox()
        if courtyard.OutlineCount() == 0:
            box = footprint.GetBoundingBox()
        return (
            pcbnew.ToMM(box.GetLeft()),
            pcbnew.ToMM(box.GetTop()),
            pcbnew.ToMM(box.GetRight()),
            pcbnew.ToMM(box.GetBottom()),
        )

    @staticmethod
    def _rectangles_intersect(
        left: tuple[float, float, float, float],
        right: tuple[float, float, float, float],
        gap: float = 0.30,
    ) -> bool:
        return not (
            left[2] + gap <= right[0]
            or right[2] + gap <= left[0]
            or left[3] + gap <= right[1]
            or right[3] + gap <= left[1]
        )

    def optimize_placement(self) -> None:
        """Resolve courtyard collisions while preserving functional regions."""

        overrides = {
            "J1": (16, 20, 90),
            "D2": (28, 20, 0),
            "L1": (42, 20, 0),
            "U1": (57, 20, 0),
            "L2": (70, 20, 0),
            "U2": (87, 20, 0),
            "L3": (99, 20, 0),
            "J6": (111, 24, 0),
            "J4": (128, 8, 0),
            "BT1": (126, 38, 0),
            "U7": (145, 30, 0),
            "J5": (164, 16, 0),
            "U3": (91, 58, 0),
            "J2": (115, 58, 0),
            "SW1": (111, 49, 0),
            "SW2": (121, 49, 0),
            "J3": (139, 58, 0),
            "U8": (165, 55, 0),
            "U9": (55, 76, 0),
            "U10": (83, 88, 0),
            "U11": (107, 88, 0),
            "U12": (127, 90, 0),
            "U13": (149, 90, 0),
            "U14": (165, 87, 0),
            "J10": (16, 112, 0),
            "J11": (34, 112, 0),
            "J12": (52, 112, 0),
            "J13": (70, 112, 0),
            "J14": (94, 112, 0),
            "J15": (123, 112, 0),
            "J16": (150, 112, 0),
            "J17": (173, 108, 90),
        }
        for reference, (x, y, rotation) in overrides.items():
            footprint = self.footprints[reference]
            footprint.SetOrientationDegrees(rotation)
            footprint.SetPosition(pcbnew.VECTOR2I_MM(x, y))

        fixed_references = set(overrides)
        fixed_references.update({"H1", "H3", "H4", "H6"})
        obstacles: list[tuple[str, tuple[float, float, float, float]]] = [
            ("SLOT_A", (126.0, 84.5, 128.0, 95.5)),
            ("SLOT_B", (148.0, 84.5, 150.0, 95.5)),
            ("SLOT_CAN", (164.0, 81.5, 166.0, 92.5)),
        ]

        for reference in sorted(fixed_references):
            footprint = self.footprints.get(reference)
            if footprint is None:
                continue
            rectangle = self._courtyard_rect(footprint)
            for other_reference, other_rectangle in obstacles:
                # The machined slot intentionally passes under the reinforced
                # isolation barrier, never under package pins.
                if (
                    reference in {"U12", "U13", "U14"}
                    and other_reference.startswith("SLOT")
                ):
                    continue
                if self._rectangles_intersect(rectangle, other_rectangle):
                    raise RuntimeError(
                        "fixed placement collision: "
                        f"{reference} with {other_reference}"
                    )
            obstacles.append((reference, rectangle))

        # Reserve a real escape annulus around the fine-pitch controller,
        # Ethernet PHY and ADC. Decouplers remain nearby, but no movable
        # footprint may occupy the staggered via rows used below.
        obstacles.extend(
            (
                ("U3_ESCAPE", (68.0, 38.0, 114.0, 78.0)),
                ("U7_ESCAPE", (137.5, 22.5, 152.5, 37.5)),
                ("U9_ESCAPE", (46.0, 65.0, 64.0, 87.0)),
            )
        )

        movable = [
            footprint
            for reference, footprint in self.footprints.items()
            if reference not in fixed_references
        ]

        def courtyard_area(footprint: pcbnew.FOOTPRINT) -> float:
            rectangle = self._courtyard_rect(footprint)
            return (
                (rectangle[2] - rectangle[0])
                * (rectangle[3] - rectangle[1])
            )

        movable.sort(
            key=lambda footprint: (
                -courtyard_area(footprint),
                footprint.GetReference(),
            )
        )

        candidates = [(0, 0)]
        for radius in range(1, 46):
            candidates.extend(
                (dx, dy)
                for dx in range(-radius, radius + 1)
                for dy in range(-radius, radius + 1)
                if max(abs(dx), abs(dy)) == radius
            )

        for footprint in movable:
            reference = footprint.GetReference()
            origin = footprint.GetPosition()
            origin_x = pcbnew.ToMM(origin.x)
            origin_y = pcbnew.ToMM(origin.y)
            initial = self._courtyard_rect(footprint)
            relative = (
                initial[0] - origin_x,
                initial[1] - origin_y,
                initial[2] - origin_x,
                initial[3] - origin_y,
            )
            selected: tuple[float, float] | None = None

            for dx, dy in candidates:
                x = origin_x + dx
                y = origin_y + dy
                rectangle = (
                    x + relative[0],
                    y + relative[1],
                    x + relative[2],
                    y + relative[3],
                )
                if (
                    rectangle[0] < 2.0
                    or rectangle[1] < 2.0
                    or rectangle[2] > self.width - 2.0
                    or rectangle[3] > self.height - 2.0
                ):
                    continue
                if any(
                    self._rectangles_intersect(rectangle, occupied)
                    for _, occupied in obstacles
                ):
                    continue
                selected = (x, y)
                obstacles.append((reference, rectangle))
                break
            if selected is None:
                raise RuntimeError(
                    f"no collision-free placement for {reference}"
                )
            footprint.SetPosition(pcbnew.VECTOR2I_MM(*selected))

    def mounting_hole(self, reference: str, x: float, y: float) -> None:
        footprint = pcbnew.FootprintLoad(
            str(FOOTPRINT_DIR / "MountingHole.pretty"),
            "MountingHole_3.2mm_M3",
        )
        if footprint is None:
            raise FileNotFoundError("MountingHole_3.2mm_M3")
        footprint.SetReference(reference)
        footprint.SetPosition(pcbnew.VECTOR2I_MM(x, y))
        footprint.Reference().SetVisible(False)
        self.board.Add(footprint)
        self.footprints[reference] = footprint

    def zone(
        self,
        net_name: str,
        layer: int,
        polygon: list[tuple[float, float]],
        clearance_mm: float,
        priority: int,
    ) -> None:
        zone = pcbnew.ZONE(self.board)
        zone.SetLayer(layer)
        zone.SetNet(self.net(net_name))
        zone.SetLocalClearance(pcbnew.FromMM(clearance_mm))
        zone.SetMinThickness(pcbnew.FromMM(0.20))
        zone.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        zone.SetAssignedPriority(priority)
        outline = zone.Outline()
        outline.NewOutline()
        for x, y in polygon:
            outline.Append(pcbnew.VECTOR2I_MM(x, y))
        outline.Append(pcbnew.VECTOR2I_MM(*polygon[0]))
        self.board.Add(zone)

    def write(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        pcbnew.SaveBoard(str(path), self.board)
        board_text = path.read_text(encoding="utf-8")
        board_text = board_text.replace(
            '\t(paper "A4")',
            '\t(paper "A3")',
            1,
        )
        path.write_text(board_text, encoding="utf-8")


def build_board(
    schematic: SchematicBuilder,
    path: Path,
) -> BoardBuilder:
    board = BoardBuilder()
    for item in schematic.specs:
        board.add(item)
    for reference, x, y in (
        ("H1", 5, 5),
        ("H3", 175, 5),
        ("H4", 5, 115),
        ("H6", 175, 115),
    ):
        board.mounting_hole(reference, x, y)
    board.optimize_placement()
    for x, y in ((127, 90), (149, 90), (165, 87)):
        board.isolation_slot(x, y, length=9.0, width=1.2)
    board.zone(
        "GND",
        pcbnew.In1_Cu,
        [(2, 2), (122, 2), (122, 106), (2, 106)],
        0.25,
        1,
    )
    board.zone(
        "3V3",
        pcbnew.In2_Cu,
        [(55, 38), (121, 38), (121, 80), (55, 80)],
        0.30,
        1,
    )
    board.zone(
        "AGND",
        pcbnew.B_Cu,
        [(8, 64), (74, 64), (74, 105), (8, 105)],
        0.30,
        2,
    )
    board.write(path)
    return board


def project_json() -> dict:
    base_class = {
        "bus_width": 12,
        "clearance": 0.18,
        "diff_pair_gap": 0.20,
        "diff_pair_via_gap": 0.25,
        "diff_pair_width": 0.25,
        "line_style": 0,
        "microvia_diameter": 0.30,
        "microvia_drill": 0.10,
        "pcb_color": "rgba(0, 0, 0, 0.000)",
        "schematic_color": "rgba(0, 0, 0, 0.000)",
        "track_width": 0.30,
        "via_diameter": 0.80,
        "via_drill": 0.40,
        "wire_width": 6,
    }
    class_values = {
        "Default": (0.18, 0.30, 0.80, 0.40),
        "POWER": (0.18, 0.80, 1.20, 0.60),
        "VIN": (0.18, 1.20, 1.60, 0.80),
        "ANALOG": (0.18, 0.35, 0.90, 0.45),
        "FIELD": (0.18, 0.50, 1.00, 0.50),
        "HIGHSPEED": (0.18, 0.25, 0.70, 0.35),
    }
    classes = []
    for name, (clearance, width, via, drill) in class_values.items():
        classes.append(
            {
                **base_class,
                "name": name,
                "clearance": clearance,
                "track_width": width,
                "via_diameter": via,
                "via_drill": drill,
            }
        )
    return {
        "board": {},
        "boards": [],
        "cvpcb": {},
        "erc": {},
        "libraries": {},
        "meta": {"filename": f"{OUTPUT_STEM}.kicad_pro", "version": 1},
        "net_settings": {
            "classes": classes,
            "meta": {"version": 3},
            "net_colors": None,
            "netclass_assignments": None,
            "netclass_patterns": [],
        },
        "pcbnew": {},
        "schematic": {},
        "sheets": [],
        "text_variables": {
            "PROJECT": "EDGE-18",
            "REVISION": "A",
            "STATUS": "DIGITAL DESIGN RELEASE",
        },
    }


def write_project() -> None:
    KICAD_DIR.mkdir(parents=True, exist_ok=True)
    path = KICAD_DIR / f"{OUTPUT_STEM}.kicad_pro"
    path.write_text(
        json.dumps(project_json(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_bom_source(items: list[SymbolSpec]) -> None:
    output = HARDWARE / "bom/edge18-main-rev-a-source.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            (
                "Reference",
                "Value",
                "Footprint",
                "Manufacturer",
                "MPN",
                "Block",
                "DNP",
                "Description",
            )
        )
        for item in sorted(items, key=lambda current: current.reference):
            if not item.in_bom:
                continue
            manufacturer = item.manufacturer
            mpn = item.mpn
            description = item.description
            capacitor_mpn = {
                "100nF": "C1608X7R1H104K080AA",
                "12pF C0G": "C1608C0G1H120J080AA",
                "1uF": "C1608X7R1E105K080AC",
                "10uF": "C1608X5R1A106M080AC",
                "10uF low-ESR": "C1608X5R1A106M080AC",
                "2.2uF 10V": "C2012X7R1A225K125AC",
                "2.2uF": "C2012X7R1A225K125AC",
            }
            resistor_mpn = {
                "0R star link": "RC0805JR-070RL",
                "49.9R 1%": "RC0603FR-0749R9L",
                "120R 1%": "RC1206FR-07120RL",
                "1k": "RC0603FR-071KL",
                "5.1k": "RC0603FR-075K1L",
                "10k": "RC0603FR-0710KL",
                "12.1k 1%": "RC0603FR-0712K1L",
                "33k": "RC0603FR-0733KL",
                "100k": "RC0603FR-07100KL",
            }
            if not manufacturer and item.reference.startswith("C"):
                manufacturer = "TDK"
                mpn = capacitor_mpn.get(
                    item.value,
                    "C1608/C2012 industrial series",
                )
                description = description or "MLCC; verify voltage derating"
            elif not manufacturer and item.reference.startswith("R"):
                manufacturer = "Yageo"
                mpn = resistor_mpn.get(item.value, "RC series")
                description = description or "Thick-film resistor"
            elif item.reference.startswith("JP"):
                manufacturer = "PCB feature"
                mpn = "N/A"
                description = description or "Solder-selectable jumper"
            elif item.reference == "J6":
                manufacturer = "Würth Elektronik"
                mpn = "61300811121"
                description = "1x8 vertical 2.54 mm service header"
            writer.writerow(
                (
                    item.reference,
                    item.value,
                    item.footprint,
                    manufacturer,
                    mpn,
                    item.block,
                    "yes" if item.dnp else "no",
                    description,
                )
            )


def write_frozen_symbol_libraries(schematic: SchematicBuilder) -> None:
    """Freeze the resolved KiCad symbols used by this revision.

    This removes dependence on future global-library changes and lets ERC
    compare the schematic cache against byte-equivalent project libraries.
    """
    output = LIBRARY_DIR / "frozen"
    output.mkdir(parents=True, exist_ok=True)
    grouped: dict[str, list] = {}
    for embedded in schematic.sch.libSymbols:
        library, entry = embedded.libId.split(":", 1)
        symbol = copy.deepcopy(embedded)
        symbol.libId = entry
        symbol.entryName = entry
        symbol.libraryNickname = None
        grouped.setdefault(library, []).append(symbol)
    for library, symbols in grouped.items():
        SymbolLib(
            version="20231120",
            generator="edge18",
            symbols=symbols,
        ).to_file(
            str(output / f"{library}.kicad_sym"),
            encoding="utf-8",
        )


def write_library_tables(items: list[SymbolSpec]) -> None:
    symbol_libraries = sorted({item.library for item in items})
    symbol_lines = ["(sym_lib_table", "  (version 7)"]
    for library in symbol_libraries:
        uri = f"${{KIPRJMOD}}/../libraries/frozen/{library}.kicad_sym"
        symbol_lines.append(
            f'  (lib (name "{library}")(type "KiCad")'
            f'(uri "{uri}")(options "")(descr ""))'
        )
    symbol_lines.append(")")
    (KICAD_DIR / "sym-lib-table").write_text(
        "\n".join(symbol_lines) + "\n",
        encoding="utf-8",
    )

    footprint_libraries = sorted(
        {
            item.footprint.split(":", 1)[0]
            for item in items
            if item.on_board and item.footprint
        }
        | {"MountingHole"}
    )
    footprint_lines = ["(fp_lib_table", "  (version 7)"]
    for library in footprint_libraries:
        footprint_lines.append(
            f'  (lib (name "{library}")(type "KiCad")'
            f'(uri "${{KICAD9_FOOTPRINT_DIR}}/{library}.pretty")'
            '(options "")(descr ""))'
        )
    footprint_lines.append(")")
    (KICAD_DIR / "fp-lib-table").write_text(
        "\n".join(footprint_lines) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--bom-only",
        action="store_true",
        help="refresh only the source BOM without replacing native CAD",
    )
    parser.add_argument(
        "--schematic-only",
        action="store_true",
        help="refresh schematic/BOM/libraries without replacing the PCB",
    )
    args = parser.parse_args()
    if args.bom_only and args.schematic_only:
        parser.error("--bom-only and --schematic-only are mutually exclusive")

    write_custom_symbols()
    if args.bom_only:
        schematic = build_schematic(None)
        write_bom_source(schematic.specs)
        print(f"Generated BOM from {len(schematic.specs)} schematic symbols")
        return 0
    if args.schematic_only:
        write_project()
        schematic = build_schematic(
            KICAD_DIR / f"{OUTPUT_STEM}.kicad_sch"
        )
        write_bom_source(schematic.specs)
        write_frozen_symbol_libraries(schematic)
        write_library_tables(schematic.specs)
        print(
            f"Generated schematic with {len(schematic.specs)} symbols "
            "without replacing the PCB"
        )
        return 0
    write_project()
    schematic = build_schematic(
        KICAD_DIR / f"{OUTPUT_STEM}.kicad_sch"
    )
    build_board(
        schematic,
        KICAD_DIR / f"{OUTPUT_STEM}.kicad_pcb",
    )
    write_bom_source(schematic.specs)
    write_frozen_symbol_libraries(schematic)
    write_library_tables(schematic.specs)
    print(
        f"Generated {len(schematic.specs)} schematic symbols and "
        f"{sum(1 for item in schematic.specs if item.on_board)} PCB items"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
