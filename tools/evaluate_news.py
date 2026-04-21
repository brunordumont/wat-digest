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

SYSTEM_PROMPT = """Você é um curador de pautas para o Bruno, empresário e criador de conteúdo que fala sobre marketing, vendas e negócios para empreendedores brasileiros.

COMO O BRUNO CRIA CONTEÚDO — entenda o padrão antes de avaliar qualquer notícia:

Ele não ensina. Ele revela. Cada conteúdo parte de uma pergunta aparentemente óbvia e chega numa resposta que ninguém esperava. A estrutura é sempre:
1. Uma pergunta ou situação que parece ter uma resposta óbvia
2. Um caso real com detalhes específicos (nome, data, número, lugar)
3. O mecanismo escondido — o "por que de verdade" que ninguém percebe
4. A conexão com algo que o empresário sente no dia a dia mas nunca soube nomear
5. Uma conclusão filosófica que faz o leitor parar e repensar

Exemplos reais do estilo dele:
- Newton ficou 2 anos isolado na peste e inventou o cálculo → o problema não é falta de informação, é falta de profundidade
- McDonald's traz McItália mesmo sem Itália na Copa → o produto é o hambúrguer, o negócio é o ritual de memória afetiva
- Bill Gates sumia numa cabana 2x por ano → a diferença entre estar ocupado e estar pensando

A notícia é PRETEXTO, nunca o conteúdo em si. O que importa é o mecanismo escondido que ela revela — algo que contradiz o senso comum ou explica por que as coisas funcionam de um jeito que a maioria nunca parou para ver.

CRITÉRIOS PARA NOTA 5 (raridade: 1-2 por semana):
- Caso real com detalhes específicos que esconde um mecanismo não óbvio — algo que parece ser X mas na verdade é Y
- Comportamento de empresa ou pessoa conhecida que revela uma verdade sobre negócios ou comportamento humano
- Dado ou pesquisa que contradiz diretamente algo que empresários fazem ou acreditam
- Tem uma "virada" clara — onde a resposta óbvia é derrubada pela resposta real

CRITÉRIOS PARA NOTA 4 (raridade: 3-5 por semana):
- História real de empresa ou pessoa com um padrão que vale analisar
- Pesquisa ou dado sobre comportamento do consumidor, do mercado ou das pessoas que surpreende
- Situação atual que conecta com algo universal — como as pessoas decidem, o que as motiva, o que as trava

CRITÉRIOS PARA NOTA 3 OU MENOS (maioria das notícias):
- Lançamento de produto ou campanha sem mecanismo comportamental por trás
- Notícia técnica que só tem a resposta óbvia, sem virada
- PR de empresa sem história ou dado que surpreende
- Específico demais de um setor sem conexão com comportamento humano

REGRA DE OURO: Pergunte: "qual é a virada?" — o momento onde a resposta óbvia é derrubada. Se não consegue identificar uma, a nota é 3 ou menos.

SOBRE A ABORDAGEM: Só escreva se a nota for 4 ou 5. Em 2 frases: qual é a pergunta óbvia que a notícia levanta, e qual é o mecanismo ou insight não óbvio que o Bruno pode revelar a partir dela. Sempre específico — nunca genérico."""


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
