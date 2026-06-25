"""
Tool: followup_reminder.py
Purpose: Send WhatsApp reminders for ClickUp tasks due today.

Two behaviors (runs every 15 min via cron):
  1. Morning digest (08:00-08:15): list ALL tasks due today
  2. Real-time alert: tasks due within the next 15 min (sent once per task)

Usage: python tools/followup_reminder.py
Requires: CLICKUP_API_KEY, CLICKUP_LIST_ID, BOTCONVERSA_API_KEY, MEU_WHATSAPP in .env
"""

import os
import sys
import json
import requests
from datetime import datetime, timezone, timedelta
from pathlib import Path
import pytz
from dotenv import load_dotenv

load_dotenv()

CLICKUP_API_KEY     = os.getenv("CLICKUP_API_KEY")
CLICKUP_LIST_ID     = os.getenv("CLICKUP_LIST_ID")
BOTCONVERSA_API_KEY = os.getenv("BOTCONVERSA_API_KEY")
MEU_WHATSAPP        = os.getenv("MEU_WHATSAPP")

TIMEZONE = pytz.timezone("America/Sao_Paulo")
SENT_LOG = Path(".tmp/followup_sent.json")
BOTCONVERSA_BASE = "https://new-backend.botconversa.com.br/api/v1/webhook"
_subscriber_id_cache = None


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def load_sent():
    if SENT_LOG.exists():
        return json.loads(SENT_LOG.read_text())
    return {}


def save_sent(data):
    SENT_LOG.parent.mkdir(exist_ok=True)
    SENT_LOG.write_text(json.dumps(data, indent=2))


def get_tasks():
    url = f"https://api.clickup.com/api/v2/list/{CLICKUP_LIST_ID}/task"
    headers = {"Authorization": CLICKUP_API_KEY}
    params = {"include_closed": "false", "subtasks": "true"}
    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    return resp.json().get("tasks", [])


def get_subscriber_id():
    global _subscriber_id_cache
    if _subscriber_id_cache:
        return _subscriber_id_cache
    headers = {"api-key": BOTCONVERSA_API_KEY, "Content-Type": "application/json"}
    resp = requests.post(f"{BOTCONVERSA_BASE}/subscriber/",
                         headers=headers,
                         json={"phone": MEU_WHATSAPP, "first_name": "Bruno", "last_name": "Dumont"})
    resp.raise_for_status()
    _subscriber_id_cache = resp.json()["id"]
    return _subscriber_id_cache


def send_whatsapp(message):
    sid = get_subscriber_id()
    headers = {"api-key": BOTCONVERSA_API_KEY, "Content-Type": "application/json"}
    resp = requests.post(f"{BOTCONVERSA_BASE}/subscriber/{sid}/send_message/",
                         headers=headers,
                         json={"type": "text", "value": message})
    resp.raise_for_status()


def due_today(task, today_date):
    """Returns due datetime if task is due today, else None."""
    due_ms = task.get("due_date")
    if not due_ms:
        return None
    due_dt = datetime.fromtimestamp(int(due_ms) / 1000, tz=timezone.utc).astimezone(TIMEZONE)
    if due_dt.date() == today_date:
        return due_dt
    return None


def due_in_window(due_dt, now):
    """Returns True if task is due between -5 and +15 minutes from now."""
    diff = (due_dt - now).total_seconds() / 60
    return -5 <= diff <= 15


def morning_digest(tasks, today):
    due_tasks = []
    for task in tasks:
        due_dt = due_today(task, today)
        if due_dt:
            url = f"https://app.clickup.com/t/{task['id']}"
            due_tasks.append((task["name"], due_dt, url))

    if not due_tasks:
        log("Nenhuma tarefa vencendo hoje — sem digest.")
        return

    due_tasks.sort(key=lambda x: x[1])


    lines = ["Bruno, hoje tem follow-up! 🚀\n"]
    for name, due_dt, url in due_tasks:
        time_str = due_dt.strftime("%H:%M") if due_dt.hour != 0 else "sem hora"
        lines.append(f"* Nome: {name} - Task no Clickup: {url} - Horário Programado: {time_str}")
    lines.append("\nBORA VENDER PORRA!!!! 🚀")

    message = "\n".join(lines)
    log(f"Enviando digest com {len(due_tasks)} tarefa(s)...")
    send_whatsapp(message)
    log("✓ Digest enviado.")


def realtime_alerts(tasks, now, today, sent):
    updated = False
    for task in tasks:
        due_dt = due_today(task, today)
        if not due_dt:
            continue
        if not due_in_window(due_dt, now):
            continue

        key = f"realtime_{task['id']}_{int(task['due_date'])}"
        if key in sent:
            continue

        name = task["name"]
        url = f"https://app.clickup.com/t/{task['id']}"
        time_str = due_dt.strftime("%H:%M")
        message = f"Bruno, hoje tem follow-up! 🚀\n\n• {name} - {url} - {time_str}\n\nBORA VENDER PORRA!!!! 🚀"

        log(f"Alerta em tempo real: '{name}' vence às {time_str}")
        try:
            send_whatsapp(message)
            log("✓ Alerta enviado.")
        except Exception as e:
            log(f"ERRO: {e}")
            continue

        sent[key] = {"task": name, "due": time_str, "sent_at": now.isoformat()}
        updated = True

    if updated:
        save_sent(sent)


def main():
    if not all([CLICKUP_API_KEY, CLICKUP_LIST_ID, BOTCONVERSA_API_KEY, MEU_WHATSAPP]):
        log("ERRO: verifique CLICKUP_API_KEY, CLICKUP_LIST_ID, BOTCONVERSA_API_KEY e MEU_WHATSAPP no .env")
        sys.exit(1)

    now   = datetime.now(TIMEZONE)
    today = now.date()

    log(f"Rodando às {now.strftime('%H:%M')} de {today}")

    tasks = get_tasks()
    log(f"{len(tasks)} tarefas encontradas.")

    sent = load_sent()

    # 1. Morning digest: roda uma vez entre 08:00 e 08:15
    digest_key = f"digest_{today}"
    if now.hour == 8 and now.minute < 15:
        if digest_key not in sent:
            morning_digest(tasks, today)
            sent[digest_key] = now.isoformat()
            save_sent(sent)
        else:
            log("Digest de hoje já enviado.")

    # 2. Real-time alerts: tarefas vencendo nos próximos 15 min
    realtime_alerts(tasks, now, today, sent)

    log("Concluído.")


if __name__ == "__main__":
    main()
