# Cálculos elétricos — EDGE-18 Rev. A

## 1. Premissas

| Parâmetro | Valor de projeto |
|---|---:|
| entrada nominal | 9–36 Vcc |
| saída principal | 5,0 V / 2,0 A contínuos |
| limite do LM76002 | 2,5 A |
| frequência usada no cálculo | 500 kHz |
| saída lógica | 3,3 V / até 3 A no TPS62132 |
| temperatura de cálculo | −20 a +70 °C ambiente |
| PCB | quatro camadas, 1 oz, 1,6 mm |

Valores de bancada substituem as premissas após o protótipo.

## 2. Buck de 5 V

O divisor `R1 = 40,2 kΩ` e `R2 = 10,0 kΩ`, com referência nominal de 1,0 V,
produz:

```text
VOUT = 1,0 × (1 + 40,2 / 10,0) = 5,02 V
```

Para `L2 = 10 µH`, 500 kHz e pior caso de ripple em 36 V:

```text
ΔIL = VOUT × (VIN − VOUT) / (VIN × L × f)
ΔIL = 5 × 31 / (36 × 10 µH × 500 kHz) = 0,861 A
```

Em 9 V, `ΔIL = 0,444 A`. Com 2,0 A de carga, o pico calculado em 36 V é
2,431 A, abaixo do limite nominal de 2,5 A, porém com margem pequena. A
indutância XAL1010-103 suporta a corrente, mas a temperatura do CI e do diodo
de entrada deve ser medida.

Com 20 µF nominais de saída (`C4 + C5`), antes de derating:

```text
ΔVcapacitivo ≈ ΔIL / (8 × f × C) = 10,8 mV
```

O ripple real soma ESR, perda de capacitância DC e layout.

## 3. Entrada e proteção

- `F1`: PTC 2 A;
- `D1`: SMBJ36A;
- `D2`: SS56 em série para inversão;
- `L1`: 10 µH;
- `C1`: 100 µF/63 V e `C2`: 1 µF/100 V.

O clamp máximo publicado da SMBJ36A fica próximo do limite absoluto de 60 V do
LM76002. Portanto a Rev. A exige ensaio de surto com a impedância real da fonte;
ela não recebe qualificação de transiente apenas por cálculo. Em 2 A, a perda
do SS56 pode se aproximar de 1 W e deve ser verificada termicamente.

## 4. Buck de 3,3 V

O TPS62132 é variante fixa de 3,3 V. `L3 = 2,2 µH`, `C7 + C8 = 44 µF`
nominais e desacoplamentos locais atendem a topologia de referência. O rail é
separado por ferrites para `3V3_A` e `3V3_ETH`. A corrente de 3 A é capacidade
do conversor, não orçamento autorizado a cada carga.

## 5. Entradas analógicas

Cada canal tem `1 kΩ + 10 nF`, logo:

```text
fc = 1 / (2πRC) = 15,9 kHz
```

Em modo 4–20 mA, o jumper fecha o shunt de `249 Ω`, 0,1%, 25 ppm/°C:

| Corrente | Tensão no ADC | Potência no shunt |
|---:|---:|---:|
| 4 mA | 0,996 V | 3,98 mW |
| 20 mA | 4,980 V | 99,6 mW |
| 24 mA diagnóstico | 5,976 V | 143,4 mW |

O resistor 0805 deve ter potência nominal compatível com a temperatura. O
SMAJ12A limita eventos de campo, mas capacitância e energia de surto precisam
ser medidas no protótipo.

## 6. Entradas digitais

Os dois ISO1212 seguem a configuração Type 3:

- `RSENSE = 562 Ω`, corrente nominal de entrada de aproximadamente 2,25 mA;
- `RTHR = 1,00 kΩ`, alvo de limiar em 11 V;
- `CIN = 10 nF` por canal;
- SMAJ33A no lado de campo.

A potência de campo é dominada pelo caminho interno do receptor; a validação
deve medir limiares crescente/decrescente em 9, 18, 24, 30 e 36 V, temperatura
e fuga do TVS.

## 7. Barramentos isolados

Cada RS-485 usa ISOW1412 com alimentação isolada integrada, TVS
SM712 e terminação de 120 Ω selecionável. O CAN usa ISOW1044, PESD2CAN e
terminação de 120 Ω selecionável. Os três transceptores possuem retorno de
campo independente e rasgo mecânico sob a barreira.

Uma terminação de 120 Ω em 5 V diferenciais dissipa até aproximadamente
208 mW; os resistores são 1206. As terminações permanecem abertas por padrão.

## 8. Classes de roteamento

| Classe | Trilhas | Clearance | Via / furo |
|---|---:|---:|---:|
| padrão | 0,30 mm | 0,18 mm | 0,80 / 0,40 mm |
| alimentação | 0,80 mm | 0,18 mm | 1,20 / 0,60 mm |
| VIN | 1,20 mm | 0,18 mm | 1,60 / 0,80 mm |
| analógico | 0,35 mm | 0,18 mm | 0,90 / 0,45 mm |
| campo | 0,50 mm | 0,18 mm | 1,00 / 0,50 mm |
| alta velocidade | 0,25 mm | 0,18 mm | 0,70 / 0,35 mm |

O mínimo global de trilha é 0,25 mm. O clearance reduzido junto a encapsulamentos
de passo fino não substitui os afastamentos de isolamento, que são obtidos pela
separação física dos domínios e rasgos.
