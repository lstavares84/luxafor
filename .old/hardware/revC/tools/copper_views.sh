#!/bin/bash
# Camadas de cobre/serigrafia em PNG (SVG do kicad-cli -> Chrome headless)
set -e
cd "$(dirname "$0")/../renders"
P=../project/luxflag.kicad_pcb
kicad-cli pcb export svg --layers F.Cu,F.Mask,F.SilkS,Edge.Cuts --mode-single --exclude-drawing-sheet --fit-page-to-board -o copper_top.svg $P >/dev/null
kicad-cli pcb export svg --layers B.Cu,B.Mask,B.SilkS,Edge.Cuts --mirror --mode-single --exclude-drawing-sheet --fit-page-to-board -o copper_bottom.svg $P >/dev/null
# vista só de trilhas (sem os planos de GND), cobre de cima vermelho e de baixo azul
python3 -c "
import pcbnew
b = pcbnew.LoadBoard('$P')
for z in list(b.Zones()): b.Delete(z)
b.Save('/tmp/_tracks_only.kicad_pcb')" 2>/dev/null
kicad-cli pcb export svg --layers F.Cu,B.Cu,Edge.Cuts --mode-single --exclude-drawing-sheet --fit-page-to-board -o copper_both.svg /tmp/_tracks_only.kicad_pcb >/dev/null
kicad-cli pcb export svg --layers F.Fab,F.SilkS,Edge.Cuts --mode-single --exclude-drawing-sheet --fit-page-to-board -o fab_top.svg $P >/dev/null
for s in copper_top copper_bottom copper_both fab_top; do
  echo "<html><body style='margin:0;background:#fff'><img src='$s.svg' style='height:1760px;margin:20px'></body></html>" > _$s.html
  google-chrome --headless=new --no-sandbox --disable-gpu --allow-file-access-from-files --hide-scrollbars \
    --screenshot=$PWD/$s.png --window-size=520,1800 file://$PWD/_$s.html 2>/dev/null
  rm _$s.html
done
