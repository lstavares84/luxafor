import io
import json
import sys
import time
import urllib.request


from signa import cli, config, store
from signa.server import serve
from signa.states import State


def test_cli_ai_and_status(capsys):
    cli.main(["modo", "--display", "misto", "--ia", "on"])
    cli.main(["ai", "--source", "claude-code", "--state", "erro"])
    cli.main(["status"])
    out = capsys.readouterr().out
    assert "LED 1 (baixo): ERRO" in out and "LED 3 (topo): LIVRE" in out


def test_hook_claude_code_via_stdin(monkeypatch, capsys):
    ev = {"hook_event_name": "PermissionRequest", "session_id": "abc"}
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(ev)))
    assert cli.main(["hook", "claude-code"]) == 0
    assert capsys.readouterr().out == ""  # stdout vazio (UserPromptSubmit trataria texto como contexto)
    assert store.read()["ai"]["claude-code/abc"]["state"] == int(State.IA_ATENCAO)
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"hook_event_name": "SessionEnd", "session_id": "abc"})))
    cli.main(["hook", "claude-code"])
    assert "claude-code/abc" not in store.read()["ai"]


def test_hook_never_fails(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO("isso não é json"))
    assert cli.main(["hook", "codex"]) == 0
    assert capsys.readouterr().out == "{}"


def test_manual_with_duration():
    cli.main(["sala", "ocupado", "--por", "30m"])
    m = store.read()["manual"]
    assert m["state"] == int(State.SALA_OCUPADO) and 1790 < m["until"] - time.time() <= 1800
    cli.main(["sala", "auto"])
    assert store.read()["manual"] is None


def test_toggle():
    cli.main(["toggle"])
    assert store.read()["manual"]["state"] == int(State.SALA_OCUPADO)
    cli.main(["toggle"])
    assert store.read()["manual"] is None


def _req(port, path, token, body=None, host=None):
    r = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=None if body is None else json.dumps(body).encode(),
                               headers={"X-Signa-Token": token, "Content-Type": "application/json"})
    if host:
        r.add_unredirected_header("Host", host)
    try:
        with urllib.request.urlopen(r, timeout=2) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code


def test_local_server_auth_and_sources():
    tok = config.local_token()
    srv = serve(0, tok, lambda: {})
    port = srv.server_address[1]
    srv.RequestHandlerClass = __import__("signa.server", fromlist=["x"]).make_handler(tok, port, lambda: {})
    try:
        assert _req(port, "/v1/ai", "errado", {"source": "chatgpt-web", "state": "processando"}) == 403
        assert _req(port, "/v1/ai", tok, {"source": "chatgpt-web", "state": "processando"}, host="evil.com:80") == 403
        assert _req(port, "/v1/ai", tok, {"source": "claude-code", "state": "erro"}) == 400  # só fontes web
        assert _req(port, "/v1/ai", tok, {"source": "chatgpt-web", "state": "ocupado"}) == 400  # só estados de IA
        assert _req(port, "/v1/ai", tok, {"source": "grok-web", "session": "tab-1", "state": "limite-semanal"}) == 200
        assert store.read()["ai"]["grok-web/tab-1"]["state"] == int(State.IA_LIMITE_SEMANAL)
        assert _req(port, "/v1/ai", tok, {"source": "grok-web", "session": "tab-1", "state": "remove"}) == 200
        assert "grok-web/tab-1" not in store.read()["ai"]
    finally:
        srv.shutdown()


def test_default_config_parses():
    c = config.load()
    assert c.get("sala", "lead_minutes") == 5 and c.get("mode", "ai_enabled") is False
