# Mecânica EDGE-18

## P0 dimensional

- gabinete: 210 × 150 × 65 mm;
- PCB: 180 × 120 × 1,6 mm;
- seis pontos de fixação M3;
- tampa removível;
- aberturas-envelope para Ethernet, USB e terminais;
- volumes funcionais para fonte, analógicas, digitais, MCU, barramentos,
  Ethernet e keep-out da antena.

Fontes:

- `source/generate_edge18_enclosure.py`;
- `source/validate_edge18_enclosure.py`;
- `native/edge18-p0-assembly.FCStd`;
- `step/edge18-p0-*.step`.

Regeneração:

```bash
./tools/generate-mechanical.sh
```

O modelo prova dimensões e particionamento. Não contém conectores finais,
parafusos, tolerâncias de fabricação, vedação, ventilação ou desenho de oficina;
não está liberado para fabricação.
