#!/usr/bin/env python3
"""Crop, label and validate the 15 EDGE-18 documentation images."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont


DPI = 180.0
PX_PER_MM = DPI / 25.4
FONT_BOLD = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
FONT_REGULAR = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")


def crop_mm(
    image: Image.Image,
    coordinates: tuple[float, float, float, float],
) -> Image.Image:
    return image.crop(tuple(round(value * PX_PER_MM) for value in coordinates))


def trim_white(image: Image.Image, padding: int = 28) -> Image.Image:
    rgb = image.convert("RGB")
    white = Image.new("RGB", rgb.size, (255, 255, 255))
    difference = ImageChops.difference(rgb, white).convert("L")
    difference = difference.point(lambda value: 255 if value > 12 else 0)
    box = difference.getbbox()
    if box is None:
        return rgb
    left = max(0, box[0] - padding)
    top = max(0, box[1] - padding)
    right = min(rgb.width, box[2] + padding)
    bottom = min(rgb.height, box[3] + padding)
    return rgb.crop((left, top, right, bottom))


def decorate(image: Image.Image, title: str, subtitle: str) -> Image.Image:
    rgb = image.convert("RGB")
    maximum = 4200
    if rgb.width > maximum:
        height = round(rgb.height * maximum / rgb.width)
        rgb = rgb.resize((maximum, height), Image.Resampling.LANCZOS)

    header_height = 104
    footer_height = 48
    canvas = Image.new(
        "RGB",
        (rgb.width, rgb.height + header_height + footer_height),
        "#f5f7fa",
    )
    canvas.paste(rgb, (0, header_height))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, canvas.width, header_height), fill="#14243a")
    draw.rectangle(
        (0, canvas.height - footer_height, canvas.width, canvas.height),
        fill="#e5eaf0",
    )
    title_font = ImageFont.truetype(str(FONT_BOLD), 34)
    subtitle_font = ImageFont.truetype(str(FONT_REGULAR), 20)
    footer_font = ImageFont.truetype(str(FONT_REGULAR), 17)
    draw.text((28, 18), title, font=title_font, fill="#ffffff")
    draw.text((30, 63), subtitle, font=subtitle_font, fill="#a9d7ff")
    draw.text(
        (24, canvas.height - 35),
        "EDGE-18 Rev. A • revisão digital congelada • NÃO FABRICAR",
        font=footer_font,
        fill="#42526a",
    )
    return canvas


def save(image: Image.Image, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG", optimize=True, compress_level=8)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("raw", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    schematic = Image.open(args.raw / "schematic.png")
    schematic_specs = (
        (
            "01-esquematico-visao-geral.png",
            (10, 10, 870, 560),
            "Esquemático completo",
            "A0 • sete blocos funcionais • 195 símbolos",
        ),
        (
            "02-esquematico-alimentacao.png",
            (10, 10, 242, 198),
            "Alimentação e proteção",
            "Entrada 9–36 V • LM76002 5 V • TPS62132 3,3 V",
        ),
        (
            "03-esquematico-controlador.png",
            (235, 10, 425, 310),
            "Controlador seguro",
            "STM32H563ZIT6 • clocks • SWD • supervisão",
        ),
        (
            "04-esquematico-armazenamento.png",
            (428, 204, 735, 310),
            "Armazenamento e serviço",
            "RTC • flash • microSD • USB-C",
        ),
        (
            "05-esquematico-rede.png",
            (495, 10, 735, 200),
            "Ethernet e Wi-Fi opcional",
            "LAN8742A RMII • ESP32-C3-WROOM-02 DNP",
        ),
        (
            "06-esquematico-analogico.png",
            (10, 310, 275, 530),
            "Quatro entradas analógicas",
            "0–10 V / 4–20 mA • ADS8684 • seleção por jumper",
        ),
        (
            "07-esquematico-digital.png",
            (275, 310, 555, 530),
            "Quatro entradas digitais",
            "IEC 61131-2 Type 3 • 2 × ISO1212",
        ),
        (
            "08-esquematico-barramentos.png",
            (550, 310, 860, 530),
            "Barramentos isolados",
            "2 × ISOW1412 RS-485 • ISOW1044 CAN-FD",
        ),
    )
    for filename, coordinates, title, subtitle in schematic_specs:
        panel = crop_mm(schematic, coordinates)
        save(decorate(panel, title, subtitle), args.output / filename)

    pcb_specs = (
        (
            "pcb-layout.png",
            "09-pcb-layout-superior.png",
            "PCB — implantação superior",
            "180 × 120 mm • roteamento parcial congelado • não fabricar",
            True,
        ),
        (
            "pcb-top.png",
            "10-pcb-cobre-superior.png",
            "PCB — cobre superior",
            "F.Cu • estado real com pendências documentadas",
            True,
        ),
        (
            "pcb-in1.png",
            "11-pcb-plano-terra.png",
            "PCB — plano interno de terra",
            "In1.Cu • visualização da camada interna",
            True,
        ),
        (
            "pcb-in2.png",
            "12-pcb-plano-alimentacao.png",
            "PCB — alimentação interna",
            "In2.Cu • visualização da camada interna",
            True,
        ),
        (
            "pcb-bottom.png",
            "13-pcb-cobre-inferior.png",
            "PCB — cobre inferior",
            "B.Cu • vista espelhada de fabricação",
            True,
        ),
    )
    for raw_name, filename, title, subtitle, should_trim in pcb_specs:
        image = Image.open(args.raw / raw_name)
        if should_trim:
            image = trim_white(image)
        save(decorate(image, title, subtitle), args.output / filename)

    for raw_name, filename, title, subtitle in (
        (
            "pcb-3d.png",
            "14-pcb-3d.png",
            "PCB — inspeção 3D",
            "Modelos KiCad disponíveis • 10 ausências documentadas",
        ),
        (
            "enclosure.png",
            "15-conjunto-mecanico-3d.png",
            "Conjunto mecânico FreeCAD",
            "PCB Rev. A • gabinete 210 × 150 × 65 mm • trilho DIN",
        ),
    ):
        save(
            decorate(Image.open(args.raw / raw_name), title, subtitle),
            args.output / filename,
        )

    generated = sorted(args.output.glob("*.png"))
    if len(generated) != 15:
        raise RuntimeError(f"expected 15 images, found {len(generated)}")
    for path in generated:
        with Image.open(path) as image:
            if image.width < 1100 or image.height < 650:
                raise RuntimeError(f"image too small: {path} {image.size}")
    print("Generated and validated 15 documentation images")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
