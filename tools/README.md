# Ferramentas locais

Os scripts deste diretório mantêm todas as dependências pesadas na partição
`/mnt/eftx-data`. Os caminhos podem ser substituídos com `EDGE18_TOOL_ROOT`.

- `generate-hardware.sh`: recria esquemático, PCB inicial e BOM de fonte;
  `--schematic-only` preserva a PCB congelada e `--bom-only` preserva ambos os
  CAD nativos.
- `kicad-cli.sh`: executa o KiCad 9 no ambiente local isolado.
- `route-board.sh`: exporta DSN, roteia com Freerouting, reimporta SES e
  recalcula os planos; não executar na baseline congelada sem nova autorização.
- `fill-zones.sh`: recalcula zonas de cobre de forma headless.
- `generate-mechanical.sh`: recria os arquivos mecânicos no FreeCAD.
- `generate-images.sh`: exporta e valida exatamente 15 imagens documentais de
  esquemático, camadas do PCB e modelos 3D.
- `generate-project-pdf.sh`: consolida documentação, decisões, gestão e as 15
  imagens em um PDF A4 paginado.
- `export-release.sh`: exige ERC/DRC limpos e exporta Gerbers, furação, IPC-D-356,
  posição, BOM, PDFs, STEP, hashes e ZIP da Rev. A.
- `validate_review.py`: valida sem KiCad/FreeCAD os artefatos commitados e o
  estado congelado esperado de 43 DRC/24 conexões.
- `generate-review-manifest.sh`: gera hashes SHA-256 do CAD, firmware,
  documentação visual, relatórios e modelos mecânicos entregues.
- `validate_release.py`: valida um futuro pacote fabril somente quando existir
  e estiver com ERC/DRC limpos.
- `run-checks.sh`: schemas, links, build/testes C17, revisão congelada e modelo
  mecânico.
