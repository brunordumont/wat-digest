"""
Tool: fetch_trends.py
Purpose: Fetch trending topics from Google Trends (Brazil + global) for content inspiration.
Usage: python tools/fetch_trends.py --output .tmp/trends.json
"""

import json
import argparse
import time
import os


BUSINESS_KEYWORDS = [
    "marketing digital",
    "vendas",
    "empreendedorismo",
    "negócios",
    "redes sociais",
]


def fetch_trending_searches() -> list:
    try:
        from pytrends.request import TrendReq
        pytrends = TrendReq(hl="pt-BR", tz=180, timeout=(10, 30))
        df = pytrends.trending_searches(pn="brazil")
        return df[0].tolist()[:25]
    except Exception as e:
        print(f"  WARNING: Could not fetch trending searches: {e}")
        return []


def fetch_related_queries(keywords: list) -> dict:
    try:
        from pytrends.request import TrendReq
        pytrends = TrendReq(hl="pt-BR", tz=180, timeout=(10, 30))

        related = {}
        # Process in batches of 4 (pytrends limit)
        for i in range(0, len(keywords), 4):
            batch = keywords[i:i + 4]
            pytrends.build_payload(batch, geo="BR", timeframe="now 7-d")
            time.sleep(1)
            queries = pytrends.related_queries()
            for kw in batch:
                try:
                    top = queries.get(kw, {}).get("top")
                    if top is not None and not top.empty:
                        related[kw] = top["query"].tolist()[:8]
                except Exception:
                    pass
        return related
    except Exception as e:
        print(f"  WARNING: Could not fetch related queries: {e}")
        return {}


def fetch_interest_over_time(keywords: list) -> dict:
    try:
        from pytrends.request import TrendReq
        pytrends = TrendReq(hl="pt-BR", tz=180, timeout=(10, 30))
        pytrends.build_payload(keywords[:4], geo="BR", timeframe="now 7-d")
        time.sleep(1)
        df = pytrends.interest_over_time()
        if df.empty:
            return {}
        # Return average interest score per keyword
        return {kw: round(float(df[kw].mean()), 1) for kw in keywords[:4] if kw in df.columns}
    except Exception as e:
        print(f"  WARNING: Could not fetch interest over time: {e}")
        return {}


def save_results(data: dict, output_path: str):
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch Google Trends data")
    parser.add_argument("--output", default=".tmp/trends.json")
    args = parser.parse_args()

    print("Fetching trending searches in Brazil...")
    trending = fetch_trending_searches()
    print(f"  {len(trending)} trending topics found")

    print("Fetching related queries for business keywords...")
    related = fetch_related_queries(BUSINESS_KEYWORDS)
    print(f"  Related queries fetched for {len(related)} keywords")

    print("Fetching interest scores...")
    interest = fetch_interest_over_time(BUSINESS_KEYWORDS)

    result = {
        "trending_searches": trending,
        "related_queries": related,
        "interest_scores": interest,
    }

    save_results(result, args.output)
    print(f"Trends data: {len(trending)} trending + {sum(len(v) for v in related.values())} related queries")
