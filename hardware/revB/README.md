# Luxafor Flag clone, rev B (KiCad 9.0.2)

Base: rev A de github.com/lstavares84/luxafor (hardware/). Tudo é gerado por script a partir de `tools/netlist.py`.

| Item | Valor |
|---|---|
| Placa | 11 x 44 mm, FR-4, 2 camadas, 0,8 mm, cobre 1 oz, cantos r = 1 mm, USB-C sobressai 0,7 mm |
| MCU | STM32C071G8U6 (UFQFPN-28 4x4, LCSC C44521811), USB FS sem cristal, DFU na ROM |
| LEDs | 3x SK6805-EC20 (C2890036) em cadeia, VDD = VBUS 5 V, 5 mA/canal |
| Nível | 74AHCT1G125 (C53114384) 3,3 -> 5 V + 33 ohm série; VIH do LED = 0,6*VDD (3,0-3,15 V) |
| Energia | AP2112K-3.3 para o MCU; consumo estimado ~55-60 mA (45 mA LEDs no branco máx.) |
| USB | HRO TYPE-C-31-M-12, CC1/CC2 5,1k, USBLC6-2SC6 |
| SWD | Tag-Connect TC2030-IDC-NL na face de baixo (1 3V3, 2 SWDIO, 3 NRST, 4 SWCLK, 5 GND) |
| BOOT0 | PA14 (= SWCLK) <- JP1 (jumper de solda NA, face de baixo) <- R4 1k <- 3V3 |

## Regenerar
```
cd tools
python3 gen_sch.py
MP=100 ./route.sh -mt 1      # placa + DSN + Freerouting 2.1.0 + SES + GND + DRC
python3 export_jlc.py        # fab/gerber.zip, fab/bom.csv, fab/cpl.csv
kicad-cli sch export pdf -o ../luxflag-schematic.pdf ../project/luxflag.kicad_sch
```

## Saídas
- project/luxflag.kicad_{pro,sch,pcb} (+ .dsn/.ses do roteamento)
- fab/gerber.zip, fab/bom.csv, fab/cpl.csv (formato JLC)
- luxflag-schematic.pdf
- renders/render_top.png, render_bottom.png, render_top_bottom.png, render_iso.png, copper_top/bottom.png
- reports/erc.rpt, reports/drc.rpt, reports/freerouting.log
- docs/parts-check.json (LCSC conferido em 2026-11-21); extratos docs/c071.txt e docs/sk.txt. Os PDFs de datasheet de terceiros não estão no git (ver abaixo).

## Pendências
1. Rotação do CPL na prévia da JLC (U1, U2, U3, U4, J1, D1-D3).
2. LED: footprint renumerado conforme datasheet OPSCO Rev A1 (1 GND, 2 DIN, 3 VDD, 4 DOUT); posição física dos pads igual à rev A.
3. BOOT0 só tem efeito com nBOOT_SEL = 0 (option byte). Flash vazia entra em DFU sozinha.
4. Pino 18/19 = PA11[PA9]/PA12[PA10]: confirmar remapeamento no firmware.
5. Modelos 3D de U1/J1/LEDs nos renders são substitutos visuais (Debian não traz os originais).
6. Par USB sem impedância controlada (FS, < 15 mm).

## Datasheets

Os PDFs de terceiros que acompanhavam `docs/` ficaram de fora do git: `c071.pdf` (~2,7 MB, datasheet do STM32C071) e `sk6805ec20.pdf` (~787 KB, especificação OPSCO do SK6805-EC20). Os extratos de texto (`docs/c071.txt`, `docs/sk.txt`) e o `docs/parts-check.json` permanecem.

- STM32C071G8U6: [página do produto (ST)](https://www.st.com/en/microcontrollers-microprocessors/stm32c071g8.html), [datasheet DS14693](https://www.st.com/resource/en/datasheet/stm32c071g8.pdf), [LCSC C44521811](https://www.lcsc.com/product-detail/C44521811.html)
- SK6805-EC20 (OPSCO, Rev A1): [LCSC C2890036](https://www.lcsc.com/product-detail/C2890036.html), [datasheet na LCSC](https://www.lcsc.com/datasheet/C2890036.pdf), [PDF espelhado na LCSC](https://datasheet.lcsc.com/datasheet/pdf/07c49d22a06f35d4be5cf08c9e5213a0.pdf)
