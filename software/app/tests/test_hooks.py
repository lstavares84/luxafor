from signa import hooks
from signa.states import State


def cc(name, **kw):
    return hooks.claude_code({"hook_event_name": name, "session_id": "s1", **kw})[0]


def test_claude_code_mapping():
    assert cc("UserPromptSubmit") == State.IA_PROCESSANDO
    assert cc("PreToolUse", tool_name="Bash") == State.IA_PROCESSANDO
    assert cc("PermissionRequest") == State.IA_ATENCAO
    assert cc("Notification", notification_type="permission_prompt") == State.IA_ATENCAO
    assert cc("Notification", notification_type="idle_prompt") == State.IA_DESOCUPADA
    assert cc("Notification", notification_type="auth_success") is None
    assert cc("Stop") == State.IA_DESOCUPADA
    assert cc("StopFailure", error="rate_limit", error_details="429 Too Many Requests") == State.IA_LIMITE_5H
    assert cc("StopFailure", error="rate_limit", last_assistant_message="weekly limit reached") == State.IA_LIMITE_SEMANAL
    assert cc("StopFailure", error="server_error") == State.IA_ERRO
    assert cc("SessionEnd") == hooks.REMOVE


def test_codex_hooks_and_stdout():
    ev = {"hook_event_name": "PostModelRequest", "session_id": "t", "status": "failed", "error": "You've hit your usage limit"}
    assert hooks.codex_hook(ev)[0] == State.IA_LIMITE_5H
    ev["error"] = "stream disconnected"
    assert hooks.codex_hook(ev)[0] == State.IA_ERRO
    assert hooks.codex_hook({"hook_event_name": "PermissionRequest"})[0] == State.IA_ATENCAO
    assert hooks.codex_hook_stdout({"hook_event_name": "Stop"}) == "{}"
    assert hooks.codex_hook_stdout({"hook_event_name": "UserPromptSubmit"}) == ""
    assert hooks.codex_notify({"type": "agent-turn-complete", "thread-id": "x"}) == (State.IA_DESOCUPADA, "x")
