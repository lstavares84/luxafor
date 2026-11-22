"""Troca só o contorno (Edge.Cuts) da placa já roteada pelo add_outline() atual e repreenche os planos."""
import sys, pcbnew
import gen_pcb
b = pcbnew.LoadBoard(gen_pcb.PCB)
for d in [d for d in b.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts]:
    b.Delete(d)
gen_pcb.add_outline(b)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(gen_pcb.PCB)
print("contorno trocado")
