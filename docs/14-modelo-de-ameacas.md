# Modelo de ameaças P0

## 1. Ativos

- identidade do dispositivo;
- chave privada e certificados;
- firmware e política mínima de versão;
- configuração e calibração;
- dados operacionais;
- disponibilidade da aquisição;
- acesso aos barramentos de campo.

## 2. Fronteiras

| Fronteira | Confiança inicial |
|---|---|
| Ethernet/Wi-Fi | não confiável |
| broker MQTT | autenticado, mas dados ainda validados |
| USB de serviço | físico privilegiado e auditado |
| cartão microSD | não confiável; dados precisam de integridade |
| RS-485/CAN | campo hostil e ruidoso |
| REST local | autenticado e limitado |
| boot/update | somente conteúdo assinado |

## 3. Ameaças e controles

| Ameaça | Controle P0 |
|---|---|
| firmware modificado | assinatura, versão mínima e rollback controlado |
| dispositivo clonado | identidade individual protegida |
| configuração malformada | schema, limite, staging e commit transacional |
| replay/duplicata MQTT | TLS, sequência e identificador idempotente |
| exaustão por rede | limites de conexão, tamanho, fila e timeout |
| cartão removido/corrompido | journal, CRC, estado degradado e recuperação |
| segredo em log | API de logging sem buffers de chave/token |
| Wi-Fi comprometido | coprocessador sem autoridade nem acesso direto ao campo |
| acesso SWD | política por estágio, registro e bloqueio de produção |
| Modbus hostil | comprimento, função, endereço e taxa limitados |

## 4. Modos de fabricação

- **desenvolvimento:** SWD aberto, chaves de teste, sem credencial de produção;
- **produção:** provisionamento individual, teste, política de debug aplicada;
- **RMA:** procedimento autenticado e destruição/rotação de credenciais;
- **descarte:** limpeza de identidade, configuração e dados.

## 5. Itens pendentes

- definir algoritmo/formato de assinatura;
- definir armazenamento de chave e configuração TrustZone;
- modelar processo de provisionamento offline;
- definir autoridade certificadora e rotação;
- executar análise estática, fuzzing e teste de penetração antes do piloto.
