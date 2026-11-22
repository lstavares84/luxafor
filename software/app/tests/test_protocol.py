import pytest

from signa import protocol as pr
from signa.device import luxafor_opcodes
from signa.engine import Decision
from signa.states import State


def test_reports_are_8_bytes():
    assert pr.static(0xFF, (1, 2, 3)) == bytes([1, 0xFF, 1, 2, 3, 0, 0, 0])
    assert pr.strobe(1, (9, 9, 9), 6, 0) == bytes([3, 1, 9, 9, 9, 6, 0, 0])
    assert pr.signa_state(State.IA_ERRO) == bytes([0x10, 7, 0, 0, 0, 0, 0, 0])
    assert pr.signa_mixed(State.SALA_LIVRE, State.IA_ATENCAO) == bytes([0x11, 1, 6, 0, 0, 0, 0, 0])


def test_unsafe_led_rejected():
    with pytest.raises(ValueError):
        pr.static(0x13, (1, 1, 1))
    with pytest.raises(ValueError):
        pr.signa_mixed(State.IA_ERRO, State.IA_ERRO)


def test_luxafor_fallback_uses_only_compatible_opcodes():
    for st in State:
        if st == State.OFF:
            continue
        for d in (Decision(False, st), Decision(True, sala=State.SALA_LIVRE, ia=st if st.is_ia else State.IA_DESOCUPADA)):
            for rep in luxafor_opcodes(d):
                assert rep[0] in (0x01, 0x03, 0x04) and len(rep) == 8
                if rep[0] in (0x01, 0x03):
                    assert rep[1] in pr.SAFE_LEDS


def test_luxafor_error_strobe_is_under_3hz():
    rep = luxafor_opcodes(Decision(False, State.IA_ERRO))[0]
    assert rep[0] == 0x03 and rep[7] == 0
    assert 1 / (rep[5] * 0.0655) < 3.0
