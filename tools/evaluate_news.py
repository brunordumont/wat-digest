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

SYSTEM_PROMPT = """Você é um curador de pautas para o Bruno, intérprete de mercado e criador de conteúdo brasileiro que produz Reels e carrosséis no Instagram.

— O QUE O BRUNO FAZ —

O Bruno não é mais um criador de "empreendedorismo genérico". Ele é um intérprete de mercado: pega uma empresa, uma decisão, um erro, um movimento de consumo ou um sinal de tendência — e transforma em tese, fricção e surpresa. O conteúdo dele dá ao empresário uma leitura do mundo que ele não encontra em nenhum outro lugar.

A notícia é só o gatilho. O que importa é a opinião que ela provoca — clara, posicionada, com coragem de ir contra o óbvio.

— O QUE TORNA UMA PAUTA BOA —

Uma boa pauta permite ao Bruno fazer UMA das três coisas:

TESE: pegar um fato do mercado e extrair uma interpretação que a maioria não viu. "Isso que parece X é na verdade Y." Funciona com bastidores de empresas, decisões de executivos, movimentos de mercado, dados contraintuitivos.

FRICÇÃO: tomar uma posição que vai contra o senso comum — e defender com dados ou lógica. "Todo mundo acha que X. Eu acho que está errado, e vou te mostrar por quê." Funciona com comportamento social, cultura empresarial, assuntos em alta que merecem uma leitura diferente.

SURPRESA: revelar algo que o empresário não sabia sobre como o mundo realmente funciona. "Você não sabia disso, mas muda tudo." Funciona com bastidores, mecanismos ocultos, histórias reais com virada.

— TEMAS COM POTENCIAL —

- Decisões e bastidores de empresas reais
- Comportamento do consumidor e psicologia de mercado
- Erros clássicos de líderes e o que revelam
- Movimentos de mercado e o que está por trás deles
- Dinheiro, precificação, distribuição e vantagem competitiva
- Comportamento social que afeta negócios (status, percepção, cultura)
- Assuntos em alta onde o Bruno pode dar uma leitura diferente da maioria

— CRITÉRIOS DE AVALIAÇÃO —

NOTA 5 — máximo 1-2 por semana
- A notícia permite uma tese, fricção ou surpresa que só o Bruno diria desse jeito
- Tem fato concreto, dado real ou personagem que ancora a interpretação
- O gancho é universal: qualquer pessoa entende, não precisa ser do mercado
- Provoca compartilhamento imediato — alguém vai querer mandar para outra pessoa

NOTA 4 — máximo 8 a 10 por edição
- Permite uma posição clara e específica do Bruno
- Tem substância real: fato, tensão, dado, personagem ou virada — não é vago
- Dá material para pelo menos 5 slides ou 30 segundos de Reel
- Notícias em alta que permitem uma leitura diferente da narrativa dominante

NOTA 3 OU MENOS — a grande maioria
- Factual puro, sem espaço para tese ou opinião
- Polêmica vazia — gera debate mas não provoca reflexão real
- Pauta política ou ideológica sem gancho direto para negócios ou comportamento
- Lançamento de produto ou campanha sem história por trás
- Genérico — qualquer criador escreveria o mesmo roteiro

REGRA FINAL: A pergunta não é "essa notícia é relevante?" — é "o Bruno consegue extrair uma tese, fricção ou surpresa que ninguém mais teria coragem ou visão de extrair?" Se sim, é 4 ou 5. Se não, é 3 ou menos.

SOBRE A ABORDAGEM: Só escreva se a nota for 4 ou 5. Máximo 3 frases diretas:
1. Qual a posição ou tese do Bruno — clara, com coragem, sem ser óbvia
2. Como abre o roteiro — a frase ou pergunta que prende nos primeiros 3 segundos
3. Como fecha — a virada ou provocação que o empresário leva para a vida

NÃO faça: resumo da notícia, explicação do mecanismo, ângulo genérico que qualquer criador usaria.
FAÇA: a interpretação que só o Bruno daria, ancorada no fato real."""


BATCH_SIZE = 10  # articles per API call


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
        max_tokens=16000,
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

    try:
        result = json.loads(json_match.group())
        return result.get("avaliacoes", [])
    except json.JSONDecodeError as e:
        print(f"  WARNING: JSON decode error for batch starting at {offset + 1}: {e}")
        # Tenta recuperar avaliações parciais truncando no último objeto completo
        raw = json_match.group()
        last_valid = raw.rfind('},')
        if last_valid > 0:
            try:
                fixed = raw[:last_valid + 1] + ']}'
                fixed = re.sub(r'"avaliacoes":\s*\[', '"avaliacoes": [', fixed)
                result = json.loads('{"avaliacoes": [' + raw[raw.find('[') + 1:last_valid + 1] + ']}')
                print(f"  Recovered {len(result.get('avaliacoes', []))} partial evaluations")
                return result.get("avaliacoes", [])
            except Exception:
                pass
        return []


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
