# Luxafor Flag clone, rev C (KiCad 9.0.2)

Evolução da rev B (`hardware/revB`). Tudo é gerado por script a partir de `tools/netlist.py`.
Apresentação completa, galeria e tabela de componentes: seção «Hardware rev C» no [README principal](../../README.md).

| Item | Valor |
|---|---|
| Placa | 11 × 44 mm, FR-4, 2 camadas, 0,8 mm, 1 oz, cantos r = 1 mm; USB-C sobressai 0,7 mm |
| LEDs | 3× **WS2816B-2020** (Worldsemi, LCSC C4154877): 16 bit/canal + gamma 4 bit, PWM 10 kHz, 20 mA (R+G+B), 6 pinos com dado duplo BI/BO |
| MCU | STM32C071G8U6 (UFQFPN-28 4×4, C44521811), USB FS sem cristal, DFU na ROM |
| Nível | SN74AHCT1G125DBVR (TI, SOT-23-5, C7484): VIH 2 V com VCC 5 V; WS2816 exige VIH ≥ 0,7×VDD = 3,5 V |
| Energia | VBUS 5 V nos LEDs e no buffer; AP2112K-3.3 (C51118) no MCU. Consumo estimado ≤ ~70 mA (3 × 20 mA + MCU) |
| USB | HRO TYPE-C-31-M-12 (C165948), CC1/CC2 5,1 kΩ, USBLC6-2SC6 (C7519) |
| SWD / BOOT0 | Tag-Connect TC2030-IDC-NL na face de baixo; JP1 (jumper de solda NA) + R4 1 kΩ puxam PA14/BOOT0 a 3V3 |
| Verificação | ERC 0. DRC 0 erros, 0 pendências, paridade OK; 1 aviso (silk do USB-C editado de propósito) |
| Roteamento | Freerouting 2.1.0 (DSN/SES, `-mt 1`), 314 trilhas, 20 vias, + remoção de trechos duplicados e pontas soltas |

## Ligação dos LEDs (datasheet WS2816B-2020, "Typical Application Circuit")
`U3.Y → R3 33 Ω → D1.DI`; `D1.BI = GND`; `Dn.DO → Dn+1.DI`; `Dn.BO → Dn+1.BI`; `D3.DO/BO` livres.
Firmware: 48 bits por LED (G16 R16 B16, MSB primeiro), T0H 200–320 ns, T1H 520–800 ns, reset > 280 µs.

## Regenerar
```
cd tools
python3 gen_sch.py
MP=100 ./route.sh -mt 1        # placa + DSN + Freerouting + SES + limpeza + GND + DRC
python3 export_jlc.py          # fab/gerber.zip, bom.csv, cpl.csv
kicad-cli sch export pdf -o ../luxflag-schematic.pdf ../project/luxflag.kicad_sch
bash render_views.sh && python3 finish_views.py   # vistas 3D + close-ups
bash copper_views.sh                              # camadas de cobre (SVG -> PNG via Chrome)
python3 annotate.py                               # renders anotados
python3 parts_check.py                            # estoque LCSC/JLC -> docs/parts-check.json
```
O Freerouting 2.1.0 (jar) não vai no pacote: baixe de github.com/freerouting/freerouting/releases.

## Pendências
1. Rotação do CPL na prévia da JLC (U1–U4, J1, D1–D3).
2. Footprint do WS2816B-2020 feito pelo datasheet; conferir na prévia.
3. BOOT0 só vale com `nBOOT_SEL = 0`; com flash vazia entra em DFU sozinho.
4. Pinos 18/19 = PA11[PA9]/PA12[PA10]: confirmar remapeamento no firmware.
5. Modelos 3D de U1, J1 e LEDs nos renders são substitutos visuais.
6. Par USB sem impedância controlada (FS, < 15 mm).
