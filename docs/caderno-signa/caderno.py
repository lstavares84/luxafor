"""Gera <nome>-conceito.pdf (A3 paisagem, 14 lâminas). Dados em dados/*.json (resultados via modelo.py);
este arquivo só desenha. Uso: python3 modelo.py && python3 prep_imagens.py && python3 caderno.py"""
import json, os, math, sys
from lib_metrologia import *
from reportlab.lib.colors import HexColor, Color

HERE = os.path.dirname(os.path.abspath(__file__))
J = lambda n: json.load(open(os.path.join(HERE, 'dados', n)))
PR, BOM, CU, NG, EN, R, PCB = J('produto.json'), J('bom.json'), J('custos.json'), J('negocio.json'), J('energia.json'), J('resultados.json'), J('placa.json')
IMG = lambda n: os.path.join(HERE, 'img', 'jpg', n + '.jpg')
MODO = {m['id']: m for m in PR['modos']}
VERM = MODO[PR['modo_principal']]['hex']
NOME = PR['nome']
RODAPE = f"{NOME} · {PR['revisao'].upper()} · CADERNO CONCEITUAL"
TOTAL = 14
IND = R['indicadores']
FX = R['cambio']


def pct(v, d=1):
    return br(v * 100, d) + ' %'


def tabela(L, x, y, cols, rows, larg, alt=5.2, head=True, size=2.15, bold_rows=(), aligns=None, cab_size=1.95, linhas=True, fonts=None):
    """cols: cabeçalhos; rows: listas de str; larg: larguras mm. y = topo. Retorna y final."""
    aligns = aligns or ['l'] * len(cols)
    if head:
        cx = x
        for c, w, a in zip(cols, larg, aligns):
            tx = cx + (w - 1 if a == 'r' else 0 if a == 'l' else w / 2)
            L.text(tx, y - 3.4, c.upper(), 'JuraM', cab_size, L.sec, cs=0.3, anchor=a)
            cx += w
        y -= 5.0
        L.line(x, y, x + sum(larg), y, L.ink, 0.2)
    for i, r in enumerate(rows):
        cx = x
        bold = i in bold_rows
        for j, (v, w, a) in enumerate(zip(r, larg, aligns)):
            f = (fonts[j] if fonts else ('Mono' if a == 'r' else 'Work'))
            if bold: f = {'Mono': 'MonoM', 'Work': 'WorkM'}.get(f, f)
            tx = cx + (w - 1 if a == 'r' else 0 if a == 'l' else w / 2)
            L.text(tx, y - alt + 1.55, v, f, size, L.ink, anchor=a)
            cx += w
        y -= alt
        if linhas:
            L.line(x, y, x + sum(larg), y, P['regua'] if not L.noite else P['borda'], 0.25 if bold else 0.1)
    return y


# =====================================================================================
def l01(c):
    L = Lamina(c, 1, TOTAL, 'CAPA', RODAPE, noite=True)
    L.image(IMG('capa'), 214, 30, 177, 236, 'render capa')
    L.text(M, 261.5, 'ESTUDO CONCEITUAL · METROLOGIA LUMINOSA', 'JuraM', 2.4, L.ink, cs=1.0)
    s = NOME; size = 21.0; cs = 5.0
    while L.width(s, 'JuraL', size, cs) > 186: size -= 0.5
    L.text(M, 184, s, 'JuraL', size, L.ink, cs=cs, tag='nome')
    L.text(M, 176.2, PR['nome_nota'].upper(), 'Mono', 1.9, L.ink, tag='prov')
    L.rect(M, 170.4, 72, 0.7, fill=VERM)
    L.nota(M, 156, 'uma luz para a sala ver seu status —', size=6.0, col=L.ink)
    L.nota(M, 147.5, 'e para você acompanhar suas IAs.', size=6.0, col=L.ink)
    L.italicos -= 1   # a frase-síntese ocupa duas linhas: conta como uma nota
    y = 123
    for k, v in PR['especificacoes_capa']:
        L.text(M, y, k, 'JuraM', 2.15, L.ink, cs=0.9)
        L.text(M + 38, y, v, 'Mono', 2.35, L.ink)
        L.line(M, y - 2.2, M + 154, y - 2.2, P['borda'], 0.12)
        y -= 7.8
    # investidor: quatro números, com remissão às premissas
    y = 66
    for k, v in [('VPL a 14 % a.a.', brl(IND['vpl'] / 1000) + ' mil'), ('TIR', pct(IND['tir'])),
                 ('PAYBACK', br(IND['payback'], 1) + ' anos'), ('PREÇO SUGERIDO', brl(R['preco_sug']))]:
        L.text(M, y, k.upper(), 'JuraM', 2.0, L.ink, cs=0.6)
        y -= 7.5
    y = 66
    for v in [brl(IND['vpl'] / 1000) + ' mil', pct(IND['tir']), br(IND['payback'], 1) + ' anos', brl(R['preco_sug'])]:
        L.text(M + 38, y, v, 'MonoM', 2.6, L.ink); y -= 7.5
    L.text(M + 100, 66, 'premissas e riscos:', 'Mono', 1.9, L.ink)
    L.text(M + 100, 62.6, 'lâminas 11 a 14', 'Mono', 1.9, L.ink)
    L.text(M, 31.5, f"{PR['revisao'].upper()} · ESTUDO CONCEITUAL · {PR['data']}", 'JuraM', 2.3, L.ink, cs=1.4)
    L.text(391, 26.2, f"render conceitual, não é foto de protótipo · SALA: {MODO['sala_ocupado']['nome']} {VERM}", 'Mono', 1.9, L.ink, anchor='r')
    return L

# =====================================================================================
def l02(c):
    L = Lamina(c, 2, TOTAL, 'VISTAS DO PRODUTO', RODAPE)
    L.titulo('VISTAS DO PRODUTO')
    S = 2.0
    fx, base = 84.0, 74.0          # vista frontal: eixo e z=0
    lx = 160.0                     # vista lateral esquerda (1.º diedro: à direita)
    tvx, tvy = fx, 50.0            # vista superior (1.º diedro: abaixo)
    ink, hid = P['tinta'], P['sec']
    Z = lambda z: base + z * S

    def contorno(cx):
        pts = [(cx - 8 * S, Z(0)), (cx + 8 * S, Z(0)), (cx + 8 * S, Z(46)), (cx + 9.5 * S, Z(46)), (cx + 9.5 * S, Z(78 - 1.5)),
               (cx + 8 * S, Z(78)), (cx - 8 * S, Z(78)), (cx - 9.5 * S, Z(78 - 1.5)), (cx - 9.5 * S, Z(46)), (cx - 8 * S, Z(46))]
        L.poly(pts, stroke=ink, lw=0.35)
        L.line(cx - 8 * S, Z(2), cx + 8 * S, Z(2), ink, 0.2)                  # tampão/tubo
        L.line(cx - 8 * S, Z(78) - 0.0, cx + 8 * S, Z(78), ink, 0.35)
        # passa-cabo (flange + bota) e cabo
        L.rect(cx - 7.5 * S, Z(78), 15 * S, 1.2 * S, stroke=ink, lw=0.3)
        L.poly([(cx - 4 * S, Z(79.2)), (cx + 4 * S, Z(79.2)), (cx + 2.8 * S, Z(88.2)), (cx - 2.8 * S, Z(88.2))], stroke=ink, lw=0.3)
        L.line(cx - 1.8 * S, Z(88.2), cx - 1.8 * S, Z(89.9), ink, 0.3); L.line(cx + 1.8 * S, Z(88.2), cx + 1.8 * S, Z(89.9), ink, 0.3)
        L.poly([(cx - 2.6 * S, Z(89.6)), (cx - 0.6 * S, Z(90.2)), (cx + 0.6 * S, Z(89.6)), (cx + 2.6 * S, Z(90.2))], stroke=ink, lw=0.2, close=False)
        # ocultas comuns
        for xx in (-6.5, 6.5):
            L.line(cx + xx * S, Z(5.7), cx + xx * S, Z(50), hid, 0.14, dash=[1.2, 0.8])
        for xx in (-8.125, 8.125):
            L.line(cx + xx * S, Z(46), cx + xx * S, Z(52), hid, 0.14, dash=[1.2, 0.8])
        L.line(cx - 8.125 * S, Z(52), cx + 8.125 * S, Z(52), hid, 0.14, dash=[1.2, 0.8])
        for xx in (-6.8, 6.8):
            L.line(cx + xx * S, Z(52), cx + xx * S, Z(74.5), hid, 0.14, dash=[1.2, 0.8])
        L.line(cx - 6.8 * S, Z(74.5), cx + 6.8 * S, Z(74.5), hid, 0.14, dash=[1.2, 0.8])
        L.line(cx - 6.425 * S, Z(5.7), cx + 6.425 * S, Z(5.7), hid, 0.14, dash=[1.2, 0.8])
        # eixo
        L.line(cx, Z(-2), cx, Z(89.4), hid, 0.1, dash=[6, 1, 1, 1])

    contorno(fx)
    # frontal: placa de face
    L.rect(fx - 5.5 * S, Z(7), 11 * S, 44 * S, stroke=hid, lw=0.16, dash=[1.2, 0.8])
    for zc in (10, 17, 24):
        L.rect(fx - 1.1 * S, Z(zc) - 1.0 * S, 2.2 * S, 2.0 * S, stroke=hid, lw=0.16, dash=[0.8, 0.6])
    L.rect(fx - 4.47 * S, Z(44.4), 8.94 * S, 7.3 * S, stroke=hid, lw=0.16, dash=[1.2, 0.8])
    contorno(lx)
    # lateral: placa de perfil (Y)
    L.rect(lx - 2.4 * S, Z(7), 0.8 * S, 44 * S, stroke=hid, lw=0.16, dash=[1.2, 0.8])
    L.rect(lx - 1.6 * S, Z(44.4), 3.3 * S, 7.3 * S, stroke=hid, lw=0.16, dash=[1.2, 0.8])
    for zc in (10, 17, 24):
        L.rect(lx - 1.6 * S, Z(zc) - 1.0 * S, 0.84 * S, 2.0 * S, stroke=hid, lw=0.16, dash=[0.8, 0.6])
    L.area(fx - 9.5 * S, Z(0), fx + 9.5 * S, Z(90.2), 'vista frontal')
    L.area(lx - 9.5 * S, Z(0), lx + 9.5 * S, Z(90.2), 'vista lateral')
    # vista superior
    for r_, w_ in ((9.5, 0.35), (8.0, 0.12), (7.5, 0.3), (4.0, 0.3), (2.8, 0.2), (1.8, 0.3)):
        L.circle(tvx, tvy, r_ * S, stroke=ink, lw=w_)
    L.line(tvx - 22, tvy, tvx + 22, tvy, hid, 0.1, dash=[6, 1, 1, 1]); L.line(tvx, tvy - 22, tvx, tvy + 22, hid, 0.1, dash=[6, 1, 1, 1])
    L.area(tvx - 19, tvy - 19, tvx + 19, tvy + 19, 'vista superior')
    # linhas de chamada pontilhadas entre vistas
    for z in (0, 46, 78, 88.2):
        L.line(fx + 9.8 * S + 1, Z(z), lx - 9.8 * S - 1, Z(z), P['clara'], 0.1, dash=[0.4, 1.0])
    for xx in (-9.5, 9.5):
        L.line(fx + xx * S, Z(0) - 1.5, fx + xx * S, tvy + 19 + 1.5, P['clara'], 0.1, dash=[0.4, 1.0])
    # cotas (sempre fora)
    L.cota_v(Z(0), Z(78), fx - 9.5 * S, fx - 9.5 * S - 9, '78')
    L.cota_v(Z(0), Z(88.2), fx - 9.5 * S, fx - 9.5 * S - 17, '88,2')
    L.cota_v(Z(46), Z(78), lx + 9.5 * S, lx + 9.5 * S + 9, '32')
    L.cota_v(Z(0), Z(46), lx + 9.5 * S, lx + 9.5 * S + 9, '46')
    L.cota_h(lx - 8 * S, lx + 8 * S, Z(0), Z(0) - 7, 'Ø16', txt_below=True)
    L.cota_h(lx - 9.5 * S, lx + 9.5 * S, Z(0), Z(0) - 15, 'Ø19', txt_below=True)
    L.text(fx + 9.5 * S + 3, Z(0) + 3, 'FRONTAL', 'JuraM', 2.1, P['sec'], cs=0.6)
    L.text(lx + 9.5 * S + 15, Z(0) + 3, 'LATERAL ESQ.', 'JuraM', 2.1, P['sec'], cs=0.6)
    L.text(tvx + 26, tvy - 1, 'SUPERIOR', 'JuraM', 2.1, P['sec'], cs=0.6)
    # isometria (render)
    L.image(IMG('p2_iso'), 222, 92, 100, 140, 'iso')
    L.text(222, 86.5, 'ISOMETRIA · RENDER CONCEITUAL', 'JuraM', 2.1, P['sec'], cs=0.6)
    # coluna de dados
    x0 = 338
    L.rotulo(x0, 240, 'ENVELOPE')
    rows = [('Ø × C', 'Ø19 × 78 mm'), ('com passa-cabo', '88,2 mm'), ('massa', '≈ 20 g (est.)'), ('escala', '2:1'),
            ('projeção', '1.º diedro'), ('norma', 'NBR 10067'), ('tol. geral', 'ISO 2768-mK')]
    y = 232
    for k, v in rows:
        L.text(x0, y, k, 'Work', 2.1, P['sec']); L.text(W - M, y, v, 'Mono', 2.1, anchor='r'); y -= 5.6
    L.rotulo(x0, y - 4, 'MATERIAIS'); y -= 12
    for k, v in [('tampa', 'Al 6061-T6 anod.'), ('tubo', 'PC opalino'), ('berço', 'PC branco'), ('tampão', 'PC opalino'), ('passa-cabo', 'TPE 60A')]:
        L.text(x0, y, k, 'Work', 2.1, P['sec']); L.text(W - M, y, v, 'Mono', 2.1, anchor='r'); y -= 5.6
    L.text(x0, y - 2, 'proposta, a validar no protótipo', 'Mono', 1.9, P['sec'])
    L.nota(x0, 70, 'placa num berço; tubo preso entre', size=3.4)
    L.text(x0, 64.5, 'tampa e tampão, sem parafuso e sem cola', 'Serif', 3.4, P['sec'])
    L.italicos -= 1
    L.text(x0, 50, 'Luz de mesa/monitor: avisa a sala', 'Work', 2.2)
    L.text(x0, 45.5, 'e, quando quiser, suas IAs.', 'Work', 2.2)
    L.glossario('NBR 10067: norma de vistas · 1.º diedro: a vista de cima vai abaixo da frontal · tracejado = parte interna oculta · Ø = diâmetro (mm)')
    return L


# =====================================================================================
def l03(c):
    L = Lamina(c, 3, TOTAL, 'SUBSISTEMA CENTRAL', RODAPE)
    L.titulo('SUBSISTEMA CENTRAL · TRÊS VISTAS')
    S = 4.0; u0 = 36.0
    bx, by = PCB['bbox'][0], PCB['bbox'][1]
    U = lambda yk: u0 + (yk - 100.0) * S
    vF = lambda xk: 182.0 + (xk - 100.0) * S                 # frente
    vB = lambda xk: 70.0 + (111.0 - xk) * S                  # verso (rebatido)
    ink, sec, cl = P['tinta'], P['sec'], P['clara']

    def placa(V, lado):
        L.rect(U(100), min(V(100), V(111)), 44 * S, 11 * S, stroke=ink, lw=0.35, r=1 * S)
        for t in PCB['tracks']:
            if (lado == 'F' and t[5] == 'F.Cu') or (lado == 'B' and t[5] == 'B.Cu'):
                L.line(U(t[1]), V(t[0]), U(t[3]), V(t[2]), cl, max(t[4] * S, 0.25))
        for v in PCB['vias']:
            L.circle(U(v[1]), V(v[0]), 0.3 * S, stroke=sec, lw=0.12)
        for f in PCB['fps']:
            for p in f['pads']:
                if p['layer'] != lado and not p['th']:
                    continue
                L.rect(U(p['y']) - p['h'] * S / 2, V(p['x']) - p['w'] * S / 2, p['h'] * S, p['w'] * S, fill=P['regua'], stroke=sec, lw=0.08)
    placa(vF, 'F'); placa(vB, 'B')
    body = {'U1': (4, 4), 'D1': (2.2, 2.0), 'D2': (2.2, 2.0), 'D3': (2.2, 2.0), 'U2': (2.9, 1.6), 'U3': (2.9, 1.6), 'U4': (2.9, 1.6)}
    alt = {'U1': 0.55, 'D': 0.84, 'U2': 1.1, 'U3': 1.1, 'U4': 1.45, 'C1': 0.8, 'J1': 3.3}
    fps = {f['ref']: f for f in PCB['fps']}
    for ref, (a, b) in body.items():
        f = fps[ref]; w, h = (a, b) if f['rot'] in (0, 180) else (b, a)
        L.rect(U(f['y']) - h * S / 2, vF(f['x']) - w * S / 2, h * S, w * S, stroke=ink, lw=0.3)
    j = fps['J1']
    L.rect(U(137.33), vF(105.5) - 4.47 * S, (144.68 - 137.33) * S, 8.94 * S, stroke=ink, lw=0.3)
    L.area(U(100), vF(100), U(144.7), vF(111), 'frente')
    L.area(U(100), vB(111), U(144), vB(100), 'verso')
    # perfil (vista de lado), face inferior em y=142
    pb = 142.0; t = 0.8 * S
    L.rect(U(100), pb, 44 * S, t, stroke=ink, lw=0.35, fill=P['regua'])
    for f in PCB['fps']:
        if f['side'] != 'F': continue
        r = f['ref']; hgt = alt.get(r, alt.get(r[0], 0.35))
        if r == 'J1':
            L.rect(U(137.33), pb + t, (144.68 - 137.33) * S, 3.3 * S, stroke=ink, lw=0.3); continue
        if r in body:
            a, b = body[r]; ln = a if f['rot'] in (0, 180) else b
            ln = b if r.startswith('D') else ln
        else:
            ln = 1.0 if f['rot'] in (0, 180) else 0.5
            ln = 1.6 if r == 'C1' else ln
        L.rect(U(f['y']) - ln * S / 2, pb + t, ln * S, hgt * S, stroke=ink, lw=0.22)
    L.area(U(100), pb, U(144.7), pb + t + 3.3 * S, 'perfil')
    # chamadas entre vistas
    for yk in (100, 144):
        L.line(U(yk), vF(100) - 1.2, U(yk), pb + t + 1.2, cl, 0.1, dash=[0.4, 1.0])
        L.line(U(yk), pb - 1.2, U(yk), vB(100) + 1.2, cl, 0.1, dash=[0.4, 1.0])
    # rótulos das vistas
    L.text(U(100), vF(111) + 2.0 + 41, '', reg=False)
    L.text(U(100) - 1, vF(100) - 4.2, 'FRENTE · COMPONENTES', 'JuraM', 1.95, sec, cs=0.5)
    L.text(U(100) - 1, pb - 4.2, 'PERFIL', 'JuraM', 1.95, sec, cs=0.5)
    L.text(U(100) - 1, vB(100) + 2.0, 'VERSO · REBATIDO', 'JuraM', 1.95, sec, cs=0.5)
    # chamadas (frente) para o alto
    lab = [('J1', 'USB-C', 'HRO TYPE-C-31-M-12'), ('U4', 'ESD', 'USBLC6-2SC6'), ('U2', 'LDO 3,3 V', 'AP2112K'),
           ('U1', 'MCU', 'STM32C071G8U6'), ('D1', 'LED 1', 'WS2816B-2020'), ('U3', 'BUFFER 5 V', 'SN74AHCT1G125'),
           ('D2', 'LED 2', 'WS2816B-2020'), ('D3', 'LED 3', 'WS2816B-2020')]
    xs = {'D3': 36, 'D2': 60, 'U3': 86, 'D1': 112, 'U1': 130, 'U2': 156, 'U4': 182, 'J1': 208}
    for ref, nm, sub in lab:
        f = fps[ref]
        px, py = U(f['y']), vF(f['x'])
        L.chamada(px, py, xs[ref], 241, nm, sub, size=2.0)
    # detalhe A (círculo)
    d1 = fps['D1']
    L.circle(U(d1['y']), vF(d1['x']), 6.5, stroke=sec, lw=0.15, dash=[1.5, 0.8])
    L.line(U(d1['y']) + 2.5, vF(d1['x']) - 6.0, U(d1['y']) + 7, 179.5, sec, 0.12)
    L.text(U(d1['y']) + 7.6, 175.6, 'A', 'JuraM', 2.6, sec)
    # cotas
    L.cota_v(vF(100), vF(111), U(100), U(100) - 6, '11,0')
    L.cota_h(U(100), U(144), vB(111), vB(111) - 7, '44,0', txt_below=True)
    L.cota_v(pb, pb + t, U(144.68), U(144.68) + 5, '0,8', lado='r')
    L.cota_v(pb + t, pb + t + 3.3 * S, U(144.68), U(144.68) + 11, '3,3', lado='r')
    # cadeia dos LEDs (no perfil, acima)
    cy = 170.0
    xsL = [U(100), U(103), U(110), U(117)]
    L.line(xsL[0], pb + t + 0.8, xsL[0], cy + 1.2, ink, 0.1)
    for xx in xsL[1:]:
        L.line(xx, pb + t + 0.84 * S + 0.8, xx, cy + 1.2, ink, 0.1)
    for a, b, s in zip(xsL[:-1], xsL[1:], ['3,0', '7,0', '7,0']):
        L.cota_h(a, b, cy, cy, s, ext=False)
    # verso: TC2030 e BOOT0
    j2, jp = fps['J2'], fps['JP1']
    L.chamada(U(j2['y']), vB(j2['x']), 226, 80, 'SWD · TAG-CONNECT', 'gravação e depuração (TC2030)', size=2.0)
    L.chamada(U(jp['y']), vB(jp['x']), 226, 104, 'JP1 · BOOT0', 'força o modo DFU (USB)', size=2.0)
    # detalhe A 15:1
    K = 15.0; dx, dy = 282.0, 196.0
    L.rect(dx - 1.1 * K, dy - 1.0 * K, 2.2 * K, 2.0 * K, stroke=ink, lw=0.35)
    L.line(dx - 1.1 * K, dy + 0.6 * K, dx - 0.7 * K, dy + 1.0 * K, ink, 0.25)
    pins = [('1', 'BI', -0.975, 0.77), ('2', 'DI', -0.975, 0), ('3', 'VDD', -0.975, -0.77),
            ('4', 'DO', 0.975, -0.77), ('5', 'BO', 0.975, 0), ('6', 'GND', 0.975, 0.77)]
    for n, nm, px, py in pins:
        L.rect(dx + (px - 0.325) * K, dy + (py - 0.225) * K, 0.65 * K, 0.45 * K, stroke=sec, fill=P['regua'], lw=0.15)
        L.text(dx + px * K, dy + py * K - 0.8, n, 'MonoM', 2.2, anchor='c', tag='dentro pino')
        if px < 0:
            L.text(dx - 1.45 * K, dy + py * K - 0.8, nm, 'Mono', 2.1, anchor='r')
        else:
            L.text(dx + 1.45 * K, dy + py * K - 0.8, nm, 'Mono', 2.1, anchor='l')
    L.area(dx - 1.3 * K, dy - 1.0 * K, dx + 1.3 * K, dy + 1.0 * K, 'detalhe')
    L.cota_h(dx - 1.1 * K, dx + 1.1 * K, dy - 1.0 * K, dy - 1.0 * K - 6, '2,2', txt_below=True)
    L.cota_h(dx - 1.3 * K, dx - 0.65 * K, dy + 1.0 * K, dy + 1.0 * K + 5, '0,65')
    L.cota_v(dy + (0.77 - 0.225) * K, dy + (0.77 + 0.225) * K, dx + 1.3 * K, dx + 1.3 * K + 15, '0,45', lado='r')
    L.cota_v(dy - 1.0 * K, dy + 1.0 * K, dx + 1.3 * K, dx + 1.3 * K + 23, '2,0', lado='r')
    L.cota_v(dy, dy + 0.77 * K, dx - 1.3 * K, dx - 1.3 * K - 16, '0,77', lado='l')
    L.text(dx - 1.1 * K, dy + 1.0 * K + 13, 'DETALHE A · 15:1 · LED WS2816B-2020', 'JuraM', 2.1, sec, cs=0.4)
    L.text(dx - 1.1 * K, dy - 1.0 * K - 14.5, 'vista de topo · dado duplo DI/BI', 'Mono', 1.9, sec)
    # ficha técnica
    x0 = 338; y = 240
    L.rotulo(x0, y, 'FICHA DO SUBSISTEMA'); y -= 8
    for k, v in [('placa', '11 × 44 × 0,8 mm'), ('substrato', 'FR-4, 2 camadas'), ('cobre', '1 oz'), ('peças', '20 (12 códigos)'),
                 ('MCU', 'Cortex-M0+ 48 MHz'), ('memória', '64 KB flash'), ('USB', '2.0 FS, sem cristal'),
                 ('LEDs', '3 × RGB 16 bit'), ('PWM', '10 kHz, gama 4 bit'), ('dados', '800 kbit/s, 48 bit/LED'),
                 ('energia', 'VBUS 5 V · LDO 3,3 V'), ('gravação', 'DFU na ROM + SWD'), ('verificação', 'ERC/DRC sem erros'),
                 ('estado', 'não fabricada'), ('escala', '4:1 · detalhe 15:1')]:
        L.text(x0, y, k, 'Work', 2.05, sec); L.text(W - M, y, v, 'Mono', 2.05, anchor='r'); y -= 5.4
    L.text(x0, 75, 'Uma placa do tamanho de um palito', 'Work', 2.2)
    L.text(x0, 70.5, 'de fósforo: fala USB e acende 3 LEDs.', 'Work', 2.2)
    L.nota(x0, 58, 'altura máxima: o conector, 3,3 mm', size=3.4)
    L.glossario('MCU: microcontrolador · LDO: regulador de tensão · ESD: proteção contra descarga eletrostática · DFU: gravação do firmware pelo próprio USB · SWD: porta de depuração')
    return L


# =====================================================================================
def icone(L, kind, x, y, S=4.0):
    ink, sec = P['tinta'], P['sec']
    if kind == 'qfn':
        L.rect(x - 2 * S, y - 2 * S, 4 * S, 4 * S, stroke=ink, lw=0.3); L.rect(x - 1.3 * S, y - 1.3 * S, 2.6 * S, 2.6 * S, fill=P['regua'])
        for i in range(7):
            o = (-1.5 + i * 0.5) * S
            for (a, b) in ((o, -2 * S), (o, 2 * S - 0.35 * S), (-2 * S, o), (2 * S - 0.35 * S, o)):
                L.rect(x + a - 0.12 * S if b in (-2 * S, 2 * S - 0.35 * S) else x + a, y + b if b in (-2 * S, 2 * S - 0.35 * S) else y + o - 0.12 * S,
                       0.24 * S if b in (-2 * S, 2 * S - 0.35 * S) else 0.35 * S, 0.35 * S if b in (-2 * S, 2 * S - 0.35 * S) else 0.24 * S, fill=sec)
    elif kind == 'led':
        L.rect(x - 1.1 * S, y - 1.0 * S, 2.2 * S, 2.0 * S, stroke=ink, lw=0.3); L.circle(x, y, 0.6 * S, stroke=sec, lw=0.2)
    elif kind == 'usb':
        L.rect(x - 4.47 * S / 2, y - 3.65 * S / 2, 4.47 * S, 3.65 * S, stroke=ink, lw=0.3, r=0.6)
        L.rect(x - 1.6 * S, y - 0.4 * S, 3.2 * S, 0.8 * S, fill=P['regua'])
    elif kind == 'sot':
        L.rect(x - 1.45 * S, y - 0.8 * S, 2.9 * S, 1.6 * S, stroke=ink, lw=0.3)
        for o in (-0.95, 0, 0.95):
            L.rect(x + o * S - 0.2 * S, y - 1.4 * S, 0.4 * S, 0.6 * S, fill=sec); L.rect(x + o * S - 0.2 * S, y + 0.8 * S, 0.4 * S, 0.6 * S, fill=sec)
    elif kind == 'pcb':
        L.rect(x - 11, y - 2.75, 22, 5.5, stroke=ink, lw=0.3, r=0.5)


def l04(c):
    L = Lamina(c, 4, TOTAL, 'COMPONENTES E MATERIAIS', RODAPE)
    L.titulo('COMPONENTES E MATERIAIS')
    rows = [('qfn', 'U1', 'Microcontrolador USB', 'STM32C071G8U6', 'QFN-28 4×4', 'C44521811'),
            ('led', 'D1–D3', 'LED RGB 16 bit ×3', 'WS2816B-2020', '2,2×2,0×0,84', 'C4154877'),
            ('usb', 'J1', 'Conector USB-C', 'HRO TYPE-C-31-M-12', '8,9×7,3×3,3', 'C165948'),
            ('sot', 'U2', 'Regulador 3,3 V', 'AP2112K-3.3', 'SOT-23-5', 'C51118'),
            ('sot', 'U3', 'Conversor de nível', 'SN74AHCT1G125', 'SOT-23-5', 'C7484'),
            ('sot', 'U4', 'Proteção ESD', 'USBLC6-2SC6', 'SOT-23-6', 'C7519'),
            ('pcb', 'PCB', 'Placa 2 camadas', 'FR-4 0,8 mm', '11×44 mm', 'gerber rev C')]
    x = M; y = 246
    larg = [30, 18, 46, 46, 32, 30]
    cx = x
    for h, w in zip(['ÍCONE 4:1', 'REF.', 'FUNÇÃO', 'PEÇA', 'ENCAPS. (mm)', 'LCSC'], larg):
        L.text(cx, y, h, 'JuraM', 1.95, P['sec'], cs=0.3); cx += w
    y -= 2.2; L.line(x, y, x + sum(larg), y, P['tinta'], 0.2)
    for k, ref, fn, pn, pk, code in rows:
        rh = 26 if k in ('qfn', 'usb') else 19
        cy = y - rh / 2
        icone(L, k, x + 13, cy, 4.0 if k != 'pcb' else 4.0)
        cx = x + larg[0]
        for v, w, f in zip([ref, fn, pn, pk, code], larg[1:], ['MonoM', 'Work', 'Mono', 'Mono', 'Mono']):
            L.text(cx, cy - 0.8, v, f, 2.15); cx += w
        y -= rh; L.line(x, y, x + sum(larg), y, P['regua'], 0.1)
    L.text(x, y - 5, 'ícones na escala 4:1 (placa 1:2)', 'Mono', 1.9, P['sec'])
    # materiais
    x0 = 252; y = 246
    L.rotulo(x0, y, 'MATERIAIS'); y -= 9
    mats = [('#1D1E21', 'Alumínio 6061-T6, anodizado preto', 'torno CNC · anodização tipo II'),
            ('#E7E5E0', 'Policarbonato opalino, fosco', 'extrusão de tubo · corte'),
            ('#F4F3EF', 'Policarbonato branco refletivo', 'SLA (piloto) · injeção (série)'),
            ('#2A2B2E', 'Elastômero TPE 60 Shore A', 'TPU impresso · injeção'),
            ('#2E5A44', 'FR-4 com máscara de solda', 'PCB 2 camadas · SMT'),
            ('#B9A27A', 'Cartão kraft', 'corte e vinco')]
    for col, nm, proc in mats:
        L.rect(x0, y - 6.5, 16, 8.5, fill=col, stroke=P['clara'], lw=0.1)
        L.text(x0 + 20, y - 0.4, nm, 'Work', 2.2)
        L.text(x0 + 20, y - 4.6, proc, 'Mono', 1.95, P['sec'])
        y -= 13
    L.text(x0, y - 1, 'proposta, a validar no protótipo', 'Mono', 1.9, P['sec'])
    # balanço de energia (barra empilhada com escala)
    bx, bw, byy = 252.0, 146.0, 86.0
    L.rotulo(bx, 122, EN['titulo'], size=2.1, cs=0.4)
    lim = EN['limite_mA']; s = bw / lim
    tot = sum(i['mA'] for i in EN['itens'])
    tons = ['#1B1E21', '#5A5F64', '#7D8186', '#A9A79F', '#D6D2C8']
    xx = bx
    for it, tn in zip(EN['itens'], tons):
        w = it['mA'] * s
        L.rect(xx, byy, w, 8, fill=tn); xx += w
    L.rect(bx, byy, bw, 8, stroke=P['tinta'], lw=0.15)
    for v in range(0, lim + 1, 100):
        L.line(bx + v * s, byy - 0.5, bx + v * s, byy - 2.2, P['tinta'], 0.12)
        L.text(bx + v * s, byy - 5.2, f'{v}', 'Mono', 1.9, anchor='c')
    for v in range(0, lim + 1, 20):
        L.line(bx + v * s, byy - 0.5, bx + v * s, byy - 1.2, P['tinta'], 0.08)
    L.text(bx + bw, byy - 8.6, 'mA', 'Mono', 1.9, P['sec'], anchor='r')
    L.line(bx + tot * s, byy + 8, bx + tot * s, byy + 12, P['tinta'], 0.15)
    L.text(bx + tot * s + 1, byy + 10, f"{tot} mA ≈ {br(tot * 5 / 1000, 2)} W", 'MonoM', 2.1)
    L.text(bx + bw, byy + 10, EN['limite_nome'], 'Mono', 1.9, P['sec'], anchor='r')
    y = byy - 13
    for i, (it, tn) in enumerate(zip(EN['itens'], tons)):
        col = i % 2; row = i // 2
        X = bx + col * 78; Y = y - row * 5.2
        L.rect(X, Y - 0.2, 3, 2.2, fill=tn)
        L.text(X + 4.5, Y, f"{it['nome']}: {it['mA']} mA", 'Work', 1.95)
    L.text(bx, y - 17, EN['nota'], 'Mono', 1.9, P['sec'])
    L.nota(252, 132, f"usa só {round(tot / lim * 100)} % do que uma porta USB 2.0 entrega", size=3.4)
    L.text(M, 33, 'Peças de catálogo, compradas prontas; nenhuma é exclusiva de um fornecedor só.', 'Work', 2.2)
    L.glossario('QFN/SOT: tipos de encapsulamento de chip · TPE: borracha termoplástica · anodização: camada de óxido colorida no alumínio · mA: miliampere')
    return L


# =====================================================================================
def assinatura(L, x, y, w, h, sig, col):
    L.line(x, y, x + w, y, P['borda'], 0.15); L.line(x, y, x, y + h, P['borda'], 0.15)
    for k in range(5):
        L.line(x + k * w / 4, y, x + k * w / 4, y - 1, P['borda'], 0.12)
    pts = []
    for i in range(201):
        t = i / 200 * 4.0
        if sig == 'const': b = 1.0
        elif sig == 'breath': b = 0.15 + 0.85 * (0.5 - 0.5 * math.cos(2 * math.pi * t / 4.0))
        elif sig == 'blink': b = 1.0 if (t * 2) % 1 < 0.5 else 0.0
        else: b = 0.0
        pts.append((x + t / 4 * w, y + b * h * 0.92))
    if sig == 'blink':
        q = []
        for i, p in enumerate(pts):
            if i and abs(p[1] - pts[i - 1][1]) > 1: q.append((p[0], pts[i - 1][1]))
            q.append(p)
        pts = q
    L.poly(pts, stroke=col or P['borda'], lw=0.35, close=False)


def brilho_estado(e, t):
    k = e['onda']
    if k == 'const':
        return e['nivel']
    if k == 'breath':
        T = e['periodo_s']
        return e['piso'] + (1 - e['piso']) * ((1 - math.cos(2 * math.pi * t / T)) / 2) ** e['expoente']
    if k == 'square':
        per = 1.0 / e['freq_hz']
        return 1.0 if (t % per) < e['duty'] * per else e['piso']
    if k == 'flash':
        return 1.0 if (t % e['periodo_s']) < e['pulso_s'] else e['piso']
    if k == 'double_pulse':
        tm = t % e['periodo_s']
        p1 = 0.0 <= tm < e['pulso_s']
        p2 = (e['pulso_s'] + e['gap_s']) <= tm < (2 * e['pulso_s'] + e['gap_s'])
        return e['pico'] if (p1 or p2) else e['piso']
    return 0.0


def curva(L, x, y, w, h, e):
    """Assinatura de brilho 0–4 s. y = baseline, h = amplitude do brilho 1,0."""
    L.line(x, y, x + w, y, P['borda'], 0.12)
    L.line(x, y, x, y + h * 0.22, P['borda'], 0.12)
    pts, prev = [], None
    n = 400
    for i in range(n + 1):
        t = i / n * 4.0
        b = brilho_estado(e, t)
        px, py = x + t / 4.0 * w, y + b * h
        if prev is not None and abs(py - prev[1]) > 0.35:
            pts.append((px, prev[1]))
        pts.append((px, py))
        prev = (px, py)
    L.poly(pts, stroke=e['hex'], lw=0.40, close=False)
    if 'semanal_nivel' in e:
        sy = y + e['semanal_nivel'] * h
        L.line(x, sy, x + w, sy, e['hex'], 0.28, dash=[1.2, 0.9])
    L.text(x, y - 3.6, '0', 'Mono', 1.75, L.ink, anchor='c')
    L.text(x + w, y - 3.6, '4 s', 'Mono', 1.75, L.ink, anchor='c')


def l05(c):
    L = Lamina(c, 5, TOTAL, 'EM FUNCIONAMENTO', RODAPE, noite=True)
    L.titulo('EM FUNCIONAMENTO')
    L.nota(M, 251.5, 'cor diz o quê; ritmo diz a urgência — sala sempre acima da IA', size=3.5, col=L.ink)
    from PIL import Image as _I
    _w, _h = _I.open(IMG('p5_sala_ocupado')).size

    # Faixa superior: MODO SALA (3 estados) + MODO MISTO (3 LEDs)
    cw1 = (W - 2 * M) / 4.0
    L.text(M, 244.0, 'MODO SALA · PADRÃO (PARA A SALA)', 'JuraM', 1.95, L.sec, cs=0.6)
    L.text(M + 3 * cw1, 244.0, 'MODO MISTO · 3 LEDS', 'JuraM', 1.95, L.sec, cs=0.6)
    sala_ids = ['sala_livre', 'sala_prestes', 'sala_ocupado']
    ih1 = 56.0; iw1 = ih1 * _w / _h
    for i, mid in enumerate(sala_ids):
        e = MODO[mid]
        cx = M + (i + 0.5) * cw1
        L.image(IMG(f'p5_{mid}'), cx - iw1 / 2, 186.0, iw1, ih1, f'estado {mid}')
        L.text(cx, 180.5, e['nome'], 'JuraM', 2.35, L.ink, cs=0.9, anchor='c')
        L.text(cx, 176.2, e['hex'], 'Mono', 1.85, L.ink, anchor='c')
        L.text(cx, 172.2, e['sinal'], 'Mono', 1.75, L.sec, anchor='c')
        gx, gw, gy, gh = cx - 27, 54, 152.5, 14.5
        curva(L, gx, gy, gw, gh, e)

    # 4.ª coluna superior: MODO MISTO (divisão física dos 3 LEDs)
    cx = M + 3.5 * cw1
    L.image(IMG('p5_misto'), cx - iw1 / 2, 186.0, iw1, ih1, 'modo misto 3 leds')
    L.text(cx, 180.5, 'SALA + IA', 'JuraM', 2.35, L.ink, cs=0.9, anchor='c')
    L.text(cx, 176.2, '0x03+0x02 sala · 0x01 IA', 'Mono', 1.8, L.ink, anchor='c')
    L.text(cx, 172.2, 'v1: OCUPADO trava 0xFF · IA some', 'Mono', 1.75, L.sec, anchor='c')
    bx, bw = cx - 27, 54
    leds = [('LED 3 · TOPO', 'SALA', MODO['sala_livre']['hex']),
            ('LED 2 · MEIO', 'SALA', MODO['sala_livre']['hex']),
            ('LED 1 · BAIXO', 'IA (EX.: ERRO)', MODO['ia_erro']['hex'])]
    yy = 162.5
    for ld, fn, hx_c in leds:
        L.circle(bx + 2.0, yy + 0.9, 1.15, fill=hx_c)
        L.text(bx + 5.2, yy, ld, 'Mono', 1.7, L.ink)
        L.text(bx + bw, yy, fn, 'Mono', 1.7, L.sec, anchor='r')
        yy -= 4.8

    L.line(M, 144.5, W - M, 144.5, P['borda'], 0.15)

    # Faixa inferior: MODO IA (opt-in, 5 estados)
    L.text(M, 139.8, 'MODO IA · OPT-IN (CLAUDE · CHATGPT · GROK)', 'JuraM', 1.95, L.sec, cs=0.6)
    cw2 = (W - 2 * M) / 5.0
    ia_ids = ['ia_livre', 'ia_processando', 'ia_atencao', 'ia_erro', 'ia_limite']
    ih2 = 54.0; iw2 = ih2 * _w / _h
    for i, mid in enumerate(ia_ids):
        e = MODO[mid]
        cx = M + (i + 0.5) * cw2
        L.image(IMG(f'p5_{mid}'), cx - iw2 / 2, 83.5, iw2, ih2, f'estado {mid}')
        L.text(cx, 78.2, e['nome'], 'JuraM', 2.1, L.ink, cs=0.65, anchor='c')
        L.text(cx, 73.9, e['hex'], 'Mono', 1.8, L.ink, anchor='c')
        L.text(cx, 70.0, e['sinal'], 'Mono', 1.65, L.sec, anchor='c')
        gx, gw, gy, gh = cx - 26, 52, 50.5, 14.5
        curva(L, gx, gy, gw, gh, e)
        if e.get('nota_wcag'):
            L.text(cx, 41.5, e['nota_wcag'], 'Mono', 1.65, L.sec, anchor='c')
        elif e.get('nota_sub'):
            L.text(cx, 41.5, e['nota_sub'], 'Mono', 1.6, L.sec, anchor='c')

    # Escada de prioridade global no rodapé da lâmina
    L.text(M, 29.2, 'PRIORIDADE', 'JuraM', 1.9, L.sec, cs=0.8)
    x = M + 29
    curto = {
        'sala_ocupado': 'OCUPADO',
        'sala_prestes': 'PRESTES',
        'ia_erro': 'ERRO',
        'ia_atencao': 'ATENÇÃO',
        'ia_processando': 'PROCESSANDO',
        'ia_limite': 'LIMITE',
        'sala_livre': 'LIVRE',
        'ia_livre': 'IA OCIOSA',
    }
    ordem_p = PR['prioridade_ordem']
    for i, mid in enumerate(ordem_p):
        e = MODO[mid]
        L.circle(x + 1.0, 30.0, 1.05, fill=e['hex'])
        x += 3.3
        bb = L.text(x, 29.2, curto[mid], 'JuraM', 1.85, L.ink, cs=0.3)
        x = bb[2] + 1.6
        if i < len(ordem_p) - 1:
            L.text(x, 29.2, '>', 'Mono', 1.8, L.sec)
            x += 3.0
    return L

# =====================================================================================
def caixa(L, x, y, w, h, titulo, linhas, destaque=False):
    L.rect(x, y, w, h, stroke=P['tinta'], lw=0.35 if destaque else 0.2)
    L.text(x + 2.5, y + h - 4.5, titulo, 'JuraM', 2.2, cs=0.5)
    yy = y + h - 9.5
    for s in linhas:
        L.text(x + 2.5, yy, s, 'Mono', 1.95, P['sec']); yy -= 3.9


def l06(c):
    L = Lamina(c, 6, TOTAL, 'SISTEMA', RODAPE)
    L.titulo('SISTEMA')
    bl = [
        ('FONTES', [
            'SALA: Google Calendar (OAuth)',
            'SALA: Outlook / MS Graph (OAuth)',
            'SALA: atalho manual · mic/câm.',
            'IA: Claude Code hooks (oficial)',
            'IA: Codex CLI notify (oficial)',
            'IA: ChatGPT/Claude/Grok web:',
            '    extensão browser (proposta, s/ API)',
            'IA: limites 5 h / sem. (a validar)',
        ], 92.0),
        ('APP DESKTOP', [
            'Win · macOS · Linux',
            'motor de prioridade',
            'modo SALA (0xFF)',
            'ou MISTO (3+2 / 1)',
            'aviso: 5 min (config. no app)',
        ], 43.0),
        ('USB HID', [
            'relatório de 8 bytes',
            'sem driver nativo',
            '12 Mbit/s · 1 ms',
        ], 41.0),
        ('MCU', [
            'STM32C071',
            'decodifica opcode',
            '8 → 16 bit + gama',
            'estados e curvas',
        ], 41.0),
        ('BUFFER', [
            '3,3 → 5 V',
            'SN74AHCT1G125',
            'sinal limpo 800 kb/s',
        ], 40.0),
        ('3 × LED', [
            'WS2816B-2020',
            '48 bit por LED',
            'PWM 10 kHz',
            '1 baixo · 2–3 topo',
        ], 41.0),
        ('DIFUSOR', [
            'PC opalino',
            'Ø16 mm',
            'luz homogênea',
        ], 40.0),
    ]
    g = 8.33
    x = M; y = 188; h = 44
    xs_b = []
    for i, (t, ls, w) in enumerate(bl):
        xs_b.append(x)
        caixa(L, x, y, w, h, t, ls, destaque=(t == 'MCU'))
        if i < len(bl) - 1:
            L.line(x + w + 0.8, y + h / 2, x + w + g - 1.2, y + h / 2, P['tinta'], 0.2)
            L.seta(x + w + g - 0.8, y + h / 2, 0, P['tinta'])
        x += w + g
    L.text(xs_b[0], 181.5, 'ENTRADA E REGRA', 'JuraM', 2.0, P['sec'], cs=0.6)
    L.text(xs_b[2], 181.5, 'TRANSPORTE', 'JuraM', 2.0, P['sec'], cs=0.6)
    L.text(xs_b[3], 181.5, 'PROCESSAMENTO', 'JuraM', 2.0, P['sec'], cs=0.6)
    L.text(xs_b[5], 181.5, 'ATUAÇÃO', 'JuraM', 2.0, P['sec'], cs=0.6)

    # tabela de protocolo
    L.rotulo(M, 166, 'PROTOCOLO · RELATÓRIO HID DE 8 BYTES')
    rows = [['0x01', 'cor fixa', 'LED, R, G, B', 'testado (Flag)'],
            ['0x02', 'transição suave', 'LED, R, G, B, tempo', 'testado (Flag)'],
            ['0x03', 'estrobo', 'LED, R, G, B, tempo, repetições', 'testado (Flag)'],
            ['0x04', 'onda', 'tipo, R, G, B, repetições, vel.', 'testado (Flag)'],
            ['0x06', 'padrão gravado', 'nº do padrão, repetições', 'testado (Flag)'],
            ['0x80', 'versão / boot', '0x80 0x3c (+ serial do boot)', 'testado (Flag)'],
            ['0x05 · 0x07–0F', 'não mapeados', 'silêncio (inexistentes no Flag)', 'reconciliado'],
            ['LED', 'endereço', '0x01 baixo · 0x02 meio · 0x03 topo · 0xFF', 'testado (Flag)']]
    tabela(L, M, 161, ['byte 0', 'função', 'bytes seguintes', 'estado'], rows, [28, 32, 76, 44], alt=5.5)
    L.text(M, 107, 'extensão por estados nativos (respiração 2,4 s e divisão 3 LEDs) no firmware SIGNA · a implementar', 'Mono', 1.9, P['sec'])

    # exemplo passo a passo
    x0 = 222
    L.rotulo(x0, 166, f"EXEMPLO · MUDAR PARA SALA: {MODO['sala_ocupado']['nome']}")
    steps = [('1', 'app lê agenda / regra', f"OCUPADO = {VERM}"),
             ('2', 'envia o relatório', '01 FF FF 3B 2F 00 00 00'),
             ('3', 'MCU confirma', 'responde 42'),
             ('4', 'converte 8 → 16 bit', 'FF→FFFF · 3B→3B3B · 2F→2F2F'),
             ('5', 'transmite 3 × 48 bit (GRB)', '144 bit × 1,25 µs = 180 µs'),
             ('6', 'pausa de quadro', '> 280 µs (datasheet)'),
             ('7', 'os 3 LEDs acendem', 'PWM 10 kHz, sem cintilação')]
    y = 158
    for n, a, b in steps:
        L.text(x0, y, n, 'MonoM', 2.3)
        L.text(x0 + 6, y, a, 'Work', 2.2)
        L.text(x0 + 66, y, b, 'Mono', 2.1, VERM if n == '2' else P['tinta'])
        y -= 7.2
    # trem de bits (0x3B = 00111011)
    bx, byy = x0, 72.0; tb = 12.0
    L.text(x0, 90, 'UM BYTE NO FIO · 0x3B = 0011 1011', 'JuraM', 2.0, P['sec'], cs=0.4)
    pts = [(bx, byy)]
    for i, b in enumerate('00111011'):
        x1 = bx + i * tb; hi = 0.62 if b == '1' else 0.26
        pts += [(x1, byy), (x1, byy + 7), (x1 + hi / 1.25 * tb, byy + 7), (x1 + hi / 1.25 * tb, byy)]
        L.text(x1 + tb / 2, byy - 4.2, b, 'Mono', 2.0, anchor='c')
    pts.append((bx + 8 * tb, byy))
    L.poly(pts, stroke=P['tinta'], lw=0.3, close=False)
    L.cota_h(bx, bx + tb, byy + 7, byy + 11, '1,25 µs', ext=False)
    L.text(bx + 8 * tb + 3, byy + 3, '“1” = 0,52–0,80 µs alto', 'Mono', 1.9, P['sec'])
    L.text(bx + 8 * tb + 3, byy - 0.6, '“0” = 0,20–0,32 µs alto', 'Mono', 1.9, P['sec'])
    L.text(x0, 52, 'Modo misto usa 0x03+0x02 (sala) e 0x01 (IA); leitura web/limites das IAs a validar.', 'Work', 2.15)
    L.nota(M, 92, 'sem driver: qualquer sistema reconhece o dispositivo', size=3.4)
    L.glossario('HID: classe USB sem driver · OAuth: autorização segura de agenda · hooks/notify: avisos oficiais de CLI · GRB: ordem verde-vermelho-azul · PWM: modulação de brilho')
    return L

# =====================================================================================
def l07(c):
    L = Lamina(c, 7, TOTAL, 'SUBSISTEMA · RENDERS', RODAPE)
    L.titulo('SUBSISTEMA · RENDERS')
    L.image(IMG('p7_frente'), M, 46, 92, 197, 'frente')
    L.image(IMG('p7_verso'), M + 100, 46, 92, 197, 'verso')
    L.image(IMG('p7_iso'), 218, 46, 186, 186, 'iso')
    L.text(M, 40, 'FRENTE · COMPONENTES', 'JuraM', 2.1, P['sec'], cs=0.5)
    L.text(M + 100, 40, 'VERSO · SWD E BOOT0', 'JuraM', 2.1, P['sec'], cs=0.5)
    L.text(218, 40, 'ISOMETRIA · LUZ DE ESTÚDIO', 'JuraM', 2.1, P['sec'], cs=0.5)
    L.text(M, 33, 'render conceitual gerado do CAD da rev C (KiCad → Blender); não é foto de protótipo', 'Mono', 1.9, P['sec'])
    L.nota(W - M, 238, 'o tamanho real cabe numa unha: 11 × 44 mm', size=3.6, anchor='r')
    L.glossario('CAD: desenho técnico em computador · SWD: porta de depuração · BOOT0: contato que força a gravação pelo USB')
    return L


def l08(c):
    L = Lamina(c, 8, TOTAL, 'PRODUTO · RENDERS I', RODAPE)
    L.titulo('PRODUTO · RENDERS I')
    L.image(IMG('p8_principal'), M, 30, 178, 222.5, 'principal')
    L.image(IMG('p8_alerta'), 206, 136, 87, 116, 'alerta')
    L.image(IMG('p8_detalhe'), 206, 30, 87, 87, 'detalhe')
    L.text(206, 130, f"FRONTAL · SALA: {MODO['sala_prestes']['nome']} {MODO['sala_prestes']['hex']}", 'JuraM', 2.0, P['sec'], cs=0.4)
    L.text(206, 125.5, 'aviso de agenda · estúdio escuro', 'Mono', 1.9, P['sec'])
    L.text(206, 121.2, 'DETALHE · CORTE DA TAMPA', 'JuraM', 2.0, P['sec'], cs=0.4)
    x0 = 310; y = 246
    L.rotulo(x0, y, 'O QUE O CLIENTE COMPRA'); y -= 10
    for a, b in [('acabamento', 'alumínio anodizado + PC opalino'), ('montagem', 'sem parafuso, sem cola · ~5 min'),
                 ('agenda', 'Google e Outlook (OAuth)'), ('monitor de IA', 'Claude, ChatGPT e Grok (opt-in)'),
                 ('instalação', 'USB-C HID, sem driver')]:
        L.text(x0, y, a.upper(), 'JuraM', 2.0, P['sec'], cs=0.4); L.text(x0, y - 4.4, b, 'Work', 2.2); y -= 12
    y -= 4
    L.rotulo(x0, y, 'NÚMEROS'); y -= 10
    for a, b in [('preço sugerido', brl(R['preco_sug'])), ('custo unitário', brl(R['custo_un_plano'], 2)),
                 ('margem de contribuição', brl(R['composicao_preco']['margem'] + R['composicao_preco']['fixos'] + R['composicao_preco']['investimento'], 2)),
                 ('massa', '≈ 20 g (est.)')]:
        L.text(x0, y, a, 'Work', 2.15, P['sec']); L.text(W - M, y, b, 'MonoM', 2.3, anchor='r'); y -= 6.2
    L.text(x0, y - 1, 'custo: lote 1.000 sem molde · lâmina 11', 'Mono', 1.9, P['sec'])
    L.text(x0, 40, f"modo principal: SALA {MODO['sala_ocupado']['nome']} {VERM}", 'Mono', 1.9, P['sec'])
    L.text(x0, 35.6, 'renders conceituais; proposta,', 'Mono', 1.9, P['sec'])
    L.text(x0, 31.6, 'a validar no protótipo', 'Mono', 1.9, P['sec'])
    L.nota(x0, 64, 'parece joia de mesa, custa como acessório', size=3.6)
    return L

def l09(c):
    L = Lamina(c, 9, TOTAL, 'PRODUTO · EM USO E MONTAGEM', RODAPE)
    L.titulo('PRODUTO · EM USO E MONTAGEM')
    L.image(IMG('p9_uso'), M, 126, 168, 126, 'uso')
    L.text(M, 120.5, f"EM USO · AO LADO DO MONITOR, SALA: {MODO['sala_ocupado']['nome']} {VERM}", 'JuraM', 2.0, P['sec'], cs=0.4)
    L.image(IMG('p9_modos_crop'), M, 43, 184, 72, 'modos')
    nomes_p9 = ['LIVRE', 'PRESTES', 'OCUPADO', 'MISTO', 'PROCESS.', 'ATENÇÃO', 'ERRO', 'LIMITE']
    cxs = json.load(open(os.path.join(HERE, 'img', 'jpg', 'p9_modos_crop.json')))
    for i, nm in enumerate(nomes_p9):
        L.text(M + cxs[i] * 184, 39, nm, 'JuraM', 1.7, P['sec'], cs=0.18, anchor='c')
    L.text(M, 33, 'ESTADOS DE SALA, MISTO (3 LEDS) E IA LADO A LADO', 'JuraM', 2.0, P['sec'], cs=0.4)
    L.image(IMG('p9_explodida'), 214, 62, 126.7, 190, 'explodida')
    x0 = 350; y = 246
    L.rotulo(x0, y, 'MONTAGEM'); y -= 8
    for n, p in [('1', 'passa-cabo TPE'), ('2', 'tampa Al'), ('3', 'placa rev C'), ('4', 'berço PC'), ('5', 'tubo difusor'), ('6', 'tampão PC')]:
        L.text(x0, y, n, 'MonoM', 2.2); L.text(x0 + 5, y, p, 'Work', 2.15); y -= 5.6
    L.text(x0, y - 2, 'de cima para baixo', 'Mono', 1.9, P['sec'])
    L.text(214, 55, 'VISTA EXPLODIDA · 6 PEÇAS, ZERO PARAFUSOS', 'JuraM', 2.0, P['sec'], cs=0.4)
    L.text(214, 50.5, 'renders conceituais; proposta, a validar no protótipo', 'Mono', 1.9, P['sec'])
    L.nota(x0, 130, 'monta em 5 minutos', size=3.6)
    L.text(x0, 123.5, 'sem ferramenta especial', 'Work', 2.1)
    return L

# =====================================================================================
def l10(c):
    L = Lamina(c, 10, TOTAL, 'LISTA DE MATERIAL', RODAPE)
    L.titulo('LISTA DE MATERIAL')
    larg = [18, 46, 106, 12, 48, 58, 14]
    cols = ['item', 'descrição', 'especificação', 'qtd', 'origem / código', 'processo', 'status']
    y = 246
    cx = M
    for h, w, a in zip(cols, larg, ['l', 'l', 'l', 'r', 'l', 'l', 'c']):
        L.text(cx + (w - 1 if a == 'r' else w / 2 if a == 'c' else 0), y, h.upper(), 'JuraM', 1.95, P['sec'], cs=0.3, anchor=a); cx += w
    y -= 2.4; L.line(M, y, M + sum(larg), y, P['tinta'], 0.25)
    for g in BOM['grupos']:
        y -= 6.4
        L.text(M, y + 1.6, g['grupo'], 'JuraM', 2.1, cs=0.5)
        y -= 0.6
        for it in g['itens']:
            ref, desc, spec, q, orig, proc, st = it
            y -= 5.6
            cx = M
            for v, w, f, a in zip([ref, desc, spec, str(q), orig, proc, st], larg, ['MonoM', 'Work', 'Work', 'Mono', 'Mono', 'Work', 'MonoM'], ['l', 'l', 'l', 'r', 'l', 'l', 'c']):
                col = P['sec'] if (st == 'P' and f != 'MonoM') else P['tinta']
                L.text(cx + (w - 1 if a == 'r' else w / 2 if a == 'c' else 0), y + 1.5, v, f, 2.05, col, anchor=a); cx += w
            L.line(M, y, M + sum(larg), y, P['regua'], 0.1)
    L.text(M, 33, 'Q = cotação JLCPCB/LCSC em 2026-11-22  ·  E = estimativa (ver premissas)  ·  P = proposta, a validar no protótipo (em tinta clara)', 'Mono', 1.95, P['sec'])
    L.glossario('SMT: montagem automática de componentes de superfície · SLA: impressão 3D em resina · CNC: usinagem por controle numérico · OEM: fabricado sob encomenda')
    return L


# =====================================================================================
def l11(c):
    L = Lamina(c, 11, TOTAL, 'CUSTOS', RODAPE)
    L.titulo('CUSTOS')
    lt = R['lotes']
    lab = [('pecas', 'Peças eletrônicas + PCB', 'Q/E'), ('pcba', 'Montagem SMT (setup, estêncil, juntas)', 'E'), ('frete', 'Frete internacional', 'E'),
           ('mec', 'Mecânica + cabo', 'E'), ('molde', 'Ferramental (moldes)', 'E'), ('subtotal', '= Valor aduaneiro', ''),
           ('impostos', 'Impostos de importação', 'E'), ('despachante', 'Despachante', 'E'), ('embalagem', 'Embalagem (BR)', 'E'),
           ('montagem', 'Montagem final e teste (BR)', 'E')]
    rows = []
    for k, nm, o in lab:
        rows.append([nm, o] + [br(l['brl'][k]) for l in lt])
    rows.append(['= TOTAL DO LOTE (R$)', ''] + [br(l['total_brl']) for l in lt])
    rows.append(['Custo por unidade (R$)', ''] + [br(l['unit_brl'], 2) for l in lt])
    rows.append(['Custo por unidade (US$)', ''] + [br(l['unit_usd'], 2) for l in lt])
    rows.append(['Fator de importação', 'E'] + [pct(l['fator_imp']) for l in lt])
    tabela(L, M, 248, ['R$ por lote', 'origem', 'lote 5', 'lote 100', 'lote 1.000'], rows, [96, 16, 36, 36, 36],
           alt=6.6, bold_rows=(5, 10, 11), aligns=['l', 'c', 'r', 'r', 'r'], size=2.2)
    y = 136
    L.rotulo(M, y, 'FÓRMULAS', size=2.1); y -= 6.5
    for s in ['valor aduaneiro = peças + SMT + frete + mecânica + molde (US$ × câmbio)',
              'impostos = valor aduaneiro × fator',
              'fator RTS (lotes 5 e 100) = (1 + II 60 %) ÷ (1 − ICMS 20 %) − 1 = 100 %',
              'fator formal (lote 1.000) = II 16 % + IPI 15 % + PIS 2,1 % + COFINS 9,65 % + ICMS 18 % por dentro = 77,0 %',
              'total = valor aduaneiro + impostos + despachante + embalagem + montagem',
              f"câmbio R$ {br(FX, 4)} por US$ · PTAX venda BCB 19/11/2026 · rever antes de decidir",
              'peças: API JLCPCB por faixa de quantidade, 2026-11-22 · demais itens: estimativa']:
        L.text(M, y, s, 'Mono', 1.95); y -= 5.2
    # coluna direita: números grandes
    x0 = 252
    L.rotulo(x0, 246, 'CUSTO POR UNIDADE')
    y = 226
    for l in lt:
        L.text(x0, y + 7.5, f"LOTE {br(l['lote'])}", 'JuraM', 2.0, P['sec'], cs=0.5)
        L.text(x0, y - 4, brl(l['unit_brl'], 2), 'JuraL', 10.5, cs=0.4)
        L.text(W - M, y - 4, 'US$ ' + br(l['unit_usd'], 2), 'Mono', 2.2, P['sec'], anchor='r')
        y -= 26
    # composição do menor lote
    l5 = lt[0]; cp = l5['comp']; tot = l5['total_brl']
    L.rotulo(x0, 136, 'COMPOSIÇÃO DO LOTE 5', size=2.1)
    bx, bw = x0, 152.0; byy = 120
    tons = ['#1B1E21', '#7D8186', '#A9A79F', '#D6D2C8']
    xx = bx
    items = [('peças', cp['pecas']), ('taxas e frete', cp['taxas_frete']), ('mecânica e acessórios', cp['mecanica_acess']), ('impostos', cp['impostos'])]
    for (nm, v), tn in zip(items, tons):
        w = v / tot * bw; L.rect(xx, byy, w, 8, fill=tn); xx += w
    L.rect(bx, byy, bw, 8, stroke=P['tinta'], lw=0.15)
    y = byy - 6
    for (nm, v), tn in zip(items, tons):
        L.rect(bx, y - 0.2, 3, 2.2, fill=tn)
        L.text(bx + 5, y, nm, 'Work', 2.1); L.text(bx + 100, y, brl(v), 'Mono', 2.1, anchor='r'); L.text(W - M, y, pct(v / tot), 'Mono', 2.1, anchor='r')
        y -= 5.4
    # nota do ferramental
    l1k = lt[2]; sm = R['lote1000_sem_molde']
    L.rotulo(x0, 72, 'PESO DO FERRAMENTAL · LOTE 1.000', size=2.1)
    L.text(x0, 64, 'com molde', 'Work', 2.1, P['sec']); L.text(x0 + 60, 64, brl(l1k['unit_brl'], 2), 'MonoM', 2.4)
    L.text(x0, 58, 'sem molde', 'Work', 2.1, P['sec']); L.text(x0 + 60, 58, brl(sm['unit_brl'], 2), 'MonoM', 2.4)
    L.text(x0, 52, 'molde no custo do lote', 'Work', 2.1, P['sec']); L.text(x0 + 60, 52, pct(1 - sm['unit_brl'] / l1k['unit_brl']), 'MonoM', 2.4)
    L.text(x0, 45, 'no plano o molde vira investimento do ano 0', 'Mono', 1.95, P['sec'])
    L.nota(x0, 34, 'escala derruba o custo: de R$ 459 para R$ 70', size=3.6)
    L.glossario('RTS: regime simplificado de importação por courier · II/IPI/PIS/COFINS/ICMS: tributos de importação · valor aduaneiro: base dos impostos · PTAX: câmbio oficial do BCB')
    return L


# =====================================================================================
def l12(c):
    L = Lamina(c, 12, TOTAL, 'PLANO DE NEGÓCIO · CICLO DE VIDA', RODAPE)
    L.titulo('PLANO DE NEGÓCIO · CICLO DE VIDA')
    un = NG['unidades']; mx = 3000
    gx, gy, gw, gh = 30.0, 118.0, 196.0, 104.0
    bw = gw / len(un)
    # faixas de fase
    for k, f in enumerate(NG['fases']):
        a = min(f['anos']) - 1; b = max(f['anos'])
        if k % 2 == 0:
            L.rect(gx + a * bw, gy, (b - a) * bw, gh, fill='#E6E2D9')
        L.text(gx + (a + b) / 2 * bw, gy + gh + 4, f['fase'], 'JuraM', 2.0, P['sec'], cs=0.5, anchor='c')
    for v in range(0, mx + 1, 500):
        y = gy + v / mx * gh
        L.line(gx - 1.5, y, gx, y, P['tinta'], 0.12)
        L.text(gx - 2.5, y - 0.7, br(v), 'Mono', 1.9, anchor='r')
    L.line(gx, gy, gx, gy + gh, P['tinta'], 0.15); L.line(gx, gy, gx + gw, gy, P['tinta'], 0.15)
    for i, u in enumerate(un):
        x = gx + i * bw + bw * 0.28; w = bw * 0.44; h = u / mx * gh
        L.rect(x, gy, w, h, fill=P['tinta'])
        L.text(x + w / 2, gy + h + 1.6, br(u), 'MonoM', 2.2, anchor='c')
        L.text(x + w / 2, gy - 4.6, f'ANO {i + 1}', 'JuraM', 1.95, P['sec'], cs=0.4, anchor='c')
    L.text(gx - 14, gy + gh + 4, 'un./ano', 'Mono', 1.9, P['sec'])
    # estratégia por fase
    y = 102
    L.rotulo(M, y, 'ESTRATÉGIA POR FASE', size=2.1); y -= 7
    for f in NG['fases']:
        anos = '–'.join(str(a) for a in (f['anos'] if len(f['anos']) == 1 else [f['anos'][0], f['anos'][-1]]))
        L.text(M, y, f['fase'], 'JuraM', 1.95, cs=0.4); L.text(M + 34, y, f'ano {anos}', 'Mono', 1.95, P['sec'])
        L.text(M + 52, y, f['estrategia'], 'Work', 2.1); L.text(M + 152, y, f['canal'], 'Mono', 1.95, P['sec'])
        y -= 6
    L.text(M, y - 1, f"total no ciclo: {br(sum(un))} unidades · {NG['unidades_origem'][:62]}", 'Mono', 1.9, P['sec'])
    L.text(M, y - 5.2, NG['unidades_origem'][62:].strip(), 'Mono', 1.9, P['sec'])
    # investimento ano 0
    x0 = 246
    rows = [[n, brl(v)] for n, v in R['investimento']]
    rows.append(['TOTAL DO INVESTIMENTO (ANO 0)', brl(R['I0'])])
    tabela(L, x0, 250, ['investimento · ano 0', 'R$'], rows, [132, 26], alt=5.3, bold_rows=(len(rows) - 1,), aligns=['l', 'r'], size=2.0)
    # premissas
    y = 182
    L.rotulo(x0, y, 'PREMISSAS', size=2.1); y -= 3
    pr = [['custo unitário (lote 1.000, sem molde)', brl(R['custo_un_plano'], 2), 'E/Q'],
          ['comissão de canal sobre o preço', pct(NG['comissao'], 0), 'E'],
          ['frete absorvido por unidade', brl(NG['frete_absorvido_brl'], 2), 'E'],
          ['impostos sobre receita (Simples, Anexo II)', '4,5–7,6 %', 'E'],
          ['garantia sobre a receita', pct(NG['garantia'], 0), 'E'],
          ['despesas fixas por ano', brl(NG['fixos_ano_brl']), 'E'],
          ['capital de giro', '30 % do CPV', 'E'],
          ['TMA · horizonte', '14 % a.a. · 5 anos', 'F'],
          ['câmbio (PTAX 19/11/2026)', 'R$ ' + br(FX, 4), 'Q'],
          ['base de mercado (IBGE 2025)', '6,6 mi em casa', 'Q'],
          ['participação no pico (ano 3)', '0,04 %', 'E']]
    tabela(L, x0, y, ['premissa', 'valor', 'origem'], pr, [104, 40, 14], alt=5.1, aligns=['l', 'r', 'c'], size=2.0)
    L.text(x0, 54, 'F = ficha · Q = cotação datada · E = estimativa (ver premissas.md)', 'Mono', 1.9, P['sec'])
    L.text(x0, 49.5, 'impostos, câmbio e mercado datados de 2026-11-22: rever antes de decidir', 'Mono', 1.9, P['sec'])
    L.nota(M, 36, 'o negócio vive de 3 anos bons; o ano 1 só paga a entrada', size=3.6)
    L.glossario('CPV: custo do produto vendido · TMA: taxa mínima de atratividade, o retorno que o investidor exige · Simples Anexo II: tabela de impostos da indústria pequena')
    return L


# =====================================================================================
def l13(c):
    L = Lamina(c, 13, TOTAL, 'PLANO DE NEGÓCIO · RETORNO', RODAPE)
    L.titulo('PLANO DE NEGÓCIO · RETORNO')
    A = R['anos']; I0 = R['I0']
    def row(nm, vals, tot=True):
        r = [nm] + vals
        return r
    f = lambda v: br(v) if round(v) >= 0 else '−' + br(-v)
    acum, accd = IND['acumulado'], IND['acumulado_desc']
    rows = [['Unidades', '—'] + [br(a['unidades']) for a in A] + [br(sum(a['unidades'] for a in A))],
            ['Receita', '—'] + [f(a['receita']) for a in A] + [f(sum(a['receita'] for a in A))],
            ['(−) custos variáveis', '—'] + [f(-a['variaveis']) for a in A] + [f(-sum(a['variaveis'] for a in A))],
            ['(−) despesas fixas', '—'] + [f(-a['fixos']) for a in A] + [f(-sum(a['fixos'] for a in A))],
            ['= resultado operacional', '—'] + [f(a['operacional']) for a in A] + [f(sum(a['operacional'] for a in A))],
            ['(−) investimento', f(-I0)] + ['—'] * 5 + [f(-I0)],
            ['(−) variação do giro', '—'] + [f(-a['dgiro']) for a in A] + [f(-sum(a['dgiro'] for a in A))],
            ['= fluxo de caixa livre', f(IND['fluxos'][0])] + [f(a['fcl']) for a in A] + [f(sum(IND['fluxos']))],
            ['acumulado', f(acum[0])] + [f(v) for v in acum[1:]] + [''],
            ['acumulado descontado 14 %', f(accd[0])] + [f(v) for v in accd[1:]] + ['']]
    tabela(L, M, 250, ['R$', 'ano 0', 'ano 1', 'ano 2', 'ano 3', 'ano 4', 'ano 5', 'total'], rows,
           [52, 24, 24, 24, 24, 24, 24, 26], alt=6.0, bold_rows=(4, 7), aligns=['l'] + ['r'] * 7, size=2.05)
    L.text(M, 182, 'custos variáveis = CPV + comissão + frete + impostos sobre receita + garantia (detalhe em resultados.json)', 'Mono', 1.9, P['sec'])
    # curva acumulado descontado
    gx, gy, gw, gh = 36.0, 50.0, 190.0, 112.0
    vmin, vmax = -200000, 500000
    Y = lambda v: gy + (v - vmin) / (vmax - vmin) * gh
    X = lambda t: gx + t / 5 * gw
    for v in range(vmin, vmax + 1, 100000):
        L.line(gx - 1.5, Y(v), gx, Y(v), P['tinta'], 0.12)
        L.text(gx - 2.5, Y(v) - 0.7, f(v / 1000) + ' mil', 'Mono', 1.9, anchor='r')
    L.line(gx, gy, gx, gy + gh, P['tinta'], 0.15)
    L.line(gx, Y(0), gx + gw, Y(0), P['tinta'], 0.2)
    for t in range(6):
        L.line(X(t), Y(0) - 1, X(t), Y(0) + 1, P['tinta'], 0.12)
        L.text(X(t), gy - 4.6, f'ano {t}', 'Mono', 1.9, anchor='c')
    L.poly([(X(t), Y(v)) for t, v in enumerate(accd)], stroke=P['tinta'], lw=0.45, close=False)
    L.poly([(X(t), Y(v)) for t, v in enumerate(acum)], stroke=P['clara'], lw=0.3, close=False, dash=[1.2, 0.8])
    for t, v in enumerate(accd):
        L.circle(X(t), Y(v), 0.8, fill=P['tinta'])
    pb = IND['payback_desc']
    L.line(X(pb), gy, X(pb), Y(0) + 4, P['tinta'], 0.2, dash=[0.8, 0.6])
    L.circle(X(pb), Y(0), 1.2, stroke=P['tinta'], lw=0.3, fill=P['papel'])
    L.text(X(pb) + 2.5, Y(0) - 6, f'payback descontado: {br(pb, 2)} anos', 'MonoM', 2.1)
    L.text(gx, gy + gh + 4, 'CAIXA ACUMULADO DESCONTADO (—) E SIMPLES (- -)', 'JuraM', 2.0, P['sec'], cs=0.4)
    # indicadores
    x0 = 262; y = 246
    L.rotulo(x0, y, 'INDICADORES · TMA 14 % A.A.')
    ind = [('VPL', brl(IND['vpl'])), ('TIR', pct(IND['tir'])), ('PAYBACK', f"{br(IND['payback'], 2)} / {br(IND['payback_desc'], 2)} anos"), ('ROI NO CICLO', pct(IND['roi'], 0))]
    sub = ['soma de FCLt ÷ 1,14^t, t = 0 a 5', 'taxa em que o VPL = 0', 'simples / descontado', 'soma FCL anos 1–5 ÷ investimento − 1']
    y -= 12
    for (k, v), s in zip(ind, sub):
        L.text(x0, y + 5, k, 'JuraM', 2.1, P['sec'], cs=0.6)
        L.text(x0, y - 5, v, 'JuraL', 8.0 if k != 'PAYBACK' else 6.2, cs=0.3)
        L.text(W - M, y + 5, s, 'Mono', 1.9, P['sec'], anchor='r')
        y -= 24
    L.rotulo(x0, 140, 'RISCOS', size=2.1)
    y = 132
    for rk in NG['riscos']:
        parts = [rk[i:i + 66] for i in range(0, len(rk), 66)]
        cut = rk[:68].rfind(' ') if len(rk) > 68 else len(rk)
        L.text(x0, y, '· ' + rk[:cut], 'Work', 2.0); y -= 4.4
        if cut < len(rk):
            L.text(x0 + 2.5, y, rk[cut:].strip(), 'Work', 2.0); y -= 4.4
        y -= 2.2
    L.text(x0, 66, f"no preço sugerido de {brl(R['preco_sug'])} · custo {brl(R['custo_un_plano'], 2)}/un.", 'Mono', 1.95, P['sec'])
    L.text(x0, 61.5, 'fluxos sem IR à parte: o Simples já o inclui', 'Mono', 1.95, P['sec'])
    L.nota(x0, 46, 'cada real investido volta quase quatro vezes', size=3.6)
    L.glossario('VPL: valor presente líquido · TIR: taxa interna de retorno · payback: tempo para recuperar o investimento · FCL: fluxo de caixa livre · ROI: retorno sobre o investimento')
    return L


# =====================================================================================
def l14(c):
    L = Lamina(c, 14, TOTAL, 'PLANO DE NEGÓCIO · PREÇO', RODAPE)
    L.titulo('PLANO DE NEGÓCIO · PREÇO')
    L.text(M, 236, 'PREÇO SUGERIDO AO CONSUMIDOR', 'JuraM', 2.2, P['sec'], cs=0.8)
    L.text(M, 208, brl(R['preco_sug']), 'JuraL', 24, cs=1.0, tag='preco')
    y = 196
    for k, v in [('preço mínimo (VPL = 0 · TIR = TMA 14 %)', brl(R['preco_min'], 2)),
                 ('margem de segurança sobre o mínimo', pct(NG['margem_seguranca'], 0) + ', final 9'),
                 ('volume de equilíbrio no preço sugerido', f"{br(R['volume_equilibrio_un'])} un. ({pct(R['volume_equilibrio_mult'], 0)} do plano)"),
                 ('referência: luz “ocupado” USB 2 cores, sem software', 'R$ 146,24')]:
        L.text(M, y, k, 'Work', 2.15, P['sec']); L.text(M + 175, y, v, 'MonoM', 2.2, anchor='r'); y -= 6.2
    L.text(M, y - 0.5, 'referência: Amazon.com.br, ASIN B0GPXXQ6ZV, 2026-11-22', 'Mono', 1.9, P['sec'])
    # curva VPL × preço
    gx, gy, gw, gh = 40.0, 44.0, 172.0, 104.0
    cv = R['curva_vpl_preco']; p0, p1 = cv[0][0], cv[-1][0]
    vmin, vmax = -400000, 800000
    X = lambda p: gx + (p - p0) / (p1 - p0) * gw
    Y = lambda v: gy + (v - vmin) / (vmax - vmin) * gh
    for v in range(vmin, vmax + 1, 200000):
        L.line(gx - 1.5, Y(v), gx, Y(v), P['tinta'], 0.12)
        L.text(gx - 2.5, Y(v) - 0.7, (br(v / 1000) if v >= 0 else '−' + br(-v / 1000)) + ' mil', 'Mono', 1.9, anchor='r')
    for p in range(p0, p1 + 1, 40):
        L.line(X(p), gy, X(p), gy - 1.2, P['tinta'], 0.12)
        L.text(X(p), gy - 4.6, br(p), 'Mono', 1.9, anchor='c')
    L.text(gx + gw, gy - 8.6, 'preço R$', 'Mono', 1.9, P['sec'], anchor='r')
    L.line(gx, gy, gx, gy + gh, P['tinta'], 0.15); L.line(gx, Y(0), gx + gw, Y(0), P['tinta'], 0.2)
    L.poly([(X(p), Y(max(min(v, vmax), vmin))) for p, v in cv], stroke=P['tinta'], lw=0.45, close=False)
    pm, ps = R['preco_min'], R['preco_sug']
    L.circle(X(pm), Y(0), 1.2, stroke=P['tinta'], fill=P['papel'], lw=0.3)
    L.line(X(pm), Y(0) - 2, X(pm), gy + 2, P['tinta'], 0.15, dash=[0.8, 0.6])
    L.text(X(pm) + 2, gy + 4, f"mínimo {brl(pm, 2)}", 'MonoM', 2.0)
    vs = IND['vpl']
    L.circle(X(ps), Y(vs), 1.0, fill=P['tinta'])
    L.text(X(ps) - 2, Y(vs) + 2.5, f"sugerido: VPL {brl(vs / 1000)} mil", 'MonoM', 2.0, anchor='r')
    L.text(gx, gy + gh + 4, 'VPL × PREÇO (VOLUME DO PLANO)', 'JuraM', 2.0, P['sec'], cs=0.4)
    # matriz
    x0 = 238
    L.rotulo(x0, 246, 'MATRIZ DE VPL · PREÇO × VOLUME (R$ MIL)', size=2.1)
    cw = 33.0; y = 236
    L.text(x0, y, 'preço \\ volume', 'Mono', 1.9, P['sec'])
    for j, v in enumerate(R['matriz_volumes']):
        L.text(x0 + 34 + (j + 1) * cw - 1, y, pct(v, 0), 'MonoM', 2.0, anchor='r')
    y -= 2.5; L.line(x0, y, x0 + 34 + 4 * cw, y, P['tinta'], 0.2)
    for i, p in enumerate(R['matriz_precos']):
        y -= 8
        lab = brl(p, 2) if i == 0 else brl(p, 0)
        L.text(x0, y + 2, lab + (' mín.' if i == 0 else ' sug.' if i == 2 else ''), 'MonoM' if i == 2 else 'Mono', 2.0)
        for j, v in enumerate(R['matriz_vpl'][i]):
            s = br(v / 1000) if round(v / 1000) >= 0 else '−' + br(-v / 1000)
            if i == 2 and j == 2:
                L.rect(x0 + 34 + j * cw + 2, y - 0.6, cw - 2, 6.2, stroke=P['tinta'], lw=0.25)
            L.text(x0 + 34 + (j + 1) * cw - 1, y + 2, s, 'MonoM' if v >= 0 else 'Mono', 2.1, P['tinta'] if v >= 0 else P['sec'], anchor='r')
        L.line(x0, y - 0.6, x0 + 34 + 4 * cw, y - 0.6, P['regua'], 0.1)
    L.text(x0, y - 6, '100 % = 8.200 un. em 5 anos · negativo em tinta clara', 'Mono', 1.9, P['sec'])
    # composição do preço
    cp = R['composicao_preco']; ps = R['preco_sug']
    itens = [('custo do produto', cp['custo']), ('comissão de canal', cp['comissao']), ('frete absorvido', cp['frete']),
             ('impostos (média)', cp['impostos']), ('garantia', cp['garantia']), ('despesas fixas rateadas', cp['fixos']),
             ('investimento rateado', cp['investimento'])]
    itens = [(n, round(v, 2)) for n, v in itens]
    itens.append(('margem (resultado)', round(ps - sum(v for _, v in itens), 2)))
    L.rotulo(x0, 150, f'COMPOSIÇÃO DO PREÇO SUGERIDO · {brl(ps)} POR UNIDADE', size=2.1)
    bx, bw, byy = x0, W - M - x0, 134.0
    tons = ['#1B1E21', '#3A3E43', '#5A5F64', '#7D8186', '#A9A79F', '#C4C1B8', '#D6D2C8', '#FFFFFF']
    xx = bx
    for (n, v), tn in zip(itens, tons):
        w = v / ps * bw; L.rect(xx, byy, w, 8, fill=tn); xx += w
    L.rect(bx, byy, bw, 8, stroke=P['tinta'], lw=0.15)
    y = byy - 6
    for (n, v), tn in zip(itens, tons):
        L.rect(bx, y - 0.2, 3, 2.2, fill=tn, stroke=P['clara'], lw=0.08)
        L.text(bx + 5, y, n, 'Work', 2.1); L.text(bx + 118, y, brl(v, 2), 'Mono', 2.1, anchor='r'); L.text(W - M, y, pct(v / ps), 'Mono', 2.1, anchor='r')
        y -= 5.3
    L.line(bx, y + 3.2, W - M, y + 3.2, P['tinta'], 0.2)
    L.text(bx + 5, y - 0.6, 'total', 'WorkM', 2.1); L.text(bx + 118, y - 0.6, brl(sum(v for _, v in itens), 2), 'MonoM', 2.1, anchor='r')
    L.text(W - M, y - 0.6, '100,0 %', 'MonoM', 2.1, anchor='r')
    L.text(bx, y - 8, 'impostos, fixos e investimento rateados por 8.200 un.', 'Mono', 1.9, P['sec'])
    L.nota(x0, 40, 'o preço de uma refeição; o retorno de um negócio', size=3.6)
    L.glossario('preço mínimo: o menor preço em que o projeto ainda rende a TMA · VPL × preço: quanto o negócio vale a cada preço · volume de equilíbrio: unidades em que VPL = 0')
    return L


def main():
    from reportlab.pdfgen import canvas
    out = os.path.join(HERE, f"{NOME.lower()}-conceito.pdf")
    c = canvas.Canvas(out, pagesize=(W * MM, H * MM))
    c.setTitle(f'{NOME} {PR["revisao"]} · caderno conceitual'); c.setAuthor('Lucas Tavares'); c.setSubject('Metrologia Luminosa')
    probs = {}
    for fn in [l01, l02, l03, l04, l05, l06, l07, l08, l09, l10, l11, l12, l13, l14]:
        L = fn(c)
        p = L.verifica()
        if p: probs[L.n] = p
        c.showPage()
    c.save()
    print(out, os.path.getsize(out) / 1e6, 'MB')
    for k, v in probs.items():
        for s in v: print(f'  [{k:02d}] {s}')
    import lib_metrologia as LM
    for g in LM.GLIFOS_FALTANDO:
        probs.setdefault(g[0], []).append(f'glifo ausente em {g[1]}: {g[2]!r} em {g[3]!r}')
        print(f'  [{g[0]:02d}] glifo ausente em {g[1]}: {g[2]!r} em {g[3]!r}')
    json.dump(probs, open(os.path.join(HERE, 'verificacao.json'), 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
