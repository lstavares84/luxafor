"""Geometria parametrica das pecas (build123d)."""
from build123d import *
from params import *
import math


def tube():
    p = Cylinder(TUBE_OD / 2, TUBE_L, align=(Align.CENTER, Align.CENTER, Align.MIN)) - \
        Cylinder(TUBE_ID / 2, TUBE_L, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return Pos(0, 0, TUBE_Z0) * p


def end_plug():
    fl = Cylinder(PLUG_FL_D / 2, PLUG_FL_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    fl = fillet(fl.edges().group_by(Axis.Z)[0], PLUG_EDGE_R)
    sp = Pos(0, 0, PLUG_FL_T) * Cylinder(PLUG_SPIG_D / 2, PLUG_SPIG_L, align=(Align.CENTER, Align.CENTER, Align.MIN))
    sp = chamfer(sp.edges().group_by(Axis.Z)[-1], 0.3)
    p = fl + sp
    # furo para o pino do berco
    x, y = POST_POS
    p -= Pos(x, y, PLUG_FL_T + PLUG_SPIG_L - SOCKET_DEPTH) * Cylinder(SOCKET_D / 2, SOCKET_DEPTH, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # rev B: furo do botao P06 (eixo = eixo da haste do S1) + rebaixo do colar no topo
    p -= Pos(0, BTN_Y, -1) * Cylinder(BTN_HOLE_D / 2, PLUG_FL_T + PLUG_SPIG_L + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    p -= Pos(0, BTN_Y, PLUG_TOP - BTN_CB_DEPTH) * Cylinder(BTN_CB_D / 2, BTN_CB_DEPTH + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    p = chamfer(p.edges().filter_by(GeomType.CIRCLE).group_by(Axis.Z)[0].filter_by(lambda e: abs(e.radius - BTN_HOLE_D / 2) < 1e-3), 0.25)
    # cavidade conica rasa no topo (espalha a luz para o fundo)
    p -= Pos(0, 0, PLUG_FL_T + PLUG_SPIG_L) * Cone(0.1, 4.5, 1.2, align=(Align.CENTER, Align.CENTER, Align.MAX)) if False else Part()
    return p


def carrier():
    L = FLANGE_Z0 - CAR_Z0
    env = Cylinder(CAR_R, L, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # espinha atras da placa (y <= face inferior da placa)
    y_front = PCB_Y0 - 0.05
    spine = env & Pos(0, (y_front - 10) / 2 + 0, L / 2) * Box(20, 10 + y_front + 10 - 10, L) if False else None
    spine = env & Pos(0, y_front - 5, L / 2) * Box(20, 10, L)
    # trilhos laterais
    rails = Part()
    for s in (-1, 1):
        r = env & Pos(s * (LIP_X + 5), (PCB_Y0 + RAIL_Y_TOP) / 2, L / 2) * Box(10, RAIL_Y_TOP - PCB_Y0, L)
        rails += r
    body = spine + rails
    # ranhuras da placa (comecam em Z da borda da placa)
    gz0 = PCB_Z0 - GROOVE_FLOOR_GAP - CAR_Z0
    for s in (-1, 1):
        gx = (GROOVE_X_IN + GROOVE_X_OUT) / 2
        body -= Pos(s * gx, PCB_Y0 + PCB_T / 2, gz0 + L) * Box(GROOVE_X_OUT - GROOVE_X_IN, GROOVE_W, 2 * L)
    # alivio para pinos THT do receptaculo USB-C (face traseira da placa)
    body -= Pos(0, PCB_Y0 - 0.3, (PCB_TOP_Z - 9.0 - CAR_Z0) + 5) * Box(9.6, 0.7, 10)
    body = Pos(0, 0, CAR_Z0) * body
    # flange com recorte para placa + USB-C
    fl = Pos(0, 0, FLANGE_Z0) * Cylinder(FLANGE_D / 2, FLANGE_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    fl -= Pos(0, (PCB_Y0 - 0.2 + PCB_Y0 + PCB_T + USB_TOP + 0.3) / 2, FLANGE_Z0 + 1) * Box(12.2, (PCB_T + USB_TOP + 0.5), 4)   # rev B: 12,2 (raio interno da orelha)
    # rev B: fendas das orelhas da placa (fundo = batente axial; a tampa fecha por cima)
    ear_floor = PCB_TOP_Z - EAR_H
    for s in (-1, 1):
        xa, xb = PCB_W / 2 + 0.2, EAR_SLOT_X_OUT
        fl -= Pos(s * (xa + xb) / 2, PCB_Y0 + PCB_T / 2, ear_floor + 2) * Box(xb - xa, GROOVE_W, 4)
    # dentes de encaixe (frente/tras) com fendas de flexao
    for s in (-1, 1):
        tooth = Pos(0, s * (SNAP_R + 7.5) / 2, FLANGE_Z0 + 1.0) * Box(SNAP_W, SNAP_R - 7.5, SNAP_H)
        tooth &= Pos(0, 0, FLANGE_Z0) * Cylinder(SNAP_R, FLANGE_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
        fl += tooth
        for sx in (-1, 1):
            fl -= Pos(sx * (SNAP_W / 2 + 0.5), s * 7.0, FLANGE_Z0 + 1) * Box(0.5, 3.2, 4)
    body += fl
    # rev B: o alivio dos pinos THT do USB-C atravessa tambem a flange (placa subiu 0,75)
    body -= Pos(0, PCB_Y0 - 0.3, PCB_TOP_Z - 4.0) * Box(9.6, 0.7, 10)
    # pino inferior (press-fit no tampao)
    x, y = POST_POS
    post = Pos(x, y, CAR_Z0 - SOCKET_DEPTH + 0.2) * Cylinder(POST_D / 2, SOCKET_DEPTH - 0.2 + 0.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
    post = chamfer(post.edges().group_by(Axis.Z)[0], 0.3)
    body += post
    return body


def cap(printed=False):
    e = PRINT_EXTRA if printed else 0.0
    c = Pos(0, 0, CAP_Z0) * Cylinder(CAP_OD / 2, CAP_L, align=(Align.CENTER, Align.CENTER, Align.MIN))
    c = fillet(c.edges().group_by(Axis.Z)[-1], CAP_TOP_R)
    c = chamfer(c.edges().group_by(Axis.Z)[0], CAP_BOT_CH)
    # rebaixo do tubo + flange
    c -= Pos(0, 0, CAP_Z0) * Cylinder(CB_D / 2 + e, CB_DEPTH, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # ranhura interna do encaixe
    gz = FLANGE_Z0 + 1.0 - SNAP_GROOVE_W / 2
    c -= Pos(0, 0, gz) * Cylinder(SNAP_GROOVE_D / 2 + e, SNAP_GROOVE_W + e, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # cavidade do plugue
    c -= Pos(0, 0, BORE_Z0 - 0.01) * Cylinder(BORE_D / 2 + e, BORE_Z1 - BORE_Z0 + 0.01, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # furo superior (passa-cabo)
    c -= Pos(0, 0, BORE_Z1 - 0.01) * Cylinder(TOP_HOLE_D / 2 + e, TOP_WALL + 0.1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # chanfro de entrada do rebaixo
    return c


def grommet():
    zb = BORE_Z1 - GR_BARB_H
    g = Pos(0, 0, zb) * Cone(GR_BARB_D / 2 - 0.4, GR_BARB_D / 2, GR_BARB_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    g += Pos(0, 0, BORE_Z1) * Cylinder(GR_BODY_D / 2, TOP_WALL, align=(Align.CENTER, Align.CENTER, Align.MIN))
    g += Pos(0, 0, CAP_TOP) * Cylinder(GR_FL_D / 2, GR_FL_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    g += Pos(0, 0, CAP_TOP + GR_FL_T) * Cone(GR_BOOT_D0 / 2, GR_BOOT_D1 / 2, GR_BOOT_L, align=(Align.CENTER, Align.CENTER, Align.MIN))
    top = CAP_TOP + GR_FL_T + GR_BOOT_L
    g -= Pos(0, 0, zb - 1) * Cylinder(GR_CABLE_D / 2, top - zb + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    g -= Pos(0, 0, zb - 0.01) * Cylinder(GR_BOOT_RELIEF_D / 2, GR_BARB_H + TOP_WALL, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # fenda longitudinal (montagem lateral no cabo)
    g -= Pos(0, 5, (zb + top) / 2) * Box(GR_SLIT, 10, top - zb + 2)
    return g


def plunger():
    """P06 botao: haste pelo tampao, colar retido no rebaixo, empurrador ate a haste do S1."""
    z0 = -BTN_PROUD
    zc = PLUG_TOP - BTN_CB_DEPTH                     # piso do rebaixo (colar apoia por gravidade)
    shaft = Pos(0, BTN_Y, z0) * Cylinder(BTN_SHAFT_D / 2, zc - z0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    shaft = fillet(shaft.edges().group_by(Axis.Z)[0], 0.6)   # ponta abaulada (tato)
    collar = Pos(0, BTN_Y, zc) * Cylinder(BTN_COLLAR_D / 2, BTN_COLLAR_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    ztop = SW_TIP_Z - BTN_GAP
    push = Pos(0, BTN_Y, zc + BTN_COLLAR_T) * Cylinder(BTN_PUSH_D / 2, ztop - zc - BTN_COLLAR_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return shaft + collar + push


def _stadium_prism(w, h, z0, length, y):
    return Pos(0, y, z0) * extrude(SlotOverall(w, h), amount=length)


def cable_plug():
    """Plugue USB-C tipico: casca oca 8,25 x 2,4 inserida 6,2 mm + sobremolde + alivio."""
    sw, sh, sl = PLUG_SHELL
    z_tip = USB_MOUTH_Z - PLUG_DEPTH
    shell = _stadium_prism(sw, sh, z_tip, sl, USB_Y)
    cw, ch = PLUG_CAV
    shell -= Pos(0, USB_Y, z_tip - 0.01) * extrude(RectangleRounded(cw, ch, 0.25), amount=sl - 0.6)
    shell.label = 'C01_plugue_casca'
    bw, bt, bl = PLUG_BODY
    z_ov = z_tip + sl
    ov = Pos(0, USB_Y, z_ov) * extrude(RectangleRounded(bw, bt, PLUG_BODY_R), amount=bl)
    ov = fillet(ov.edges().group_by(Axis.Z)[-1], 1.2)
    ov.label = 'C01_sobremolde'
    d0, d1, blen = BOOT
    boot = Pos(0, USB_Y, z_ov + bl - 0.5) * Cone(d0 / 2, d1 / 2, blen + 0.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
    boot.label = 'C01_alivio'
    return shell, ov, boot


def cable_path(full=True):
    """Trajeto do cabo: sobe pelo passa-cabo, curva por cima da borda do monitor e desce atras."""
    z0 = CABLE_Z0
    pts = [Line((0, USB_Y, z0), (0, USB_Y, CABLE_RISE))]
    if full:
        r1, hz, r2, down = 12.0, 26.0, 10.0, 90.0
        a1 = CenterArc((0, USB_Y - r1, CABLE_RISE), r1, 0, 90) if False else None
        p0 = Vector(0, USB_Y, CABLE_RISE)
        arc1 = ThreePointArc(p0, p0 + Vector(0, -r1 * (1 - 0.7071), r1 * 0.7071), p0 + Vector(0, -r1, r1))
        p1 = p0 + Vector(0, -r1, r1)
        p2 = p1 + Vector(0, -hz, 0)
        ln = Line(p1, p2)
        arc2 = ThreePointArc(p2, p2 + Vector(0, -r2 * 0.7071, -r2 * (1 - 0.7071)), p2 + Vector(0, -r2, -r2))
        p3 = p2 + Vector(0, -r2, -r2)
        pts += [arc1, ln, arc2, Line(p3, p3 + Vector(0, 0, -down))]
    return Wire(pts)


def cable(full=True):
    path = cable_path(full)
    prof = Plane(origin=path @ 0, z_dir=path % 0) * Circle(CABLE_D / 2)
    c = sweep(prof, path)
    c.label = 'C01_cabo'
    return c


def cable_length(full=True):
    return cable_path(full).length


BOARD_STEP = __import__('os').path.join(__import__('os').path.dirname(__file__), 'board', 'signa-revD-pcb.step')


def board():
    s = import_step(BOARD_STEP)
    # STEP do KiCad: X 100..111, Y -144,65..-100 (borda do botao em -100), face da placa Z 0..0,8
    b = Pos(-105.5, PCB_Y0, -93.0 + (PCB_Z0 - 7.0)) * (Rot(-90, 0, 0) * s)
    b.label = 'E01_placa_SIGNA_revD'
    return b
