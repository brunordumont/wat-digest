"""
Tool: send_alert.py
Purpose: Send an error alert email when the digest pipeline fails.
Usage: python tools/send_alert.py --step "nome_do_passo" --log /tmp/digest.log
"""

import os
import argparse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def send_alert(step: str, log_tail: str):
    sender = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_PASSWORD")
    recipient = os.getenv("EMAIL_RECIPIENT")

    if not all([sender, password, recipient]):
        print("Credenciais de e-mail não configuradas — alerta não enviado.")
        return

    date_str = datetime.now().strftime("%d/%m/%Y %H:%M")

    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="font-family: Arial, sans-serif; background:#f5f5f5; margin:0; padding:20px;">
  <table width="600" cellpadding="0" cellspacing="0" style="background:#fff; border-radius:8px; overflow:hidden; margin:0 auto;">
    <tr>
      <td style="background:#dc2626; padding:24px 32px;">
        <p style="margin:0; color:#fca5a5; font-size:12px; text-transform:uppercase; letter-spacing:1px;">Alerta do Pipeline · {date_str}</p>
        <h1 style="margin:8px 0 0 0; color:#fff; font-size:20px;">Digest nao rodou hoje</h1>
      </td>
    </tr>
    <tr>
      <td style="padding:24px 32px;">
        <p style="margin:0 0 8px 0; font-size:14px; color:#1a1a1a;">O pipeline falhou no passo: <strong>{step}</strong></p>
        <p style="margin:0 0 16px 0; font-size:13px; color:#555;">Voce nao vai receber o digest de hoje. Verifique o erro abaixo e corrija antes de amanha.</p>
        <div style="background:#f9f9f9; border:1px solid #eee; border-radius:4px; padding:16px;">
          <p style="margin:0 0 8px 0; font-size:11px; font-weight:bold; color:#888; text-transform:uppercase;">Ultimas linhas do log</p>
          <pre style="margin:0; font-size:12px; color:#1a1a1a; white-space:pre-wrap; word-break:break-all;">{log_tail}</pre>
        </div>
        <p style="margin:16px 0 0 0; font-size:12px; color:#888;">Log completo em: /tmp/digest.log</p>
      </td>
    </tr>
  </table>
</body>
</html>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Pipeline falhou — {step} · {date_str}"
    msg["From"] = sender
    msg["To"] = recipient
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())

    print(f"Alerta enviado para {recipient}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--step", required=True)
    parser.add_argument("--log", default="/tmp/digest.log")
    args = parser.parse_args()

    log_tail = ""
    try:
        with open(args.log, "r") as f:
            lines = f.readlines()
            log_tail = "".join(lines[-30:])
    except Exception:
        log_tail = "(log nao disponivel)"

    send_alert(args.step, log_tail)
