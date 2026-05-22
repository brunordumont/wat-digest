---
name: content-calendar
description: Use when Chief (content orchestrator) plans client's editorial calendar — 4-8 week horizon, 3-5 posts/week, mix of formats (carousel, reel, static, story). MotorSales clients post 4-6x/week focused on used-car dealership audience.
metadata:
  version: 1.0.0
  domain: creative
  owner_agents: Chief, CS Manager
  requires_config:
    - brand.icp
    - brand.context
    - brand.voice_profile
---

> **Nota sobre exemplos:** Os exemplos abaixo usam contexto MotorSales (lojas de carros usados · 4-6 posts/semana) como ilustração concreta. **O framework é universal** · adapte o nicho via `brand.icp` e a cadência via `brand.context` quando aplicar a outro negócio.

# Content Calendar Planning

## When to use

Use this skill when:
- Chief agent needs to plan quarterly (12 semanas) content calendar
- Weekly planning (Monday 9h ritual with Analyst report)
- Balancing content pillars across platforms
- Capacity planning (specialist bandwidth vs output targets)
- Strategic content launches (coordinated campaigns)

Do NOT use for:
- Individual post scheduling (that's execution, not planning)
- Ad campaign calendars (Performance team handles)
- Client-specific calendars (each client has own rhythm)

## Instructions

### Planning Horizons

**Strategic (12 semanas):**
- Content pillar distribution
- Platform prioritization
- Major launches/campaigns
- Specialist capacity allocation

**Tactical (Weekly):**
- Specific post topics
- Specialist assignments
- Deadline tracking
- Approval checkpoints

### Content Pillar Framework

MotorSales.ai uses **3 pillars** (rotate for variety):

| Pillar | Purpose | Frequency | Example Topics |
|--------|---------|-----------|----------------|
| **Educational** | Teach insights | 50% | Erros comuns, How-to, Frameworks |
| **Social Proof** | Build credibility | 30% | Cases, Depoimentos, Resultados |
| **Conversion** | Drive action | 20% | Vagas abertas, Free tools, CTAs |

**Balance rule:** No more than 2 consecutive posts same pillar.

### Platform Mix (MotorSales.ai Default)

| Platform | Frequency | Formats |
|----------|-----------|---------|
| Instagram | 3×/semana | 2 Carousels + 1 Static |
| LinkedIn | 2×/semana | 1 Carousel + 1 Text post |
| Blog | 1×/semana | Long-form article (optional) |

**Total output:** 5-6 posts/semana cross-platform

### Weekly Template

```markdown
# Semana XX — DD/MM a DD/MM/YYYY

## Monday Planning (9h)
- Analyst report review (Domingo EOD received)
- Winner identification (top 20% performers)
- Content pillar selection this week
- Specialist assignments

## Production Schedule

### Terça (assignments)
- [ ] Instagram Carousel 1: {Topic} — {Pillar} — {Copywriter assigned}
- [ ] LinkedIn Text Post: {Topic} — {Pillar} — {Copywriter assigned}

### Quarta (drafts due)
- [ ] Instagram Carousel 1 script → Carousel agent
- [ ] LinkedIn Text Post draft → Static agent OR Copy direct

### Quinta (designs due)
- [ ] Instagram Carousel 1 PNG exports ready
- [ ] LinkedIn post formatted (text + optional image)

### Sexta (approval)
- [ ] Arthur batch review (OpenClaw preview)
- [ ] Revisions if needed
- [ ] Schedule publish (Segunda próxima semana)

### Sábado-Domingo
- [ ] Analyst tracking performance
- [ ] Domingo EOD: Weekly report ready
```

### Quarterly Calendar (12 Semanas)

**Structure:**
```markdown
# Q1 2026 — Jan-Mar Content Calendar

## Content Themes
- Semanas 1-4: Holding Cost Crisis (Educational pillar)
- Semanas 5-8: Case Studies Success (Social Proof pillar)
- Semanas 9-12: Free Tools Launch (Conversion pillar)

## Platform Targets
- Instagram: 36 posts total (24 carousels + 12 statics)
- LinkedIn: 24 posts total (12 carousels + 12 text)
- Blog: 12 articles (1/semana)

## Major Launches
- Semana 3: ROI Calculator release (coordinated campaign)
- Semana 7: Case Study #1 "Loja XYZ" (multi-post series)
- Semana 11: Webinar "Evite R$84K/ano" (event funnel)

## Specialist Capacity
- Copy: 6 scripts/semana (sustainable pace)
- Carousel: 3 designs/semana (BrandOS intensive)
- Static: 2 posts/semana (Canva templates faster)
- Tweet: 1 thread/semana (optional bonus content)
- Analyst: 1 report/semana (Domingo ritual)
```

### Repurposing Strategy (Efficiency Multiplier)

**Winners cascade into multi-format:**

```
Week 1: Original Instagram Carousel "7 Erros R$84K/ano" (performs 8.5% ER)
  ↓
Week 2: Repurpose as:
  - LinkedIn text post (slides 1-3 resumo + CTA)
  - Email newsletter (full 10 slides + images inline)
  - Blog article (expand each erro 300 palavras, SEO optimize)
  
Week 3: Continue repurposing:
  - Instagram Stories (1 story per erro, swipe-up carousel)
  - Tweet thread (7 tweets: hook + 5 erros + CTA)
  
Result: 1 carousel creation → 6 posts total (6× ROI)
```

**Rule:** Only repurpose winners (>1.5× benchmark). Never amplify mediocre content.

## Examples

**Example 1: Strategic 12-Week Plan**

```markdown
# Q2 2026 Content Calendar

## Themes
- Abril (4 semanas): Meta Ads Pixel Setup (Educational)
- Maio (4 semanas): Client Wins Series (Social Proof)
- Junho (4 semanas): MotorSales Features (Conversion)

## Output Targets
- 72 posts total cross-platform
- 48 carousels (Instagram + LinkedIn)
- 24 text/static posts
- 12 blog articles

## Key Launches
- Sem 2: Pixel Setup Guide (lead magnet)
- Sem 6: Client Case #1 (video testimonial)
- Sem 10: New Feature Announcement (product update)

## Capacity Planning
- Copy: 6/week × 12 weeks = 72 scripts ✅ (within capacity)
- Carousel: 3/week × 12 weeks = 36 designs ✅
- Static: 2/week × 12 weeks = 24 posts ✅
- Repurposing: ~20 winners → 60 additional posts (bonus content)
```

**Example 2: Tactical Weekly Plan**

```markdown
# Semana 15 — 14-20 Abril 2026

## Analyst Insights (from Domingo report)
- Winner: "5 passos setup Pixel" (7.2% ER) → REPURPOSE
- Loser: Quote posts (<2% ER avg) → KILL format

## This Week Content Pillars
- Educational (60%): Pixel setup deep-dive
- Social Proof (40%): Client win announcement

## Schedule

**Terça:**
- IG Carousel: "Pixel CAPI: 60% mais conversões" (Educational)
- LinkedIn Post: "Cliente vendeu R$240K em 30 dias" (Social Proof)

**Quarta:**
- Copy scripts due → Carousel + Static agents
- Repurpose "5 passos Pixel" → Tweet thread (7 tweets)

**Quinta:**
- Designs ready (PNG exports + formatted posts)
- Blog article: Expand "Pixel CAPI" carousel (1500 palavras SEO)

**Sexta:**
- Arthur batch review 14h
- Schedule publish: Segunda 21 Abril 9h

**Domingo:**
- Analyst report (track this week's 5 posts performance)
```

## Avoid

- Planning >12 semanas ahead (market changes fast, flexibility needed)
- More than 3 content pillars (confusion, lack of focus)
- Same pillar 3+ consecutive posts (audience fatigue)
- Overcommitting specialist capacity (burnout risk)
- Planning without Analyst data (flying blind)
- Rigid calendars (leave 20% flexibility for reactive content)
- Ignoring repurposing queue (efficiency loss - winners should cascade)

**Remember:** Plan 12 weeks strategy, execute 1 week tactical. Balance 3 pillars (Educational 50%, Social Proof 30%, Conversion 20%). Leverage repurposing (1 → 5 formats). Monday 9h ritual (Analyst report → Weekly plan). Analyst-driven (data > intuition). Flexibility buffer (20% reactive capacity).
