# Orçamento preliminar de pinos e periféricos

Este documento reserva periféricos; não é pinout de PCB. Atribuições físicas
serão conferidas no datasheet, CubeMX e ERC antes do esquema.

| Função | Periférico previsto | Sinais/recursos |
|---|---|---|
| Ethernet | ETH RMII | REF_CLK, MDIO/MDC, CRS_DV, RXD0/1, TX_EN, TXD0/1, reset/IRQ |
| RS-485 A | USART2 | TX, RX, DE |
| RS-485 B | USART3 | TX, RX, DE |
| Wi-Fi | UART7 + SPI opcional | TX, RX, CTS, RTS, EN, BOOT, CS/SCK/MISO/MOSI |
| ADC externo | SPI1 | SCK, MISO, MOSI, CS, RST, BUSY/ALARM |
| CAN | FDCAN1 | TX, RX, STB/EN |
| microSD | SDMMC1 | CK, CMD, D0–D3, card detect |
| flash staging | OCTOSPI1 | CK, CS e IO0–IO3/7 conforme memória |
| USB serviço | USB FS | DM, DP, VBUS sense |
| entradas digitais | TIM/GPIO | DI1–DI4, quatro canais de captura |
| RTC | LSE | OSC32_IN/OUT e VBAT |
| debug | SWD | SWDIO, SWCLK, SWO, NRST |
| supervisão | ADC interno/GPIO | VIN, 5V, 3V3, PGOOD, temperatura |
| status | GPIO/PWM | LEDs e buzzer opcional |

## Restrições

- evitar conflito com pinos de boot e debug;
- preservar console de recuperação independente do Wi-Fi;
- entradas de captura devem estar em timers adequados;
- RMII tem prioridade sobre funções alternativas;
- pinos do domínio seguro são definidos antes da aplicação;
- nenhum sinal de campo liga diretamente ao MCU;
- reservar pelo menos oito GPIO e uma UART para expansão/produção.

## Gate do pinout

O pinout só será aceito quando:

1. tabela completa de pinos estiver ligada ao símbolo KiCad;
2. todas as funções alternativas forem verificadas;
3. clocks e DMA forem mapeados;
4. conflitos de interrupção forem analisados;
5. CubeMX/projeto de referência concordarem;
6. ERC e checklist manual estiverem limpos.
