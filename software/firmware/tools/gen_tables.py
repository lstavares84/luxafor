#!/usr/bin/env python3
"""Gera src/signa_tables.c/.h e tests/vectors_states.h a partir de data/produto.json.

Fonte única dos estados SIGNA (cor, onda, períodos, níveis). Rode de novo sempre que o
produto.json mudar:  python3 tools/gen_tables.py
"""
import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FW = os.path.dirname(HERE)
ROOT = os.path.dirname(FW)
P = json.load(open(os.path.join(ROOT, "data", "produto.json"), encoding="utf-8"))
M = {m["id"]: m for m in P["modos"]}

GAMMA = 2.2
Q = 4096  # Q12

# id do firmware -> (enum, chave produto.json, variante)
STATES = [
    ("SIGNA_ST_OFF", None, None),
    ("SIGNA_ST_SALA_LIVRE", "sala_livre", None),
    ("SIGNA_ST_SALA_PRESTES", "sala_prestes", None),
    ("SIGNA_ST_SALA_OCUPADO", "sala_ocupado", None),
    ("SIGNA_ST_IA_DESOCUPADA", "ia_livre", None),
    ("SIGNA_ST_IA_PROCESSANDO", "ia_processando", None),
    ("SIGNA_ST_IA_ATENCAO", "ia_atencao", None),
    ("SIGNA_ST_IA_ERRO", "ia_erro", None),
    ("SIGNA_ST_IA_LIMITE_5H", "ia_limite", "5h"),
    ("SIGNA_ST_IA_LIMITE_SEMANAL", "ia_limite", "semanal"),
]


def level(key, var, t):
    """Mesma função de caderno.py::brilho_estado (t em segundos)."""
    if key is None:
        return 0.0
    e = M[key]
    k = e["onda"]
    if var == "semanal":
        return e["semanal_nivel"]
    if k == "const":
        return e["nivel"]
    if k == "breath":
        T = e["periodo_s"]
        return e["piso"] + (1 - e["piso"]) * ((1 - math.cos(2 * math.pi * t / T)) / 2) ** e["expoente"]
    # ondas por partes em ms inteiros (evita o erro de float de 1.2 % 0.4 em Python)
    ms = round(t * 1000)
    if k == "square":
        per = round(1000 / e["freq_hz"])
        return 1.0 if (ms % per) < round(e["duty"] * per) else e["piso"]
    if k == "flash":
        return 1.0 if (ms % round(e["periodo_s"] * 1000)) < round(e["pulso_s"] * 1000) else e["piso"]
    if k == "double_pulse":
        tm = ms % round(e["periodo_s"] * 1000)
        on, gap = round(e["pulso_s"] * 1000), round(e["gap_s"] * 1000)
        p1 = 0 <= tm < on
        p2 = (on + gap) <= tm < (2 * on + gap)
        return e["pico"] if (p1 or p2) else e["piso"]
    raise ValueError(k)


def q12(x):
    return max(0, min(Q, int(round(x * Q))))


def desc(key, var):
    if key is None:
        return dict(rgb=(0, 0, 0), wave="SIGNA_W_CONST", per=0, on=0, gap=0, hi=0, lo=0, tab=0)
    e = M[key]
    h = e["hex"].lstrip("#")
    rgb = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    k = e["onda"]
    if var == "semanal":
        return dict(rgb=rgb, wave="SIGNA_W_CONST", per=0, on=0, gap=0, hi=q12(e["semanal_nivel"]), lo=0, tab=0)
    if k == "const":
        return dict(rgb=rgb, wave="SIGNA_W_CONST", per=0, on=0, gap=0, hi=q12(e["nivel"]), lo=0, tab=0)
    if k == "breath":
        return dict(rgb=rgb, wave="SIGNA_W_BREATH", per=round(e["periodo_s"] * 1000), on=0, gap=0,
                    hi=Q, lo=q12(e["piso"]), tab=e["expoente"])
    if k == "square":
        per = round(1000 / e["freq_hz"])
        return dict(rgb=rgb, wave="SIGNA_W_PULSE", per=per, on=round(per * e["duty"]), gap=0,
                    hi=Q, lo=q12(e["piso"]), tab=0)
    if k == "flash":
        return dict(rgb=rgb, wave="SIGNA_W_PULSE", per=round(e["periodo_s"] * 1000),
                    on=round(e["pulso_s"] * 1000), gap=0, hi=Q, lo=q12(e["piso"]), tab=0)
    if k == "double_pulse":
        return dict(rgb=rgb, wave="SIGNA_W_DOUBLE", per=round(e["periodo_s"] * 1000),
                    on=round(e["pulso_s"] * 1000), gap=round(e["gap_s"] * 1000),
                    hi=q12(e["pico"]), lo=q12(e["piso"]), tab=0)
    raise ValueError(k)


def main():
    descs = [desc(k, v) for _, k, v in STATES]
    exps = sorted({d["tab"] for d in descs if d["wave"] == "SIGNA_W_BREATH"})
    tabidx = {x: i for i, x in enumerate(exps)}

    out = []
    out.append("/* GERADO por tools/gen_tables.py a partir de data/produto.json. Não editar à mão. */\n")
    out.append('#include "signa_tables.h"\n\n')
    out.append(f"/* gamma {GAMMA}: entrada Q8.8 (0..65535) em 256 passos, saída 16 bit */\n")
    out.append("const uint16_t signa_gamma_lut[257] = {\n")
    g = [round(((i / 256) ** GAMMA) * 65535) for i in range(257)]
    for i in range(0, 257, 12):
        out.append("  " + ", ".join(str(x) for x in g[i:i + 12]) + ",\n")
    out.append("};\n\n")
    out.append("/* forma ((1-cos(2*pi*x))/2)^exp, x = i/256, Q12; uma tabela por expoente */\n")
    out.append(f"const uint16_t signa_breath_tab[{len(exps)}][257] = {{\n")
    for x in exps:
        v = [q12(((1 - math.cos(2 * math.pi * i / 256)) / 2) ** x) for i in range(257)]
        out.append(f"  {{ /* exp {x} */\n")
        for i in range(0, 257, 16):
            out.append("    " + ", ".join(str(y) for y in v[i:i + 16]) + ",\n")
        out.append("  },\n")
    out.append("};\n\n")
    out.append("const signa_state_desc_t signa_states[SIGNA_ST_COUNT] = {\n")
    for (en, k, v), d in zip(STATES, descs):
        r, gg, b = d["rgb"]
        t = tabidx.get(d["tab"], 0) if d["wave"] == "SIGNA_W_BREATH" else 0
        out.append(f"  [{en}] = {{ {r}, {gg}, {b}, {d['wave']}, {t}, {d['per']}, {d['on']}, {d['gap']}, {d['hi']}, {d['lo']} }},"
                   f" /* {k or 'off'}{' ' + v if v else ''} */\n")
    out.append("};\n")
    open(os.path.join(FW, "src", "signa_tables.c"), "w").write("".join(out))

    h = ["/* GERADO por tools/gen_tables.py. Não editar à mão. */\n#pragma once\n#include <stdint.h>\n\n",
         "typedef enum {\n"]
    for i, (en, k, v) in enumerate(STATES):
        h.append(f"  {en} = {i},\n")
    h.append("  SIGNA_ST_COUNT\n} signa_state_t;\n\n")
    h.append("enum { SIGNA_W_CONST = 0, SIGNA_W_BREATH = 1, SIGNA_W_PULSE = 2, SIGNA_W_DOUBLE = 3 };\n\n")
    h.append("typedef struct {\n  uint8_t r, g, b;\n  uint8_t wave;\n  uint8_t table;\n"
             "  uint16_t period_ms, on_ms, gap_ms;\n  uint16_t hi_q12, lo_q12;\n} signa_state_desc_t;\n\n")
    h.append("extern const uint16_t signa_gamma_lut[257];\n")
    h.append(f"extern const uint16_t signa_breath_tab[{len(exps)}][257];\n")
    h.append("extern const signa_state_desc_t signa_states[SIGNA_ST_COUNT];\n")
    open(os.path.join(FW, "src", "signa_tables.h"), "w").write("".join(h))

    times = [0, 37, 100, 129, 130, 131, 250, 333, 499, 500, 501, 600, 777, 1200, 1500, 2000, 2399, 2400, 2999, 3500, 7777]
    v = ["/* GERADO por tools/gen_tables.py: nível esperado (Q12) por estado e tempo (ms). */\n#pragma once\n",
         f"static const uint32_t VEC_T[{len(times)}] = {{ {', '.join(map(str, times))} }};\n",
         f"static const uint16_t VEC_L[{len(STATES)}][{len(times)}] = {{\n"]
    for en, k, var in STATES:
        v.append("  { " + ", ".join(str(q12(level(k, var, t / 1000))) for t in times) + f" }}, /* {en} */\n")
    v.append("};\n")
    open(os.path.join(FW, "tests", "vectors_states.h"), "w").write("".join(v))
    print("ok:", len(STATES), "estados,", len(exps), "tabelas de respiração")


if __name__ == "__main__":
    main()
