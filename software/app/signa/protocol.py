"""Relatórios HID de 8 bytes (sem Report ID). Ver docs/arquitetura.md §Protocolo."""
from __future__ import annotations

from .states import State

ACK = 0x42
OP_STATIC, OP_FADE, OP_STROBE, OP_WAVE, OP_PATTERN = 0x01, 0x02, 0x03, 0x04, 0x06
OP_VERSION, OP_SERIAL_R = 0x80, 0x62
OP_STATE, OP_MIXED, OP_BRIGHT, OP_INFO = 0x10, 0x11, 0x12, 0x1F
LED_ALL, LED_BOTTOM, LED_MIDDLE, LED_TOP = 0xFF, 0x01, 0x02, 0x03
SAFE_LEDS = {LED_ALL, LED_BOTTOM, LED_MIDDLE, LED_TOP}  # 0x13 trava o Luxafor original


def _r(*b: int) -> bytes:
    if any(not 0 <= x <= 255 for x in b):
        raise ValueError("byte fora de 0..255")
    return bytes(b).ljust(8, b"\0")[:8]


def _led(led: int) -> int:
    if led not in SAFE_LEDS:
        raise ValueError(f"LED 0x{led:02x} não permitido (só 1, 2, 3, FF)")
    return led


def static(led: int, rgb) -> bytes:
    return _r(OP_STATIC, _led(led), *rgb)


def fade(led: int, rgb, tempo: int) -> bytes:
    return _r(OP_FADE, _led(led), *rgb, tempo)


def strobe(led: int, rgb, tempo: int, rep: int) -> bytes:
    return _r(OP_STROBE, _led(led), *rgb, tempo, 0, rep)


def wave(kind: int, rgb, rep: int, vel: int) -> bytes:
    return _r(OP_WAVE, kind, *rgb, 0, rep, vel)


def signa_state(st: State) -> bytes:
    return _r(OP_STATE, int(st))


def signa_mixed(sala: State, ia: State) -> bytes:
    if not (sala == State.OFF or sala.is_sala) or not (ia == State.OFF or ia.is_ia):
        raise ValueError("misto: primeiro um estado de sala, depois um de IA")
    return _r(OP_MIXED, int(sala), int(ia))


def brightness(v: int) -> bytes:
    return _r(OP_BRIGHT, v)


def info() -> bytes:
    return _r(OP_INFO)


def is_signa_info(resp: bytes) -> bool:
    return len(resp) >= 3 and resp[0] == OP_INFO and resp[1:3] == b"SG"
