"""Mini-biblioteca de desenho tecnico: projecoes (build123d HLR) -> PDF/PNG (matplotlib) + DXF (ezdxf).
Convencao: 1o diedro (ABNT NBR 10067 / ISO 5456-2), unidades mm."""
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Circle as MCirc, Rectangle
import ezdxf
from build123d import *
from params import REV, DATE

PT = 72 / 25.4
LW = dict(vis=0.5, hid=0.25, cen=0.18, dim=0.18, thin=0.25, frame=0.7, sec=0.35)
LS = dict(vis='-', hid=(0, (3, 1.5)), cen=(0, (8, 2, 1.5, 2)), dim='-', thin='-', frame='-', sec='-')
LAYER = dict(vis='VISIVEL', hid='OCULTA', cen='CENTRO', dim='COTA', thin='FINA', frame='MOLDURA', sec='CORTE')
LT = dict(vis='CONTINUOUS', hid='DASHED', cen='CENTER', dim='CONTINUOUS', thin='CONTINUOUS', frame='CONTINUOUS', sec='CONTINUOUS')


def _vec(t):
    return Vector(*t)


class View:
    def __init__(self, sheet, shape, direction, up, origin, scale, hidden=True, section=None, label=None, center=None):
        """direction: vetor do observador para a peca (ex.: (0,-1,0) = observador em +Y).
        origin: ponto da folha (mm) onde cai o ponto 'center' do modelo."""
        self.sheet, self.scale = sheet, scale
        self.fwd = _vec(direction).normalized()
        self.up0 = _vec(up)
        self.right = self.fwd.cross(self.up0).normalized()
        self.up = self.right.cross(self.fwd).normalized()
        self.center = _vec(center) if center else Vector(0, 0, 0)
        self.origin = origin
        eye = tuple(-self.fwd * 1000)
        vis, hid = shape.project_to_viewport(eye, tuple(self.up0), (0, 0, 0))
        cu, cv = self.uv0(self.center)
        self.cu, self.cv = cu, cv
        for e in vis:
            sheet.poly([self.map2(p) for p in _disc(e)], 'vis')
        if hidden:
            for e in hid:
                sheet.poly([self.map2(p) for p in _disc(e)], 'hid')
        if section is not None:
            # faces de corte = faces do solido cortado que estao no plano de corte
            pl_pt, pl_n = section
            for f in shape.faces():
                c = f.center()
                n = f.normal_at(c)
                if abs(abs(n.dot(_vec(pl_n))) - 1) < 1e-6 and abs((c - _vec(pl_pt)).dot(_vec(pl_n))) < 1e-4:
                    outer = [self.map(p) for p in _wire_pts(f.outer_wire())]
                    inners = [[self.map(p) for p in _wire_pts(w)] for w in f.inner_wires()]
                    sheet.hatch(outer, inners)
        if label:
            xs = [self.origin[0]]
            sheet.text(origin[0], label[1], label[0], 3.5, ha='center', weight='bold')

    def uv0(self, p):
        p = _vec(tuple(p))
        return p.dot(self.right), p.dot(self.up)

    def map(self, p):
        u, v = self.uv0(p)
        return (self.origin[0] + (u - self.cu) * self.scale, self.origin[1] + (v - self.cv) * self.scale)

    def map2(self, p2):
        # p2 = ponto ja projetado pelo build123d (x=u, y=v)
        return (self.origin[0] + (p2.X - self.cu) * self.scale, self.origin[1] + (p2.Y - self.cv) * self.scale)


def _disc(e):
    try:
        if e.geom_type == GeomType.LINE:
            return [e @ 0, e @ 1]
    except Exception:
        pass
    n = max(6, min(120, int(e.length / 0.25)))
    return [e @ (i / n) for i in range(n + 1)]


def _wire_pts(w):
    pts = []
    for e in w.order_edges() if hasattr(w, 'order_edges') else w.edges():
        d = _disc(e)
        pts += d
    return pts


class Sheet:
    def __init__(self, fmt, number, title, material, finish, scale_txt, mass_g=None, sheet='1/1', tol='ISO 2768-mK'):
        self.W, self.H = dict(A4=(297, 210), A3=(420, 297))[fmt]
        self.fig = plt.figure(figsize=(self.W / 25.4, self.H / 25.4))
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, self.W); self.ax.set_ylim(0, self.H); self.ax.axis('off'); self.ax.set_aspect('equal')
        self.doc = ezdxf.new('R2010', setup=True)
        self.doc.units = ezdxf.units.MM
        for k, name in LAYER.items():
            if name not in self.doc.layers:
                self.doc.layers.add(name, linetype=LT[k])
        self.msp = self.doc.modelspace()
        self.number, self.title = number, title
        self._frame(material, finish, scale_txt, mass_g, sheet, tol)

    # ---------- primitivas ----------
    def poly(self, pts, kind='vis', closed=False):
        if len(pts) < 2:
            return
        xs, ys = zip(*pts)
        self.ax.plot(xs, ys, color='k', lw=LW[kind] * PT, ls=LS[kind], solid_capstyle='round')
        self.msp.add_lwpolyline([(x, y) for x, y in pts], close=closed, dxfattribs=dict(layer=LAYER[kind]))

    def line(self, a, b, kind='vis'):
        self.poly([a, b], kind)

    def text(self, x, y, s, h=2.5, ha='left', va='bottom', rot=0, weight='normal', dxf=True):
        self.ax.text(x, y, s, fontsize=h * PT * 1.0 / 0.72, ha=ha, va=va, rotation=rot, family='DejaVu Sans', weight=weight)
        if dxf:
            al = {('left', 'bottom'): 'BOTTOM_LEFT', ('center', 'bottom'): 'BOTTOM_CENTER', ('right', 'bottom'): 'BOTTOM_RIGHT',
                  ('left', 'center'): 'MIDDLE_LEFT', ('center', 'center'): 'MIDDLE_CENTER', ('right', 'center'): 'MIDDLE_RIGHT',
                  ('left', 'top'): 'TOP_LEFT', ('center', 'top'): 'TOP_CENTER', ('right', 'top'): 'TOP_RIGHT'}[(ha, va)]
            for i, ln in enumerate(s.split('\n')):
                t = self.msp.add_text(ln, height=h, rotation=rot, dxfattribs=dict(layer='FINA'))
                t.set_placement((x, y - i * h * 1.6), align=getattr(ezdxf.enums.TextEntityAlignment, al))

    def hatch(self, outer, inners=()):
        from matplotlib.path import Path
        verts, codes = [], []
        for ring in [outer] + list(inners):
            verts += ring + [ring[0]]
            codes += [Path.MOVETO] + [Path.LINETO] * (len(ring) - 1) + [Path.CLOSEPOLY]
        from matplotlib.patches import PathPatch
        self.ax.add_patch(PathPatch(Path(verts, codes), facecolor='none', edgecolor='k', hatch='////', lw=0))
        h = self.msp.add_hatch(color=7, dxfattribs=dict(layer='CORTE'))
        h.set_pattern_fill('ANSI31', scale=0.5)
        h.paths.add_polyline_path(outer, is_closed=True, flags=ezdxf.const.BOUNDARY_PATH_EXTERNAL)
        for r in inners:
            h.paths.add_polyline_path(r, is_closed=True)

    def arrow(self, tip, tail, size=2.5):
        dx, dy = tip[0] - tail[0], tip[1] - tail[1]
        L = math.hypot(dx, dy) or 1
        ux, uy = dx / L, dy / L
        w = size * 0.3
        p1 = (tip[0] - ux * size + uy * w, tip[1] - uy * size - ux * w)
        p2 = (tip[0] - ux * size - uy * w, tip[1] - uy * size + ux * w)
        self.ax.add_patch(MPoly([tip, p1, p2], closed=True, color='k', lw=0))
        s = self.msp.add_solid([tip, p1, p2], dxfattribs=dict(layer='COTA'))

    # ---------- cotas ----------
    def dim(self, a, b, off, text, orient='h', ts=2.5, side=None):
        """a,b pontos na folha; off = deslocamento da linha de cota (mm folha, com sinal)."""
        if orient == 'h':
            y = (a[1] if off > 0 and a[1] >= b[1] else b[1] if off > 0 else min(a[1], b[1])) if False else None
            y = (max(a[1], b[1]) if off > 0 else min(a[1], b[1])) + off
            pa, pb = (a[0], y), (b[0], y)
            self.line((a[0], a[1] + math.copysign(0.8, off)), (a[0], y + math.copysign(1.5, off)), 'dim')
            self.line((b[0], b[1] + math.copysign(0.8, off)), (b[0], y + math.copysign(1.5, off)), 'dim')
        else:
            x = (max(a[0], b[0]) if off > 0 else min(a[0], b[0])) + off
            pa, pb = (x, a[1]), (x, b[1])
            self.line((a[0] + math.copysign(0.8, off), a[1]), (x + math.copysign(1.5, off), a[1]), 'dim')
            self.line((b[0] + math.copysign(0.8, off), b[1]), (x + math.copysign(1.5, off), b[1]), 'dim')
        L = math.dist(pa, pb)
        if L > 8:
            self.line(pa, pb, 'dim'); self.arrow(pa, pb); self.arrow(pb, pa)
            mid = ((pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2)
        else:  # setas por fora
            d = ((pb[0] - pa[0]) / (L or 1), (pb[1] - pa[1]) / (L or 1))
            ea = (pa[0] - d[0] * 5, pa[1] - d[1] * 5); eb = (pb[0] + d[0] * 5, pb[1] + d[1] * 5)
            self.line(ea, eb, 'dim'); self.arrow(pa, ea); self.arrow(pb, eb)
            mid = (eb[0] + d[0] * 1, eb[1] + d[1] * 1) if side == 'out' else ((pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2)
        if orient == 'h':
            if L <= 8 and side == 'out':
                self.text(mid[0] + 0.5, mid[1] + 0.6, text, ts, ha='left', va='bottom')
            else:
                self.text(mid[0], mid[1] + 0.6, text, ts, ha='center', va='bottom')
        else:
            if L <= 8 and side == 'out':
                mx = pa[0]; my = (pa[1] + pb[1]) / 2
                if off < 0:
                    self.text(mx - 1.2, my, text, ts, ha='right', va='center')
                else:
                    self.text(mx + 1.2, my, text, ts, ha='left', va='center')
            else:
                self.text(mid[0] - 0.6, mid[1], text, ts, ha='center', va='bottom', rot=90)

    def leader(self, tip, knee, text, ts=2.3, ha=None):
        self.line(tip, knee, 'dim'); self.arrow(tip, knee, 2.0)
        ha = ha or ('left' if knee[0] >= tip[0] else 'right')
        end = (knee[0] + (6 if ha == 'left' else -6), knee[1])
        self.line(knee, end, 'dim')
        self.text(end[0] + (0.8 if ha == 'left' else -0.8), end[1], text, ts, ha=ha, va='center')

    def balloon(self, tip, center, n, r=4.0):
        ang = math.atan2(tip[1] - center[1], tip[0] - center[0])
        start = (center[0] + r * math.cos(ang), center[1] + r * math.sin(ang))
        self.line(start, tip, 'dim')
        self.ax.add_patch(MCirc(tip, 0.6, color='k'))
        self.ax.add_patch(MCirc(center, r, fill=False, lw=0.35 * PT))
        self.msp.add_circle(center, r, dxfattribs=dict(layer='COTA'))
        self.text(center[0], center[1], str(n), 3.5, ha='center', va='center', weight='bold')

    def centerline(self, a, b):
        self.line(a, b, 'cen')

    def rect(self, x, y, w, h, kind='thin'):
        self.poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)], kind)

    def table(self, x, y_top, cols, rows, rh=5.0, ts=2.2, header=True):
        """cols: [(titulo, largura)], rows: listas de strings. Desenha de cima para baixo."""
        W = sum(w for _, w in cols)
        allrows = ([[c for c, _ in cols]] if header else []) + rows
        for i, r in enumerate(allrows):
            yy = y_top - (i + 1) * rh
            self.rect(x, yy, W, rh, 'thin')
            xx = x
            for j, (c, w) in enumerate(cols):
                if j:
                    self.line((xx, yy), (xx, yy + rh), 'thin')
                self.text(xx + 1.0, yy + rh / 2, str(r[j]), ts, va='center', weight='bold' if header and i == 0 else 'normal')
                xx += w
        return y_top - len(allrows) * rh

    def notes(self, x, y_top, title, lines, ts=2.0, lh=3.4, width=170):
        import textwrap
        self.text(x, y_top, title, 2.6, va='top', weight='bold')
        n = int(width / (0.74 * ts))
        out = []
        for l in lines:
            w = textwrap.wrap(l, n, subsequent_indent='   ') or ['']
            out += w
        for i, l in enumerate(out):
            self.text(x, y_top - 4.5 - i * lh, l, ts, va='top')
        return y_top - 4.5 - len(out) * lh

    def cut_line(self, a, b, letter, arrow_dir):
        """Indicacao do plano de corte: a,b extremos na folha; arrow_dir = vetor (folha) do sentido de observacao."""
        self.line(a, b, 'cen')
        for p, q in ((a, b), (b, a)):
            L = math.dist(p, q); d = ((q[0]-p[0])/L, (q[1]-p[1])/L)
            self.poly([p, (p[0]+d[0]*4, p[1]+d[1]*4)], 'frame')
            tip = (p[0] + arrow_dir[0]*6, p[1] + arrow_dir[1]*6)
            self.line(p, tip, 'vis'); self.arrow(tip, p, 2.5)
            self.text(tip[0] + arrow_dir[0]*1.5 - d[0]*2.5, tip[1] + arrow_dir[1]*1.5 - d[1]*2.5, letter, 3.2, ha='center', va='center', weight='bold')

    # ---------- moldura / legenda ----------
    def _frame(self, material, finish, scale_txt, mass_g, sheet, tol):
        W, H = self.W, self.H
        self.rect(5, 5, W - 10, H - 10, 'frame') if False else None
        self.rect(20, 10, W - 30, H - 20, 'frame')   # margem de arquivamento 20 mm a esquerda
        tw, th = 180, 42
        x0, y0 = W - 10 - tw, 10
        self.tb = (x0, y0, tw, th)
        r = [10, 8, 8, 8, 8]
        ys = [y0]
        for h in r[::-1]:
            ys.append(ys[-1] + h)
        self.rect(x0, y0, tw, th, 'frame')
        for yy in ys[1:-1]:
            self.line((x0, yy), (x0 + tw, yy), 'thin')
        # linha 1 (topo, 10 mm): projeto + titulo
        top = y0 + th
        self.line((x0 + 120, top - 10), (x0 + 120, top), 'thin')
        self.text(x0 + 1.5, top - 1.2, 'PROJETO', 1.6, va='top')
        tt = 'SIGNA — ' + self.title
        self.text(x0 + 1.5, top - 5.6, tt, min(3.0, 115 / (len(tt) * 0.78)), va='center', weight='bold')
        self.text(x0 + 121.5, top - 1.2, 'DESENHO Nº', 1.6, va='top')
        self.text(x0 + 121.5, top - 6, self.number, 3.2, va='center', weight='bold')
        # linha 2: material / acabamento
        def cell(xa, xb, yrow, lab, val, ts=2.2):
            self.line((xa, yrow), (xa, yrow + 8), 'thin')
            self.text(xa + 1.2, yrow + 7.2, lab, 1.6, va='top')
            avail = xb - xa - 2.4
            if len(val) * 0.74 * ts > avail:
                ts2 = avail / (len(val) * 0.74)
                if ts2 >= 1.6:
                    ts = ts2
                else:  # quebra em 2 linhas
                    ts = max(1.5, min(ts, avail / (((len(val) + 1) // 2 + 2) * 0.74)))
                    cut = val.rfind(' ', 0, len(val) // 2 + 6)
                    val = val[:cut] + '\n' + val[cut + 1:]
                    self.text(xa + 1.2, yrow + 4.4, val, ts, va='center')
                    return
            self.text(xa + 1.2, yrow + 2.8, val, ts, va='center')
        y2 = top - 18
        cell(x0, x0 + 70, y2, 'MATERIAL', material, 2.0)
        cell(x0 + 70, x0 + tw, y2, 'ACABAMENTO', finish, 2.0)
        y3 = top - 26
        cell(x0, x0 + 45, y3, 'TOLERÂNCIA GERAL', tol)
        cell(x0 + 45, x0 + 75, y3, 'MASSA (estim.)', f'{mass_g:.1f} g' if mass_g else '—')
        cell(x0 + 75, x0 + 105, y3, 'ESCALA', scale_txt)
        cell(x0 + 105, x0 + 125, y3, 'UNIDADE', 'mm')
        cell(x0 + 125, x0 + 145, y3, 'REV.', REV)
        cell(x0 + 145, x0 + tw, y3, 'FOLHA', sheet)
        y4 = top - 34
        cell(x0, x0 + 45, y4, 'DATA', DATE)
        cell(x0 + 45, x0 + 105, y4, 'DESENHO', 'Grok Bot p/ Lucas Tavares')
        cell(x0 + 105, x0 + tw, y4, 'PROJEÇÃO', '1º diedro (ABNT/ISO)')
        y5 = y0
        cell(x0, x0 + tw, y5, 'OBSERVAÇÃO', 'Cotas em mm. Não medir no desenho. Arestas vivas quebrar 0,1–0,3 mm salvo indicação.', 2.0)
        # simbolo 1o diedro: cone (ponta menor a esquerda) + circulos a direita
        sx, sy, h = x0 + 160, y4 + 4.0, 5.0
        L = 1.3 * h
        self.poly([(sx - L, sy - 0.3 * h), (sx, sy - h / 2), (sx, sy + h / 2), (sx - L, sy + 0.3 * h), (sx - L, sy - 0.3 * h)], 'vis')
        cx = sx + 0.5 * h + h / 2
        for rr in (h / 2, 0.3 * h):
            self.ax.add_patch(MCirc((cx, sy), rr, fill=False, lw=0.35 * PT))
            self.msp.add_circle((cx, sy), rr, dxfattribs=dict(layer='VISIVEL'))
        self.line((sx - L - 1, sy), (cx + h / 2 + 1, sy), 'cen')

    def save(self, base):
        self.fig.savefig(base + '.pdf')
        self.fig.savefig(base + '.png', dpi=130)
        self.doc.saveas(base + '.dxf')
        plt.close(self.fig)
