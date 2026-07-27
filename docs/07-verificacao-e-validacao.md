# Verificação e validação

## Matriz inicial

| Teste | Critério | Estado | Evidência |
|---|---|---|---|
| VT-18-01 | configuração inválida isolada | pendente | relatório + dados brutos |
| VT-18-02 | RS-485 ensaiado | pendente | relatório + dados brutos |
| VT-18-03 | qualidade distingue falhas | pendente | relatório + dados brutos |
| VT-18-04 | fila com política explícita | pendente | relatório + dados brutos |
| VT-18-05 | update/rollback preservam configuração | pendente | relatório + dados brutos |

## Níveis de teste

1. revisão de requisito e cálculo;
2. teste unitário/simulação;
3. inspeção e teste elétrico sem função perigosa;
4. integração em bancada com simuladores;
5. ensaio progressivo no envelope especificado;
6. piloto acompanhado;
7. regressão após alteração de hardware, firmware ou calibração.

## Regras de evidência

- relatório referencia revisão/commit e número de série;
- dados brutos são preservados em formato aberto;
- instrumentos e incertezas relevantes são identificados;
- falha não é apagada por repetição bem-sucedida;
- critério alterado depois do teste exige justificativa e nova revisão;
- a coluna Estado só muda quando a evidência estiver acessível.
