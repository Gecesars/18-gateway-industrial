# Arquitetura EDGE-18

## 1. Decisão principal

O STM32H563ZIT6 é a autoridade do equipamento: adquire, valida, registra e
decide o que pode sair da unidade. Ethernet é nativa ao MCU por RMII. O
ESP32-C3-MINI-1 é um coprocessador opcional de Wi-Fi e nunca armazena a raiz de
identidade do produto. Ausência, reset ou comprometimento do módulo Wi-Fi não
interrompe a aquisição cabeada.

## 2. Diagrama de blocos

```text
  9–36 Vdc
      │
  proteção + LM76002 ── 5 V ── 3,3 V ─────────────────────────────┐
      │                                                           │
      │     ┌──────────────── STM32H563ZIT6 ────────────────┐      │
      │     │ TrustZone / FreeRTOS / watchdog / RTC         │      │
      │     │                                                │      │
      │     │ SPI1 ─ ADS8684 ─ AI1..AI4 0–10 V / 4–20 mA    │      │
      │     │ GPIO/TIM ─ 2× ISO1212 ─ DI1..DI4 / pulso      │      │
      │     │ UART ─ ISOW1412 ─ RS485-A                     │      │
      │     │ UART ─ ISOW1412 ─ RS485-B                     │      │
      │     │ FDCAN ─ ISO1042 + DC/DC ─ CAN (fase 2)        │      │
      │     │ RMII ─ LAN8742A ─ magnetics/RJ45              │      │
      │     │ UART/SPI ─ ESP32-C3-MINI-1 (opcional)         │      │
      │     │ SDMMC ─ microSD; OctoSPI ─ flash de staging   │      │
      │     │ USB FS ─ USB-C de serviço; SWD de produção    │      │
      │     └────────────────────────────────────────────────┘      │
      └─────────────────────────────────────────────────────────────┘
```

## 3. Domínios elétricos

| Domínio | Referência | Observação |
|---|---|---|
| lógica | `DGND` | MCU, Ethernet, USB, armazenamento e Wi-Fi |
| analógico de campo | `AGND_FIELD` | quatro AI compartilham referência; não são isoladas entre si |
| RS-485 A | `GND_485A` | barreira e potência isolada próprias |
| RS-485 B | `GND_485B` | barreira e potência isolada próprias |
| CAN | `GND_CAN` | barreira ISO1042 e DC/DC próprio |
| entradas digitais | `FGND_DI` | isolamento para lógica; retorno de campo documentado |
| chassi | `CHASSIS` | ligação controlada a blindagens e gabinete |

`AGND_FIELD` e `DGND` serão unidos somente no ponto definido pelo projeto do
front-end/ADC. Essa união não deve ser confundida com isolação de canal.

## 4. Partições de firmware

```text
secure boot / identidade / verificação de imagem
                         │
HAL ─ drivers ─ aquisição ─ modelo de pontos ─ regras somente leitura
                         │                 │
                         ├─ fila RAM ─ armazenamento persistente
                         │                 │
                         └─ publicador ─ MQTT/TLS ─ broker
                                           │
configuração validada ─ staging ─ commit ──┘
```

### 4.1 Camada segura

- boot verificado;
- identidade e material criptográfico;
- política de debug;
- contador de rollback e versão mínima;
- verificação da configuração antes da promoção.

### 4.2 Núcleo determinístico

- relógio monotônico;
- planejador de leituras;
- drivers sem alocação dinâmica depois do boot;
- qualidade de ponto;
- watchdog e supervisão de tarefas;
- fila em RAM com pressão de retorno explícita.

### 4.3 Serviços

- armazenamento em microSD;
- Ethernet/LwIP;
- mbedTLS;
- MQTT;
- NTP/DNS/DHCP;
- configuração REST local;
- ponte para o coprocessador Wi-Fi.

## 5. Fluxo de configuração

1. receber documento em área de staging;
2. verificar autenticação, tamanho, hash e versão do schema;
3. validar sintaxe e semântica;
4. construir nova tabela de dispositivos/pontos fora da tabela ativa;
5. verificar recursos, conflitos e limites;
6. gravar cópia persistente com CRC/hash;
7. trocar ponteiro ativo em transação curta;
8. manter última versão válida para rollback;
9. registrar autor, origem, versão e resultado.

## 6. Fluxo de telemetria

1. driver entrega amostra bruta e diagnóstico;
2. conversor aplica tipo, endian, escala e calibração;
3. validador atribui qualidade;
4. ponto recebe timestamp monotônico e UTC quando confiável;
5. política de mudança/período decide registrar;
6. registro entra na fila persistente;
7. publicador atribui `message_id`;
8. confirmação QoS remove o item elegível;
9. métricas registram atraso, repetição e descarte.

## 7. Reutilização pelos projetos filhos

O EDGE-18 publicará três contratos versionados:

- `edge-hal`: relógio, armazenamento, rede, serial, ADC e GPIO;
- `edge-model`: ponto, qualidade, unidade, configuração e eventos;
- `edge-transport`: envelope MQTT, identidade, fila e diagnóstico.

Projetos filhos adicionam adaptadores e perfis. Eles não devem copiar drivers ou
alterar schemas silenciosamente. Dependências usam tags imutáveis e changelog.

## 8. Estados operacionais

| Estado | Aquisição | Buffer | Publicação | Configuração |
|---|---|---|---|---|
| `BOOT` | não | recuperação | não | não |
| `SAFE` | diagnóstico | sim | saúde | somente serviço local |
| `RUN_LOCAL` | sim | sim | não | local autenticada |
| `RUN_ONLINE` | sim | sim | sim | conforme política |
| `DEGRADED` | parcial | sim | saúde + válidos | bloqueada se recursos insuficientes |
| `UPDATE` | congelada/limitada | preservado | não | somente pacote assinado |
| `RECOVERY` | não | preservado | não | imagem/configuração anterior |

## 9. Restrições

- Wi-Fi não é caminho obrigatório.
- CAN não será ativado no MVP.
- Não existem saídas de controle no P0.
- O gateway não substitui CLP, relé de segurança ou proteção de processo.
- Isolação e EMC permanecem metas até ensaios do protótipo.
