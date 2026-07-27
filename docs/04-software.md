# Software e firmware

## Componentes previstos

| ID | Componente | Estado |
|---|---|---|
| SW-18-01 | scheduler de aquisição | planejado |
| SW-18-02 | Modbus mestre | planejado |
| SW-18-03 | modelo JSON | planejado |
| SW-18-04 | editor web | planejado |
| SW-18-05 | MQTT/REST | planejado |
| SW-18-06 | fila e atualização com rollback | planejado |

## Organização proposta

- `firmware/`: HAL, drivers, serviços de domínio e testes embarcados;
- `software/backend/`: ingestão, regras, persistência e APIs;
- `software/frontend/`: interface de usuário;
- `software/tools/`: calibração, provisionamento, exportação e diagnóstico;
- configurações e protocolos terão schema e número de versão.

## Requisitos de qualidade

- build reproduzível e dependências fixadas;
- análise estática, formatação e testes executáveis em CI;
- testes unitários do domínio sem exigir hardware;
- simuladores/fakes para sensores e protocolos;
- watchdog, métricas de saúde e logs sem segredos;
- atualização com verificação, migração de configuração e recuperação;
- limites de fila, timeout, repetição e descarte explicitamente definidos.

## Dados fundamentais

- ponto/endereço/tipo/escala
- valor/qualidade/timestamp
- configuração/versionamento
- evento/regra
- diagnóstico

## Estado atual

Não há implementação nesta baseline. O primeiro commit de código deverá incluir
instruções de build/teste e um teste mínimo automatizado.
