import re
from pathlib import Path

from signa.states import State, level, look

VEC = Path(__file__).resolve().parents[2] / "firmware" / "tests" / "vectors_states.h"


def test_python_curves_match_firmware_vectors():
    txt = VEC.read_text()
    times = [int(x) for x in re.search(r"VEC_T\[\d+\] = \{([^}]*)\}", txt)[1].split(",")]
    rows = re.findall(r"\{ ([\d, ]+) \}, /\* (\w+) \*/", txt)
    assert len(rows) == 10
    for vals, name in rows:
        st = State[name.replace("SIGNA_ST_", "")]
        for t, q in zip(times, map(int, vals.split(","))):
            assert abs(round(level(st, t / 1000) * 4096) - q) <= 1, (name, t)


def test_colors_from_produto_json():
    assert look(State.SALA_OCUPADO).rgb == (0xFF, 0x3B, 0x2F)
    assert look(State.IA_ERRO).rgb == (0xFF, 0x3F, 0xC8)


def test_error_strobe_below_3hz():
    rises, prev = 0, False
    for ms in range(10000):
        on = level(State.IA_ERRO, ms / 1000) > 0.5
        rises += on and not prev
        prev = on
    assert rises == 25  # 2,5 Hz
