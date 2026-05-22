---
name: appointment-setter
description: Agenda diagnósticos de 45min com Bruno (fundador da Axis) para leads qualificados de hotéis e pousadas. Confirma presença de todos os decisores, envia confirmação por WhatsApp e lembretes automáticos. Usar quando Catch aprova lead para diagnóstico.
metadata:
  version: 1.0.0
  domain: presales
  owner_agents: Catch
  requires_config:
    - stack.calendar_provider
    - stack.communication_channel
    - brand.company_name
---

# Appointment Setter · Axis Marketing

Skill de agendamento para diagnósticos de 45min com Bruno.
Meta: taxa de comparecimento >70%.

---

## Quando usar

- Lead qualificado (Tier A ou B) pelo Catch
- Após validar ICP + BANT
- Confirmar que TODOS os decisores estarão presentes

---

## Workflow completo

### 1. Verificar disponibilidade de Bruno

Buscar 3 slots nos próximos 5 dias úteis:
- Priorizar Terça/Quarta/Quinta
- Priorizar horários 9h-17h (evitar >18h — maior no-show)
- Buffer mínimo de 20min entre reuniões

### 2. Confirmar decisores

```
"Só um detalhe antes de confirmar: tem sócio ou outra pessoa
envolvida nas decisões de marketing? Se sim, preciso que esteja
na reunião também."

Se tem sócio:
"Ótimo. No {{dia}} às {{hora}} conseguem estar juntos você e {{nome_socio}}?"

Se não tem:
"Perfeito, então tá confirmado para {{dia}} às {{hora}}."
```

### 3. Coletar e-mail do lead

Antes de criar o evento, confirmar o e-mail:

```
Ótimo! Para te mandar o link da reunião por e-mail também,
qual é o melhor e-mail de vocês?
```

### 4. Criar agendamento

Campos obrigatórios:
- Título: "Reunião de Diagnóstico {{nome_lead}} & Bruno - {{nome_propriedade}}"
- Duração: 45 minutos
- Participantes: Bruno (brunordumont@gmail.com) + lead (e-mail coletado) + sócios se houver
- Plataforma: Google Meet (link gerado automaticamente via conferenceData)

Executar tool:
```
python tools/create_calendar_event.py \
  --datetime "{{datetime_iso_sem_timezone}}" \
  --lead-name "{{nome_lead}}" \
  --property-name "{{nome_propriedade}}" \
  --lead-email "{{email_lead}}"
```

O tool retorna `meet_link` — usar na confirmação abaixo.

### 5. Enviar confirmação por WhatsApp

```
Show! Diagnóstico confirmado:

📅 {{dia_semana}}, {{data}} às {{hora}}
⏱️ 45 minutos
📍 Google Meet (link abaixo)
🔗 {{link_meet}}

O Bruno vai olhar a situação atual de vocês e identificar
as maiores oportunidades. Sem compromisso.

Qualquer dúvida antes, me chama aqui!
```

### 6. Lembrete 24h antes

```
Fala {{nome}}! Tudo bem? 👋

Só passando pra confirmar: amanhã às {{hora}} temos
o diagnóstico da Axis com o Bruno.

Você {{e {{nome_socio}}}} ainda confirmados?
```

### 7. Lembrete 30min antes

```
{{nome}}, diagnóstico em 30 minutos! ⏰

Link: {{link_meet}}

Até já!
```

---

## Estratégias anti no-show

1. **Confirmar todos os decisores** antes de criar o evento (sobe 35% o comparecimento)
2. **Nome da propriedade no título** do evento (personalização)
3. **Link Meet na confirmação** (não só no lembrete — reduz fricção)
4. **Lembrete 24h + 30min** (dois pontos de contato)
5. **Evitar sexta à tarde e finais de semana** (maior no-show)

---

## Reagendamento (no-show)

Máximo 3 tentativas:

**Tentativa 1 — imediata (+10min):**
```
{{nome}}, tá tudo bem? O Bruno está te esperando na call 🤔
```

**Tentativa 2 — +2h:**
```
{{nome}}, vi que não conseguiu. Aconteceu algum imprevisto?
Conseguimos reagendar?
```

**Tentativa 3 — +24h:**
```
Fala {{nome}}! Última tentativa — tenho {{dia1}} às {{hora1}}
ou {{dia2}} às {{hora2}}. Algum serve?
```

Após 3 tentativas sem resposta: mover para nurturing (sales-farming-cadence).

---

## Métricas alvo

| Métrica | Meta |
|---|---|
| Taxa comparecimento | >70% |
| Taxa no-show | <30% |
| Taxa reagendamento (no-shows) | >35% |
| Todos decisores confirmados | >85% dos agendamentos |

---

## Regras inegociáveis

- Nunca agendar sem confirmar que o decisor principal estará presente
- Nunca agendar na sexta após 16h (no-show alto)
- Buffer mínimo de 20min entre reuniões de Bruno
- Máximo 3 tentativas de reagendamento por no-show
