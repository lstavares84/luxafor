#!/usr/bin/env python3
"""Envia um comando cru e registra eventos IN com timestamp (usado para mapear animações).

Uso: tools/anim.py <hex hex ...>    ex.: tools/anim.py 06 03 01
Variáveis: T=segundos de escuta (padrão 15), DELAY=espera antes de enviar (padrão 5).
"""
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from luxafor import Luxafor  # noqa: E402

lx = Luxafor()
lx.off()
time.sleep(float(os.environ.get("DELAY", "5")))
t0 = time.time()
print("RX", [p.hex(" ") for p in lx.send([int(x, 16) for x in sys.argv[1:]], 0)])
end = t0 + float(os.environ.get("T", "15"))
while time.time() < end:
    for p in lx.read(0.05):
        print("%.2fs" % (time.time() - t0), p.hex(" "), flush=True)
