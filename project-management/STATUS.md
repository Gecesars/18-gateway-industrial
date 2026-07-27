# Status do projeto

**Projeto:** 18 — EDGE-18 Gateway Industrial
**Data:** 2026-07-27
**Fase:** G1 digital concluído; G2 bloqueado no layout
**Saúde:** amarela — entrega digital ampla, PCB ainda não fabricável

## Concluído

- [x] ordem de desenvolvimento aprovada;
- [x] Projeto 18 definido como plataforma-pai;
- [x] requisitos P0 detalhados;
- [x] STM32H563 e componentes principais selecionados;
- [x] seis ADRs;
- [x] schemas de configuração/telemetria e exemplos;
- [x] núcleo C17 de pontos, qualidade, fila e CRC Modbus;
- [x] build, testes e CI;
- [x] modelo dimensional FreeCAD/STEP P0 validado;
- [x] matriz de reutilização para projetos filhos.
- [x] esquemático A0 Rev. A com ERC limpo;
- [x] BOM de 181 posições e pinout STM32 de 144 pinos;
- [x] PCB quatro camadas posicionada e parcialmente roteada;
- [x] código C17 dos serviços centrais e testes host;
- [x] quinze vistas técnicas e PDF consolidado;
- [x] STEP da PCB e conjunto FreeCAD Rev. A;
- [x] baseline da PCB congelada por decisão do responsável.

## Evidência atual

| Indicador | Resultado |
|---|---:|
| testes host | suíte C17, aprovada |
| esquemático | ERC: 0 erros, 0 avisos |
| PCB congelada | 43 DRC; 24 conexões abertas; 0 erro de footprint |
| trilha mínima presente | 0,25 mm |
| BOM | 181 posições; 4 DNP |
| pinout | 144 pinos |
| schemas/exemplos | aprovados |
| modelo FreeCAD/STEP | Rev. A, aprovado pelo validador dimensional |
| imagens técnicas | 15 |
| PDF consolidado | 1 |
| protótipos | 0 |
| ensaios físicos | 0 |

## Congelado por decisão

- [ ] 24 conexões abertas;
- [ ] 43 ocorrências de DRC;
- [ ] dez modelos 3D ausentes na biblioteca local.

## Próximo gate

G1 pode ser revisado documentalmente. G2 permanece bloqueado até uma futura
autorização para retomar o layout, fechar conectividade e obter DRC limpo.

## Bloqueios

- PCB não liberada para fabricação;
- cliente/equipamento Modbus piloto ainda não escolhido;
- licença do repositório ainda não definida;
- normas/ensaios comerciais ainda não congelados.
