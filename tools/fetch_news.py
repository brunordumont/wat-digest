"""
Tool: fetch_news.py
Purpose: Fetch recent news from RSS feeds. Niche sources are filtered by keywords; general sources pass all articles.
Usage: python tools/fetch_news.py --output .tmp/news_raw.json
Output: .tmp/news_raw.json
"""

import os
import json
import re
import argparse
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

DEFAULT_SOURCES = [
    # Brasil — negócios e mercado
    "https://braziljournal.com/feed/",           # bastidores, executivos, capital, mercado
    "https://neofeed.com.br/feed/",              # análises, líderes, estratégia, crises
    "https://exame.com/feed/",
    "https://forbes.com.br/feed/",
    "https://www.infomoney.com.br/feed/",
    "https://valor.globo.com/rss/",
    "https://www.publicitarioscriativos.com/feed/",
    "https://www.meioemensagem.com.br/feed/",
    "https://news.google.com/rss/search?q=site:meioemensagem.com.br&hl=pt-BR&gl=BR&ceid=BR:pt-419",  # fallback via Google News
    # Internacional — estratégia e negócios
    "https://www.marketingdive.com/feeds/news/",
    "https://feeds.hbr.org/harvardbusiness",
    "https://www.fastcompany.com/latest/rss",
    "https://www.inc.com/rss",
    "https://feeds.businessinsider.com/custom/all",
    "https://www.marketingweek.com/feed/",
    "https://www.notboring.co/feed",             # tese, posicionamento, vantagem competitiva
    "https://news.google.com/rss/search?q=site:cbinsights.com&hl=en-US&gl=US&ceid=US:en",  # CB Insights via Google News
    # Brasil — geral (sem filtro de keyword, IA decide)
    "https://feeds.folha.uol.com.br/folha/cotidiano/rss091.xml",
    "https://feeds.bbci.co.uk/portuguese/rss.xml",
    "https://g1.globo.com/rss/g1/",
    "https://veja.abril.com.br/feed/",
    # Internacional — geral (sem filtro de keyword, IA decide)
    "https://feeds.feedburner.com/TheAtlantic",
    "https://www.wired.com/feed/rss",
    "https://bigthink.com/feed/",
    "https://revistaoeste.com/feed/",
]

DEFAULT_KEYWORDS = [
    "marketing", "digital", "growth", "vendas", "negócios",
    "empreendedorismo", "estratégia", "branding", "leads",
    "conversão", "receita", "startup", "gestão", "empresa",
    "decisão", "comportamento", "posicionamento", "distribuição",
    "vantagem", "competitivo", "psicologia", "consumidor",
]

# Sources that cover general topics — bypass keyword filter, let AI decide relevance
GENERAL_SOURCES = [
    "braziljournal.com",
    "neofeed.com.br",
    "notboring.co",
    "folha.uol.com.br",
    "bbci.co.uk",
    "g1.globo.com",
    "veja.abril.com.br",
    "feedburner.com/TheAtlantic",
    "wired.com",
    "bigthink.com",
    "revistaoeste.com",
    "cbinsights.com",
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

        raw_desc = entry.get("summary", "") or ""
        clean_desc = re.sub(r'<[^>]+>', '', raw_desc).strip()

        articles.append({
            "title": entry.get("title", "").strip(),
            "description": clean_desc,
            "url": entry.get("link", ""),
            "source": feed.feed.get("title", url),
            "published_at": pub_dt.isoformat(),
            "pub_dt": pub_dt,
        })

    return articles


def is_general_source(url: str) -> bool:
    return any(domain in url for domain in GENERAL_SOURCES)


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

            if is_general_source(url):
                relevant = recent[:10]  # general sources: top 10 most recent, AI decides relevance
            else:
                relevant = [a for a in recent if is_relevant(a, keywords)][:20]

            print(f"  → {len(articles)} total | {len(recent)} recent | {len(relevant)} relevant")
            all_articles.extend(relevant)
        except Exception as e:
            print(f"  ERROR fetching {url}: {e}")

    for a in all_articles:
        a.pop("pub_dt", None)

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
