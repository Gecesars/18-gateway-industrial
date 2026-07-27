# Fabricação e implantação

## Estratégia inicial

- simuladores Modbus
- perfis de equipamentos
- painel industrial piloto
- programa de integradores

## Conteúdo previsto para um futuro pacote de fabricação

- Gerbers X2 das quatro camadas, máscaras, serigrafias e contorno;
- furação PTH/NPTH separada, mapa de furos e IPC-D-356;
- posição CSV sem itens DNP, BOM de fonte e BOM agrupada;
- esquemático e desenho de montagem em PDF;
- fonte mecânica FreeCAD e STEP da PCB/conjunto;
- especificação de PCB, material, cobre, acabamento e teste elétrico;
- instruções de montagem, torque, chicote, isolação e inspeção;
- firmware de produção, provisionamento e gabarito de fim de linha;
- etiqueta com projeto, revisão, número de série e avisos.

## Implantação

1. levantamento e registro do local;
2. conferência de compatibilidade e riscos;
3. instalação conforme desenho;
4. testes de aceitação do site;
5. backup da configuração e fotos;
6. entrega do as-built e treinamento;
7. janela de observação e plano de rollback.

O comando abaixo só conclui se ERC e DRC estiverem limpos e gera hashes e ZIP:

```bash
./tools/export-release.sh
```

Saídas futuras: `release/edge18-rev-a/` e `release/edge18-rev-a.zip`.

Na baseline congelada de 27 de julho de 2026, o comando falha corretamente
porque há 43 ocorrências de DRC e 24 conexões abertas. Nenhum Gerber foi
liberado. O relatório está em
[`reports/edge18-main-rev-a-drc.rpt`](reports/edge18-main-rev-a-drc.rpt).

Mesmo após um DRC limpo, o pacote não elimina análise DFM do fabricante,
inspeção de primeira peça, bring-up controlado, ensaio térmico, surto/EFT/ESD,
emissões/imunidade, isolamento e certificação aplicável.
