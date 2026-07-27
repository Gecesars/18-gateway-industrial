# Reutilização do EDGE-18

## 1. Responsabilidade do projeto-pai

O Projeto 18 mantém os contratos genéricos de aquisição e telemetria. Um projeto
filho pode substituir a PCB ou adicionar sensores, mas não deve criar uma
segunda definição incompatível de ponto, qualidade, fila ou envelope MQTT.

## 2. Ativos compartilhados

| Ativo | Forma de distribuição | Compatibilidade |
|---|---|---|
| `edge-model` | biblioteca C versionada | SemVer; ABI não é promessa entre majors |
| schemas JSON | release e URL imutável | versão no próprio documento |
| envelope MQTT | especificação + testes de contrato | prefixo `edge/v1` |
| HAL | interfaces C; porta por MCU | API versionada |
| ferramentas de configuração | pacote/CLI | compatível com schemas declarados |
| perfil de fabricação/teste | documentação e fixtures | por revisão de hardware |

## 3. Matriz de consumidores

| Projeto | Reutiliza | Especialização |
|---|---|---|
| 1 — Telemetria Broadcast | modelo, MQTT, buffer, Modbus, Ethernet | SNMP, transmissores e backend de estação |
| 2 — Gerador/combustível | HAL, I/O, eventos, buffer | máquina ATS e intertravamentos externos |
| 3 — Sensor RF IoT | modelo, MQTT, identidade, armazenamento | aquisição e calibração RF |
| 11 — NOC SaaS | tópicos, inventário e diagnóstico | multi-tenancy e operação comercial |
| 12 — Tower Companies | RTU, perfis e segurança | inventário corporativo e SLA |
| 13 — Qualidade de energia | transporte e armazenamento | ADC simultâneo, DSP e metrologia |
| 15 — Banco de baterias | RS-485, pontos e tendências | nós de impedância |
| 16 — Kit solar | analógicas, Modbus e buffer | SOC e prioridade de cargas |
| 17 — Frota | envelope e operação offline | OBD/GNSS/4G e privacidade |
| 19 — Torres | telemetria e tempo | IMU, espectro e baseline estrutural |

## 4. Regras contra bifurcação

1. Alteração comum nasce neste repositório.
2. O projeto filho abre requisito ou issue com caso de uso.
3. Mudança recebe teste de contrato.
4. Uma release imutável é publicada.
5. O filho atualiza a dependência e registra a versão.
6. Fork permanente só ocorre por ADR explícito.

## 5. Limites do reaproveitamento

- proteções automotivas não são herdadas de uma entrada industrial;
- isolação de RS-485 não qualifica interface de alta tensão;
- calibração RF/metrológica permanece no projeto consumidor;
- um schema comum não torna dois equipamentos intercambiáveis;
- certificação e ensaio pertencem a cada produto físico.
