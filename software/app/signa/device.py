"""Saídas: SIGNA nativo (0x10/0x11), Luxafor Flag original (fallback 01/03/04) e simulador ANSI."""
from __future__ import annotations

import sys
import threading
import time
from typing import Protocol as _P

from . import protocol as pr
from .engine import Decision
from .states import State, color_at, level, look

# (VID, PID, descrição). TODO(Lucas): trocar 1209:0001 pelo par definitivo.
KNOWN_IDS = [(0x1209, 0x0001, "SIGNA (pid.codes test PID)"), (0x04D8, 0xF372, "Luxafor Flag / SIGNA com IDs do Flag")]


class Output(_P):
    def show(self, d: Decision) -> None: ...
    def tick(self) -> None: ...
    def close(self) -> None: ...


# ---------------------------------------------------------------- HID
class HidLink:
    """hidapi (pacote PyPI "hidapi", import hid). Escreve 00 + 8 bytes (Report ID 0)."""

    def __init__(self, vid: int, pid: int, path: bytes | None = None):
        import hid  # type: ignore
        self.dev = hid.device()
        if path:
            self.dev.open_path(path)
        else:
            self.dev.open(vid, pid)
        self.dev.set_nonblocking(True)
        self.lock = threading.Lock()

    def send(self, rep: bytes) -> None:
        with self.lock:
            if self.dev.write(b"\0" + rep) < 0:
                raise OSError("falha de escrita HID")

    def read(self, timeout: float = 0.1) -> list[bytes]:
        out, end = [], time.time() + timeout
        while time.time() < end:
            with self.lock:
                d = self.dev.read(8)
            if d:
                out.append(bytes(d))
            else:
                time.sleep(0.005)
        return out

    def close(self) -> None:
        self.dev.close()


def enumerate_devices():
    try:
        import hid  # type: ignore
    except ImportError:
        return []
    found = []
    for vid, pid, desc in KNOWN_IDS:
        for d in hid.enumerate(vid, pid):
            found.append({"vid": vid, "pid": pid, "desc": desc, "path": d["path"],
                          "serial": d.get("serial_number"), "product": d.get("product_string")})
    return found


def probe_is_signa(link) -> bool:
    link.send(pr.info())
    return any(pr.is_signa_info(r) for r in link.read(0.15))


class SignaOut:
    """Firmware SIGNA: um comando por transição; as curvas rodam no firmware."""

    def __init__(self, link, brightness: int = 255):
        self.link, self.last = link, None
        link.send(pr.brightness(brightness))

    def show(self, d: Decision) -> None:
        if d == self.last:
            return
        self.link.send(pr.signa_mixed(d.sala, d.ia) if d.mixed else pr.signa_state(d.all_state))
        self.last = d

    def tick(self) -> None:
        pass

    def close(self) -> None:
        self.link.close()


class LuxaforOut:
    """Luxafor Flag original: não tem os estados. Dois jeitos de renderizar:
    stream  -> o app manda 01 (cor fixa) por LED a ~25 Hz seguindo a mesma curva do firmware
    opcodes -> um comando por transição: 01 fixo, 04 wave 5 (respiração), 03 strobe (piscar)
    """

    def __init__(self, link, render: str = "stream", fps: float = 25.0):
        self.link, self.render, self.dt = link, render, 1.0 / fps
        self.d: Decision | None = None
        self.t0 = time.time()
        self.last_tx = 0.0
        self.last_cols: list | None = None

    def show(self, d: Decision) -> None:
        if d == self.d:
            return
        prev = self.d
        self.d = d
        if prev is None or prev.leds() != d.leds():
            self.t0 = time.time()
        if self.render == "opcodes":
            for rep in luxafor_opcodes(d):
                self.link.send(rep)
                self.link.read(0.02)
        else:
            self.last_cols = None
            self.tick()

    def tick(self) -> None:
        if self.render != "stream" or self.d is None or time.time() - self.last_tx < self.dt:
            return
        t = time.time() - self.t0
        cols = [color_at(s, t) for s in self.d.leds()]
        if cols != self.last_cols:
            if cols[0] == cols[1] == cols[2]:
                self.link.send(pr.static(pr.LED_ALL, cols[0]))
            else:
                for i, c in enumerate(cols):
                    if self.last_cols is None or self.last_cols[i] != c:
                        self.link.send(pr.static(i + 1, c))
            self.last_cols = cols
        self.last_tx = time.time()
        self.link.read(0.0)  # esvazia ACKs

    def close(self) -> None:
        self.link.close()


def _scaled(st: State, lv: float):
    r, g, b = look(st).rgb
    return (round(r * lv), round(g * lv), round(b * lv))


def luxafor_opcodes(d: Decision) -> list[bytes]:
    """Aproximação com os opcodes do Flag (tempo de strobe = 65,5 ms × t; wave = ~65 ms × vel)."""
    def one(led: int, st: State) -> bytes:
        e = look(st).spec
        k = "const" if look(st).variant == "semanal" else e["onda"]
        if k == "breath" and led == pr.LED_ALL:      # wave 5 só existe para todos os LEDs
            return pr.wave(5, look(st).rgb, 0, max(1, round(e["periodo_s"] * 1000 / 65)))
        if k in ("square", "flash"):
            per = 1.0 / e["freq_hz"]
            return pr.strobe(led, look(st).rgb, max(1, round(per * 1000 / 65.5)), 0)
        if k == "double_pulse":
            return pr.static(led, _scaled(st, e["pico"]))
        return pr.static(led, _scaled(st, level(st, 0.0) if k == "const" else 0.6))

    a, b, c = d.leds()
    if a == b == c:
        return [one(pr.LED_ALL, a)]
    return [pr.static(pr.LED_MIDDLE, _scaled(b, level(b, 0))), pr.static(pr.LED_TOP, _scaled(c, level(c, 0))),
            one(pr.LED_BOTTOM, a)]


# ---------------------------------------------------------------- simulador
class SimOut:
    """Sem hardware: desenha os 3 LEDs no terminal (cor ANSI 24 bit) a ~20 Hz."""

    def __init__(self, stream=None, fps: float = 20.0, plain: bool = False):
        self.s = stream or sys.stdout
        self.d: Decision | None = None
        self.t0 = time.time()
        self.dt, self.last = 1.0 / fps, 0.0
        self.plain = plain or not self.s.isatty()
        self.printed = None

    def show(self, d: Decision) -> None:
        if d != self.d:
            if self.d is None or self.d.leds() != d.leds():
                self.t0 = time.time()
            self.d = d
            if self.plain:
                self._line(0.0, newline=True)

    def _line(self, t: float, newline=False):
        leds = self.d.leds()
        parts = []
        for i in (2, 1, 0):
            st = leds[i]
            r, g, b = color_at(st, t)
            name = look(st).name
            if self.plain:
                parts.append(f"LED{i + 1}={name}")
            else:
                parts.append(f"\x1b[48;2;{r};{g};{b}m    \x1b[0m {name:<26}")
        txt = ("  ".join(parts)) if self.plain else (" | ".join(parts))
        if self.plain:
            if txt != self.printed:
                print(time.strftime("%H:%M:%S"), txt, file=self.s, flush=True)
                self.printed = txt
        else:
            self.s.write("\r" + txt + ("\n" if newline else ""))
            self.s.flush()

    def tick(self) -> None:
        if self.d is None or self.plain or time.time() - self.last < self.dt:
            return
        self.last = time.time()
        self._line(time.time() - self.t0)

    def close(self) -> None:
        if not self.plain:
            self.s.write("\n")


def open_output(backend: str = "auto", luxafor_render: str = "stream", brightness: int = 255):
    if backend == "sim":
        return SimOut()
    devs = enumerate_devices()
    if not devs:
        if backend == "auto":
            return None
        raise RuntimeError("nenhum SIGNA/Luxafor encontrado (hidapi instalado? permissão udev no Linux?)")
    d = devs[0]
    link = HidLink(d["vid"], d["pid"], d["path"])
    if backend in ("auto", "signa") and probe_is_signa(link):
        return SignaOut(link, brightness)
    if backend == "signa":
        link.close()
        raise RuntimeError("o aparelho não respondeu ao 0x1F (não é firmware SIGNA)")
    return LuxaforOut(link, luxafor_render)
