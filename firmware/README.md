# Firmware EDGE-18

## Estado

O núcleo C17 independente da HAL está implementado e testado no host:

- modelo fixo de ponto, máscara de qualidade e identificadores;
- fila limitada com políticas de overflow e métricas;
- validação semântica de tabelas de dispositivos e pontos;
- framing, CRC, validação e decodificação Modbus RTU;
- escalonador periódico com fase, backoff exponencial e saturação;
- journal binário com CRC, marcador de commit e recuperação de escrita
  interrompida;
- serialização limitada do envelope `edge.telemetry/1`;
- máquina de estados de boot, provisão, rede, degradação e atualização;
- validação de manifesto com alvo, tamanho, contador anti-rollback, digest e
  callback criptográfico.

A porta STM32H563 (HAL, FreeRTOS, LwIP, mbedTLS, FatFs e drivers de placa) é uma
camada separada e continua dependente de teste na PCB física. O código deste
diretório não simula que a integração eletroeletrônica já foi ensaiada.

## Build no computador

```bash
cmake -S .. -B ../build/host -DCMAKE_BUILD_TYPE=Debug
cmake --build ../build/host
ctest --test-dir ../build/host --output-on-failure
```

## Integração no STM32H563

As APIs de `include/edge` não dependem da HAL. A porta de alvo deve fornecer:

1. clock, MPU/TrustZone, RNG, RTC e IWDG;
2. FreeRTOS e supervisor que é o único alimentador do watchdog;
3. UART + DE das duas portas RS-485;
4. SPI do ADS8684, flash e microSD;
5. RMII/LwIP, mbedTLS e MQTT QoS 1;
6. armazenamento em bloco que grave o marcador de commit por último;
7. verificação real de assinatura no callback de `update_manifest`.

Não há alocação dinâmica no caminho de aquisição do núcleo.

O mapa de placa e a sequência de inicialização estão em
`platform/stm32h563/`.
