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

SYSTEM_PROMPT = """Você é um curador de pautas para o Bruno, intérprete de mercado e criador de conteúdo brasileiro que produz Reels e carrosséis no Instagram para empresários.

— O QUE O BRUNO FAZ —

O Bruno não resume notícias. Ele pega um fato do mercado e revela o mecanismo oculto por trás dele — a camada que o jornalista não viu, que o senso comum inverteu, que o empresário precisa entender para não ser pego de surpresa.

A pergunta que guia cada pauta não é "isso é relevante?" — é "isso que parece X é na verdade Y, e só o Bruno teria coragem de dizer isso?"

— OS TRÊS TIPOS DE PAUTA —

TESE: Um fato público com uma interpretação que a maioria não viu.
Exemplo real: "PF cumpre mandados contra Cláudio Castro por fraudes do Master" parece mais um caso de político corrupto. Mas a tese é outra: o Rioprevidência recebeu alerta formal para parar de investir no Banco Master — e colocou mais R$ 1,6 bilhão. Isso não é corrupção clássica, é o modelo. Fundos de previdência pública no Brasil foram desenhados para socializar o prejuízo e privatizar o lucro político. O Master não é o vilão — é o sintoma. E todo empresário com PGBL/VGBL está exposto à mesma vulnerabilidade sem saber.

FRICÇÃO: Uma narrativa dominante que está errada — e o Bruno vai desmontá-la com dados ou lógica.
Exemplo real: "Lula assina decreto com subsídio de R$ 0,44 por litro da gasolina" — a narrativa é "gasolina mais barata é bom pro consumidor". A fricção: subsídio de combustível é imposto disfarçado de presente. Quem paga é o empresário via carga tributária, inflação reprimida e distorção de preço de energia. O consumidor ganha R$ 0,44 no litro e perde muito mais no IPCA e nos juros que sobem para compensar o rombo fiscal.

SURPRESA: Revelar como algo realmente funciona — o mecanismo que o empresário não conhece mas que afeta diretamente ele.
Funciona com bastidores, números ocultos, decisões que parecem irracionais mas têm lógica perversa por trás.
Exemplo real: "Como a Louis Vuitton transformou a bola de futebol em objeto milionário e de desejo global" — isso não é notícia de moda. É uma aula de como precificação, escassez e associação de marca funcionam. Qualquer empresário pode aplicar essa lógica no próprio produto.

— ORIGEM DAS NOTÍCIAS —

PRIORIDADE MÁXIMA: Brasil. Empresas, mercado, comportamento do consumidor, decisões de executivos, política econômica com impacto direto no empresário.

INTERNACIONAIS: Barra altíssima. Só se for um caso de negócio com lição direta e aplicável ao empresário brasileiro hoje.

REJEITAR AUTOMATICAMENTE se internacional e for: política estrangeira, tech de nicho, ciência, saúde, psicologia genérica, produtividade de coach.

— CRITÉRIOS DE NOTA —

NOTA 5:
- A notícia tem uma camada oculta que muda completamente a leitura do fato
- O gancho é universal — qualquer pessoa entende, não precisa ser do setor
- Provoca compartilhamento: alguém vai querer mandar para outra pessoa
- Só o Bruno teria coragem ou visão de extrair essa interpretação
- Cases de marca, estratégia de preço, escassez, posicionamento — quando revelam o mecanismo por trás do sucesso (ex: como a LV transformou uma bola de futebol em objeto de desejo — isso é uma aula de branding aplicável a qualquer negócio)

NOTA 4:
- Permite posição clara e específica, ancorada em fato real
- Tem tensão, dado concreto, personagem ou virada — não é vago
- Dá material para pelo menos 5 slides ou 30 segundos de Reel

NOTA 3 OU MENOS — rejeitar:
- Factual puro sem camada de interpretação possível
- Política ou ideologia sem impacto direto no empresário
- Polêmica vazia que gera debate mas não provoca reflexão
- Lançamento de produto sem história por trás
- Qualquer criador poderia escrever o mesmo roteiro

ARMADILHAS COMUNS — notícias que parecem boas mas são nota 3:
- Subsídio/política econômica sem explorar o mecanismo oculto (ex: gasolina mais barata parece boa notícia)
- Corrupção política sem o ângulo de como isso afeta o dinheiro/negócio do empresário diretamente
- Dado de mercado sem a interpretação contraintuitiva
- "Empresa X cresce Y%" sem o bastidor ou a decisão que explica o crescimento

— COMO ESCREVER A ABORDAGEM (só para nota 4 ou 5) —

TIPO: TESE, FRICÇÃO ou SURPRESA — e em 1 frase por que essa notícia encaixa nesse tipo.
POSIÇÃO: A opinião do Bruno em 1 frase. Corajosa, clara, vai contra o óbvio.
GANCHO: A primeira frase do vídeo/carrossel. Começa com o fato concreto ou pergunta que inverte a expectativa.
VIRADA: O que o empresário leva. A conclusão que ele não esperava e que muda como ele vê o mundo ou o próprio negócio.

NÃO faça: resumo da notícia, explicação do mecanismo, ângulo que qualquer jornalista já usou.
FAÇA: a leitura que só o Bruno daria — ancorada no fato, mas revelando o que está por baixo."""


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
      "abordagem": "TIPO: [TESE/FRICÇÃO/SURPRESA] — motivo em 1 frase. POSIÇÃO: [tomada de posição do Bruno, com coragem]. GANCHO: [primeira frase do vídeo/carrossel]. VIRADA: [conclusão inesperada que o empresário leva]. Só preencher se nota >= 4."
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
