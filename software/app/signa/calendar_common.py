"""Classificação de eventos de agenda -> estado da sala (puro, testável)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from .states import State


@dataclass(frozen=True)
class Busy:
    start: datetime
    end: datetime
    title: str = ""
    tentative: bool = False


def room_state(events: list[Busy], now: datetime, lead_minutes: float, tentative_is_busy: bool = True) -> State:
    lead = timedelta(minutes=lead_minutes)
    soon = False
    for e in events:
        if e.tentative and not tentative_is_busy:
            continue
        if e.start <= now < e.end:
            return State.SALA_OCUPADO
        if now < e.start <= now + lead:
            soon = True
    return State.SALA_PRESTES if soon else State.SALA_LIVRE


def parse_iso(s: str) -> datetime:
    """ISO 8601 do Google (com offset) ou do Graph (sem offset, em UTC com Prefer: outlook.timezone="UTC")."""
    s = s.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    if "." in s:  # Graph manda 7 casas de fração
        head, frac = s.split(".", 1)
        tz = ""
        for sep in "+-":
            if sep in frac:
                frac, tz = frac.split(sep, 1)
                tz = sep + tz
                break
        s = f"{head}.{frac[:6]}{tz}"
    d = datetime.fromisoformat(s)
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
