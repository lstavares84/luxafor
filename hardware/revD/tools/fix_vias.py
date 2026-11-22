"""Afasta vias cujo furo-a-furo ficou < 0,5 mm (aviso do DRC após o Freerouting).
Move a via (e as pontas de trilha ligadas a ela) 0,03 mm para longe da vizinha."""
import pcbnew, itertools, sys
PCB = sys.argv[1]
b = pcbnew.LoadBoard(PCB)
vias = [t for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T]
tr = [t for t in b.GetTracks() if t.Type() == pcbnew.PCB_TRACE_T]
moved = 0
for a, c in itertools.combinations(vias, 2):
    d = (a.GetPosition() - c.GetPosition()).EuclideanNorm()
    gap = d - (a.GetDrill() + c.GetDrill()) / 2
    if gap < pcbnew.FromMM(0.505):
        v = c.GetPosition() - a.GetPosition()
        need = pcbnew.FromMM(0.503) - gap
        k = need / max(d, 1)
        dv = pcbnew.VECTOR2I(int(v.x * k), int(v.y * k))
        old = c.GetPosition(); new = old + dv
        for t in tr:
            if t.GetNetCode() != c.GetNetCode(): continue
            if t.GetStart() == old: t.SetStart(new)
            if t.GetEnd() == old: t.SetEnd(new)
        c.SetPosition(new); moved += 1
        print("via movida", pcbnew.ToMM(old.x), pcbnew.ToMM(old.y), "gap", round(pcbnew.ToMM(gap), 3))
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(PCB)
print("vias movidas:", moved)
