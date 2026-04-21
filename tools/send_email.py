"""
Tool: send_email.py
Purpose: Send a daily news digest email with AI-evaluated articles.
Usage: python tools/send_email.py --input .tmp/news_evaluated.json
Requires: EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECIPIENT in .env
"""

import os
import json
import argparse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SCORE_COLORS = {5: "#16a34a", 4: "#65a30d", 3: "#ca8a04", 2: "#ea580c", 1: "#dc2626"}
FORMAT_ICONS = {
    "carrossel": "🎠",
    "thread": "🧵",
    "vídeo curto": "🎬",
    "artigo": "📝",
    "post opinião": "💬",
}


def score_stars(nota: int) -> str:
    return "★" * nota + "☆" * (5 - nota)


def format_icon(formato: str) -> str:
    for key, icon in FORMAT_ICONS.items():
        if key in (formato or "").lower():
            return icon
    return "📌"


def build_html(articles: list) -> str:
    date_str = datetime.now().strftime("%d/%m/%Y")

    # Only top 5 articles by score
    worth = sorted(articles, key=lambda x: x.get("ai_nota", 0), reverse=True)[:5]
    worth = [a for a in worth if a.get("ai_nota", 0) >= 4]
    not_worth = []

    def article_row(a: dict, show_ai: bool = True) -> str:
        pub = a.get("published_at", "")[:10]
        nota = a.get("ai_nota", 0)
        color = SCORE_COLORS.get(nota, "#888")
        stars = score_stars(nota)
        angulo = a.get("ai_angulo", "")
        formato = a.get("ai_formato", "")
        motivo = a.get("ai_motivo", "")
        fmt_icon = format_icon(formato)

        gancho = a.get("ai_gancho", "")
        ai_block = ""
        if show_ai and a.get("ai_nota", 0) >= 4:
            ai_block = f"""
            <div style="background:#f0fdf4; border-left:3px solid #16a34a; padding:10px 12px; margin-top:10px; border-radius:0 4px 4px 0;">
              <p style="margin:0 0 6px 0; font-size:11px; font-weight:bold; color:#16a34a; text-transform:uppercase;">🎬 Ideia de Reel</p>
              <p style="margin:0 0 4px 0; font-size:13px; color:#1a1a1a;"><strong>Gancho:</strong> "{gancho}"</p>
              <p style="margin:0; font-size:13px; color:#555;"><strong>Ângulo:</strong> {angulo}</p>
            </div>"""

        score_badge = ""
        if nota:
            score_badge = f'<span style="background:{color}; color:#fff; font-size:11px; padding:2px 8px; border-radius:12px; margin-left:8px;">{stars} {nota}/5</span>'

        return f"""
        <tr>
          <td style="padding:16px; border-bottom:1px solid #eee; vertical-align:top;">
            <p style="margin:0 0 4px 0; font-size:11px; color:#888;">{a.get('source','')} · {pub}{score_badge}</p>
            <a href="{a.get('url','')}" style="font-size:15px; font-weight:bold; color:#1a1a1a; text-decoration:none; line-height:1.4;">
              {a.get('title','')}
            </a>
            <p style="margin:8px 0 0 0; font-size:13px; color:#555; line-height:1.5;">
              {a.get('description','')[:220]}{'...' if len(a.get('description','')) > 220 else ''}
            </p>
            {ai_block}
            <p style="margin:10px 0 0 0;"><a href="{a.get('url','')}" style="font-size:12px; color:#0066cc;">Ler matéria →</a></p>
          </td>
        </tr>"""

    # Build worth section
    worth_rows = "".join(article_row(a, show_ai=True) for a in worth)
    if worth:
        worth_section = f"""
            <tr>
              <td style="padding:20px 32px 8px 32px;">
                <p style="margin:0; font-size:13px; font-weight:bold; color:#16a34a; text-transform:uppercase; letter-spacing:1px;">
                  Vale usar ({len(worth)})
                </p>
              </td>
            </tr>
            <tr><td>
              <table width="100%" cellpadding="0" cellspacing="0">
                {worth_rows}
              </table>
            </td></tr>"""
    else:
        worth_section = ""

    # Build not worth section (collapsed style)
    not_worth_rows = ""
    if not_worth:
        not_worth_rows = f"""
        <tr>
          <td style="padding:20px 32px 8px 32px;">
            <p style="margin:0; font-size:13px; font-weight:bold; color:#888; text-transform:uppercase; letter-spacing:1px;">
              Descartadas ({len(not_worth)})
            </p>
          </td>
        </tr>
        <tr><td>
          <table width="100%" cellpadding="0" cellspacing="0" style="opacity:0.6;">
            {"".join(article_row(a, show_ai=True) for a in not_worth)}
          </table>
        </td></tr>"""

    html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"></head>
    <body style="font-family: Arial, sans-serif; background:#f5f5f5; margin:0; padding:0;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f5f5; padding:20px 0;">
        <tr><td align="center">
          <table width="640" cellpadding="0" cellspacing="0" style="background:#fff; border-radius:8px; overflow:hidden;">

            <!-- Header -->
            <tr>
              <td style="background:#1a1a1a; padding:24px 32px;">
                <p style="margin:0; color:#888; font-size:12px; text-transform:uppercase; letter-spacing:1px;">Digest Diário · {date_str}</p>
                <h1 style="margin:8px 0 0 0; color:#fff; font-size:22px;">Marketing & Negócios</h1>
                <p style="margin:8px 0 0 0; color:#aaa; font-size:13px;">
                  <span style="color:#4ade80; font-weight:bold;">{len(worth)} matérias aprovadas</span> para criar conteúdo hoje
                  {f'· {len(not_worth)} descartadas' if not_worth else ''}
                </p>
              </td>
            </tr>

            <!-- Worth using -->
            {worth_section}

            <!-- Not worth -->
            {not_worth_rows}

            <!-- Footer -->
            <tr>
              <td style="padding:24px 32px; background:#f9f9f9; border-top:1px solid #eee;">
                <p style="margin:0; font-size:12px; color:#999; text-align:center;">
                  Fontes: Exame · Forbes BR · InfoMoney · Valor Econômico<br>
                  Curadoria com IA · Agente WAT
                </p>
              </td>
            </tr>

          </table>
        </td></tr>
      </table>
    </body>
    </html>
    """
    return html


def send_email(articles: list):
    sender = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_PASSWORD")
    recipient = os.getenv("EMAIL_RECIPIENT")
    subject = os.getenv("EMAIL_SUBJECT", "📰 Digest de Notícias - Marketing & Negócios")

    if not all([sender, password, recipient]):
        raise ValueError("EMAIL_SENDER, EMAIL_PASSWORD, and EMAIL_RECIPIENT must be set in .env")

    if not articles:
        print("No articles to send. Skipping email.")
        return

    worth_count = sum(1 for a in articles if a.get("ai_vale"))
    html_body = build_html(articles)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"📰 {worth_count} matérias para conteúdo · {datetime.now().strftime('%d/%m/%Y')}"
    msg["From"] = sender
    msg["To"] = recipient
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    print(f"Sending email to {recipient}...")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())

    print("Email sent successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send news digest email with AI evaluation")
    parser.add_argument("--input", default=".tmp/news_evaluated.json")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        articles = json.load(f)

    send_email(articles)
