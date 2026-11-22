#!/usr/bin/env python3
"""Modelos 3D (STEP) dos componentes sem modelo no pacote do KiCad 9 do Debian.

Coordenadas do modelo KiCad: origem = origem do footprint, X igual, Y = -Y do footprint,
Z para cima a partir da face da placa. Cotas dos datasheets em docs/ds:
  J1  HRO TYPE-C-31-M-12: carcaça 8,94 x 7,30 x 3,26; boca USB-C 8,34 x 2,56 (spec USB-C),
      língua 6,69 x 0,70; boca no y_fp = +3,65 (borda da placa).
  D*  WS2816B-2020: 2,2 x 2,0 x 0,84 (C4154877, "2.2mm*2.0mm*0.84mm").
  U1  UFQFPN28 4 x 4 x 0,55 (DS14693, Table 71).
  S1  ALPS SKRTLAE010: corpo 4,5 x 2,56 x 3,3, haste Ø2 com eixo a 1,7 mm, avanço 0,84 (C110293).
"""
import os
from build123d import *

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib", "3d")
os.makedirs(OUT, exist_ok=True)
STEEL = Color(0.78, 0.78, 0.80)
BLACK = Color(0.08, 0.08, 0.09)
WHITE = Color(0.96, 0.96, 0.94)
GOLD = Color(0.85, 0.68, 0.30)


def stadium(w, h, l):
    """Prisma de seção estádio (USB-C) ao longo de -Y, começando em Y=0."""
    s = Plane.XZ * SlotOverall(w, h)
    return extrude(s, amount=l)          # Plane.XZ normal = -Y -> extrude vai para +Y? (verificado abaixo)


def save(parts, name):
    c = Compound(children=parts, label=name)
    export_step(c, os.path.join(OUT, name + ".step"))
    print("ok", name, [round(v, 2) for v in (c.bounding_box().min.X, c.bounding_box().max.X,
                                          c.bounding_box().min.Y, c.bounding_box().max.Y,
                                          c.bounding_box().min.Z, c.bounding_box().max.Z)])


# ---------------- J1 HRO TYPE-C-31-M-12 ----------------
W, L, HT = 8.94, 7.30, 3.26
ZC = HT / 2
YM = -3.65                                   # boca (modelo)
shell = Pos(0, 0, ZC) * Box(W, L, HT)
shell = fillet(shell.edges().filter_by(Axis.Y), 1.2)
CAV_D = 6.60                                 # profundidade da cavidade a partir da boca
cav = Pos(0, YM + CAV_D / 2 - 0.01, ZC) * (Rot(90, 0, 0) * extrude(SlotOverall(8.34, 2.56), amount=CAV_D, both=True)).scale(1) if False else None
slot = SlotOverall(8.34, 2.56)
cav = Pos(0, YM - 0.01, ZC) * (Rot(-90, 0, 0) * extrude(slot, amount=CAV_D + 0.01))
shell = shell - cav
shell.color, shell.label = STEEL, "J1_carcaca"
tongue = Pos(0, (YM + 1.0 + YM + CAV_D) / 2, ZC) * Box(6.69, CAV_D - 1.0, 0.70)
tongue = fillet(tongue.edges().filter_by(Axis.Z).group_by(Axis.Y)[0], 0.3)
tongue.color, tongue.label = BLACK, "J1_lingua"
legs = Part()
for sx in (-1, 1):
    for y, ln in ((3.13, 2.1), (-1.05, 1.6)):
        legs += Pos(sx * 4.32, y, -0.5) * Box(0.6, ln - 0.4, 1.6)
pins = Part()
for x in (-3.25, -2.45, -1.75, -1.25, -0.75, -0.25, 0.25, 0.75, 1.25, 1.75, 2.45, 3.25):
    pins += Pos(x, 3.65 + 0.35, 0.08) * Box(0.25, 0.7, 0.16)
legs.color = pins.color = STEEL
legs.label, pins.label = "J1_pernas", "J1_terminais"
save([shell, tongue, legs, pins], "USB_C_HRO_TYPE-C-31-M-12")

# ---------------- WS2816B-2020 ----------------
body = Pos(0, 0, 0.42) * Box(2.0, 2.2, 0.84) if False else Pos(0, 0, 0.42) * Box(2.2, 2.0, 0.84)
win = Pos(0, 0, 0.84) * Cylinder(0.75, 0.30, align=(Align.CENTER, Align.CENTER, Align.MAX))
body = body - win
body.color, body.label = WHITE, "LED_corpo"
lens = Pos(0, 0, 0.84) * Cylinder(0.749, 0.30, align=(Align.CENTER, Align.CENTER, Align.MAX))
lens.color, lens.label = Color(0.95, 0.97, 1.0), "LED_lente"
pads = Part()
for x in (-0.975, 0.975):
    for y in (-0.77, 0, 0.77):
        pads += Pos(x * 1.02, y, 0.06) * Box(0.3, 0.3, 0.12)
pads.color, pads.label = GOLD, "LED_terminais"
save([body, lens, pads], "LED_WS2816B-2020")

# ---------------- UFQFPN28 4x4 ----------------
q = Pos(0, 0, 0.275) * Box(4.0, 4.0, 0.55)
q.color, q.label = BLACK, "QFN_corpo"
dot = Pos(-1.5, 1.5, 0.55) * Cylinder(0.2, 0.02, align=(Align.CENTER, Align.CENTER, Align.MIN))
dot.color, dot.label = Color(0.3, 0.3, 0.3), "QFN_pino1"
lp = Part()
for i in range(7):
    o = -1.5 + i * 0.5
    for x, y, w, h in ((-1.85, o, 0.32, 0.25), (1.85, o, 0.32, 0.25), (o, -1.85, 0.25, 0.32), (o, 1.85, 0.25, 0.32)):
        lp += Pos(x, y, 0.1) * Box(w, h, 0.2)
lp.color, lp.label = STEEL, "QFN_terminais"
save([q, dot, lp], "QFN-28_4x4_UFQFPN28")

# ---------------- ALPS SKRTLAE010 ----------------
sb = Pos(0, (1.35 - 1.21) / 2, 1.45) * Box(4.5, 2.56, 2.9)
sb.color, sb.label = WHITE, "SKRT_corpo"
top = Pos(0, (1.35 - 1.21) / 2, 3.1) * Box(4.5, 2.56, 0.4)
top.color, top.label = BLACK, "SKRT_tampa"
stem = Pos(0, -1.21, 1.7) * (Rot(90, 0, 0) * Cylinder(1.0, 0.83, align=(Align.CENTER, Align.CENTER, Align.MIN)))
stem.color, stem.label = BLACK, "SKRT_haste"
boss = Part()
for sx in (-1, 1):
    boss += Pos(sx * 2.125, 0, -0.45) * Cylinder(0.4, 0.45, align=(Align.CENTER, Align.CENTER, Align.MIN))
boss.color, boss.label = WHITE, "SKRT_guias"
tm = Part()
for x in (-1.225, 0, 1.225):
    tm += Pos(x, 1.35 + 0.25, 0.06) * Box(0.4, 0.8, 0.12)
for sx in (-1, 1):
    tm += Pos(sx * 1.85, -1.05, 0.06) * Box(1.0, 0.6, 0.12)
tm.color, tm.label = STEEL, "SKRT_terminais"
save([sb, top, stem, boss, tm], "SW_SKRTLAE010")
