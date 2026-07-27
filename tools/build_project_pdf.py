#!/usr/bin/env python3
"""Build the consolidated EDGE-18 engineering PDF from repository sources."""

from __future__ import annotations

from html import escape
from pathlib import Path

import markdown
from weasyprint import CSS, HTML


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/EDGE-18-projeto-completo-rev-a.pdf"
DOCUMENTS = (
    ROOT / "README.md",
    ROOT / "docs/00-proposta.md",
    ROOT / "docs/01-requisitos.md",
    ROOT / "docs/02-arquitetura.md",
    ROOT / "docs/03-hardware.md",
    ROOT / "docs/04-software.md",
    ROOT / "docs/05-interfaces-e-dados.md",
    ROOT / "docs/06-seguranca-e-conformidade.md",
    ROOT / "docs/07-verificacao-e-validacao.md",
    ROOT / "docs/08-fabricacao-e-implantacao.md",
    ROOT / "docs/09-operacao-e-manutencao.md",
    ROOT / "docs/10-controle-documental.md",
    ROOT / "docs/11-reutilizacao.md",
    ROOT / "docs/12-fontes-primarias.md",
    ROOT / "docs/13-pinout-stm32h563-rev-a.md",
    ROOT / "docs/14-modelo-de-ameacas.md",
    ROOT / "docs/15-calculos-eletricos.md",
    ROOT / "docs/16-bom-e-montagem.md",
    ROOT / "docs/17-estado-da-pcb-rev-a.md",
    ROOT / "docs/decisions/0001-mcu-stm32h563.md",
    ROOT / "docs/decisions/0002-monitoramento-sem-saidas.md",
    ROOT / "docs/decisions/0003-isolacao-de-campo.md",
    ROOT / "docs/decisions/0004-wifi-coprocessador.md",
    ROOT / "docs/decisions/0005-contratos-versionados.md",
    ROOT / "docs/decisions/0006-dimensoes-p0.md",
    ROOT / "project-management/STATUS.md",
    ROOT / "project-management/ROADMAP.md",
    ROOT / "project-management/RISKS.md",
    ROOT / "project-management/BACKLOG.md",
    ROOT / "firmware/README.md",
    ROOT / "hardware/README.md",
    ROOT / "mechanical/README.md",
)


CSS_TEXT = """
@page {
  size: A4;
  margin: 18mm 15mm 17mm 18mm;
  @top-left {
    content: "EDGE-18 Rev. A";
    color: #53657a;
    font-size: 8.5pt;
  }
  @top-right {
    content: "Engenharia digital";
    color: #53657a;
    font-size: 8.5pt;
  }
  @bottom-center {
    content: "Página " counter(page) " de " counter(pages);
    color: #53657a;
    font-size: 8.5pt;
  }
}
@page cover {
  margin: 0;
  @top-left { content: none; }
  @top-right { content: none; }
  @bottom-center { content: none; }
}
html { color: #17253a; font-family: "DejaVu Sans", sans-serif; font-size: 9.2pt; }
body { line-height: 1.36; }
.cover {
  page: cover;
  height: 297mm;
  padding: 27mm 22mm;
  box-sizing: border-box;
  background: linear-gradient(145deg, #102139 0%, #193c5a 62%, #16704c 100%);
  color: white;
}
.cover h1 { font-size: 31pt; margin: 0 0 4mm; color: white; }
.cover h2 { font-size: 16pt; color: #bde3ff; margin: 0 0 10mm; }
.cover img { width: 100%; max-height: 145mm; object-fit: contain; margin: 8mm 0; }
.cover .meta { margin-top: 9mm; font-size: 11pt; }
.warning {
  background: #fff4d6;
  border-left: 4px solid #dc8b00;
  color: #4f3500;
  padding: 3mm 4mm;
  margin: 4mm 0;
}
h1 { color: #102f4f; font-size: 21pt; page-break-before: always; margin-top: 0; }
h2 { color: #135b56; font-size: 15pt; margin-top: 7mm; }
h3 { color: #244d6d; font-size: 11.5pt; }
p, li { orphans: 3; widows: 3; }
table { border-collapse: collapse; width: 100%; margin: 3mm 0 5mm; font-size: 7.8pt; }
th { background: #183b59; color: white; }
th, td { border: 0.25mm solid #b9c4cf; padding: 1.3mm 1.6mm; vertical-align: top; }
tr:nth-child(even) td { background: #f1f5f8; }
code { font-family: "DejaVu Sans Mono", monospace; background: #eef2f5; }
pre { background: #122234; color: #e8f2f7; padding: 3mm; white-space: pre-wrap; font-size: 7.6pt; }
a { color: #12629a; text-decoration: none; }
blockquote { border-left: 3px solid #2b8a7e; margin-left: 0; padding-left: 4mm; color: #344a5e; }
.gallery-page { page-break-before: always; text-align: center; }
.gallery-page h2 { font-size: 17pt; }
.gallery-page img { max-width: 100%; max-height: 235mm; object-fit: contain; }
.source-label { color: #607286; font-size: 8pt; margin-bottom: 3mm; }
.document { page-break-before: always; }
"""


def markdown_to_html(text: str) -> str:
    return markdown.markdown(
        text,
        extensions=("extra", "tables", "fenced_code", "sane_lists"),
        output_format="html5",
    )


def main() -> int:
    images = sorted((ROOT / "docs/images").glob("*.png"))
    if len(images) != 15:
        raise RuntimeError(f"expected 15 images before PDF, found {len(images)}")
    missing = [path for path in DOCUMENTS if not path.exists()]
    if missing:
        raise FileNotFoundError(f"missing PDF sources: {missing}")

    cover_image = images[13].relative_to(ROOT).as_posix()
    parts = [
        "<section class='cover'>",
        "<h1>EDGE-18</h1>",
        "<h2>Gateway industrial universal — Dossiê da revisão digital Rev. A</h2>",
        f"<img src='{escape(cover_image)}' alt='PCB EDGE-18 em 3D'>",
        "<div class='meta'>",
        "<p><strong>Data:</strong> 27 de julho de 2026</p>",
        "<p><strong>MCU:</strong> STM32H563ZIT6</p>",
        "<p><strong>CAD:</strong> KiCad 9 + FreeCAD 1.0</p>",
        "<p><strong>Repositório:</strong> Gecesars/18-gateway-industrial</p>",
        "</div>",
        "<div class='warning'><strong>NÃO FABRICAR.</strong> Revisão digital "
        "congelada com 43 ocorrências de DRC e 24 conexões abertas. A retomada "
        "do layout, protótipo, bring-up, DFM e ensaios físicos permanecem "
        "pendentes.</div>",
        "</section>",
        "<section class='document'>",
        "<h1>Galeria técnica — 15 vistas</h1>",
        "<p>As vistas de esquemático são recortes em alta resolução para manter "
        "referências, valores e nomes de nets legíveis.</p>",
        "</section>",
    ]
    for image in images:
        title = image.stem.replace("-", " ").title().replace("Pcb", "PCB")
        relative = image.relative_to(ROOT).as_posix()
        parts.extend(
            (
                "<section class='gallery-page'>",
                f"<h2>{escape(title)}</h2>",
                f"<p class='source-label'>{escape(relative)}</p>",
                f"<img src='{escape(relative)}' alt='{escape(title)}'>",
                "</section>",
            )
        )

    for source in DOCUMENTS:
        content = source.read_text(encoding="utf-8")
        parts.extend(
            (
                "<section class='document'>",
                f"<p class='source-label'>Fonte: "
                f"{escape(source.relative_to(ROOT).as_posix())}</p>",
                markdown_to_html(content),
                "</section>",
            )
        )

    html = (
        "<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'>"
        "<title>EDGE-18 — Projeto completo Rev. A</title></head><body>"
        + "\n".join(parts)
        + "</body></html>"
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html, base_url=str(ROOT)).write_pdf(
        str(OUTPUT),
        stylesheets=[CSS(string=CSS_TEXT)],
    )
    print(f"Generated {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
