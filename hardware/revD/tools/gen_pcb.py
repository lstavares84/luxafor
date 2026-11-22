#!/usr/bin/env python3
"""Gera hardware/indicador/luxflag.kicad_pcb (contorno, posicionamento, redes, regras JLC).

Coordenadas em mm a partir do canto superior esquerdo da placa.
Eixo Y cresce para baixo: y = 0 é o topo do aparelho, y = 44 é a ponta do USB-C.
A face de cima (F.Cu) olha para a raiz da bandeira difusora.

Uso:
  gen_pcb.py            -> gera a placa sem trilhas e exporta luxflag.dsn
  gen_pcb.py --ses ARQ  -> importa as trilhas do Freerouting, preenche os planos e salva
"""
import os
import sys

import pcbnew

from gen_sch import flat_symbol, pins_of, uid
from netlist import PARTS

HERE = os.path.dirname(os.path.abspath(__file__))
HW = os.path.dirname(HERE)
PROJ = os.path.join(HW, "project")
PCB = os.path.join(PROJ, "luxflag.kicad_pcb")
DSN = os.path.join(PROJ, "luxflag.dsn")

W, H = 11.0, 44.0          # contorno da placa (mm)
OX, OY = 100.0, 100.0      # origem na folha do KiCad
CX = W / 2

# ref: (x, y, rotação em graus, face)  face: "F" (LEDs) ou "B" (pads SWD)
PLACE = {
    # rev D: LEDs +2,2 mm (abre espaço para o botão S1 na borda de baixo)
    "D3": (CX, 5.2, 0, "F"), "D2": (CX, 12.2, 0, "F"), "D1": (CX, 19.2, 0, "F"),
    "C8": (9.1, 5.2, 90, "F"), "C7": (9.1, 12.2, 90, "F"), "C6": (9.1, 19.2, 90, "F"),
    # coluna da esquerda: buffer de nível 3,3 -> 5 V e resistor série
    "C5": (1.9, 10.6, 90, "F"), "U3": (1.9, 13.9, 90, "F"), "R3": (1.9, 17.0, 90, "F"),
    "R4": (1.9, 20.2, 90, "F"), "C2": (9.1, 21.4, 90, "F"),
    # MCU QFN-28 4x4 e desacoplamentos junto aos pinos 3/4 (VDD/VSS) e 5 (NRST)
    "U1": (CX, 25.5, 0, "F"),
    "C3": (1.5, 24.6, 90, "F"), "C4": (1.5, 27.0, 90, "F"),
    # alimentação e proteção USB
    "U2": (2.75, 31.75, 90, "F"), "U4": (8.25, 31.75, 90, "F"),
    "C1": (1.9, 34.7, 0, "F"), "R1": (4.6, 34.7, 0, "F"), "R2": (7.6, 34.7, 0, "F"),
    # USB-C: boca para baixo, sobressai 0,7 mm da borda
    "J1": (CX, H - 3.0, 0, "F"),
    # rev D: botão lateral na borda y=0 (haste para fora, eixo no centro da placa)
    "S1": (CX, 1.8, 180, "F"), "R5": (1.5, 6.4, 90, "F"),
    # face de trás: Tag-Connect TC2030 entre D3 e D2; jumper BOOT0 atrás do MCU
    "J2": (CX, 8.7, 0, "B"),
    "JP1": (CX, 21.0, 0, "B"),
    # rev D: pontos de teste na face de trás
    "TP1": (3.0, 30.5, 0, "B"), "TP2": (5.5, 30.5, 0, "B"), "TP3": (8.0, 30.5, 0, "B"),
}


# Modelos 3D: os do pacote do KiCad 9 (Debian) para passivos/SOT-23; para U1, J1, D1-D3 e S1
# (sem modelo no pacote) usamos modelos próprios gerados por tools/models3d.py a partir das
# cotas dos datasheets (lib/3d/*.step). Não afetam Gerber/BOM/CPL.
M3D = "${KIPRJMOD}/../lib/3d/"
SUBST_3D = {
    "U1": (M3D + "QFN-28_4x4_UFQFPN28.step", (1, 1, 1)),
    "J1": (M3D + "USB_C_HRO_TYPE-C-31-M-12.step", (1, 1, 1)),
    "D1": (M3D + "LED_WS2816B-2020.step", (1, 1, 1)),
    "S1": (M3D + "SW_SKRTLAE010.step", (1, 1, 1)),
}
SUBST_3D["D2"] = SUBST_3D["D3"] = SUBST_3D["D1"]


def mm(x, y):
    return pcbnew.VECTOR2I_MM(OX + x, OY + y)


def fp_path(fpid):
    lib, name = fpid.split(":")
    d = (os.path.join(HW, "lib", "indicador.pretty") if lib == "indicador"
         else f"/usr/share/kicad/footprints/{lib}.pretty")
    return d, name


def build(zones=True):
    board = pcbnew.BOARD()
    ds = board.GetDesignSettings()
    ds.SetCopperLayerCount(2)
    ds.SetBoardThickness(pcbnew.FromMM(0.8))
    # regras compatíveis com o processo padrão da JLCPCB (2 camadas)
    ds.m_TrackMinWidth = pcbnew.FromMM(0.127)
    ds.m_MinClearance = pcbnew.FromMM(0.127)
    ds.m_ViasMinSize = pcbnew.FromMM(0.45)
    ds.m_MinThroughDrill = pcbnew.FromMM(0.3)
    ds.m_HoleToHoleMin = pcbnew.FromMM(0.5)
    ds.m_CopperEdgeClearance = pcbnew.FromMM(0.3)
    nc = ds.m_NetSettings.GetDefaultNetclass()
    nc.SetTrackWidth(pcbnew.FromMM(0.2))
    nc.SetClearance(pcbnew.FromMM(0.15))
    nc.SetViaDiameter(pcbnew.FromMM(0.6))
    nc.SetViaDrill(pcbnew.FromMM(0.3))

    nets = {}

    def net(name):
        if name not in nets:
            ni = pcbnew.NETINFO_ITEM(board, name)
            board.Add(ni)
            nets[name] = ni
        return nets[name]

    for ref, (lib, sym, value, fpid, lcsc, conns, _) in PARTS.items():
        if ref.startswith("#"):
            continue
        d, name = fp_path(fpid)
        fp = pcbnew.FootprintLoad(d, name)
        assert fp, f"footprint {fpid} não encontrado"
        fp.SetFPIDAsString(fpid)
        fp.SetReference(ref)
        fp.SetValue(value)
        fp.Reference().SetVisible(False)  # placa minúscula: designadores só no Fab/CPL
        x, y, rot, side = PLACE[ref]
        fp.SetPosition(mm(x, y))
        fp.SetOrientationDegrees(rot)
        if ref in SUBST_3D:
            path, sc = SUBST_3D[ref]
            fp.Models().clear()
            m = pcbnew.FP_3DMODEL()
            m.m_Filename = path
            m.m_Scale.x, m.m_Scale.y, m.m_Scale.z = sc
            fp.Models().push_back(m)
        board.Add(fp)
        if ref == "J1":
            # remove a marca de borda da serigrafia do conector (cai sobre o contorno)
            for g in fp.GraphicalItems():
                if g.GetLayer() == pcbnew.F_SilkS and pcbnew.ToMM(g.GetBoundingBox().GetBottom()) - OY > H - 1.3:
                    g.SetLayer(pcbnew.F_Fab)
        if side == "B":
            fp.Flip(mm(x, y), pcbnew.FLIP_DIRECTION_TOP_BOTTOM)
        # pinos ocultos do USB (A9/B4/B9 = VBUS, A12/B1/B12 = GND) seguem os visíveis
        alias = {"A9": "A4", "B4": "A4", "B9": "A4", "A12": "A1", "B1": "A1", "B12": "A1"}
        fp.SetPath(pcbnew.KIID_PATH("/" + uid("sym", ref)))
        pnames = {}
        pins_of(flat_symbol(lib, sym)[1], pnames)
        for pad in fp.Pads():
            num = pad.GetNumber()
            if not num:
                continue
            key = alias.get(num, num) if ref == "J1" else num
            if key in conns and conns[key]:
                pad.SetNet(net("/" + conns[key] if not conns[key].startswith("+") else "/" + conns[key]))
            elif num in pnames:
                nm = pnames[num].replace("/", "{slash}")
                pad.SetNet(net(f"unconnected-({ref}-{nm}-Pad{num})"))

    add_outline(board)

    add_text(board)
    if zones:
        add_zones(board, net("/GND"))
    else:
        add_edge_keepout(board)
    return board


# rev D: orelhas no topo (lado do USB-C) = batente axial da placa no Pendente.
# As orelhas apoiam no fundo das fendas da flange do berço e ficam presas sob o ressalto da tampa:
# seguram o peso, a força do botão (1,6 N, para cima) e a extração do cabo (8–20 N).
EAR_X = 2.1            # quanto cada orelha passa da lateral da placa (|x| = 7,6 mm do eixo)
EAR_H = 1.0            # altura da orelha (y = 43,0..44,0)
R_OUT, R_EAR, R_IN = 1.0, 0.3, 0.5   # canto de baixo, canto da orelha, raio interno (fresa Ø1,0)


def _seg(board, a, b):
    s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(mm(*a)); s.SetEnd(mm(*b)); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(pcbnew.FromMM(0.05))
    board.Add(s)


def _arc(board, c, r, a0, a1):
    import math
    st = (c[0] + r * math.cos(math.radians(a0)), c[1] + r * math.sin(math.radians(a0)))
    md = (c[0] + r * math.cos(math.radians((a0 + a1) / 2)), c[1] + r * math.sin(math.radians((a0 + a1) / 2)))
    en = (c[0] + r * math.cos(math.radians(a1)), c[1] + r * math.sin(math.radians(a1)))
    s = pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_ARC)
    s.SetArcGeometry(mm(*st), mm(*md), mm(*en)); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(pcbnew.FromMM(0.05))
    board.Add(s)
    return st, en


def add_outline(board):
    """Contorno (y para baixo no KiCad): cantos r=1 na borda do botão (y=0); orelhas no topo (y=44)."""
    y_e = H - EAR_H
    xl, xr = -EAR_X, W + EAR_X
    # borda de baixo (y=0) e cantos r=1
    _seg(board, (R_OUT, 0), (W - R_OUT, 0))
    _arc(board, (W - R_OUT, R_OUT), R_OUT, -90, 0)
    _arc(board, (R_OUT, R_OUT), R_OUT, 180, 270)
    # laterais até o raio interno da orelha
    _seg(board, (W, R_OUT), (W, y_e - R_IN))
    _seg(board, (0, R_OUT), (0, y_e - R_IN))
    # raio interno (côncavo) lateral -> borda de baixo da orelha
    _arc(board, (W + R_IN, y_e - R_IN), R_IN, 90, 180)
    _arc(board, (-R_IN, y_e - R_IN), R_IN, 0, 90)
    # borda de baixo das orelhas
    _seg(board, (W + R_IN, y_e), (xr - R_EAR, y_e))
    _seg(board, (-R_IN, y_e), (xl + R_EAR, y_e))
    # cantos externos das orelhas
    _arc(board, (xr - R_EAR, y_e + R_EAR), R_EAR, -90, 0)
    _arc(board, (xl + R_EAR, y_e + R_EAR), R_EAR, 180, 270)
    _seg(board, (xr, y_e + R_EAR), (xr, H - R_EAR))
    _seg(board, (xl, y_e + R_EAR), (xl, H - R_EAR))
    _arc(board, (xr - R_EAR, H - R_EAR), R_EAR, 0, 90)
    _arc(board, (xl + R_EAR, H - R_EAR), R_EAR, 90, 180)
    # borda de cima (USB-C)
    _seg(board, (xl + R_EAR, H), (xr - R_EAR, H))


def add_edge_keepout(board, m=0.35):
    """Faixa proibida para trilhas/vias junto à borda (só no DSN do Freerouting,
    que não conhece a regra de isolamento da borda)."""
    for x0, y0, x1, y1 in [(0, 0, W, m), (0, H - m, W, H), (0, 0, m, H), (W - m, 0, W, H)]:
        z = pcbnew.ZONE(board)
        z.SetIsRuleArea(True)
        z.SetDoNotAllowTracks(True)
        z.SetDoNotAllowVias(True)
        z.SetDoNotAllowPads(False)
        z.SetDoNotAllowFootprints(False)
        z.SetDoNotAllowCopperPour(False)
        z.SetLayerSet(pcbnew.LSET.AllCuMask())
        ol = z.Outline()
        ol.NewOutline()
        for px, py in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]:
            ol.Append(mm(px, py))
        board.Add(z)


def add_zones(board, gnd):
    # planos de GND nas duas faces
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        z = pcbnew.ZONE(board)
        z.SetLayer(layer)
        z.SetNet(gnd)
        z.SetLocalClearance(pcbnew.FromMM(0.2))
        z.SetMinThickness(pcbnew.FromMM(0.2))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        ol = z.Outline()
        ol.NewOutline()
        for px, py in [(0, 0), (W, 0), (W, H), (0, H)]:
            ol.Append(mm(px, py))
        board.Add(z)


def add_text(board):
    # texto de identificação na face de trás
    t = pcbnew.PCB_TEXT(board)
    t.SetText("SIGNA rev D")
    t.SetPosition(mm(CX, 15.0)); t.SetLayer(pcbnew.B_SilkS)
    t.SetTextSize(pcbnew.VECTOR2I_MM(0.8, 0.8)); t.SetTextThickness(pcbnew.FromMM(0.12))
    t.SetMirrored(True)
    board.Add(t)


def remove_dangling(board):
    """Remove pontas soltas que o Freerouting às vezes deixa (stubs sem ligação)."""
    tol = pcbnew.FromMM(0.01)
    seen, dup = set(), []
    for t in [t for t in board.GetTracks() if t.Type() == pcbnew.PCB_TRACE_T]:
        a, b = (t.GetStart().x, t.GetStart().y), (t.GetEnd().x, t.GetEnd().y)
        key = (t.GetLayer(), t.GetNetCode(), min(a, b), max(a, b))
        if key in seen or a == b:
            dup.append(t)
        else:
            seen.add(key)
    for t in dup:
        board.Delete(t)
    if dup:
        print("trechos duplicados removidos:", len(dup))
    while True:
        tracks = [t for t in board.GetTracks() if t.Type() == pcbnew.PCB_TRACE_T]
        vias = [t for t in board.GetTracks() if t.Type() == pcbnew.PCB_VIA_T]
        pads = list(board.GetPads())
        def connected(t, p):
            for o in tracks:
                if o is t or o.GetLayer() != t.GetLayer():
                    continue
                for q in (o.GetStart(), o.GetEnd()):
                    if abs(q.x - p.x) <= tol and abs(q.y - p.y) <= tol:
                        return True
            for v in vias:
                if (v.GetPosition() - p).EuclideanNorm() <= v.GetWidth(pcbnew.F_Cu) // 2:
                    return True
            for pd in pads:
                if pd.IsOnLayer(t.GetLayer()) and pd.HitTest(p):
                    return True
            return False
        dead = [t for t in tracks if not (connected(t, t.GetStart()) and connected(t, t.GetEnd()))]
        if not dead:
            return
        for t in dead:
            board.Delete(t)
        print("pontas soltas removidas:", len(dead))


def main():
    if "--ses" in sys.argv:
        board = pcbnew.LoadBoard(PCB)
        ses = sys.argv[sys.argv.index("--ses") + 1]
        assert pcbnew.ImportSpecctraSES(board, ses), "falha ao importar SES"
        remove_dangling(board)
        pcbnew.ZONE_FILLER(board).Fill(board.Zones())
        board.Save(PCB)
        print("trilhas importadas:", len(board.GetTracks()))
        return
    # DSN sem os planos: assim o Freerouting também traça o GND
    assert pcbnew.ExportSpecctraDSN(build(zones=False), DSN), "falha ao exportar DSN"
    build(zones=True).Save(PCB)
    print("placa salva; DSN exportado:", DSN)


if __name__ == "__main__":
    main()
