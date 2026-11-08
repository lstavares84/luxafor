#!/usr/bin/env python3
"""Exporta os arquivos de fabricação e montagem para a JLCPCB.

Saída em hardware/indicador/jlc/:
  gerber/            Gerbers + furação (Excellon); compactar em gerber.zip
  gerber.zip         arquivo para upload da placa
  bom.csv            Comment, Designator, Footprint, LCSC
  cpl.csv            Designator, Mid X, Mid Y, Layer, Rotation

As rotações do CPL seguem o padrão do KiCad. Confira a prévia de montagem no
site da JLC antes de pagar: alguns encapsulamentos (SOT-23, TSSOP, USB-C)
costumam precisar de correção de 90 ou 180 graus.
"""
import csv
import os
import shutil
import subprocess
from collections import defaultdict

from netlist import PARTS

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.join(os.path.dirname(HERE), "indicador")
PCB = os.path.join(PROJ, "indicador.kicad_pcb")
OUT = os.path.join(PROJ, "jlc")
GER = os.path.join(OUT, "gerber")
LAYERS = "F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts"


def run(*args):
    subprocess.run(["kicad-cli", *args], check=True, stdout=subprocess.DEVNULL)


def main():
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(GER)
    run("pcb", "export", "gerbers", "--layers", LAYERS, "--subtract-soldermask",
        "--no-netlist", "-o", GER + "/", PCB)
    run("pcb", "export", "drill", "--format", "excellon", "--excellon-separate-th",
        "--generate-map", "--map-format", "gerberx2", "-o", GER + "/", PCB)
    shutil.make_archive(os.path.join(OUT, "gerber"), "zip", GER)

    pos = os.path.join(OUT, "pos.csv")
    run("pcb", "export", "pos", "--format", "csv", "--units", "mm", "--side", "both",
        "-o", pos, PCB)

    # BOM: só peças montadas (com código LCSC)
    groups = defaultdict(list)
    for ref, (_lib, _sym, value, fp, lcsc, _c, _p) in PARTS.items():
        if lcsc:
            groups[(value, fp.split(":")[1], lcsc)].append(ref)
    with open(os.path.join(OUT, "bom.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Comment", "Designator", "Footprint", "LCSC"])
        for (value, fp, lcsc), refs in sorted(groups.items(), key=lambda g: g[1][0]):
            w.writerow([value, ",".join(sorted(refs)), fp, lcsc])

    mounted = {r for refs in groups.values() for r in refs}
    with open(pos) as f, open(os.path.join(OUT, "cpl.csv"), "w", newline="") as g:
        w = csv.writer(g)
        w.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
        for row in csv.DictReader(f):
            if row["Ref"] in mounted:
                w.writerow([row["Ref"], row["PosX"] + "mm", row["PosY"] + "mm",
                            "Top" if row["Side"] == "top" else "Bottom", row["Rot"]])
    os.remove(pos)
    print("ok:", OUT)


if __name__ == "__main__":
    main()
