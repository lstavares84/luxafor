"""Extrai geometria da placa rev C (KiCad) para dados/placa.json (usado pelo desenho)."""
import pcbnew, json
b = pcbnew.LoadBoard('/workspace/luxpcb-revC/project/luxflag.kicad_pcb')
mm = pcbnew.ToMM
bb = b.GetBoardEdgesBoundingBox()
out = dict(bbox=[mm(bb.GetX()), mm(bb.GetY()), mm(bb.GetWidth()), mm(bb.GetHeight())], fps=[], tracks=[], vias=[], edges=[])
for d in b.GetDrawings():
    if d.GetLayerName() == 'Edge.Cuts':
        s = d.GetShapeStr()
        out['edges'].append(dict(shape=s, start=[mm(d.GetStart().x), mm(d.GetStart().y)], end=[mm(d.GetEnd().x), mm(d.GetEnd().y)],
                                 center=[mm(d.GetCenter().x), mm(d.GetCenter().y)] if s in ('Arc', 'Circle') else None,
                                 mid=[mm(d.GetArcMid().x), mm(d.GetArcMid().y)] if s == 'Arc' else None))
for f in b.GetFootprints():
    cy = f.GetCourtyard(f.GetLayer())
    fb = f.GetFpPadsLocalBbox() if hasattr(f, 'GetFpPadsLocalBbox') else None
    bbx = f.GetBoundingBox(False)
    pads = []
    for p in f.Pads():
        pb = p.GetBoundingBox()
        pads.append(dict(n=p.GetNumber(), x=mm(p.GetPosition().x), y=mm(p.GetPosition().y), w=mm(pb.GetWidth()), h=mm(pb.GetHeight()),
                         layer='F' if p.IsOnLayer(pcbnew.F_Cu) else 'B', th=p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH, net=p.GetNetname()))
    out['fps'].append(dict(ref=f.GetReference(), val=f.GetValue(), x=mm(f.GetPosition().x), y=mm(f.GetPosition().y), rot=f.GetOrientationDegrees(),
                           side='B' if f.IsFlipped() else 'F', bbox=[mm(bbx.GetX()), mm(bbx.GetY()), mm(bbx.GetWidth()), mm(bbx.GetHeight())], pads=pads))
for t in b.GetTracks():
    if t.GetClass() == 'PCB_VIA':
        out['vias'].append([mm(t.GetPosition().x), mm(t.GetPosition().y), mm(t.GetWidth())])
    else:
        out['tracks'].append([mm(t.GetStart().x), mm(t.GetStart().y), mm(t.GetEnd().x), mm(t.GetEnd().y), mm(t.GetWidth()), t.GetLayerName()])
json.dump(out, open('dados/placa.json', 'w'), indent=0)
print(out['bbox'], len(out['fps']), len(out['tracks']), len(out['vias']))
for f in out['fps']: print(f['ref'], f['val'], round(f['x'],2), round(f['y'],2), f['rot'], f['side'], [round(v,2) for v in f['bbox']])
