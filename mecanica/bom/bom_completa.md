# BOM completa — SIGNA (mecânica rev B, placa rev D)

Gerada por `bom/gerar_bom.py` (2026-11-22). Valores em **US$ por produto montado** (qtd × preço unitário), em dois lotes (100 e 1000 unidades).
**Só os componentes eletrônicos têm preço consultado** (API de peças da JLCPCB, faixa de quantidade do lote; arquivo `jlc_precos_eletronica.json`).
Todo o resto é **ESTIMATIVA** de ordem de grandeza e precisa de cotação (ver `rfq_checklist.md`). Não inclui frete, impostos de importação (Brasil: II/IPI/ICMS podem somar 60–100 %), margem nem certificações.

BOM da placa (fonte única): `../../hardware/revD/fab/bom.csv`. Componentes da placa: **US$ 2.67** (lote 100) / **US$ 2.26** (lote 1000).

| Cat. | Item | Descrição | Desenho/ref. | Fornecedor | Part number | Qtd | US$ @100 | US$ @1000 | Status |
|---|---|---|---|---|---|---|---|---|---|
| Eletrônica | U1 | MCU STM32C071G8U6 (QFN-28) | LXE-E01 | LCSC/JLCPCB | STM32C071G8U6 (C44521811) | 1 | 1.800 | 1.617 | verificado (preço/estoque do dia) |
| Eletrônica | D1-D3 | LED RGB WS2816B-2020 | LXE-E01 | LCSC/JLCPCB | WS2816B-2020 (C4154877) | 3 | 0.222 | 0.172 | verificado (preço/estoque do dia) |
| Eletrônica | J1 | USB-C HRO TYPE-C-31-M-12 | LXE-E01 | LCSC/JLCPCB | TYPE-C-31-M-12 (C165948) | 1 | 0.148 | 0.104 | verificado (preço/estoque do dia) |
| Eletrônica | U2 | LDO AP2112K-3.3TRG1 | LXE-E01 | LCSC/JLCPCB | AP2112K-3.3TRG1 (C51118) | 1 | 0.129 | 0.094 | verificado (preço/estoque do dia) |
| Eletrônica | U3 | Buffer TI SN74AHCT1G125DBVR | LXE-E01 | LCSC/JLCPCB | SN74AHCT1G125DBVR (C7484) | 1 | 0.089 | 0.071 | verificado (preço/estoque do dia) |
| Eletrônica | U4 | ESD ST USBLC6-2SC6 | LXE-E01 | LCSC/JLCPCB | USBLC6-2SC6 (C7519) | 1 | 0.118 | 0.084 | verificado (preço/estoque do dia) |
| Eletrônica | C1 | Cap. 10 uF 0603 X5R | LXE-E01 | LCSC/JLCPCB | CL10A106KP8NNNC (C19702) | 1 | 0.017 | 0.012 | verificado (preço/estoque do dia) |
| Eletrônica | C2 | Cap. 1 uF 0402 X5R | LXE-E01 | LCSC/JLCPCB | CL05A105KA5NQNC (C52923) | 1 | 0.005 | 0.004 | verificado (preço/estoque do dia) |
| Eletrônica | C3-C8 | Cap. 100 nF 0402 X7R | LXE-E01 | LCSC/JLCPCB | CL05B104KO5NNNC (C1525) | 6 | 0.015 | 0.009 | verificado (preço/estoque do dia) |
| Eletrônica | R1,R2 | Res. 5,1 k 0402 | LXE-E01 | LCSC/JLCPCB | 0402WGF5101TCE (C25905) | 2 | 0.003 | 0.002 | verificado (preço/estoque do dia) |
| Eletrônica | R3 | Res. 33 R 0402 | LXE-E01 | LCSC/JLCPCB | 0402WGF330JTCE (C25105) | 1 | 0.001 | 0.001 | verificado (preço/estoque do dia) |
| Eletrônica | R4,R5 | Res. 1 k 0402 (pull-up BOOT0 + série do botão) | LXE-E01 | LCSC/JLCPCB | 0402WGF1001TCE (C11702) | 2 | 0.002 | 0.002 | verificado (preço/estoque do dia) |
| Eletrônica | S1 | Chave tátil lateral ALPS SKRTLAE010 (1,6 N) | LXE-E01 | LCSC/JLCPCB | SKRTLAE010 (C110293) | 1 | 0.116 | 0.092 | verificado (preço/estoque do dia) |
| Eletrônica | PCB | PCB 2 camadas 11×44×0,8 mm (15,2 nas orelhas), ENIG, painelizada | LXE-E01 | JLCPCB | gerber.zip (luxpcb-revD/fab) | 1 | 0.200 | 0.060 | ESTIMATIVA |
| Eletrônica | PCBA | Montagem SMT 1 face (setup + estêncil + 7 peças "extended" × US$3 + juntas) | LXE-E01 | JLCPCB | — | 1 | 0.505 | 0.150 | ESTIMATIVA |
| Eletrônica | FW | Gravação de firmware via USB DFU (ROM) + teste | teste.md | interno | — | 1 | 0.100 | 0.050 | ESTIMATIVA |
| Mecânica | P01 | Tubo difusor PC opalino Ø16/13 × 48, cortado e jateado | LXP-P01 | fornecedor de tubos PC difusor (China) / serralheria plástica (BR) | não definido | 1 | 0.900 | 0.300 | ESTIMATIVA — cotar |
| Mecânica | P02 | Tampa Al 6061-T6 torneada, anodizada preta | LXP-P02 | JLCCNC / PCBWay CNC (protótipo); torno CNC tipo suíço (série) | não definido | 1 | 5.500 | 1.600 | ESTIMATIVA — cotar |
| Mecânica | P02b | Tampa impressa (só protótipo; não soma no custo de série) | LXP-P02 | JLC3DP (MJF PA12 preto / SLA preto) | — | 0 | 1.500 | 0.000 | ESTIMATIVA (opcional) |
| Mecânica | P03 | Berço PC branco | LXP-P03 | 100 un.: SLA/MJF (JLC3DP); 1000 un.: injeção (molde família P03+P04) | não definido | 1 | 1.800 | 0.100 | ESTIMATIVA — cotar |
| Mecânica | P04 | Tampão PC opalino | LXP-P04 | idem P03 | não definido | 1 | 0.900 | 0.060 | ESTIMATIVA — cotar |
| Mecânica | P06 | Botão (pino) PC opalino Ø3/Ø4,4 × 7,4 | LXP-P06 | 100 un.: SLA translúcido (JLC3DP); 1000 un.: cavidade extra no molde família P03+P04 | não definido | 1 | 0.400 | 0.020 | ESTIMATIVA — cotar |
| Mecânica | P05 | Passa-cabo TPE 60A bipartido | LXP-P05 | 100 un.: silicone fundido em molde impresso / TPU 3D; 1000 un.: injeção TPE | não definido | 1 | 0.600 | 0.050 | ESTIMATIVA — cotar |
| Mecânica | FERR | Ferramental amortizado (molde família P03+P04+P06 em alumínio ~US$3.300 + molde P05 ~US$1.000) | manufatura.md | ferramentaria (China/BR) | — | 1 | 0.000 | 4.300 | ESTIMATIVA |
| Cabo | C01 | Cabo USB-C ↔ USB-C 1,5 m, USB 2.0, capa Ø3,5–4,0; casca ≥5,8 mm, sobremolde ≤11,6×6,4, sobremolde+bota ≤24,5 mm, bota ≤Ø6,4 | LXP-A00 item 7 | fabricante de cabos OEM (Shenzhen) / distribuidor BR | não definido | 1 | 1.800 | 1.000 | ESTIMATIVA — exigir amostra e medir plugue |
| Cabo | C02 | Adaptador USB-A macho → USB-C fêmea (opcional, p/ PCs sem USB-C) | — | idem | não definido | 1 | 0.450 | 0.250 | ESTIMATIVA (decisão Lucas) |
| Embalagem | K01 | Caixa kraft/cartão 60×40×130 mm com berço de papelão | — | gráfica BR / fornecedor China | não definido | 1 | 1.000 | 0.350 | ESTIMATIVA |
| Embalagem | K02 | Cartão de instruções A7 + QR para software | — | gráfica | — | 1 | 0.100 | 0.030 | ESTIMATIVA |
| Embalagem | K03 | Saco/manga de proteção para o tubo | — | genérico | — | 1 | 0.050 | 0.020 | ESTIMATIVA |
| Etiquetas | L01 | Etiqueta de série/lote (dentro da caixa) + etiqueta da caixa | — | genérico | — | 2 | 0.060 | 0.020 | ESTIMATIVA |
| Etiquetas | L02 | Gravação a laser no topo da tampa (logo/nº série) | LXP-P02 nota 6 | fornecedor CNC | — | 1 | 0.300 | 0.100 | ESTIMATIVA (opcional) |
| Fixação/adesivos | F01 | Nenhum parafuso nem cola no projeto (encaixes + press-fit) | — | — | — | 0 | 0.000 | 0.000 | n/a |
| Fixação/adesivos | F02 | Cola UV (gota) de contingência no pino do berço, se o press-fit soltar | — | ex.: adesivo UV para PC (a escolher) | não definido | 0 | 0.020 | 0.010 | opcional |
| Montagem | M01 | Montagem final (≈4 min) + teste funcional (≈1 min) + embalagem | montagem.md / teste.md | interno | — | 1 | 1.200 | 0.600 | ESTIMATIVA |

## Totais por unidade (US$)

| Categoria | Lote 100 | Lote 1000 |
|---|---|---|
| Eletrônica | 3.47 | 2.52 |
| Mecânica | 10.10 | 6.43 |
| Cabo | 2.25 | 1.25 |
| Embalagem | 1.15 | 0.40 |
| Etiquetas | 0.36 | 0.12 |
| Fixação/adesivos | 0.00 | 0.00 |
| Montagem | 1.20 | 0.60 |
| **Total** | **18.53** | **11.32** |

Notas:
- P02b (tampa impressa) e F02 (cola de contingência) não entram no total.
- Lote 1000 inclui ferramental amortizado (US$ 4,30/un.). Sem ele: US$ 7.02.
- Cabo C02 (adaptador USB-A) entra no total; retirar se Lucas decidir não incluir.
- **Risco de suprimento:** STM32C071G8U6 tinha só 109 un. no estoque JLC em 2026-11-22 (preço do lote 1000 usa a faixa de preço, não garante estoque). Alternativa pino a pino STM32C071GBU6 (C42113261): 0 un., US$ 3,54 @100.
- Rev D vs. rev C: +S1 (C110293, extended) +R5 (C11702, basic). A peça extended a mais custa ~US$ 3 por pedido de montagem (taxa pública JLC; conferir na cotação).
