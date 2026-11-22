"""Outlook / Microsoft 365 via Microsoft Graph — GET /me/calendarView (escopo Calendars.Read).
Login por fluxo de dispositivo do MSAL (cliente público; não precisa de segredo do app).
Docs: https://learn.microsoft.com/graph/api/user-list-calendarview
      https://learn.microsoft.com/entra/msal/python/
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from . import secrets_store
from .calendar_common import Busy, parse_iso

SCOPES = ["Calendars.Read"]
KEY = "outlook-msal-cache"
GRAPH = "https://graph.microsoft.com/v1.0"


def _app(client_id: str, tenant: str):
    import msal
    cache = msal.SerializableTokenCache()
    raw = secrets_store.get(KEY)
    if raw:
        cache.deserialize(raw)
    app = msal.PublicClientApplication(client_id, authority=f"https://login.microsoftonline.com/{tenant}",
                                       token_cache=cache)
    return app, cache


def _save(cache) -> None:
    if cache.has_state_changed:
        secrets_store.put(KEY, cache.serialize())


def login(client_id: str, tenant: str = "common", echo=print) -> None:
    app, cache = _app(client_id, tenant)
    flow = app.initiate_device_flow(scopes=SCOPES)
    if "user_code" not in flow:
        raise RuntimeError(f"Outlook: falha ao iniciar o login: {flow.get('error_description')}")
    echo(flow["message"])  # "Para entrar, abra https://microsoft.com/devicelogin e digite o código ..."
    res = app.acquire_token_by_device_flow(flow)
    if "access_token" not in res:
        raise RuntimeError(f"Outlook: login falhou: {res.get('error_description')}")
    _save(cache)


def _token(client_id: str, tenant: str) -> str:
    app, cache = _app(client_id, tenant)
    accts = app.get_accounts()
    res = app.acquire_token_silent(SCOPES, account=accts[0]) if accts else None
    _save(cache)
    if not res or "access_token" not in res:
        raise RuntimeError("Outlook: faça `signa-cli login outlook` primeiro")
    return res["access_token"]


def classify(ev: dict, ignore_all_day: bool = True) -> Busy | None:
    if ev.get("isCancelled"):
        return None
    if ev.get("showAs") in ("free", "workingElsewhere", "unknown"):
        return None
    if (ev.get("responseStatus") or {}).get("response") == "declined":
        return None
    if ev.get("isAllDay") and ignore_all_day:
        return None
    s, e = parse_iso(ev["start"]["dateTime"]), parse_iso(ev["end"]["dateTime"])
    tentative = ev.get("showAs") == "tentative" or (ev.get("responseStatus") or {}).get("response") == "tentativelyAccepted"
    return Busy(s, e, ev.get("subject", ""), tentative)


def fetch(client_id: str, tenant: str = "common", ignore_all_day: bool = True, horizon_h: float = 12) -> list[Busy]:
    import requests
    now = datetime.now(timezone.utc)
    params = {"startDateTime": (now - timedelta(hours=12)).strftime("%Y-%m-%dT%H:%M:%SZ"),
              "endDateTime": (now + timedelta(hours=horizon_h)).strftime("%Y-%m-%dT%H:%M:%SZ"),
              "$select": "subject,start,end,showAs,isAllDay,isCancelled,responseStatus",
              "$orderby": "start/dateTime", "$top": "100"}
    headers = {"Authorization": f"Bearer {_token(client_id, tenant)}", "Prefer": 'outlook.timezone="UTC"'}
    out: list[Busy] = []
    url = f"{GRAPH}/me/calendarView"
    while url:
        r = requests.get(url, params=params, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()
        for ev in data.get("value", []):
            b = classify(ev, ignore_all_day)
            if b:
                out.append(b)
        url, params = data.get("@odata.nextLink"), None
    return out
