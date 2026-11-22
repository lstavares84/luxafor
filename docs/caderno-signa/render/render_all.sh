#!/bin/bash
B=/opt/blender-4.2.3-linux-x64/blender
N=${N:-64}
cd "$(dirname "$0")"
for s in ${@:-capa p8_principal p8_alerta p8_detalhe p9_uso p9_modos p9_explodida p7_frente p7_verso p7_iso}; do
  $B -b --python scenes.py -- $s $N 2>&1 | grep -E "RENDER OK|rror|Traceback"
done
