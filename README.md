# Projeto 18 — Gateway Industrial Modbus/CAN Universal

**Categoria:** Automação industrial
**Estado:** concepção documentada; implementação ainda não iniciada
**Baseline documental:** 2026-07-26

## Objetivo

Integrar equipamentos legados a MQTT/REST por configuração web, com qualidade de dados, regras locais e buffer offline.

## Usuários

- integradores
- pequenas indústrias
- manutenção e automação

## MVP

Modbus RTU mestre, quatro analógicas, quatro digitais, Ethernet, MQTT e diagnóstico/configuração web; CAN/OPC-UA entram depois.

## Estrutura

- `docs/`: especificação técnica e operacional.
- `project-management/`: andamento, backlog, riscos, decisões e atas.
- `hardware/`: fontes eletrônicas e BOM quando o desenvolvimento começar.
- `firmware/`: software embarcado e testes.
- `software/`: backend, frontend, aplicativos e ferramentas.
- `mechanical/`: gabinetes, suportes e desenhos.
- `simulation/`: modelos e estudos.
- `tests/`: planos, fixtures, dados e evidências.
- `manufacturing/`: fabricação, montagem e implantação.
- `tools/`: automação reproduzível.

## Regras de estado

Uma caixa marcada representa evidência existente, não intenção. O projeto não
deve ser apresentado como protótipo, validado ou comercial até que os gates
correspondentes em `project-management/ROADMAP.md` estejam concluídos.

Comece por [`docs/README.md`](docs/README.md) e
[`project-management/STATUS.md`](project-management/STATUS.md).
