# BOM e montagem — EDGE-18 Rev. A

## 1. Fontes normativas

- BOM por posição: `hardware/bom/edge18-main-rev-a-source.csv`;
- BOM agrupada: `release/edge18-rev-a/assembly/edge18-main-rev-a-bom-grouped.csv`;
- posição: `release/edge18-rev-a/assembly/edge18-main-rev-a-position.csv`;
- desenho: `release/edge18-rev-a/documents/edge18-main-rev-a-assembly.pdf`;
- netlist de teste: `release/edge18-rev-a/assembly/edge18-main-rev-a.ipc`.

A BOM possui 181 posições e 113 linhas agrupadas. Nenhuma posição tem
fabricante ou MPN vazio. Substituição exige comparar encapsulamento, tensão,
potência, tolerância, temperatura, lifecycle e parâmetros elétricos.

## 2. DNP padrão

| Referências | Motivo |
|---|---|
| `U8` | ESP32-C3-WROOM-02 opcional |
| `C46` | bulk local do módulo Wi-Fi |
| `R48`, `R49` | pull-ups EN/BOOT do módulo Wi-Fi |

Para montar Wi-Fi, popular os quatro itens juntos, revisar o keep-out da antena
no gabinete e carregar firmware compatível. Não montar apenas parte do conjunto.

## 3. Opções configuráveis

| Referência | Padrão | Fechado quando |
|---|---|---|
| `JP1` | aberto | AI1 em 4–20 mA |
| `JP2` | aberto | AI2 em 4–20 mA |
| `JP3` | aberto | AI3 em 4–20 mA |
| `JP4` | aberto | AI4 em 4–20 mA |
| `JP5` | aberto | RS-485 A é extremidade do barramento |
| `JP6` | aberto | RS-485 B é extremidade do barramento |
| `JP7` | aberto | CAN é extremidade do barramento |

O modo da configuração deve coincidir com o jumper físico. Nunca fechar duas
terminações adicionais em uma rede já terminada.

## 4. Pontos críticos de montagem

1. inspecionar polaridade de `D1`, `D2`, TVS e LEDs;
2. verificar voiding e pasta nos exposed pads de `U1`, `U2`, `U7` e `U8`;
3. confirmar que os rasgos sob `U12`, `U13` e `U14` foram usinados;
4. não preencher os rasgos com cola, coating condutivo ou fixador;
5. manter `R68` como única união intencional `AGND`–`GND`;
6. lavar resíduos entre os domínios isolados;
7. conferir os bornes de 5,08 mm e sua orientação antes do reflow/onda;
8. montar a bateria CR1220 somente após limpeza e inspeção;
9. aplicar etiqueta Rev. A e número de série antes do teste funcional.

## 5. Sequência de inspeção

- AOI de polaridade, ponte e ausência;
- raio X dos exposed pads quando disponível;
- continuidade/curto dos rails com fonte desligada;
- teste elétrico pelo IPC-D-356;
- alimentação inicial em 9 V com limite de 100 mA e módulos isolados sem carga;
- validação de 5 V, 3,3 V, reset, clocks e consumo;
- só então conectar SWD, interfaces de campo e Ethernet.

O primeiro artigo não deve ser conectado simultaneamente a alimentação de campo,
USB aterrada e instrumentos não isolados sem revisar laços de terra.
