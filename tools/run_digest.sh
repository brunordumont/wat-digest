#!/bin/bash
# run_digest.sh — Executa o pipeline completo do digest diário

PROJECT_DIR="/Users/bruno/TESTE CLAUDE CODE"
cd "$PROJECT_DIR"

LOG_FILE="/tmp/digest.log"
exec >> "$LOG_FILE" 2>&1

echo ""
echo "=== Digest Diário de Notícias ==="
echo "$(date '+%Y-%m-%d %H:%M:%S')"
echo ""

fail() {
    echo "ERRO em $1 — abortando pipeline."
    python3 tools/send_alert.py --step "$1" --log "$LOG_FILE"
    exit 1
}

echo "[1/5] Buscando notícias..."
python3 tools/fetch_news.py --days 3 --output .tmp/news_raw.json || fail "fetch_news"

echo ""
echo "[2/5] Filtrando artigos..."
python3 tools/filter_news.py --input .tmp/news_raw.json --output .tmp/news_filtered.json || fail "filter_news"

echo ""
echo "[3/5] Avaliando potencial de conteúdo com IA..."
python3 tools/evaluate_news.py --input .tmp/news_filtered.json --output .tmp/news_evaluated.json || fail "evaluate_news"

echo ""
echo "[4/5] Gerando curadoria editorial..."
python3 tools/editorial.py --news .tmp/news_evaluated.json --output .tmp/editorial.json || fail "editorial"

echo ""
echo "[5/5] Enviando e-mail..."
python3 tools/send_email.py --input .tmp/news_evaluated.json --editorial .tmp/editorial.json || fail "send_email"

echo ""
echo "=== Concluído ==="
