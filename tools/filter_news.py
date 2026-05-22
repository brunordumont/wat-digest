"""
Tool: filter_news.py
Purpose: Filter and rank raw news articles by relevance, removing duplicates and low-quality items.
Usage: python tools/filter_news.py --input .tmp/news_raw.json --output .tmp/news_filtered.json
Output: .tmp/news_filtered.json
"""

import os
import json
import argparse
from datetime import datetime

# Fontes internacionais que só passam se tiverem gancho explícito com Brasil
INTERNATIONAL_ONLY_SOURCES = [
    "scientificamerican.com",
    "bigthink.com",
    "feedburner.com/TheAtlantic",
    "theatlantic.com",
    "wired.com",
    "fastcompany.com",
    "inc.com",
    "businessinsider.com",
    "marketingdive.com",
    "marketingweek.com",
    "notboring.co",
    "hbr.org",
    "harvardbusiness",
]

BRAZIL_KEYWORDS = [
    "brasil", "brazil", "brasileiro", "brasileira", "são paulo", "rio de janeiro",
    "mercado brasileiro", "empresas brasileiras", "real", "bndes", "ibge",
    "embrapa", "petrobras", "vale ", "ambev", "itaú", "bradesco", "nubank",
]


def is_international_source(url: str) -> bool:
    return any(domain in url.lower() for domain in INTERNATIONAL_ONLY_SOURCES)


def has_brazil_hook(article: dict) -> bool:
    text = ((article.get("title") or "") + " " + (article.get("description") or "")).lower()
    return any(kw in text for kw in BRAZIL_KEYWORDS)


def filter_articles(articles: list, min_description_length: int = 50) -> list:
    seen_titles = set()
    filtered = []

    for article in articles:
        title = (article.get("title") or "").strip()
        description = (article.get("description") or "").strip()
        url = article.get("url", "")
        source = article.get("source", "Unknown")
        if isinstance(source, dict):
            source = source.get("name", "Unknown")

        # Skip removed or empty articles
        if title in ("[Removed]", "") or not url:
            continue

        # Skip duplicates
        if title.lower() in seen_titles:
            continue

        # Skip articles with very short descriptions
        if len(description) < min_description_length:
            continue

        # International sources: only pass if there's an explicit Brazil hook
        if is_international_source(url) and not has_brazil_hook(article):
            continue

        seen_titles.add(title.lower())
        filtered.append({
            "title": title,
            "description": description,
            "url": url,
            "source": source,
            "published_at": article.get("published_at") or article.get("publishedAt", ""),
            "content_hook": description[:200] + "..." if len(description) > 200 else description,
        })

    print(f"Filtered: {len(articles)} → {len(filtered)} articles")
    return filtered


def save_results(articles: list, output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter and rank news articles")
    parser.add_argument("--input", default=".tmp/news_raw.json")
    parser.add_argument("--output", default=".tmp/news_filtered.json")
    parser.add_argument("--min-desc", type=int, default=50)
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        articles = json.load(f)

    filtered = filter_articles(articles, args.min_desc)
    save_results(filtered, args.output)
