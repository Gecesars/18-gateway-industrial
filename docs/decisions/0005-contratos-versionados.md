# ADR 0005 — contratos versionados no projeto-pai

- Estado: aceito
- Data: 2026-07-26

## Decisão

Modelo de ponto, qualidade, configuração e envelope MQTT são mantidos pelo
Projeto 18 e publicados em releases imutáveis. Projetos filhos consomem versões
declaradas.

## Consequências

Mudanças comuns exigem compatibilidade e testes de contrato. Evita-se copiar e
divergir código entre os vinte repositórios.
