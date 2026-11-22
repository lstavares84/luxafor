"""Sistema visual 'Metrologia' (papel/noite, régua, marcas, rodapé, cotas, chamadas, tabelas) em reportlab.
Unidades em mm. Cada texto/imagem é registrado para a verificação automática de sobreposição e margem."""
import os
from reportlab.pdfgen import canvas as rcanvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, Color
import math

MM = 72 / 25.4
W, H, M = 420.0, 297.0, 16.0
HERE = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(HERE, 'fontes')
for n, f in [('JuraL', 'Jura-Light.ttf'), ('JuraM', 'Jura-Medium.ttf'), ('Mono', 'GeistMono-Regular.ttf'),
             ('MonoM', 'GeistMono-Medium.ttf'), ('Work', 'WorkSans-Regular.ttf'), ('WorkM', 'WorkSans-Medium.ttf'),
             ('Serif', 'InstrumentSerif-Italic.ttf')]:
    pdfmetrics.registerFont(TTFont(n, os.path.join(FD, f)))
from fontTools.ttLib import TTFont as _FT
CMAP = {n: set(_FT(os.path.join(FD, f)).getBestCmap().keys()) for n, f in [('JuraL', 'Jura-Light.ttf'), ('JuraM', 'Jura-Medium.ttf'), ('Mono', 'GeistMono-Regular.ttf'),
        ('MonoM', 'GeistMono-Medium.ttf'), ('Work', 'WorkSans-Regular.ttf'), ('WorkM', 'WorkSans-Medium.ttf'), ('Serif', 'InstrumentSerif-Italic.ttf')]}
GLIFOS_FALTANDO = []

P = dict(papel='#EEEAE2', tinta='#1B1E21', sec='#5A5F64', clara='#A9A79F', regua='#D6D2C8', grade='#E2DED5',
         noite='#090C11', painel='#161B22', borda='#2A313B', ntexto='#C9CDD3', ngrade='#151A21')


def hx(c):
    return HexColor(c) if isinstance(c, str) else c


def br(v, d=0):
    s = f"{v:,.{d}f}"
    if s.lstrip('-').strip('0.,') == '':   # evita "-0"
        s = s.lstrip('-')
    return s.replace(',', '§').replace('.', ',').replace('§', '.')


def brl(v, d=0):
    return ('−R$ ' if v < 0 else 'R$ ') + br(abs(v), d)


class Lamina:
    def __init__(self, c, n, total, nome_lamina, rodape_centro, noite=False):
        self.c, self.n, self.total, self.nome, self.noite = c, n, total, nome_lamina, noite
        self.rodape_centro = rodape_centro
        self.boxes = []      # (tipo, (x0,y0,x1,y1), rotulo)
        self.italicos = 0
        self.ink = P['ntexto'] if noite else P['tinta']
        self.sec = P['ntexto'] if noite else P['sec']
        self.light = P['borda'] if noite else P['clara']
        self.fundo()

    # ---------- primitivas ----------
    def fill(self, col): self.c.setFillColor(hx(col))
    def stroke(self, col, w=0.18): self.c.setStrokeColor(hx(col)); self.c.setLineWidth(w * MM)

    def line(self, x1, y1, x2, y2, col=None, w=0.18, dash=None):
        c = self.c; self.stroke(col or self.ink, w)
        c.setDash([d * MM for d in dash] if dash else [])
        c.line(x1 * MM, y1 * MM, x2 * MM, y2 * MM); c.setDash([])

    def rect(self, x, y, w, h, stroke=None, fill=None, lw=0.18, dash=None, r=0):
        c = self.c
        if stroke: self.stroke(stroke, lw)
        if fill: self.fill(fill)
        c.setDash([d * MM for d in dash] if dash else [])
        if r:
            c.roundRect(x * MM, y * MM, w * MM, h * MM, r * MM, stroke=1 if stroke else 0, fill=1 if fill else 0)
        else:
            c.rect(x * MM, y * MM, w * MM, h * MM, stroke=1 if stroke else 0, fill=1 if fill else 0)
        c.setDash([])

    def circle(self, x, y, r, stroke=None, fill=None, lw=0.18, dash=None):
        c = self.c
        if stroke: self.stroke(stroke, lw)
        if fill: self.fill(fill)
        c.setDash([d * MM for d in dash] if dash else [])
        c.circle(x * MM, y * MM, r * MM, stroke=1 if stroke else 0, fill=1 if fill else 0); c.setDash([])

    def poly(self, pts, stroke=None, fill=None, lw=0.18, close=True, dash=None):
        c = self.c; p = c.beginPath(); p.moveTo(pts[0][0] * MM, pts[0][1] * MM)
        for x, y in pts[1:]: p.lineTo(x * MM, y * MM)
        if close: p.close()
        if stroke: self.stroke(stroke, lw)
        if fill: self.fill(fill)
        c.setDash([d * MM for d in dash] if dash else [])
        c.drawPath(p, stroke=1 if stroke else 0, fill=1 if fill else 0); c.setDash([])

    def width(self, s, font, size, cs=0):
        return pdfmetrics.stringWidth(s, font, size * MM) / MM + cs * max(len(s) - 1, 0)

    def text(self, x, y, s, font='Mono', size=2.2, col=None, cs=0, anchor='l', reg=True, rot=0, tag=None):
        s = str(s); c = self.c
        falta = sorted(set(ch for ch in s if ord(ch) not in CMAP[font] and ch != ' '))
        if falta: GLIFOS_FALTANDO.append((self.n, font, ''.join(falta), s[:40]))
        w = self.width(s, font, size, cs)
        x0 = x - (w if anchor == 'r' else w / 2 if anchor == 'c' else 0)
        c.saveState(); c.setFillColor(hx(col or self.ink))
        if rot:
            c.translate(x * MM, y * MM); c.rotate(rot)
            t = c.beginText(); t.setTextOrigin(-(x - x0) * MM, 0)
        else:
            t = c.beginText(); t.setTextOrigin(x0 * MM, y * MM)
        t.setFont(font, size * MM); t.setCharSpace(cs * MM); t.textOut(s); c.drawText(t); c.restoreState()
        asc, desc = 0.74 * size, 0.22 * size
        if font == 'Serif': asc, desc = 0.72 * size, 0.25 * size
        if rot in (90, -270):
            bb = (x - asc, x0 - x + y, x + desc, x0 - x + y + w)
        else:
            bb = (x0, y - desc, x0 + w, y + asc)
        if reg: self.boxes.append(('t', bb, tag or s[:30]))
        if font == 'Serif': self.italicos += 1
        return bb

    def image(self, path, x, y, w, h, tag='img'):
        self.c.drawImage(path, x * MM, y * MM, w * MM, h * MM, preserveAspectRatio=False, mask=None)
        self.boxes.append(('i', (x, y, x + w, y + h), tag))

    def area(self, x0, y0, x1, y1, tag):
        self.boxes.append(('a', (x0, y0, x1, y1), tag))

    # ---------- moldura ----------
    def fundo(self):
        c = self.c
        self.fill(P['noite'] if self.noite else P['papel']); c.rect(0, 0, W * MM, H * MM, stroke=0, fill=1)
        self.fill(P['ngrade'] if self.noite else P['grade'])
        x = M
        while x <= W - M + 0.01:
            y = M
            while y <= H - M + 0.01:
                c.circle(x * MM, y * MM, 0.07 * MM, stroke=0, fill=1); y += 5
            x += 5
        # marcas de registro em L (fora da margem, braços de 5 mm)
        k = self.light if not self.noite else P['borda']
        for (cx, cy, dx, dy) in [(M - 5, M - 5, -1, -1), (W - M + 5, M - 5, 1, -1), (M - 5, H - M + 5, -1, 1), (W - M + 5, H - M + 5, 1, 1)]:
            self.line(cx, cy, cx - dx * 5, cy, k, 0.18); self.line(cx, cy, cx, cy - dy * 5, k, 0.18)
        # régua no topo (dentro da margem)
        y0 = H - M
        rc = P['borda'] if self.noite else P['sec']
        self.line(M, y0, W - M, y0, rc, 0.12)
        for i in range(0, int(W - 2 * M) + 1):
            L = 2.6 if i % 10 == 0 else 1.6 if i % 5 == 0 else 0.8
            self.line(M + i, y0, M + i, y0 - L, rc, 0.08 if L < 1 else 0.12)
            if i % 50 == 0 and 0 < i < W - 2 * M:
                self.text(M + i + 0.6, y0 - 4.6, str(i), 'Mono', 1.9, self.light if not self.noite else P['borda'], reg=False)
        # rodapé
        fy = M + 1.2
        self.text(M, fy, f"{self.n:02d} / {self.total}", 'Mono', 2.3, self.ink, tag='folio')
        self.text(W / 2, fy, self.rodape_centro, 'JuraM', 2.3, self.sec, cs=1.1, anchor='c', tag='rodape')
        self.text(W - M, fy, self.nome, 'JuraM', 2.3, self.ink, cs=0.6, anchor='r', tag='nome_lamina')
        self.line(M, M + 5.5, W - M, M + 5.5, P['borda'] if self.noite else P['regua'], 0.12)

    def titulo(self, s, sub='METROLOGIA LUMINOSA'):
        self.text(M, 261.5, s, 'JuraL', 7.0, self.ink, cs=1.6, tag='titulo')
        self.line(M, 257.6, M + 26, 257.6, self.ink, 0.25)
        if sub:
            self.text(W - M, 261.5, sub, 'JuraM', 2.3, self.sec, cs=1.0, anchor='r', tag='sub')

    def glossario(self, s):
        self.text(M, M + 7.6, s, 'Mono', 1.9, self.sec, tag='glossario')

    def nota(self, x, y, s, size=3.6, anchor='l', col=None):
        return self.text(x, y, s, 'Serif', size, col or self.sec, anchor=anchor, tag='nota')

    def rotulo(self, x, y, s, size=2.3, anchor='l', col=None, cs=0.6):
        return self.text(x, y, s.upper(), 'JuraM', size, col or self.ink, cs=cs, anchor=anchor)

    # ---------- desenho técnico ----------
    def seta(self, x, y, ang, col, L=1.6, a=16):
        r = math.radians(ang)
        p1 = (x - L * math.cos(r - math.radians(a)), y - L * math.sin(r - math.radians(a)))
        p2 = (x - L * math.cos(r + math.radians(a)), y - L * math.sin(r + math.radians(a)))
        self.poly([(x, y), p1, p2], fill=col)

    def cota_h(self, x1, x2, yref, ydim, s, col=None, size=2.1, ext=True, txt_below=False):
        col = col or self.ink
        if ext:
            d = 1 if ydim > yref else -1
            self.line(x1, yref + d * 0.8, x1, ydim + d * 1.2, col, 0.1)
            self.line(x2, yref + d * 0.8, x2, ydim + d * 1.2, col, 0.1)
        self.line(x1, ydim, x2, ydim, col, 0.12)
        self.seta(x2, ydim, 0, col); self.seta(x1, ydim, 180, col)
        ty = ydim - size - 0.8 if txt_below else ydim + 0.9
        return self.text((x1 + x2) / 2, ty, s, 'Mono', size, col, anchor='c', tag='cota ' + s)

    def cota_v(self, y1, y2, xref, xdim, s, col=None, size=2.1, ext=True, lado=None):
        col = col or self.ink
        if ext:
            d = 1 if xdim > xref else -1
            self.line(xref + d * 0.8, y1, xdim + d * 1.2, y1, col, 0.1)
            self.line(xref + d * 0.8, y2, xdim + d * 1.2, y2, col, 0.1)
        self.line(xdim, y1, xdim, y2, col, 0.12)
        self.seta(xdim, y2, 90, col); self.seta(xdim, y1, 270, col)
        lado = lado or ('l' if xdim < xref else 'r')
        tx = xdim - 0.9 if lado == 'l' else xdim + 0.9 + size * 0.75
        return self.text(tx, (y1 + y2) / 2, s, 'Mono', size, col, anchor='c', rot=90, tag='cota ' + s)

    def chamada(self, px, py, lx, ly, s, sub=None, anchor='l', col=None, size=2.2):
        col = col or self.ink
        self.circle(px, py, 0.45, fill=col)
        sx = lx - 2 if anchor == 'l' else lx + 2
        self.line(px, py, sx, ly, col, 0.12); self.line(sx, ly, lx - (0.5 if anchor == 'l' else -0.5), ly, col, 0.12)
        bb = self.text(lx, ly - 0.8, s.upper(), 'JuraM', size, col, cs=0.4, anchor=anchor)
        if sub:
            self.text(lx, ly - 0.8 - size - 1.2, sub, 'Mono', 1.9, self.sec, anchor=anchor)
        return bb

    # ---------- verificação ----------
    def verifica(self):
        prob = []
        for k, (x0, y0, x1, y1), t in self.boxes:
            if t in ('folio', 'rodape', 'nome_lamina'):
                continue
            if x0 < M - 0.05 or x1 > W - M + 0.05 or y0 < M - 0.05 or y1 > H - M + 0.05:
                prob.append(f'margem: {t!r} {tuple(round(v, 1) for v in (x0, y0, x1, y1))}')
        tb = [b for b in self.boxes]
        for i in range(len(tb)):
            for j in range(i + 1, len(tb)):
                ki, a, ti = tb[i]; kj, b, tj = tb[j]
                if ki != 't' and kj != 't':
                    if ki == 'a' or kj == 'a':
                        continue
                if (ki == 'a' and kj == 'i') or (ki == 'i' and kj == 'a'):
                    continue
                ox = min(a[2], b[2]) - max(a[0], b[0]); oy = min(a[3], b[3]) - max(a[1], b[1])
                if ox > 0.15 and oy > 0.15:
                    if (ki == 'a' or kj == 'a') and ('dentro' in ti or 'dentro' in tj):
                        continue
                    prob.append(f'sobreposição: {ti!r} × {tj!r}')
        if self.italicos > 2:
            prob.append(f'itálicos: {self.italicos} (> 2)')
        return prob
