#!/usr/bin/env python3
"""Gera renders anotados (face de cima e de baixo) com chamadas por componente.

Calibração: render ortogonal com fundo transparente; a largura do contorno
(15,2 mm nas orelhas da rev D) e a borda superior (y = 0, descontada a haste do S1) dão escala e origem. As posições
vêm dos footprints do .kicad_pcb (pcbnew). Na face de baixo o eixo X é espelhado.
"""
import os
import pcbnew
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REN = os.path.join(HERE, "..", "renders")
PCB = os.path.join(HERE, "..", "project", "luxflag.kicad_pcb")
W_MM = 15.2          # largura total nas orelhas (rev D): x = -2,1 .. 13,1 mm
X_EAR = 2.1          # orelha além da borda x = 0 do corpo
Y_STEM = 0.24        # haste do S1 passa 0,24 mm da borda y = 0
OX, OY = 100.0, 100.0

# ref: (peça, função)
LABELS = {
    "D3": ("WS2816B-2020", "LED 3 (topo), RGB 16 bit"),
    "D2": ("WS2816B-2020", "LED 2 (meio), RGB 16 bit"),
    "D1": ("WS2816B-2020", "LED 1 (baixo), RGB 16 bit"),
    "C8": ("100 nF", "desacoplamento D3"),
    "C7": ("100 nF", "desacoplamento D2"),
    "C6": ("100 nF", "desacoplamento D1"),
    "C5": ("100 nF", "desacoplamento U3"),
    "U3": ("SN74AHCT1G125", "nível 3,3 V → 5 V (dado)"),
    "R3": ("33 Ω", "série do dado dos LEDs"),
    "R4": ("1 kΩ", "pull-up BOOT0 (via JP1)"),
    "C2": ("1 µF", "saída do LDO 3,3 V"),
    "C3": ("100 nF", "desacoplamento VDD do MCU"),
    "C4": ("100 nF", "filtro do NRST"),
    "U1": ("STM32C071G8U6", "MCU, USB FS sem cristal"),
    "U2": ("AP2112K-3.3", "LDO 3,3 V / 600 mA"),
    "U4": ("USBLC6-2SC6", "proteção ESD do USB"),
    "C1": ("10 µF", "capacitor de entrada VBUS"),
    "R1": ("5,1 kΩ", "CC1 → dispositivo USB-C"),
    "R2": ("5,1 kΩ", "CC2 → dispositivo USB-C"),
    "J1": ("HRO TYPE-C-31-M-12", "USB-C 16 pinos"),
    "J2": ("Tag-Connect TC2030", "SWD: 3V3, SWDIO, NRST, SWCLK, GND"),
    "JP1": ("jumper de solda", "BOOT0 → DFU (fechar p/ gravar)"),
    "S1": ("ALPS SKRTLAE010", "botão lateral: OCUPADO/LIVRE; BOOT0 ao ligar"),
    "R5": ("1 kΩ", "série do botão → PA14 (ESD)"),
    "TP1": ("ponto de teste", "VBUS 5 V"),
    "TP2": ("ponto de teste", "dado dos LEDs 5 V"),
    "TP3": ("ponto de teste", "GND"),
}

# chamadas extras (sem footprint próprio), coordenadas em mm da placa
EXTRA = {
    "B": {
        "J2-guia": (2.96, 8.7, "furos-guia TC2030", "3 furos NPTH p/ o cabo sem pernas"),
        "J1-S1": (9.82, 42.05, "J1 blindagem", "4 pinos THT de fixação do USB-C"),
        "J1-NPTH": (2.61, 38.4, "J1 pinos-guia", "2 furos NPTH de alinhamento"),
        "GND": (4.0, 32.5, "plano de GND", "cobre nas duas faces, costurado por vias"),
        "TXT": (5.5, 15.0, "serigrafia", "identificação da revisão"),
    },
    "F": {
        "J2-furos": (8.04, 8.7, "furos TC2030", "passam pela placa entre D3 e D2"),
        "S1-haste": (5.5, -0.2, "haste do S1", "sai 0,24 mm da borda; empurrada pelo botão P06"),
    },
}


def font(sz, bold=False):
    f = "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else "")
    return ImageFont.truetype(f, sz)

def calib(img):
    bb = img.getchannel("A").point(lambda a: 255 if a > 200 else 0).getbbox()
    s = (bb[2] - bb[0]) / W_MM
    return s, bb[0] + X_EAR * s, bb[1] + Y_STEM * s, bb[2] - X_EAR * s

def positions():
    b = pcbnew.LoadBoard(PCB)
    out = {}
    for fp in b.GetFootprints():
        r = fp.GetReference()
        bbox = fp.GetBoundingBox(False)  # sem textos
        c = bbox.GetCenter() if r in ("J1",) else fp.GetPosition()
        out[r] = (pcbnew.ToMM(c.x) - OX, pcbnew.ToMM(c.y) - OY, fp.IsFlipped())
    return out

def spread(items, top, bottom, h):
    """items: lista de [y_desejado, ...]; distribui sem sobreposição (altura h)."""
    items.sort(key=lambda t: t[0])
    ys = [t[0] for t in items]
    for i in range(1, len(ys)):
        ys[i] = max(ys[i], ys[i-1] + h)
    over = ys[-1] - (bottom - h) if ys else 0
    if over > 0:
        ys[-1] -= over
        for i in range(len(ys) - 2, -1, -1):
            ys[i] = min(ys[i], ys[i+1] - h)
    if ys and ys[0] < top:
        sh = top - ys[0]
        ys = [y + sh for y in ys]
    return ys

def annotate(raw, side, refs_extra, out, title):
    img = Image.open(os.path.join(REN, raw)).convert("RGBA")
    a = img.getchannel("A").point(lambda v: 255 if v > 235 else 0)
    img.putalpha(a)
    s, x0, y0, x1 = calib(img)
    pos = positions()
    want = [r for r, (x, y, fl) in pos.items() if r in LABELS and (fl == (side == "B") or r in refs_extra)]
    MARGIN = 900
    BG = (248, 249, 251, 255)
    crop_top, crop_bot = int(y0 - 2.5 * s), int(y0 + 46.5 * s)
    board = img.crop((0, crop_top, img.width, crop_bot))
    W = board.width + 2 * MARGIN
    H = board.height + 120
    canvas = Image.new("RGBA", (W, H), BG)
    canvas.alpha_composite(board, (MARGIN, 120))
    d = ImageDraw.Draw(canvas)
    f1, f2, ft = font(30, True), font(25), font(40, True)
    d.text((40, 30), title, font=ft, fill=(30, 32, 36))

    def px(x, y):
        X = (x0 + x * s) if side == "F" else (x1 - x * s)
        return MARGIN + X, 120 + (y0 - crop_top) + y * s

    left, right = [], []
    cx = MARGIN + (x0 + x1) / 2
    pts_all = {r: px(*pos[r][:2]) for r in want}
    for k, (xm, ym, part, fn) in EXTRA.get(side, {}).items():
        pts_all[k] = px(xm, ym); LABELS[k] = (part, fn); want.append(k)

    def blockers(r, to_left):
        X, Y = pts_all[r]
        return [o for o, (Xo, Yo) in pts_all.items() if o != r and abs(Yo - Y) < 1.0 * s
                and ((Xo < X) if to_left else (Xo > X))]
    for r in sorted(want, key=lambda r: abs(pts_all[r][0] - cx), reverse=True):
        X, Y = pts_all[r]
        bl, br = len(blockers(r, True)), len(blockers(r, False))
        if X < cx - 1 and bl <= br: go_left = True
        elif X > cx + 1 and br <= bl: go_left = False
        elif bl != br: go_left = bl < br
        else: go_left = len(left) <= len(right)
        blocked = blockers(r, go_left)
        want_y = Y - 1.6 * s if blocked else Y
        (left if go_left else right).append([want_y, r, X, Y])
    LH = 78
    for group, is_left in ((left, True), (right, False)):
        if not group: continue
        ys = spread(group, 160, H - 20, LH)
        for (_wy, r, Xt, Yt), yl in zip(group, ys):
            part, fn = LABELS[r]
            l1, l2 = (f"{r}  {part}" if r in pos else part), fn
            w = max(d.textlength(l1, font=f1), d.textlength(l2, font=f2))
            if is_left:
                tx = MARGIN - 60 - w; anchor_x = MARGIN - 45
            else:
                tx = W - MARGIN + 60; anchor_x = W - MARGIN + 45
            ty = yl - 30
            d.text((tx, ty), l1, font=f1, fill=(20, 22, 26))
            d.text((tx, ty + 36), l2, font=f2, fill=(90, 94, 102))
            col = (0, 112, 243)
            elbow_x = MARGIN + (x0 - 30 if is_left else x1 + 30)
            pts = [(anchor_x, yl + 4), (elbow_x, yl + 4), (Xt, Yt)]
            d.line(pts, fill=col, width=3, joint="curve")
            d.ellipse((Xt - 7, Yt - 7, Xt + 7, Yt + 7), outline=(255, 255, 255), fill=col, width=3)
    canvas.convert("RGB").save(os.path.join(REN, out), optimize=True)
    print(out, canvas.size, "escala %.1f px/mm" % s)

if __name__ == "__main__":
    annotate("raw_render_top.png", "F", (), "annotated_top.png",
             "Face de cima: botão, LEDs, MCU, energia e USB-C (rev D)")
    annotate("raw_render_bottom.png", "B", ("J1",), "annotated_bottom.png",
             "Face de baixo: programação (SWD), BOOT0 e pontos de teste")
