# Manufacturing

## Finalidade

Pacote de fabricação, montagem e implantação.

## Entregáveis futuros

- Gerbers/BOM/posição
- instruções de montagem
- gabarito de fim de linha
- as-built

## Estado Rev. A congelada

Nenhum pacote de fabricação foi emitido. A PCB tem 43 ocorrências de DRC e 24
conexões abertas; portanto, Gerbers, arquivos de posição e ordens de montagem
estão bloqueados. A evidência está em
[`../docs/17-estado-da-pcb-rev-a.md`](../docs/17-estado-da-pcb-rev-a.md).

`tools/export-release.sh` mantém o gate técnico: ele só gera o pacote quando
ERC e DRC estiverem limpos.
