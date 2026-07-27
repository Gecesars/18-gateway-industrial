#!/usr/bin/env python3
"""Generate the revision-controlled STM32H563 pin table from native CAD."""

from __future__ import annotations

import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
TOOL_ROOT = Path(
    os.environ.get(
        "EDGE18_TOOL_ROOT",
        "/mnt/eftx-data/cache/antenna-coupler-tools",
    )
)
KICAD_ROOT = TOOL_ROOT / "kicad/root"
EDA_SITE = TOOL_ROOT / "python-eda/lib/python3.13/site-packages"
sys.path.insert(0, str(EDA_SITE))
sys.path.insert(0, str(KICAD_ROOT / "usr/lib/python3/dist-packages"))

import pcbnew
from kiutils.symbol import SymbolLib


BOARD = ROOT / "hardware/edge18-main/edge18-main-rev-a.kicad_pcb"
SYMBOLS = (
    ROOT / "hardware/libraries/frozen/MCU_ST_STM32H5.kicad_sym"
)
OUTPUT = ROOT / "docs/13-pinout-stm32h563-rev-a.md"


def domain(net: str) -> str:
    if net == "RESERVADO":
        return "RESERVADO"
    if net in {
        "GND",
        "AGND",
        "3V3",
        "3V3_A",
        "3V3_RTC",
        "VCAP1",
        "VCAP2",
    }:
        return "ALIMENTAÇÃO"
    prefixes = (
        ("ETH_", "ETHERNET"),
        ("RS485A_", "RS-485 A"),
        ("RS485B_", "RS-485 B"),
        ("ADC_", "ADC"),
        ("AI", "ANALÓGICO"),
        ("DI", "DIGITAL"),
        ("SD_", "MICROSD"),
        ("FLASH_", "FLASH"),
        ("USB_", "USB"),
        ("WIFI_", "WI-FI"),
        ("CAN_", "CAN"),
        ("SW", "DEBUG"),
        ("HSE_", "CLOCK"),
        ("LSE_", "CLOCK"),
        ("RTC_", "RTC"),
        ("PGOOD_", "SUPERVISÃO"),
        ("VIN_", "SUPERVISÃO"),
        ("5V_", "SUPERVISÃO"),
        ("3V3_", "SUPERVISÃO"),
        ("LED_", "STATUS"),
        ("EXP_", "EXPANSÃO"),
    )
    for prefix, name in prefixes:
        if net.startswith(prefix):
            return name
    if net in {"NRST", "BOOT0"}:
        return "DEBUG"
    if net.startswith("I2C_"):
        return "I²C"
    return "CONTROLE"


def main() -> int:
    board = pcbnew.LoadBoard(str(BOARD))
    footprint = board.FindFootprintByReference("U3")
    if footprint is None:
        raise RuntimeError("U3 not found in board")
    nets = {
        str(pad.GetNumber()): pad.GetNetname() or "RESERVADO"
        for pad in footprint.Pads()
    }

    library = SymbolLib().from_file(str(SYMBOLS))
    symbol = library.symbols[0]
    names = {
        pin.number: pin.name
        for unit in symbol.units
        for pin in unit.pins
    }

    lines = [
        "# Pinout STM32H563ZIT6 — EDGE-18 Rev. A",
        "",
        "Tabela gerada diretamente do símbolo congelado e do PCB nativo. "
        "`RESERVADO` significa pad sem net nesta revisão; não autoriza uso "
        "sem atualizar esquemático, PCB, firmware e análise de conflitos.",
        "",
        "| Pino | Nome físico | Net Rev. A | Domínio |",
        "|---:|---|---|---|",
    ]
    for number in range(1, 145):
        key = str(number)
        net = nets.get(key, "RESERVADO")
        lines.append(
            f"| {number} | `{names.get(key, 'N/D')}` | "
            f"`{net}` | {domain(net)} |"
        )
    assigned = sum(net != "RESERVADO" for net in nets.values())
    lines.extend(
        (
            "",
            "## Controle",
            "",
            "- encapsulamento: LQFP-144, passo 0,50 mm;",
            f"- pads com net atribuída: {assigned};",
            f"- pads reservados: {144 - assigned};",
            "- RMII, SWD e alimentação têm prioridade sobre expansões;",
            "- as funções alternativas devem ser reproduzidas no projeto "
            "STM32Cube/HAL e conferidas no build do alvo;",
            "- a fonte normativa elétrica continua sendo o esquemático e o "
            "PCB da Rev. A.",
            "",
        )
    )
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
