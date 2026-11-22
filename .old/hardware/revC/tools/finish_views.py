"""Recorta as vistas cruas (raw_*.png, fundo transparente) e aplica fundo claro.
Também gera os close-ups a partir do render de alta resolução."""
import glob, os
from PIL import Image
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "renders"))
BG = (244, 245, 247)
def finish(src, dst, margin=40):
    im = Image.open(src).convert("RGBA")
    bb = im.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()
    im = im.crop((max(bb[0]-margin, 0), max(bb[1]-margin, 0), min(bb[2]+margin, im.width), min(bb[3]+margin, im.height)))
    out = Image.new("RGBA", im.size, BG + (255,)); out.alpha_composite(im)
    out.convert("RGB").save(dst, optimize=True)
for f in glob.glob("raw_render_*.png"):
    if "hires" in f: continue
    finish(f, f[4:])
# close-ups (calibração: 2000x5200 zoom 0.93 -> board x 0..11 mm)
hi = Image.open("raw_render_top_hires.png").convert("RGBA")
bb = hi.getchannel("A").point(lambda a: 255 if a > 200 else 0).getbbox()
s = (bb[2] - bb[0]) / 11.0; x0, y0 = bb[0], bb[1]
def crop_mm(name, ya, yb):
    box = (int(x0 - 0.6*s), int(y0 + ya*s), int(x0 + 11.6*s), int(y0 + yb*s))
    im = hi.crop(box); out = Image.new("RGBA", im.size, BG + (255,)); out.alpha_composite(im)
    out.convert("RGB").save(name, optimize=True)
crop_mm("closeup_leds.png", -0.6, 19.5)
crop_mm("closeup_mcu.png", 18.5, 30.0)
crop_mm("closeup_usb.png", 28.5, 45.3)
print("scale px/mm hires:", s)
