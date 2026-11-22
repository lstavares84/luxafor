"""Google Calendar API v3 — events.list (OAuth "installed app", escopo só leitura de eventos).
Docs: https://developers.google.com/workspace/calendar/api/v3/reference/events/list
      https://developers.google.com/identity/protocols/oauth2/native-app
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from . import secrets_store
from .calendar_common import Busy, parse_iso

SCOPES = ["https://www.googleapis.com/auth/calendar.events.readonly"]
KEY = "google-token"


def login(client_secrets_file: str) -> None:
    from google_auth_oauthlib.flow import InstalledAppFlow
    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
    creds = flow.run_local_server(port=0, open_browser=True)  # loopback 127.0.0.1 + PKCE
    secrets_store.put(KEY, creds.to_json())


def _creds():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    raw = secrets_store.get(KEY)
    if not raw:
        raise RuntimeError("Google: faça `signa-cli login google` primeiro")
    creds = Credentials.from_authorized_user_info(json.loads(raw), SCOPES)
    if not creds.valid and creds.refresh_token:
        creds.refresh(Request())
        secrets_store.put(KEY, creds.to_json())
    return creds


def classify(item: dict, ignore_all_day: bool = True) -> Busy | None:
    """Converte um evento do Google em intervalo ocupado, ou None se não conta."""
    if item.get("status") == "cancelled":
        return None
    if item.get("transparency") == "transparent":          # marcado como "Livre"
        return None
    if item.get("eventType") in ("workingLocation", "birthday"):  # focusTime e outOfOffice contam como ocupado
        return None
    me = next((a for a in item.get("attendees", []) if a.get("self")), None)
    if me and me.get("responseStatus") == "declined":
        return None
    st, en = item.get("start", {}), item.get("end", {})
    if "dateTime" not in st:                                 # dia inteiro
        if ignore_all_day:
            return None
        s = datetime.fromisoformat(st["date"]).replace(tzinfo=timezone.utc)
        e = datetime.fromisoformat(en["date"]).replace(tzinfo=timezone.utc)
    else:
        s, e = parse_iso(st["dateTime"]), parse_iso(en["dateTime"])
    tentative = bool(me and me.get("responseStatus") == "tentative")
    return Busy(s, e, item.get("summary", ""), tentative)


def fetch(calendars: list[str], ignore_all_day: bool = True, horizon_h: float = 12) -> list[Busy]:
    from googleapiclient.discovery import build
    svc = build("calendar", "v3", credentials=_creds(), cache_discovery=False)
    now = datetime.now(timezone.utc)
    out: list[Busy] = []
    for cal in calendars:
        res = svc.events().list(calendarId=cal, timeMin=(now - timedelta(hours=12)).isoformat(),
                                timeMax=(now + timedelta(hours=horizon_h)).isoformat(), singleEvents=True,
                                orderBy="startTime", maxResults=100).execute()
        for it in res.get("items", []):
            b = classify(it, ignore_all_day)
            if b:
                out.append(b)
    return out
