"""
Tool: send_email.py
Purpose: Send a daily news digest email with AI-evaluated articles and editorial.
Usage: python tools/send_email.py --input .tmp/news_evaluated.json --editorial .tmp/editorial.json
Requires: EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECIPIENT in .env
"""

import os
import json
import re
import argparse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SCORE_COLORS = {5: "#16a34a", 4: "#65a30d", 3: "#ca8a04", 2: "#ea580c", 1: "#dc2626"}


def score_stars(nota: int) -> str:
    return "★" * nota + "☆" * (5 - nota)


def build_editorial_section(editorial: dict) -> str:
    if not editorial:
        return ""

    nota_editorial = editorial.get("nota_editorial", "")
    top_picks = editorial.get("top_picks", [])

    picks_html = ""
    for i, pick in enumerate(top_picks, 1):
        picks_html += f"""
        <div style="margin-bottom:16px; padding-bottom:16px; border-bottom:1px solid #eee;">
          <p style="margin:0 0 6px 0; font-size:12px; font-weight:bold; color:#1a1a1a;">#{i} {pick.get('titulo', '')}</p>
          <p style="margin:0 0 4px 0; font-size:12px; color:#555;"><strong>Pergunta:</strong> {pick.get('pergunta_obvia', '')}</p>
          <p style="margin:0 0 4px 0; font-size:12px; color:#16a34a;"><strong>A virada:</strong> {pick.get('a_virada', '')}</p>
          <p style="margin:0 0 4px 0; font-size:12px; color:#1a1a1a;"><strong>O que o empresário vai sentir:</strong> {pick.get('conexao_humana', '')}</p>
          <p style="margin:0; font-size:11px; color:#888; font-style:italic;">Formato: {pick.get('formato_sugerido', '')}</p>
        </div>"""

    return f"""
    <tr>
      <td style="background:#1a1a1a; padding:24px 32px 12px 32px;">
        <p style="margin:0; font-size:13px; font-weight:bold; color:#fff; text-transform:uppercase; letter-spacing:1px;">
          Curadoria do Dia
        </p>
        <p style="margin:8px 0 0 0; font-size:13px; color:#aaa; line-height:1.6;">{nota_editorial}</p>
      </td>
    </tr>
    <tr>
      <td style="background:#fafafa; padding:20px 32px;">
        <p style="margin:0 0 16px 0; font-size:12px; font-weight:bold; color:#333; text-transform:uppercase; letter-spacing:1px;">Melhores Pautas</p>
        {picks_html}
      </td>
    </tr>"""


def build_html(articles: list, editorial: dict = None) -> str:
    date_str = datetime.now().strftime("%d/%m/%Y")

    all_worth = sorted(articles, key=lambda x: x.get("ai_nota", 0), reverse=True)
    nota5 = [a for a in all_worth if a.get("ai_nota", 0) == 5]
    nota4 = [a for a in all_worth if a.get("ai_nota", 0) == 4]
    top10 = nota5 if nota5 else nota4
    total_worth = len(nota5) + len(nota4)
    rest = []

    def article_row(a: dict) -> str:
        pub = a.get("published_at", "")[:10]
        nota = a.get("ai_nota", 0)
        color = SCORE_COLORS.get(nota, "#888")
        stars = score_stars(nota)
        abordagem = a.get("ai_abordagem", "")

        ai_block = ""
        if nota >= 4 and abordagem:
            import re as _re
            def _fmt(label, key):
                m = _re.search(rf'{key}:\s*(.+?)(?=\s+(?:POSIÇÃO|GANCHO|VIRADA|TIPO):|$)', abordagem, _re.IGNORECASE | _re.DOTALL)
                val = m.group(1).strip().rstrip('.') if m else ""
                if not val:
                    return ""
                colors = {"TIPO": "#6366f1", "POSIÇÃO": "#dc2626", "GANCHO": "#0066cc", "VIRADA": "#16a34a"}
                c = colors.get(key, "#555")
                return f'<p style="margin:0 0 8px 0; font-size:13px; color:#1a1a1a;"><span style="font-size:10px; font-weight:bold; color:{c}; text-transform:uppercase; letter-spacing:0.5px;">{label} · </span>{val}</p>'

            rows = _fmt("Tipo", "TIPO") + _fmt("Posição", "POSIÇÃO") + _fmt("Gancho", "GANCHO") + _fmt("Virada", "VIRADA")
            if not rows:
                rows = f'<p style="margin:0; font-size:13px; color:#1a1a1a;">{abordagem}</p>'

            ai_block = f"""
            <div style="background:#f0fdf4; border-left:3px solid #16a34a; padding:10px 14px; margin-top:10px; border-radius:0 4px 4px 0;">
              <p style="margin:0 0 8px 0; font-size:10px; font-weight:bold; color:#16a34a; text-transform:uppercase; letter-spacing:1px;">Como explorar</p>
              {rows}
            </div>"""

        score_badge = f'<span style="background:{color}; color:#fff; font-size:11px; padding:2px 8px; border-radius:12px; margin-left:8px;">{stars} {nota}/5</span>' if nota else ""

        desc = re.sub(r'<[^>]+>', '', a.get('description', '') or '').strip()
        desc_short = desc[:220] + ('...' if len(desc) > 220 else '')

        return f"""
        <tr>
          <td style="padding:16px; border-bottom:1px solid #eee; vertical-align:top;">
            <p style="margin:0 0 4px 0; font-size:11px; color:#888;">{a.get('source','')} · {pub}{score_badge}</p>
            <a href="{a.get('url','')}" style="font-size:15px; font-weight:bold; color:#1a1a1a; text-decoration:none; line-height:1.4;">
              {a.get('title','')}
            </a>
            <p style="margin:8px 0 0 0; font-size:13px; color:#555; line-height:1.5;">{desc_short}</p>
            {ai_block}
            <p style="margin:10px 0 0 0;"><a href="{a.get('url','')}" style="font-size:12px; color:#0066cc;">Ler materia</a></p>
          </td>
        </tr>"""

    def rest_row(a: dict) -> str:
        nota = a.get("ai_nota", 0)
        color = SCORE_COLORS.get(nota, "#888")
        pub = a.get("published_at", "")[:10]
        return f"""
        <tr>
          <td style="padding:10px 16px; border-bottom:1px solid #f0f0f0; vertical-align:top;">
            <p style="margin:0 0 2px 0; font-size:11px; color:#888;">{a.get('source','')} · {pub} <span style="background:{color}; color:#fff; font-size:10px; padding:1px 6px; border-radius:8px; margin-left:4px;">{nota}/5</span></p>
            <a href="{a.get('url','')}" style="font-size:13px; font-weight:bold; color:#1a1a1a; text-decoration:none; line-height:1.4;">{a.get('title','')}</a>
            <p style="margin:4px 0 0 0; font-size:12px; color:#555;">{a.get('ai_abordagem', '')}</p>
          </td>
        </tr>"""

    if top10:
        top_rows = "".join(article_row(a) for a in top10)
        worth_section = f"""
        <tr>
          <td style="padding:20px 32px 8px 32px;">
            <p style="margin:0; font-size:13px; font-weight:bold; color:#16a34a; text-transform:uppercase; letter-spacing:1px;">
              {"Pautas Nota 5" if nota5 else "Pautas Nota 4"} — {len(top10)} hoje
            </p>
          </td>
        </tr>
        <tr><td>
          <table width="100%" cellpadding="0" cellspacing="0">{top_rows}</table>
        </td></tr>"""
    else:
        worth_section = """
        <tr>
          <td style="padding:32px; text-align:center;">
            <p style="margin:0 0 8px 0; font-size:15px; font-weight:bold; color:#1a1a1a;">Nenhuma pauta aprovada hoje</p>
            <p style="margin:0; font-size:13px; color:#888; line-height:1.6;">
              O pipeline rodou normalmente. Amanha pode ser diferente.
            </p>
          </td>
        </tr>"""

    rest_section = ""
    if rest:
        rest_rows = "".join(rest_row(a) for a in rest)
        rest_section = f"""
        <tr>
          <td style="padding:20px 32px 8px 32px; border-top:2px solid #eee;">
            <p style="margin:0; font-size:12px; font-weight:bold; color:#888; text-transform:uppercase; letter-spacing:1px;">
              Outras {len(rest)} pautas aprovadas
            </p>
          </td>
        </tr>
        <tr><td>
          <table width="100%" cellpadding="0" cellspacing="0">{rest_rows}</table>
        </td></tr>"""

    editorial_section = build_editorial_section(editorial or {})

    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="font-family: Arial, sans-serif; background:#f5f5f5; margin:0; padding:0;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f5f5; padding:20px 0;">
    <tr><td align="center">
      <table width="640" cellpadding="0" cellspacing="0" style="background:#fff; border-radius:8px; overflow:hidden;">

        <tr>
          <td style="background:#1a1a1a; padding:24px 32px;">
            <p style="margin:0; color:#888; font-size:12px; text-transform:uppercase; letter-spacing:1px;">Digest Diario · {date_str}</p>
            <h1 style="margin:8px 0 0 0; color:#fff; font-size:22px;">Marketing & Negocios</h1>
            <p style="margin:8px 0 0 0; color:#aaa; font-size:13px;">
              <span style="color:#4ade80; font-weight:bold;">{total_worth} pautas aprovadas</span> para criar conteudo hoje
            </p>
          </td>
        </tr>

        {worth_section}
        {rest_section}
        {editorial_section}

        <tr>
          <td style="padding:24px 32px; background:#f9f9f9; border-top:1px solid #eee;">
            <p style="margin:0; font-size:12px; color:#999; text-align:center;">
              Curadoria com IA · Agente WAT
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""
    return html


def send_email(articles: list, editorial: dict = None):
    sender = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_PASSWORD")
    recipient = os.getenv("EMAIL_RECIPIENT")

    if not all([sender, password, recipient]):
        raise ValueError("EMAIL_SENDER, EMAIL_PASSWORD, and EMAIL_RECIPIENT must be set in .env")

    worth_count = sum(1 for a in articles if a.get("ai_vale")) if articles else 0
    html_body = build_html(articles, editorial)

    msg = MIMEMultipart("alternative")
    date_str = datetime.now().strftime('%d/%m/%Y')
    subject = f"📰 Bruno, aqui estão as {worth_count} pautas para conteúdo · {date_str}" if worth_count > 0 else f"📰 Bruno, nenhuma pauta aprovada hoje · {date_str}"
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    print(f"Sending email to {recipient}...")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())

    print("Email sent successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send news digest email")
    parser.add_argument("--input", default=".tmp/news_evaluated.json")
    parser.add_argument("--editorial", default=".tmp/editorial.json")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        articles = json.load(f)

    editorial = {}
    if os.path.exists(args.editorial):
        with open(args.editorial, "r", encoding="utf-8") as f:
            editorial = json.load(f)

    send_email(articles, editorial)
