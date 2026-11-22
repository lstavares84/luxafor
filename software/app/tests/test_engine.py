import itertools

from signa.engine import AIReport, Decision, Inputs, Policy, decide
from signa.states import LADDER, RANK, State

NOW = 1_000_000.0
SALA = [State.SALA_LIVRE, State.SALA_PRESTES, State.SALA_OCUPADO]
IA = [State.IA_DESOCUPADA, State.IA_PROCESSANDO, State.IA_ATENCAO, State.IA_ERRO, State.IA_LIMITE_5H, State.IA_LIMITE_SEMANAL]


def inp(cal=State.SALA_LIVRE, **ai):
    i = Inputs(calendar=cal)
    for k, st in ai.items():
        i.ai[k] = AIReport(st, NOW, k.replace("_", "-"))
    return i


def test_ladder_exact_order():
    assert [s for s in LADDER if s != State.OFF] == [
        State.SALA_OCUPADO, State.SALA_PRESTES, State.IA_ERRO, State.IA_ATENCAO, State.IA_PROCESSANDO,
        State.IA_LIMITE_5H, State.IA_LIMITE_SEMANAL, State.SALA_LIVRE, State.IA_DESOCUPADA]


def test_ai_opt_in_off_shows_only_room():
    p = Policy(ai_enabled=False)
    d = decide(inp(State.SALA_PRESTES, claude_code=State.IA_ERRO), p, NOW)
    assert d == Decision(False, State.SALA_PRESTES)


def test_escada_all_pairs():
    p = Policy(display="escada", ai_enabled=True)
    for s, a in itertools.product(SALA, IA):
        d = decide(inp(s, claude_code=a), p, NOW)
        expect = min((s, a), key=RANK.get)
        assert d.leds() == (expect,) * 3, (s, a)


def test_misto_split_and_busy_lock():
    p = Policy(display="misto", ai_enabled=True)
    for s, a in itertools.product(SALA, IA):
        leds = decide(inp(s, codex=a), p, NOW).leds()
        if s == State.SALA_OCUPADO:
            assert leds == (State.SALA_OCUPADO,) * 3  # ocupado trava os 3 em vermelho
        else:
            assert leds == (a, s, s)


def test_manual_beats_calendar_and_expires():
    p = Policy()
    i = inp(State.SALA_LIVRE)
    i.manual, i.manual_until = State.SALA_OCUPADO, NOW + 60
    assert decide(i, p, NOW).all_state == State.SALA_OCUPADO
    assert decide(i, p, NOW + 61).all_state == State.SALA_LIVRE
    i.manual, i.manual_until = State.SALA_LIVRE, None
    i.calendar = State.SALA_OCUPADO
    assert decide(i, p, NOW + 9999).all_state == State.SALA_LIVRE  # "livre" manual também vence a agenda


def test_aggregate_sources_strongest_wins():
    p = Policy(display="misto", ai_enabled=True)
    d = decide(inp(claude_code=State.IA_PROCESSANDO, codex=State.IA_ATENCAO, grok_web=State.IA_LIMITE_5H), p, NOW)
    assert d.ia == State.IA_ATENCAO
    d = decide(inp(claude_code=State.IA_LIMITE_SEMANAL, codex=State.IA_LIMITE_5H), p, NOW)
    assert d.ia == State.IA_LIMITE_5H


def test_ttl_processing_goes_idle_and_unknown_source_ignored():
    p = Policy(display="misto", ai_enabled=True, processing_ttl_s=900)
    i = inp()
    i.ai["claude-code/x"] = AIReport(State.IA_PROCESSANDO, NOW - 901, "claude-code")
    i.ai["hacker/x"] = AIReport(State.IA_ERRO, NOW, "hacker")
    assert decide(i, p, NOW).ia == State.IA_DESOCUPADA


def test_no_ai_reports_is_idle():
    p = Policy(display="misto", ai_enabled=True)
    assert decide(inp(), p, NOW).leds() == (State.IA_DESOCUPADA, State.SALA_LIVRE, State.SALA_LIVRE)
