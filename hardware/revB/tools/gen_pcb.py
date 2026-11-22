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
    # LEDs alinhados ao centro, voltados para a raiz da bandeira (topo = D3)
    "D3": (CX, 3.0, 0, "F"), "D2": (CX, 10.0, 0, "F"), "D1": (CX, 17.0, 0, "F"),
    "C8": (9.1, 3.0, 90, "F"), "C7": (9.1, 10.0, 90, "F"), "C6": (9.1, 17.0, 90, "F"),
    # coluna da esquerda: buffer de nível 3,3 -> 5 V e resistor série
    "C5": (1.9, 10.6, 90, "F"), "U3": (1.9, 13.9, 90, "F"), "R3": (1.9, 17.0, 90, "F"),
    "R4": (1.9, 20.2, 90, "F"), "C2": (9.1, 20.6, 90, "F"),
    # MCU QFN-28 4x4 e desacoplamentos junto aos pinos 3/4 (VDD/VSS) e 5 (NRST)
    "U1": (CX, 25.5, 0, "F"),
    "C3": (1.5, 24.6, 90, "F"), "C4": (1.5, 27.0, 90, "F"),
    # alimentação e proteção USB
    "U2": (2.75, 31.75, 90, "F"), "U4": (8.25, 31.75, 90, "F"),
    "C1": (1.9, 34.7, 0, "F"), "R1": (4.6, 34.7, 0, "F"), "R2": (7.6, 34.7, 0, "F"),
    # USB-C: boca para baixo, sobressai 0,7 mm da borda
    "J1": (CX, H - 3.0, 0, "F"),
    # face de trás: Tag-Connect TC2030 entre D3 e D2; jumper BOOT0 atrás do MCU
    "J2": (CX, 6.5, 0, "B"),
    "JP1": (CX, 21.0, 0, "B"),
}


# Modelos 3D só para os renders: o pacote kicad-packages3d 9.0.2 do Debian não traz
# os modelos do QFN-28 sem EP nem do HRO TYPE-C-31-M-12, e o SK6805-EC20 não tem modelo.
# Usamos substitutos visuais parecidos (não afetam Gerber/BOM/CPL).
M3D = "${KICAD9_3DMODEL_DIR}/"
SUBST_3D = {
    "U1": (M3D + "Package_DFN_QFN.3dshapes/QFN-28-1EP_4x4mm_P0.4mm_EP2.4x2.4mm.step", (1, 1, 1)),
    "J1": (M3D + "Connector_USB.3dshapes/USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal.step", (1, 1, 1)),
    "D1": (M3D + "LED_SMD.3dshapes/LED_WS2812B-Mini_PLCC4_3.5x3.5mm.step", (0.571, 0.571, 0.6)),
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

    # contorno com cantos arredondados (r = 1 mm)
    r = 1.0
    segs = [((r, 0), (W - r, 0)), ((W, r), (W, H - r)), ((W - r, H), (r, H)), ((0, H - r), (0, r))]
    for a, b in segs:
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(mm(*a)); s.SetEnd(mm(*b))
        s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(pcbnew.FromMM(0.05))
        board.Add(s)
    k = r * (1 - 0.7071067811865476)
    corners = [((0, r), (k, k), (r, 0)), ((W - r, 0), (W - k, k), (W, r)),
               ((W, H - r), (W - k, H - k), (W - r, H)), ((r, H), (k, H - k), (0, H - r))]
    for st, md, en in corners:
        a = pcbnew.PCB_SHAPE(board)
        a.SetShape(pcbnew.SHAPE_T_ARC)
        a.SetArcGeometry(mm(*st), mm(*md), mm(*en))
        a.SetLayer(pcbnew.Edge_Cuts); a.SetWidth(pcbnew.FromMM(0.05))
        board.Add(a)

    add_text(board)
    if zones:
        add_zones(board, net("/GND"))
    else:
        add_edge_keepout(board)
    return board


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
    t.SetText("LUXCLONE rev B")
    t.SetPosition(mm(CX, 14.5)); t.SetLayer(pcbnew.B_SilkS)
    t.SetTextSize(pcbnew.VECTOR2I_MM(0.8, 0.8)); t.SetTextThickness(pcbnew.FromMM(0.12))
    t.SetMirrored(True)
    board.Add(t)


def main():
    if "--ses" in sys.argv:
        board = pcbnew.LoadBoard(PCB)
        ses = sys.argv[sys.argv.index("--ses") + 1]
        assert pcbnew.ImportSpecctraSES(board, ses), "falha ao importar SES"
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
