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


def generate_editorial(articles: list) -> dict:
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

    # Build articles summary
    articles_text = ""
    for i, a in enumerate(top_articles, 1):
        articles_text += f"""
[{i}] {a.get('title', '')}
Fonte: {a.get('source', '')} | Nota: {a.get('ai_nota', 0)}/5
Abordagem sugerida: {a.get('ai_abordagem', '')}
---"""

    prompt = f"""Com base nas melhores pautas do dia, produza a curadoria editorial para o Bruno.

PAUTAS APROVADAS DO DIA:
{articles_text}

Retorne SOMENTE um JSON válido, sem texto adicional:
{{
  "top_picks": [
    {{
      "titulo": "título da matéria",
      "pergunta_obvia": "a pergunta aparentemente óbvia que essa pauta levanta",
      "a_virada": "o mecanismo escondido — a resposta real que derruba a óbvia, específica e surpreendente",
      "conexao_humana": "o que o empresário vai reconhecer na própria vida quando ouvir isso",
      "formato_sugerido": "como entregar (ex: revelar um caso histórico, desconstruir uma crença, analisar um comportamento de mercado)"
    }}
  ],
  "nota_editorial": "2-3 frases: qual pauta está mais potente hoje e por que vai ressoar com o empresário brasileiro agora."
}}

Selecione os 3 melhores top_picks. Seja específico e profundo — nada genérico."""

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
    parser.add_argument("--output", default=".tmp/editorial.json")
    args = parser.parse_args()

    with open(args.news, "r", encoding="utf-8") as f:
        articles = json.load(f)

    print("Generating editorial...")
    editorial = generate_editorial(articles)

    os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else ".", exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(editorial, f, ensure_ascii=False, indent=2)

    picks = len(editorial.get("top_picks", []))
    print(f"Editorial generated: {picks} top picks")
    print(f"Saved to {args.output}")
