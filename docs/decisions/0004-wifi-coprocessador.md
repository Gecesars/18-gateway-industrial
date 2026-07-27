# ADR 0004 — Wi-Fi como coprocessador opcional

- Estado: aceito para P0
- Data: 2026-07-26

## Decisão

Ethernet no STM32 é a rede principal. ESP32-C3-WROOM-02 fornece Wi-Fi opcional e
pode ser removido/desenergizado. Ele não controla I/O nem conserva a identidade
raiz.

## Consequências

É necessário protocolo interno e atualização coordenada de dois firmwares, mas
falha do rádio não derruba aquisição ou Ethernet.
