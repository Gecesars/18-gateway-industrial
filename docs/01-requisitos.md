# Requisitos do Gateway Industrial — P0

**Baseline:** 2026-07-26
**Estado:** aprovado para projeto detalhado; desempenho ainda não ensaiado
**Produto:** `EDGE-18`

## 1. Objetivo

O EDGE-18 é uma plataforma de aquisição industrial somente de monitoramento. Ele
converte Modbus RTU, sinais analógicos e entradas digitais em pontos com unidade,
timestamp e qualidade; conserva dados durante a perda de rede e os publica por
MQTT/TLS. Ethernet é o enlace principal. Wi-Fi é opcional. CAN-FD estará no
hardware P0 para reutilização futura, mas não faz parte do aceite do MVP.

## 2. Envelope do MVP

| Item | Requisito P0 |
|---|---|
| Alimentação | 9–36 Vcc nominal, 15 W máximos previstos |
| Placa | 180 × 120 mm, quatro camadas, sem miniaturização agressiva |
| Temperatura de uso do protótipo | 0–50 °C, ambiente interno, sem condensação |
| MCU | STM32H563ZIT6, Cortex-M33/TrustZone |
| Rede | Ethernet 10/100; Wi-Fi 2,4 GHz opcional |
| Campo serial | 2 × RS-485 isoladas, Modbus RTU mestre |
| Analógicas | 4 × 0–10 V ou 4–20 mA, referência de campo comum |
| Digitais | 4 × 24 V isoladas, contato/pulso |
| CAN | 1 × CAN-FD isolado, hardware reservado, firmware pós-MVP |
| Configuração | JSON Schema v1, interface local autenticada |
| Telemetria | MQTT 3.1.1 ou 5.0 sobre TLS, QoS 1 |
| Armazenamento | microSD industrial; fila limitada e auditável |
| Controle físico | nenhum no MVP |

## 3. Requisitos funcionais

### 3.1 Inicialização, identidade e tempo

| ID | Requisito | Aceite |
|---|---|---|
| SYS-001 | Inicializar em estado somente leitura, sem acionar carga externa | inspeção e teste de boot/reset |
| SYS-002 | Possuir identificador imutável de hardware e identificador lógico configurável | leitura por USB/REST e persistência |
| SYS-003 | Registrar versão de hardware, bootloader, firmware, schema e configuração | mensagem de inventário |
| SYS-004 | Inicializar em até 10 s quando não houver recuperação de armazenamento | medição em 30 ciclos |
| TIME-001 | Sincronizar por NTP quando houver rede | erro ≤ 1 s após sincronismo |
| TIME-002 | Manter RTC durante falta de alimentação por bateria de backup | ensaio de 72 h |
| TIME-003 | Marcar dado sem tempo confiável com qualidade específica | teste unitário e integração |

### 3.2 Modbus RTU

| ID | Requisito | Aceite |
|---|---|---|
| MB-001 | Operar como mestre em duas portas RS-485 independentes | dois escravos simultâneos |
| MB-002 | Suportar 1.200–115.200 bit/s, 8N1, 8E1 e 8O1 | matriz de configuração |
| MB-003 | Suportar funções 01, 02, 03, 04, 05, 06, 15 e 16 | simulador Modbus |
| MB-004 | Agrupar leituras contíguas sem atravessar dispositivo, função ou limite configurado | teste do planejador |
| MB-005 | Limitar o MVP a 32 escravos e 128 pontos no total | validação do schema |
| MB-006 | Possuir timeout, número de tentativas e intervalo configuráveis por dispositivo | injeção de timeout |
| MB-007 | Distinguir timeout, CRC, exceção Modbus, conversão e dado obsoleto | qualidade publicada |
| MB-008 | Terminação de 120 Ω e polarização devem ser selecionáveis por porta | inspeção e medição |

### 3.3 Entradas analógicas

| ID | Requisito | Aceite |
|---|---|---|
| AI-001 | Oferecer quatro canais single-ended com referência de campo comum | inspeção elétrica |
| AI-002 | Selecionar 0–10 V por software no ADC e 4–20 mA por shunt físico de 249 Ω, 0,1% | teste por canal |
| AI-003 | Usar aquisição de 16 bits; não prometer 16 bits efetivos | ruído/ENOB medidos |
| AI-004 | Alcançar erro total alvo ≤ ±0,2% do fundo de escala após calibração, 23 ±5 °C | calibrador de bancada |
| AI-005 | Permitir média, mediana, corte de espúrio e taxa de 1–100 amostras/s | testes do pipeline |
| AI-006 | Detectar corrente abaixo de 3,6 mA e acima de 21 mA como estados configuráveis | fonte de corrente |
| AI-007 | Impedir que um canal fora de faixa invalide os demais | injeção por canal |
| AI-008 | Registrar coeficientes de ganho/offset por canal e revisão de calibração | leitura/exportação |

### 3.4 Entradas digitais e pulsos

| ID | Requisito | Aceite |
|---|---|---|
| DI-001 | Oferecer quatro entradas de 24 V compatíveis com contato seco por fonte externa | bancada 0/24 V |
| DI-002 | Isolar galvanicamente as entradas da lógica | revisão e ensaio de isolação do protótipo |
| DI-003 | Permitir debounce configurável de 0–1.000 ms | teste temporal |
| DI-004 | Contar pulsos até 10 kHz com largura mínima de 50 µs no modo rápido | gerador de pulsos |
| DI-005 | Preservar totalizador em armazenamento não volátil sem escrever a cada pulso | teste de corte |
| DI-006 | Publicar estado, borda, contador e qualidade separadamente | contrato de telemetria |

### 3.5 Ethernet, Wi-Fi e serviços

| ID | Requisito | Aceite |
|---|---|---|
| NET-001 | Usar Ethernet 10/100 como enlace primário | DHCP e IP estático |
| NET-002 | Usar Wi-Fi somente como enlace opcional, sem impedir operação cabeada | módulo ausente/desabilitado |
| NET-003 | Não aceitar conexão de entrada oriunda de rede não confiável por padrão | varredura de portas |
| NET-004 | Expor REST/configuração somente na interface local autorizada | teste de ACL |
| NET-005 | Implementar DNS, DHCP, NTP e resolução de falhas separada por serviço | injeção de falha |
| NET-006 | Manter aquisição e buffer durante ausência total de rede | ensaio offline |

### 3.6 MQTT e dados

| ID | Requisito | Aceite |
|---|---|---|
| MQ-001 | Publicar por MQTT sobre TLS 1.2 ou superior | broker de homologação |
| MQ-002 | Usar autenticação mútua por certificado no modo de produção | teste de certificado válido/revogado |
| MQ-003 | Publicar telemetria com QoS 1 e identificador idempotente | reconexão e duplicata |
| MQ-004 | Separar tópicos de inventário, estado, telemetria, evento e diagnóstico | inspeção do broker |
| MQ-005 | Nunca registrar chave privada, senha ou token nos logs | teste automatizado |
| DATA-001 | Cada ponto deve carregar ID, valor, unidade, qualidade e tempo de aquisição | validação de schema |
| DATA-002 | Valor inválido não pode ser convertido silenciosamente em zero | teste unitário |
| DATA-003 | Escala deve usar expressão linear explícita ou enumeração versionada | validação de configuração |

### 3.7 Buffer e recuperação

| ID | Requisito | Aceite |
|---|---|---|
| BUF-001 | Armazenar pelo menos 1.000.000 de registros no perfil padrão | teste de capacidade |
| BUF-002 | Usar fila persistente limitada, com descarte do mais antigo somente após registrar contador | ensaio de saturação |
| BUF-003 | Recuperar arquivo/fila após corte em qualquer ponto de escrita | 100 ciclos de corte |
| BUF-004 | Reenviar em ordem de aquisição sem impedir dados atuais | teste de reconexão |
| BUF-005 | Aceitar duplicação de transporte e garantir ID idempotente | teste de QoS/reboot |
| BUF-006 | Sinalizar cartão ausente, somente leitura, cheio ou corrompido | matriz de falhas |

### 3.8 Configuração e atualização

| ID | Requisito | Aceite |
|---|---|---|
| CFG-001 | Validar toda configuração contra `gateway-config.schema.json` | suíte de configurações |
| CFG-002 | Aplicar configuração nova de forma transacional | corte durante aplicação |
| CFG-003 | Manter última configuração válida e cópia de fábrica | recuperação |
| CFG-004 | Rejeitar somente a entidade inválida quando isso não comprometer o conjunto | teste parcial |
| UPD-001 | Verificar assinatura e compatibilidade antes de atualizar | imagem alterada/incompatível |
| UPD-002 | Retornar à imagem anterior após falha de boot confirmada | teste de rollback |
| UPD-003 | Preservar identidade, calibração, totalizadores e configuração | regressão |

## 4. Requisitos não funcionais

| ID | Requisito | Meta do protótipo |
|---|---|---|
| PERF-001 | Latência aquisição→publicação com rede disponível | ≤ 2 s no perfil padrão |
| PERF-002 | Ocupação sustentada de CPU | < 70% |
| PERF-003 | Memória dinâmica | proibida após inicialização no núcleo de aquisição |
| REL-001 | Operação contínua | 30 dias sem travamento |
| REL-002 | Watchdog | hardware independente e causa de reset registrada |
| REL-003 | Brownout | nenhuma configuração parcial; reinício seguro |
| SEC-001 | Raiz de confiança | recursos de segurança/TrustZone do STM32H563 |
| SEC-002 | Debug de produção | política documentada de bloqueio e recuperação |
| DOC-001 | Reprodutibilidade | build, teste e artefatos vinculados a commit |
| MAINT-001 | Diagnóstico | exportável sem segredos e sem depender da nuvem |

## 5. Fora do MVP

- OPC-UA;
- aquisição CAN e transmissão CAN ativa;
- saídas digitais ou analógicas;
- lógica de controle capaz de comandar processo;
- modem 4G integrado;
- alimentação por rede elétrica;
- classificação SIL/PL, certificação EMC ou conformidade comercial;
- funcionamento externo, atmosfera explosiva ou temperatura industrial completa.

## 6. Gates

1. **G0 — contratos:** requisitos, ADRs, schemas e núcleo testável no host.
2. **G1 — elétrica:** esquema, cálculos, ERC e revisão independente.
3. **G2 — mecânica/PCB:** layout, DRC, isolação, envelopes e pacote P0.
4. **G3 — bring-up:** fontes, clocks, debug, armazenamento e fail-safe.
5. **G4 — I/O:** RS-485, analógicas e digitais em bancada.
6. **G5 — rede:** Ethernet, TLS, MQTT, buffer e recuperação.
7. **G6 — piloto:** 30 dias somente de monitoramento.

Nenhum gate posterior transforma metas anteriores em resultados medidos sem
evidência anexada.
