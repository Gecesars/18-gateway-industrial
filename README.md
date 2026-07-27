# EDGE-18 — Gateway Industrial Modbus/CAN Universal

Plataforma-pai para aquisição industrial e telemetria dos demais projetos do
portfólio. O EDGE-18 lê Modbus RTU, quatro sinais 0–10 V/4–20 mA e quatro
entradas digitais/pulso, conserva dados offline e publica por MQTT/TLS.

> **Estado: revisão digital A congelada para documentação — não fabricar.**
> O esquemático passa no ERC, mas a PCB foi mantida no ponto solicitado pelo
> responsável: 43 ocorrências de DRC e 24 conexões abertas. Os arquivos servem
> para revisão de engenharia e continuidade do desenvolvimento; não constituem
> uma liberação fabril, protótipo validado ou produto certificado.

## Arquitetura P0

| Bloco | Seleção |
|---|---|
| MCU | STM32H563ZIT6, Cortex-M33/TrustZone |
| Ethernet | LAN8742Ai, RMII 10/100 |
| Wi-Fi | ESP32-C3-MINI-1 opcional |
| RS-485 | 2 × ISOW1412 isoladas |
| Analógicas | ADS8684, quatro canais de 16 bits |
| Digitais | 2 × ISO1212, quatro entradas de 24 V |
| CAN | ISO1042 reservado para fase 2 |
| Alimentação | 9–36 Vcc; LM76002 como referência |
| PCB | 180 × 120 mm, quatro camadas |

O MVP é somente de monitoramento. Não possui saídas de comando e não substitui
CLP ou relé de segurança.

## Entregue nesta revisão

- requisitos verificáveis e seis ADRs;
- esquemático KiCad A0 com sete blocos e ERC limpo;
- PCB KiCad de quatro camadas, 180 × 120 mm, com roteamento parcial congelado;
- trilhas de 0,25 a 1,20 mm, sem segmento abaixo de 0,25 mm;
- BOM de 181 posições, pinout de 144 pinos e cálculos elétricos;
- STEP atual da PCB e conjunto paramétrico FreeCAD;
- relatório DRC integral com as pendências conhecidas;
- arquitetura elétrica e de software;
- contratos de configuração e telemetria em JSON Schema;
- exemplos válidos;
- núcleo C17 testável com configuração, Modbus, scheduler, journal, telemetria,
  máquina de estados e manifesto de atualização;
- testes estritos no host e CI;
- quinze vistas técnicas e PDF consolidado.

## Evidência CAD — 15 vistas

Os recortes do esquemático foram exportados em alta resolução e ampliados por
bloco para preservar referências, valores e nomes de redes. As vistas da PCB
mostram deliberadamente o estado congelado, inclusive o roteamento ainda
incompleto.

| | | |
|---|---|---|
| ![Esquemático completo](docs/images/01-esquematico-visao-geral.png) | ![Alimentação](docs/images/02-esquematico-alimentacao.png) | ![Controlador](docs/images/03-esquematico-controlador.png) |
| ![Armazenamento](docs/images/04-esquematico-armazenamento.png) | ![Rede](docs/images/05-esquematico-rede.png) | ![Entradas analógicas](docs/images/06-esquematico-analogico.png) |
| ![Entradas digitais](docs/images/07-esquematico-digital.png) | ![Barramentos isolados](docs/images/08-esquematico-barramentos.png) | ![Implantação superior](docs/images/09-pcb-layout-superior.png) |
| ![Cobre superior](docs/images/10-pcb-cobre-superior.png) | ![Plano interno de terra](docs/images/11-pcb-plano-terra.png) | ![Plano interno de alimentação](docs/images/12-pcb-plano-alimentacao.png) |
| ![Cobre inferior](docs/images/13-pcb-cobre-inferior.png) | ![PCB em 3D](docs/images/14-pcb-3d.png) | ![Conjunto mecânico](docs/images/15-conjunto-mecanico-3d.png) |

Documento consolidado: [EDGE-18 — projeto completo Rev. A](docs/EDGE-18-projeto-completo-rev-a.pdf).

## Verificação local

```bash
./tools/run-checks.sh
```

## Navegação

- [índice técnico](docs/README.md);
- [requisitos](docs/01-requisitos.md);
- [arquitetura](docs/02-arquitetura.md);
- [hardware](docs/03-hardware.md);
- [software](docs/04-software.md);
- [estado congelado da PCB Rev. A](docs/17-estado-da-pcb-rev-a.md);
- [relatório ERC](docs/reports/edge18-main-rev-a-erc.rpt);
- [relatório DRC](docs/reports/edge18-main-rev-a-drc.rpt);
- [fontes primárias](docs/12-fontes-primarias.md);
- [status](project-management/STATUS.md);
- [roadmap](project-management/ROADMAP.md).

## Licença

A licença ainda não foi definida. Não redistribua artefatos como se uma licença
já tivesse sido concedida.
