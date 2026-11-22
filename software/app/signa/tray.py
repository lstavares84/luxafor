"""Ícone na bandeja (opcional, extra [tray]: pystray + Pillow). O daemon roda numa thread."""
from __future__ import annotations

import threading

from . import store
from .daemon import Daemon
from .states import State, look


def run_tray(cfg, sim: bool = False):
    import pystray  # type: ignore
    from PIL import Image, ImageDraw  # type: ignore

    dmn = Daemon(cfg, backend="sim" if sim else None)
    threading.Thread(target=dmn.run, daemon=True, name="signa-daemon").start()

    def icon_for(st: State):
        img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        ImageDraw.Draw(img).ellipse((8, 8, 56, 56), fill=look(st).rgb + (255,))
        return img

    def setter(st):
        return lambda icon, item: store.set_manual(st)

    def mode(display, ia):
        return lambda icon, item: store.set_mode(display, ia)

    menu = pystray.Menu(
        pystray.MenuItem("Ocupado (manual)", setter(State.SALA_OCUPADO)),
        pystray.MenuItem("Livre (manual)", setter(State.SALA_LIVRE)),
        pystray.MenuItem("Automático (agenda)", setter(None)),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Modo sala", mode("sala", False)),
        pystray.MenuItem("Modo misto (sala + IA)", mode("misto", True)),
        pystray.MenuItem("Modo escada", mode("escada", True)),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Sair", lambda icon, item: icon.stop()),
    )
    icon = pystray.Icon("signa", icon_for(State.SALA_LIVRE), "SIGNA", menu)

    def refresh():
        while True:
            d = dmn.decision
            if d:
                icon.icon = icon_for(d.leds()[2])
                icon.title = "SIGNA: " + " / ".join(look(s).name for s in d.leds()[::-1])
            threading.Event().wait(1.0)

    threading.Thread(target=refresh, daemon=True).start()
    icon.run()
