from datetime import datetime, timedelta, timezone

from signa import calendar_google as g
from signa import calendar_outlook as o
from signa.calendar_common import Busy, parse_iso, room_state
from signa.states import State

T = datetime(2026, 11, 23, 14, 0, tzinfo=timezone.utc)


def test_room_state_lead_and_busy():
    ev = [Busy(T + timedelta(minutes=5), T + timedelta(minutes=35))]
    assert room_state(ev, T, 5) == State.SALA_PRESTES
    assert room_state(ev, T - timedelta(seconds=1), 5) == State.SALA_LIVRE
    assert room_state(ev, T + timedelta(minutes=5), 5) == State.SALA_OCUPADO
    assert room_state(ev, T + timedelta(minutes=35), 5) == State.SALA_LIVRE
    assert room_state(ev, T - timedelta(minutes=4), 10) == State.SALA_PRESTES  # 9 min antes, aviso de 10
    assert room_state(ev, T - timedelta(minutes=4), 5) == State.SALA_LIVRE  # configurável


def test_tentative():
    ev = [Busy(T - timedelta(minutes=1), T + timedelta(minutes=30), tentative=True)]
    assert room_state(ev, T, 5, tentative_is_busy=True) == State.SALA_OCUPADO
    assert room_state(ev, T, 5, tentative_is_busy=False) == State.SALA_LIVRE


def test_google_classify():
    base = {"start": {"dateTime": "2026-11-23T11:00:00-03:00"}, "end": {"dateTime": "2026-11-23T11:30:00-03:00"}}
    b = g.classify(base)
    assert b.start == T and not b.tentative
    assert g.classify({**base, "transparency": "transparent"}) is None
    assert g.classify({**base, "status": "cancelled"}) is None
    assert g.classify({**base, "attendees": [{"self": True, "responseStatus": "declined"}]}) is None
    assert g.classify({**base, "attendees": [{"self": True, "responseStatus": "tentative"}]}).tentative
    assert g.classify({**base, "eventType": "workingLocation"}) is None
    assert g.classify({"start": {"date": "2026-11-23"}, "end": {"date": "2026-11-24"}}) is None


def test_outlook_classify():
    base = {"start": {"dateTime": "2026-11-23T14:00:00.0000000", "timeZone": "UTC"},
            "end": {"dateTime": "2026-11-23T14:30:00.0000000", "timeZone": "UTC"}, "showAs": "busy"}
    b = o.classify(base)
    assert b.start == T
    assert o.classify({**base, "showAs": "free"}) is None
    assert o.classify({**base, "isCancelled": True}) is None
    assert o.classify({**base, "responseStatus": {"response": "declined"}}) is None
    assert o.classify({**base, "showAs": "tentative"}).tentative
    assert o.classify({**base, "isAllDay": True}) is None


def test_parse_iso():
    assert parse_iso("2026-11-23T14:00:00Z") == T
    assert parse_iso("2026-11-23T14:00:00.1234567") == T.replace(microsecond=123456)
