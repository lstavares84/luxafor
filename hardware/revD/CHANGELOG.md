# CHANGELOG: placa SIGNA rev D (a partir da rev C)

Data: 2026-11-22. Origem: conceito SIGNA [pt37u]. A placa mostra o estado da sala (LIVRE / PRESTES A ENTRAR / OCUPADO) vindo do Google/Outlook. Em OCUPADO, os 3 LEDs ficam travados em vermelho. O monitor de IA é opcional (opt-in).
Tudo é regenerado a partir de `tools/netlist.py` + `tools/gen_pcb.py`, como na rev C.

## Resumo
| # | Mudança | Por quê |
|---|---|---|
| 1 | **S1**: chave tátil lateral ALPS **SKRTLAE010** (LCSC C110293), na borda de baixo (y = 0, girada 180°) | Permite alternar OCUPADO/LIVRE à mão sem PC. A mesma tecla serve para entrar em DFU (BOOT0) sem abrir o produto |
| 2 | **R5** 1 kΩ 0402 (C11702, basic) entre S1 e PA14 (SWCLK/BOOT0) | Proteção ESD/corrente em série. Isola o botão do SWD |
| 3 | **TP1** VBUS, **TP2** dado dos LEDs 5 V, **TP3** GND (pads Ø1,0 na face de baixo, sem componente) | Teste de produção com cama de pregos/ponteira, sem soldar nada |
| 4 | LEDs D1–D3 e C6–C8 deslocados +2,2 mm (y = 5,2 / 12,2 / 19,2). TC2030 (J2) em y = 8,7 e C2 em y = 21,4 | Abre espaço para o S1 na borda |
| 5 | **Orelhas** na ponta do USB: largura total 15,2 mm (±7,6 do eixo), 1,0 mm de altura, cantos externos r 0,3 e internos r 0,5 | Batente axial: a placa apoia nas fendas da flange do berço e fica presa sob o ressalto da tampa. Ver item "Mecânica" |
| 6 | Serigrafia "SIGNA rev D"; título do esquema rev D | Identificação |
| 7 | Footprint próprio `indicador:SW_SKRTLAE010_JLC` (pads aparados) | O footprint da biblioteca KiCad deixava 0,099 mm entre o furo NPTH e o pad. A regra pede 0,25 mm |
| 8 | Modelos 3D próprios (`lib/3d/`, build123d): J1, LEDs, MCU, S1 | STEP fiel para a montagem integrada ([`mecanica/`](../../mecanica/)) |
| 9 | `tools/fix_vias.py` no `route.sh` | O Freerouting deixava 2 vias com furo a 0,498 mm (aviso). Agora ficam a ≥ 0,503 mm |

## Ligação do botão (detalhe)
- Caminho: `3V3 → R4 1 kΩ → BOOT_PU → S1 → BTN → R5 1 kΩ → PA14 (SWCLK/BOOT0)`. R5 fica em paralelo com o JP1 (jumper de solda, que continua lá).
- **Em uso:** o firmware lê o IDR de PA14 sem tirar o pino da função alternativa SWCLK. O pull-down interno do SWCLK mantém o nível baixo; botão apertado = nível ALTO (≈ 3V3 × pull-down/(2 k + pull-down)). O SWD continua funcionando. Debounce no firmware (sugestão: 30 ms; pressão longa de 2 s para não trocar sem querer).
- **Recuperação:** segurar o botão ao ligar o cabo põe BOOT0 em 1 e entra no DFU da ROM. **Só vale com `nBOOT_SEL = 0`** (option byte, a gravar na produção).
- **Sem capacitor** no nó: um capacitor em SWCLK estragaria o SWD.

## Avaliado e NÃO feito (com motivo)
| Opção | Decisão | Motivo |
|---|---|---|
| Botão capacitivo | Não | O STM32C071 não tem TSC. A leitura teria de atravessar ~7 mm de ar + PC do tubo, o que não é confiável. Usar a tampa de Al como eletrodo pediria contato de mola e daria toques falsos ao segurar o produto |
| Sensor de luz ambiente | Não | Dentro do tubo opalino ele veria os próprios LEDs. Só funcionaria apagando os LEDs para medir, e isso causa cintilação visível. O brilho pode ser ajustado pelo app no PC. Custo/benefício ruim |
| TVS dedicado no botão | Não | O botão P06 é de PC isolante, com ~6 mm de caminho de fuga até o cobre, e R5 limita a corrente. O USBLC6 continua no USB |
| Trocar MCU por STM32C071GBU6 (128 KB) | Não (fica como alternativa documentada) | Estoque 0 na JLC e na LCSC em 2026-11-22, a US$ 3,54 @100. O G8U6 (64 KB) tem 109 un. na JLC. As versões "N" (GBU6N/G8U6N) têm estoque 0 e **não** são troca direta |

## Mecânica (efeito na montagem SIGNA rev B)
- Na rev A, a placa só apoiava a borda de baixo no fundo da ranhura e **nada a segurava por cima**. Puxar o cabo (8–20 N para tirar um USB-C) arrancaria a placa das ranhuras. Os cantos r 1 também não assentavam bem no fundo.
- Na rev D, as orelhas apoiam no piso das fendas da flange (Z = 50,75) e a tampa fica 0,25 mm acima. A borda de baixo fica 0,30 mm acima do fundo da ranhura, o que evita apoio duplo (hiperestático). A placa subiu 0,75 mm (PCB_Z0 = 7,75).
- Resultado: a boca do USB-C fica 0,40 mm acima da flange. Qualquer plugue com ≥ 5,8 mm de casca exposta encaixa até o fim, e o rebaixo para sobremolde da flange foi eliminado.
- Painelização: a placa tem 15,2 mm de largura nas orelhas. O trilho/V-cut precisa considerar isso; as orelhas não podem ser quebradas.

## Verificação
- ERC: **0 violações** (`reports/erc.rpt`).
- DRC: **0 erros, 0 pendências, paridade OK**. 1 aviso `lib_footprint_mismatch` no J1 (serigrafia editada de propósito, igual à rev C) (`reports/drc.rpt`).
- Roteamento: Freerouting 2.1.0 com MP=80. Com MP=100/150 o SES perdia as redes da cadeia de LEDs (5 pendências). Resultado: 342 trilhas e 24 vias.
- Contorno: 15,25 × 44,05 mm no bounding box do Edge.Cuts (as orelhas entram no bounding box).

## Custo (delta rev C → rev D)
Preços da API de peças da JLCPCB em 2026-11-22 (`docs/jlc_revD_2026-11-22.json`):
| Peça | LCSC | Estoque JLC | Biblioteca | Preço |
|---|---|---|---|---|
| SKRTLAE010 | C110293 | 69 662 | extended | US$ 0,1437 @1, 0,1025 @150, 0,0922 @500, 0,0779 @3000 |
| 1 kΩ 0402 | C11702 | 29 M | basic | US$ 0,0011 / 0,0009 @1000 |
| STM32C071G8U6 (mantido) | C44521811 | **109** | extended | US$ 1,80 @100, 1,67 @490 |
| STM32C071GBU6 (alternativa) | C42113261 | **0** | extended | US$ 3,54 @100 |

- **Componentes: +US$ 0,12 por placa @100 e +US$ 0,09 @1000** (S1 + R5).
- **Montagem: +1 peça extended ≈ US$ 3 por pedido** (taxa pública da JLC, conferir na cotação). Equivale a +US$ 0,03/placa @100. As juntas a mais são desprezíveis.
- **Estimativa total da eletrônica: ≈ +US$ 0,15/placa @100 e ≈ +US$ 0,10 @1000.**
- A PCB não muda de preço de forma relevante (15,2 × 44 em vez de 11 × 44: ~+0,01–0,02 US$/placa no painel, **estimativa**).
- Mecânica (rev B): botão P06 + furo/rebaixo no tampão. Ver [`mecanica/bom/bom_completa.md`](../../mecanica/bom/bom_completa.md) (**estimativa**: +US$ 0,40 @100 impresso; +US$ 0,02 + ~US$ 300 de ferramental @1000).
- Produto completo (BOM SIGNA vs. Pendente rev A, **estimativa**): US$ 17,98 → 18,53 @100 (+0,55); US$ 10,91 → 11,32 @1000 (+0,41).

## Pendências para o firmware (equipe signa-sw)
1. Ler o botão pelo IDR de PA14 sem reconfigurar o pino (manter AF SWCLK com pull-down). Fazer debounce e definir o gesto (curto = alterna OCUPADO/LIVRE manual; longo = ?).
2. Gravar `nBOOT_SEL = 0` na produção para o DFU pelo botão funcionar.
3. Durante o debug com a sonda SWD conectada, o botão gera clocks espúrios. Não apertar durante o debug.
