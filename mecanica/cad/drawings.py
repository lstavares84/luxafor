"""Gera os desenhos tecnicos (PDF/PNG/DXF) em ../desenhos."""
import os, sys
from build123d import *
from params import *
from parts import *
from drafting import Sheet, View

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'desenhos')
os.makedirs(OUT, exist_ok=True)
FRONT = ((0, -1, 0), (0, 0, 1))      # observador em +Y (frente, lado dos LEDs)
TOP = ((0, 0, -1), (0, 1, 0))        # observador acima
BOTTOM = ((0, 0, 1), (0, -1, 0))     # observador abaixo
LEFT = ((1, 0, 0), (0, 0, 1))        # observador a esquerda (-X) -> vista colocada a direita (1o diedro)
ISO = ((-0.55, -0.75, -0.45), (0, 0, 1))
HALF = Pos(0, -100, 100) * Box(400, 200, 400)   # mantem y <= 0
SEC = ((0, 0, 0), (0, 1, 0))
DENS = dict(tube=1.20, plug=1.20, carrier=1.20, cap=2.70, grommet=1.10, plunger=1.20)
f = lambda v: f'{v:.2f}'.rstrip('0').rstrip('.').replace('.', ',')


def iso_small(sh, shape, origin, scale, center):
    View(sh, shape, *ISO, origin=origin, scale=scale, hidden=False, center=center, label=None)


# ======================================================== P01 tubo
def d_tube():
    p = tube()
    sh = Sheet('A4', 'LXP-P01', 'P01 Tubo difusor', 'PC opalino grau difusor, extrudado', 'Fosco externo (jateado #220 ou textura MT-11010)', '2:1', p.volume / 1000 * DENS['tube'])
    s = 2.0
    v = View(sh, p & HALF, *FRONT, origin=(65, 122), scale=s, section=SEC, center=(0, 0, 26))
    sh.text(65, 192, 'CORTE A-A', 3.5, ha='center', weight='bold')
    sh.centerline(v.map((0, 0, 0)), v.map((0, 0, 52)))
    sh.dim(v.map((8, 0, 50)), v.map((-8, 0, 50)), 9, f'Ø{f(TUBE_OD)} ±0,15')
    sh.dim(v.map((6.5, 0, 2)), v.map((-6.5, 0, 2)), -8, f'Ø{f(TUBE_ID)} ±0,15')
    sh.dim(v.map((-8, 0, 2)), v.map((-8, 0, 50)), 9, f'{f(TUBE_L)} ±0,2', orient='v')
    sh.leader(v.map((-7.25, 0, 49.6)), (108, 180), 'Quebrar cantos 0,2×45° (int./ext.)')
    t = View(sh, p, *TOP, origin=(160, 140), scale=s, center=(0, 0, 0))
    sh.text(160, 118, 'VISTA B (de cima)', 3.0, ha='center', va='top', weight='bold')
    sh.centerline((136, 140), (184, 140)); sh.centerline((160, 116 + 2), (160, 164))
    sh.leader((160 - 4.6 * s, 140 + 4.6 * s), (185, 172), 'Concentricidade ID/OD ≤ 0,15', ha='left') if False else sh.leader((160 + 5.5 * s, 140 + 5.5 * s), (190, 172), 'Concentricidade ID/OD ≤ 0,15')
    sh.cut_line((160 + 10 * s, 140), (160 - 10 * s, 140), 'A', (0, -1))
    iso_small(sh, p, (245, 150), 1.3, (0, 0, 26))
    sh.notes(112, 104, 'NOTAS', [
        '1. Tubo extrudado em PC opalino (ex.: Makrolon/Lexan grau difusor ou equivalente); transmitância alvo 50–65 %.',
        '2. Corte em serra/fresa, esquadro ≤ 0,1 mm, sem rebarba; faces de corte acetinadas.',
        '3. Superfície externa: jateado fino (óxido de alumínio #220) ou tubo com textura fosca de fábrica.',
        '4. Retilineidade ≤ 0,1 mm em 48 mm; ovalização ≤ 0,15 mm.',
        '5. Preso axialmente entre a flange do berço (P03) e o tampão (P04): sem cola.',
        '6. Difusão a validar com amostra: LEDs não devem aparecer como pontos a 0,5 m.',
    ])
    sh.save(os.path.join(OUT, 'LXP-P01_tubo_difusor'))


# ======================================================== P02 tampa
def d_cap():
    p = cap()
    sh = Sheet('A4', 'LXP-P02', 'P02 Tampa (usinada)', 'Al 6061-T6, barra Ø20/Ø22', 'Microesfera + anodização tipo II preta fosca, Ra ≤ 1,6 µm', '2:1', p.volume / 1000 * DENS['cap'])
    s = 2.0
    O = (62, 128)
    v = View(sh, p & HALF, *FRONT, origin=O, scale=s, section=SEC, center=(0, 0, 62))
    sh.text(O[0], 186, 'CORTE A-A', 3.5, ha='center', weight='bold')
    sh.centerline(v.map((0, 0, CAP_Z0 - 2)), v.map((0, 0, CAP_TOP + 2)))
    R = CAP_OD / 2
    sh.dim(v.map((R, 0, CAP_TOP)), v.map((-R, 0, CAP_TOP)), 6, f'Ø{f(CAP_OD)} -0,1')
    sh.dim(v.map((TOP_HOLE_D/2, 0, CAP_TOP)), v.map((-TOP_HOLE_D/2, 0, CAP_TOP)), 14, f'Ø{f(TOP_HOLE_D)} H9')
    sh.dim(v.map((-R, 0, CAP_Z0)), v.map((-R, 0, CAP_TOP)), 8, f'{f(CAP_L)} ±0,1', orient='v')
    sh.dim(v.map((-CB_D/2, 0, CAP_Z0)), v.map((-CB_D/2, 0, CAP_Z0 + CB_DEPTH)), 22, f'{f(CB_DEPTH)} +0,05/0', orient='v')
    sh.dim(v.map((CB_D/2, 0, CAP_Z0)), v.map((-CB_D/2, 0, CAP_Z0)), -8, f'Ø{f(CB_D)} +0,10/0')
    sh.dim(v.map((BORE_D/2, 0, BORE_Z0 + 10)), v.map((-BORE_D/2, 0, BORE_Z0 + 10)), 0.01, f'Ø{f(BORE_D)} ±0,1')
    sh.dim(v.map((R, 0, BORE_Z1)), v.map((R, 0, CAP_TOP)), -7, f'{f(TOP_WALL)}', orient='v', side='out')
    gz = FLANGE_Z0 + 1.0 - SNAP_GROOVE_W / 2
    sh.dim(v.map((R, 0, CAP_Z0)), v.map((R, 0, gz)), -7, f'{f(gz-CAP_Z0)} ±0,05', orient='v')
    sh.leader(v.map((-SNAP_GROOVE_D/2 + 0.1, 0, gz + SNAP_GROOVE_W/2)), (104, 70), f'Ranhura interna Ø{f(SNAP_GROOVE_D)} ±0,05 × {f(SNAP_GROOVE_W)} +0,1/0')
    sh.leader(v.map((-R + 0.45, 0, CAP_TOP - 0.45)), (100, 176), f'R{f(CAP_TOP_R)}')
    t = View(sh, p, *TOP, origin=(O[0], 46), scale=s, center=(0, 0, 0))
    sh.text(O[0], 24, 'VISTA B (de cima)', 3.0, ha='center', va='top', weight='bold')
    sh.centerline((O[0] - 23, 46), (O[0] + 23, 46)); sh.centerline((O[0], 46 - 22), (O[0], 46 + 22))
    sh.cut_line((O[0] + 11.5 * s, 46), (O[0] - 11.5 * s, 46), 'A', (0, -1))
    w2 = View(sh, p, *BOTTOM, origin=(150, 160), scale=s, center=(0, 0, 0))
    sh.text(150, 186, 'VISTA C (de baixo)', 3.0, ha='center', weight='bold')
    sh.centerline((150 - 23, 160), (150 + 23, 160)); sh.centerline((150, 160 - 23), (150, 160 + 23))
    iso_small(sh, p, (240, 162), 1.6, (0, 0, 62))
    y = sh.notes(112, 134, 'NOTAS', [
        '1. Torneada em 6061-T6; rebaixo, ranhura e furos concêntricos ao Ø externo ≤ 0,05. Chanfro externo inferior 0,3×45°.',
        '2. Anodização tipo II preta selada (MIL-A-8625 T.II Cl.2, 10–15 µm), aspecto fosco por jato de microesfera.',
        '3. Tubo P01 Ø16 ±0,15 no rebaixo Ø16,25: folga 0,10–0,50 (posiciona, não aperta).',
        '4. Flange do berço Ø16 -0,05/-0,10; dentes R8,45 travam na ranhura Ø17.',
        '5. Furo Ø12,8 passa um plugue USB-C padrão (≤ 12,3 × 6,8 mm); vedado pelo passa-cabo P05.',
        '6. Gravação a laser opcional no topo, após anodizar.',
    ])
    y = sh.table(112, y - 2, [('Variante', 34), ('Ø rebaixo', 22), ('Ø ranhura', 22), ('Ø cavidade', 22), ('Ø furo sup.', 24)], [
        ['P02 Al usinado', f(CB_D), f(SNAP_GROOVE_D), f(BORE_D), f(TOP_HOLE_D)],
        ['P02b impressa', f(CB_D+2*PRINT_EXTRA), f(SNAP_GROOVE_D+2*PRINT_EXTRA), f(BORE_D+2*PRINT_EXTRA), f(TOP_HOLE_D+2*PRINT_EXTRA)],
    ], rh=4.6, ts=2.0)
    sh.text(112, y - 1.5, 'P02b (protótipo): MJF PA12 tingido preto ou SLA resina preta fosca; demais cotas iguais.', 1.9, va='top')
    sh.save(os.path.join(OUT, 'LXP-P02_tampa'))


# ======================================================== P03 berco
def d_carrier():
    p = carrier()
    sh = Sheet('A4', 'LXP-P03', 'P03 Berço da placa', 'PC branco alta refletância, injetado', 'SPI B-1 nas faces frontais; resto VDI 24', '2:1 (C 3:1)', p.volume / 1000 * DENS['carrier'])
    s = 2.0
    v = View(sh, p, *FRONT, origin=(55, 116), scale=s, center=(0, 0, 27), hidden=False)
    sh.text(55, 186, 'VISTA A (frente)', 3.0, ha='center', weight='bold')
    sh.centerline(v.map((0, 0, 0)), v.map((0, 0, 54)))
    sh.dim(v.map((FLANGE_D/2, 0, FLANGE_Z0 + FLANGE_T)), v.map((-FLANGE_D/2, 0, FLANGE_Z0 + FLANGE_T)), 6, f'Ø{f(FLANGE_D)} -0,05/-0,10')
    sh.dim(v.map((-CAR_R, 0, CAR_Z0)), v.map((-CAR_R, 0, FLANGE_Z0)), 14, f'{f(FLANGE_Z0-CAR_Z0)} ±0,1', orient='v')
    sh.dim(v.map((-FLANGE_D/2, 0, FLANGE_Z0)), v.map((-FLANGE_D/2, 0, FLANGE_Z0 + FLANGE_T)), 6, f'{f(FLANGE_T)}', orient='v', side='out')
    sh.dim(v.map((GROOVE_X_OUT, 0, 30)), v.map((-GROOVE_X_OUT, 0, 30)), 0.01, f'{f(2*GROOVE_X_OUT)} +0,1/0', ts=2.2)
    sh.dim(v.map((CAR_R, 0, CAR_Z0)), v.map((CAR_R, 0, PCB_Z0)), -6, f'{f(PCB_Z0-CAR_Z0)}', orient='v', side='out')
    sh.dim(v.map((CAR_R, 0, CAR_Z0 - SOCKET_DEPTH + 0.2)), v.map((CAR_R, 0, CAR_Z0)), -14, f'{f(SOCKET_DEPTH-0.2)}', orient='v', side='out')
    w = View(sh, p, *LEFT, origin=(110, 116), scale=s, center=(0, 0, 27), hidden=True)
    sh.text(110, 186, 'VISTA B (esq.)', 3.0, ha='center', weight='bold')
    s3 = 3.0
    t = View(sh, p, *TOP, origin=(175, 150), scale=s3, center=(0, 0, 0), hidden=True)
    sh.text(175, 186, 'VISTA C (de cima) 3:1', 3.0, ha='center', weight='bold')
    sh.leader(t.map((-GROOVE_X_OUT + 0.1, PCB_Y0 + PCB_T/2, 60)), (205, 120), f'Ranhura {f(GROOVE_W)} +0,05/0 (placa 0,8)')
    sh.leader(t.map((POST_POS[0] + 1.0, POST_POS[1] - 1.0, 60)), (205, 113), f'Pino Ø{f(POST_D)} c/ 3 nervuras (press-fit)')
    sh.leader(t.map((-1.0, -SNAP_R + 0.1, 60)), (205, 106), f'Dente de encaixe R{f(SNAP_R)} (2×)')
    sh.leader(t.map((-(PCB_W/2 + 0.2 + EAR_SLOT_X_OUT)/2, PCB_Y0 + PCB_T/2, 60)), (205, 99), f'Fenda orelha X±{f(EAR_SLOT_X_OUT)}, piso Z{f(PCB_TOP_Z-EAR_H)} (2×)')
    sh.leader(t.map((5.6, PCB_Y0 + PCB_T + 1.5, 60)), (205, 92), 'Recorte flange 12,2 (placa+USB-C)')
    iso_small(sh, p, (262, 160), 1.1, (0, 0, 27))
    sh.notes(140, 85, 'NOTAS', [
        f'1. Placa SIGNA rev D entra pelas ranhuras a partir do topo; as orelhas (15,2 de largura total) apoiam no piso das fendas da flange (Z={f(PCB_TOP_Z-EAR_H)}) = batente axial.',
        f'2. Borda inferior da placa fica {f(GROOVE_FLOOR_GAP)} acima do fundo da ranhura (sem hiperestático). A tampa P02 fecha as orelhas por cima (folga {f(EAR_GAP_TOP)}).',
        '3. Alívio traseiro 9,6 × 0,7 para os pinos THT do USB-C, atravessando também a flange (rev B).',
        '4. Face frontal branca atua como refletor atrás da placa. Saída de molde 0,5–1°.',
        '5. Protótipo: SLA branco ou MJF PA12 branco.',
    ], width=145)
    sh.save(os.path.join(OUT, 'LXP-P03_berco'))


# ======================================================== P04 tampao
def d_plug():
    p = end_plug()
    sh = Sheet('A4', 'LXP-P04', 'P04 Tampão inferior', 'PC opalino (mesmo grau do tubo), injetado', 'Externo fosco igual ao tubo (MT-11010 no molde)', '3:1', p.volume / 1000 * DENS['plug'])
    s = 3.0
    HX = Pos(100, 0, 0) * Box(200, 400, 400)
    v = View(sh, p & HX, *LEFT, origin=(70, 158), scale=s, section=((0, 0, 0), (1, 0, 0)), center=(0, 0, 3))
    sh.text(70, 190, 'CORTE A-A', 3.5, ha='center', weight='bold')
    sh.centerline(v.map((0, 0, -1)), v.map((0, 0, 7)))
    sh.dim(v.map((0, 8, 0)), v.map((0, -8, 0)), -7, f'Ø{f(PLUG_FL_D)} -0,1')
    sh.dim(v.map((0, PLUG_SPIG_D/2, 6)), v.map((0, -PLUG_SPIG_D/2, 6)), 7, f'Ø{f(PLUG_SPIG_D)} ±0,03')
    sh.dim(v.map((0, -8, 0)), v.map((0, -8, PLUG_FL_T)), 6, f'{f(PLUG_FL_T)}', orient='v', side='out')
    sh.dim(v.map((0, -8, 0)), v.map((0, -8, PLUG_FL_T + PLUG_SPIG_L)), 16, f'{f(PLUG_FL_T + PLUG_SPIG_L)} ±0,05', orient='v')
    sh.leader(v.map((0, 7.7, 0.3)), (32, 135), f'R{f(PLUG_EDGE_R)}', ha='right')
    sh.leader(v.map((0, BTN_Y - BTN_HOLE_D/2, 1.0)), (122, 172), f'Furo do botão Ø{f(BTN_HOLE_D)} +0,05/0, chanfro 0,25')
    sh.leader(v.map((0, BTN_Y - BTN_CB_D/2, PLUG_TOP - 0.5)), (122, 180), f'Rebaixo Ø{f(BTN_CB_D)} × {f(BTN_CB_DEPTH)} (colar do P06)')
    t = View(sh, p, *TOP, origin=(70, 88), scale=s, center=(0, 0, 0))
    sh.text(70, 48, 'VISTA B (de cima)', 3.0, ha='center', va='top', weight='bold')
    sh.centerline((70 - 28, 88), (70 + 28, 88)); sh.centerline((70, 88 - 27), (70, 88 + 28))
    sh.cut_line((70, 88 + 9.5 * s), (70, 88 - 9.5 * s), 'A', (1, 0))
    sh.leader(t.map((POST_POS[0] - SOCKET_D/2*0.7, POST_POS[1] - SOCKET_D/2*0.7, 6)), (112, 66), f'Furo Ø{f(SOCKET_D)} +0,05/0 × {f(SOCKET_DEPTH)} prof.')
    sh.dim(t.map((0, 0, 6)), t.map((0, POST_POS[1], 6)), -40, f'{f(-POST_POS[1])} ±0,05', orient='v')
    iso_small(sh, p, (245, 160), 2.5, (0, 0, 3))
    sh.notes(140, 128, 'NOTAS', [
        '1. Ajuste no tubo (ID 13 ±0,15): deslizante leve a leve interferência; o tubo é preso axialmente pela pilha flange P03 / tampão P04.',
        '2. Pino do berço Ø3,0 com nervuras em furo Ø2,9: interferência 0,05–0,15 (press-fit, sem cola). Desmontável com alavanca.',
        '3. Ponto de injeção: centro da face interna (oculto), fora do furo do botão.',
        f'4. Rev B: furo Ø{f(BTN_HOLE_D)} coaxial com a haste do S1 (Y={f(BTN_Y)}); o botão P06 entra por cima antes de montar o tampão.',
        '5. Protótipo: SLA resina branca translúcida + jateado.',
    ], width=145)
    sh.save(os.path.join(OUT, 'LXP-P04_tampao'))


# ======================================================== P05 passa-cabo
def d_grommet():
    p = grommet()
    sh = Sheet('A4', 'LXP-P05', 'P05 Passa-cabo bipartido', 'TPE 60 Shore A preto (ou silicone 60A)', 'Fosco VDI 30; fenda longitudinal 0,3', '3:1', p.volume / 1000 * DENS['grommet'])
    s = 3.0
    zc = (BORE_Z1 - GR_BARB_H + CAP_TOP + GR_FL_T + GR_BOOT_L) / 2
    v = View(sh, p & (Pos(-100, 0, 0) * Box(200, 400, 400) if False else HALF), *FRONT, origin=(80, 115), scale=s, section=SEC, center=(0, 0, zc))
    sh.text(80, 152, 'CORTE A-A', 3.5, ha='center', weight='bold')
    sh.centerline(v.map((0, 0, BORE_Z1 - 3)), v.map((0, 0, CAP_TOP + 12)))
    sh.dim(v.map((GR_FL_D/2, 0, CAP_TOP)), v.map((-GR_FL_D/2, 0, CAP_TOP)), -26, f'Ø{f(GR_FL_D)}')
    sh.dim(v.map((GR_BODY_D/2, 0, BORE_Z1 + 1.5)), v.map((-GR_BODY_D/2, 0, BORE_Z1 + 1.5)), 0.01, f'Ø{f(GR_BODY_D)}')
    sh.dim(v.map((GR_BARB_D/2, 0, BORE_Z1 - GR_BARB_H)), v.map((-GR_BARB_D/2, 0, BORE_Z1 - GR_BARB_H)), -8, f'Ø{f(GR_BARB_D)} (garra)')
    top = CAP_TOP + GR_FL_T + GR_BOOT_L
    sh.dim(v.map((GR_BOOT_D1/2, 0, top)), v.map((-GR_BOOT_D1/2, 0, top)), 6, f'Ø{f(GR_BOOT_D1)}')
    sh.dim(v.map((-GR_FL_D/2, 0, BORE_Z1 - GR_BARB_H)), v.map((-GR_FL_D/2, 0, top)), 12, f'{f(top-BORE_Z1+GR_BARB_H)}', orient='v')
    sh.dim(v.map((GR_FL_D/2, 0, BORE_Z1)), v.map((GR_FL_D/2, 0, CAP_TOP)), -8, f'{f(TOP_WALL)}*', orient='v')
    sh.leader(v.map((-GR_CABLE_D/2, 0, top - 4)), (130, 135), f'Furo do cabo Ø{f(GR_CABLE_D)} (cabo Ø3,5–4,0)')
    sh.leader(v.map((-GR_BOOT_RELIEF_D/2, 0, BORE_Z1 + 1)), (130, 85), f'Alívio Ø{f(GR_BOOT_RELIEF_D)} (bota do plugue)')
    t = View(sh, p, *TOP, origin=(80, 45), scale=s, center=(0, 0, 0))
    sh.text(80, 16, 'VISTA SUPERIOR (B)', 3.0, ha='center', weight='bold')
    sh.leader(t.map((0, 5, top)), (130, 55), f'Fenda {f(GR_SLIT)} até o furo (montagem lateral)')
    iso_small(sh, p, (245, 150), 2.4, (0, 0, zc))
    sh.notes(150, 125, 'NOTAS', [
        '* espessura da parede da tampa P02.',
        '1. Abre-se pela fenda e envolve o cabo; empurrar no furo',
        '   Ø12,8 da tampa até a garra travar sob a parede.',
        '2. Cabo do usuário passa antes pelo furo da tampa.',
        '3. Carga do produto (~20 g) fica no conector USB-C',
        '   (retenção ≥ 8 N) + atrito do passa-cabo.',
    ])
    sh.save(os.path.join(OUT, 'LXP-P05_passa_cabo'))


# ======================================================== P06 botao
def d_plunger():
    p = Pos(0, -BTN_Y, BTN_PROUD) * plunger()     # eixo no Z, ponta em Z=0
    sh = Sheet('A4', 'LXP-P06', 'P06 Botão (pino de acionamento)', 'PC opalino (mesmo grau do tampão), injetado', 'Fosco; ponta abaulada R0,6', '5:1', p.volume / 1000 * DENS['plunger'])
    s = 5.0
    L = SW_TIP_Z - BTN_GAP + BTN_PROUD
    zc = PLUG_TOP - BTN_CB_DEPTH + BTN_PROUD
    v = View(sh, p, *FRONT, origin=(70, 110), scale=s, center=(0, 0, L / 2), hidden=False)
    sh.text(70, 172, 'VISTA A (frente)', 3.0, ha='center', weight='bold')
    sh.centerline(v.map((0, 0, -1)), v.map((0, 0, L + 1)))
    sh.dim(v.map((BTN_SHAFT_D/2, 0, 1.5)), v.map((-BTN_SHAFT_D/2, 0, 1.5)), 0.01, f'Ø{f(BTN_SHAFT_D)} -0,05/0', ts=2.2)
    sh.dim(v.map((BTN_COLLAR_D/2, 0, zc + BTN_COLLAR_T)), v.map((-BTN_COLLAR_D/2, 0, zc + BTN_COLLAR_T)), 8, f'Ø{f(BTN_COLLAR_D)} ±0,05')
    sh.dim(v.map((BTN_PUSH_D/2, 0, L)), v.map((-BTN_PUSH_D/2, 0, L)), 6, f'Ø{f(BTN_PUSH_D)}')
    sh.dim(v.map((-BTN_COLLAR_D/2, 0, 0)), v.map((-BTN_COLLAR_D/2, 0, zc)), 12, f'{f(zc)}', orient='v')
    sh.dim(v.map((-BTN_COLLAR_D/2, 0, zc)), v.map((-BTN_COLLAR_D/2, 0, zc + BTN_COLLAR_T)), 6, f'{f(BTN_COLLAR_T)}', orient='v', side='out')
    sh.dim(v.map((BTN_COLLAR_D/2, 0, 0)), v.map((BTN_COLLAR_D/2, 0, L)), -14, f'{f(L)} ±0,05', orient='v')
    iso_small(sh, p, (245, 150), 5.0, (0, 0, L / 2))
    sh.notes(140, 110, 'NOTAS', [
        f'1. Montagem: entra por cima no furo Ø{f(BTN_HOLE_D)} do tampão P04; o colar apoia por gravidade no rebaixo Ø{f(BTN_CB_D)} × {f(BTN_CB_DEPTH)}.',
        f'2. Ponta sai {f(BTN_PROUD)} abaixo do tampão (achável no tato). Empurrador fica {f(BTN_GAP)} abaixo da haste do S1 (pior caso 0,0–0,8).',
        f'3. Curso total até atuar o S1: {f(BTN_GAP + SW_TRAVEL)} nominal (≤ 1,0 pior caso). Força: 1,6 N do S1 (ALPS SKRTLAE010).',
        '4. Material igual ao tampão: some visualmente quando os LEDs acendem.',
        '5. Protótipo: SLA resina translúcida; tolerância do Ø3,0 crítica (folga radial 0,1).',
    ], width=145)
    sh.save(os.path.join(OUT, 'LXP-P06_botao'))


if __name__ == '__main__':
    which = sys.argv[1:] or ['tube', 'cap', 'carrier', 'plug', 'grommet', 'plunger', 'asm']
    for w in which:
        globals()['d_' + w]() if 'd_' + w in globals() else __import__('drawings_asm').d_asm()
        print('ok', w)
