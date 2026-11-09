#!/usr/bin/env python3
"""Caderno conceitual "Metrologia Luminosa": 6 lâminas A3 do indicador rev A.

Lê a geometria real da placa (hardware/indicador/indicador.kicad_pcb) via pcbnew
e desenha tudo em mm com reportlab. Saída: docs/conceito/indicador-conceito.pdf
"""
import math
import os

import pcbnew
from reportlab.lib.colors import Color, HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PCB = os.path.join(ROOT, "hardware", "indicador", "indicador.kicad_pcb")
OUT = os.path.join(HERE, "indicador-conceito.pdf")
FONTS = ("/home/lstavares84/.claude/plugins/cache/anthropic-agent-skills/"
         "example-skills/2c5958ecac7c/skills/canvas-design/canvas-fonts/")

MMPT = 72 / 25.4
PW, PH = 420.0, 297.0
M = 16.0                                   # margem externa
TOTAL = 11                                 # lâminas no caderno

for name, f in [("Jura", "Jura-Light.ttf"), ("JuraM", "Jura-Medium.ttf"),
                ("Mono", "GeistMono-Regular.ttf"), ("Serif", "InstrumentSerif-Italic.ttf"),
                ("Sans", "WorkSans-Regular.ttf")]:
    pdfmetrics.registerFont(TTFont(name, FONTS + f))

PAPER = HexColor("#EEEAE2")
INK = HexColor("#1B1E21")
INK2 = HexColor("#5A5F64")
INK3 = HexColor("#A9A79F")
INK4 = HexColor("#D6D2C8")
NIGHT = HexColor("#090C11")
NIGHT2 = HexColor("#161B22")
NIGHT3 = HexColor("#2A313B")
MOON = HexColor("#C9CDD3")

STATES = [  # nome, cor, forma da onda
    ("LIVRE", HexColor("#2FD28A"), "steady_low"),
    ("PROCESSANDO", HexColor("#3D8BFF"), "breathe"),
    ("ATENÇÃO", HexColor("#FFB21E"), "blink"),
    ("ERRO", HexColor("#FF3FC8"), "strobe"),
    ("EM REUNIÃO", HexColor("#FF3B2F"), "steady_high"),
]

# placa: máscara preta fosca, acabamento ENIG
MASK = HexColor("#121417")
MASK_TRK = HexColor("#22262B")
GOLD = HexColor("#C8A35A")
GOLD_D = HexColor("#8E7135")
EPOXY = HexColor("#26282B")
CERAM = HexColor("#BFA57E")
SHELL = HexColor("#B9BCC0")
LEDW = HexColor("#F3F0E8")

# ---------------------------------------------------------------- produto (mm)
BODY_W, BODY_H, BODY_D = 12.0, 48.0, 15.0          # X, Y, Z
FLAG_X0, FLAG_X1 = 12.0, 34.0
FLAG_Y0, FLAG_Y1 = 2.0, 21.0                        # a partir do topo
FLAG_T = 2.5                                        # espessura (Z)
BOARD_TOP = 2.0                                     # placa começa 2 mm abaixo do topo
BOARD_FACE_X = 4.4                                  # face dos LEDs (X)
LED_Y = [3.0, 10.0, 17.0]                           # na placa (topo = 0)


# ================================================================== utilidades
def new_page(c, dark=False):
    c.scale(MMPT, MMPT)
    c.setFillColor(NIGHT if dark else PAPER)
    c.rect(0, 0, PW, PH, stroke=0, fill=1)


def text(c, x, y, s, font="Mono", size=2.3, color=INK, anchor="l", spacing=0):
    c.setFillColor(color)
    if spacing:
        w = pdfmetrics.stringWidth(s, font, size) + spacing * (len(s) - 1)
        x0 = x - (w if anchor == "r" else w / 2 if anchor == "c" else 0)
        c.setFont(font, size)
        for ch in s:
            c.drawString(x0, y, ch)
            x0 += pdfmetrics.stringWidth(ch, font, size) + spacing
        return w
    c.setFont(font, size)
    {"l": c.drawString, "r": c.drawRightString, "c": c.drawCentredString}[anchor](x, y, s)
    return pdfmetrics.stringWidth(s, font, size)


def line(c, x1, y1, x2, y2, w=0.12, color=INK, dash=None):
    c.setStrokeColor(color)
    c.setLineWidth(w)
    c.setDash(*dash) if dash else c.setDash()
    c.line(x1, y1, x2, y2)
    c.setDash()


def arrow_head(c, x, y, ang, color=INK, s=1.4):
    c.setFillColor(color)
    p = c.beginPath()
    p.moveTo(x, y)
    for da in (-0.28, 0.28):
        p.lineTo(x - s * math.cos(ang + da), y - s * math.sin(ang + da))
    p.close()
    c.drawPath(p, stroke=0, fill=1)


def dim(c, x1, y1, x2, y2, label, off=6.0, color=INK, size=2.4, ext=True):
    """Cota com linhas de chamada; off positivo = à esquerda do vetor 1->2."""
    ang = math.atan2(y2 - y1, x2 - x1)
    nx, ny = -math.sin(ang), math.cos(ang)
    a = (x1 + nx * off, y1 + ny * off)
    b = (x2 + nx * off, y2 + ny * off)
    if ext:
        sg = 1 if off > 0 else -1
        line(c, x1 + nx * 1.2 * sg, y1 + ny * 1.2 * sg, a[0] + nx * 1.5 * sg, a[1] + ny * 1.5 * sg, 0.08, color)
        line(c, x2 + nx * 1.2 * sg, y2 + ny * 1.2 * sg, b[0] + nx * 1.5 * sg, b[1] + ny * 1.5 * sg, 0.08, color)
    line(c, a[0], a[1], b[0], b[1], 0.1, color)
    arrow_head(c, b[0], b[1], ang, color)
    arrow_head(c, a[0], a[1], ang + math.pi, color)
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    c.saveState()
    c.translate(mx, my)
    rot = math.degrees(ang)
    if rot > 90 or rot <= -90:
        rot += 180
    c.rotate(rot)
    w = pdfmetrics.stringWidth(label, "Mono", size)
    bg = c._fillColorObj if False else None
    text(c, 0, 0.9, label, "Mono", size, color, "c")
    c.restoreState()
    return w


def rrect(c, x, y, w, h, r, stroke=INK, fill=None, lw=0.15, dash=None):
    c.setLineWidth(lw)
    c.setStrokeColor(stroke if stroke else INK)
    c.setDash(*dash) if dash else c.setDash()
    if fill is not None:
        c.setFillColor(fill)
    c.roundRect(x, y, w, h, r, stroke=1 if stroke else 0, fill=1 if fill is not None else 0)
    c.setDash()


def glow(c, x, y, r, color, steps=46, peak=0.5):
    c.saveState()
    c.setFillColor(color)
    for i in range(steps):
        t = i / (steps - 1)
        rr = r * (1 - t) + 0.2
        c.setFillAlpha(peak * (1.0 / steps) * (1.6 + 3 * t * t))
        c.circle(x, y, rr, stroke=0, fill=1)
    c.restoreState()


def dot_grid(c, x0, y0, x1, y1, step, color, r=0.12):
    c.setFillColor(color)
    y = y0
    while y <= y1 + 1e-6:
        x = x0
        while x <= x1 + 1e-6:
            c.circle(x, y, r, stroke=0, fill=1)
            x += step
        y += step


def frame(c, n, title, dark=False):
    """Marcas de registro, régua superior, fólio. Mesmo esqueleto em todas as lâminas."""
    ink = MOON if dark else INK
    faint = NIGHT3 if dark else INK4
    mid = HexColor("#5C6670") if dark else INK3
    L = 5.0
    for cx, cy, sx, sy in [(M, PH - M, 1, -1), (PW - M, PH - M, -1, -1), (M, M, 1, 1), (PW - M, M, -1, 1)]:
        line(c, cx, cy, cx + L * sx, cy, 0.12, ink)
        line(c, cx, cy, cx, cy + L * sy, 0.12, ink)
    # régua superior (1 mm de subdivisão a cada 10 mm marcados)
    y = PH - M + 4.5
    for i in range(0, int(PW - 2 * M - 30) + 1):
        x = M + 15 + i
        h = 1.6 if i % 10 == 0 else 0.8 if i % 5 == 0 else 0.4
        line(c, x, y, x, y + h, 0.06, faint if i % 10 else mid)
    text(c, M, M - 7.0, f"{n:02d} / {TOTAL:02d}", "Mono", 2.2, ink)
    text(c, PW / 2, M - 7.0, "INDICADOR · REV A · CADERNO CONCEITUAL", "JuraM", 2.0, mid, "c", spacing=0.9)
    text(c, PW - M, M - 7.0, title, "Mono", 2.2, ink, "r")


# ================================================================== produto 2D
def product_front(c, ox, oy, s, glow_color=None, stroke=INK, fill=None, lw=0.2, hidden=None, show_board=False,
                  spot=None, spot_r=5.0):
    """Vista frontal (X × Y). (ox, oy) = canto inferior esquerdo do corpo."""
    H = BODY_H * s
    # bandeira
    fx0, fx1 = ox + FLAG_X0 * s - 0.4 * s, ox + FLAG_X1 * s
    fy1, fy0 = oy + H - FLAG_Y0 * s, oy + H - FLAG_Y1 * s
    if glow_color is not None:
        lit_flag(c, fx0, fy0, fx1 - fx0, fy1 - fy0, 1.6 * s, glow_color, ox, oy, s)
    if spot is not None:
        c.saveState()
        cp = c.beginPath()
        cp.roundRect(fx0, fy0, fx1 - fx0, fy1 - fy0, 1.6 * s)
        c.clipPath(cp, stroke=0, fill=0)
        for ly in LED_Y:
            glow(c, ox + FLAG_X0 * s, oy + H - (BOARD_TOP + ly) * s, spot_r * s, spot, peak=0.65)
        c.restoreState()
    rrect(c, fx0, fy0, fx1 - fx0, fy1 - fy0, 1.6 * s, stroke, None if glow_color is not None else fill, lw)
    # corpo (desenhado por cima da raiz da bandeira)
    rrect(c, ox, oy, BODY_W * s, H, 1.6 * s, stroke, fill if fill is not None else (NIGHT if glow_color is not None else PAPER), lw)
    if show_board:
        hc = hidden or INK3
        bx = ox + (BOARD_FACE_X - 0.8) * s
        by1 = oy + H - BOARD_TOP * s
        rrect(c, bx, by1 - 44 * s, 0.8 * s, 44 * s, 0, hc, None, 0.1, dash=(1.2, 0.8))
        for ly in LED_Y:
            yy = by1 - ly * s
            c.setStrokeColor(hc)
            c.setLineWidth(0.1)
            c.rect(bx + 0.8 * s, yy - 1.0 * s, 0.65 * s, 2.0 * s, stroke=1, fill=0)
        # USB-C
        rrect(c, ox + (BOARD_FACE_X) * s, oy - 0.0 * s, 3.26 * s, 7.35 * s, 0.5 * s, hc, None, 0.1, dash=(1.2, 0.8))
        # raiz da bandeira dentro do corpo
        line(c, ox + (BOARD_FACE_X + 0.75) * s, fy1 - 0.5 * s, ox + (BOARD_FACE_X + 0.75) * s, fy0 + 0.5 * s, 0.1, hc, (1.2, 0.8))


def lit_flag(c, x, y, w, h, r, col, ox, oy, s):
    c.saveState()
    p = c.beginPath()
    p.roundRect(x, y, w, h, r)
    c.clipPath(p, stroke=0, fill=0)
    c.setFillColor(NIGHT)
    c.rect(x, y, w, h, stroke=0, fill=1)
    hi = Color(min(1, col.red * 0.35 + 0.65), min(1, col.green * 0.35 + 0.65), min(1, col.blue * 0.35 + 0.65))
    c.linearGradient(x, 0, x + w, 0, [hi, col, Color(col.red * 0.55, col.green * 0.55, col.blue * 0.55)],
                     [0, 0.22, 1], extend=True)
    c.restoreState()


def flag_halo(c, ox, oy, s, col, strength=1.0):
    H = BODY_H * s
    cx = ox + (FLAG_X0 + FLAG_X1) / 2 * s
    cy = oy + H - (FLAG_Y0 + FLAG_Y1) / 2 * s
    glow(c, cx, cy, 20 * s, col, peak=0.6 * strength)
    glow(c, ox + FLAG_X0 * s, cy, 14 * s, col, peak=0.45 * strength)


def product_side(c, ox, oy, s, stroke=INK, lw=0.2, show_hidden=True):
    """Vista lateral esquerda (Z × Y)."""
    H = BODY_H * s
    rrect(c, ox, oy, BODY_D * s, H, 1.6 * s, stroke, PAPER, lw)
    if show_hidden:
        cz = ox + BODY_D / 2 * s
        line(c, cz, oy + H - FLAG_Y0 * s, cz, oy + H - FLAG_Y1 * s, 0.1, INK3, (1.2, 0.8))
        for dz in (-FLAG_T / 2, FLAG_T / 2):
            line(c, cz + dz * s, oy + H - FLAG_Y0 * s, cz + dz * s, oy + H - FLAG_Y1 * s, 0.1, INK3, (1.2, 0.8))
        rrect(c, cz - 4.47 * s, oy, 8.94 * s, 7.35 * s, 0.5 * s, INK3, None, 0.1, dash=(1.2, 0.8))
        rrect(c, cz - 5.5 * s, oy + H - (BOARD_TOP + 44) * s, 11 * s, 44 * s, 1 * s, INK3, None, 0.1, dash=(1.2, 0.8))


def product_top(c, ox, oy, s, stroke=INK, lw=0.2):
    """Vista superior (X × Z), primeiro diedro: abaixo da frontal."""
    cz = oy + BODY_D / 2 * s
    rrect(c, ox + FLAG_X0 * s - 0.4 * s, cz - FLAG_T / 2 * s, (FLAG_X1 - FLAG_X0 + 0.4) * s, FLAG_T * s, 0.6 * s, stroke, PAPER, lw)
    rrect(c, ox, oy, BODY_W * s, BODY_D * s, 1.6 * s, stroke, PAPER, lw)


# ================================================================== isometria
COS30, SIN30 = math.cos(math.pi / 6), 0.5


def iso(ox, oy, s, x, y, z):
    return ox + (x - z) * COS30 * s, oy + (y - (x + z) * SIN30) * s


def iso_box(c, ox, oy, s, x0, y0, z0, dx, dy, dz, fills, stroke, lw=0.18):
    P = lambda x, y, z: iso(ox, oy, s, x, y, z)
    faces = [  # +y (topo), +z (frente), +x (direita)
        [(x0, y0 + dy, z0), (x0 + dx, y0 + dy, z0), (x0 + dx, y0 + dy, z0 + dz), (x0, y0 + dy, z0 + dz)],
        [(x0, y0, z0 + dz), (x0 + dx, y0, z0 + dz), (x0 + dx, y0 + dy, z0 + dz), (x0, y0 + dy, z0 + dz)],
        [(x0 + dx, y0, z0), (x0 + dx, y0, z0 + dz), (x0 + dx, y0 + dy, z0 + dz), (x0 + dx, y0 + dy, z0)],
    ]
    for f, col in zip(faces, fills):
        p = c.beginPath()
        pts = [P(*v) for v in f]
        p.moveTo(*pts[0])
        for q in pts[1:]:
            p.lineTo(*q)
        p.close()
        if col is not None:
            c.setFillColor(col)
        c.setStrokeColor(stroke)
        c.setLineWidth(lw)
        c.drawPath(p, stroke=1, fill=1 if col is not None else 0)


def product_iso(c, ox, oy, s, dark=False, col=None):
    """Isometria: Y para cima; corpo na origem, bandeira em +X."""
    if dark:
        body = [NIGHT3, NIGHT2, HexColor("#1E242C")]
        st = HexColor("#56606B")
    else:
        body = [HexColor("#F7F4EE"), HexColor("#E3DED4"), HexColor("#D2CCC0")]
        st = INK
    iso_box(c, ox, oy, s, 0, 0, 0, BODY_W, BODY_H, BODY_D, body, st)
    fz = BODY_D / 2 - FLAG_T / 2
    fy0 = BODY_H - FLAG_Y1
    if col is None:
        ff = [HexColor("#FBFAF7"), HexColor("#EFECE6"), HexColor("#E6E2DA")] if not dark else body
    else:
        ff = [Color(min(1, col.red * .5 + .5), min(1, col.green * .5 + .5), min(1, col.blue * .5 + .5)),
              col, Color(col.red * .7, col.green * .7, col.blue * .7)]
    iso_box(c, ox, oy, s, BODY_W, fy0, fz, FLAG_X1 - FLAG_X0, FLAG_Y1 - FLAG_Y0, FLAG_T, ff,
            st if col is None else Color(col.red * .5, col.green * .5, col.blue * .5))
    # boca do USB-C na face inferior não aparece; marca a fresta da junta corpo/tampa
    a = iso(ox, oy, s, 0, 6, BODY_D)
    b = iso(ox, oy, s, BODY_W, 6, BODY_D)
    line(c, a[0], a[1], b[0], b[1], 0.08, st)
    b2 = iso(ox, oy, s, BODY_W, 6, 0)
    line(c, b[0], b[1], b2[0], b2[1], 0.08, st)


# ================================================================== placa
def load_pcb():
    B = pcbnew.LoadBoard(PCB)
    to = lambda v: pcbnew.ToMM(v)
    pads, tracks, vias, fps = [], [], [], []
    for fp in B.GetFootprints():
        fps.append(dict(ref=fp.GetReference(), val=fp.GetValue(), fpid=str(fp.GetFPID().GetLibItemName()),
                        x=to(fp.GetPosition().x) - 100, y=to(fp.GetPosition().y) - 100,
                        rot=fp.GetOrientationDegrees(), back=fp.IsFlipped()))
        for p in fp.Pads():
            ls = p.GetLayerSet()
            pads.append(dict(ref=fp.GetReference(), x=to(p.GetPosition().x) - 100, y=to(p.GetPosition().y) - 100,
                             w=to(p.GetSizeX()), h=to(p.GetSizeY()), rot=p.GetOrientationDegrees(),
                             shape=int(p.GetShape()), drill=to(p.GetDrillSizeX()), dh=to(p.GetDrillSizeY()),
                             F=ls.Contains(pcbnew.F_Cu), B=ls.Contains(pcbnew.B_Cu)))
    for t in B.GetTracks():
        if t.GetClass() == "PCB_VIA":
            vias.append(dict(x=to(t.GetPosition().x) - 100, y=to(t.GetPosition().y) - 100,
                             d=to(t.GetWidth(pcbnew.F_Cu)), drill=to(t.GetDrillValue())))
        else:
            tracks.append(dict(x1=to(t.GetStart().x) - 100, y1=to(t.GetStart().y) - 100,
                               x2=to(t.GetEnd().x) - 100, y2=to(t.GetEnd().y) - 100,
                               w=to(t.GetWidth()), L="F" if t.GetLayer() == pcbnew.F_Cu else "B"))
    return dict(pads=pads, tracks=tracks, vias=vias, fps=fps)


BW, BH = 11.0, 44.0
# corpo de cada encapsulamento: (largura X, altura Y no footprint sem rotação, altura Z, cor)
BODIES = {
    "TSSOP-20_4.4x6.5mm_P0.65mm": (4.4, 6.5, 1.2, EPOXY),
    "SOT-23-5": (1.6, 2.9, 1.1, EPOXY),
    "SOT-23-6": (1.6, 2.9, 1.1, EPOXY),
    "SOT-353_SC-70-5": (1.25, 2.0, 1.0, EPOXY),
    "LED_SK6805-EC20_2.0x2.0mm": (2.0, 2.0, 0.65, LEDW),
    "C_0402_1005Metric": (1.0, 0.5, 0.5, CERAM),
    "R_0402_1005Metric": (1.0, 0.5, 0.35, EPOXY),
    "C_0603_1608Metric": (1.6, 0.8, 0.8, CERAM),
    "USB_C_Receptacle_HRO_TYPE-C-31-M-12": (8.94, 7.35, 3.26, SHELL),
}


class BoardView:
    def __init__(self, c, ox, oy, s, mirror=False):
        self.c, self.ox, self.oy, self.s, self.mirror = c, ox, oy, s, mirror

    def P(self, x, y):
        if self.mirror:
            x = BW - x
        return self.ox + x * self.s, self.oy + (BH - y) * self.s


def rot_rect_path(c, cx, cy, w, h, ang_deg, r=0.0):
    a = math.radians(ang_deg)
    ca, sa = math.cos(a), math.sin(a)
    c.saveState()
    c.translate(cx, cy)
    c.rotate(ang_deg)
    return ca, sa


def draw_board(c, bv, pcb, side="F", detail=True, label_layer=None):
    s = bv.s
    x0, y0 = bv.P(0, BH)
    if bv.mirror:
        x0 = bv.ox
    # sombra muito discreta
    c.saveState()
    c.setFillColor(INK)
    c.setFillAlpha(0.07)
    c.roundRect(bv.ox + 0.9, bv.oy - 0.9, BW * s, BH * s, 1.0 * s, stroke=0, fill=1)
    c.restoreState()
    # substrato + máscara
    c.setFillColor(MASK)
    c.roundRect(bv.ox, bv.oy, BW * s, BH * s, 1.0 * s, stroke=0, fill=1)
    c.saveState()
    pth = c.beginPath()
    pth.roundRect(bv.ox, bv.oy, BW * s, BH * s, 1.0 * s)
    c.clipPath(pth, stroke=0, fill=0)
    # trilhas sob a máscara
    c.setLineCap(1)
    c.setStrokeColor(MASK_TRK)
    for t in pcb["tracks"]:
        if t["L"] != side:
            continue
        a, b = bv.P(t["x1"], t["y1"]), bv.P(t["x2"], t["y2"])
        c.setLineWidth(t["w"] * s)
        c.line(a[0], a[1], b[0], b[1])
    # contorno sutil das trilhas
    c.setLineCap(0)
    c.restoreState()
    # pads (ENIG)
    for p in pcb["pads"]:
        on = p["F"] if side == "F" else p["B"]
        if not on:
            continue
        cx, cy = bv.P(p["x"], p["y"])
        rot = p["rot"] * (-1 if bv.mirror else 1)
        c.saveState()
        c.translate(cx, cy)
        c.rotate(rot)
        c.setFillColor(GOLD)
        w, h = p["w"] * s, p["h"] * s
        if p["shape"] == 0:
            c.circle(0, 0, w / 2, stroke=0, fill=1)
        elif p["shape"] == 2:
            r = min(w, h) / 2
            c.roundRect(-w / 2, -h / 2, w, h, r, stroke=0, fill=1)
        elif p["shape"] == 4:
            c.roundRect(-w / 2, -h / 2, w, h, min(w, h) * 0.25, stroke=0, fill=1)
        else:
            c.rect(-w / 2, -h / 2, w, h, stroke=0, fill=1)
        if p["drill"] > 0:
            c.setFillColor(PAPER)
            dw, dh = p["drill"] * s, (p["dh"] or p["drill"]) * s
            c.roundRect(-dw / 2, -dh / 2, dw, dh, min(dw, dh) / 2, stroke=0, fill=1)
        c.restoreState()
    for v in pcb["vias"]:
        cx, cy = bv.P(v["x"], v["y"])
        c.setFillColor(GOLD_D)
        c.circle(cx, cy, v["d"] / 2 * s, stroke=0, fill=1)
        c.setFillColor(PAPER)
        c.circle(cx, cy, v["drill"] / 2 * s, stroke=0, fill=1)
    if side == "F" and detail:
        for fp in pcb["fps"]:
            body = BODIES.get(fp["fpid"])
            if not body or fp["back"]:
                continue
            draw_body(c, bv, fp, body)
    if side == "B":
        # serigrafia de identificação (espelhada na vista por baixo = legível)
        cx, cy = bv.P(BW / 2, 21.6)
        text(c, cx, cy, "IND rev A", "Mono", 0.75 * s, HexColor("#E9E6DF"), "c")
        for fp in pcb["fps"]:
            if fp["back"]:
                px, py = bv.P(fp["x"], fp["y"])
                c.setStrokeColor(HexColor("#E9E6DF"))
                c.setLineWidth(0.12 * s)
                c.circle(px, py, 0.82 * s, stroke=1, fill=0)
    # borda fina
    c.setStrokeColor(INK)
    c.setLineWidth(0.12)
    c.roundRect(bv.ox, bv.oy, BW * s, BH * s, 1.0 * s, stroke=1, fill=0)


def draw_body(c, bv, fp, body):
    s = bv.s
    w, h, _z, col = body
    cx, cy = bv.P(fp["x"], fp["y"])
    c.saveState()
    c.translate(cx, cy)
    c.rotate(fp["rot"])
    W, H = w * s, h * s
    name = fp["fpid"]
    if name.startswith("USB"):
        clip = c.beginPath()
        clip.rect(-W / 2, -H / 2, W, H)
        c.clipPath(clip, stroke=0, fill=0)
        c.linearGradient(-W / 2, 0, W / 2, 0, [HexColor("#8F9398"), HexColor("#E2E4E6"), HexColor("#A5A9AE")],
                         [0, 0.45, 1], extend=False)
        c.setStrokeColor(HexColor("#6E7378"))
        c.setLineWidth(0.1)
        c.rect(-W / 2, -H / 2 + 0.3 * s, W, H - 0.6 * s, stroke=1, fill=0)
        c.setStrokeColor(HexColor("#8A8E93"))
        c.setLineWidth(0.06)
        for k in range(1, 6):
            yy = -H / 2 + 0.3 * s + k * (H - 0.6 * s) / 6
            c.line(-W / 2 + 0.6 * s, yy, W / 2 - 0.6 * s, yy)
    elif name.startswith("LED"):
        c.setFillColor(LEDW)
        c.rect(-W / 2, -H / 2, W, H, stroke=0, fill=1)
        c.setFillColor(HexColor("#E4DFD4"))
        c.rect(-W / 2 + 0.18 * s, -H / 2 + 0.18 * s, W - 0.36 * s, H - 0.36 * s, stroke=0, fill=1)
        # três chips (R, G, B) sob o difusor
        for i, cc in enumerate(("#E0584F", "#4FB37A", "#4F7FE0")):
            c.setFillColor(HexColor(cc))
            c.rect((-0.55 + i * 0.4) * s, -0.12 * s, 0.24 * s, 0.24 * s, stroke=0, fill=1)
        c.setFillColor(HexColor("#2A2C2F"))
        c.rect(-0.75 * s, -0.75 * s, 0.38 * s, 0.38 * s, stroke=0, fill=1)
    elif col is CERAM:
        c.setFillColor(col)
        c.rect(-W / 2, -H / 2, W, H, stroke=0, fill=1)
        c.setFillColor(HexColor("#D9D6CF"))
        e = W * 0.22
        c.rect(-W / 2, -H / 2, e, H, stroke=0, fill=1)
        c.rect(W / 2 - e, -H / 2, e, H, stroke=0, fill=1)
    elif name.startswith("R_"):
        c.setFillColor(EPOXY)
        c.rect(-W / 2, -H / 2, W, H, stroke=0, fill=1)
        c.setFillColor(HexColor("#D9D6CF"))
        e = W * 0.2
        c.rect(-W / 2, -H / 2, e, H, stroke=0, fill=1)
        c.rect(W / 2 - e, -H / 2, e, H, stroke=0, fill=1)
    else:
        c.setFillColor(col)
        c.rect(-W / 2, -H / 2, W, H, stroke=0, fill=1)
        c.setStrokeColor(HexColor("#3A3D41"))
        c.setLineWidth(0.08)
        c.rect(-W / 2 + 0.12 * s, -H / 2 + 0.12 * s, W - 0.24 * s, H - 0.24 * s, stroke=1, fill=0)
        c.setFillColor(HexColor("#4A4D52"))
        c.circle(-W / 2 + 0.45 * s, H / 2 - 0.45 * s, 0.16 * s, stroke=0, fill=1)
    c.restoreState()


def board_profile(c, pcb, ox, oy, s):
    """Vista lateral da placa: Y (vertical) × X (espessura + alturas)."""
    t = 0.8
    # placa
    c.setFillColor(HexColor("#8C8064"))
    c.rect(ox, oy, t * s, BH * s, stroke=0, fill=1)
    c.setFillColor(MASK)
    c.rect(ox - 0.05 * s, oy, 0.05 * s, BH * s, stroke=0, fill=1)
    c.rect(ox + t * s, oy, 0.05 * s, BH * s, stroke=0, fill=1)
    for fp in pcb["fps"]:
        body = BODIES.get(fp["fpid"])
        if not body or fp["back"]:
            continue
        w, h, z, col = body
        span = w if fp["rot"] % 180 else h
        if fp["fpid"].startswith("USB"):
            y_top = fp["y"] - 3.7
            y_bot = fp["y"] + 3.7
        else:
            y_top, y_bot = fp["y"] - span / 2, fp["y"] + span / 2
        x = ox + (t + 0.05) * s
        y = oy + (BH - y_bot) * s
        if fp["fpid"].startswith("USB"):
            c.linearGradient(x, 0, x + z * s, 0, [HexColor("#9DA1A6"), HexColor("#E2E4E6"), HexColor("#9DA1A6")],
                             [0, .5, 1], extend=False) if False else None
            c.setFillColor(SHELL)
        else:
            c.setFillColor(col if col is not LEDW else HexColor("#E8E3D8"))
        c.setStrokeColor(INK)
        c.setLineWidth(0.06)
        c.rect(x, y, z * s, (y_bot - y_top) * s, stroke=1, fill=1)
    c.setStrokeColor(INK)
    c.setLineWidth(0.1)
    c.rect(ox, oy, t * s, BH * s, stroke=1, fill=0)


# ================================================================== lâminas
def page_cover(c):
    new_page(c, dark=True)
    dot_grid(c, M + 4, M + 4, PW - M - 4, PH - M - 4, 6.0, HexColor("#151A21"), 0.18)
    s = 4.2
    ox, oy = 222.0, 47.0
    blue = STATES[1][1]
    flag_halo(c, ox, oy, s, blue, 1.0)
    product_front(c, ox, oy, s, glow_color=blue, stroke=HexColor("#3A4350"), lw=0.25,
                  spot=HexColor("#D6E6FF"), spot_r=6.0)
    # título
    tx = M + 12
    text(c, tx, 214, "INDICADOR", "Jura", 21, MOON, spacing=3.2)
    line(c, tx, 205, tx + 46, 205, 0.15, blue)
    text(c, tx, 196.0, "três pontos de luz para saber o que a máquina", "Serif", 6.2, HexColor("#AEB6C0"))
    text(c, tx, 188.5, "está fazendo, sem olhar para a tela.", "Serif", 6.2, HexColor("#AEB6C0"))
    rows = [("ENVELOPE", "48 × 34 × 15 mm"), ("LUZ", "3 × RGB endereçável · 24 bit"),
            ("CONTROLE", "STM32C071 · USB 2.0 FS sem cristal"), ("CONEXÃO", "USB-C · HID 8 bytes"),
            ("PLACA", "11 × 44 × 0,8 mm · 2 camadas")]
    y = 92
    for k, v in rows:
        text(c, tx, y, k, "JuraM", 2.1, HexColor("#5E6873"), spacing=0.8)
        text(c, tx + 30, y, v, "Mono", 2.5, MOON)
        line(c, tx, y - 3.2, tx + 118, y - 3.2, 0.06, NIGHT3)
        y -= 9.0
    text(c, tx, 38, "REV A  ·  ESTUDO CONCEITUAL  ·  2026-11-08", "Mono", 2.0, HexColor("#4C5661"))
    frame(c, 1, "CAPA", dark=True)


def page_views(c):
    new_page(c)
    dot_grid(c, M + 4, M + 4, PW - M - 4, PH - M - 4, 5.0, HexColor("#E2DED5"), 0.14)
    s = 3.2
    fx, fy = 46.0, 112.0
    # frontal
    product_front(c, fx, fy, s, stroke=INK, show_board=True)
    H = BODY_H * s
    # lateral esquerda (à direita da frontal, primeiro diedro)
    sx = fx + FLAG_X1 * s + 34
    product_side(c, sx, fy, s)
    # superior (abaixo da frontal)
    ty = fy - 26 - BODY_D * s
    product_top(c, fx, ty, s)
    # linhas de chamada entre as vistas
    for yy in (fy, fy + H):
        line(c, fx + FLAG_X1 * s + 6, yy, sx - 4, yy, 0.06, INK3, (0.6, 1.2))
    for xx in (fx, fx + BODY_W * s, fx + FLAG_X1 * s):
        line(c, xx, fy - 4, xx, ty + BODY_D * s + 4, 0.06, INK3, (0.6, 1.2))
    # cotas
    dim(c, fx, fy + H, fx, fy, "48", off=-9)
    dim(c, fx, ty, fx + FLAG_X1 * s, ty, "34", off=-8)
    dim(c, sx, fy, sx + BODY_D * s, fy, "15", off=-8)
    dim(c, fx + FLAG_X1 * s, fy + H - FLAG_Y0 * s, fx + FLAG_X1 * s, fy + H - FLAG_Y1 * s, "19", off=7)
    dim(c, fx + FLAG_X0 * s, fy + H + 2, fx + FLAG_X1 * s, fy + H + 2, "22", off=6)
    dim(c, fx, fy + H + 2, fx + BODY_W * s, fy + H + 2, "12", off=6)
    dim(c, fx + FLAG_X1 * s + 1, ty + BODY_D / 2 * s + FLAG_T / 2 * s, fx + FLAG_X1 * s + 1, ty + BODY_D / 2 * s - FLAG_T / 2 * s, "2,5", off=6)
    # rótulos das vistas
    lab = lambda x, y, t: text(c, x, y, t, "JuraM", 2.2, INK2, spacing=1.0)
    lab(fx, fy - 12.5, "VISTA FRONTAL")
    lab(sx, fy - 12.5, "VISTA LATERAL ESQUERDA")
    lab(fx, ty - 14.0, "VISTA SUPERIOR")
    text(c, fx, ty - 19.0, "1.º diedro · escala 3,2 : 1 · cotas em mm", "Mono", 2.0, INK3)
    # isometria
    isz = 2.35
    ix = 268.0 + 15 * COS30 * isz + 8
    iy = 70.0 + 13.5 * isz
    product_iso(c, ix, iy, isz)
    lab(268.0, 58, "ISOMETRIA")
    text(c, 268.0, 53.0, "junta corpo/tampa a 6 mm da base", "Mono", 2.0, INK3)
    # legenda do tracejado
    lx, ly = 268.0, 250.0
    text(c, lx, ly, "VISTAS DO PRODUTO", "Jura", 7.0, INK, spacing=1.6)
    line(c, lx, ly - 4.5, lx + 26, ly - 4.5, 0.15, INK)
    line(c, lx, ly - 13, lx + 10, ly - 13, 0.12, INK3, (1.2, 0.8))
    text(c, lx + 13, ly - 13.8, "placa, LEDs e USB-C ocultos", "Mono", 2.1, INK2)
    text(c, lx, ly - 21.5, "A raiz da bandeira entra no corpo até encostar", "Serif", 4.4, INK2)
    text(c, lx, ly - 27.0, "na face dos LEDs: a luz entra pela borda.", "Serif", 4.4, INK2)
    frame(c, 2, "VISTAS DO PRODUTO")


def page_board(c, pcb):
    new_page(c)
    s = 5.0
    top = PH - M - 30
    oy = top - BH * s
    tvx, svx, bvx = 74.0, 158.0, 214.0
    draw_board(c, BoardView(c, tvx, oy, s), pcb, "F")
    board_profile(c, pcb, svx, oy, s)
    draw_board(c, BoardView(c, bvx, oy, s, mirror=True), pcb, "B")
    # cotas
    dim(c, tvx, oy + BH * s, tvx + BW * s, oy + BH * s, "11,0", off=5)
    dim(c, bvx, oy, bvx, oy + BH * s, "44,0", off=-6) if False else dim(c, bvx + BW * s, oy, bvx + BW * s, oy + BH * s, "44,0", off=-6)
    dim(c, svx, oy + BH * s, svx + 0.8 * s, oy + BH * s, "0,8", off=5)
    dim(c, svx, oy - 1, svx + (0.85 + 3.26) * s, oy - 1, "4,1", off=-5)
    # chamadas da vista de cima
    labels = {"D3": "LED topo · SK6805-EC20", "D2": "LED meio", "D1": "LED baixo",
              "U3": "nível 3,3 → 5 V", "U1": "STM32C071F8", "U2": "LDO 3,3 V",
              "U4": "ESD USB", "J1": "USB-C 16P"}
    bv = BoardView(c, tvx, oy, s)
    fps = {f["ref"]: f for f in pcb["fps"]}
    order = ["D3", "D2", "U3", "D1", "U1", "U2", "U4", "J1"]
    y_lab = [fps[r]["y"] for r in order]
    nudge = {"U2": 4.5, "U4": -4.5, "D3": 0, "U3": 0}
    for ref, yb in zip(order, y_lab):
        px, py = bv.P(fps[ref]["x"], fps[ref]["y"])
        ly = py + nudge.get(ref, 0)
        lx = M + 6
        line(c, px, py, tvx - 3, ly, 0.08, INK2)
        line(c, tvx - 3, ly, lx + 34, ly, 0.08, INK2)
        c.setFillColor(INK)
        c.circle(px, py, 0.45, stroke=0, fill=1)
        text(c, lx, ly + 0.9, ref, "Mono", 2.3, INK)
        text(c, lx, ly - 2.6, labels[ref], "Sans", 2.0, INK2)
    lab = lambda x, y, t: text(c, x, y, t, "JuraM", 2.2, INK2, spacing=1.0)
    lab(tvx, oy - 12, "FACE DE CIMA")
    lab(svx - 4, oy - 12, "PERFIL")
    lab(bvx, oy - 12, "FACE DE BAIXO")
    text(c, tvx, oy - 17, "componentes · voltada à bandeira", "Mono", 1.9, INK3)
    text(c, svx - 4, oy - 17, "alturas reais", "Mono", 1.9, INK3)
    text(c, bvx, oy - 17, "pads SWD · vista por baixo", "Mono", 1.9, INK3)
    # bloco da direita
    rx = 300.0
    text(c, rx, top + 6, "PLACA DE CIRCUITO", "Jura", 7.0, INK, spacing=1.6)
    line(c, rx, top + 1.5, rx + 26, top + 1.5, 0.15, INK)
    specs = [("SUBSTRATO", "FR-4 · 0,8 mm · 2 camadas"), ("COBRE", "35 µm (1 oz) · planos de GND"),
             ("MÁSCARA", "preta fosca"), ("ACABAMENTO", "ENIG"), ("TRILHA / ISOL.", "0,20 / 0,15 mm"),
             ("VIAS", "0,6 / 0,3 mm · 18 un."), ("MONTAGEM", "SMT, só na face de cima")]
    y = top - 12
    for k, v in specs:
        text(c, rx, y, k, "JuraM", 2.0, INK3, spacing=0.7)
        text(c, rx + 30, y, v, "Mono", 2.2, INK)
        line(c, rx, y - 3, PW - M - 6, y - 3, 0.05, INK4)
        y -= 8.2
    # detalhe 14:1 do LED
    dx, dyc, ds = rx + 46, 74.0, 14.0
    text(c, rx, dyc + 26, "DETALHE · SK6805-EC20 · 14 : 1", "JuraM", 2.0, INK2, spacing=0.8)
    c.setStrokeColor(INK3)
    c.setLineWidth(0.08)
    c.setDash(0.8, 0.6)
    c.rect(dx - 1.0 * ds, dyc - 1.0 * ds, 2.0 * ds, 2.0 * ds, stroke=1, fill=0)
    c.setDash()
    pins = {(0.55, 0.55): ("1", "VDD"), (0.55, -0.55): ("2", "DOUT"), (-0.55, -0.55): ("3", "GND"), (-0.55, 0.55): ("4", "DIN")}
    for (px, py), (n, nm) in pins.items():
        cx, cy = dx + px * ds, dyc - py * ds
        c.setFillColor(GOLD)
        c.rect(cx - 0.3 * ds, cy - 0.3 * ds, 0.6 * ds, 0.6 * ds, stroke=0, fill=1)
        text(c, cx, cy - 1.0, n, "Mono", 2.6, INK, "c")
        side = 1 if px > 0 else -1
        text(c, dx + side * (1.0 * ds + 3.5), cy - 0.8, nm, "Mono", 2.2, INK2, "l" if side > 0 else "r")
    dim(c, dx - 1.0 * ds, dyc - 1.0 * ds, dx + 1.0 * ds, dyc - 1.0 * ds, "2,0", off=-5)
    dim(c, dx - 0.85 * ds, dyc + 1.0 * ds, dx - 0.25 * ds, dyc + 1.0 * ds, "0,6", off=4, ext=False)
    frame(c, 3, "PLACA · TRÊS VISTAS")


def package_icon(c, fpid, cx, cy, s):
    body = BODIES.get(fpid)
    if not body:
        return
    w, h, _z, col = body
    if fpid.startswith("USB"):
        w, h = h, w
    W, H = w * s, h * s
    if fpid.startswith("USB"):
        c.setFillColor(SHELL)
    elif col is LEDW:
        c.setFillColor(HexColor("#E8E3D8"))
    else:
        c.setFillColor(col)
    c.setStrokeColor(INK)
    c.setLineWidth(0.06)
    c.rect(cx - W / 2, cy - H / 2, W, H, stroke=1, fill=1)
    if fpid.startswith(("C_", "R_")):
        c.setFillColor(HexColor("#D9D6CF"))
        e = W * 0.22
        c.rect(cx - W / 2, cy - H / 2, e, H, stroke=0, fill=1)
        c.rect(cx + W / 2 - e, cy - H / 2, e, H, stroke=0, fill=1)


def page_bom(c):
    new_page(c)
    top = PH - M - 24
    text(c, M + 6, top + 6, "COMPONENTES", "Jura", 7.0, INK, spacing=1.6)
    line(c, M + 6, top + 1.5, M + 32, top + 1.5, 0.15, INK)
    rows = [
        ("U1", "1", "Microcontrolador M0+, USB sem cristal", "STM32C071F8P6", "TSSOP-20", "C43650205", "TSSOP-20_4.4x6.5mm_P0.65mm"),
        ("D1–D3", "3", "LED RGB endereçável, 5 mA/canal", "SK6805-EC20", "2020", "C2890036", "LED_SK6805-EC20_2.0x2.0mm"),
        ("U2", "1", "Regulador linear 3,3 V, 600 mA", "AP2112K-3.3", "SOT-23-5", "C51118", "SOT-23-5"),
        ("U3", "1", "Buffer 3,3 → 5 V para o dado dos LEDs", "74AHCT1G125", "SC-70-5", "C53114384", "SOT-353_SC-70-5"),
        ("U4", "1", "Proteção ESD de D+/D− e VBUS", "USBLC6-2SC6", "SOT-23-6", "C7519", "SOT-23-6"),
        ("J1", "1", "Receptáculo USB-C, 16 pinos", "TYPE-C-31-M-12", "SMD + THT", "C165948", "USB_C_Receptacle_HRO_TYPE-C-31-M-12"),
        ("C1", "1", "Capacitor 10 µF X5R, entrada VBUS", "CL10A106KP8NNNC", "0603", "C19702", "C_0603_1608Metric"),
        ("C2", "1", "Capacitor 1 µF X5R, saída 3,3 V", "CL05A105KA5NQNC", "0402", "C52923", "C_0402_1005Metric"),
        ("C3–C8", "6", "Capacitor 100 nF X7R, desacoplamento", "CL05B104KO5NNNC", "0402", "C1525", "C_0402_1005Metric"),
        ("R1, R2", "2", "Resistor 5,1 kΩ 1 %, CC do USB-C", "0402WGF5101TCE", "0402", "C25905", "R_0402_1005Metric"),
        ("R3", "1", "Resistor 33 Ω, série no dado dos LEDs", "0402WGF330JTCE", "0402", "C25105", "R_0402_1005Metric"),
    ]
    cols = [M + 6, M + 26, M + 36, M + 128, M + 168, M + 190, M + 212]
    heads = ["REF", "QTD", "FUNÇÃO", "PEÇA", "ENCAPS.", "LCSC", "ESCALA 6:1"]
    y = top - 12
    for x, h in zip(cols, heads):
        text(c, x, y, h, "JuraM", 1.9, INK3, spacing=0.7)
    line(c, M + 6, y - 2.6, M + 236, y - 2.6, 0.12, INK)
    y -= 10.5
    for ref, q, fn, part, pkg, lcsc, fpid in rows:
        text(c, cols[0], y, ref, "Mono", 2.4, INK)
        text(c, cols[1], y, q, "Mono", 2.4, INK)
        text(c, cols[2], y, fn, "Sans", 2.3, INK)
        text(c, cols[3], y, part, "Mono", 2.1, INK)
        text(c, cols[4], y, pkg, "Mono", 2.1, INK2)
        text(c, cols[5], y, lcsc, "Mono", 2.1, INK2)
        package_icon(c, fpid, cols[6] + 12, y + 0.8, 1.0 if fpid.startswith("USB") else 1.3 if "TSSOP" in fpid else 3.0)
        line(c, M + 6, y - 4.4, M + 236, y - 4.4, 0.05, INK4)
        y -= 16.6
    text(c, M + 6, y - 2, "Todos do catálogo JLCPCB; passivos na categoria básica.", "Serif", 4.2, INK2)

    # materiais
    mx = 272.0
    text(c, mx, top + 6, "MATERIAIS", "Jura", 7.0, INK, spacing=1.6)
    line(c, mx, top + 1.5, mx + 26, top + 1.5, 0.15, INK)
    mats = [
        ("CORPO E TAMPA", "PC/ABS", "injeção · textura fina", HexColor("#E3DED4")),
        ("BANDEIRA", "policarbonato difusor", "injeção · guia de luz pela borda", HexColor("#F8F7F3")),
        ("PLACA", "FR-4, cobre, máscara preta", "laminação · ENIG · SMT", MASK),
        ("CONTATOS USB-C", "liga de cobre, aço inox", "estampagem · solda THT", SHELL),
        ("FIXAÇÃO", "ímã NdFeB Ø10 × 1,5 + fita VHB", "sinterizado · revestido Ni", HexColor("#7D8186")),
    ]
    y = top - 14
    for k, mat, proc, col in mats:
        c.setFillColor(col)
        c.setStrokeColor(INK)
        c.setLineWidth(0.08)
        c.rect(mx, y - 5.5, 9, 9, stroke=1, fill=1)
        text(c, mx + 14, y + 1.0, k, "JuraM", 1.9, INK3, spacing=0.7)
        text(c, mx + 14, y - 3.2, mat, "Sans", 2.6, INK)
        text(c, mx + 14, y - 7.0, proc, "Mono", 2.0, INK2)
        y -= 17.5
    text(c, mx, y + 3.0, "corpo, bandeira e fixação: proposta, a validar no protótipo", "Mono", 1.9, INK3)
    # orçamento de energia
    y = 92.0
    text(c, mx, y, "ENERGIA", "Jura", 5.0, INK, spacing=1.2)
    y -= 9
    bars = [("LEDs (3 × 3 × 5 mA)", 45), ("MCU + USB", 10), ("nível + LDO", 2)]
    total = sum(b for _, b in bars)
    bx = mx
    for i, (k, v) in enumerate(bars):
        w = v / 60 * 112
        c.setFillColor([INK, INK2, INK3][i])
        c.rect(bx, y, w, 3.2, stroke=0, fill=1)
        bx += w
    c.setStrokeColor(INK)
    c.setLineWidth(0.08)
    c.rect(mx, y, 112, 3.2, stroke=1, fill=0)
    text(c, mx + 112, y + 5.0, "escala 0–60 mA", "Mono", 1.9, INK3, "r")
    yy = y - 5
    for i, (k, v) in enumerate(bars):
        c.setFillColor([INK, INK2, INK3][i])
        c.rect(mx, yy - 0.4, 2.2, 2.2, stroke=0, fill=1)
        text(c, mx + 4, yy, f"{k}", "Mono", 2.0, INK2)
        text(c, mx + 76, yy, f"{v} mA", "Mono", 2.0, INK, "r")
        yy -= 4.5
    text(c, mx, yy - 1.5, f"pico de {total} mA, de 500 mA do USB", "Serif", 4.2, INK2)
    frame(c, 4, "COMPONENTES E MATERIAIS")


def wave(kind, t):
    if kind == "steady_low":
        return 0.28
    if kind == "steady_high":
        return 1.0
    if kind == "breathe":
        return 0.15 + 0.85 * (0.5 - 0.5 * math.cos(2 * math.pi * t / 2.4)) ** 1.6
    if kind == "blink":
        return 1.0 if (t % 1.0) < 0.5 else 0.06
    if kind == "strobe":
        return 1.0 if (t % 0.25) < 0.08 else 0.04
    return 0


def page_states(c):
    new_page(c, dark=True)
    dot_grid(c, M + 4, M + 4, PW - M - 4, PH - M - 4, 6.0, HexColor("#121720"), 0.16)
    text(c, M + 12, PH - M - 18, "EM FUNCIONAMENTO", "Jura", 7.0, MOON, spacing=1.6)
    line(c, M + 12, PH - M - 22.5, M + 38, PH - M - 22.5, 0.15, MOON)
    text(c, M + 12, PH - M - 31, "uma cor por estado; a forma no tempo diz a urgência", "Serif", 4.6, HexColor("#8E98A4"))
    n = len(STATES)
    colw = (PW - 2 * M - 24) / n
    s = 2.35
    base_y = 100.0
    for i, (name, col, kind) in enumerate(STATES):
        cx = M + 12 + colw * i + colw / 2
        ox = cx - (FLAG_X1 / 2) * s
        flag_halo(c, ox, base_y, s, col, 0.7 if kind != "steady_low" else 0.32)
        lit = col if kind != "steady_low" else Color(col.red * .62, col.green * .62, col.blue * .62)
        product_front(c, ox, base_y, s, glow_color=lit, stroke=HexColor("#323A45"), lw=0.2,
                      spot=Color(min(1, col.red * .4 + .6), min(1, col.green * .4 + .6), min(1, col.blue * .4 + .6)),
                      spot_r=4.8)
        # nome
        text(c, cx, base_y - 14, name, "JuraM", 2.6, MOON, "c", spacing=1.1)
        # onda de brilho
        wx0, wx1 = cx - colw / 2 + 8, cx + colw / 2 - 8
        wy0, wh = base_y - 46, 18
        line(c, wx0, wy0, wx1, wy0, 0.08, NIGHT3)
        for k in range(0, 5):
            xx = wx0 + (wx1 - wx0) * k / 4
            line(c, xx, wy0, xx, wy0 - 1.2, 0.08, HexColor("#3A4350"))
        c.setStrokeColor(col)
        c.setLineWidth(0.35)
        p = c.beginPath()
        N = 400
        for j in range(N + 1):
            t = 4.0 * j / N
            v = wave(kind, t)
            xx = wx0 + (wx1 - wx0) * j / N
            yy = wy0 + v * wh
            (p.moveTo if j == 0 else p.lineTo)(xx, yy)
        c.drawPath(p, stroke=1, fill=0)
        text(c, wx0, wy0 - 5, "0", "Mono", 1.8, HexColor("#5E6873"))
        text(c, wx1, wy0 - 5, "4 s", "Mono", 1.8, HexColor("#5E6873"), "r")
    # escada de prioridade
    py = 30.0
    text(c, M + 12, py + 1, "PRIORIDADE", "JuraM", 2.0, HexColor("#5E6873"), spacing=0.8)
    order = [STATES[4], STATES[3], STATES[2], STATES[1], STATES[0]]
    x = M + 46
    for k, (name, col, _) in enumerate(order):
        c.setFillColor(col)
        c.circle(x, py + 1.7, 1.1, stroke=0, fill=1)
        w = text(c, x + 3, py + 1, name, "Mono", 2.2, MOON)
        x += w + 9
        if k < len(order) - 1:
            text(c, x - 5.6, py + 1, ">", "Mono", 2.2, HexColor("#5E6873"))
    frame(c, 5, "ESTADOS", dark=True)


def node(c, x, y, w, h, title, sub, accent=None, dark=False):
    c.setFillColor(PAPER)
    c.setStrokeColor(INK)
    c.setLineWidth(0.14)
    c.rect(x, y, w, h, stroke=1, fill=1)
    if accent is not None:
        c.setFillColor(accent)
        c.rect(x, y + h - 1.0, w, 1.0, stroke=0, fill=1)
    text(c, x + 3.5, y + h - 6.5, title, "JuraM", 2.4, INK, spacing=0.6)
    for i, sline in enumerate(sub):
        text(c, x + 3.5, y + h - 11.5 - i * 4.0, sline, "Mono", 1.95, INK2)


def wire(c, x1, y1, x2, y2, label=None, color=INK):
    line(c, x1, y1, x2, y2, 0.12, color)
    arrow_head(c, x2, y2, math.atan2(y2 - y1, x2 - x1), color, 1.6)
    if label:
        text(c, (x1 + x2) / 2, max(y1, y2) + 1.4, label, "Mono", 1.85, INK2, "c")


def page_system(c):
    new_page(c)
    dot_grid(c, M + 4, M + 4, PW - M - 4, PH - M - 4, 5.0, HexColor("#E2DED5"), 0.14)
    top = PH - M - 24
    text(c, M + 6, top + 6, "DO EVENTO À LUZ", "Jura", 7.0, INK, spacing=1.6)
    line(c, M + 6, top + 1.5, M + 32, top + 1.5, 0.15, INK)
    # coluna 1: fontes
    srcs = [("CLAUDE CODE", ["hooks: início, permissão,", "fim, erro"], STATES[1][1]),
            ("CODEX", ["notify ao terminar"], STATES[1][1]),
            ("MICROFONE", ["PipeWire: fonte em uso"], STATES[4][1]),
            ("CÂMERA", ["/dev/video* aberto"], STATES[4][1]),
            ("AGENDA", ["Google · Outlook (OAuth)"], STATES[4][1])]
    x1, w1, h1 = M + 6, 62, 17
    ys = [top - 22 - i * 31 for i in range(len(srcs))]
    for (t, sub, col), y in zip(srcs, ys):
        node(c, x1, y, w1, h1, t, sub, col)
    # daemon
    x2, w2, h2 = x1 + w1 + 30, 72, 72
    y2 = ys[2] + h1 / 2 - h2 / 2
    node(c, x2, y2, w2, h2, "DAEMON LINUX", ["Python · reaproveita luxafor.py", "", "junta as fontes", "aplica a prioridade", "escolhe o estado", "", "1 comando por mudança"])
    for y in ys:
        wire(c, x1 + w1, y + h1 / 2, x2, y2 + h2 / 2 + (y + h1 / 2 - (ys[2] + h1 / 2)) * 0.25)
    # dispositivo
    x3, w3 = x2 + w2 + 34, 96
    y3, h3 = y2 - 20, h2 + 40
    c.setStrokeColor(INK3)
    c.setLineWidth(0.1)
    c.setDash(1.2, 0.8)
    c.rect(x3 - 6, y3 - 6, w3 + 12, h3 + 12, stroke=1, fill=0)
    c.setDash()
    text(c, x3 - 6, y3 + h3 + 8.5, "INDICADOR", "JuraM", 2.0, INK3, spacing=0.8)
    wire(c, x2 + w2, y2 + h2 / 2, x3, y2 + h2 / 2, "USB HID · 8 bytes")
    mcu_y = y2 + h2 / 2 - 15
    node(c, x3, mcu_y, 44, 30, "STM32C071", ["USB FS sem cristal", "animações na flash", "SPI → 800 kHz"])
    node(c, x3 + 56, mcu_y + 3, 40, 24, "74AHCT1G125", ["3,3 V → 5 V"])
    wire(c, x3 + 44, mcu_y + 15, x3 + 56, mcu_y + 15)
    # cadeia de LEDs
    ly = mcu_y - 30
    for k, (nm, col) in enumerate([("D1 baixo", STATES[0][1]), ("D2 meio", STATES[1][1]), ("D3 topo", STATES[4][1])]):
        lx = x3 + 8 + k * 30
        c.setFillColor(LEDW)
        c.setStrokeColor(INK)
        c.setLineWidth(0.12)
        c.rect(lx, ly, 10, 10, stroke=1, fill=1)
        for j, cc in enumerate(("#E0584F", "#4FB37A", "#4F7FE0")):
            c.setFillColor(HexColor(cc))
            c.rect(lx + 2.2 + j * 2.2, ly + 4.3, 1.4, 1.4, stroke=0, fill=1)
        text(c, lx + 5, ly - 4.5, nm, "Mono", 1.9, INK2, "c")
        if k < 2:
            wire(c, lx + 10, ly + 5, lx + 30, ly + 5)
    wire(c, x3 + 76, mcu_y + 3, x3 + 76, mcu_y - 6)
    line(c, x3 + 76, mcu_y - 6, x3 + 13, mcu_y - 6, 0.12)
    wire(c, x3 + 13, mcu_y - 6, x3 + 13, ly + 10)
    # protocolo
    px, py = x3 + w3 + 26, top - 14
    text(c, px, py + 2, "PROTOCOLO", "Jura", 5.0, INK, spacing=1.2)
    cmds = [("01", "cor fixa", "LED R G B"), ("02", "fade", "LED R G B t"), ("03", "strobe", "LED R G B t 00 n"),
            ("04", "wave", "tipo R G B 00 n v"), ("06", "padrão", "id n"), ("80", "versão", "→ 80 VV"),
            ("··", "estado", "proposto")]
    y = py - 9
    for op, nm, args in cmds:
        c.setFillColor(INK)
        c.rect(px, y - 1.2, 7.5, 4.4, stroke=0, fill=1)
        text(c, px + 3.75, y, op, "Mono", 2.2, PAPER, "c")
        text(c, px + 11, y, nm, "Sans", 2.3, INK)
        text(c, px + 31, y, args, "Mono", 1.95, INK2)
        y -= 7.2
    text(c, px, y - 3, "compatível com o", "Serif", 4.2, INK2)
    text(c, px, y - 8.2, "protocolo mapeado do Luxafor.", "Serif", 4.2, INK2)
    # bytes
    by = 64.0
    text(c, M + 6, by + 10, "RELATÓRIO HID (8 BYTES) · COR FIXA NO LED DO TOPO EM AZUL", "JuraM", 2.0, INK3, spacing=0.7)
    vals = ["01", "03", "00", "00", "FF", "00", "00", "00"]
    names = ["op", "led", "R", "G", "B", "", "", ""]
    for i, (v, n) in enumerate(zip(vals, names)):
        bx = M + 6 + i * 15
        c.setStrokeColor(INK)
        c.setLineWidth(0.12)
        c.setFillColor(STATES[1][1] if v == "FF" else PAPER)
        c.rect(bx, by - 4, 13, 9, stroke=1, fill=1)
        text(c, bx + 6.5, by - 0.8, v, "Mono", 2.8, PAPER if v == "FF" else INK, "c")
        text(c, bx + 6.5, by - 8.5, n, "Mono", 1.9, INK2, "c")
    frame(c, 6, "SISTEMA")


def main():
    pcb = load_pcb()
    c = canvas.Canvas(OUT, pagesize=(PW * MMPT, PH * MMPT))
    c.setTitle("Indicador rev A · caderno conceitual")
    c.setAuthor("lstavares84")
    from paginas_extra import EXTRA_PAGES
    for fn in (page_cover, page_views, lambda c: page_board(c, pcb), page_bom, page_states, page_system,
               *EXTRA_PAGES):
        fn(c)
        c.showPage()
    c.save()
    print("ok:", OUT)


if __name__ == "__main__":
    main()
