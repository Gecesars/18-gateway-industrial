# Hardware EDGE-18 P0

## 1. Componentes arquiteturais

| Ref. funcional | Componente de referência | Função | Estado |
|---|---|---|---|
| MCU | STM32H563ZIT6, LQFP-144 | autoridade, Ethernet MAC, FDCAN, segurança | selecionado para P0 |
| PHY | LAN8742Ai | Ethernet 10/100 RMII | selecionado para P0 |
| Wi-Fi | ESP32-C3-MINI-1 | enlace opcional/coprocessador | selecionado, DNP permitido |
| ADC | ADS8684IDBT | 4 canais, 16 bits, faixas até ±10,24 V | selecionado para P0 |
| DI | 2 × ISO1212DBQ | quatro entradas industriais isoladas | selecionado para P0 |
| RS-485 | 2 × ISOW1412 | transceptor e potência isolada | selecionado para P0 |
| CAN | ISO1042 + DC/DC isolado | CAN/CAN-FD para fase 2 | reservado no P0 |
| Buck principal | LM76002 | 9–36 V para 5 V, margem até 60 V no CI | selecionado para cálculo |
| 3,3 V | conversor de 2 A ou mais | lógica, PHY e Wi-Fi | seleção antes do esquema final |
| Armazenamento | microSD industrial + flash OctoSPI | fila e atualização | interface selecionada |
| Serviço | USB-C USB 2.0 FS + SWD | console, recuperação e produção | selecionado |

Nenhum componente está qualificado apenas por aparecer nesta tabela. Footprint,
estoque, lifecycle, térmica, EMC e substitutos precisam ser verificados antes
do gate de fabricação.

## 2. Placa e mecânica

- dimensões-alvo: 180 × 120 mm;
- quatro camadas: sinal/componente, plano GND, alimentação/sinal, sinal;
- FR-4 de 1,6 mm; cobre inicial de 1 oz;
- conectores de campo plugáveis, passo mínimo 5,08 mm;
- terminais de campo em uma borda, Ethernet/USB na borda oposta;
- barreiras de isolação sem cobre em todas as camadas;
- furos de montagem metálicos ligados ao chassi conforme análise EMC;
- gabinete-alvo: alumínio 210 × 150 × 65 mm, suporte para trilho DIN;
- antena do ESP32 na borda, com keep-out em cobre e afastamento do gabinete, ou
  variante MINI-1U com antena externa.

O conjunto dimensional P0 está em
`mechanical/native/edge18-p0-assembly.FCStd`, com exportações STEP da base,
tampa e conjunto. Ele verifica dimensões, seis fixações M3, aberturas-envelope
e separação inicial dos blocos. Conectores, tolerâncias, vedação e desenho de
fabricação ainda dependem do KiCad G1/G2.

## 3. Alimentação

### 3.1 Entrada

1. borne 9–36 Vcc;
2. fusível substituível ou PTC dimensionado;
3. proteção contra inversão por MOSFET/ideal diode;
4. TVS e filtro de modo comum/diferencial definidos por ensaio;
5. LM76002 para 5 V;
6. conversor 3,3 V;
7. supervisão de `VIN`, `5V`, `3V3` e sinal `POWER_GOOD`.

O limite de 60 V do LM76002 não autoriza aplicar 60 V à placa: TVS, MOSFET,
capacitores e demais componentes possuem limites próprios.

### 3.2 Orçamento preliminar

| Bloco | 5 V equivalente, pior caso de projeto |
|---|---:|
| STM32H563 + memórias | 0,30 A |
| Ethernet PHY/magnetics | 0,15 A |
| ESP32-C3 em transmissão | 0,50 A |
| ADC e front-end | 0,10 A |
| isoladores e DC/DC | 0,45 A |
| microSD em pico | 0,25 A |
| USB, LEDs e margem | 0,25 A |
| **Total de projeto** | **2,00 A** |

O buck será dimensionado para pelo menos 2,5 A. Correntes reais serão medidas no
P0 e a tabela será substituída por resultados.

## 4. Entradas analógicas

- o ADS8684 oferece faixas programáveis por canal;
- 0–10 V entra diretamente pelo caminho protegido;
- 4–20 mA usa shunt de 249 Ω, 0,1%, baixa deriva, selecionado fisicamente;
- 20 mA produz 4,98 V no shunt;
- cada canal terá proteção, filtro RC e ponto de teste;
- os canais compartilham `AGND_FIELD`;
- a calibração usa pelo menos zero, 25%, 50%, 75% e fundo de escala;
- o firmware armazena ganho, offset, temperatura e instrumento usado.

O shunt não será comutado por chave analógica no P0 para evitar resistência,
leakage e estados ambíguos. Jumper/codificação física deve ser visível ao
firmware por entrada de identificação ou configuração bloqueada.

## 5. Entradas digitais

Dois ISO1212 implementam quatro entradas de 24 V. O circuito de resistores será
calculado para a classe IEC 61131-2 pretendida a partir do datasheet e validado
no EVM/referência. Cada canal terá:

- borne `DIx` e retorno de campo;
- proteção contra inversão e surto;
- LED de campo sem comprometer o limiar;
- saída lógica para GPIO e timer do MCU;
- modo estado/debounce ou pulso rápido;
- ponto de teste somente no lado seguro.

## 6. RS-485

Cada porta possui barreira e alimentação isolada independentes. Em cada uma:

- A/B/GND de campo em borne próprio;
- TVS específica para barramento;
- choke opcional e footprint de ajuste EMC;
- terminação de 120 Ω selecionável;
- polarização selecionável, nunca duplicada por padrão;
- LEDs no lado lógico;
- controle de direção por hardware/periférico quando possível;
- clearances e keep-outs conforme isolamento escolhido.

## 7. Ethernet e Wi-Fi

O LAN8742Ai liga-se ao STM32 por RMII. O projeto inclui cristal/clock conforme
topologia escolhida, resistores de strap, magnetics, RJ45 blindado, ESD e ligação
controlada ao chassi.

O ESP32-C3:

- é opcional;
- recebe 3,3 V com chaveamento/reset independente;
- comunica por UART de controle e, se necessário, SPI;
- não acessa diretamente RS-485, ADC, CAN ou chaves privadas;
- pode ser removido e substituído pela variante com antena externa.

## 8. CAN reservado

O ISO1042 suporta CAN clássico e CAN-FD. O P0 terá transceptor, terminação
selecionável e conector, mas o firmware do MVP mantém o periférico desabilitado.
Transmissão futura exigirá requisito, ADR e testes próprios.

## 9. Regras de layout

- pares RMII curtos, impedância e retorno contínuo;
- nenhum sinal cru de campo atravessa a região do MCU;
- SPI do ADC afastado do buck e do módulo Wi-Fi;
- plano analógico controlado e união única documentada;
- keep-out completo sob barreiras;
- capacitores de desacoplamento no mesmo lado e junto ao pino;
- test points para todas as fontes, reset, clocks e barramentos internos;
- serigrafia identifica claramente domínio, tensão e posição de terminação;
- DRC não substitui revisão de creepage, clearance e caminho de retorno.

## 10. Estado

Arquitetura, componentes principais e modelo dimensional P0 foram criados.
Esquemático, cálculos de fonte/proteção, footprints, PCB e mecânica de produção
permanecem pendentes; nenhum arquivo P0 está liberado para fabricação.
