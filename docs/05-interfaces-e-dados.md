# Interfaces e dados EDGE-18

## 1. Conectores da Rev. A

| ID | Interface | Sinais | Domínio |
|---|---|---|---|
| J1 | alimentação | VIN+, VIN−, CHASSIS | 9–36 Vcc |
| J2 | SWD ARM 10 pinos | SWDIO, SWCLK, SWO, NRST, 3V3, GND | produção |
| J3 | microSD | SDMMC 4 bits, detect, 3V3, GND, shield | armazenamento |
| J4 | USB-C serviço | USB 2.0 FS device, CC1/CC2, VBUS, GND, shield | lógica/serviço |
| J5 | Ethernet | RJ45 blindado com magnetics e LEDs | magneticamente isolado |
| J6 | serviço/expansão | 3V3, GND, I2C, UART, GPIO, NRST | lógica |
| J10 | analógica 1 | AI1_FIELD, AGND | campo comum |
| J11 | analógica 2 | AI2_FIELD, AGND | campo comum |
| J12 | analógica 3 | AI3_FIELD, AGND | campo comum |
| J13 | analógica 4 | AI4_FIELD, AGND | campo comum |
| J14 | digitais 1–4 | DI1_FIELD…DI4_FIELD, DI_FIELD_GND | campo isolado |
| J15 | RS-485 A | A+, B−, RS485A_GND | isolado |
| J16 | RS-485 B | A+, B−, RS485B_GND | isolado |
| J17 | CAN-FD | CAN-H, CAN-L, CAN_GND | isolado, reservado |

Essa numeração corresponde ao esquemático Rev. A. Ela ainda não autoriza a
montagem de chicote: pinout, chaveamento e polaridade devem ser confirmados
contra a revisão que vier a ser liberada para fabricação.

## 2. Configuração

O arquivo de configuração possui:

- `schema_version`;
- identidade lógica e site;
- rede e tempo;
- dispositivos;
- pontos;
- política de armazenamento;
- broker e tópicos;
- diagnóstico.

A fonte normativa é `schemas/gateway-config.schema.json`. Campos desconhecidos
são rejeitados no MVP para impedir interpretações silenciosas.

## 3. Modelo de ponto

| Campo | Tipo | Regra |
|---|---|---|
| `point_id` | string | único, 1–48 caracteres seguros para tópico |
| `sequence` | uint64 | monotônico por dispositivo |
| `timestamp_ms` | int64 | UTC Unix em ms; zero se não confiável |
| `monotonic_ms` | uint64 | sempre presente desde o boot |
| `value_type` | enum | bool, i64, u64, f64 ou string curta |
| `value` | variante | não substitui qualidade |
| `unit` | string | UCUM quando aplicável |
| `quality` | uint32 | máscara documentada |
| `source` | string | dispositivo/canal |
| `config_revision` | uint32 | revisão que produziu o valor |

## 4. Tópicos MQTT v1

Prefixo:

```text
edge/v1/{tenant}/{site}/{device}/
```

| Sufixo | Retain | QoS | Conteúdo |
|---|---:|---:|---|
| `inventory` | sim | 1 | hardware, versões e capacidades |
| `state` | sim | 1 | online, boot ID, saúde resumida |
| `telemetry` | não | 1 | lote de pontos |
| `events` | não | 1 | mudança de estado, falha e auditoria |
| `diagnostics` | não | 0/1 | métricas sem segredos |

Comandos remotos não fazem parte do MQTT v1. Configuração remota futura terá
canal separado, assinatura e política explícita.

## 5. Envelope de telemetria

Exemplo informativo:

```json
{
  "schema": "edge.telemetry/1",
  "device_id": "edge18-000001",
  "boot_id": "9f462527",
  "message_id": "0000000000018a42",
  "sent_at_ms": 1785100000123,
  "points": [
    {
      "point_id": "tank.level",
      "sequence": 18720,
      "timestamp_ms": 1785099999980,
      "monotonic_ms": 623991,
      "value_type": "f64",
      "value": 73.2,
      "unit": "%",
      "quality": 0,
      "source": "ai1",
      "config_revision": 4
    }
  ]
}
```

## 6. Idempotência

`device_id + boot_id + message_id` identifica uma publicação. `point_id +
sequence` identifica uma amostra. O backend aceita repetição por QoS 1 e não
depende de entrega exatamente uma vez.

## 7. REST local

Recursos previstos:

- `GET /v1/health`;
- `GET /v1/inventory`;
- `GET /v1/config`;
- `PUT /v1/config/staging`;
- `POST /v1/config/validate`;
- `POST /v1/config/commit`;
- `POST /v1/config/rollback`;
- `GET /v1/diagnostics/export`.

REST exige autenticação, limite de tamanho, timeout e log de auditoria. A API não
expõe chave privada nem endpoint de comando físico.

## 8. Modbus

Um ponto Modbus define porta, escravo, função, endereço, quantidade, tipo,
endian, escala, unidade, período, timeout, tentativas e idade máxima. Endereços
internos são base zero. A UI pode exibir notação 4xxxx, mas deve converter de
forma explícita.

## 9. Compatibilidade

- breaking changes incrementam a versão do schema/tópico;
- consumidores devem ignorar qualidade desconhecida somente quando o bit for
  declarado extensível;
- firmware não promove configuração de versão superior;
- migração nunca altera calibração sem registro separado.
