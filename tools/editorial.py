"""
Tool: editorial.py
Purpose: Generate an AI editorial with the best content picks and angles for the day.
Usage: python tools/editorial.py --news .tmp/news_evaluated.json --trends .tmp/trends.json --output .tmp/editorial.json
"""

import os
import json
import argparse
import re
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """Você é o editor pessoal do Bruno, dono de uma assessoria de marketing digital que cria conteúdo para empresários brasileiros no Instagram.

Você conhece profundamente a filosofia de conteúdo do Bruno:
- Conteúdo é ferramenta de visão, não de venda. A venda é consequência da confiança.
- O Bruno É o nicho — as pessoas seguem ele pela visão, opinião e observações, não pelo assunto.
- A notícia é um pretexto para provocar uma reflexão profunda, fora do óbvio.
- O melhor conteúdo faz o empresário enxergar algo de um ângulo que ele nunca tinha visto.
- Evitar conteúdo técnico genérico ("5 dicas de..."). Preferir: casos reais, erros, bastidores, opiniões fortes, análises que vão fundo.
- Mix: 60% marketing/negócios + 40% conteúdo humano (rotina, mentalidade, bastidores do empreendedorismo).

Seu trabalho hoje: analisar as melhores pautas do dia e os assuntos em alta, e dar ao Bruno uma visão editorial clara — o que ele deve priorizar e como abordar de forma única."""


def generate_editorial(articles: list, trends: dict) -> dict:
    try:
        import anthropic
    except ImportError:
        print("ERROR: anthropic not installed.")
        raise

    api_key = os.getenv("ANTHROPIC_API_KEY")
    client = anthropic.Anthropic(api_key=api_key)

    # Top articles (nota >= 4)
    top_articles = sorted(
        [a for a in articles if a.get("ai_nota", 0) >= 4],
        key=lambda x: x.get("ai_nota", 0),
        reverse=True
    )[:6]

    trending = trends.get("trending_searches", [])[:15]
    related = trends.get("related_queries", {})

    # Build articles summary
    articles_text = ""
    for i, a in enumerate(top_articles, 1):
        articles_text += f"""
[{i}] {a.get('title', '')}
Fonte: {a.get('source', '')} | Nota: {a.get('ai_nota', 0)}/5
Abordagem sugerida: {a.get('ai_abordagem', '')}
---"""

    # Build trends summary
    trending_text = ", ".join(trending) if trending else "Nenhum dado disponível"
    related_text = ""
    for kw, queries in related.items():
        if queries:
            related_text += f"\n{kw}: {', '.join(queries[:5])}"

    prompt = f"""Com base nas melhores pautas do dia e nos assuntos em alta, produza uma curadoria editorial para o Bruno.

PAUTAS APROVADAS DO DIA:
{articles_text}

ASSUNTOS EM ALTA NO GOOGLE TRENDS (Brasil):
{trending_text}

BUSCAS RELACIONADAS A MARKETING/NEGÓCIOS:
{related_text if related_text else 'Não disponível'}

Retorne SOMENTE um JSON válido, sem texto adicional:
{{
  "top_picks": [
    {{
      "titulo": "título da matéria ou assunto",
      "porque_hoje": "por que essa é a melhor pauta para hoje — o que torna ela especialmente relevante agora",
      "angulo_profundo": "o ângulo específico que o Bruno pode explorar — que visão, opinião ou análise vai fazer o empresário pensar diferente",
      "formato_sugerido": "como entregar (ex: opinião direta, análise de caso, reflexão pessoal, provocação)"
    }}
  ],
  "trends_para_conteudo": [
    {{
      "assunto": "assunto em alta",
      "conexao_com_negocio": "como esse assunto se conecta com a audiência do Bruno — empresários e profissionais de marketing",
      "angulo": "que visão o Bruno pode trazer sobre esse assunto que ninguém está falando"
    }}
  ],
  "nota_editorial": "Uma análise geral do dia em 2-3 frases: o que o momento pede, qual tema está mais potente hoje, qual tipo de conteúdo vai ressoar mais com a audiência do Bruno."
}}

Selecione os 3 melhores top_picks e os 2 trends mais relevantes para a audiência do Bruno. Seja específico e profundo — nada genérico."""

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4000,
        system=[{
            "type": "text",
            "text": SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"}
        }],
        messages=[{"role": "user", "content": prompt}]
    )

    text = next((b.text for b in response.content if b.type == "text"), "")
    json_match = re.search(r'\{[\s\S]*\}', text)
    if not json_match:
        print("WARNING: Could not parse editorial JSON")
        return {}

    return json.loads(json_match.group())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate AI editorial for the digest")
    parser.add_argument("--news", default=".tmp/news_evaluated.json")
    parser.add_argument("--trends", default=".tmp/trends.json")
    parser.add_argument("--output", default=".tmp/editorial.json")
    args = parser.parse_args()

    with open(args.news, "r", encoding="utf-8") as f:
        articles = json.load(f)

    trends = {}
    if os.path.exists(args.trends):
        with open(args.trends, "r", encoding="utf-8") as f:
            trends = json.load(f)

    print("Generating editorial...")
    editorial = generate_editorial(articles, trends)

    os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else ".", exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(editorial, f, ensure_ascii=False, indent=2)

    picks = len(editorial.get("top_picks", []))
    trends_count = len(editorial.get("trends_para_conteudo", []))
    print(f"Editorial generated: {picks} top picks + {trends_count} trend angles")
    print(f"Saved to {args.output}")
