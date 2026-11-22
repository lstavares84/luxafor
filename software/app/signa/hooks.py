"""Tradução dos eventos oficiais das CLIs de IA para estados SIGNA (puro, testável).

Claude Code hooks: https://code.claude.com/docs/en/hooks  (verificado em 22/11/2026)
  UserPromptSubmit / PreToolUse / PostToolUse / SubagentStart -> PROCESSANDO
  PermissionRequest, Notification(permission_prompt | elicitation_* | agent_needs_input) -> PRECISA DE ATENÇÃO
  Notification(idle_prompt) e Stop -> DESOCUPADA
  StopFailure(rate_limit) -> LIMITE (5 h ou semanal pelo texto do erro: heurística, a validar)
  StopFailure(outros) -> ERRO;  Notification(quota_auto_resume_fired) -> PROCESSANDO
  SessionEnd -> remove a sessão
Codex hooks (hooks.json): https://learn.chatgpt.com/docs/hooks  (verificado em 22/11/2026)
  UserPromptSubmit / PreToolUse / PostToolUse -> PROCESSANDO; PermissionRequest -> ATENÇÃO; Stop -> DESOCUPADA
  PostModelRequest(status=failed) -> ERRO, ou LIMITE se o texto falar de limite (heurística)
  SessionEnd -> remove.  Stop/SubagentStop exigem JSON no stdout: a CLI imprime "{}".
Codex `notify` (config.toml): só emite "agent-turn-complete" -> DESOCUPADA.
"""
from __future__ import annotations

import re

from .states import State

REMOVE = "remove"
_WEEK = re.compile(r"week|semana|7[- ]day", re.I)
_LIMIT = re.compile(r"rate[ _-]?limit|usage limit|quota|limite|too many requests|429", re.I)


def limit_variant(text: str) -> State:
    return State.IA_LIMITE_SEMANAL if _WEEK.search(text or "") else State.IA_LIMITE_5H


def claude_code(ev: dict):
    """-> (State | REMOVE | None, session_id)"""
    name, sid = ev.get("hook_event_name", ""), ev.get("session_id", "")
    if name in ("UserPromptSubmit", "PreToolUse", "PostToolUse", "PostToolBatch", "SubagentStart", "PreCompact"):
        return State.IA_PROCESSANDO, sid
    if name == "PermissionRequest":
        return State.IA_ATENCAO, sid
    if name == "Notification":
        nt = ev.get("notification_type", "")
        if nt in ("permission_prompt", "elicitation_dialog", "elicitation_url_dialog", "agent_needs_input"):
            return State.IA_ATENCAO, sid
        if nt == "idle_prompt":
            return State.IA_DESOCUPADA, sid
        if nt == "quota_auto_resume_fired":
            return State.IA_PROCESSANDO, sid
        if nt == "quota_auto_resume_disabled":
            return State.IA_LIMITE_5H, sid
        return None, sid
    if name == "Stop":
        return State.IA_DESOCUPADA, sid
    if name == "StopFailure":
        err = ev.get("error", "")
        if err == "rate_limit":
            return limit_variant(f"{ev.get('error_details', '')} {ev.get('last_assistant_message', '')}"), sid
        if err in ("billing_error",):
            return State.IA_LIMITE_SEMANAL if _WEEK.search(ev.get("error_details", "") or "") else State.IA_ERRO, sid
        return State.IA_ERRO, sid
    if name == "PostToolUseFailure":
        return State.IA_PROCESSANDO, sid  # ferramenta falhou, mas o agente segue trabalhando
    if name == "SessionEnd":
        return REMOVE, sid
    return None, sid


def codex_hook(ev: dict):
    name, sid = ev.get("hook_event_name", ""), ev.get("session_id", "") or ev.get("thread_id", "")
    if name in ("UserPromptSubmit", "PreToolUse", "PostToolUse", "PreModelRequest", "SubagentStart", "PreCompact"):
        return State.IA_PROCESSANDO, sid
    if name == "PermissionRequest":
        return State.IA_ATENCAO, sid
    if name in ("Stop", "Interrupt"):
        return State.IA_DESOCUPADA, sid
    if name == "PostModelRequest":
        if ev.get("status") == "failed":
            err = str(ev.get("error") or "")
            return (limit_variant(err) if _LIMIT.search(err) else State.IA_ERRO), sid
        return None, sid
    if name == "SessionEnd":
        return REMOVE, sid
    return None, sid


def codex_hook_stdout(ev: dict) -> str:
    """Stop/SubagentStop/Interrupt do Codex: texto puro no stdout é inválido; '{}' = sem decisão."""
    return "{}" if ev.get("hook_event_name") in ("Stop", "SubagentStop", "Interrupt") else ""


def codex_notify(payload: dict):
    if payload.get("type") == "agent-turn-complete":
        return State.IA_DESOCUPADA, payload.get("thread-id", "")
    return None, payload.get("thread-id", "")
