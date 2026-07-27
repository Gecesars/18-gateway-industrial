# Interfaces e modelo de dados

## Interfaces

| ID | Interface | Contrato a documentar |
|---|---|---|
| IF-18-01 | Modbus RTU/TCP | direção, níveis, conector/protocolo e falhas a definir |
| IF-18-02 | CAN futuro | direção, níveis, conector/protocolo e falhas a definir |
| IF-18-03 | 4–20 mA/0–10 V | direção, níveis, conector/protocolo e falhas a definir |
| IF-18-04 | pulso/contato | direção, níveis, conector/protocolo e falhas a definir |
| IF-18-05 | Ethernet/Wi-Fi | direção, níveis, conector/protocolo e falhas a definir |
| IF-18-06 | MQTT/REST | direção, níveis, conector/protocolo e falhas a definir |

Para cada interface elétrica serão registrados pinos, níveis absolutos,
referência de terra, isolação, proteção, direção, estado em reset e chicote. Para
cada protocolo serão registrados framing, versão, autenticação, timeout,
repetição, idempotência e compatibilidade.

## Entidades e grandezas

| ID | Dado | Metadados obrigatórios |
|---|---|---|
| D-18-01 | ponto/endereço/tipo/escala | unidade, faixa, qualidade e retenção a definir |
| D-18-02 | valor/qualidade/timestamp | unidade, faixa, qualidade e retenção a definir |
| D-18-03 | configuração/versionamento | unidade, faixa, qualidade e retenção a definir |
| D-18-04 | evento/regra | unidade, faixa, qualidade e retenção a definir |
| D-18-05 | diagnóstico | unidade, faixa, qualidade e retenção a definir |

## Regras de dados

- valor inválido não é zero;
- unidade e escala pertencem ao contrato;
- dado atrasado ou reconstruído deve ser identificável;
- identidade de dispositivo e calibração não podem ser inferidas pelo endereço;
- alterações de schema exigem migração e teste de compatibilidade;
- retenção e acesso devem respeitar a finalidade declarada.
