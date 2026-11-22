#!/bin/bash
# placa -> DSN -> Freerouting -> SES -> trilhas + GND -> DRC
set -e
cd "$(dirname "$0")"
python3 gen_pcb.py 2>&1 | grep -v assert
timeout 900 java -jar freerouting-2.1.0.jar --gui.enabled=false -de ../project/luxflag.dsn -do ../project/luxflag.ses -mp ${MP:-100} "$@" > ../reports/freerouting.log 2>&1
python3 gen_pcb.py --ses ../project/luxflag.ses 2>&1 | grep -v assert
python3 fix_vias.py ../project/luxflag.kicad_pcb 2>&1 | grep -v assert
cd ..
kicad-cli pcb drc --severity-all --schematic-parity -o reports/drc.rpt project/luxflag.kicad_pcb | tail -3
grep "^\[" reports/drc.rpt | sort | uniq -c | sort -rn
