# Status do projeto

**Projeto:** 18 — EDGE-18 Gateway Industrial
**Data:** 2026-07-26
**Fase:** G0 — contratos e núcleo reutilizável
**Saúde:** amarela — arquitetura avançou; hardware físico ainda não existe

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

## Evidência atual

| Indicador | Resultado |
|---|---:|
| testes host | 1 executável, aprovado |
| casos unitários internos | fila, qualidade, identificador e CRC |
| schemas/exemplos | aprovados |
| modelo FreeCAD/STEP | dimensional P0, aprovado pelo validador |
| esquemáticos/PCBs | 0 |
| protótipos | 0 |
| ensaios físicos | 0 |

## Em andamento

- [ ] pinout físico do STM32H563;
- [ ] cálculo detalhado da alimentação;
- [ ] esquemático KiCad P0;

## Próximo gate

Fechar G0 com parser/validador C da configuração, scheduler inicial, protocolo
Modbus mestre no host e revisão dos contratos. Depois iniciar G1 elétrico.

## Bloqueios

- cliente/equipamento Modbus piloto ainda não escolhido;
- seleção final do regulador 3,3 V e memória OctoSPI;
- licença do repositório ainda não definida;
- normas/ensaios comerciais ainda não congelados.
