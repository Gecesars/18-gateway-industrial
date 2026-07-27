# ADR 0002 — MVP somente de monitoramento

- Estado: aceito
- Data: 2026-07-26

## Decisão

O P0 não terá saídas de controle de processo. Funções Modbus 05/06/15/16 existem
na biblioteca para testes/perfis futuros, mas são desabilitadas por política no
MVP e não podem ser disparadas pela nuvem.

## Consequências

Reduz-se o risco do primeiro piloto. Projetos que comandam cargas devem adicionar
hardware, intertravamentos, autorização e testes próprios.
