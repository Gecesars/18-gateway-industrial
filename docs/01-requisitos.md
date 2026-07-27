# Requisitos

## Objetivo do sistema

Integrar equipamentos legados a MQTT/REST por configuração web, com qualidade de dados, regras locais e buffer offline.

## Requisitos funcionais iniciais

| ID | Requisito | Verificação prevista |
|---|---|---|
| F-18-01 | RS-485 | teste, inspeção ou demonstração documentada |
| F-18-02 | analógicas/digitais | teste, inspeção ou demonstração documentada |
| F-18-03 | configuração declarativa | teste, inspeção ou demonstração documentada |
| F-18-04 | MQTT | teste, inspeção ou demonstração documentada |
| F-18-05 | buffer | teste, inspeção ou demonstração documentada |
| F-18-06 | diagnóstico | teste, inspeção ou demonstração documentada |

## Requisitos de aceite do MVP

| ID | Critério | Evidência requerida |
|---|---|---|
| A-18-01 | configuração inválida isolada | evidência anexada ao relatório de validação |
| A-18-02 | RS-485 ensaiado | evidência anexada ao relatório de validação |
| A-18-03 | qualidade distingue falhas | evidência anexada ao relatório de validação |
| A-18-04 | fila com política explícita | evidência anexada ao relatório de validação |
| A-18-05 | update/rollback preservam configuração | evidência anexada ao relatório de validação |

## Requisitos não funcionais comuns

- estado de falha deve ser explícito e registrável;
- configurações e formatos de dados devem possuir versão;
- atualização não pode apagar calibração ou identidade sem confirmação;
- logs precisam distinguir tempo de aquisição e de recepção quando aplicável;
- montagem, teste e recuperação devem ser reproduzíveis por outra pessoa;
- nenhuma meta de desempenho será convertida em alegação comercial sem ensaio.

## Dentro do escopo

- RS-485
- analógicas/digitais
- configuração declarativa
- MQTT
- buffer
- diagnóstico

## Fora do escopo da primeira versão

- universalidade sem perfis testados
- OPC-UA e CAN no MVP
- exposição direta de barramento industrial à internet

## Dependências

- equipamentos Modbus reais
- laboratório EMC
- integradores piloto
- infraestrutura MQTT

Mudanças de requisito serão registradas no changelog e, quando alterarem uma
decisão estrutural, em `project-management/DECISIONS.md`.
