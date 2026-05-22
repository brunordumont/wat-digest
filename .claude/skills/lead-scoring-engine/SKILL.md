---
name: lead-scoring-engine
description: Score de 0-100 para leads de hotéis e pousadas baseado em fit com ICP da Axis (tipo propriedade, porte em UHs, decisor, dor, timing). Usar após qualificação inicial para priorizar fila de leads antes de agendar com Bruno.
metadata:
  version: 1.0.0
  domain: presales
  owner_agents: Catch
  requires_config:
    - brand.icp
    - brand.pricing
---

# Lead Scoring Engine · Axis Marketing

Score 0-100 que combina fit firmográfico + intenção de compra.
Tier A (>=70): agendar diagnóstico com Bruno imediatamente.
Tier B (40-69): nurturing ativo, agendar em 1-2 semanas.
Tier C (<40): nurturing longo ou desqualificar.

---

## Modelo de Score

### FIT Score (50 pontos)

| Dimensão | Pontos | Critérios |
|---|---|---|
| Tipo propriedade | 20 | Hotel/pousada/resort = 20pts; hostel = 10pts; outro = 0pts |
| Porte (UHs) | 20 | 20-100 UHs = 20pts; 10-19 = 15pts; <10 = 5pts; >100 = 10pts |
| Autoridade decisor | 10 | Dono/sócio = 10pts; gerente geral = 8pts; gerente marketing = 6pts; outro = 2pts |

### INTENT Score (50 pontos)

| Dimensão | Pontos | Critérios |
|---|---|---|
| Dor alinhada | 20 | Dor clara e alinhada = 20pts; dor vaga = 10pts; fora do escopo = 0pts |
| Canal de entrada | 15 | Indicação = 15pts; inbound orgânico = 12pts; tráfego pago = 10pts; cold = 5pts |
| Timing | 15 | Urgente (próxima temporada) = 15pts; próximos 3m = 10pts; 6m+ = 5pts; indefinido = 2pts |

---

## Exemplos

### Tier A (agendar imediatamente)
```
Pousada 25 UHs · dona · dor OTA-dependência · indicação · timing urgente
fit: 20+20+10 = 50 | intent: 20+15+15 = 50 | total: 100
```

### Tier B (nurturing ativo)
```
Hotel 12 UHs · gerente marketing · dor vaga · orgânico · timing 6 meses
fit: 20+15+6 = 41 | intent: 10+12+5 = 27 | total: 68
```

### Tier C (nurturing longo)
```
Hostel 8 UHs · funcionário sem poder · dor fora do escopo · cold · indefinido
fit: 10+5+2 = 17 | intent: 0+5+2 = 7 | total: 24
```

---

## Regras

- Calcular score mesmo com dados incompletos (NULL = 0pts, não erro)
- Incluir reasoning no output para Bruno revisar
- Não cachear score por mais de 24h
- Nunca assumir Tier A sem validar todos os critérios
- Não re-qualificar lead desqualificado há menos de 7 dias
