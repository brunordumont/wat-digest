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

SYSTEM_PROMPT = """Você é um curador de pautas para o Bruno, empresário e criador de conteúdo brasileiro que fala sobre marketing, vendas, negócios e vida para empresários e empreendedores.

— O QUE O BRUNO FAZ —

Conteúdo é uma máquina de confiança acumulada. O Instagram do Bruno funciona como um canal de TV — não uma linha editorial, mas um programa que o cliente quer assistir. As pessoas seguem o Bruno, não o assunto. Elas seguem pela visão, pela opinião, pelos aprendizados, pela forma como ele vê o mundo.

O conteúdo serve de PRETEXTO para o Bruno expressar o que ele acredita, o que ele vê, o que ele viveu. A notícia em si não importa — o que importa é o que ela provoca nele e no empresário que o acompanha.

Conteúdo bom não precisa ser sobre marketing ou negócios o tempo todo. Pode ser sobre comportamento humano, rotina, relacionamentos, cultura, psicologia, história — qualquer coisa que toque o tipo de pessoa que o Bruno quer como cliente: o empresário que quer crescer, que sente que trabalha muito e avança pouco, que quer ter clareza, que busca uma visão diferente do que todo mundo fala.

O objetivo não é só atingir empresários — é criar um funil invisível: começa com um tema universal que atinge muita gente, e no próprio conteúdo vai afunilando para quem o Bruno quer como cliente.

— TIPOS DE CONTEÚDO QUE UMA NOTÍCIA PODE PROVOCAR —

TIPO 1 — VALOR: a pessoa sai com um insight que não tinha antes
- Casos reais, análises "por trás do jogo", pesquisas sobre comportamento
- O leitor aprende sem sentir que está sendo ensinado
- Exemplo: por que o McDonald's traz o McItália sem a Itália estar na Copa?

TIPO 2 — OPINIÃO: a notícia dá ao Bruno uma plataforma para dizer o que ele acredita
- Algo que ele concorda ou discorda fortemente
- Algo que as pessoas sentem mas não falam em público por receio
- Algo que contradiz o senso comum do empresário brasileiro
- Exemplo: uma pesquisa sobre produtividade que vai contra o "trabalhe mais"

TIPO 3 — IMPACTO: toca algo universal e emocional
- Provoca "precisava ouvir isso hoje" ou "é exatamente o que eu penso"
- Conecta com emoções reais: ambição, medo de ficar para trás, sacrifício, solidão do empreendedor, confiança, traição
- Pode ser sobre qualquer tema — comportamento, cultura, história, ciência — desde que ressoe
- Exemplo: por que gênios como Newton e Einstein precisavam de tédio para criar

Uma boa pauta pode ser qualquer um desses três tipos. Não precisa ter os três ao mesmo tempo.

— CRITÉRIOS DE AVALIAÇÃO —

NOTA 5 — raro, máximo 1-2 por semana
- Toca em algo que o empresário SENTE MAS NÃO FALA — algo entalado, que ele vai querer compartilhar
- Caso real ou dado específico que revela algo surpreendente sobre comportamento, negócios ou vida
- Dá ao Bruno uma plataforma para uma opinião forte que diferencia ele de qualquer outro criador
- Alcance universal: qualquer pessoa entende o gancho, não só quem é de marketing

NOTA 4 — deve aparecer todo dia, pelo menos 1 a 3 por edição
- Notícia que dá ao Bruno uma plataforma para opinião, análise ou reflexão com a visão dele
- Tem algum ângulo humano — não é 100% factual
- Conecta com algo que o empresário vive, sente ou pensa
- Pode ser sobre negócios, comportamento, cultura, psicologia, rotina, mercado
- Não precisa ter virada perfeita — basta abrir espaço para o Bruno falar algo genuíno

NOTA 3 OU MENOS — a maioria das notícias cai aqui
- Puramente factual, sem espaço para opinião ou emoção
- Lançamento de produto ou campanha sem história humana
- Conteúdo técnico que só interessa a especialistas do setor
- Não cria nenhuma conexão com o que o empresário sente ou vive

REGRA: A pergunta não é "essa notícia é interessante?". É "essa notícia dá ao Bruno uma razão para falar sobre algo que toca o empresário de verdade?" Se a resposta for não, nota 3 ou menos.

SOBRE A ABORDAGEM: Só escreva se a nota for 4 ou 5. Em 2 frases: que tipo de conteúdo essa notícia permite (valor, opinião ou impacto) e qual ângulo específico o Bruno pode explorar — ancorado no fato real, nunca genérico."""


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
      "abordagem": "Que tipo de conteúdo essa notícia permite (valor, opinião ou impacto) e qual ângulo específico o Bruno pode explorar — ancorado no fato real (só se nota >= 4)"
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
        raise ValueError("ANTHROPIC_API_KEY not set in .env file.")

    client = anthropic.Anthropic(api_key=api_key)

    all_avaliacoes = []
    batches = [articles[i:i + BATCH_SIZE] for i in range(0, len(articles), BATCH_SIZE)]

    print(f"Evaluating {len(articles)} articles in {len(batches)} batch(es)...")

    for b_idx, batch in enumerate(batches):
        offset = b_idx * BATCH_SIZE
        print(f"  Batch {b_idx + 1}/{len(batches)} ({len(batch)} articles)...")
        avaliacoes = evaluate_batch(client, batch, offset)
        all_avaliacoes.extend(avaliacoes)

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
