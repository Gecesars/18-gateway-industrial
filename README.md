# EDGE-18 — Gateway Industrial Modbus/CAN Universal

Plataforma-pai para aquisição industrial e telemetria dos demais projetos do
portfólio. O EDGE-18 lê Modbus RTU, quatro sinais 0–10 V/4–20 mA e quatro
entradas digitais/pulso, conserva dados offline e publica por MQTT/TLS.

> **Estado: Gate G0 em desenvolvimento.**
> Arquitetura, contratos, schemas, núcleo testável no host e modelo mecânico
> dimensional P0 existem. Não há esquemático, PCB, firmware STM32 inicializável
> ou protótipo físico. Nada está liberado para fabricação ou instalação.

## Arquitetura P0

| Bloco | Seleção |
|---|---|
| MCU | STM32H563ZIT6, Cortex-M33/TrustZone |
| Ethernet | LAN8742Ai, RMII 10/100 |
| Wi-Fi | ESP32-C3-MINI-1 opcional |
| RS-485 | 2 × ISOW1412 isoladas |
| Analógicas | ADS8684, quatro canais de 16 bits |
| Digitais | 2 × ISO1212, quatro entradas de 24 V |
| CAN | ISO1042 reservado para fase 2 |
| Alimentação | 9–36 Vcc; LM76002 como referência |
| PCB | 180 × 120 mm, quatro camadas |

O MVP é somente de monitoramento. Não possui saídas de comando e não substitui
CLP ou relé de segurança.

## Implementado

- requisitos verificáveis e seis ADRs;
- arquitetura elétrica e de software;
- contratos de configuração e telemetria em JSON Schema;
- exemplos válidos;
- modelo C17 de ponto/qualidade;
- fila limitada com métricas e políticas de overflow;
- CRC-16 Modbus;
- conjunto dimensional FreeCAD/STEP do gabinete e PCB;
- testes no host e CI.

## Verificação local

```bash
./tools/run-checks.sh
```

## Navegação

- [índice técnico](docs/README.md);
- [requisitos](docs/01-requisitos.md);
- [arquitetura](docs/02-arquitetura.md);
- [hardware](docs/03-hardware.md);
- [software](docs/04-software.md);
- [fontes primárias](docs/12-fontes-primarias.md);
- [status](project-management/STATUS.md);
- [roadmap](project-management/ROADMAP.md).

## Licença

A licença ainda não foi definida. Não redistribua artefatos como se uma licença
já tivesse sido concedida.
