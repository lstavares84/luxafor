#!/usr/bin/env python3
"""Controle do Luxafor Flag (04d8:f372, firmware 0x3c) via /dev/hidraw, sem dependências.

Uso:
  luxafor.py color   <led> <cor>
  luxafor.py fade    <led> <cor> [tempo=20]            # tempo × ~0,25 ms por degrau de brilho
  luxafor.py strobe  <led> <cor> [tempo=10] [rep=3]    # cada piscada = tempo × ~65 ms
  luxafor.py wave    <tipo 1-5> <cor> [rep=3] [vel=30] # vel maior = mais lento
  luxafor.py pattern <id 1-8 | nome> [rep=1]           # rep 0 = repetir até outro comando
  luxafor.py off | version | listen
  luxafor.py raw <hex ...>                             # 8 bytes crus (0x51/0x52 gravam o serial; 0x13 trava)
  Adicione --wait para bloquear até o evento de fim (fade, strobe, wave 5, pattern).

<led>: all | bottom | middle | top | 1 | 2 | 3
<cor>: red green blue yellow cyan magenta white orange off, ou hex RRGGBB
"""
import glob
import os
import select
import sys
import time

VID, PID = "000004D8", "0000F372"

# Validado visualmente: só existem 3 LEDs (1 = baixo, 2 = meio, 3 = topo).
# Os endereços 4-6, 0x41 e 0x42 são aceitos mas não acendem nada.
# b1 = 0x13 TRAVA o firmware; outros valores acima disso não foram testados.
LEDS = {"all": 0xFF, "bottom": 1, "middle": 2, "top": 3, "1": 1, "2": 2, "3": 3}
SAFE_LEDS = {1, 2, 3, 0xFF}

COLORS = {
    "red": (255, 0, 0), "green": (0, 255, 0), "blue": (0, 0, 255),
    "yellow": (255, 255, 0), "cyan": (0, 255, 255), "magenta": (255, 0, 255),
    "white": (255, 255, 255), "orange": (255, 80, 0), "off": (0, 0, 0),
}

# Descrições observadas com 3 LEDs.
WAVES = {
    1: "sobe de baixo para cima",
    2: "vários LEDs acesos juntos, mudando",
    3: "sobe de baixo para cima (variação do 1)",
    4: "os 3 ficam fixos na cor e depois apagam",
    5: "os 3 pulsam juntos uma vez por repetição (único com evento de fim)",
}
PATTERNS = {
    1: ("traffic", "semáforo: vermelho → vermelho+amarelo → verde (~2 s)"),
    2: ("climb", "sobe um a um, fica branco, troca de cor (não mandou evento de fim)"),
    3: ("rainbow", "arco-íris (~11,5 s)"),
    4: ("tones", "3 cores, cada uma forte e depois clareando (~16 s)"),
    5: ("police", "flash vermelho e depois azul (~0,9 s)"),
    6: ("rainbow-blue", "arco-íris terminando em azul (~2,6 s)"),
    7: ("gpb", "verde → rosa → azul (~1,35 s)"),
    8: ("rainbow2", "arco-íris (~3,5 s)"),
}
PATTERN_BY_NAME = {name: pid for pid, (name, _) in PATTERNS.items()}

CMD_STATIC, CMD_FADE, CMD_STROBE, CMD_WAVE, CMD_PATTERN = 0x01, 0x02, 0x03, 0x04, 0x06
CMD_VERSION = 0x80
# 0x51 grava 6 bytes do serial na NVM; 0x52 grava os 4 primeiros; 0x62 lê o serial.
# 0x05 e 0x07–0x0F não existem (sem resposta). Não envie 0x51/0x52 por engano: alteram o serial.
ACK = 0x42
EVT_DONE = b"\x00\x01"


def find_device():
    for path in glob.glob("/sys/class/hidraw/hidraw*/device/uevent"):
        with open(path) as f:
            if f"HID_ID=0003:{VID}:{PID}" in f.read():
                return "/dev/" + path.split("/")[4]
    sys.exit("Luxafor Flag não encontrado")


def parse_led(s):
    led = LEDS.get(s.lower())
    if led is None:
        sys.exit(f"LED inválido: {s} (use all, bottom, middle, top, 1, 2 ou 3)")
    return led


def parse_color(s):
    s = s.lower().lstrip("#")
    if s in COLORS:
        return COLORS[s]
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


class Luxafor:
    def __init__(self, path=None):
        self.fd = os.open(path or find_device(), os.O_RDWR)

    def read(self, timeout):
        out, end = [], time.time() + timeout
        while (left := end - time.time()) > 0:
            if select.select([self.fd], [], [], left)[0]:
                out.append(os.read(self.fd, 8))
        return out

    def send(self, data, timeout=0.2):
        data = bytes(data)[:8].ljust(8, b"\0")
        # Sem Report ID: o hidraw descarta um 0x00 inicial, então prefixamos
        # 0x00 para que o opcode chegue intacto ao firmware.
        os.write(self.fd, b"\0" + data)
        return self.read(timeout)

    def wait(self, timeout=60):
        """Bloqueia até o evento 00 01 (fim de animação). Retorna os segundos ou None."""
        t0 = time.time()
        while time.time() - t0 < timeout:
            if any(p[:2] == EVT_DONE for p in self.read(0.05)):
                return time.time() - t0
        return None

    @staticmethod
    def _check_led(led):
        if led not in SAFE_LEDS:
            raise ValueError(f"LED 0x{led:02x} não validado (0x13 trava o firmware)")

    def color(self, led, rgb):
        self._check_led(led)
        return self.send([CMD_STATIC, led, *rgb])

    def fade(self, led, rgb, t=20):
        self._check_led(led)
        return self.send([CMD_FADE, led, *rgb, t])

    def strobe(self, led, rgb, t=10, rep=3):
        self._check_led(led)
        return self.send([CMD_STROBE, led, *rgb, t, 0, rep])

    def wave(self, kind, rgb, rep=3, speed=30):
        if kind not in WAVES:
            raise ValueError("wave: tipo 1 a 5")
        return self.send([CMD_WAVE, kind, *rgb, 0, rep, speed])

    def pattern(self, pid, rep=1):
        if pid not in PATTERNS:
            raise ValueError("pattern: id 1 a 8 (0 e 9+ não validados)")
        return self.send([CMD_PATTERN, pid, rep])

    def off(self):
        return self.color(0xFF, (0, 0, 0))

    def version(self):
        for r in self.send([CMD_VERSION]):
            if r[0] == CMD_VERSION:
                return r[1]


def main(a):
    wait = "--wait" in a
    a = [x for x in a if x != "--wait"]
    if not a:
        sys.exit(__doc__)
    lx, cmd = Luxafor(), a[0]
    n = lambda i, d: int(a[i], 0) if len(a) > i else d
    if cmd == "color":
        r = lx.color(parse_led(a[1]), parse_color(a[2]))
    elif cmd == "fade":
        r = lx.fade(parse_led(a[1]), parse_color(a[2]), n(3, 20))
    elif cmd == "strobe":
        r = lx.strobe(parse_led(a[1]), parse_color(a[2]), n(3, 10), n(4, 3))
    elif cmd == "wave":
        r = lx.wave(int(a[1], 0), parse_color(a[2]), n(3, 3), n(4, 30))
    elif cmd == "pattern":
        pid = PATTERN_BY_NAME.get(a[1]) or int(a[1], 0)
        r = lx.pattern(pid, n(2, 1))
    elif cmd == "off":
        r = lx.off()
    elif cmd == "version":
        print(f"firmware 0x{lx.version():02x}")
        return
    elif cmd == "raw":
        r = lx.send([int(x, 16) for x in a[1:]], 0.5)
    elif cmd == "listen":
        while True:
            for p in lx.read(1):
                print(p.hex(" "), flush=True)
    else:
        sys.exit(__doc__)
    for p in r:
        print("RX", p.hex(" "))
    if wait:
        # o evento pode ter chegado já dentro da janela de leitura do send()
        d = 0.0 if any(p[:2] == EVT_DONE for p in r) else lx.wait()
        print("fim após %.2f s" % d if d is not None else "sem evento de fim")


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except ValueError as e:
        sys.exit(f"erro: {e}")
