"""Verificacao de interferencias e folgas do conjunto integrado (placa rev D + pecas + cabo)."""
import itertools, json, math, os
from build123d import *
from parts import *

OUTD = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs')
os.makedirs(OUTD, exist_ok=True)


def leaves(x, loc=Location(), path=''):
    if x.children:
        l = loc * x.location if x.location is not None else loc
        for c in x.children:
            yield from leaves(c, l, path + '/' + (x.label or ''))
    else:
        yield path + '/' + (x.label or ''), x.moved(loc)


b = board()
BL = list(leaves(b))
def pick(key):
    return Compound([s for n, s in BL if key in n])
pcb = pick('luxflag_PCB')
j1_shell, j1_tongue = pick('J1_carcaca'), pick('J1_lingua')
stem, swbody = pick('SKRT_haste'), Compound([s for n, s in BL if 'SKRT_corpo' in n or 'SKRT_tampa' in n])
leds = pick('LED_corpo')
board_all = Compound([s for n, s in BL])

shell, ov, boot = cable_plug()
P = dict(tubo=tube(), tampao=end_plug(), berco=carrier(), tampa=cap(), passa_cabo=grommet(), botao=plunger(),
         plugue_casca=shell, sobremolde=ov, alivio=boot, cabo=cable(), placa=board_all)
INTENT = {frozenset(('tampao', 'berco')): 'press-fit do pino do berço no tampão',
          frozenset(('passa_cabo', 'cabo')): 'aperto do passa-cabo (furo Ø%.1f) no cabo Ø%.1f' % (GR_CABLE_D, CABLE_D),
          frozenset(('alivio', 'cabo')): 'mesmo objeto (capa entra no alívio do plugue)',
          frozenset(('sobremolde', 'alivio')): 'mesmo objeto (sobremolde + alívio)',
          frozenset(('plugue_casca', 'sobremolde')): 'mesmo objeto (casca presa no sobremolde)'}
out, res = [], {'interferencias': {}, 'folgas': {}}
out.append('SIGNA Pendente rev B + placa rev D — verificação de montagem (%s)' % DATE)
out.append('== Interferências (volume de interseção, mm³) ==')
bad = 0
for a, c in itertools.combinations(P, 2):
    try:
        v = (P[a] & P[c]).volume
    except Exception as e:
        v = float('nan')
    if v != v or abs(v) > 1e-3:
        k = frozenset((a, c))
        tag = INTENT.get(k)
        if not tag:
            bad += 1
        out.append(f'  {a} x {c}: {v:.3f}  [' + (('intencional: ' + tag) if tag else 'NÃO INTENCIONAL') + ']')
        res['interferencias'][f'{a}x{c}'] = round(v, 4)
out.append(f'  -> interferências não intencionais: {bad}')

def gap(x, y):
    return x.distance_to(y)

F = []
def f(nome, val, nota=''):
    F.append((nome, val, nota)); res['folgas'][nome] = round(val, 3)

# placa no berço
f('placa (PCB) – berço', gap(pcb, P['berco']), 'contato de apoio: orelhas no fundo das fendas da flange (Z=%.2f) = assento' % (PCB_TOP_Z - EAR_H))
f('orelhas da placa – ressalto da tampa (axial)', FLANGE_Z0 + FLANGE_T - PCB_TOP_Z, 'batente para cima: botão 1,6 N e extração do cabo 8–20 N')
f('borda de baixo da placa – fundo das ranhuras', GROOVE_FLOOR_GAP, 'sem apoio aqui (evita hiperestático)')
f('orelhas – fundo lateral da fenda (por lado)', EAR_SLOT_X_OUT - EAR_X_OUT)
f('orelhas – tampa (mín. 3D)', gap(pcb, P['tampa']))
f('orelhas – tubo (mín. 3D)', gap(pcb, P['tubo']), 'orelhas ficam acima do tubo (Z ≥ %.2f > 50)' % (PCB_TOP_Z - EAR_H))
grv_t = (GROOVE_W - PCB_T) / 2
f('placa na ranhura: folga por face (espessura)', grv_t, 'ranhura 0,90 × placa 0,80')
f('placa na ranhura: folga lateral total', 2 * (GROOVE_X_OUT - PCB_W / 2), 'fundo da ranhura |x| 5,65 × borda 5,50 (por lado 0,15)')
f('placa (com componentes) – tubo', gap(board_all, P['tubo']))

f('placa (com componentes) – tampão', gap(board_all, P['tampao']))
f('LED (topo) – difusor, frente', TUBE_ID / 2 - leds.bounding_box().max.Y, 'WS2816B 0,84 mm; parede interna do tubo')
f('corpo do botão S1 – tubo', gap(swbody, P['tubo']))
# botao
f('botão P06 – haste do S1 (axial, nominal)', gap(P['botao'], stem), 'tubo 48 ±0,2 e orelhas da placa ±0,2 -> 0,0 a 0,8 mm (pior caso); curso elétrico 0,2')
f('botão P06 – tampão (radial no furo)', (BTN_HOLE_D - BTN_SHAFT_D) / 2, 'colar apoiado no fundo do rebaixo por gravidade (contato)')
f('colar P06 – parede do rebaixo (radial)', (BTN_CB_D - BTN_COLLAR_D) / 2)
f('botão P06 – berço', gap(P['botao'], P['berco']))
f('botão P06 – placa', gap(P['botao'], pcb))
f('curso total até acionar (pior caso)', BTN_GAP + 0.4 + SW_TRAVEL, 'folga máx. 0,8 + curso 0,2; nominal %.1f' % (BTN_GAP + SW_TRAVEL))
# USB-C
f('casca do plugue – cavidade do receptáculo (lateral)', (REC_CAV[0] - PLUG_SHELL[0]) / 2, 'spec: 8,34 × 2,56 vs 8,25 × 2,40')
f('casca do plugue – cavidade do receptáculo (altura)', (REC_CAV[1] - PLUG_SHELL[1]) / 2)
f('casca do plugue – carcaça J1 (mín. 3D)', gap(shell, j1_shell))
f('língua J1 – interior do plugue (mín. 3D)', gap(j1_tongue, shell))
f('ponta da casca – fundo da cavidade (axial)', REC_CAV[2] - PLUG_DEPTH)
f('sobremolde – flange do berço', gap(ov, P['berco']), 'boca do USB-C fica %.2f mm acima da flange: qualquer casca exposta ≥ %.2f mm assenta' % (USB_MOUTH_Z - FLANGE_Z0 - FLANGE_T, PLUG_DEPTH - (USB_MOUTH_Z - FLANGE_Z0 - FLANGE_T)))
f('espaço p/ sobremolde + alívio (boca → topo do alívio do passa-cabo)', CAP_TOP - USB_MOUTH_Z, 'cabos com sobremolde + alívio até ~24,5 mm e alívio ≤ Ø6,4 nos últimos 4,5 mm')
f('sobremolde – boca do receptáculo (axial)', ov.bounding_box().min.Z - USB_MOUTH_Z)
f('sobremolde – tampa (cavidade Ø%.1f)' % BORE_D, gap(ov, P['tampa']))
f('sobremolde – passa-cabo', gap(ov, P['passa_cabo']))
f('alívio do plugue – passa-cabo', gap(boot, P['passa_cabo']))
f('cabo – tampa (furo do topo)', gap(P['cabo'], P['tampa']))
f('casca do plugue – placa (PCB)', gap(shell, pcb))
bw, bt, _ = PLUG_BODY
cx, cy = bw / 2 - PLUG_BODY_R, bt / 2 - PLUG_BODY_R
diag = 2 * (math.hypot(cx, cy) + PLUG_BODY_R)
f('sobremolde passa no furo Ø%.1f (diagonal %.2f)' % (TOP_HOLE_D, diag), (TOP_HOLE_D - diag) / 2, 'por lado; plugues até 12,3 × 6,8 com r ≥ 3 também passam')

out.append('== Folgas (mm; 0,000 = contato projetado) ==')
for n, v, nota in F:
    out.append(f'  {n}: {v:.3f}' + (f'   ({nota})' if nota else ''))
out.append(f'LEDs em Z = {[round(PCB_Z0 + d, 1) for d in LED_FROM_EDGE]}; botão em Y = {BTN_Y:.2f} (quase no eixo); eixo USB em Y = {USB_Y:.2f}')
out.append(f'cabo modelado: {cable_length():.0f} mm (capa Ø{CABLE_D}) do alívio até atrás do monitor; o resto do cabo de 1,5 m não é modelado')
out.append(f'altura do corpo: {CAP_TOP:.1f} mm; com bota do passa-cabo {CAP_TOP + GR_FL_T + GR_BOOT_L:.1f} mm; botão sai {BTN_PROUD} mm abaixo do tampão')
dens = dict(tubo=1.20, tampao=1.20, berco=1.20, tampa=2.70, passa_cabo=1.10, botao=1.20)
m = {k: round(P[k].volume / 1000 * d, 2) for k, d in dens.items()}
out.append(f'massas (g) estimadas: {m} + placa ~1,0  total ~{sum(m.values()) + 1.0:.1f} g (sem cabo)')
txt = '\n'.join(out)
print(txt)
open(os.path.join(OUTD, 'verificacao_montagem.txt'), 'w').write(txt + '\n')
json.dump(res, open(os.path.join(OUTD, 'verificacao_montagem.json'), 'w'), indent=1, ensure_ascii=False)
