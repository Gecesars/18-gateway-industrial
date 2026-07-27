# ADR 0003 — isolamento das interfaces de campo

- Estado: aceito para P0
- Data: 2026-07-26

## Decisão

As duas RS-485 usam ISOW1412 e o CAN usa ISOW1044, todos com potência isolada
integrada e domínio próprio. As quatro entradas digitais
serão isoladas da lógica. As analógicas compartilharão referência de campo e não
serão isoladas individualmente no P0.

## Consequências

O manual deve declarar a referência comum das analógicas. Aplicações que exigem
isolação canal a canal precisarão de módulo específico.
