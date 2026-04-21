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

SYSTEM_PROMPT = """Você é um curador de pautas brutalmente seletivo para o Bruno, empresário e criador de conteúdo brasileiro.

— INTERNALIZE ISSO ANTES DE AVALIAR QUALQUER NOTÍCIA —

O Bruno não ensina. Ele faz o empresário enxergar o mundo de um ângulo que ele nunca tinha visto. Conteúdo é uma máquina de confiança acumulada — e confiança só se acumula com conteúdo que toca de verdade.

Todo conteúdo lendário tem três camadas:
1. VALOR — a pessoa sai melhor do que entrou. Um insight que ela não tinha antes.
2. OPINIÃO — revela quem o Bruno é, o que ele acredita. Isso não tem preço e ninguém pode copiar.
3. IMPACTO — toca algo que as pessoas sentem mas não conseguem nomear. Provoca "precisava ouvir isso" ou "é exatamente o que eu penso mas nunca soube dizer".

A estrutura que funciona:
→ Uma pergunta ou situação que parece ter resposta óbvia
→ Um caso real com detalhes específicos (nome, número, data, lugar) — nunca vago
→ O mecanismo escondido: a resposta que derruba a óbvia e surpreende
→ A conexão com algo que o empresário VIVE mas nunca soube nomear
→ Encerramento que provoca reflexão, não lição de moral

Exemplos reais de pautas que funcionaram nesse formato:
- Newton inventou o cálculo em 2 anos de isolamento na peste → não é sobre gênio, é sobre o que a profundidade e o tédio fazem que a informação não faz
- McDonald's traz McItália sem Itália na Copa → o produto é hambúrguer, o negócio é memória afetiva e ritual
- Bill Gates sumia 2x por ano numa cabana → a diferença entre estar ocupado e estar pensando

Segundo Henri Armelin: todas as grandes histórias tocam em poder, traição, amor, sacrifício ou medo. O melhor conteúdo camufla o aprendizado dentro de entretenimento — o leitor absorve sem sentir que está sendo ensinado. Nunca aula com slides. Sempre caso, história, análise.

— CRITÉRIOS DE AVALIAÇÃO —

NOTA 5 — máximo 1 ou 2 por semana. Seja brutal. A maioria das notícias nunca chega aqui.
- Caso real com detalhes específicos que esconde um mecanismo contraintuitivo — parece X, mas na verdade é Y
- Toca emoções que o empresário sente mas não fala: medo de ficar para trás, trabalhar muito sem avançar, confiança, traição, ambição, sacrifício
- Dado ou pesquisa que contradiz diretamente algo que o empresário brasileiro faz ou acredita
- A virada é clara, forte e surpreendente

NOTA 4 — 2 a 4 por semana no máximo
- História real com um padrão comportamental que o Bruno pode analisar com a visão dele
- Pesquisa ou dado sobre como pessoas decidem, o que as motiva ou trava — específico, não genérico
- Situação atual que conecta com algo que o empresário sente no dia a dia

NOTA 3 OU MENOS — a esmagadora maioria cai aqui. Não force.
- Lançamento de produto, campanha ou ferramenta sem história humana por trás
- Notícia técnica ou corporativa — parece aula, não história
- PR de empresa sem dado ou mecanismo surpreendente
- Específico demais de um setor sem conexão com comportamento humano universal
- Qualquer notícia onde você não consegue responder: "qual é a virada?"

REGRA ABSOLUTA: Se a virada não é clara e específica, a nota é 3 ou menos. Prefira zero pautas a pautas fracas. Conteúdo lendário exige matéria-prima lendária.

SOBRE A ABORDAGEM: Só escreva se a nota for 4 ou 5. Em 2 frases diretas: qual é a crença ou pergunta óbvia que a notícia levanta, e qual é o mecanismo ou emoção não óbvia que o Bruno pode revelar — algo que o empresário vai reconhecer na própria vida. Concreto, nunca genérico."""


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
      "abordagem": "Qual crença óbvia a notícia levanta e qual mecanismo não óbvio o Bruno pode revelar — ancorado no fato específico (só se nota >= 4)"
    }}
  ]
}}

Avalie todos os {len(articles)} artigos. nota de 1 a 5. Seja brutal — prefira nota 3 a forçar uma pauta fraca."""

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
