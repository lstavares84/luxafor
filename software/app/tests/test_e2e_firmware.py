"""Integração: o app conversa com o MESMO motor C do firmware (compilado como .so), sem hardware."""
import ctypes
import subprocess
from pathlib import Path

import pytest

from signa.device import LuxaforOut, SignaOut, probe_is_signa
from signa.engine import Decision
from signa.states import State, look

FW = Path(__file__).resolve().parents[2] / "firmware"


@pytest.fixture(scope="module")
def lib(tmp_path_factory):
    so = tmp_path_factory.mktemp("fw") / "libengine.so"
    subprocess.run(["gcc", "-shared", "-fPIC", "-O1", "-I", str(FW / "src"), "-o", str(so),
                    str(FW / "src/engine.c"), str(FW / "src/signa_tables.c")], check=True)
    L = ctypes.CDLL(str(so))
    L.engine_init(bytes(6), None)
    return L


class FakeLink:
    """Faz o papel do hidapi: entrega o relatório ao motor C e devolve as respostas."""
    def __init__(self, L):
        self.L, self.sent = L, []

    def send(self, rep: bytes):
        assert len(rep) == 8
        self.sent.append(rep)
        self.L.engine_handle_report(rep)

    def read(self, timeout=0.1):
        out, buf = [], ctypes.create_string_buffer(8)
        while self.L.engine_pop_report(buf):
            out.append(buf.raw)
        return out

    def close(self):
        pass

    def ticks(self, n):
        for _ in range(n):
            self.L.engine_tick_1ms()

    def disp(self):
        arr = (ctypes.c_uint16 * 9)()
        self.L.engine_display_q88(arr)
        return [tuple(arr[i * 3:(i + 1) * 3]) for i in range(3)]


def c16(rgb, lv=1.0):
    return tuple(int(int(c * 257) * round(lv * 4096) >> 12) for c in rgb)


def test_probe_and_native_states(lib):
    link = FakeLink(lib)
    assert probe_is_signa(link)
    out = SignaOut(link)
    link.read()
    out.show(Decision(True, sala=State.SALA_OCUPADO, ia=State.IA_ERRO))
    link.ticks(10)
    red = c16(look(State.SALA_OCUPADO).rgb)
    assert link.disp() == [red, red, red]
    out.show(Decision(True, sala=State.SALA_LIVRE, ia=State.IA_ERRO))
    link.ticks(50)
    d = link.disp()
    assert d[0] == c16(look(State.IA_ERRO).rgb)  # LED 1 no pulso do erro
    assert d[2] == c16(look(State.SALA_LIVRE).rgb, 0.28)
    n = len(link.sent)
    out.show(Decision(True, sala=State.SALA_LIVRE, ia=State.IA_ERRO))
    assert len(link.sent) == n  # mesma decisão: nada é reenviado


def test_luxafor_fallback_opcodes_on_compatible_engine(lib):
    link = FakeLink(lib)
    out = LuxaforOut(link, render="opcodes")
    out.show(Decision(False, State.IA_ERRO))  # strobe 03 com rep 0
    assert link.sent[-1][0] == 0x03
    link.ticks(1)
    assert link.disp()[0][0] == 0xFFFF
    on = 0
    for _ in range(10000):
        link.ticks(1)
        on += link.disp()[0][0] > 0
    assert 0.4 < on / 10000 < 0.6  # strobe a 50 %


def test_luxafor_stream(lib):
    link = FakeLink(lib)
    out = LuxaforOut(link, render="stream")
    out.show(Decision(True, sala=State.SALA_LIVRE, ia=State.IA_PROCESSANDO))
    assert all(r[0] == 0x01 and r[1] in (1, 2, 3, 0xFF) for r in link.sent)
