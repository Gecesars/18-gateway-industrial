# Changelog

## 2026-07-27 — baseline de revisão digital congelada

- interrompidas novas tentativas de roteamento por decisão do responsável;
- congelada a PCB com 43 ocorrências de DRC e 24 conexões abertas;
- confirmado que não há trilha abaixo de 0,25 mm;
- adicionados relatórios ERC/DRC integrais e documento de estado da PCB;
- exportado STEP da PCB corrente;
- explicitado em toda a documentação que a revisão não está liberada para
  fabricação.

## 2026-07-26 — engenharia digital Rev. A

- criado esquemático KiCad com 195 símbolos e ERC limpo;
- criada PCB de quatro camadas com 181 itens, classes de 0,25 a 1,20 mm;
- selecionados ESP32-C3-WROOM-02 e ISOW1044 com footprints oficiais;
- congeladas bibliotecas de símbolos e criada BOM sem campos de fabricante/MPN
  vazios;
- implementados configuração, Modbus, scheduler, journal, telemetria, máquina
  de estados e manifesto de atualização em C17;
- criado pinout completo, extraído automaticamente do CAD;
- mantida a distinção entre revisão digital e validação do protótipo físico.

## 2026-07-26 — início do desenvolvimento G0

- aprovado o Projeto 18 como plataforma-pai;
- detalhados requisitos, arquitetura, hardware, software, segurança e testes;
- selecionados STM32H563, LAN8742A, ESP32-C3, ADS8684, ISO1212, ISOW1412,
  ISO1042 e LM76002 como referências P0;
- criados seis ADRs e matriz de reutilização;
- criados schemas e exemplos de configuração/telemetria;
- implementado núcleo C17 com ponto, qualidade, fila e CRC Modbus;
- adicionados testes host e CI;
- gerado e validado o conjunto dimensional P0 em FreeCAD e STEP;
- mantido o estado honesto: nenhum hardware físico existe.

## 2026-07-26

- criada a pasta do Projeto 18;
- importada a proposta do portfólio;
- criada baseline documental completa;
- criado controle de andamento, roadmap, backlog, decisões e riscos;
- estado definido honestamente como `concepção documentada`.
