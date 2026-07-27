# Hardware

## Finalidade

Fontes de eletrônica do projeto.

## Entregáveis Rev. A

- `edge18-main/edge18-main-rev-a.kicad_sch`: esquemático A0 com sete blocos;
- `edge18-main/edge18-main-rev-a.kicad_pcb`: PCB 180 × 120 mm, quatro camadas;
- `libraries/frozen/`: símbolos resolvidos e congelados para ERC reprodutível;
- `bom/edge18-main-rev-a-source.csv`: 181 posições e quatro DNP;
- `scripts/generate_kicad.py`: fonte determinística de esquemático, PCB inicial
  e BOM;
- `scripts/generate_pinout.py`: tabela dos 144 pinos extraída do CAD;
- `scripts/specctra_io.py`: intercâmbio DSN/SES;
- relatórios ERC/DRC em `docs/reports/`.

## Regras principais

- trilha mínima global: 0,25 mm;
- padrão: 0,30 mm; analógico: 0,35 mm; campo: 0,50 mm;
- alimentação: 0,80 mm; VIN: 1,20 mm;
- quatro camadas: F.Cu, In1.Cu, In2.Cu e B.Cu;
- três rasgos sob as barreiras isoladas;
- ESP32-C3-WROOM-02 marcado DNP;
- nenhuma saída de controle de processo.

## Estado congelado

A PCB Rev. A foi congelada em 27 de julho de 2026 com 43 ocorrências de DRC e
24 conexões abertas, por decisão do responsável. Não retome o roteamento nem
gere arquivos fabris a partir desta baseline sem nova autorização. O
esquemático tem ERC limpo e não há trilha abaixo de 0,25 mm.

Detalhes: [`../docs/17-estado-da-pcb-rev-a.md`](../docs/17-estado-da-pcb-rev-a.md).

## Regeneração e validação de desenvolvimento

```bash
./tools/generate-hardware.sh
./tools/kicad-cli.sh sch erc \
  --exit-code-violations hardware/edge18-main/edge18-main-rev-a.kicad_sch
./tools/kicad-cli.sh pcb drc \
  --exit-code-violations hardware/edge18-main/edge18-main-rev-a.kicad_pcb
```

`generate-hardware.sh` substitui o PCB pelo posicionamento inicial; execute o
roteamento depois dele somente em uma futura linha de desenvolvimento
autorizada. `--schematic-only` atualiza esquemático, BOM e bibliotecas sem tocar
na PCB congelada; `--bom-only` atualiza somente a BOM.

## Limite da liberação

O ERC está limpo, mas o DRC não está. A revisão atual não pode ser fabricada.
Protótipo, DFM, bring-up, térmica, surto, EMC e isolamento também continuam
pendentes.
