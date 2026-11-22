"""Malhas para render/GLB: placa agrupada por cor, pecas inteiras e cortadas (y > eixo do USB removido)."""
import os, collections, json
from build123d import *
from parts import *
EXP = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'export')
D = os.path.join(EXP, 'mesh'); os.makedirs(D, exist_ok=True)
HALF = Pos(0, -100 + USB_Y, 50) * Box(300, 200, 400)      # mantem y < eixo do USB-C


def leaves(x, loc=Location(), col=None, path=''):
    c = x.color if getattr(x, 'color', None) is not None else col
    if x.children:
        l = loc * x.location if x.location is not None else loc
        for ch in x.children:
            yield from leaves(ch, l, c, path + '/' + (x.label or ''))
    else:
        yield path + '/' + (x.label or ''), x.moved(loc), c


def key_of(n, c):
    if 'luxflag_PCB' in n: return 'pcb'
    if 'luxflag_pad' in n: return 'pad'
    if 'luxflag_copper' in n or 'luxflag_via' in n: return 'cobre'
    if 'silkscreen' in n: return 'serigrafia'
    if 'LED_lente' in n: return 'led_lente'
    if 'LED_corpo' in n: return 'led_corpo'
    if 'SKRT_haste' in n or 'SKRT_tampa' in n: return 'preto'
    if 'SKRT_corpo' in n or 'SKRT_guias' in n: return 'branco'
    if 'J1_lingua' in n or 'QFN_corpo' in n: return 'preto'
    if 'J1_' in n or 'terminais' in n or 'QFN_term' in n: return 'metal'
    if c is None: return 'cinza'
    r, g, b = [round(v, 2) for v in tuple(c)[:3]]
    if r > 0.6 and g > 0.6 and b > 0.6: return 'metal'
    if r < 0.25 and g < 0.25 and b < 0.25: return 'preto'
    if r > 0.45 and g < 0.45: return 'resistor'
    return 'comp'


groups = collections.defaultdict(list)
for n, s, c in leaves(board()):
    groups[key_of(n, c)] += list(s.solids()) if hasattr(s, 'solids') else [s]
info = {}
for k, sols in groups.items():
    comp = Compound(sols)
    export_stl(comp, os.path.join(D, f'placa_{k}.stl'), tolerance=0.01, angular_tolerance=0.2)
    cut = []
    for s in sols:
        try:
            r = s & HALF
            if r is not None and r.volume > 1e-6: cut.append(r)
        except Exception:
            pass
    if cut:
        export_stl(Compound(cut), os.path.join(D, f'placa_{k}_corte.stl'), tolerance=0.01, angular_tolerance=0.2)
    info[k] = len(sols)
print('placa:', info)

shell, ov, boot = cable_plug()
PARTS = dict(tubo=tube(), tampa=cap(), berco=carrier(), tampao=end_plug(), passa_cabo=grommet(), botao=plunger(),
             plugue_casca=shell, sobremolde=ov, alivio=boot, cabo=cable(), cabo_curto=cable(full=False),
             cabo_toco=Pos(0, USB_Y, CABLE_Z0) * Cylinder(CABLE_D / 2, 28, align=(Align.CENTER, Align.CENTER, Align.MIN)))
for n, p in PARTS.items():
    export_stl(p, os.path.join(D, n + '.stl'), tolerance=0.01, angular_tolerance=0.1)
    if n in ('cabo',):
        continue
    try:
        export_stl(p & HALF, os.path.join(D, n + '_corte.stl'), tolerance=0.01, angular_tolerance=0.1)
    except Exception as e:
        print('corte falhou', n, e)
json.dump(dict(LED_Z=[PCB_Z0 + d for d in LED_FROM_EDGE], LED_Y=PCB_FRONT_Y + LED_H, USB_Y=USB_Y, CABLE_RISE=CABLE_RISE,
               CAP_TOP=CAP_TOP, BTN_Y=BTN_Y), open(os.path.join(D, 'geo.json'), 'w'))
print('ok')
