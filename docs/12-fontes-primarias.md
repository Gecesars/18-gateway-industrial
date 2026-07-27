# Fontes primárias e seleção de componentes

**Consulta:** 2026-07-26. Use sempre a revisão mais nova antes de congelar BOM ou
footprint.

## Controlador

- [STM32H563ZI — página oficial ST](https://www.st.com/en/microcontrollers-microprocessors/stm32h563zi.html)
- [STM32H562/H563 — datasheet oficial](https://www.st.com/resource/en/datasheet/stm32h563zi.pdf)

Motivo: Cortex-M33 com TrustZone, 2 MB de flash, 640 KB de RAM, Ethernet MAC,
dois FDCAN, SDMMC, USB e periféricos suficientes no LQFP-144. A seleção não
dispensa pinout completo, errata e disponibilidade.

## Ethernet e Wi-Fi

- [LAN8742A — datasheet Microchip](https://ww1.microchip.com/downloads/en/DeviceDoc/8742a.pdf)
- [ESP32-C3-WROOM-02 — datasheet Espressif](https://www.espressif.com/sites/default/files/documentation/esp32-c3-wroom-02_datasheet_en.pdf)

O LAN8742A fornece o PHY RMII. O ESP32-C3 é coprocessador opcional; o STM32
continua autoridade e suporta funcionamento sem rádio.

## Aquisição analógica

- [ADS8684 — produto e documentação TI](https://www.ti.com/product/ADS8684)
- [ADS8684 — datasheet](https://www.ti.com/lit/ds/symlink/ads8684.pdf)

O ADS8684 reúne quatro canais, 16 bits, SPI, faixas programáveis unipolares e
bipolares, referência interna e proteção de entrada especificada pelo fabricante.
Proteção interna não substitui TVS, filtro, resistor e análise de surto da placa.

## Interfaces isoladas

- [ISO1212 — entradas digitais TI](https://www.ti.com/product/ISO1212)
- [ISOW1412 — RS-485 com potência isolada TI](https://www.ti.com/product/ISOW1412)
- [ISOW1412 — datasheet](https://www.ti.com/lit/ds/symlink/isow1412.pdf)
- [ISOW1044 — CAN-FD com potência isolada TI](https://www.ti.com/product/ISOW1044)

O ISO1212 atende entradas industriais de 24–60 V conforme a configuração de
resistores. ISOW1412 e ISOW1044 integram a potência das três interfaces de
barramento isoladas. Uma solução com transceptor e DC/DC separados permanece
alternativa se ruído, custo ou estoque exigirem.

## Alimentação

- [LM76002 — buck 3,5–60 V/2,5 A TI](https://www.ti.com/product/LM76002)

A faixa do CI oferece margem sobre 36 V nominal. O envelope final depende de
todos os componentes da entrada, do layout e dos ensaios.

## Documentos ainda obrigatórios

- errata do STM32H563;
- reference manual e hardware development guide do STM32H5;
- layout RMII e recomendações do PHY/magnetics;
- guias de layout dos isoladores e do ADC;
- relatórios de lifecycle/PCN e estoque no congelamento da BOM;
- normas aplicáveis na edição escolhida para comercialização.
