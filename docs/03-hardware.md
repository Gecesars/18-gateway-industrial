# Hardware

## Blocos previstos

| ID | Bloco | Estado |
|---|---|---|
| HW-18-01 | MCU com RTOS | a selecionar/projetar |
| HW-18-02 | duas RS-485 isoladas | a selecionar/projetar |
| HW-18-03 | CAN futuro | a selecionar/projetar |
| HW-18-04 | I/O protegido | a selecionar/projetar |
| HW-18-05 | Ethernet/Wi-Fi | a selecionar/projetar |
| HW-18-06 | caixa DIN | a selecionar/projetar |

## Entregáveis obrigatórios

- esquemático editável com revisão e notas de projeto;
- PCB com regras de classe, stack-up, DRC e revisão visual;
- bibliotecas locais para símbolos/footprints não padronizados;
- BOM com fabricante, MPN, quantidade, substitutos e estado de estoque;
- arquivos de fabricação gerados de commit identificado;
- desenho de montagem, chicotes, pinagem e pontos de teste;
- orçamento de potência e árvore de alimentação;
- análise de falhas de boot/reset e proteções;
- modelo 3D mecânico e verificação de envelopes quando houver gabinete.

## Regras de desenvolvimento

1. Selecionar componentes por requisitos elétricos, ambientais e de ciclo de
   vida, não apenas por disponibilidade imediata.
2. Registrar cálculos de dissipação, margens de tensão/corrente e tolerâncias.
3. Separar domínio sensível, potência e comunicação no esquema e layout.
4. Qualquer exceção de roteamento deve ser local, justificada e auditável.
5. Revisar footprint contra desenho do fabricante e, no protótipo, contra a peça
   física antes do pedido.

## Estado atual

Não há fonte eletrônica criada nesta baseline. A lista acima é arquitetura
pretendida e deverá ser transformada em requisitos elétricos antes do KiCad.
