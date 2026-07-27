# Firmware EDGE-18

## Estado

O primeiro núcleo host-testable está implementado:

- modelo fixo de ponto e máscara de qualidade;
- validação de identificadores;
- fila limitada com políticas `reject-new` e `drop-oldest`;
- métricas de inserção, remoção e descarte;
- CRC-16 Modbus;
- testes de wrap-around, overflow, qualidade e entradas inválidas.

Não existe ainda firmware STM32 inicializável. O código atual prova contratos do
domínio sem fingir que drivers, FreeRTOS, Ethernet ou armazenamento estão
prontos.

## Build no computador

```bash
cmake -S .. -B ../build/host -DCMAKE_BUILD_TYPE=Debug
cmake --build ../build/host
ctest --test-dir ../build/host --output-on-failure
```

## Próximas portas

1. `platform/host` para testes de tempo e arquivo;
2. `platform/stm32h563` para clock, watchdog e UART;
3. FreeRTOS e supervisor;
4. Modbus mestre;
5. journal persistente;
6. LwIP/mbedTLS/MQTT.
