"""Daemon: lê agenda e estado das IAs, roda o motor de prioridade e mantém a luz em dia."""
from __future__ import annotations

import logging
import threading
import time
from datetime import datetime, timezone

from . import config as cfgmod
from . import store
from .calendar_common import Busy, room_state
from .device import open_output
from .engine import decide
from .states import State, look

log = logging.getLogger("signa")


class CalendarPoller:
    def __init__(self, cfg: cfgmod.Config):
        self.cfg = cfg
        self.events: list[Busy] = []
        self.errors: dict[str, str] = {}
        self.by_src: dict[str, list[Busy]] = {}
        self._stop = threading.Event()

    def poll_once(self) -> None:
        c = self.cfg
        allday = c.get("sala", "ignore_all_day", True)
        fetchers = {}
        if c.get("google", "enabled"):
            def g():
                from . import calendar_google
                return calendar_google.fetch(c.get("google", "calendars", ["primary"]), allday)
            fetchers["google"] = g
        if c.get("outlook", "enabled"):
            def o():
                from . import calendar_outlook
                return calendar_outlook.fetch(c.get("outlook", "client_id"), c.get("outlook", "tenant", "common"), allday)
            fetchers["outlook"] = o
        for name, fn in fetchers.items():
            try:
                self.by_src[name] = fn()
                self.errors.pop(name, None)
            except Exception as e:  # rede, token expirado etc.: mantém a última leitura boa
                self.errors[name] = str(e)
                log.warning("%s: %s", name, e)
        self.events = [b for evs in self.by_src.values() for b in evs]

    def run(self) -> None:
        period = max(15, int(self.cfg.get("sala", "poll_seconds", 60)))
        while not self._stop.is_set():
            self.poll_once()
            self._stop.wait(period)

    def state(self, now: datetime) -> State:
        return room_state(self.events, now, float(self.cfg.get("sala", "lead_minutes", 5)),
                          bool(self.cfg.get("sala", "tentative_is_busy", True)))

    def stop(self):
        self._stop.set()


class Daemon:
    def __init__(self, cfg: cfgmod.Config, backend: str | None = None):
        self.cfg = cfg
        self.backend = backend or cfg.get("device", "backend", "auto")
        self.cal = CalendarPoller(cfg)
        self.out = None
        self.decision = None
        self.next_retry = 0.0

    def status(self) -> dict:
        d = self.decision
        return {"decisao": None if d is None else [look(s).name for s in d.leds()],
                "agenda_erros": self.cal.errors, "saida": type(self.out).__name__ if self.out else None}

    def _ensure_output(self) -> None:
        if self.out is not None or time.time() < self.next_retry:
            return
        try:
            self.out = open_output(self.backend, self.cfg.get("device", "luxafor_render", "stream"),
                                   int(self.cfg.get("device", "brightness", 255)))
            if self.out:
                log.info("saída: %s", type(self.out).__name__)
                self.decision = None
        except Exception as e:
            log.warning("dispositivo: %s", e)
            self.out = None
        if self.out is None:
            self.next_retry = time.time() + 2.0

    def step(self, now: float | None = None):
        now = time.time() if now is None else now
        raw = store.read_cached()
        policy = cfgmod.policy_from(self.cfg)
        mode = raw.get("mode", {})
        policy.display = mode.get("display", policy.display)
        policy.ai_enabled = mode.get("ai_enabled", policy.ai_enabled)
        inp = store.to_inputs(raw, self.cal.state(datetime.fromtimestamp(now, timezone.utc)))
        return decide(inp, policy, now)

    def run(self, port: int | None = None) -> None:
        threading.Thread(target=self.cal.run, daemon=True, name="signa-cal").start()
        port = port or int(self.cfg.get("server", "port", 47623))
        try:
            from .server import serve
            serve(port, cfgmod.local_token(), self.status)
        except OSError as e:
            log.warning("servidor local na porta %d: %s", port, e)
        hk = self.cfg.get("hotkey", "toggle_busy", "")
        if hk:
            start_hotkey(hk)
        while True:
            self._ensure_output()
            d = self.step()
            if self.out:
                try:
                    if d != self.decision:
                        log.info("LEDs: %s", [look(s).name for s in d.leds()])
                    self.out.show(d)
                    self.decision = d
                    self.out.tick()
                except OSError as e:  # desplugou
                    log.warning("dispositivo perdido: %s", e)
                    try:
                        self.out.close()
                    except Exception:
                        pass
                    self.out = None
            time.sleep(0.02)


def toggle_busy() -> State | None:
    raw = store.read()
    m = raw.get("manual")
    if m and m.get("state") == int(State.SALA_OCUPADO):
        store.set_manual(None)
        return None
    store.set_manual(State.SALA_OCUPADO)
    return State.SALA_OCUPADO


def start_hotkey(combo: str) -> None:
    """Atalho global (pynput). No Wayland o pynput costuma não ver teclas: use a CLI num atalho do sistema."""
    try:
        from pynput import keyboard  # type: ignore
    except ImportError:
        log.warning("hotkey: instale o extra [hotkey] (pynput)")
        return
    h = keyboard.GlobalHotKeys({combo: toggle_busy})
    h.daemon = True
    h.start()
