"""Estados SIGNA. Mesma fonte de dados do firmware (data/produto.json) e mesmos IDs do opcode 0x10/0x11."""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from enum import IntEnum
from importlib import resources


class State(IntEnum):
    OFF = 0
    SALA_LIVRE = 1
    SALA_PRESTES = 2
    SALA_OCUPADO = 3
    IA_DESOCUPADA = 4
    IA_PROCESSANDO = 5
    IA_ATENCAO = 6
    IA_ERRO = 7
    IA_LIMITE_5H = 8
    IA_LIMITE_SEMANAL = 9

    @property
    def is_sala(self) -> bool:
        return self in (State.SALA_LIVRE, State.SALA_PRESTES, State.SALA_OCUPADO)

    @property
    def is_ia(self) -> bool:
        return self >= State.IA_DESOCUPADA


# chave no produto.json e variante
_KEYS = {
    State.SALA_LIVRE: ("sala_livre", None), State.SALA_PRESTES: ("sala_prestes", None),
    State.SALA_OCUPADO: ("sala_ocupado", None), State.IA_DESOCUPADA: ("ia_livre", None),
    State.IA_PROCESSANDO: ("ia_processando", None), State.IA_ATENCAO: ("ia_atencao", None),
    State.IA_ERRO: ("ia_erro", None), State.IA_LIMITE_5H: ("ia_limite", "5h"),
    State.IA_LIMITE_SEMANAL: ("ia_limite", "semanal"),
}

# Escada global (firmware_comportamento.md §7.1), do mais forte para o mais fraco
LADDER = [State.SALA_OCUPADO, State.SALA_PRESTES, State.IA_ERRO, State.IA_ATENCAO, State.IA_PROCESSANDO,
          State.IA_LIMITE_5H, State.IA_LIMITE_SEMANAL, State.SALA_LIVRE, State.IA_DESOCUPADA, State.OFF]
RANK = {s: i for i, s in enumerate(LADDER)}

NAMES = {  # nomes aceitos na CLI
    "livre": State.SALA_LIVRE, "prestes": State.SALA_PRESTES, "ocupado": State.SALA_OCUPADO,
    "desocupada": State.IA_DESOCUPADA, "idle": State.IA_DESOCUPADA, "processando": State.IA_PROCESSANDO,
    "busy": State.IA_PROCESSANDO, "atencao": State.IA_ATENCAO, "attention": State.IA_ATENCAO,
    "erro": State.IA_ERRO, "error": State.IA_ERRO, "limite": State.IA_LIMITE_5H,
    "limite-5h": State.IA_LIMITE_5H, "limite-semanal": State.IA_LIMITE_SEMANAL, "off": State.OFF,
}


@dataclass(frozen=True)
class Look:
    name: str
    rgb: tuple[int, int, int]
    spec: dict
    variant: str | None


def _load() -> dict:
    with resources.files("signa").joinpath("data/produto.json").open(encoding="utf-8") as f:
        return {m["id"]: m for m in json.load(f)["modos"]}


_MODOS = _load()


def look(st: State) -> Look:
    if st == State.OFF:
        return Look("APAGADO", (0, 0, 0), {"onda": "const", "nivel": 0.0}, None)
    key, var = _KEYS[st]
    m = _MODOS[key]
    h = m["hex"].lstrip("#")
    name = m["nome"] + (f" ({var})" if var else "")
    return Look(name, (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)), m, var)


def level(st: State, t: float) -> float:
    """Brilho 0..1 no instante t (s). Mesma curva de caderno.py::brilho_estado e do firmware."""
    lk = look(st)
    e, var = lk.spec, lk.variant
    if var == "semanal":
        return e["semanal_nivel"]
    k = e["onda"]
    ms = round(t * 1000)
    if k == "const":
        return e["nivel"]
    if k == "breath":
        T = e["periodo_s"]
        return e["piso"] + (1 - e["piso"]) * ((1 - math.cos(2 * math.pi * t / T)) / 2) ** e["expoente"]
    if k == "square":
        per = round(1000 / e["freq_hz"])
        return 1.0 if ms % per < round(e["duty"] * per) else e["piso"]
    if k == "flash":
        return 1.0 if ms % round(e["periodo_s"] * 1000) < round(e["pulso_s"] * 1000) else e["piso"]
    if k == "double_pulse":
        tm = ms % round(e["periodo_s"] * 1000)
        on, gap = round(e["pulso_s"] * 1000), round(e["gap_s"] * 1000)
        return e["pico"] if (tm < on or on + gap <= tm < 2 * on + gap) else e["piso"]
    return 0.0


def color_at(st: State, t: float) -> tuple[int, int, int]:
    r, g, b = look(st).rgb
    lv = level(st, t)
    return (round(r * lv), round(g * lv), round(b * lv))
