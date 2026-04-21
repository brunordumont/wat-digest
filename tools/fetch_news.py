"""
Tool: fetch_news.py
Purpose: Fetch recent news from RSS feeds of specific sources and filter by niche keywords.
Usage: python tools/fetch_news.py --output .tmp/news_raw.json
Output: .tmp/news_raw.json
"""

import os
import json
import argparse
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

DEFAULT_SOURCES = [
    "https://exame.com/feed/",
    "https://forbes.com.br/feed/",
    "https://www.infomoney.com.br/feed/",
    "https://valor.globo.com/rss/",
]

DEFAULT_KEYWORDS = [
    "marketing", "digital", "growth", "vendas", "negócios",
    "empreendedorismo", "estratégia", "branding", "leads",
    "conversão", "receita", "startup", "gestão",
]


def fetch_rss(url: str) -> list:
    try:
        import feedparser
    except ImportError:
        print("ERROR: feedparser not installed. Run: pip install feedparser")
        raise

    print(f"Fetching: {url}")
    feed = feedparser.parse(url)
    articles = []

    for entry in feed.entries:
        published = entry.get("published_parsed") or entry.get("updated_parsed")
        if published:
            pub_dt = datetime(*published[:6], tzinfo=timezone.utc)
        else:
            pub_dt = datetime.now(timezone.utc)

        articles.append({
            "title": entry.get("title", "").strip(),
            "description": entry.get("summary", "").strip(),
            "url": entry.get("link", ""),
            "source": feed.feed.get("title", url),
            "published_at": pub_dt.isoformat(),
            "pub_dt": pub_dt,
        })

    return articles


def is_relevant(article: dict, keywords: list) -> bool:
    text = (article["title"] + " " + article["description"]).lower()
    return any(kw.lower() in text for kw in keywords)


def fetch_all(sources: list, keywords: list, days: int = 1) -> list:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    all_articles = []

    for url in sources:
        try:
            articles = fetch_rss(url)
            recent = [a for a in articles if a["pub_dt"] >= cutoff]
            relevant = [a for a in recent if is_relevant(a, keywords)]
            print(f"  → {len(articles)} total | {len(recent)} recent | {len(relevant)} relevant")
            all_articles.extend(relevant)
        except Exception as e:
            print(f"  ERROR fetching {url}: {e}")

    # Remove pub_dt (not serializable) before saving
    for a in all_articles:
        a.pop("pub_dt", None)

    # Sort by published_at descending
    all_articles.sort(key=lambda x: x["published_at"], reverse=True)

    print(f"\nTotal relevant articles: {len(all_articles)}")
    return all_articles


def save_results(articles: list, output_path: str):
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch news from RSS feeds")
    parser.add_argument("--sources", default=os.getenv("RSS_SOURCES", ",".join(DEFAULT_SOURCES)))
    parser.add_argument("--keywords", default=os.getenv("NICHE_KEYWORDS", ",".join(DEFAULT_KEYWORDS)))
    parser.add_argument("--days", type=int, default=1)
    parser.add_argument("--output", default=".tmp/news_raw.json")
    args = parser.parse_args()

    sources = [s.strip() for s in args.sources.split(",") if s.strip()]
    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]

    articles = fetch_all(sources, keywords, args.days)
    save_results(articles, args.output)
