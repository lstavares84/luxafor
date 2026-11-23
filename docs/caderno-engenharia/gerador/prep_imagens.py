"""Prepara figuras do caderno de engenharia (JPEG sobre papel/noite, esquema, desenhos)."""
from PIL import Image, ImageFilter, ImageOps
import numpy as np, os, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
JPG = os.path.join(IMG, 'jpg')
os.makedirs(JPG, exist_ok=True)
NIGHT = (9, 12, 17)
PAPEL = (238, 234, 226)


def _pasta(env, relativos, reserva):
    """Caminho da fonte: SIGNA_* se definida; senão a pasta deste repositório; senão /workspace."""
    v = os.environ.get(env, '').strip()
    if v:
        return v
    raiz = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
    for rel in relativos:
        p = os.path.join(raiz, rel)
        if os.path.isdir(p):
            return p
    return reserva


REV_D = _pasta('SIGNA_REVD', ('hardware/revD',), '/workspace/luxpcb-revD')
MECH = _pasta('SIGNA_MECH', ('mecanica',), '/workspace/signa-3d')
CONC = _pasta('SIGNA_CONC', ('docs/caderno-signa', '.old/docs/conceito'), '/workspace/caderno-revC')


def bloom(rgb, raio, ganho, thr=0.45):
    a = np.asarray(rgb).astype(np.float32) / 255
    mx = a.max(axis=2)
    mn = a.min(axis=2)
    sat = (mx - mn) / np.maximum(mx, 1e-3)
    m = ((mx > thr) & (sat > 0.30)).astype(np.float32)[..., None]
    g = Image.fromarray((a * m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(raio))
    g2 = Image.fromarray((a * m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(max(raio / 4, 1)))
    b = np.asarray(g).astype(np.float32) / 255 * ganho + np.asarray(g2).astype(np.float32) / 255 * ganho * 0.35
    out = 1 - (1 - a) * (1 - np.clip(b, 0, 1))
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))


def salva(im, nome, q=90, maxlado=2600):
    if im.mode != 'RGB':
        im = im.convert('RGB')
    if max(im.size) > maxlado:
        f = maxlado / max(im.size)
        im = im.resize((int(im.width * f), int(im.height * f)), Image.LANCZOS)
    path = os.path.join(JPG, nome + '.jpg')
    im.save(path, quality=q, optimize=True, progressive=True)
    print(nome, im.size)
    return path


def sobre(path, fundo, crop_alpha=True, pad=0):
    im = Image.open(path).convert('RGBA')
    if crop_alpha:
        a = np.asarray(im)[..., 3]
        ys, xs = np.where(a > 8)
        if len(xs):
            x0, y0, x1, y1 = xs.min(), ys.min(), xs.max(), ys.max()
            x0, y0 = max(x0 - pad, 0), max(y0 - pad, 0)
            x1, y1 = min(x1 + pad, im.width - 1), min(y1 + pad, im.height - 1)
            im = im.crop((x0, y0, x1 + 1, y1 + 1))
    bg = Image.new('RGBA', im.size, fundo + (255,))
    bg.alpha_composite(im)
    return bg.convert('RGB')


def pdf_page(pdf, i, dpi, nome, crop=True):
    import pymupdf
    d = pymupdf.open(pdf)
    pix = d[i].get_pixmap(dpi=dpi, alpha=False)
    tmp = os.path.join(IMG, nome + '_raw.png')
    pix.save(tmp)
    d.close()
    im = Image.open(tmp).convert('RGB')
    if crop:
        a = 255 - np.asarray(ImageOps.grayscale(im))
        # crop near-white margins
        mask = a > 12
        ys, xs = np.where(mask)
        if len(xs):
            pad = int(0.01 * max(im.size))
            x0, y0 = max(xs.min() - pad, 0), max(ys.min() - pad, 0)
            x1, y1 = min(xs.max() + pad, im.width - 1), min(ys.max() + pad, im.height - 1)
            im = im.crop((x0, y0, x1 + 1, y1 + 1))
    return salva(im, nome, q=92, maxlado=3600)


def main():
    # esquema
    pdf_page(os.path.join(REV_D, 'luxflag-schematic.pdf'), 0, 200, 'esquematico')

    # desenhos técnicos (já em PNG A3)
    for name, src in [
        ('A00', os.path.join(MECH, 'desenhos/LXP-A00_conjunto.png')),
        ('P01', os.path.join(MECH, 'desenhos/LXP-P01_tubo_difusor.png')),
        ('P02', os.path.join(MECH, 'desenhos/LXP-P02_tampa.png')),
        ('P03', os.path.join(MECH, 'desenhos/LXP-P03_berco.png')),
        ('P04', os.path.join(MECH, 'desenhos/LXP-P04_tampao.png')),
        ('P05', os.path.join(MECH, 'desenhos/LXP-P05_passa_cabo.png')),
        ('P06', os.path.join(MECH, 'desenhos/LXP-P06_botao.png')),
    ]:
        im = Image.open(src).convert('RGB')
        salva(im, 'des_' + name, q=90, maxlado=2800)

    # renders 3D SIGNA sobre papel
    for name, src in [
        ('iso', os.path.join(MECH, 'renders/iso.png')),
        ('explodida', os.path.join(MECH, 'renders/explodida.png')),
        ('corte', os.path.join(MECH, 'renders/corte.png')),
        ('detalhe_usbc', os.path.join(MECH, 'renders/detalhe_usbc.png')),
        ('detalhe_usbc_anotado', os.path.join(MECH, 'renders/detalhe_usbc_anotado.png')),
        ('em_uso', os.path.join(MECH, 'renders/em_uso.png')),
        ('livre', os.path.join(MECH, 'renders/livre.png')),
    ]:
        salva(sobre(src, PAPEL, pad=20), name, q=90)

    # capa / cenas de uso sobre noite com bloom
    for name, src, r, g in [
        ('capa_iso', os.path.join(MECH, 'renders/iso.png'), 50, 0.9),
        ('capa_uso', os.path.join(MECH, 'renders/em_uso.png'), 60, 1.3),
        ('noite_livre', os.path.join(MECH, 'renders/livre.png'), 55, 1.2),
    ]:
        im = Image.open(src).convert('RGBA')
        bg = Image.new('RGBA', im.size, NIGHT + (255,))
        bg.alpha_composite(im)
        salva(bloom(bg.convert('RGB'), r, g, thr=0.35), name, q=92)

    # estados da lâmina 5 do caderno conceitual (já preparados)
    src_jpg = os.path.join(CONC, 'img', 'jpg')
    for n in [
        'p5_sala_livre', 'p5_sala_prestes', 'p5_sala_ocupado', 'p5_misto',
        'p5_ia_livre', 'p5_ia_processando', 'p5_ia_atencao', 'p5_ia_erro', 'p5_ia_limite',
        'capa', 'p2_iso', 'p9_explodida', 'p9_uso', 'p9_modos',
    ]:
        s = os.path.join(src_jpg, n + '.jpg')
        if os.path.exists(s):
            shutil.copy(s, os.path.join(JPG, n + '.jpg'))
            print('copy', n)

    # placa rev D
    pcb = os.path.join(REV_D, 'renders')
    for name, src in [
        ('pcb_top', 'annotated_top.png'),
        ('pcb_bot', 'annotated_bottom.png'),
        ('pcb_iso1', 'render_iso_front_1.png'),
        ('pcb_iso2', 'render_iso_front_2.png'),
        ('pcb_iso_usb', 'render_iso_front_usb.png'),
        ('pcb_iso_back', 'render_iso_back_1.png'),
        ('pcb_side', 'render_side.png'),
        ('pcb_leds', 'closeup_leds.png'),
        ('pcb_mcu', 'closeup_mcu.png'),
        ('pcb_usb', 'closeup_usb.png'),
        ('cu_top', 'copper_top.png'),
        ('cu_bot', 'copper_bottom.png'),
        ('cu_both', 'copper_both.png'),
        ('fab_top', 'fab_top.png'),
        ('raw_top', 'render_top.png'),
        ('raw_bot', 'render_bottom.png'),
    ]:
        p = os.path.join(pcb, src)
        im = Image.open(p)
        if im.mode == 'RGBA':
            im = sobre(p, PAPEL, crop_alpha=True, pad=8)
        else:
            im = im.convert('RGB')
        salva(im, name, q=90, maxlado=2800)

    # passos de montagem (Pendente rev A — referência visual; a sequência rev B é descrita no texto)
    pr = '/workspace/pendente/renders'
    for i in range(1, 6):
        p = os.path.join(pr, f'passo{i}.png')
        if os.path.exists(p):
            salva(sobre(p, PAPEL, pad=16), f'passo{i}', q=90)

    print('ok')


if __name__ == '__main__':
    main()
