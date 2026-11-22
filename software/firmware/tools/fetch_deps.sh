#!/bin/sh
# Baixa as dependências do firmware nas versões testadas (22/11/2026).
set -e
D="$(cd "$(dirname "$0")/.." && pwd)/third_party"
mkdir -p "$D" && cd "$D"
get() { [ -d "$1" ] || git clone -q "$2" "$1"; git -C "$1" fetch -q --depth 1 origin "$3" 2>/dev/null || true; git -C "$1" checkout -q "$3"; }
get tinyusb https://github.com/hathach/tinyusb.git 490eb4ec9669912388332cff31898cb3263cdd06
get cmsis-device-c0 https://github.com/STMicroelectronics/cmsis-device-c0.git bcc8d94fecb767d1afb53d8c12a8f87ebeb503a2
get CMSIS_5 https://github.com/ARM-software/CMSIS_5.git 55b19837f5703e418ca37894d5745b1dc05e4c91
echo "ok: $(pwd)"
