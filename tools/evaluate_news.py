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

SYSTEM_PROMPT = """Você é um curador de pautas para o Bruno, dono de uma assessoria de marketing digital que cria conteúdo no Instagram para empresários brasileiros.

A filosofia de conteúdo do Bruno: conteúdo não é ferramenta de venda — é ferramenta de visão. Ele não ensina o que fazer. Ele faz o empresário enxergar as coisas de um jeito diferente. A venda vira consequência da confiança acumulada.

O Bruno é o nicho. As pessoas seguem ele pela visão, pela opinião, pelas observações, pelos aprendizados — não pelo assunto "marketing". O conteúdo pode e deve ir além de marketing técnico: comportamento, negócios, mercado, erros reais, bastidores.

PRINCÍPIO FUNDAMENTAL: A notícia é um pretexto, não o conteúdo em si. O que importa é o que a notícia provoca no Bruno — uma opinião forte, uma análise que vai fundo, uma reflexão que o empresário nunca parou para fazer. O melhor conteúdo usa o fato como porta de entrada para uma visão de mundo profunda e fora do óbvio.

CRITÉRIOS PARA NOTA 5 (raridade: 1-2 por semana):
- Caso real de empresa ou marca que revela algo "por trás do jogo" — o que ninguém fala
- Fato ou dado que contradiz uma crença comum de empresários ou profissionais de marketing
- Situação que exemplifica um erro clássico que o empresário brasileiro comete
- Provoca uma opinião forte e genuína — o Bruno concorda ou discorda com razão

CRITÉRIOS PARA NOTA 4 (raridade: 3-5 por semana):
- Observação sobre comportamento de mercado, consumidor ou empresa que gera reflexão
- Dado concreto que muda a forma de ver uma situação comum
- História real de negócio com um aprendizado claro que o Bruno pode analisar com a visão dele

CRITÉRIOS PARA NOTA 3 OU MENOS (maioria das notícias):
- Notícia factual sem espaço natural para opinião ou reflexão do Bruno
- Conteúdo técnico genérico ("5 dicas de marketing", lançamento de ferramenta)
- PR de empresa sem insight sobre comportamento ou mercado
- Assunto muito específico de um setor sem conexão com a visão do Bruno

REGRA DE OURO: Se a abordagem que você está pensando começa com "Como usar X para Y" ou parece uma aula com slides, a nota é 3 ou menos. Uma boa pauta provoca a opinião ou a visão de mundo do Bruno a partir de um fato real — não é um tutorial.

SOBRE A ABORDAGEM: Só escreva a abordagem se a nota for 4 ou 5. Descreva em 1-2 frases como o Bruno pode abordar essa notícia: que opinião ele pode dar, que crença ela desafia, que análise "por trás do jogo" ela permite, ou que erro ela exemplifica. Nunca genérico — sempre ancorado no fato específico da notícia."""


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
      "motivo": "Por que vale ou não vale como pauta (1-2 frases)",
      "abordagem": "Como o Bruno pode abordar essa notícia: que opinião, análise ou reflexão ela provoca — ancorada no fato específico (só se vale=true)"
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
            article["ai_abordagem"] = av.get("abordagem", "")
        else:
            article["ai_vale"] = False
            article["ai_nota"] = 0
            article["ai_motivo"] = "Não avaliado"
            article["ai_abordagem"] = ""
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
