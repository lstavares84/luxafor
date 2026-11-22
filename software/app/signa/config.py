"""Configuração em TOML. Segredos (tokens OAuth) ficam no chaveiro do sistema (keyring), nunca aqui."""
from __future__ import annotations

import os
import secrets
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    import tomllib  # 3.11+
except ImportError:  # pragma: no cover
    import tomli as tomllib  # type: ignore

DEFAULT_TOML = """\
# SIGNA — configuração do app de desktop
[device]
backend = "auto"          # auto | signa | luxafor | sim
luxafor_render = "stream" # Luxafor original: stream (curvas pelo app, ~25 Hz) | opcodes (1 comando por estado)
brightness = 255          # 0–255 (só firmware SIGNA)

[mode]
display = "misto"         # sala | misto (LED 3+2 sala, LED 1 IA) | escada (3 LEDs = estado mais forte)
ai_enabled = false        # modo IA é opt-in

[sala]
lead_minutes = 5          # "prestes a entrar" N min antes da reunião
tentative_is_busy = true  # reunião "talvez" conta como ocupado
ignore_all_day = true     # eventos de dia inteiro não acendem nada
poll_seconds = 60

[google]
enabled = false
calendars = ["primary"]
# arquivo JSON do cliente OAuth tipo "App para computador" (Google Cloud Console). Fora do repositório.
client_secrets_file = ""

[outlook]
enabled = false
client_id = ""            # registro de app no Microsoft Entra ID (cliente público, fluxo de dispositivo)
tenant = "common"         # common | organizations | consumers | <id do tenant>

[ai]
sources = ["claude-code", "codex", "chatgpt-web", "claude-web", "grok-web"]
processing_ttl_s = 900
attention_ttl_s = 0
error_ttl_s = 600
limit_5h_ttl_s = 18000
limit_week_ttl_s = 86400

[hotkey]
toggle_busy = ""          # ex.: "<ctrl>+<alt>+b" (precisa de pynput)

[server]
port = 47623              # só 127.0.0.1; token em token.txt na pasta de config
"""


def config_dir() -> Path:
    if os.environ.get("SIGNA_HOME"):
        return Path(os.environ["SIGNA_HOME"])
    if sys.platform == "win32":
        return Path(os.environ.get("APPDATA", Path.home())) / "signa"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "signa"
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "signa"


@dataclass
class Config:
    raw: dict = field(default_factory=dict)
    path: Path | None = None

    def get(self, section: str, key: str, default=None):
        return self.raw.get(section, {}).get(key, default)


def load(path: Path | None = None) -> Config:
    path = path or config_dir() / "config.toml"
    base = tomllib.loads(DEFAULT_TOML)
    if path.exists():
        user = tomllib.loads(path.read_text(encoding="utf-8"))
        for sec, vals in user.items():
            base.setdefault(sec, {}).update(vals)
    return Config(base, path)


def write_default(path: Path | None = None) -> Path:
    path = path or config_dir() / "config.toml"
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(DEFAULT_TOML, encoding="utf-8")
    return path


def local_token() -> str:
    """Token compartilhado entre daemon, CLI e extensão (só protege a porta local de outros sites)."""
    p = config_dir() / "token.txt"
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(secrets.token_urlsafe(24), encoding="utf-8")
        try:
            os.chmod(p, 0o600)
        except OSError:
            pass
    return p.read_text(encoding="utf-8").strip()


def policy_from(cfg: Config):
    from .engine import Policy
    a = cfg.raw.get("ai", {})
    return Policy(display=cfg.get("mode", "display", "misto"), ai_enabled=bool(cfg.get("mode", "ai_enabled", False)),
                  processing_ttl_s=a.get("processing_ttl_s", 900), attention_ttl_s=a.get("attention_ttl_s", 0),
                  error_ttl_s=a.get("error_ttl_s", 600), limit_5h_ttl_s=a.get("limit_5h_ttl_s", 18000),
                  limit_week_ttl_s=a.get("limit_week_ttl_s", 86400), ai_sources=tuple(a.get("sources", ())))
