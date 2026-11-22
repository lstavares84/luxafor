"""Motor de prioridade: decide o que os 3 LEDs mostram.

Escada global (firmware_comportamento.md §7.1):
  SALA OCUPADO > SALA PRESTES > IA ERRO > IA ATENÇÃO > IA PROCESSANDO > IA LIMITE > SALA LIVRE > IA DESOCUPADA
Modos de exibição:
  sala   -> só a sala, nos 3 LEDs (IA desligada: é opt-in)
  misto  -> LED 3+2 = sala, LED 1 = IA; OCUPADO trava os 3 em vermelho (v1, não configurável)
  escada -> os 3 LEDs mostram o estado mais forte da escada global
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

from .states import RANK, State

IA_ORDER = [State.IA_ERRO, State.IA_ATENCAO, State.IA_PROCESSANDO, State.IA_LIMITE_5H,
            State.IA_LIMITE_SEMANAL, State.IA_DESOCUPADA]


@dataclass(frozen=True)
class Decision:
    mixed: bool
    all_state: State = State.OFF     # quando mixed = False
    sala: State = State.OFF          # quando mixed = True
    ia: State = State.OFF

    def leds(self) -> tuple[State, State, State]:
        """(LED 1 baixo, LED 2 meio, LED 3 topo)"""
        if not self.mixed:
            return (self.all_state,) * 3
        if self.sala == State.SALA_OCUPADO:
            return (State.SALA_OCUPADO,) * 3
        return (self.ia, self.sala, self.sala)


@dataclass
class AIReport:
    state: State
    at: float
    source: str
    session: str = ""


@dataclass
class Inputs:
    calendar: State = State.SALA_LIVRE          # o que a agenda diz agora
    manual: State | None = None                 # atalho/CLI: vence a agenda
    manual_until: float | None = None           # None = até ser desligado
    ai: dict[str, AIReport] = field(default_factory=dict)  # chave "fonte/sessão"


@dataclass
class Policy:
    display: str = "misto"        # sala | misto | escada
    ai_enabled: bool = False      # opt-in
    processing_ttl_s: float = 900   # processando sem sinal -> desocupada (CLI que morreu)
    attention_ttl_s: float = 0      # 0 = até a próxima mudança
    error_ttl_s: float = 600
    limit_5h_ttl_s: float = 5 * 3600
    limit_week_ttl_s: float = 24 * 3600
    ai_sources: tuple[str, ...] = ("claude-code", "codex", "chatgpt-web", "claude-web", "grok-web")


def _expired(r: AIReport, p: Policy, now: float) -> bool:
    ttl = {State.IA_PROCESSANDO: p.processing_ttl_s, State.IA_ATENCAO: p.attention_ttl_s,
           State.IA_ERRO: p.error_ttl_s, State.IA_LIMITE_5H: p.limit_5h_ttl_s,
           State.IA_LIMITE_SEMANAL: p.limit_week_ttl_s}.get(r.state, 0)
    return bool(ttl) and now - r.at > ttl


def sala_state(inp: Inputs, now: float) -> State:
    if inp.manual is not None and (inp.manual_until is None or now < inp.manual_until):
        return inp.manual
    return inp.calendar


def ia_state(inp: Inputs, p: Policy, now: float) -> State:
    """Agrega todas as fontes/sessões: vence a mais forte da sub-escada da IA."""
    best = None
    for r in inp.ai.values():
        if r.source not in p.ai_sources:
            continue
        st = State.IA_DESOCUPADA if _expired(r, p, now) else r.state
        if best is None or IA_ORDER.index(st) < IA_ORDER.index(best):
            best = st
    return best or State.IA_DESOCUPADA


def decide(inp: Inputs, p: Policy, now: float | None = None) -> Decision:
    now = time.time() if now is None else now
    sala = sala_state(inp, now)
    if not p.ai_enabled or p.display == "sala":
        return Decision(mixed=False, all_state=sala)
    ia = ia_state(inp, p, now)
    if p.display == "misto":
        return Decision(mixed=True, sala=sala, ia=ia)
    # escada global
    top = min((sala, ia), key=lambda s: RANK[s])
    return Decision(mixed=False, all_state=top)
