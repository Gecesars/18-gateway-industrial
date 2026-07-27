# Roadmap e gates

| Gate | Conteúdo | Estado | Saída |
|---|---|---|---|
| G0 | requisitos, ADRs, schemas e núcleo host | concluído digitalmente | contratos v0.1 e testes |
| G1 | esquema, cálculos e ERC | concluído digitalmente | KiCad Rev. A, ERC limpo |
| G2 | PCB, mecânica, DRC e fabricação | bloqueado no layout congelado | exige 0 DRC e 0 conexões |
| G3 | alimentação, clock, debug e storage | pendente | relatório de bring-up |
| G4 | RS-485, Modbus, AI e DI | pendente | matriz de I/O |
| G5 | Ethernet, TLS, MQTT e fila persistente | pendente | ensaio integrado |
| G6 | confiabilidade e pré-compliance | pendente | 30 dias + relatório |
| G7 | piloto somente leitura | bloqueado por G0–G6 | aceite de campo |
| G8 | CAN/OPC-UA/expansões | fora do MVP | nova baseline |

## Regra

Um gate só conclui com evidência. Fontes geradas não equivalem a placa montada;
simulação não equivale a ensaio; piloto não equivale a produto certificado.
