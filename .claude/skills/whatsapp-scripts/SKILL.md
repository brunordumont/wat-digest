---
name: whatsapp-scripts
description: Scripts prontos para cada etapa do processo de qualificação inbound via WhatsApp da Axis. Usar quando Catch precisa de template para opener, pitch, agendamento, follow-up ou desqualificação com leads de hotéis e pousadas.
metadata:
  version: 1.0.0
  domain: presales
  owner_agents: Catch
---

# WhatsApp Scripts · Axis Marketing

Scripts otimizados para cada etapa do funil de qualificação inbound.
Tom: humano, acolhedor, profissional. Nunca parecer robô ou telemarketing.

---

## ETAPA 1, Opener (primeiro contato)

**Base:**
```
Oi {{nome}}, tudo bem?

Vi que você entrou em contato com a Axis. Sou o Catch, cuido do comercial aqui.

Pode me contar um pouco mais sobre a propriedade de vocês?
```

**Variação A (veio de formulário):**
```
Oi {{nome}}! Vi que você preencheu nosso formulário.

Sou o Catch da Axis. Pode me contar mais sobre a propriedade?
Quantas UHs têm?
```

**Variação B (indicação):**
```
Oi {{nome}}, tudo bem?

O {{nome_indicador}} me falou de vocês. Sou o Catch, cuido do comercial na Axis.

Pode me contar sobre a propriedade?
```

---

## ETAPA 2, Qualificação (perguntas ICP)

```
Que bacana! E você que cuida do marketing, toma as decisões nessa área?
```

```
Qual é o maior desafio de marketing que vocês enfrentam hoje?
```

```
Vocês já investem em marketing atualmente ou estão começando agora?
```

---

## ETAPA 3, Pitch (após entender a dor)

**Para dor de OTA-dependência:**
```
Entendo bem. Esse é exatamente o problema que a Axis resolve.

A gente ajuda hotéis e pousadas a reduzir a dependência de OTA
e aumentar reservas diretas, que têm margem muito maior pra vocês.

Nosso ponto de entrada é R$3k/mês. Isso cabe no contexto de vocês?
```

**Para dor de visibilidade/Google:**
```
Faz todo sentido. Quem não aparece no Google hoje perde reserva
pra concorrência todo dia.

A Axis cuida justamente disso, estratégia digital completa
pra propriedades como a de vocês.

Nosso ponto de entrada é R$3k/mês. Isso cabe no contexto?
```

**Para dor de baixa ocupação:**
```
Entendo. Baixa temporada é o maior desafio do setor.

A Axis trabalha estratégia de marketing pra manter ocupação
mais equilibrada ao longo do ano, não só na alta.

Nosso ponto de entrada é R$3k/mês. Isso cabe pra vocês?
```

---

## ETAPA 4, Agendamento

**Proposta de slots:**
```
Ótimo! O próximo passo seria um diagnóstico de 45min com o Bruno,
fundador da Axis. Ele olha a situação atual de vocês e identifica
as maiores oportunidades. É sem compromisso.

Tenho 3 horários disponíveis:
1️⃣ {{dia1}} às {{hora1}}
2️⃣ {{dia2}} às {{hora2}}
3️⃣ {{dia3}} às {{hora3}}

Qual funciona melhor?
```

**Coleta de e-mail (após lead escolher o horário):**
```
Show! Para te mandar o link da reunião por e-mail também,
qual é o melhor e-mail de vocês?
```

**Confirmação (após criar o evento):**
```
Agendado!

📅 {{dia_semana}}, {{data}} às {{hora}}
⏱️ 45 minutos
🔗 {{link_meet}}

O convite já foi pro seu e-mail. Qualquer dúvida antes, me chama aqui!
```

---

## ETAPA 5, Confirmação de Sócios/Decisores

```
Só um detalhe: tem sócio ou outra pessoa envolvida nas decisões
de marketing? Se sim, é importante que esteja na reunião também.
```

```
Perfeito! Então no {{dia}} às {{hora}} vou precisar de você
{{e de {{nome_socio}} se houver}} na call. Conseguem?
```

---

## FOLLOW-UP por nível

### Nível 1, Quebrou gelo mas parou

**+24h:**
```
👀
```

**+48h:**
```
Oi {{nome}}?
```

**+72h:**
```
Semana corrida aí, {{nome}}? Me avisa quando puder! 😅
```

**+7 dias:**
```
Fala {{nome}}! Como tá a ocupação aí?
Ainda com desafio de reserva direta?
```

---

### Nível 2, Demonstrou interesse mas não agendou

**+24h:**
```
E aí {{nome}}, conseguiu pensar no que conversamos?

Ainda tenho horários essa semana:
{{dia1}} {{hora1}} ou {{dia2}} {{hora2}}
```

**+48h:**
```
Fala {{nome}}, correria aí? 😅

Quando tiver um tempinho a gente segue!
```

**+7 dias:**
```
Boa semana {{nome}}! 🏨

O desafio de {{dor_mencionada}} continua? Vamos marcar aquele papo?
```

---

### Nível 3, No-show (confirmou mas não apareceu)

**Imediato (10min após):**
```
{{nome}}, tá tudo bem? O Bruno está te esperando na call 🤔
```

**+2h:**
```
{{nome}}, vi que não conseguiu entrar. Aconteceu algum imprevisto?
```

**+24h:**
```
Fala {{nome}}! Conseguimos reagendar?

Tenho: {{dia1}} às {{hora1}} ou {{dia2}} às {{hora2}}
```

**+48h (última):**
```
{{nome}}, última tentativa aqui.

{{dia}} às {{hora}} ou {{dia2}} às {{hora2}}?

Se não rolar agora, deixamos pra outra hora sem problema.
```

---

## DESQUALIFICAÇÃO (respeitosa)

**Propriedade em construção:**
```
Entendi! A Axis trabalha com propriedades já em operação —
nossa estratégia depende de dados reais de reservas.

Com {{prazo}} pra abertura ainda não faria sentido agora.

Quando estiver chegando perto (uns 2-3 meses antes),
me chama que montamos uma estratégia de lançamento. Combinado?
```

**Budget muito abaixo:**
```
Entendo, {{nome}}. Nosso mínimo hoje é R$3k/mês,
que é o necessário pra ter resultado real no marketing.

Se o contexto mudar lá na frente, me chama de volta!
Sucesso aí 🏨
```

**Fora do nicho:**
```
Entendi! A Axis é especializada em hotéis e pousadas especificamente.

Para {{tipo_negocio}}, infelizmente não sou o mais indicado.

Posso te indicar alguém se quiser?
```

---

## Variáveis disponíveis

```
{{nome}}         , nome do lead
{{nome_socio}}   , nome do sócio (se houver)
{{nome_indicador}}, quem indicou
{{dia1..3}}      , opções de horário
{{hora1..3}}     , horários
{{dia}}, {{hora}}, horário confirmado
{{dor_mencionada}}, dor que o lead citou
{{tipo_negocio}} , tipo de negócio se fora do nicho
{{prazo}}        , prazo até abertura (se pré-abertura)
```
