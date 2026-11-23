"""Helpers de layout para o caderno de engenharia (tabelas, caixas, setas, formas de onda, paginação)."""
from lib_metrologia import *
from reportlab.lib.colors import HexColor
import math, os

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = lambda *p: os.path.join(HERE, 'img', *p)
JPG = lambda n: os.path.join(HERE, 'img', 'jpg', n + '.jpg')

RODAPE = "SIGNA · CADERNO DE ENGENHARIA · REV. 0"
DOC_ID = "SIGNA-ENG-001"
DOC_REV = "0"
DOC_DATA = "22 nov. 2026"


def _row_height(L, r, larg, fonts, aligns, size, alt, wrap_cols):
    nlines = 1
    wrapped = []
    for j, (v, w, a) in enumerate(zip(r, larg, aligns)):
        f = (fonts[j] if fonts else ('Mono' if a == 'r' else 'Work'))
        txt = str(v)
        need_wrap = (j in wrap_cols) or (L.width(txt, f, size) > w - 2.0)
        if need_wrap:
            pad_x = (3.0 if (a == 'l' and j > 0 and aligns[j - 1] == 'r') else 0.0) + (4.0 if (a == 'r' and j + 1 < len(larg) and aligns[j + 1] == 'l') else 1.0)
            ls = L.wrap(txt, f, size, max(w - pad_x - 2.0, 8.0))
            wrapped.append(ls)
            nlines = max(nlines, len(ls))
        else:
            wrapped.append([txt])
    min_alt = max(alt, size * 1.72)
    if nlines == 1:
        row_h = min_alt
    else:
        lead = size * 1.32
        row_h = 2.6 + 0.96 * size + (nlines - 1) * lead + 2.4
    return row_h, nlines, wrapped


def _head_height(L, cols, larg, cab_size):
    wrapped_h = []
    nlines = 1
    for c, w in zip(cols, larg):
        cu = c.upper()
        if L.width(cu, 'JuraM', cab_size, cs=0.25) > w - 1.8:
            ls = L.wrap(cu, 'JuraM', cab_size, max(w - 1.8, 8.0), cs=0.2)
            wrapped_h.append(ls)
            nlines = max(nlines, len(ls))
        else:
            wrapped_h.append([cu])
    if nlines == 1:
        h = max(10.5, cab_size * 1.75)
    else:
        h = 2.2 + 0.96 * cab_size + (nlines - 1) * (cab_size * 1.28) + 2.2
    return h, nlines, wrapped_h


def tabela(L, x, y, cols, rows, larg, alt=11.5, head=True, size=6.45, bold_rows=(),
           aligns=None, cab_size=5.85, linhas=True, fonts=None, max_y=38.0, wrap_cols=None):
    """cols: cabeçalhos; rows: listas de str; larg: larguras mm. y = topo.
    Quebra automaticamente células e cabeçalhos que ultrapassem a largura da coluna.
    Retorna (y_final, restantes) — restantes não cabem acima de max_y."""
    aligns = aligns or ['l'] * len(cols)
    wrap_cols = wrap_cols or set()
    if head:
        head_h, hlines, wrapped_h = _head_height(L, cols, larg, cab_size)
        cx = x
        for idx_c, (hls, w, a) in enumerate(zip(wrapped_h, larg, aligns)):
            lpad = 3.0 if (a == 'l' and idx_c > 0 and aligns[idx_c - 1] == 'r') else 0.0
            rpad = 4.0 if (a == 'r' and idx_c + 1 < len(larg) and aligns[idx_c + 1] == 'l') else 1.0
            tx = cx + (w - rpad if a == 'r' else lpad if a == 'l' else w / 2.0)
            if len(hls) == 1:
                by = y - head_h / 2.0 - 0.26 * cab_size
                L.text(tx, by, hls[0], 'JuraM', cab_size, L.sec, cs=0.25, anchor=a)
            else:
                yy = y - 2.2 - 0.74 * cab_size
                for hl in hls:
                    L.text(tx, yy, hl, 'JuraM', cab_size, L.sec, cs=0.2, anchor=a)
                    yy -= cab_size * 1.28
            cx += w
        y -= head_h
        L.line(x, y, x + sum(larg), y, L.ink, 0.25)
    leftover = []
    started = False
    for i, r in enumerate(rows):
        row_h, nlines, wrapped = _row_height(L, r, larg, fonts, aligns, size, alt, wrap_cols)
        if started and y - row_h < max_y:
            leftover = rows[i:]
            break
        if y - row_h < max_y and not started and i > 0:
            leftover = rows[i:]
            break
        started = True
        cx = x
        bold = i in bold_rows
        lead = size * 1.32
        for j, (v, w, a) in enumerate(zip(r, larg, aligns)):
            f = (fonts[j] if fonts else ('Mono' if a == 'r' else 'Work'))
            if bold:
                f = {'Mono': 'MonoM', 'Work': 'WorkM'}.get(f, f)
            lines = wrapped[j]
            idx_c = j
            lpad = 3.0 if (a == 'l' and idx_c > 0 and aligns[idx_c - 1] == 'r') else 0.0
            rpad = 4.0 if (a == 'r' and idx_c + 1 < len(larg) and aligns[idx_c + 1] == 'l') else 1.0
            tx = cx + (w - rpad if a == 'r' else lpad if a == 'l' else w / 2.0)
            if nlines == 1:
                by = y - row_h / 2.0 - 0.26 * size
                L.text(tx, by, lines[0], f, size, L.ink, anchor=a)
            else:
                yy = y - 2.6 - 0.74 * size
                for ln in lines:
                    L.text(tx, yy, ln, f, size, L.ink, anchor=a)
                    yy -= lead
            cx += w
        y -= row_h
        if linhas:
            L.line(x, y, x + sum(larg), y, P['regua'] if not L.noite else P['borda'], 0.30 if bold else 0.12)
    return y, leftover


def caixa(L, x, y, w, h, titulo=None, stroke=None, fill=None, lw=0.18):
    """Caixa com título opcional no topo interno. y = base."""
    L.rect(x, y, w, h, stroke=stroke or L.ink, fill=fill, lw=lw)
    if titulo:
        L.rotulo(x + 3.0, y + h - 8.5, titulo, size=6.3)
    return y + h - (14.0 if titulo else 3.0)


def seta_linha(L, x1, y1, x2, y2, col=None, w=0.28, seta=True):
    col = col or L.ink
    L.line(x1, y1, x2, y2, col, w)
    if seta:
        ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
        L.seta(x2, y2, ang, col, L=2.8, a=18)


def bloco(L, x, y, w, h, linhas, title=None, fill=None, size=6.15):
    """Bloco de diagrama (x,y = canto inferior esquerdo). linhas: lista de str, centradas."""
    L.rect(x, y, w, h, stroke=L.ink, fill=fill or None, lw=0.32, r=1.2)
    t_size = 5.7
    # embrulha linhas que não caibam em w - 6
    wrapped = []
    for ln in linhas:
        wrapped.extend(L.wrap(ln, 'Work', size, max(w - 6.0, 12.0)))
    lead = size * 1.35
    if title:
        L.text(x + w / 2.0, y + h - 8.5, title, 'JuraM', t_size, L.sec, cs=0.35, anchor='c')
        avail_h = h - 13.0
        block_h = (len(wrapped) - 1) * lead
        top = y + avail_h / 2.0 + block_h / 2.0 - 0.26 * size
    else:
        block_h = (len(wrapped) - 1) * lead
        top = y + h / 2.0 + block_h / 2.0 - 0.26 * size
    yy = top
    for ln in wrapped:
        L.text(x + w / 2.0, yy, ln, 'Work', size, L.ink, anchor='c')
        yy -= lead
    L.area(x, y, x + w, y + h, 'dentro bloco')
    return (x, y, x + w, y + h)


def onda(L, x, y, w, h, tipo, col, periodo_s=None, piso=0.0, expoente=1.4, pulso_s=None, gap_s=None, pico=1.0, duty=0.5, nivel=1.0):
    """Desenha a forma de onda do estado na caixa (x,y,w,h). tipo: const, breath, square, flash, double_pulse."""
    L.rect(x, y, w, h, stroke=P['regua'], lw=0.1)
    L.line(x, y, x + w, y, P['clara'], 0.08)
    samples = 120
    pts = []
    T = periodo_s or 1.0
    for i in range(samples + 1):
        t = (i / samples) * (T if tipo != 'const' else 1.0)
        if tipo != 'const':
            t = (i / samples) * (2 * T)
        if tipo == 'const':
            v = nivel
        elif tipo == 'breath':
            phase = (t / T) * 2 * math.pi
            v = piso + (1 - piso) * (((1 - math.cos(phase)) / 2) ** expoente)
        elif tipo == 'square':
            frac = (t % T) / T
            v = 1.0 if frac < duty else piso
        elif tipo == 'flash':
            tau = pulso_s or 0.13
            frac = (t % T)
            v = 1.0 if frac < tau else piso
        elif tipo == 'double_pulse':
            tau = pulso_s or 0.25
            gap = gap_s or 0.25
            frac = (t % T)
            if frac < tau or (gap + tau <= frac < gap + 2 * tau):
                v = pico
            else:
                v = piso
        else:
            v = nivel
        px = x + (i / samples) * w
        py = y + 0.4 + v * (h - 0.8)
        pts.append((px, py))
    if len(pts) >= 2:
        L.poly(pts, stroke=col, lw=0.35, close=False)
    return pts


def chip(c):
    """Swatch de cor — helper só retorna o hex normalizado."""
    return c if c.startswith('#') else ('#' + c)


class Flow:
    """Paginador automático para lâminas que podem continuar em páginas '(cont.)'."""

    def __init__(self, canvas, start_n, total, sec, toc_title, short=None,
                 noite=False, skip_images=False, emit_pages=True):
        self.c = canvas
        self.n = start_n
        self.total = total
        self.sec = sec
        self.toc_title = toc_title
        self.base_short = (short or toc_title).upper()
        self.noite = noite
        self.skip_images = skip_images
        self.emit_pages = emit_pages

        self.base_title = toc_title.upper()
        self.sub = 'METROLOGIA LUMINOSA'
        self.gloss_txt = None
        self.base_min_y = M + 12.0
        self.min_y = self.base_min_y
        self.x = M
        self.w = W - 2 * M
        self.y = 242.0
        self.L = None
        self.page_idx = 0
        self.pages = []      # [{'sec', 'title', 'short', 'noite'}]
        self.problemas = []  # [(page_num, title, probs)]

    def _open_page(self, is_cont=False):
        t = f'{self.base_title} (cont.)' if is_cont else self.base_title
        sh = f'{self.base_short} (CONT.)' if is_cont else self.base_short
        toc_t = f'{self.toc_title} (cont.)' if is_cont else self.toc_title
        self.L = Lamina(self.c, self.n, self.total, sh, RODAPE,
                        noite=self.noite, skip_images=self.skip_images)
        self.y = self.L.titulo(t, self.sub)
        self.x = M
        self.w = W - 2 * M
        self.min_y = self.base_min_y
        self.page_idx += 1
        self.pages.append({
            'sec': self.sec,
            'title': toc_t,
            'short': sh,
            'noite': self.noite,
            'page': self.n,
        })

    def _close_page(self):
        if self.L is None:
            return
        if self.gloss_txt:
            self.L.glossario(self.gloss_txt)
        probs = self.L.verifica()
        if probs:
            self.problemas.append((self.n, self.pages[-1]['title'], probs))
        if self.emit_pages:
            self.c.showPage()
        self.n += 1

    def titulo(self, title, sub='METROLOGIA LUMINOSA'):
        self.base_title = title
        self.sub = sub
        self._open_page(is_cont=False)
        return self.y

    def glossario(self, txt):
        self.gloss_txt = txt
        if self.L is not None:
            self.base_min_y = self.L.glossario_min_y(txt)
            if self.min_y < self.base_min_y:
                self.min_y = self.base_min_y

    def set_box(self, x, w, y=None, min_y=None):
        self.x = x
        self.w = w
        if y is not None:
            self.y = y
        if min_y is not None:
            self.min_y = max(min_y, self.base_min_y)

    def next_page(self):
        self._close_page()
        self._open_page(is_cont=True)
        return self.y

    def gap(self, mm=8.0):
        self.y -= mm

    def need(self, h):
        if self.y - h < self.min_y:
            self.next_page()

    def rotulo(self, s, size=7.0, gap_before=0.0, min_following=30.0):
        if gap_before:
            self.y -= gap_before
        if self.y - (size * 1.45 + min_following) < self.min_y:
            self.next_page()
        self.L.rotulo(self.x, self.y, s, size=size)
        self.y -= (size * 1.35 + 4.5)

    def para(self, s, font='Work', size=7.0, leading=None, width=None, gap=12.5, col=None):
        w = width if width is not None else self.w
        lead = leading if leading is not None else size * 1.42
        lines = self.L.wrap(s, font, size, w)
        if not lines:
            return
        idx = 0
        # se não cabem pelo menos 2 linhas (ou todas se <=2), começa na próxima
        min_lines = len(lines) if len(lines) <= 7 else 2
        if self.y - ((min_lines - 1) * lead + 0.25 * size) < self.min_y:
            self.next_page()
            w = width if width is not None else self.w
            lines = self.L.wrap(s, font, size, w)
        while idx < len(lines):
            if self.y - 0.25 * size < self.min_y:
                self.next_page()
                w = width if width is not None else self.w
                rem_text = ' '.join(lines[idx:])
                lines = self.L.wrap(rem_text, font, size, w)
                idx = 0
                continue
            self.L.text(self.x, self.y, lines[idx], font, size, col or self.L.ink, tag=f'p:{self.n}:{idx}')
            self.y -= lead
            idx += 1
        self.y += (lead - gap)

    def code_lines(self, lines, font='Mono', size=6.4, step=9.5, indent=4.0, gap=6.0):
        for ln in lines:
            wrapped = self.L.wrap(ln if ln else ' ', font, size, max(self.w - indent, 20.0))
            for wln in wrapped:
                if self.y - 0.25 * size < self.min_y:
                    self.next_page()
                self.L.text(self.x + indent, self.y, wln, font, size, self.L.ink)
                self.y -= step
        self.y -= gap

    def kv_list(self, items, key_w=78.0, k_size=6.5, v_size=6.5, gap=4.0, line_div=True, v_font='Mono'):
        lead = v_size * 1.38
        for k, v in items:
            v_w = max(self.w - key_w, 40.0)
            v_lines = self.L.wrap(str(v), v_font, v_size, v_w)
            h_need = max(1, len(v_lines)) * lead + (3.0 if line_div else 1.5)
            if self.y - h_need < self.min_y:
                self.next_page()
                v_w = max(self.w - key_w, 40.0)
                v_lines = self.L.wrap(str(v), v_font, v_size, v_w)
            self.L.text(self.x, self.y, k, 'Work', k_size, P['sec'] if not self.noite else self.L.sec)
            yy = self.y
            for vl in v_lines:
                self.L.text(self.x + key_w, yy, vl, v_font, v_size, self.L.ink)
                yy -= lead
            if line_div:
                div_y = yy + lead - 3.2
                self.L.line(self.x, div_y, self.x + self.w, div_y, P['regua'] if not self.noite else P['borda'], 0.12)
                self.y = div_y - (gap + 3.5)
            else:
                self.y = yy - gap * 0.5

    def tabela(self, cols, rows, larg, alt=11.5, head=True, size=6.45, bold_rows=(),
               aligns=None, cab_size=5.85, linhas=True, fonts=None, wrap_cols=None, gap=9.0,
               cont_larg=None):
        aligns = aligns or ['l'] * len(cols)
        wrap_cols = wrap_cols or set()
        rem = list(rows)
        rem_bold = tuple(bold_rows)
        cur_larg = larg
        while rem:
            head_h = _head_height(self.L, cols, cur_larg, cab_size)[0] if head else 0.0
            first_h = _row_height(self.L, rem[0], cur_larg, fonts, aligns, size, alt, wrap_cols)[0]
            if self.y - head_h - first_h < self.min_y and self.y < self.L.top_y - 4.0:
                self.next_page()
                if cont_larg is not None:
                    cur_larg = cont_larg
            y_end, leftover = tabela(
                self.L, self.x, self.y, cols, rem, cur_larg,
                alt=alt, head=head, size=size, bold_rows=rem_bold,
                aligns=aligns, cab_size=cab_size, linhas=linhas,
                fonts=fonts, max_y=self.min_y, wrap_cols=wrap_cols
            )
            if not leftover:
                self.y = y_end - gap
                break
            consumed = len(rem) - len(leftover)
            rem_bold = tuple(idx - consumed for idx in rem_bold if idx >= consumed)
            rem = leftover
            self.next_page()
            if cont_larg is not None:
                cur_larg = cont_larg

    def finish(self):
        self._close_page()
        return self.pages, self.problemas
