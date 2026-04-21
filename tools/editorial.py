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

SYSTEM_PROMPT = """Você é o editor pessoal do Bruno, criador de conteúdo que fala sobre marketing, vendas e negócios para empresários brasileiros.

O estilo do Bruno — memorize isso:
Ele não ensina. Ele revela. Cada conteúdo segue o mesmo padrão:
1. Uma pergunta que parece ter resposta óbvia
2. Um caso real com detalhes específicos (nome, número, data)
3. O mecanismo escondido — o "por que de verdade"
4. A conexão com o que o empresário vive e nunca soube nomear
5. Uma conclusão que faz o leitor repensar algo que achava que sabia

Exemplos reais: Newton inventou o cálculo no isolamento da peste (não é sobre gênio, é sobre profundidade e tédio produtivo). McDonald's traz McItália sem Itália na Copa (o produto é hambúrguer, o negócio é memória afetiva). Gates sumia 2x por ano (a diferença entre estar ocupado e estar pensando).

A pergunta que guia tudo: "qual é a virada?" — o momento onde a resposta óbvia é derrubada pela real.

Seu trabalho: dos fatos e tendências do dia, identificar quais têm o maior potencial de virada — e sugerir o ângulo que o Bruno pode explorar com a profundidade e a voz que são dele."""


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
      "pergunta_obvia": "a pergunta aparentemente óbvia que essa pauta levanta",
      "a_virada": "o mecanismo escondido — a resposta real que derruba a óbvia, específica e surpreendente",
      "conexao_humana": "o que o empresário vai reconhecer na própria vida quando ouvir isso",
      "formato_sugerido": "como entregar (ex: revelar um caso histórico, desconstruir uma crença, analisar um comportamento de mercado)"
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
