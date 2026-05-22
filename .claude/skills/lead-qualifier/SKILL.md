---
name: lead-qualifier
description: Qualifica leads inbound de hotéis e pousadas baseado em tipo de propriedade, porte (UHs), dor de marketing e budget. Determina se lead tem fit com a Axis. Usar quando novo lead chega e precisa de score de qualificação.
metadata:
  version: 1.0.0
  domain: presales
  owner_agents: Catch
  requires_config:
    - brand.icp
    - brand.pricing
---

# Lead Qualifier — Qualificação de Leads · Axis Marketing

Analisa leads que chegam via WhatsApp, formulário ou indicação e determina se têm fit com os serviços da Axis (assessoria de marketing para hotéis e pousadas).

## Critérios de Qualificação

### Lead QUALIFICADO se:
- Tipo: hotel, pousada ou resort em operação
- Decisor acessível (dono, gerente geral, gerente de marketing)
- Dor alinhada com o que a Axis resolve
- Budget: R$3k/mês disponível (ou abertura para discutir)

### Dores ALINHADAS (fit claro):
- Alta dependência de OTAs (Booking, Airbnb) comendo margem
- Poucos reservas diretas pelo site próprio
- Baixa ocupação em baixa temporada
- Não aparece no Google quando buscam hospedagem na região
- Instagram/redes sociais sem resultado mensurável
- Não sabe o que está funcionando no marketing
- Quer reduzir CAC de reserva

### Dores FORA DO ESCOPO (sem fit):
- "Quero gerir minha conta no Booking" — gerenciamento de OTA não é nosso foco
- "Preciso de sistema de reservas / PMS" — tecnologia hoteleira não fazemos
- "Quero construir meu site" — não fazemos desenvolvimento web avulso
- "Preciso de revenue management" — fora do escopo

### Lead DESQUALIFICADO se:
- Propriedade ainda em construção (pré-abertura > 3 meses)
- Não é hospedagem (restaurante, bar, etc.)
- Decisor inacessível e sem perspectiva de acesso
- Budget muito abaixo de R$3k sem perspectiva de crescimento
- Já teve má experiência com Axis (avaliar caso a caso)

## Input Esperado

```json
{
  "nome": "Maria Silva",
  "propriedade": "Pousada das Flores",
  "tipo": "pousada",
  "uhs": 18,
  "localizacao": "Litoral Paulista",
  "decisor": "dona",
  "dor": "Alta dependência de OTA, quase zero reserva direta",
  "budget_ok": true,
  "timing": "próxima temporada"
}
```

## Output

### Se QUALIFICADO:
```json
{
  "status": "qualificado",
  "fit_score": 85,
  "prioridade": "alta",
  "proxima_etapa": "agendar_diagnostico_bruno",
  "motivo": "Pousada 18 UHs em operação, dona decide, dor alinhada (OTA-dependência), budget OK",
  "tags": ["pousada_media", "dor_reserva_direta", "fit_forte"]
}
```

### Se DESQUALIFICADO:
```json
{
  "status": "desqualificado",
  "motivo": "Propriedade ainda em construção (abertura em 8 meses)",
  "proxima_etapa": "follow_up_em_5_meses",
  "tags": ["pre_abertura", "futuro_cliente"]
}
```

## Priorização

| Prioridade | Critérios |
|---|---|
| **Alta** | 20+ UHs + dor clara + timing urgente + decisor direto |
| **Média** | 10-20 UHs + dor identificada + timing próximos meses |
| **Baixa** | <10 UHs ou timing indefinido ou fit parcial |

## Casos Especiais

- **Indicação de cliente ativo:** baixar threshold 20% (fit cultural pré-validado)
- **Ex-cliente:** qualificar sempre, prioridade alta
- **No-show 3x:** desqualificar mesmo com fit técnico

## Anti-Patterns

❌ Qualificar só porque "parece ter dinheiro"  
❌ Desqualificar por não engajamento (pode estar ocupado)  
❌ Ignorar a dor e olhar só números  
❌ Qualificar propriedade fora do nicho de hospedagem  
