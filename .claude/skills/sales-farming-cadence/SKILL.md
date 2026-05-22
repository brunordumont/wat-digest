---
name: sales-farming-cadence
description: Cadência de nurturing multi-toque para leads de hotéis e pousadas que demonstraram interesse mas não têm timing agora. Sequência D+1, D+7, D+21, D+60 via WhatsApp e email. Usar quando Catch classifica lead como WARM ou COLD com potencial futuro.
metadata:
  version: 1.0.0
  domain: presales-farming
  owner_agents: Catch, nurturing
  requires_config:
    - stack.messaging_channel
    - stack.email_provider
    - brand.copy_packs
---

# Sales Farming Cadence · Axis Marketing

Cadência de nutrição para leads que não têm timing agora mas têm fit.
Objetivo: manter relacionamento até o momento certo aparecer.

---

## Quando usar

- Lead WARM: tem fit mas sem timing (timing > 3 meses)
- Lead COLD: tem fit mas sem urgência definida
- Lead pré-abertura: propriedade ainda em construção
- Lead pós no-show 3x: mover para nurturing longo

---

## Cadência (4 ciclos)

### Ciclo 1 — Reengajamento suave (D+1 a D+7)

**D+1 — WhatsApp:**
```
Oi {{nome}}! Foi bom conversar.

Se o momento mudar ou tiver dúvidas sobre marketing
pra {{nome_propriedade}}, me chama. 🏨
```

**D+7 — WhatsApp:**
```
Fala {{nome}}! Como tá a ocupação aí?

Vi uma tendência interessante no setor de hospedagem
que pode ser relevante pra vocês — posso te mandar?
```

**D+7 — Email (se tiver):**
```
Assunto: Uma coisa que vi sobre {{cidade/região}} que pode ajudar

Oi {{nome}},

[insight relevante para o nicho de hospedagem — ex: tendência de busca,
dado de reservas diretas vs OTA, mudança no Google Hotels, etc.]

Se fizer sentido conversar sobre como isso impacta a {{nome_propriedade}},
é só responder aqui.

Abraço,
Bruno — Axis Marketing
```

---

### Ciclo 2 — Valor e caso prático (D+21)

**D+21 — WhatsApp:**
```
{{nome}}, tudo bem?

Acabamos de finalizar um trabalho com uma pousada em
{{região_similar}} — resultado interessante em {{métrica}}.

Se quiser que eu te conte como foi, é só falar.
```

**D+21 — Email:**
```
Assunto: Como uma pousada em {{região}} aumentou reservas diretas em X%

Oi {{nome}},

[mini-case de resultado real — anônimo se necessário]

O desafio era parecido com o que você mencionou.

Se quiser entender como aplicar na {{nome_propriedade}},
posso fazer um diagnóstico rápido. Sem compromisso.

Abraço,
Bruno
```

---

### Ciclo 3 — Reativação direta (D+60)

**D+60 — WhatsApp:**
```
Oi {{nome}}! Faz um tempo.

Como tá a {{nome_propriedade}}? A situação de
{{dor_mencionada}} evoluiu ou ainda tá no radar?
```

**D+60 — Email:**
```
Assunto: Faz um tempo, {{nome}}

Oi {{nome}},

Aqui é o Bruno da Axis. A gente conversou há uns 2 meses
sobre {{dor_mencionada}} na {{nome_propriedade}}.

Não sei se o momento mudou, mas queria avisar que
temos algumas novidades desde então.

Se fizer sentido retomar, é só me dizer.
Se preferir que eu pare de incomodar, também tudo bem!

Abraço,
Bruno
```

---

### Ciclo Final — Breakup (D+120)

**WhatsApp:**
```
{{nome}}, última mensagem aqui.

Tentei algumas vezes ao longo desses meses e
entendo que pode não ser o momento certo.

Se um dia fizer sentido cuidar do marketing
da {{nome_propriedade}} com a Axis, me chama.

Sucesso aí! 🏨
```

**Email:**
```
Assunto: Última mensagem

{{nome}},

Essa é minha última mensagem.

Tentamos conversar algumas vezes e percebi que
pode não ser o momento pra vocês — o que é ok.

Vou parar de entrar em contato. Se mudar de ideia,
é só responder aqui que eu lembro imediatamente.

Sucesso com a {{nome_propriedade}}!

Abraço,
Bruno — Axis Marketing
```

---

## Regras

- Máximo 1 mensagem por canal por ciclo (não bombardear)
- Sempre personalizar com nome da propriedade e dor mencionada
- Após breakup: aguardar 14 dias antes de arquivar definitivamente
- Se lead responder em qualquer etapa: mover para "Em Conversa" imediatamente
- Não reutilizar o mesmo texto entre ciclos

---

## Variáveis

```
{{nome}}              — nome do lead
{{nome_propriedade}}  — nome da propriedade
{{dor_mencionada}}    — dor que o lead citou no primeiro contato
{{região_similar}}    — região de case similar
{{cidade}}            — cidade da propriedade
```
