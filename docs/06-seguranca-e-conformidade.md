# Segurança, conformidade e limites

## 1. Classificação atual

O EDGE-18 P0 é protótipo de bancada e monitoramento. Não é CLP de segurança, não
é fonte isoladora, não possui classificação SIL/PL, não está certificado e não
deve comandar processo.

## 2. Perigos

| Perigo | Controle de projeto | Gate |
|---|---|---|
| inversão/sobretensão de alimentação | fusível, proteção reversa, TVS e buck com margem | esquema + bancada limitada |
| diferença de potencial em RS-485/CAN | isoladores e potência isolada | layout + ensaio |
| surto/ESD nos terminais | proteção por interface e caminho ao chassi | pré-compliance |
| ligação errada 4–20 mA/0–10 V | seleção física, serigrafia e configuração coerente | inspeção + teste |
| curto em borne | limitação/proteção por canal | injeção de falha |
| aquecimento de DC/DC/TVS/shunt | cálculo, termografia e derating | térmica |
| perda de dados | fila limitada, journal e diagnóstico | cortes repetidos |
| configuração maliciosa | autenticação, schema, limites e transação | segurança |
| firmware adulterado | assinatura, boot seguro e rollback | atualização |
| acesso indevido ao campo | nenhum comando no MVP; rede segmentada | revisão de portas |

## 3. Regras obrigatórias de bancada

1. inspeção visual e continuidade sem energia;
2. energizar por fonte isolada com limite de corrente;
3. testar cada rail antes de montar MCU/módulos caros quando possível;
4. usar simuladores e cargas de baixa energia;
5. conectar um único domínio de campo por vez no bring-up;
6. registrar instrumento, serial, revisão e configuração;
7. interromper diante de aquecimento, odor, oscilação, reset ou valor incoerente.

## 4. Rede

- Ethernet de operação fica em segmento controlado;
- configuração local não é exposta à internet;
- Wi-Fi nasce desabilitado;
- MQTT inicia apenas após validação de certificado e relógio;
- chaves privadas não saem pela API nem entram em backup comum;
- serviços e portas abertas são inventariados em cada release.

## 5. Normas a avaliar

As edições aplicáveis serão congeladas antes da comercialização. A lista de
trabalho inclui segurança de equipamentos de controle/medição, EMC industrial,
interfaces digitais IEC 61131-2, Ethernet/rádio, materiais e descarte. Esta lista
não afirma conformidade nem substitui laboratório acreditado.

## 6. Creepage e clearance

Os valores não serão copiados de uma regra genérica. Devem considerar tensão de
trabalho, transientes, categoria de sobretensão, pollution degree, material,
altitude, tipo de isolamento e encapsulamento. O PCB terá keep-outs explícitos e
uma revisão manual além do DRC.

## 7. Limites de uso

- 0–50 °C interno e sem condensação no P0;
- somente SELV/PELV e sinais dentro do envelope documentado;
- analógicas compartilham referência;
- nenhuma ligação direta à rede elétrica;
- nenhum ambiente explosivo;
- nenhum comando de atuador;
- nenhum piloto sem relatório dos gates G1–G5.
