#!/bin/bash
# Gera as vistas 3D da placa (fundo transparente -> recorte -> fundo claro)
set -e
cd "$(dirname "$0")/../renders"
P=../project/luxflag.kicad_pcb
R="kicad-cli pcb render --quality high --background transparent"
r() { out=$1; shift; $R "$@" -o raw_$out $P >/dev/null; }
r render_top.png            --side top    -w 1000 -h 2600 --zoom 0.93
r render_bottom.png         --side bottom -w 1000 -h 2600 --zoom 0.93
r render_top_hires.png      --side top    -w 2000 -h 5200 --zoom 0.93
r render_iso_front_1.png    --side top    --perspective --rotate "310,0,330" --zoom 0.8 -w 2200 -h 2200
r render_iso_front_2.png    --side top    --perspective --rotate "300,0,30"  --zoom 0.8 -w 2200 -h 2200
r render_iso_front_usb.png  --side top    --perspective --rotate "325,0,180" --zoom 0.8 -w 2200 -h 2200
r render_iso_front_low.png  --side top    --perspective --rotate "290,0,345" --zoom 0.8 -w 2200 -h 2200
r render_iso_back_1.png     --side bottom --perspective --rotate "310,0,330" --zoom 0.8 -w 2200 -h 2200
r render_iso_back_2.png     --side bottom --perspective --rotate "300,0,30"  --zoom 0.8 -w 2200 -h 2200
r render_side.png           --side left   --zoom 2.6 -w 2400 -h 700
