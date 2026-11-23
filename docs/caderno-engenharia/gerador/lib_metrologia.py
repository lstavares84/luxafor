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
_IMG_SIZE_CACHE = {}

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
    def __init__(self, c, n, total, nome_lamina, rodape_centro, noite=False, skip_images=False):
        self.c, self.n, self.total, self.nome, self.noite = c, n, total, nome_lamina, noite
        self.rodape_centro = rodape_centro
        self.skip_images = skip_images
        self.boxes = []      # (tipo, (x0,y0,x1,y1), rotulo)
        self.italicos = 0
        self.ink = P['ntexto'] if noite else P['tinta']
        self.sec = P['ntexto'] if noite else P['sec']
        self.light = P['borda'] if noite else P['clara']
        self.top_y = 242.0
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

    def text(self, x, y, s, font='Mono', size=6.45, col=None, cs=0, anchor='l', reg=True, rot=0, tag=None):
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
        if not self.skip_images:
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
                self.text(M + i + 0.8, y0 - 7.1, str(i), 'Mono', 5.7, self.light if not self.noite else P['borda'], reg=False)
        # rodapé (3x = 6.9 mm)
        fy = M + 1.8
        fsize = 6.9
        folio_txt = f"{self.n:02d} / {self.total}"
        folio_w = self.width(folio_txt, 'Mono', fsize)
        rod_cs = 0.45
        rod_w = self.width(self.rodape_centro, 'JuraM', fsize, rod_cs)
        nome_txt = self.nome
        nome_cs = 0.35
        nome_w = self.width(nome_txt, 'JuraM', fsize, nome_cs)
        # garantir que os três textos do rodapé nunca colidam
        if (M + folio_w + 6 > W / 2 - rod_w / 2) or (W / 2 + rod_w / 2 + 6 > W - M - nome_w):
            rod_cs = 0.0
            rod_w = self.width(self.rodape_centro, 'JuraM', fsize, rod_cs)
            nome_cs = 0.0
            nome_w = self.width(nome_txt, 'JuraM', fsize, nome_cs)
        max_nome_w = (W - M) - (W / 2 + rod_w / 2 + 8)
        if nome_w > max_nome_w and max_nome_w > 20:
            while len(nome_txt) > 6 and self.width(nome_txt + '…', 'JuraM', fsize, nome_cs) > max_nome_w:
                nome_txt = nome_txt[:-1]
            nome_txt = nome_txt.rstrip() + '…'
        self.text(M, fy, folio_txt, 'Mono', fsize, self.ink, tag='folio')
        self.text(W / 2, fy, self.rodape_centro, 'JuraM', fsize, self.sec, cs=rod_cs, anchor='c', tag='rodape')
        self.text(W - M, fy, nome_txt, 'JuraM', fsize, self.ink, cs=nome_cs, anchor='r', tag='nome_lamina')
        self.line(M, M + 9.0, W - M, M + 9.0, P['borda'] if self.noite else P['regua'], 0.14)

    def titulo(self, s, sub='METROLOGIA LUMINOSA'):
        sub_size = 6.9
        sub_cs = 0.6
        sub_w = self.width(sub, 'JuraM', sub_size, sub_cs) if sub else 0
        avail1 = (W - 2 * M) - (sub_w + 14 if sub else 0)
        tsize = 11.5
        tcs = 0.9
        if self.width(s, 'JuraL', tsize, tcs) <= avail1:
            self.text(M, 258.5, s, 'JuraL', tsize, self.ink, cs=tcs, tag='titulo')
            self.line(M, 253.0, M + 36, 253.0, self.ink, 0.30)
            self.top_y = 242.0
        elif self.width(s, 'JuraL', 10.0, 0.4) <= avail1:
            self.text(M, 259.0, s, 'JuraL', 10.0, self.ink, cs=0.4, tag='titulo')
            self.line(M, 253.5, M + 36, 253.5, self.ink, 0.30)
            self.top_y = 242.5
        else:
            # quebra em 2 linhas para nunca encostar no sub
            lines = self.wrap(s, 'JuraL', 10.2, avail1, cs=0.4)
            if len(lines) > 2:
                lines = [lines[0], ' '.join(lines[1:])]
            self.text(M, 259.5, lines[0], 'JuraL', 10.2, self.ink, cs=0.4, tag='titulo:0')
            self.text(M, 246.5, lines[1], 'JuraL', 10.2, self.ink, cs=0.4, tag='titulo:1')
            self.line(M, 241.0, M + 36, 241.0, self.ink, 0.30)
            self.top_y = 230.0
        if sub:
            self.text(W - M, 259.5, sub, 'JuraM', sub_size, self.sec, cs=sub_cs, anchor='r', tag='sub')
        return self.top_y

    def glossario_min_y(self, s, size=5.8):
        if not s:
            return M + 12.0
        lines = self.wrap(s, 'Mono', size, W - 2 * M)
        leading = size * 1.34
        top_base = (M + 11.5) + (len(lines) - 1) * leading
        return top_base + 0.74 * size + 5.0

    def glossario(self, s, size=5.8):
        lines = self.wrap(s, 'Mono', size, W - 2 * M)
        leading = size * 1.34
        yy = (M + 11.5) + (len(lines) - 1) * leading
        for i, ln in enumerate(lines):
            self.text(M, yy, ln, 'Mono', size, self.sec, tag=f'glossario:{i}')
            yy -= leading
        return self.glossario_min_y(s, size)

    def nota(self, x, y, s, size=10.8, anchor='l', col=None):
        return self.text(x, y, s, 'Serif', size, col or self.sec, anchor=anchor, tag='nota')

    def rotulo(self, x, y, s, size=7.0, anchor='l', col=None, cs=0.45):
        return self.text(x, y, s.upper(), 'JuraM', size, col or self.ink, cs=cs, anchor=anchor)

    # ---------- desenho técnico ----------
    def seta(self, x, y, ang, col, L=2.4, a=18):
        r = math.radians(ang)
        p1 = (x - L * math.cos(r - math.radians(a)), y - L * math.sin(r - math.radians(a)))
        p2 = (x - L * math.cos(r + math.radians(a)), y - L * math.sin(r + math.radians(a)))
        self.poly([(x, y), p1, p2], fill=col)

    def cota_h(self, x1, x2, yref, ydim, s, col=None, size=6.3, ext=True, txt_below=False):
        col = col or self.ink
        if ext:
            d = 1 if ydim > yref else -1
            self.line(x1, yref + d * 0.8, x1, ydim + d * 1.2, col, 0.1)
            self.line(x2, yref + d * 0.8, x2, ydim + d * 1.2, col, 0.1)
        self.line(x1, ydim, x2, ydim, col, 0.12)
        self.seta(x2, ydim, 0, col); self.seta(x1, ydim, 180, col)
        ty = ydim - size - 0.8 if txt_below else ydim + 0.9
        return self.text((x1 + x2) / 2, ty, s, 'Mono', size, col, anchor='c', tag='cota ' + s)

    def cota_v(self, y1, y2, xref, xdim, s, col=None, size=6.3, ext=True, lado=None):
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

    def chamada(self, px, py, lx, ly, s, sub=None, anchor='l', col=None, size=6.6):
        col = col or self.ink
        self.circle(px, py, 0.6, fill=col)
        sx = lx - 2 if anchor == 'l' else lx + 2
        self.line(px, py, sx, ly, col, 0.12); self.line(sx, ly, lx - (0.5 if anchor == 'l' else -0.5), ly, col, 0.12)
        bb = self.text(lx, ly - 0.8, s.upper(), 'JuraM', size, col, cs=0.4, anchor=anchor)
        if sub:
            self.text(lx, ly - 0.8 - size - 1.6, sub, 'Mono', 5.7, self.sec, anchor=anchor)
        return bb

    def image_fit(self, path, x, y, w, h, tag='img', anchor='c', mask='auto'):
        """Encaixa a imagem na caixa (x, y, w, h) mm preservando a proporção. y é a base da caixa."""
        if path in _IMG_SIZE_CACHE:
            iw, ih = _IMG_SIZE_CACHE[path]
        else:
            from reportlab.lib.utils import ImageReader
            ir = ImageReader(path)
            iw, ih = ir.getSize()
            _IMG_SIZE_CACHE[path] = (iw, ih)
        if iw <= 0 or ih <= 0:
            return (x, y, x + w, y + h)
        aspect = iw / float(ih)
        if aspect >= (w / h if h else aspect):
            dw, dh = w, w / aspect
        else:
            dh, dw = h, h * aspect
        if anchor in ('c', 'center'):
            dx, dy = x + (w - dw) / 2.0, y + (h - dh) / 2.0
        elif anchor == 'sw':
            dx, dy = x, y
        elif anchor == 'nw':
            dx, dy = x, y + h - dh
        elif anchor == 'ne':
            dx, dy = x + w - dw, y + h - dh
        elif anchor == 'se':
            dx, dy = x + w - dw, y
        else:
            dx, dy = x, y
        if not self.skip_images:
            self.c.drawImage(path, dx * MM, dy * MM, dw * MM, dh * MM,
                             preserveAspectRatio=True, mask=mask, anchor='sw')
        self.boxes.append(('i', (dx, dy, dx + dw, dy + dh), tag))
        return (dx, dy, dx + dw, dy + dh)

    def _split_long_token(self, tok, font, size, width, cs=0):
        """Quebra um token sem espaços em sub-pedaços que caibam em width."""
        if self.width(tok, font, size, cs) <= width:
            return [tok]
        seps = set('/_-.,·+=:')
        out = []
        cur = ''
        for ch in tok:
            trial = cur + ch
            if self.width(trial, font, size, cs) <= width or not cur:
                cur = trial
            else:
                # tenta quebrar no último separador dentro de cur
                cut = -1
                for k in range(len(cur) - 1, 0, -1):
                    if cur[k] in seps:
                        cut = k + 1
                        break
                if cut > 0 and cut < len(cur):
                    out.append(cur[:cut])
                    cur = cur[cut:] + ch
                else:
                    out.append(cur)
                    cur = ch
        if cur:
            out.append(cur)
        return out

    def wrap(self, s, font, size, width, cs=0):
        s = str(s)
        if not s:
            return ['']
        raw_words = s.split(' ')
        words = []
        for w in raw_words:
            if self.width(w, font, size, cs) > width:
                words.extend(self._split_long_token(w, font, size, width, cs))
            else:
                words.append(w)
        lines, cur = [], ''
        for w in words:
            trial = w if not cur else cur + ' ' + w
            if self.width(trial, font, size, cs) <= width or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, s, font='Work', size=7.0, col=None, width=180, leading=None, anchor='l', tag='p'):
        """Parágrafo com quebra. y = baseline da 1.ª linha. Retorna a baseline da última linha."""
        leading = leading if leading is not None else size * 1.42
        lines = self.wrap(s, font, size, width)
        yy = y
        last = y
        for i, ln in enumerate(lines):
            self.text(x, yy, ln, font, size, col, anchor=anchor, tag=f'{tag}:{i}')
            last = yy
            yy -= leading
        return last

    def caption(self, x, y, s, width=180, size=5.9):
        """Legenda em Mono. y = baseline da 1.ª linha. Retorna a baseline da última."""
        return self.para(x, y, s, font='Mono', size=size, col=self.sec, width=width, leading=size * 1.36, tag='cap')

    # ---------- verificação ----------
    def verifica(self):
        prob = []
        for k, (x0, y0, x1, y1), t in self.boxes:
            if t in ('folio', 'rodape', 'nome_lamina'):
                continue
            if x0 < M - 0.1 or x1 > W - M + 0.1 or y0 < M - 0.1 or y1 > H - M + 0.1:
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
