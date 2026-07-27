# Verificação e validação

## 1. Estado da evidência

`passou` significa que relatório e dados estão no repositório ou artefato
identificado. Código que compila não valida hardware. Simulação não substitui
ensaio.

## 2. Matriz P0

| ID | Teste | Critério | Estado |
|---|---|---|---|
| VT-CORE-01 | build C17 com warnings como erro | compila no host | passou |
| VT-CORE-02 | fila FIFO e wrap-around | ordem preservada | passou |
| VT-CORE-03 | overflow `reject-new` | item novo rejeitado sem perder antigo | passou |
| VT-CORE-04 | overflow `drop-oldest` | contador e itens corretos | passou |
| VT-CORE-05 | máscara de qualidade | bits independentes | passou |
| VT-CORE-06 | CRC Modbus | vetor conhecido `0xCDC5` | passou |
| VT-CFG-01 | schemas JSON | Draft 2020-12 válido | passou no host |
| VT-CFG-02 | exemplos | válidos e invariantes coerentes | passou no host |
| VT-EDA-01 | ERC KiCad Rev. A | 0 erros e 0 avisos | passou |
| VT-EDA-02 | DRC KiCad Rev. A | 0 violações e 0 conexões abertas | falhou: 43/24 |
| VT-EDA-03 | largura mínima presente | nenhum segmento abaixo de 0,25 mm | passou |
| VT-MEC-01 | modelo dimensional FreeCAD | gabinete 210 × 150 × 65 mm, PCB 180 × 120 mm e objetos esperados | passou |
| VT-PWR-01 | entrada 9–36 V | rails dentro da tolerância | pendente de hardware |
| VT-PWR-02 | inversão e brownout | sem dano/configuração parcial | pendente |
| VT-RS-01 | duas RS-485 | simultâneas, isoladas, matriz de baud/paridade | pendente |
| VT-MB-01 | funções Modbus de leitura | simulador e exceções | pendente |
| VT-AI-01 | 0–10 V | erro ≤ meta por canal | pendente |
| VT-AI-02 | 4–20 mA | erro e diagnósticos por canal | pendente |
| VT-DI-01 | limiares 24 V | quatro canais | pendente |
| VT-DI-02 | pulso | 10 kHz/50 µs | pendente |
| VT-ETH-01 | Ethernet | DHCP, estático, perda/retorno | pendente |
| VT-TLS-01 | autenticação | válido, expirado, revogado e relógio inválido | pendente |
| VT-MQ-01 | QoS 1/reconexão | duplicatas idempotentes | pendente |
| VT-BUF-01 | capacidade | 1.000.000 registros | pendente |
| VT-BUF-02 | corte de energia | 100 cortes sem corrupção além do registro parcial | pendente |
| VT-UPD-01 | imagem alterada | rejeitada | pendente |
| VT-UPD-02 | falha de boot | rollback preserva dados/configuração | pendente |
| VT-REL-01 | operação contínua | 30 dias sem travamento | pendente |
| VT-SEC-01 | portas e segredos | superfície conforme modelo; nenhum segredo em log | pendente |

## 3. Bancadas

### 3.1 Digital/firmware

- computador Linux;
- simulador Modbus;
- broker MQTT com CA de laboratório;
- injeção de perda, atraso, duplicação e corrupção;
- arquivos/cartões com falhas simuladas.

### 3.2 Elétrica

- fonte isolada programável com limite;
- multímetro calibrado;
- osciloscópio;
- gerador de função/pulsos;
- fonte 0–10 V e calibrador 4–20 mA;
- adaptadores RS-485/CAN isolados;
- câmera térmica ou termopares;
- carga eletrônica.

### 3.3 Pré-compliance

- ESD/EFT/surge somente depois da revisão de segurança;
- LISN/célula TEM quando disponível;
- captura de emissões do buck, Ethernet e Wi-Fi;
- ensaios repetidos nas configurações de terminação.

## 4. Evidência

Cada relatório contém:

- requisito/teste;
- commit e revisão de hardware;
- número de série;
- instrumentos e validade de calibração;
- diagrama de ligação;
- entradas, configuração e ambiente;
- dados brutos;
- resultado, anomalias e responsável;
- impacto sobre riscos e próximos gates.

O resultado de `VT-EDA-02` está preservado integralmente em
[`reports/edge18-main-rev-a-drc.rpt`](reports/edge18-main-rev-a-drc.rpt). A
falha é deliberadamente visível e bloqueia a fabricação.
