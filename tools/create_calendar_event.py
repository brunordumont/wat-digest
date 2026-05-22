"""
Tool: create_calendar_event.py
Purpose: Cria evento de diagnóstico no Google Calendar de Bruno com link Meet automático.
Usage: python tools/create_calendar_event.py --datetime "2026-05-27T10:00:00" --lead-name "Ana Lima" --property-name "Pousada do Sol" --lead-email "ana@pousadadosol.com.br"
Output: JSON com link do evento e link do Google Meet
"""

import os
import json
import argparse
from datetime import datetime, timedelta
import pytz

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]
TIMEZONE = "America/Sao_Paulo"
CALENDAR_ID = "primary"
BRUNO_EMAIL = "brunordumont@gmail.com"
MEETING_DURATION_MIN = 45


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


def create_event(service, lead_name, property_name, lead_email, start_dt):
    tz = pytz.timezone(TIMEZONE)

    if start_dt.tzinfo is None:
        start_dt = tz.localize(start_dt)

    end_dt = start_dt + timedelta(minutes=MEETING_DURATION_MIN)

    title = f"Reunião de Diagnóstico {lead_name} & Bruno - {property_name}"

    attendees = [{"email": BRUNO_EMAIL}]
    if lead_email:
        attendees.append({"email": lead_email})

    event_body = {
        "summary": title,
        "start": {
            "dateTime": start_dt.isoformat(),
            "timeZone": TIMEZONE,
        },
        "end": {
            "dateTime": end_dt.isoformat(),
            "timeZone": TIMEZONE,
        },
        "attendees": attendees,
        "conferenceData": {
            "createRequest": {
                "requestId": f"axis-{lead_name.lower().replace(' ', '-')}-{start_dt.strftime('%Y%m%d%H%M')}",
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
            }
        },
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "popup", "minutes": 30},
                {"method": "email", "minutes": 1440},  # 24h antes
            ],
        },
    }

    created = service.events().insert(
        calendarId=CALENDAR_ID,
        body=event_body,
        conferenceDataVersion=1,
        sendUpdates="all",
    ).execute()

    meet_link = created.get("conferenceData", {}).get("entryPoints", [{}])[0].get("uri", "")

    return {
        "event_id": created["id"],
        "title": title,
        "start": start_dt.isoformat(),
        "end": end_dt.isoformat(),
        "meet_link": meet_link,
        "event_link": created.get("htmlLink", ""),
        "attendees": [a["email"] for a in attendees],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cria evento de diagnóstico no Google Calendar")
    parser.add_argument("--datetime", required=True, help="Data e hora do evento (YYYY-MM-DDTHH:MM:SS)")
    parser.add_argument("--lead-name", required=True, help="Nome do lead")
    parser.add_argument("--property-name", required=True, help="Nome da propriedade")
    parser.add_argument("--lead-email", default="", help="E-mail do lead (opcional)")
    args = parser.parse_args()

    try:
        creds = get_credentials()
        service = build("calendar", "v3", credentials=creds)

        start_dt = datetime.strptime(args.datetime, "%Y-%m-%dT%H:%M:%S")
        result = create_event(service, args.lead_name, args.property_name, args.lead_email, start_dt)

        print(json.dumps(result, ensure_ascii=False, indent=2))

    except FileNotFoundError as e:
        print(json.dumps({"error": str(e)}))
    except Exception as e:
        print(json.dumps({"error": f"Erro inesperado: {str(e)}"}))
