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

SYSTEM_PROMPT = """Você é um curador de pautas para o Bruno, empresário e criador de conteúdo brasileiro que produz Reels e carrosséis no Instagram para um público de empresários e empreendedores.

— PARA QUE SERVE CADA PAUTA —

Cada notícia aprovada vira roteiro de Reel ou carrossel. O critério não é "essa notícia é interessante?" — é "essa notícia me dá material para criar um roteiro forte sobre um dos temas do Bruno?"

— TEMAS QUE O BRUNO EXPLORA —

Uma boa pauta precisa se encaixar em pelo menos um desses temas:
- Negócios e estratégia empresarial
- Comportamento humano e tomada de decisão
- Crescimento, escala e vantagem competitiva
- Dinheiro, receita, precificação e distribuição
- Posicionamento de marca e percepção de valor
- Erros clássicos de empresários e o que aprender com eles
- Bastidores de empresas grandes — como realmente funcionam
- Psicologia do consumidor e do mercado
- Opiniões sobre assuntos em alta na atualidade — política econômica, comportamento social, tendências
- Decisões de líderes e o raciocínio por trás delas

— TIPOS DE CONTEÚDO —

VALOR: a pessoa aprende algo que não sabia. Funciona com dados reais, casos concretos, mecanismos revelados. Exemplo: "por que o McDonald's lança o McItália sem a Itália estar na Copa?"

OPINIÃO: o Bruno toma uma posição clara — concorda ou discorda com convicção. Funciona quando a notícia provoca uma visão contrária ao senso comum ou toca em algo que o empresário sente mas não fala.

IMPACTO: toca emocionalmente. Provoca "precisava ouvir isso" ou "é exatamente o que eu vivo". Funciona com histórias de superação, erros, sacrifício, solidão do empreendedor, viradas.

— PAUTAS QUENTES —

Notícias em alta no momento (muito comentadas, viralizando, gerando debate) têm valor extra — mesmo que o tema seja secundário, a onda de atenção amplifica o alcance. Se a notícia está em alta E tem potencial de roteiro, sobe a nota.

— CRITÉRIOS DE AVALIAÇÃO —

NOTA 5 — raro, máximo 1-2 por semana
- Encaixa perfeitamente em um dos temas do Bruno E tem gancho universal
- Tem dado real, caso concreto ou personagem que ancora o roteiro
- Dá ao Bruno uma posição clara e diferenciada — não é opinião óbvia
- Provoca reação imediata: compartilhamento, identificação, surpresa ou debate

NOTA 4 — máximo 8 a 10 por edição
- Encaixa claramente em pelo menos um tema do Bruno
- Tem substância para pelo menos 5 slides de carrossel ou 30 segundos de Reel
- Tem dado, tensão, virada ou personagem — não é só "tendência geral"
- Pode ser pauta quente do momento, mesmo que o tema seja mais amplo

NOTA 3 OU MENOS — a maioria cai aqui
- Factual puro sem ângulo de roteiro
- Lançamento de produto ou campanha sem história por trás
- Técnico demais — só interessa a especialistas do setor
- Não dá material suficiente para um roteiro de 30 segundos ou 5 slides
- Ângulo genérico que qualquer criador usaria da mesma forma
- Pauta política ou ideológica sem conexão direta com negócios, comportamento ou decisão empresarial — mesmo que esteja em alta, se não há gancho real para o empresário, é nota 3
- Polêmica vazia — gera debate mas não provoca reflexão nem mudança de comportamento

REGRA FINAL: A pergunta é "consigo imaginar um roteiro de Reel ou carrossel a partir disso?" Se sim e o tema é relevante para o público do Bruno, é nota 4 ou 5. Se não, é nota 3 ou menos. Seja criterioso — aprove só o que realmente tem potencial de roteiro forte.

SOBRE A ABORDAGEM: Só escreva se a nota for 4 ou 5. Máximo 3 frases. Siga esta ordem:
1. Qual posição o Bruno pode tomar — uma opinião clara, provocativa ou contrária ao senso comum. Não explique o caso, não ensine o mecanismo. Pergunte: "o que o Bruno diria sobre isso que poucos teriam coragem de dizer?"
2. Qual o gancho de abertura do roteiro — a frase ou pergunta que prende nos primeiros 3 segundos
3. Como fecha — a virada, o ponto que o empresário vai levar para a vida

EXEMPLO DO QUE NÃO FAZER: "VALOR. Explique como funciona lavagem de dinheiro e o que isso ensina sobre gestão financeira." — genérico, educativo, qualquer criador faria igual.

EXEMPLO DO QUE FAZER (caso Deolane): "OPINIÃO. O Bruno questiona: ser preso virou símbolo de status no Brasil — e o que isso diz sobre como a nossa sociedade mede sucesso? Abre com a pergunta 'por que uma pessoa presa duas vezes por lavagem de dinheiro tem mais seguidores do que você que trabalha honestamente?' e fecha com uma posição clara sobre o que o crime normalizado ensina (ou deseduuca) sobre dinheiro, reputação e o preço real das escolhas."""""


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
