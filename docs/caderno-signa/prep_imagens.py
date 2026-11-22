"""Converte os renders (PNG) em JPEG para o PDF. Cenas noturnas: composição sobre #090C11 + halo radial
(bloom) feito da própria luz do render. Saída em img/jpg/."""
from PIL import Image, ImageFilter
import numpy as np, os, json, sys
IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img')
OUT = os.path.join(IMG, 'jpg'); os.makedirs(OUT, exist_ok=True)
NIGHT = (9, 12, 17)
PAPEL = (238, 234, 226)


def bloom(rgb, raio, ganho, thr=0.45):
    a = np.asarray(rgb).astype(np.float32) / 255
    mx = a.max(axis=2); mn = a.min(axis=2)
    sat = (mx - mn) / np.maximum(mx, 1e-3)
    m = ((mx > thr) & (sat > 0.30)).astype(np.float32)[..., None]
    g = Image.fromarray((a * m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(raio))
    g2 = Image.fromarray((a * m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(raio / 4))
    b = np.asarray(g).astype(np.float32) / 255 * ganho + np.asarray(g2).astype(np.float32) / 255 * ganho * 0.35
    out = 1 - (1 - a) * (1 - np.clip(b, 0, 1))
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))


def noite(nome, raio=70, ganho=1.4):
    im = Image.open(os.path.join(IMG, nome + '.png')).convert('RGBA')
    bg = Image.new('RGBA', im.size, NIGHT + (255,)); bg.alpha_composite(im)
    return bloom(bg.convert('RGB'), raio, ganho)


def salva(im, nome, q=90, maxlado=2200):
    if max(im.size) > maxlado:
        f = maxlado / max(im.size); im = im.resize((int(im.width * f), int(im.height * f)), Image.LANCZOS)
    im.save(os.path.join(OUT, nome + '.jpg'), quality=q, optimize=True, progressive=True)


def prepara_p5():
    """Recortes individuais da lâmina 05 (SALA, MISTO e IA)."""
    NAMES = [
        'p5_sala_livre', 'p5_sala_prestes', 'p5_sala_ocupado', 'p5_misto',
        'p5_ia_livre', 'p5_ia_processando', 'p5_ia_atencao', 'p5_ia_erro', 'p5_ia_limite'
    ]
    ims, boxes = [], []
    for n in NAMES:
        pth = os.path.join(IMG, n + '.png')
        im = Image.open(pth).convert('RGBA')
        a = np.asarray(im)[..., 3]
        ys, xs = np.where(a > 10)
        boxes.append((int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())))
        bg = Image.new('RGBA', im.size, NIGHT + (255,))
        bg.alpha_composite(im)
        if n == 'p5_ia_livre':
            ims.append(bloom(bg.convert('RGB'), 30, 0.35, thr=0.20))
        elif n == 'p5_sala_livre':
            ims.append(bloom(bg.convert('RGB'), 55, 1.7, thr=0.40))
        elif n == 'p5_ia_limite':
            ims.append(bloom(bg.convert('RGB'), 50, 1.25, thr=0.35))
        else:
            ims.append(bloom(bg.convert('RGB'), 55, 1.45, thr=0.45))
    x0 = min(b[0] for b in boxes); y0 = min(b[1] for b in boxes)
    x1 = max(b[2] for b in boxes); y1 = max(b[3] for b in boxes)
    pad_x, pad_bot = 160, 140
    W, H = ims[0].size
    x0, y0, x1, y1 = max(x0 - pad_x, 0), 0, min(x1 + pad_x, W - 1), min(y1 + pad_bot, H - 1)
    for n, im in zip(NAMES, ims):
        c = im.crop((x0, y0, x1 + 1, y1 + 1))
        canvas = Image.new('RGB', (c.width, c.height + 50), NIGHT)
        canvas.paste(c, (0, 50))
        canvas.save(os.path.join(OUT, n + '.jpg'), quality=92, optimize=True, progressive=True)
    print('p5', len(NAMES), canvas.size)


def prepara_resto():
    for n in ['capa', 'p8_alerta']:
        salva(noite(n), n)
    m = noite('p9_modos', raio=40, ganho=1.25)
    salva(m, 'p9_modos')
    a = np.asarray(Image.open(os.path.join(IMG, 'p9_modos.png')))[..., 3]
    rows = a[int(a.shape[0] * 0.55):, :]
    cols = (rows > 10).any(axis=0)
    spans, s0 = [], None
    for x, v in enumerate(cols):
        if v and s0 is None: s0 = x
        if not v and s0 is not None: spans.append((s0, x)); s0 = None
    spans = [s for s in spans if s[1] - s[0] > 20]
    cx = [(s0 + s1) // 2 for s0, s1 in spans]
    print('p9_modos centers', cx)
    # faixa horizontal para a lâmina 9 (proporção 184 × 72 mm)
    rr = np.where((a > 10).any(axis=1))[0]
    s0, s1 = spans[0]
    larg = (a[:, max(s0 - 40, 0):s1 + 40] > 10).sum(axis=1)
    topo = int(np.where(larg > (s1 - s0) * 0.6)[0].min())
    bot = min(int(rr.max()) + 45, a.shape[0]); topo = max(topo - 45, 0)
    # garante largura suficiente para todos os 8 produtos + margem do halo
    need_w = (spans[-1][1] - spans[0][0]) + 180
    hh = max(bot - topo, int(need_w * 72 / 184))
    ww = int(hh * 184 / 72)
    if ww > m.width:
        ww = m.width; hh = int(ww * 72 / 184)
    x0 = max(0, min(m.width - ww, (spans[0][0] + spans[-1][1] - ww) // 2))
    cy_mid = (topo + bot) // 2
    top = max(0, min(m.height - hh, cy_mid - hh // 2))
    m_crop = m.crop((x0, top, x0 + ww, top + hh))
    cx_norm = [(c - x0) / ww for c in cx]
    salva(m_crop, 'p9_modos_crop')
    json.dump(cx_norm, open(os.path.join(OUT, 'p9_modos_crop.json'), 'w'))
    print('crop', ww, hh, 'centers_norm', [round(v, 3) for v in cx_norm])
    for n in ['p8_principal', 'p8_detalhe', 'p9_uso', 'p9_explodida', 'p7_frente', 'p7_verso', 'p7_iso', 'p2_iso']:
        pth = os.path.join(IMG, n + '.png')
        if os.path.exists(pth):
            im = Image.open(pth)
            if im.mode == 'RGBA':
                bg = Image.new('RGBA', im.size, PAPEL + (255,)); bg.alpha_composite(im)
                if n.startswith('p7_'):
                    A = np.asarray(im).astype(np.float32); al = A[..., 3:4] / 255
                    out = np.asarray(bg).astype(np.float32)[..., :3]
                    pap = np.array(PAPEL, np.float32)
                    som = np.minimum(out, pap)
                    w = np.clip((0.92 - al) / 0.3, 0, 1)
                    out = out * (1 - w) + som * w
                    bg = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
                im = bg
            salva(im.convert('RGB'), n)
    print('ok')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'p5':
        prepara_p5()
    else:
        prepara_p5()
        prepara_resto()
