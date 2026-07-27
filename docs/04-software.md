# Software e firmware EDGE-18

## 1. Plataforma

- linguagem do núcleo: C17;
- RTOS-alvo: FreeRTOS;
- rede: LwIP;
- TLS: mbedTLS;
- MQTT: cliente com QoS 1 e sessão controlada;
- armazenamento: camada própria sobre FatFs/driver de bloco;
- build: CMake para núcleo host; toolchain Arm para alvo;
- schemas: JSON Schema Draft 2020-12;
- testes: executáveis no host sem placa e testes HIL no protótipo.

O código de domínio não incluirá headers da HAL STM32. A porta alvo implementa
interfaces pequenas de tempo, armazenamento, serial, rede e entropia.

## 2. Módulos

| Módulo | Responsabilidade |
|---|---|
| `edge_point` | valor, tipo, unidade, timestamp e qualidade |
| `edge_queue` | fila limitada em RAM, política de pressão e métricas |
| `edge_config` | validação semântica de dispositivos, referências e pontos |
| `edge_scheduler` | agenda leituras com fase e backoff sem bloquear portas |
| `modbus_master` | framing, CRC, respostas, exceções e endian |
| `analog_input` | aquisição, filtros, calibração e diagnóstico |
| `digital_input` | debounce, bordas, frequência e totalizadores |
| `persistent_log` | journal com CRC/commit, recuperação e compactação |
| `mqtt_transport` | envelope limitado, QoS, reconexão e idempotência |
| `health` | watchdog, reset cause, recursos e self-test |
| `secure_update` | alvo, hash, assinatura, contador e rollback |

O núcleo host implementado corresponde a `edge_point`, `edge_queue`,
`edge_config`, `edge_scheduler`, framing/decodificação de `modbus_master`,
formato de `persistent_log`, envelope de telemetria, máquina de estados e
validação de manifesto. Drivers STM32, RTOS, rede e sistema de arquivos ficam
na porta de hardware e só podem ser considerados concluídos após integração
HIL.

## 3. Tarefas previstas

| Tarefa | Prioridade | Período/evento | Watchdog |
|---|---:|---|---|
| supervisor | máxima | 100 ms | alimenta IWDG após consenso |
| entradas digitais | alta | interrupção + 1 ms | contador de progresso |
| aquisição analógica | alta | 10–1.000 ms | deadline |
| Modbus A/B | alta | por agenda | deadline por transação |
| persistência | média | fila/evento | backlog máximo |
| publicador MQTT | média | fila/rede | heartbeat |
| rede/tempo | média | eventos | estado |
| REST/configuração | baixa | conexão local | timeout |
| diagnóstico | baixa | 1 s | não crítico |

Somente o supervisor alimenta o watchdog, e apenas quando as tarefas críticas
avançaram dentro da janela.

## 4. Memória

- nenhuma alocação dinâmica no caminho de aquisição após o boot;
- tabelas de até 32 dispositivos e 128 pontos alocadas na promoção de
  configuração;
- buffers de protocolo têm limites compilados;
- mensagens grandes são serializadas por partes;
- certificados e chaves possuem área dedicada;
- métricas incluem high-water mark de pilha, heap e filas.

## 5. Qualidade do ponto

A qualidade é uma máscara de bits. `GOOD` é zero; falhas podem coexistir.

| Bit | Nome | Significado |
|---:|---|---|
| 0 | `COMM_TIMEOUT` | dispositivo não respondeu |
| 1 | `COMM_CRC` | quadro corrompido |
| 2 | `PROTOCOL_EXCEPTION` | exceção do protocolo |
| 3 | `OUT_OF_RANGE` | fora da faixa configurada |
| 4 | `SENSOR_FAULT` | diagnóstico do canal |
| 5 | `STALE` | idade maior que o limite |
| 6 | `TIME_UNSYNCED` | UTC não confiável |
| 7 | `CONVERSION_ERROR` | tipo/escala inválidos |
| 8 | `CONFIG_ERROR` | entidade desabilitada pela configuração |
| 9 | `STORAGE_DEGRADED` | persistência não garantida |

Um valor pode ser transportado para diagnóstico com qualidade ruim, mas
consumidores não devem tratá-lo como medida válida.

## 6. Fila

O núcleo implementa fila limitada em RAM e um codec de journal testável no
host. A porta de persistência no microSD deve preservar:

- cabeçalho, versão, comprimento, sequência e CRC;
- marcador de commit de 32 bits gravado por último;
- recuperação até o último registro completo;
- segmentos fechados imutáveis;
- confirmação MQTT por faixa de sequência;
- descarte do segmento mais antigo somente com métrica e evento.

## 7. Atualização

1. baixar por canal autenticado;
2. validar manifesto, hardware, tamanho e hash;
3. verificar assinatura na zona segura;
4. gravar slot inativo/staging;
5. reiniciar em modo de tentativa;
6. executar self-test e marcar boot saudável;
7. reverter automaticamente se o prazo expirar.

O validador implementado rejeita alvo incompatível, imagem vazia ou grande
demais, contador de segurança não crescente, digest SHA-256 nulo e assinatura
inválida. A criptografia é injetada por callback para que a implementação de
alvo use a zona segura, sem uma falsa verificação no código portátil.

## 8. Critérios de código

- warnings tratados como erro;
- API documentada e tipos de largura explícita;
- nenhuma função bloqueante sem timeout;
- erros não convertidos em booleano genérico;
- logs estruturados, sem segredos;
- testes de limite, wrap-around, fila cheia e entradas inválidas;
- fuzzing futuro para parser de configuração e Modbus;
- CI executa build, testes, schemas e verificações de documentação.
