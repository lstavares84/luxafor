"""Estado compartilhado (state.json na pasta de config). A CLI e os hooks gravam aqui mesmo sem o daemon
rodando; o daemon relê quando o arquivo muda. Escrita atômica com trava simples por arquivo."""
from __future__ import annotations

import json
import os
import time
from contextlib import contextmanager
from pathlib import Path

from .config import config_dir
from .engine import AIReport, Inputs
from .states import State

MAX_AGE_S = 24 * 3600


def path() -> Path:
    return config_dir() / "state.json"


@contextmanager
def _lock(p: Path, timeout: float = 2.0):
    lk = p.with_suffix(".lock")
    lk.parent.mkdir(parents=True, exist_ok=True)
    end = time.time() + timeout
    while True:
        try:
            fd = os.open(lk, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            break
        except FileExistsError:
            try:
                if time.time() - lk.stat().st_mtime > 10:  # trava esquecida por processo morto
                    lk.unlink(missing_ok=True)
                    continue
            except FileNotFoundError:
                continue
            if time.time() > end:
                raise TimeoutError("state.json travado")
            time.sleep(0.01)
    try:
        yield
    finally:
        lk.unlink(missing_ok=True)


def read() -> dict:
    try:
        return json.loads(path().read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


_cache: tuple = (None, None, {})


def read_cached() -> dict:
    """Para o laço do daemon: só relê o arquivo quando o mtime muda."""
    global _cache
    p = path()
    try:
        m = p.stat().st_mtime_ns
    except FileNotFoundError:
        return {}
    if _cache[0] != str(p) or _cache[1] != m:
        _cache = (str(p), m, read())
    return _cache[2]


def update(fn) -> dict:
    p = path()
    with _lock(p):
        d = read()
        fn(d)
        now = time.time()
        d["ai"] = {k: v for k, v in d.get("ai", {}).items() if now - v.get("at", 0) < MAX_AGE_S}
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps(d, indent=1), encoding="utf-8")
        os.replace(tmp, p)
    return d


def set_ai(source: str, state: State | None, session: str = "") -> None:
    key = f"{source}/{session or 'default'}"

    def f(d):
        ai = d.setdefault("ai", {})
        if state is None:
            ai.pop(key, None)
        else:
            ai[key] = {"source": source, "session": session, "state": int(state), "at": time.time()}
    update(f)


def set_manual(state: State | None, until: float | None = None) -> None:
    def f(d):
        d["manual"] = None if state is None else {"state": int(state), "until": until}
    update(f)


def set_mode(display: str | None = None, ai_enabled: bool | None = None) -> None:
    def f(d):
        m = d.setdefault("mode", {})
        if display is not None:
            m["display"] = display
        if ai_enabled is not None:
            m["ai_enabled"] = ai_enabled
    update(f)


def to_inputs(d: dict, calendar: State) -> Inputs:
    inp = Inputs(calendar=calendar)
    m = d.get("manual")
    if m:
        inp.manual, inp.manual_until = State(m["state"]), m.get("until")
    for k, v in d.get("ai", {}).items():
        try:
            inp.ai[k] = AIReport(State(v["state"]), v["at"], v["source"], v.get("session", ""))
        except (KeyError, ValueError):
            continue
    return inp
