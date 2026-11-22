"""Tokens OAuth no chaveiro do sistema (Windows Credential Manager, macOS Keychain, Secret Service no Linux)."""
from __future__ import annotations

SERVICE = "signa"


def get(name: str) -> str | None:
    import keyring
    return keyring.get_password(SERVICE, name)


def put(name: str, value: str) -> None:
    import keyring
    keyring.set_password(SERVICE, name, value)


def delete(name: str) -> None:
    import keyring
    from keyring.errors import PasswordDeleteError
    try:
        keyring.delete_password(SERVICE, name)
    except PasswordDeleteError:
        pass
