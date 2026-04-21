"""
Tool: export_to_sheets.py
Purpose: Export filtered news articles to a Google Sheet for easy review.
Usage: python tools/export_to_sheets.py --input .tmp/news_filtered.json --sheet-id YOUR_SHEET_ID
Requires: credentials.json (Google OAuth) in project root
Output: Appends rows to the specified Google Sheet
"""

import os
import json
import argparse
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def get_sheets_service():
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
    except ImportError:
        print("ERROR: Google libraries not installed.")
        print("Run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        raise

    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = None
    token_path = "token.json"
    creds_path = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return build("sheets", "v4", credentials=creds)


def export_to_sheet(articles: list, sheet_id: str, tab_name: str = "Notícias"):
    service = get_sheets_service()
    sheet = service.spreadsheets()

    run_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    header = ["Data da Busca", "Título", "Descrição", "Fonte", "Publicado em", "URL"]
    rows = [header]

    for a in articles:
        rows.append([
            run_date,
            a.get("title", ""),
            a.get("description", ""),
            a.get("source", ""),
            a.get("published_at", ""),
            a.get("url", ""),
        ])

    body = {"values": rows}
    result = sheet.values().append(
        spreadsheetId=sheet_id,
        range=f"{tab_name}!A1",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body=body,
    ).execute()

    print(f"Exported {len(articles)} articles to Google Sheet: {sheet_id}")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export news to Google Sheets")
    parser.add_argument("--input", default=".tmp/news_filtered.json")
    parser.add_argument("--sheet-id", required=True, help="Google Sheet ID from the URL")
    parser.add_argument("--tab", default="Notícias")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        articles = json.load(f)

    export_to_sheet(articles, args.sheet_id, args.tab)
