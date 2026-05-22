"""
Tool: get_calendar_slots.py
Purpose: Busca os próximos slots livres no Google Calendar de Bruno para agendamento de diagnósticos.
Usage: python tools/get_calendar_slots.py --next-business-day --morning 1 --afternoon 1
Output: JSON com slots disponíveis (data, hora, link Meet)
"""

import os
import json
import argparse
from datetime import datetime, timedelta, time
import pytz

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
TIMEZONE = "America/Sao_Paulo"
CALENDAR_ID = "primary"

# Slots a verificar: manhã 9h-12h, tarde 14h-17h
MORNING_SLOTS = ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30"]
AFTERNOON_SLOTS = ["14:00", "14:30", "15:00", "15:30", "16:00", "16:30"]
MEETING_DURATION_MIN = 45
BUFFER_MIN = 20  # tempo mínimo antes/após cada reunião


def get_credentials():
    creds = None
    token_path = os.path.join(os.path.dirname(__file__), "..", "token.json")
    credentials_path = os.path.join(os.path.dirname(__file__), "..", "credentials.json")

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(
                    "credentials.json não encontrado. "
                    "Siga as instruções em workflows/setup-google-calendar.md"
                )
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, "w") as f:
            f.write(creds.to_json())

    return creds


def next_business_day(from_date=None):
    tz = pytz.timezone(TIMEZONE)
    d = from_date or datetime.now(tz).date()
    d += timedelta(days=1)
    # pula fim de semana
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d


def get_busy_times(service, date):
    tz = pytz.timezone(TIMEZONE)
    start = tz.localize(datetime.combine(date, time(0, 0)))
    end = tz.localize(datetime.combine(date, time(23, 59)))

    body = {
        "timeMin": start.isoformat(),
        "timeMax": end.isoformat(),
        "timeZone": TIMEZONE,
        "items": [{"id": CALENDAR_ID}],
    }
    result = service.freebusy().query(body=body).execute()
    busy = result["calendars"][CALENDAR_ID]["busy"]
    return busy


def is_slot_free(busy_times, slot_start, duration_min, buffer_min):
    tz = pytz.timezone(TIMEZONE)
    slot_end = slot_start + timedelta(minutes=duration_min)
    # adiciona buffer antes e depois
    window_start = slot_start - timedelta(minutes=buffer_min)
    window_end = slot_end + timedelta(minutes=buffer_min)

    for busy in busy_times:
        busy_start = datetime.fromisoformat(busy["start"]).astimezone(tz)
        busy_end = datetime.fromisoformat(busy["end"]).astimezone(tz)
        # verifica sobreposição com a janela (slot + buffer)
        if busy_start < window_end and busy_end > window_start:
            return False
    return True


def find_slots(date, busy_times, n_morning=1, n_afternoon=1):
    tz = pytz.timezone(TIMEZONE)
    found_morning = []
    found_afternoon = []

    for slot_str in MORNING_SLOTS:
        if len(found_morning) >= n_morning:
            break
        h, m = map(int, slot_str.split(":"))
        slot_start = tz.localize(datetime.combine(date, time(h, m)))
        if is_slot_free(busy_times, slot_start, MEETING_DURATION_MIN, BUFFER_MIN):
            found_morning.append(slot_start)

    for slot_str in AFTERNOON_SLOTS:
        if len(found_afternoon) >= n_afternoon:
            break
        h, m = map(int, slot_str.split(":"))
        slot_start = tz.localize(datetime.combine(date, time(h, m)))
        if is_slot_free(busy_times, slot_start, MEETING_DURATION_MIN, BUFFER_MIN):
            found_afternoon.append(slot_start)

    return found_morning + found_afternoon


def format_slots(slots):
    days_pt = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    result = []
    for slot in slots:
        result.append({
            "dia_semana": days_pt[slot.weekday()],
            "data": slot.strftime("%d/%m"),
            "hora": slot.strftime("%H:%M"),
            "datetime_iso": slot.isoformat(),
            "label": f"{days_pt[slot.weekday()]} ({slot.strftime('%d/%m')}) às {slot.strftime('%H:%M')}",
        })
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Busca slots livres no Google Calendar")
    parser.add_argument("--morning", type=int, default=1, help="Qtd de slots de manhã")
    parser.add_argument("--afternoon", type=int, default=1, help="Qtd de slots de tarde")
    parser.add_argument("--date", default=None, help="Data específica (YYYY-MM-DD). Padrão: próximo dia útil")
    args = parser.parse_args()

    try:
        creds = get_credentials()
        service = build("calendar", "v3", credentials=creds)

        target_date = (
            datetime.strptime(args.date, "%Y-%m-%d").date()
            if args.date
            else next_business_day()
        )

        busy = get_busy_times(service, target_date)
        slots = find_slots(target_date, busy, args.morning, args.afternoon)
        formatted = format_slots(slots)

        print(json.dumps({"date": str(target_date), "slots": formatted}, ensure_ascii=False, indent=2))

    except FileNotFoundError as e:
        print(json.dumps({"error": str(e)}))
    except Exception as e:
        print(json.dumps({"error": f"Erro inesperado: {str(e)}"}))
