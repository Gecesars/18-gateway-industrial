# Mecânica EDGE-18

## Rev. A digital

- gabinete: 210 × 150 × 65 mm;
- PCB: 180 × 120 × 1,6 mm;
- quatro pontos de fixação M3;
- tampa removível;
- aberturas para Ethernet, USB, alimentação e terminais;
- dois adaptadores inferiores para trilho DIN;
- importação do STEP real da PCB quando o pacote de release está presente;
- volumes funcionais para fonte, analógicas, digitais, MCU, barramentos,
  Ethernet e keep-out da antena.

Fontes:

- `source/generate_edge18_enclosure.py`;
- `source/validate_edge18_enclosure.py`;
- `native/edge18-rev-a-assembly.FCStd`;
- `step/edge18-main-rev-a.step` (exportação da PCB KiCad congelada);
- `step/edge18-rev-a-*.step`.

Regeneração:

```bash
./tools/generate-mechanical.sh
```

O modelo confere envelope, fixações, recortes e conjunto PCB/gabinete. Parafusos,
torques, junta, grau IP, dissipação e desenho de oficina dependem do protótipo e
do processo de fabricação escolhido.

Dez referências de modelos 3D não estão disponíveis na biblioteca KiCad local
e são omitidas na exportação atual. A lista e o impacto estão documentados em
[`../docs/17-estado-da-pcb-rev-a.md`](../docs/17-estado-da-pcb-rev-a.md).
