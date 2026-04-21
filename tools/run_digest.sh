#!/bin/bash
# run_digest.sh — Executa o pipeline completo do digest diário
# Cron sugerido (8h da manhã): 0 8 * * * /bin/bash "/Users/bruno/Teste Claude Code/tools/run_digest.sh"

set -e

PROJECT_DIR="/Users/bruno/Teste Claude Code"
cd "$PROJECT_DIR"

echo "=== Digest Diário de Notícias ==="
echo "$(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Step 1: Fetch news from RSS feeds
echo "[1/4] Buscando notícias..."
python3 tools/fetch_news.py --days 3 --output .tmp/news_raw.json

# Step 2: Filter articles
echo ""
echo "[2/4] Filtrando artigos..."
python3 tools/filter_news.py --input .tmp/news_raw.json --output .tmp/news_filtered.json

# Step 3: AI evaluation
echo ""
echo "[3/4] Avaliando potencial de conteúdo com IA..."
python3 tools/evaluate_news.py --input .tmp/news_filtered.json --output .tmp/news_evaluated.json

# Step 4: Send email
echo ""
echo "[4/4] Enviando e-mail..."
python3 tools/send_email.py --input .tmp/news_evaluated.json

echo ""
echo "=== Concluído ==="
