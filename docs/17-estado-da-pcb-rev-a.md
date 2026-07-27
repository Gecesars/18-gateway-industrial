# Estado congelado da PCB Rev. A

## 1. Decisão de controle

Em 27 de julho de 2026, o responsável pelo projeto determinou que a PCB fosse
mantida no estado corrente e que não fossem feitas novas tentativas de
roteamento. O arquivo
`hardware/edge18-main/edge18-main-rev-a.kicad_pcb` é, portanto, uma baseline de
revisão digital, não uma placa liberada para fabricação.

Nenhuma exceção de DRC foi aprovada. Nenhuma ocorrência abaixo deve ser
interpretada como aceita para produção.

## 2. Evidência automatizada

| Verificação | Resultado congelado |
|---|---:|
| ERC do esquemático | 0 erros, 0 avisos |
| violações DRC da PCB | 43 |
| conexões abertas | 24 |
| erros de footprint | 0 |
| curtos entre redes reportados | 0 |
| segmentos de trilha | 2.654 |
| vias | 289 |
| footprints | 185 |
| pads | 869 |
| zonas de cobre | 3 |

Os relatórios integrais são:

- [`reports/edge18-main-rev-a-erc.rpt`](reports/edge18-main-rev-a-erc.rpt);
- [`reports/edge18-main-rev-a-drc.rpt`](reports/edge18-main-rev-a-drc.rpt).

O manifesto
[`reports/edge18-rev-a.sha256`](reports/edge18-rev-a.sha256) permite verificar
a integridade dos CAD, código, imagens, PDF, relatórios e modelos mecânicos
entregues.

## 3. Distribuição das ocorrências de DRC

| Categoria | Quantidade | Interpretação |
|---|---:|---|
| `hole_to_hole` | 4 | furos/vias próximos demais |
| `copper_edge_clearance` | 7 | cobre próximo dos rasgos de isolamento |
| `clearance` | 1 | afastamento cobre–cobre abaixo de 0,18 mm |
| `track_dangling` | 17 | extremidades de trilhas sem continuidade |
| `via_dangling` | 14 | vias conectadas em somente uma camada |
| `unconnected_items` | 24 | ligações lógicas ainda abertas |

O total de 43 corresponde às cinco primeiras categorias. As 24 conexões abertas
são informadas separadamente pelo KiCad.

## 4. Larguras efetivamente presentes

| Largura | Segmentos | Uso |
|---:|---:|---|
| 0,25 mm | 1.084 | escapes e sinais de alta densidade |
| 0,30 mm | 429 | sinais gerais |
| 0,35 mm | 158 | sinais analógicos |
| 0,40 mm | 15 | transições herdadas do roteador |
| 0,50 mm | 275 | interfaces de campo |
| 0,601–0,740 mm | 16 | transições geométricas do roteador |
| 0,80 mm | 638 | alimentação |
| 1,20 mm | 39 | entrada VIN |

Não há segmento abaixo de 0,25 mm. Existe uma microvia de 0,30/0,10 mm no
escape do PHY Ethernet; as demais vias têm diâmetro mínimo de 0,70 mm.

## 5. Estado do 3D

O STEP da PCB congelada está em
`mechanical/step/edge18-main-rev-a.step`. A exportação inclui o corpo da placa,
furos e a maior parte dos componentes disponíveis na biblioteca KiCad local.
Dez referências de modelos 3D indicadas pelos footprints não existem nessa
versão da biblioteca e aparecem omitidas no STEP/render:

- `L1`, `L2`, `L3`;
- `F1`;
- `J3`, `J5`;
- `U1`, `U2`, `U4`, `U7`.

Essa ausência é uma pendência visual/mecânica e não altera a conectividade
elétrica. Antes de validar colisões e recortes do gabinete, os modelos corretos
dos fabricantes devem substituir as aproximações/ausências.

## 6. Condições para futura liberação fabril

Uma revisão posterior só pode receber o estado `liberada para fabricação`
depois de:

1. fechar as 24 conexões;
2. eliminar as 43 ocorrências de DRC sem criar exceções silenciosas;
3. executar inspeção cruzada de esquemático, layout, polaridade e pinout;
4. completar e alinhar os dez modelos 3D ausentes;
5. realizar DFM com o fabricante e revisar stack-up/impedâncias;
6. montar protótipos e concluir bring-up, elétrica, térmica, EMC e isolamento;
7. registrar a evidência e aprovar formalmente o gate G2.

Até lá, Gerbers e arquivos de montagem não devem ser usados para compra ou
produção.
