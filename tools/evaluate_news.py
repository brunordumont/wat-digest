"""
Tool: evaluate_news.py
Purpose: Use Claude to evaluate which news articles are worth using for content creation.
Usage: python tools/evaluate_news.py --input .tmp/news_filtered.json --output .tmp/news_evaluated.json
Output: .tmp/news_evaluated.json — articles enriched with AI evaluation and content suggestions
"""

import os
import json
import argparse
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """Você é um curador de pautas extremamente seletivo para uma assessoria de marketing digital brasileira que produz Reels.

Sua missão é encontrar as poucas notícias que são NATURALMENTE boas pautas — não forçar nada. A maioria das notícias deve ser descartada.

Contexto do criador: assessoria de marketing digital, fala sobre marketing, growth, vendas e negócios para empreendedores e profissionais brasileiros. Tom direto, opiniões fortes, linguagem acessível.

CRITÉRIOS PARA NOTA 5 (raridade: 1-2 por semana):
- Dado ou fato que choca ou surpreende genuinamente o público de marketing/negócios
- Contradiz algo que as pessoas acreditam ou fazem normalmente
- É uma tendência grande que vai impactar diretamente quem trabalha com marketing
- O gancho surge naturalmente do próprio fato — não precisa ser inventado

CRITÉRIOS PARA NOTA 4 (raridade: 3-5 por semana):
- Notícia relevante para o público que abre espaço para uma opinião ou ponto de vista forte
- Dado concreto (número, pesquisa, resultado) que prova um ponto importante
- Caso real de empresa/marca que ilustra um aprendizado claro de marketing

CRITÉRIOS PARA NOTA 3 OU MENOS (maioria das notícias):
- Notícia factual sem ângulo natural para opinião ou ensinamento
- Assunto que já foi muito falado e não traz nada novo
- Lançamento de produto/campanha sem insight acionável
- Específico demais de um setor ou empresa sem conexão com marketing

REGRA DE OURO: Se o gancho que você está pensando começa com "Como usar X para Y" ou é genérico demais, a nota é 3 ou menos. Um bom gancho parte do fato específico da notícia, não de uma lição genérica de marketing.

SOBRE OS GANCHOS: Só escreva gancho e ângulo se a nota for 4 ou 5. O gancho deve citar o dado ou fato específico da notícia — nunca genérico. Exemplo ruim: "Você sabia que o marketing digital está mudando?". Exemplo bom: "A Havaianas perdeu 40% das vendas tentando ser premium — e voltou atrás."."""


BATCH_SIZE = 15  # articles per API call


def evaluate_batch(client, articles: list, offset: int) -> list:
    import re

    articles_text = ""
    for i, a in enumerate(articles, 1):
        articles_text += f"""
[ARTIGO {offset + i}]
Título: {a.get('title', '')}
Fonte: {a.get('source', '')}
Descrição: {a.get('description', '')}
---"""

    user_prompt = f"""Avalie os seguintes artigos e retorne um JSON com sua análise.

{articles_text}

Retorne SOMENTE um JSON válido, sem texto adicional, no seguinte formato:
{{
  "avaliacoes": [
    {{
      "numero": {offset + 1},
      "vale": true,
      "nota": 4,
      "motivo": "Por que vale ou não vale para um Reel (1-2 frases)",
      "gancho": "Frase de abertura do Reel — os primeiros 3 segundos (só se vale=true)",
      "angulo": "O que ensinar ou defender no Reel em 1 frase (só se vale=true)"
    }}
  ]
}}

Avalie todos os {len(articles)} artigos. nota de 1 a 5."""

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=8000,
        system=[{
            "type": "text",
            "text": SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"}
        }],
        messages=[{"role": "user", "content": user_prompt}]
    )

    text = next((b.text for b in response.content if b.type == "text"), "")

    json_match = re.search(r'\{[\s\S]*\}', text)
    if not json_match:
        print(f"  WARNING: Could not parse JSON for batch starting at {offset + 1}")
        return []

    result = json.loads(json_match.group())
    return result.get("avaliacoes", [])


def evaluate_articles(articles: list) -> list:
    try:
        import anthropic
    except ImportError:
        print("ERROR: anthropic not installed. Run: pip install anthropic")
        raise

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key == "your_anthropic_api_key_here":
        raise ValueError("ANTHROPIC_API_KEY not set in .env file. Get one at https://anthropic.com")

    client = anthropic.Anthropic(api_key=api_key)

    # Process in batches to avoid token limits
    all_avaliacoes = []
    batches = [articles[i:i + BATCH_SIZE] for i in range(0, len(articles), BATCH_SIZE)]

    print(f"Evaluating {len(articles)} articles in {len(batches)} batch(es)...")

    for b_idx, batch in enumerate(batches):
        offset = b_idx * BATCH_SIZE
        print(f"  Batch {b_idx + 1}/{len(batches)} ({len(batch)} articles)...")
        avaliacoes = evaluate_batch(client, batch, offset)
        all_avaliacoes.extend(avaliacoes)

    # Merge evaluation back into articles
    evaluated = []
    for i, article in enumerate(articles):
        av = next((a for a in all_avaliacoes if a.get("numero") == i + 1), None)
        if av:
            article["ai_vale"] = av.get("vale", False)
            article["ai_nota"] = av.get("nota", 0)
            article["ai_motivo"] = av.get("motivo", "")
            article["ai_gancho"] = av.get("gancho", "")
            article["ai_angulo"] = av.get("angulo", "")
        else:
            article["ai_vale"] = False
            article["ai_nota"] = 0
            article["ai_motivo"] = "Não avaliado"
            article["ai_angulo"] = ""
            article["ai_formato"] = ""
        evaluated.append(article)

    worth = [a for a in evaluated if a["ai_vale"]]
    print(f"Evaluation complete: {len(worth)}/{len(evaluated)} articles worth using for content")

    return evaluated


def save_results(articles: list, output_path: str):
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate news articles for content potential")
    parser.add_argument("--input", default=".tmp/news_filtered.json")
    parser.add_argument("--output", default=".tmp/news_evaluated.json")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        articles = json.load(f)

    if not articles:
        print("No articles to evaluate.")
        save_results([], args.output)
    else:
        evaluated = evaluate_articles(articles)
        save_results(evaluated, args.output)
