"""signa-cli — controle do SIGNA pela linha de comando (e alvo dos hooks das CLIs de IA)."""
from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import time

from . import config as cfgmod
from . import hooks, store
from .states import NAMES, State, look

AI_SOURCES = ("claude-code", "codex", "chatgpt-web", "claude-web", "grok-web", "outro")


def _dur(s: str | None) -> float | None:
    if not s:
        return None
    m = re.fullmatch(r"(\d+)\s*([smh]?)", s.strip())
    if not m:
        raise SystemExit(f"duração inválida: {s} (ex.: 30m, 2h, 90s)")
    return int(m[1]) * {"": 60, "s": 1, "m": 60, "h": 3600}[m[2]]


def cmd_ai(a):
    st = NAMES.get(a.state)
    if a.state == "limite" and a.variant == "semanal":
        st = State.IA_LIMITE_SEMANAL
    if st is None or not st.is_ia:
        raise SystemExit(f"estado de IA inválido: {a.state}")
    store.set_ai(a.source, st, a.session or "")


def _hook(fn, raw: str, out_fn=None):
    """Hooks nunca podem travar nem bloquear a CLI de IA: qualquer erro vira silêncio, exit 0."""
    try:
        ev = json.loads(raw or "{}")
        st, sid = fn(ev)
        src = "claude-code" if fn is hooks.claude_code else "codex"
        if st == hooks.REMOVE:
            store.set_ai(src, None, sid)
        elif st is not None:
            store.set_ai(src, st, sid)
        if out_fn:
            sys.stdout.write(out_fn(ev))
    except Exception as e:  # noqa: BLE001
        print(f"signa: {e}", file=sys.stderr)
        if out_fn:
            sys.stdout.write("{}")
    return 0


def cmd_hook(a):
    raw = sys.stdin.read()
    if a.tool == "claude-code":
        return _hook(hooks.claude_code, raw)
    return _hook(hooks.codex_hook, raw, hooks.codex_hook_stdout)


def cmd_notify(a):
    try:
        st, sid = hooks.codex_notify(json.loads(a.payload))
        if st is not None:
            store.set_ai("codex", st, sid)
    except Exception as e:  # noqa: BLE001
        print(f"signa: {e}", file=sys.stderr)
    return 0


def cmd_sala(a):
    if a.state == "auto":
        store.set_manual(None)
        return
    st = {"livre": State.SALA_LIVRE, "ocupado": State.SALA_OCUPADO, "prestes": State.SALA_PRESTES}[a.state]
    d = _dur(a.por)
    store.set_manual(st, time.time() + d if d else None)


def cmd_toggle(a):
    from .daemon import toggle_busy
    st = toggle_busy()
    print("ocupado (manual)" if st else "automático (agenda)")


def cmd_mode(a):
    store.set_mode(display=a.display, ai_enabled={"on": True, "off": False}.get(a.ia) if a.ia else None)


def cmd_status(a):
    from .daemon import Daemon
    cfg = cfgmod.load()
    dmn = Daemon(cfg, backend="sim")
    if a.agenda:
        dmn.cal.poll_once()
    d = dmn.step()
    raw = store.read()
    names = [look(s).name for s in d.leds()]
    print(f"LED 3 (topo): {names[2]}\nLED 2 (meio): {names[1]}\nLED 1 (baixo): {names[0]}")
    if raw.get("manual"):
        print("manual:", raw["manual"])
    for k, v in sorted(raw.get("ai", {}).items()):
        print(f"  {k}: {State(v['state']).name} há {time.time() - v['at']:.0f} s")
    if dmn.cal.errors:
        print("erros de agenda:", dmn.cal.errors)


def cmd_daemon(a):
    from .daemon import Daemon
    logging.basicConfig(level=logging.INFO if not a.quiet else logging.WARNING, format="%(asctime)s %(message)s")
    cfg = cfgmod.load()
    if a.tray:
        from .tray import run_tray
        return run_tray(cfg, a.sim)
    Daemon(cfg, backend="sim" if a.sim else None).run()


def cmd_demo(a):
    """Simulador: percorre todos os estados no terminal, sem hardware."""
    from .device import SimOut
    from .engine import Decision
    out = SimOut()
    seq = [Decision(False, s) for s in State if s != State.OFF] + [
        Decision(True, sala=State.SALA_LIVRE, ia=State.IA_PROCESSANDO),
        Decision(True, sala=State.SALA_PRESTES, ia=State.IA_ERRO),
        Decision(True, sala=State.SALA_OCUPADO, ia=State.IA_ATENCAO)]
    for d in seq:
        out.show(d)
        end = time.time() + a.segundos
        while time.time() < end:
            out.tick()
            time.sleep(0.01)
        out._line(0, newline=True) if not out.plain else None
    out.close()


def cmd_login(a):
    cfg = cfgmod.load()
    if a.service == "google":
        from . import calendar_google
        f = a.client_secrets or cfg.get("google", "client_secrets_file")
        if not f:
            raise SystemExit("defina [google].client_secrets_file no config.toml ou use --client-secrets")
        calendar_google.login(f)
    else:
        from . import calendar_outlook
        cid = cfg.get("outlook", "client_id")
        if not cid:
            raise SystemExit("defina [outlook].client_id no config.toml")
        calendar_outlook.login(cid, cfg.get("outlook", "tenant", "common"))
    print("ok: token guardado no chaveiro do sistema")


def cmd_logout(a):
    from . import secrets_store
    secrets_store.delete("google-token" if a.service == "google" else "outlook-msal-cache")


def cmd_devices(a):
    from .device import HidLink, enumerate_devices, probe_is_signa
    devs = enumerate_devices()
    if not devs:
        print("nenhum aparelho (hidapi instalado? no Linux, regra udev em docs/README.md)")
    for d in devs:
        kind = "?"
        try:
            link = HidLink(d["vid"], d["pid"], d["path"])
            kind = "SIGNA nativo" if probe_is_signa(link) else "Luxafor (protocolo compatível)"
            link.close()
        except Exception as e:  # noqa: BLE001
            kind = f"erro: {e}"
        print(f"{d['vid']:04x}:{d['pid']:04x} serial={d['serial']} -> {kind}")


def cmd_init(a):
    print("config:", cfgmod.write_default())
    print("token local:", cfgmod.config_dir() / "token.txt", "(cole na extensão)")
    cfgmod.local_token()


def main(argv=None):
    p = argparse.ArgumentParser(prog="signa-cli", description="SIGNA: luz de status (sala + IAs)")
    sp = p.add_subparsers(dest="cmd", required=True)

    s = sp.add_parser("ai", help="informa o estado de uma IA")
    s.add_argument("--source", required=True, choices=AI_SOURCES)
    s.add_argument("--state", required=True, help="desocupada|processando|atencao|erro|limite")
    s.add_argument("--variant", choices=["5h", "semanal"], default="5h")
    s.add_argument("--session", default="")
    s.set_defaults(fn=cmd_ai)

    s = sp.add_parser("hook", help="lê o JSON do hook no stdin (Claude Code / Codex)")
    s.add_argument("tool", choices=["claude-code", "codex"])
    s.set_defaults(fn=cmd_hook)

    s = sp.add_parser("notify", help="alvo do `notify` do Codex (recebe o JSON como argumento)")
    s.add_argument("tool", choices=["codex"])
    s.add_argument("payload")
    s.set_defaults(fn=cmd_notify)

    s = sp.add_parser("sala", help="estado manual da sala (vence a agenda)")
    s.add_argument("state", choices=["livre", "ocupado", "prestes", "auto"])
    s.add_argument("--por", help="duração (ex.: 30m, 2h); sem isso, até `sala auto`")
    s.set_defaults(fn=cmd_sala)

    sp.add_parser("toggle", help="alterna ocupado manual / automático (para atalho)").set_defaults(fn=cmd_toggle)

    s = sp.add_parser("modo", help="modo de exibição e IA on/off")
    s.add_argument("--display", choices=["sala", "misto", "escada"])
    s.add_argument("--ia", choices=["on", "off"])
    s.set_defaults(fn=cmd_mode)

    s = sp.add_parser("status", help="mostra o que a luz está decidindo")
    s.add_argument("--agenda", action="store_true", help="consulta a agenda agora")
    s.set_defaults(fn=cmd_status)

    s = sp.add_parser("daemon", help="roda o serviço (agenda + IAs -> luz)")
    s.add_argument("--sim", action="store_true", help="sem hardware: desenha no terminal")
    s.add_argument("--tray", action="store_true", help="ícone na bandeja (extra [tray])")
    s.add_argument("--quiet", action="store_true")
    s.set_defaults(fn=cmd_daemon)

    s = sp.add_parser("demo", help="simulador: mostra todos os estados")
    s.add_argument("--segundos", type=float, default=4.0)
    s.set_defaults(fn=cmd_demo)

    s = sp.add_parser("login", help="autoriza a agenda (token vai para o chaveiro)")
    s.add_argument("service", choices=["google", "outlook"])
    s.add_argument("--client-secrets")
    s.set_defaults(fn=cmd_login)
    s = sp.add_parser("logout")
    s.add_argument("service", choices=["google", "outlook"])
    s.set_defaults(fn=cmd_logout)

    sp.add_parser("devices", help="lista aparelhos SIGNA/Luxafor").set_defaults(fn=cmd_devices)
    sp.add_parser("init", help="cria config.toml e token local").set_defaults(fn=cmd_init)

    a = p.parse_args(argv)
    return a.fn(a) or 0


if __name__ == "__main__":
    sys.exit(main())
