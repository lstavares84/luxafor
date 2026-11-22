"""Desenho de conjunto (A3): corte A-A, corte B-B, vista explodida isometrica com baloes e lista de pecas."""
import os
from build123d import *
from params import *
from parts import *
from drafting import Sheet, View
from drawings import OUT, FRONT, LEFT, HALF, f

ISO = ((-0.55, -0.75, -0.45), (0, 0, 1))


def board_proxy():
    """Placa simplificada p/ o desenho (HLR do STEP completo é lento): substrato + orelhas + J1 + LEDs + MCU + S1."""
    yb = PCB_Y0 + PCB_T / 2
    b = Pos(0, yb, PCB_Z0 + PCB_L / 2) * Box(PCB_W, PCB_T, PCB_L)
    b += Pos(0, yb, PCB_TOP_Z - EAR_H / 2) * Box(2 * EAR_X_OUT, PCB_T, EAR_H)
    yf = PCB_FRONT_Y
    b += Pos(0, yf + USB_TOP / 2, USB_MOUTH_Z - 3.675) * Box(8.94, USB_TOP, 7.35)
    for d in LED_FROM_EDGE:
        b += Pos(0, yf + LED_H / 2, PCB_Z0 + d) * Box(2.2, LED_H, 2.0)
    b += Pos(0, yf + 0.275, PCB_Z0 + 28.6) * Box(4.0, 0.55, 4.0)
    b += Pos(0, yf + SW_BODY[1] / 2, PCB_Z0 + 1.8) * Box(SW_BODY[0], SW_BODY[1], 2.56)
    b += Pos(0, BTN_Y, SW_TIP_Z) * Cylinder(1.0, 1.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return b


def cable_proxy(stub=25):
    return Compound(list(cable_plug()) + [Pos(0, USB_Y, CABLE_Z0) * Cylinder(CABLE_D / 2, stub, align=(Align.CENTER, Align.CENTER, Align.MIN))])


def d_asm():
    P = dict(tube=tube(), cap=cap(), carrier=carrier(), plug=end_plug(), grommet=grommet(), plunger=plunger())
    B = board_proxy()
    C = cable_proxy(25)
    mass = sum(P[k].volume / 1000 * dd for k, dd in dict(tube=1.2, cap=2.7, carrier=1.2, plug=1.2, grommet=1.1, plunger=1.2).items()) + 1.0  # placa montada ~1,0 g (estimativa)
    sh = Sheet('A3', 'LXP-A00', 'Conjunto (montagem)', 'Ver lista de peças', 'Ver desenhos de peça', '1,75:1 / 0,75:1', mass, sheet='1/1')
    s = 1.75
    # ---------------- corte A-A (plano Y=0, observador na frente)
    cutA = Compound([P[k] & HALF for k in P] + [B, C])  # placa e cabo em vista (não cortados)
    O = (70, 160)
    v = View(sh, cutA, *FRONT, origin=O, scale=s, section=((0, 0, 0), (0, 1, 0)), center=(0, 0, 50), hidden=False)
    sh.text(O[0], 270, 'CORTE A-A', 3.5, ha='center', weight='bold')
    sh.centerline(v.map((0, 0, -2)), v.map((0, 0, 104)))
    R = CAP_OD / 2
    top = CAP_TOP + GR_FL_T + GR_BOOT_L
    sh.dim(v.map((R, 0, CAP_TOP)), v.map((-R, 0, CAP_TOP)), 26, f'Ø{f(CAP_OD)}')
    sh.dim(v.map((8, 0, 0)), v.map((-8, 0, 0)), -8, f'Ø{f(TUBE_OD)}')
    sh.dim(v.map((-R, 0, 0)), v.map((-R, 0, CAP_TOP)), 10, f'{f(CAP_TOP)}', orient='v')
    sh.dim(v.map((-R, 0, 0)), v.map((-R, 0, top)), 20, f'{f(top)} (c/ passa-cabo)', orient='v')
    sh.dim(v.map((R, 0, CAP_Z0)), v.map((R, 0, CAP_TOP)), -8, f'{f(CAP_L)}', orient='v')
    sh.dim(v.map((R, 0, TUBE_Z0 - 2)), v.map((R, 0, CAP_Z0)), -8, f'{f(CAP_Z0)} (visível)', orient='v')
    for i, z in enumerate([PCB_Z0 + d for d in LED_FROM_EDGE]):
        sh.leader(v.map((0, 0, z)), (O[0] - 46, v.map((0, 0, z))[1] + 4 - 4 * i), f'D{3-i}', ha='right')
    sh.leader(v.map((3, 0, USB_MOUTH_Z - 3)), (O[0] - 40, v.map((0, 0, USB_MOUTH_Z))[1] - 12), 'USB-C (J1)', ha='right')
    sh.leader(v.map((4, 0, USB_MOUTH_Z + 8)), (O[0] - 40, v.map((0, 0, USB_MOUTH_Z))[1] + 14), 'Plugue (C01)', ha='right')
    sh.leader(v.map((SNAP_R - 0.2, 0, FLANGE_Z0 + 1)), (O[0] - 40, v.map((0, 0, FLANGE_Z0))[1] - 24), 'Encaixe', ha='right')
    sh.leader(v.map((EAR_X_OUT - 0.3, 0, PCB_TOP_Z - 0.5)), (O[0] + 40, v.map((0, 0, FLANGE_Z0))[1] - 20), 'Orelha da placa (batente)')
    sh.leader(v.map((0, 0, -BTN_PROUD + 0.2)), (O[0] - 40, v.map((0, 0, 0))[1] - 3), 'Botão (8)', ha='right')
    # ---------------- corte B-B (plano X=0, observador a esquerda -> colocado a direita)
    HX = Pos(100, 0, 0) * Box(200, 400, 400)
    cutB = Compound([P[k] & HX for k in P] + [B & HX])
    O2 = (172, 160)
    w = View(sh, cutB, *LEFT, origin=O2, scale=s, section=((0, 0, 0), (1, 0, 0)), center=(0, 0, 50), hidden=False)
    sh.text(O2[0], 270, 'CORTE B-B', 3.5, ha='center', weight='bold')
    sh.centerline(w.map((0, 0, -2)), w.map((0, 0, 92)))
    led_top = PCB_Y0 + PCB_T + LED_H
    # LEFT: u = -y -> frente (+Y) fica a esquerda
    zL = PCB_Z0 + LED_FROM_EDGE[1]
    sh.dim(w.map((0, led_top, zL)), w.map((0, TUBE_ID / 2, zL)), 0.01, f'{f(TUBE_ID/2-led_top)}', ts=2.2)
    sh.leader(w.map((0, (led_top + TUBE_ID / 2) / 2, zL)), (O2[0] - 40, w.map((0, 0, zL))[1] + 22), 'LED → difusor', ha='right')
    sh.dim(w.map((0, -2.4, 30)), w.map((0, -1.6, 30)), 0.01, '') if False else None
    sh.leader(w.map((0, PCB_Y0 + 0.4, 38)), (O2[0] + 34, w.map((0, 0, 38))[1]), 'Placa SIGNA rev D')
    sh.leader(w.map((0, -5.0, 29)), (O2[0] + 34, w.map((0, 0, 29))[1]), 'Berço (refletor)')
    # indicacao dos planos de corte numa vista de topo simbolica (circulo)
    cx, cy, rr = 120, 75, 9.5 * s
    import math
    pts = [(cx + rr * math.cos(t / 40 * 2 * math.pi), cy + rr * math.sin(t / 40 * 2 * math.pi)) for t in range(41)]
    sh.poly(pts, 'vis')
    sh.text(cx, cy - rr - 9, 'Planos de corte (vista de cima)', 2.5, ha='center', va='top')
    sh.cut_line((cx + rr + 4, cy), (cx - rr - 4, cy), 'A', (0, -1))
    sh.cut_line((cx, cy + rr + 4), (cx, cy - rr - 4), 'B', (1, 0))
    sh.text(cx + rr + 8, cy + rr, '↑ frente (LEDs)', 2.2, ha='left')
    # ---------------- vista explodida
    offs = dict(plunger=(0, 0, -76), plug=(0, 0, -64), tube=(0, 0, -56), carrier=(0, 0, 0), board=(30, 0, 8), cap=(0, 0, 30), grommet=(0, 0, 52))
    parts_exp = [Pos(*offs[k]) * P[k] for k in ('plunger', 'plug', 'tube', 'carrier', 'cap', 'grommet')] + [Pos(*offs['board']) * B]
    E = Compound(parts_exp)
    se = 0.75
    O3 = (330, 185)
    ve = View(sh, E, *ISO, origin=O3, scale=se, center=(10, 0, 30), hidden=False)
    sh.text(O3[0], 278, 'VISTA EXPLODIDA (isométrica)', 3.5, ha='center', weight='bold')
    items = [  # (n, ponto no modelo (ja deslocado), posicao do balao)
        (1, (-8, 0, 20 + offs['tube'][2]), (-40, -10)),
        (2, (-9.5, 0, 62 + offs['cap'][2]), (-30, 0)),
        (3, (0, -8, 51), (28, 4)),
        (4, (-8, 0, 1 + offs['plug'][2]), (-28, -6)),
        (5, (-7.5, 0, 78.6 + offs['grommet'][2]), (-24, 4)),
        (6, (30 - 4, -1.6, 34 + offs['board'][2]), (-26, -4)),
        (8, (0, BTN_Y, 0 + offs['plunger'][2]), (-24, -6)),
    ]
    for n, pt, dlt in items:
        tip = ve.map(pt)
        sh.balloon(tip, (tip[0] + dlt[0], tip[1] + dlt[1]), n)
    # ---------------- lista de pecas
    rows = [
        ['1', 'LXP-P01', 'Tubo difusor Ø16/13 × 48', 'PC opalino extrudado, fosco', '1'],
        ['2', 'LXP-P02', 'Tampa superior Ø19 × 32', 'Al 6061-T6 anod. tipo II preto', '1'],
        ['3', 'LXP-P03', 'Berço da placa', 'PC branco (injetado)', '1'],
        ['4', 'LXP-P04', 'Tampão inferior Ø16', 'PC opalino (injetado)', '1'],
        ['5', 'LXP-P05', 'Passa-cabo bipartido', 'TPE 60A preto', '1'],
        ['6', 'LXE-E01', 'Placa SIGNA rev D 11(15,2)×44×0,8', 'ver luxpcb-revD (BOM/CPL)', '1'],
        ['7', 'LXC-C01', 'Cabo USB-C Ø3,5–4,0, 1,5 m (comprado)', 'sobremolde ≤11,6×6,4; +bota ≤24,5 mm', '1'],
        ['8', 'LXP-P06', 'Botão (pino) Ø3/Ø4,4 × 7,4', 'PC opalino (injetado)', '1'],
    ]
    yb = sh.table(230, 112, [('Item', 10), ('Código', 20), ('Descrição', 66), ('Material / ref.', 72), ('Qtd', 12)], rows, rh=5.6, ts=2.3)
    sh.notes(20, 46, 'NOTAS DE MONTAGEM', [
        '1. Sequência: placa (6) nas ranhuras do berço (3) até as orelhas apoiarem → tubo (1) pela base → botão (8) no furo do tampão (4) → tampão no pino do berço → conjunto na tampa (2) até o encaixe travar → cabo pelo furo da tampa → plugue no USB-C → passa-cabo (5) no cabo e no furo.',
        f'2. Pilha axial: flange do berço apoia no ressalto da tampa; tubo preso entre flange (Z={f(FLANGE_Z0)}) e tampão (Z={f(TUBE_Z0)}). Sem cola.',
        f'3. Folgas verificadas no CAD (docs/verificacao_montagem.txt): placa–tubo ≥ 0,50; sobremolde–tampa ≥ 0,97; botão–haste S1 {f(BTN_GAP)}; LED → difusor {f(TUBE_ID/2-led_top)} mm.',
        '4. Item 7 é comprado: casca exposta ≥ 5,8 mm, sobremolde ≤ 11,6 × 6,4 (diagonal ≤ 12,3), sobremolde + bota ≤ 24,5 mm, bota ≤ Ø6,4, capa Ø3,5–4,0.',
    ], width=190)
    sh.save(os.path.join(OUT, 'LXP-A00_conjunto'))


if __name__ == '__main__':
    d_asm()
