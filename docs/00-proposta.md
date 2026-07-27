### Projeto 18 — Gateway Industrial Modbus/CAN Universal

**Descrição:** "Caixa" que traduz sensores e equipamentos legados (Modbus RTU/TCP, CAN, 4–20 mA, pulso) para dashboard web/MQTT sem exigir programação — SCADA acessível para pequenas indústrias.

**Funcionamento detalhado:** o usuário escolhe uma interface, endereço e
registrador, aplica tipo, escala, unidade e política de publicação e testa a
leitura antes de ativá-la. O runtime agenda aquisições sem bloquear os demais
barramentos, marca qualidade e timestamp, armazena durante indisponibilidade e
executa regras locais a partir de uma configuração versionada.

**MVP verificável:** Modbus RTU mestre, quatro entradas analógicas, quatro
digitais, Ethernet e MQTT, com configuração e diagnóstico web. CAN, Modbus TCP,
OPC-UA e editor visual de regras serão adicionados como módulos independentes.

**Critérios de aceite principais:**
- configuração inválida não pode derrubar aquisições já ativas;
- isolamento, polarização e terminação do RS-485 documentados e ensaiados;
- qualidade diferencia timeout, exceção Modbus, valor fora de faixa e dado
  desatualizado;
- fila offline possui limite e política de descarte explícitos;
- atualização assinada permite rollback sem perder a configuração.

**Dependências e riscos:** pretensão de universalidade, conflitos elétricos de
terra, equipamentos com mapas incorretos, exposição de protocolos industriais à
internet e necessidade de suporte a perfis.

**Especificação técnica:**
- Interfaces: 2× RS-485, 1× CAN, 4× analógicas, 4× digitais/pulso, Ethernet + Wi-Fi
- Configuração 100% via web local: mapear registrador → nome da variável → dashboard, sem código
- Northbound: MQTT, HTTP REST, OPC-UA (fase 2)
- Regras locais (if/then) executando mesmo sem internet; buffer de dados em queda de link

**Etapas de desenvolvimento:**
1. Definir modelo de configuração declarativa (JSON) e editor web amigável
2. Firmware com drivers Modbus mestre, CAN e analógicas sobre RTOS
3. Biblioteca de perfis prontos de equipamentos comuns (inversores, medidores, CLPs)
4. Motor de regras local com editor visual simples
5. Ensaios de EMC industrial e temperatura; caixa DIN
6. Programa de integradores (revenda com margem)

**Documentação a produzir:** manual de configuração com receitas passo a passo, biblioteca de perfis documentada, guia de integração MQTT/REST, catálogo para integradores.

**Mercado:** integradores e pequenas indústrias que não pagam SCADA tradicional; o Projeto 11/12 usa a mesma base.

---
