#!/bin/bash
# run_digest.sh — Executa o pipeline completo do digest diário

set -e

PROJECT_DIR="/Users/bruno/TESTE CLAUDE CODE"
cd "$PROJECT_DIR"

echo "=== Digest Diário de Notícias ==="
echo "$(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Step 1: Fetch news from RSS feeds
echo "[1/6] Buscando notícias..."
python3 tools/fetch_news.py --days 3 --output .tmp/news_raw.json

# Step 2: Filter articles
echo ""
echo "[2/6] Filtrando artigos..."
python3 tools/filter_news.py --input .tmp/news_raw.json --output .tmp/news_filtered.json

# Step 3: AI evaluation
echo ""
echo "[3/6] Avaliando potencial de conteúdo com IA..."
python3 tools/evaluate_news.py --input .tmp/news_filtered.json --output .tmp/news_evaluated.json

# Step 4: Generate editorial
echo ""
echo "[4/5] Gerando curadoria editorial..."
python3 tools/editorial.py --news .tmp/news_evaluated.json --output .tmp/editorial.json

# Step 5: Send email
echo ""
echo "[5/5] Enviando e-mail..."
python3 tools/send_email.py --input .tmp/news_evaluated.json --editorial .tmp/editorial.json

echo ""
echo "=== Concluído ==="
