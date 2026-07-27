# Porta STM32H563 — EDGE-18 Rev. A

## Contrato

`board_pins.h` espelha as nets ligadas ao U3 no KiCad. O alvo deve ser criado
para `STM32H563ZIT6`, LQFP-144, com:

- HSE de 25 MHz e LSE de 32,768 kHz;
- SYSCLK/HCLK de até 250 MHz;
- clock USB de 48 MHz e RMII de 50 MHz conforme árvore validada;
- I-cache, MPU e TrustZone configurados antes da aplicação;
- IWDG alimentado somente pelo supervisor;
- RNG usado para boot ID, TLS e nonces;
- SWD preservado na fabricação.

## Ordem de inicialização

1. ler causa de reset e manter saídas de controle inexistentes;
2. clock, alimentação e cache;
3. MPU/TrustZone e proteção de chaves;
4. GPIO em estados seguros;
5. RTC, monotônico e watchdog;
6. SPI/SDMMC/UART/FDCAN/RMII/USB;
7. recuperar configuração e journal;
8. iniciar FreeRTOS;
9. self-test e promoção para `running` ou `degraded`.

## Regras de drivers

- UART RS-485 sempre tem timeout, controle DE e drenagem do último stop bit;
- DMA não aponta para memória liberada ou stack expirada;
- SDMMC grava payload/CRC antes do marcador de commit;
- falha do microSD mantém aquisição com qualidade `STORAGE_DEGRADED`;
- CAN permanece standby no MVP;
- Wi-Fi fica em reset quando os quatro itens DNP não estão montados;
- erro de clock, PGOOD ou self-test impede publicação de telemetria como boa.

## Geração do projeto

O projeto STM32CubeIDE/CMake de alvo deve ser gerado a partir do pinout
normativo e fixar a versão do STM32CubeH5. Arquivos gerados pelo Cube não são
forjados neste repositório sem a ferramenta e sem build ARM reproduzível.
O núcleo em `firmware/src` permanece independente da HAL e já é compilado e
testado no host.
