# Arquitetura do sistema

## Contexto

Integrar equipamentos legados a MQTT/REST por configuração web, com qualidade de dados, regras locais e buffer offline.

## Fluxo funcional

```text
fontes/sensores → proteção e aquisição → processamento local
        → armazenamento/buffer → comunicação → aplicação/operador
        ← configuração autorizada, versionada e auditável
```

O sentido de retorno representa configuração; comandos que possam produzir
efeito físico só serão habilitados quando estiverem explicitamente no escopo e
possuírem intertravamentos.

## Blocos de hardware

- MCU com RTOS
- duas RS-485 isoladas
- CAN futuro
- I/O protegido
- Ethernet/Wi-Fi
- caixa DIN

## Blocos de software

- scheduler de aquisição
- Modbus mestre
- modelo JSON
- editor web
- MQTT/REST
- fila e atualização com rollback

## Interfaces de fronteira

- Modbus RTU/TCP
- CAN futuro
- 4–20 mA/0–10 V
- pulso/contato
- Ethernet/Wi-Fi
- MQTT/REST

## Princípios

- aquisição e função segura continuam operando sem backend;
- transporte não altera unidade, qualidade ou significado do dado;
- drivers, domínio e apresentação permanecem desacoplados;
- hardware específico fica atrás de uma HAL ou adaptador testável;
- estados de boot, reset, brownout, sensor inválido e link ausente são definidos;
- relógio, identidade, configuração e calibração têm origem conhecida.

## Distribuição prevista

- simuladores Modbus
- perfis de equipamentos
- painel industrial piloto
- programa de integradores

Diagramas elétricos, de implantação, sequência e estados serão adicionados às
fontes editáveis antes do gate de protótipo.
