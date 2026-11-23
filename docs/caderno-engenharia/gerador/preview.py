"""Renderiza as lâminas do PDF em PNG (preview/) para conferência visual."""
import pymupdf, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
pdf = os.path.join(HERE, 'signa-engenharia.pdf')
d = pymupdf.open(pdf)
os.makedirs(os.path.join(HERE, 'preview'), exist_ok=True)
dpi = int(sys.argv[1]) if len(sys.argv) > 1 else 110
pages = [int(x) for x in sys.argv[2:]] or range(1, len(d) + 1)
for n in pages:
    d[n - 1].get_pixmap(dpi=dpi).save(os.path.join(HERE, 'preview', f'lamina_{n:03d}.png'))
print(len(d), 'páginas;', 'renderizadas:', len(list(pages)))
