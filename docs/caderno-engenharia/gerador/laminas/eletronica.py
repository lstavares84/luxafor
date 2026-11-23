"""Lâminas de eletrônica — placa SIGNA rev D."""
from lib_metrologia import *
from helpers import *
import dados as D


def register(book):
    book.divisor('II', 'ELETRÔNICA', [
        'Placa rev D: STM32C071G8U6, três WS2816B-2020, USB-C, botão lateral, pontos de teste e orelhas de retenção.',
        'O esquemático, a pinagem, o orçamento de potência, o layout, o ERC/DRC e os arquivos de fabricação cabem nesta seção.',
        'Custo eletrônico consultado na API da JLCPCB em 22/11/2026. ERC: zero violações. DRC: zero erros, um aviso de serigrafia no J1.',
    ], short='ELETRÔNICA')
    book.add_flow('II  ELETRÔNICA', 'Placa rev D  ·  o que mudou', l_delta, 'PLACA REV D')
    book.add('II  ELETRÔNICA', 'Esquemático', l_esquema)
    book.add_flow('II  ELETRÔNICA', 'Pinagem do MCU', l_pinagem)
    book.add_flow('II  ELETRÔNICA', 'Redes e componentes', l_redes)
    book.add_flow('II  ELETRÔNICA', 'Alimentação e corrente', l_potencia)
    book.add_flow('II  ELETRÔNICA', 'Cadeia de LEDs e temporização', l_leds, 'CADEIA DE LEDS')
    book.add_flow('II  ELETRÔNICA', 'USB, ESD e proteção', l_usb)
    book.add_flow('II  ELETRÔNICA', 'Botão, BOOT0 e pontos de teste', l_botao, 'BOTÃO, BOOT0 E TPs')
    book.add_flow('II  ELETRÔNICA', 'BOM eletrônica e estoque JLC', l_bom, 'BOM ELETRÔNICA')
    book.add_flow('II  ELETRÔNICA', 'Layout, stackup e regras', l_layout)
    book.add('II  ELETRÔNICA', 'Vista anotada  ·  face de cima', l_anot_top, 'VISTA ANOTADA · CIMA')
    book.add('II  ELETRÔNICA', 'Vista anotada  ·  face de baixo', l_anot_bot, 'VISTA ANOTADA · BAIXO')
    book.add_flow('II  ELETRÔNICA', 'Close-ups e cobre', l_closeups)
    book.add_flow('II  ELETRÔNICA', 'ERC e DRC', l_ercdrc)
    book.add_flow('II  ELETRÔNICA', 'Fabricação e parâmetros JLC', l_fab, 'FABRICAÇÃO JLC')
    book.add_flow('II  ELETRÔNICA', 'Painelização e pendências', l_painel)


def l_delta(F):
    F.titulo('PLACA REV D  ·  O QUE MUDOU EM RELAÇÃO À REV C')
    F.glossario('Fonte: luxpcb-revD/CHANGELOG.md, 22/11/2026. Contorno: 15,25 × 44,05 mm no bounding box do Edge.Cuts (as orelhas entram no box).')
    F.L.image_fit(JPG('pcb_iso1'), 266, 76, 138, 162, 'iso placa', anchor='c')
    F.L.caption(266, 68, 'Fig.  —  SIGNA rev D, isometria da face de cima (LEDs, MCU, USB-C e S1 na borda de baixo).', width=138)
    F.set_box(M, 240, y=F.y, min_y=F.base_min_y)
    rows = [
        ['S1', 'Chave tátil lateral ALPS SKRTLAE010 (C110293) na borda de baixo (y = 0, girada 180°). Alterna OCUPADO/LIVRE à mão e entra em DFU se estiver apertada ao ligar o cabo.'],
        ['R5', '1 kΩ 0402 (C11702, basic) entre S1 e PA14. Proteção de corrente/ESD em série; isola o botão do SWD. Sem capacitor no nó (estragaria o SWD).'],
        ['TP1–TP3', 'Pads Ø1,0 mm na face de baixo, sem componente: TP1 VBUS, TP2 dado dos LEDs em 5 V, TP3 GND. Cama de pregos ou ponteira, sem soldar nada.'],
        ['LEDs', 'D1–D3 e C6–C8 deslocados +2,2 mm (y = 5,2 / 12,2 / 19,2). TC2030 (J2) em y = 8,7 e C2 em y = 21,4, para abrir espaço ao S1.'],
        ['Orelhas', 'Na ponta do USB: largura total 15,2 mm (±7,6 do eixo), 1,0 mm de altura, cantos externos r 0,3 e internos r 0,5. Batente axial contra a extração do cabo.'],
        ['Serigrafia', '« SIGNA rev D ». Título do esquema atualizado.'],
        ['Footprint S1', 'indicador:SW_SKRTLAE010_JLC com pads aparados: o da biblioteca deixava 0,099 mm entre furo NPTH e pad (a regra pede 0,25 mm).'],
        ['Vias', 'fix_vias.py no route.sh: o Freerouting deixava 2 vias com furo a 0,498 mm (aviso); agora ≥ 0,503 mm.'],
    ]
    F.tabela(['Item', 'Mudança'], rows, [46, 194], cont_larg=[60, 328],
             wrap_cols={1}, fonts=['Mono', 'Work'], size=6.2, cab_size=5.85)
    F.para('Avaliados e não feitos: toque capacitivo (o C071 não tem TSC; o caminho atravessaria ~7 mm de ar + PC) e sensor de luz ambiente (dentro do tubo opalino ele veria os próprios LEDs). MCU mantido no G8U6 (64 KB): o GBU6 está com estoque zero na JLC em 22/11/2026.')


def l_esquema(c, n, total, skip_images=False):
    L = Lamina(c, n, total, 'ESQUEMÁTICO', RODAPE, skip_images=skip_images)
    L.titulo('ESQUEMÁTICO  ·  SIGNA REV D')
    L.image_fit(JPG('esquematico'), M, 46, 388, 194, 'esquematico', anchor='c')
    L.caption(M, 38, 'Fig.  —  Esquemático gerado por tools/gen_sch.py a partir de tools/netlist.py (fonte única das ligações). Uma folha, KiCad 9.0.2.', width=388)
    return L


def l_pinagem(F):
    F.titulo('PINAGEM DO STM32C071G8U6  ·  UFQFPN-28  (versão GP, não N)')
    F.glossario('NC = não conectar. Pinos NC ficam no netlist como None e saem no PCB como unconnected-(U1-…). SWD e BOOT0 compartilham o PA14.')
    rows = [[str(p), nome, rede, nota] for p, nome, rede, nota in D.MCU_PINS]
    F.tabela(['Pino', 'Sinal (DS14693)', 'Rede', 'Função nesta placa'],
             rows, [24, 72, 62, 230],
             aligns=['c', 'l', 'l', 'l'],
             fonts=['Mono', 'Mono', 'Mono', 'Work'],
             wrap_cols={1, 2, 3}, size=6.2, cab_size=5.85)
    F.para('Fonte da pinagem: DS14693, figura do encapsulamento UFQFPN-28 versão GP (_GxU). A versão N (G8U6N / GBU6N) troca o pino 17 para VDDIO2 e não é substituta direta. USB nos pinos 18/19 é a atribuição padrão: o firmware não deve ligar o remapeamento PA9/PA10.')


def l_redes(F):
    F.titulo('REDES E ATRIBUIÇÃO DE PINOS  ·  DEMAIS COMPONENTES')
    F.glossario('Fonte: luxpcb-revD/tools/netlist.py, a fonte única do circuito (gen_sch.py e gen_pcb.py só consomem este arquivo).')
    rows = [
        ['J1 USB-C', 'S1,A1 GND  ·  A4 VBUS  ·  A5 CC1  ·  B5 CC2  ·  A7/B7 USB_DM  ·  A6/B6 USB_DP  ·  A8/B8 NC'],
        ['R1, R2 5,1 kΩ', 'R1: CC1–GND  ·  R2: CC2–GND  (identificação USB 2.0 / UFP)'],
        ['U4 USBLC6-2SC6', '1 e 6 USB_DP  ·  3 e 4 USB_DM  ·  5 VBUS  ·  2 GND'],
        ['C1 10 µF', 'VBUS–GND  (entrada)'],
        ['U2 AP2112K-3.3', '1 e 3 VBUS  ·  2 GND  ·  5 +3V3  ·  4 NC'],
        ['C2 1 µF', '+3V3–GND  (saída do LDO)'],
        ['C3 100 nF', '+3V3–GND  (desacoplo do MCU)'],
        ['C4 100 nF', 'NRST–GND'],
        ['U3 74AHCT1G125', '1 GND (OE, sempre habilitado)  ·  2 LED_DIN_3V3 (A)  ·  3 GND  ·  4 LED_DIN_5V (Y)  ·  5 VBUS'],
        ['C5 100 nF', 'VBUS–GND  (desacoplo do buffer)'],
        ['R3 33 Ω', 'LED_DIN_5V – LED1_DIN'],
        ['D1 WS2816B', '3 VBUS  ·  6 GND  ·  2 LED1_DIN (DI)  ·  1 GND (BI)  ·  4 LED2_DIN (DO)  ·  5 LED2_BIN (BO)'],
        ['D2 WS2816B', '3 VBUS  ·  6 GND  ·  2 LED2_DIN  ·  1 LED2_BIN  ·  4 LED3_DIN  ·  5 LED3_BIN'],
        ['D3 WS2816B', '3 VBUS  ·  6 GND  ·  2 LED3_DIN  ·  1 LED3_BIN  ·  4 e 5 NC (DO/BO livres)'],
        ['C6, C7, C8', '100 nF VBUS–GND ao lado de D1, D2 e D3'],
        ['J2 TC2030', '1 +3V3  ·  2 SWDIO  ·  3 NRST  ·  4 SWCLK_BOOT0  ·  5 GND  ·  6 NC  (face de baixo, sem componente)'],
        ['R4 1 kΩ', '+3V3 – BOOT_PU'],
        ['JP1', 'jumper de solda NA: BOOT_PU – SWCLK_BOOT0'],
        ['S1 SKRTLAE010', '1 BOOT_PU  ·  2 BTN'],
        ['R5 1 kΩ', 'BTN – SWCLK_BOOT0'],
        ['TP1 / TP2 / TP3', 'VBUS  ·  LED_DIN_5V  ·  GND  (pads Ø1,0 mm, face de baixo)'],
    ]
    F.tabela(['Ref.', 'Ligações (pino–rede)'], rows, [72, 316],
             fonts=['Mono', 'Work'], wrap_cols={1}, size=6.2, cab_size=5.85)


def l_potencia(F):
    F.titulo('ALIMENTAÇÃO E ORÇAMENTO DE CORRENTE')
    F.glossario('UFP = upstream-facing port (dispositivo). O LDO é o AP2112K-3.3TRG1 (C51118). Corrente do LED: datasheet WS2816B-2020.')
    L = F.L
    bloco(L, 16, 186, 72, 42, ['USB VBUS', '5 V'], title='ENTRADA')
    seta_linha(L, 88, 207, 108, 207)
    bloco(L, 108, 188, 70, 38, ['C1 10 µF'], title='FILTRO')
    seta_linha(L, 178, 214, 202, 224)
    seta_linha(L, 178, 198, 202, 176)
    bloco(L, 202, 206, 104, 36, ['LEDs D1–D3 + C6–8', 'U3 + C5  ·  U4'], title='RAIL 5 V')
    bloco(L, 202, 154, 104, 40, ['AP2112K-3.3', 'C2 1 µF, C3 100 nF'], title='LDO')
    seta_linha(L, 306, 174, 322, 174)
    bloco(L, 322, 154, 82, 40, ['MCU, J2, R4', 'C4 em NRST'], title='RAIL 3,3 V')
    F.y = 140
    F.rotulo('ORÇAMENTO  (estimativa de datasheet, a confirmar no 1.º lote)')
    rows = [
        ['Enumerado, LEDs apagados', '≈ 10–15 mA', '> 30 mA', 'MCU + LDO + LEDs em repouso < 0,8 mA cada'],
        ['Branco 100 % (R+G+B)', '≈ 70–80 mA', '> 100 mA', '3 × 20 mA (datasheet WS2816B) + MCU/LDO'],
        ['OCUPADO (só R, nível 1,0)', 'a medir', 'a definir', 'um canal por LED; menor que o branco 100 %'],
        ['LIVRE (nível 0,28) / IA 0,08', 'a medir', 'a definir', 'fração do PWM; fotometria e corrente a registrar'],
        ['Teto do descritor', '100 mA', '—', 'MaxPower do descritor de configuração; aceite de produção usa este teto'],
        ['Capa do conceito', '≤ 0,5 W a 5 V', '—', '= 100 mA, bate com o descritor'],
    ]
    F.tabela(['Estado', 'Esperado', 'Reprova se', 'Nota'],
             rows, [96, 58, 52, 182], wrap_cols={3},
             fonts=['Work', 'Mono', 'Mono', 'Work'], size=6.2, cab_size=5.85)
    F.para('Não há orçamento medido na rev D (nada rodou em silício). Os valores de apagado e branco vêm de teste.md do pacote Pendente, calculados pelos datasheets. A tensão de teste de produção é 5,00 V. O USB do computador deve fornecer pelo menos 100 mA; a prática comum de portas de 500 mA dá folga, mas o produto se declara como dispositivo de 100 mA.')


def l_leds(F):
    F.titulo('CADEIA DE LEDS E TEMPORIZAÇÃO  ·  WS2816B-2020')
    F.glossario('Fontes: arquitetura.md §2.4–2.5, README da rev D, datasheet WS2816B-2020. PWM do Flag original é 8 bit linear; no SIGNA as cores intermediárias ficam mais escuras (gamma 2,2).')
    F.para('Ligação (datasheet, « Typical Application Circuit »): U3.Y → R3 33 Ω → D1.DI; D1.BI = GND; Dn.DO → Dn+1.DI; Dn.BO → Dn+1.BI; D3.DO/BO livres. O primeiro LED da cadeia é D1 = LED 1 (baixo).')
    F.rotulo('QUADRO SPI  (SYSCLK 48 MHz, SPI1 a 12 MHz, palavras de 16 bit)', gap_before=2.0)
    rows1 = [
        ['0', '0xE000', '250 ns', '1 083 ns', 'T0H 200–320 ns, T0L 800–1 200 ns'],
        ['1', '0xFF00', '667 ns', '667 ns', 'T1H 520–800 ns, T1L 480–1 000 ns'],
        ['ciclo', '16 bit', '1,333 µs', '—', 'mínimo do datasheet: ≥ 1,25 µs'],
    ]
    F.tabela(['Bit', 'Palavra', 'Alto', 'Baixo', 'Datasheet WS2816B'],
             rows1, [32, 46, 48, 48, 214], fonts=['Mono', 'Mono', 'Mono', 'Mono', 'Work'], size=6.2, cab_size=5.85)
    rows2 = [
        ['Ordem no fio', 'G16 R16 B16, bit mais significativo primeiro (datasheet: « Data transmit in order of GRB, high bit data at first »)'],
        ['Quadro completo', '1 + 144 + 1 palavras = 195 µs  (3 LEDs × 48 bit → 144 palavras de 16 bit, mais sentinelas)'],
        ['Reenvio', 'no máximo a cada 2 ms, se a cor mudou e o DMA está livre; a linha fica > 1,8 ms em baixo (reset > 280 µs)'],
        ['Tolerância de relógio', 'HSI ±1 %: T0H 248–253 ns e T1H 660–673 ns. Folga de 48 ns até 200 ns e de 67 ns até 320 ns no T0H (aguenta cerca de ±20 % de erro)'],
        ['Buffer', 'O AHCT1G125 soma alguns ns de atraso de propagação e quase nada de distorção de largura. VIH ≥ 2 V com VCC 5 V; o WS2816 exige VIH ≥ 0,7×VDD = 3,5 V — por isso o buffer, e não um GPIO de 3,3 V direto.'],
        ['Protocolo 8→16 bit', 'R,G,B de 8 bit no HID; o motor guarda Q8.8, aplica nível do estado (Q12) e brilho global (0x12), e passa por gamma 2,2 (LUT de 257 pontos) antes dos 16 bit no fio.'],
        ['Validação pendente', 'Confirmar no silício: SPI sem intervalo entre palavras (R3) e a ordem GRB (01 FF FF 00 00 = vermelho).'],
    ]
    F.tabela(['Tema', 'Valor'], rows2, [84, 304], wrap_cols={1}, fonts=['Work', 'Work'], size=6.2, cab_size=5.85)


def l_usb(F):
    F.titulo('USB, ESD E PROTEÇÃO')
    F.glossario('Fontes: netlist.py, README rev D, teste.md, arquitetura.md §2.3. Impedância controlada do par USB: não feita, registrada como consideração — não é certificação.')
    F.L.image_fit(JPG('pcb_usb'), 266, 86, 138, 152, 'usb close', anchor='c')
    F.L.caption(266, 78, 'Fig.  —  Close-up do receptáculo HRO TYPE-C-31-M-12 (J1), CC e TVS.', width=138)
    F.set_box(M, 240, y=F.y, min_y=F.base_min_y)
    rows = [
        ['Receptáculo', 'HRO TYPE-C-31-M-12, LCSC C165948  ·  12 pinos, USB 2.0'],
        ['Saliência', 'USB-C sobressai 0,65 mm da placa (README rev D). A boca fica 0,40 mm acima da flange do berço.'],
        ['CC1 / CC2', 'R1 e R2 5,1 kΩ a GND: o computador reconhece um dispositivo USB 2.0 e liga o VBUS.'],
        ['Par D+/D−', 'J1 A6/B6 = USB_DP, A7/B7 = USB_DM, com USBLC6-2SC6 (U4, C7519) entre o conector e o MCU. Sem controle de impedância (Full Speed, trecho < 15 mm).'],
        ['TVS', 'USBLC6-2SC6, SOT-23-6: protege D+ e D−, referenciada a VBUS e GND. Não há TVS dedicado no botão (ver CHANGELOG).'],
        ['Enumeração', 'Full Speed, classe HID vendor, MaxPower 100 mA. Aceite: enumerar em < 2 s, sem erros no dmesg.'],
        ['DFU', 'Bootloader da ROM da ST, VID:PID 0483:df11, aparece com flash vazia ou com BOOT0 = 1 e nBOOT_SEL = 0.'],
    ]
    F.tabela(['Tema', 'Especificação'], rows, [56, 184], cont_larg=[76, 312], wrap_cols={1}, fonts=['Work', 'Work'], size=6.2, cab_size=5.85)
    F.para('Não há proteção de transiente no VBUS além da capacitância de entrada (C1 10 µF) e do próprio LDO. Inversão de polaridade não se aplica a um receptáculo USB-C com CC corretos. Sobrecorrente: o limite prático é o da porta do computador e o descritor de 100 mA.')


def l_botao(F):
    F.titulo('BOTÃO, BOOT0 E PONTOS DE TESTE')
    F.glossario('Fontes: CHANGELOG.md (ligação do botão, pendências de firmware) e netlist.py (TP1–TP3, R4, R5, JP1, S1, J2).')
    F.para('Caminho elétrico: +3V3 → R4 1 kΩ → rede BOOT_PU → S1 → rede BTN → R5 1 kΩ → PA14 (SWCLK/BOOT0). O R5 fica em paralelo com o JP1 (jumper de solda normalmente aberto).')
    rows = [
        ['Em uso (previsto)', 'O firmware lê o IDR de PA14 sem tirar o pino da função alternativa SWCLK. O pull-down interno do SWCLK mantém o nível baixo; botão apertado = nível alto (divisor 2 kΩ + pull-down). O SWD continua funcionando. Debounce sugerido: 30 ms; pressão longa sugerida: 2 s (gesto longo: a definir).'],
        ['Recuperação / DFU', 'Segurar o botão ao ligar o cabo põe BOOT0 em 1 e entra no DFU da ROM. Só vale com nBOOT_SEL = 0 (option byte, a gravar na produção).'],
        ['JP1', 'Continua no projeto: ponte de solda para puxar BOOT0 a 3V3 por R4, útil se o botão falhar ou para programação na bancada. Manter aberto ao depurar por SWD.'],
        ['SWD / debug', 'Tag-Connect TC2030-IDC-NL na face de baixo (J2). Durante o debug com a sonda conectada, o botão gera clocks espúrios: não apertar.'],
        ['Capacitor no nó', 'Propositadamente ausente: um capacitor em SWCLK estragaria o SWD.'],
        ['Implementação', 'Pendência do firmware: a leitura do botão ainda não está no código entregue (board.h da 0.1 não expõe a API; nada testado em silício).'],
        ['TP1 VBUS', 'Pad Ø1,0 mm, face de baixo, rede VBUS. Medir 5 V na cama de pregos.'],
        ['TP2 LED_DIN', 'Pad Ø1,0 mm, rede LED_DIN_5V (depois do buffer e antes/sobre o R3). Sonda de temporização dos bits.'],
        ['TP3 GND', 'Pad Ø1,0 mm, terra de referência.'],
    ]
    F.tabela(['Item', 'Descrição'], rows, [76, 312], wrap_cols={1}, fonts=['Work', 'Work'], size=6.2, cab_size=5.85)


def l_bom(F):
    F.titulo('BOM ELETRÔNICA  ·  PREÇOS E ESTOQUE JLC  (22/11/2026)')
    F.glossario('Fontes: signa-3d/bom/bom_completa.md, fab/bom.csv, docs/jlc_revD_2026-11-22.json, docs/parts-check.json, docs/estoque_stm32c071.json. « ext. » = biblioteca extended da JLC.')
    rows = [
        ['U1', 'STM32C071G8U6', 'C44521811', 'ext.', '109', '36', '1,800', '1,617'],
        ['D1–D3', 'WS2816B-2020 (×3)', 'C4154877', 'ext.', '2 818', '2 815', '0,222', '0,172'],
        ['J1', 'TYPE-C-31-M-12', 'C165948', 'ext.', '479 345', '461 430', '0,148', '0,104'],
        ['U2', 'AP2112K-3.3TRG1', 'C51118', 'ext.', '19 212', '19 815', '0,129', '0,094'],
        ['U3', 'SN74AHCT1G125DBVR', 'C7484', 'ext.', '37 449', '17 080', '0,089', '0,071'],
        ['U4', 'USBLC6-2SC6', 'C7519', 'ext.', '40 782', '39 405', '0,118', '0,084'],
        ['S1', 'SKRTLAE010', 'C110293', 'ext.', '69 662', '—', '0,116', '0,092'],
        ['C1', '10 µF 0603 X5R', 'C19702', 'basic', '9,8 M', '351 k', '0,017', '0,012'],
        ['C2', '1 µF 0402 X5R', 'C52923', 'basic', '9,1 M', '94 k', '0,005', '0,004'],
        ['C3–C8', '100 nF 0402 X7R (×6)', 'C1525', 'basic', '33 M', '2,5 M', '0,015', '0,009'],
        ['R1,R2', '5,1 kΩ 0402 (×2)', 'C25905', 'basic', '4,0 M', '817 k', '0,003', '0,002'],
        ['R3', '33 Ω 0402', 'C25105', 'basic', '4,4 M', '1,1 M', '0,001', '0,001'],
        ['R4,R5', '1 kΩ 0402 (×2)', 'C11702', 'basic', '29 M', '16 M', '0,002', '0,002'],
        ['PCB', '2 camadas 15,2×44×0,8, ENIG (est.)', '—', '—', '—', '—', '0,200', '0,060'],
        ['PCBA', 'SMT 1 face + 7 ext. (est.)', '—', '—', '—', '—', '0,505', '0,150'],
        ['FW', 'DFU + teste (est.)', '—', '—', '—', '—', '0,100', '0,050'],
    ]
    F.tabela(['Ref.', 'Componente', 'LCSC', 'Bib.', 'Est. JLC', 'Est. LCSC', 'US$ @100', 'US$ @1000'],
             rows, [32, 96, 50, 28, 46, 46, 45, 45],
             aligns=['l', 'l', 'l', 'c', 'r', 'r', 'r', 'r'],
             fonts=['Mono', 'Work', 'Mono', 'Work', 'Mono', 'Mono', 'Mono', 'Mono'],
             wrap_cols={1, 2}, size=6.0, cab_size=5.65)
    F.para('Componentes (só peças, sem PCB/PCBA/FW): US$ 2,67 @100  /  US$ 2,26 @1000.', gap=10.0)
    F.para('Eletrônica completa (com PCB, montagem e gravação, estimativa): US$ 3,47 @100  /  US$ 2,52 @1000.', gap=10.0)
    F.para('Delta rev C → rev D: +S1 +R5  ≈ +US$ 0,15/placa @100 e +US$ 0,10 @1000 (peças + rateio da taxa extended).', gap=10.0)
    F.para('Estoque do MCU: 109 un. na JLC e 36 na LCSC em 22/11/2026 (faixa US$ 1,80 @100, 1,62 @980 na JLC). Alternativa pino a pino STM32C071GBU6 (C42113261, 128 KB): estoque 0 na JLC, US$ 3,54 @100. Versões com sufixo N: estoque 0 e não são troca direta. Preços da S1: US$ 0,1437 @1, 0,1025 @150, 0,0922 @500, 0,0779 @3000 (jlc_revD_2026-11-22.json). R5 (C11702) é basic, US$ 0,0011 / 0,0009 @1000. Estoques de U2–U4, J1 e passivos: parts-check.json (consulta do dia; S1 entra pelo arquivo rev D).')


def l_layout(F):
    F.titulo('LAYOUT, STACKUP E REGRAS DE PROJETO')
    F.glossario('Fontes: luxflag.kicad_pro, luxflag.kicad_pcb, fab/gerber/luxflag-job.gbrjob, CHANGELOG.md. A placa é gerada por script (gen_pcb.py + route.sh); não é um layout « à mão » como fonte da verdade.')
    F.rotulo('GEOMETRIA E PILHA')
    rows1 = [
        ['Contorno', '15,25 × 44,05 mm no bounding box do Edge.Cuts (11 mm no corpo, 15,2 mm nas orelhas)'],
        ['Espessura', '0,80 mm  (KiCad thickness 0,8; job: BoardThickness 0,8)'],
        ['Camadas', '2  ·  F.Cu e B.Cu'],
        ['Cobre', '0,035 mm por face  (= 1 oz)  ·  job: MaterialStackup F.Cu / B.Cu'],
        ['Dielétrico', 'FR-4, 0,71 mm entre cobres'],
        ['Máscara', '0,01 mm por face  ·  cor: a definir (verde ou preta)'],
        ['Acabamento', 'README da rev D especifica ENIG; o luxflag-job.gbrjob está com Finish: "None"  ·  confirmar no pedido JLC'],
        ['Roteamento', 'Freerouting 2.1.0, -mt 1, MP=80  ·  342 trilhas, 24 vias  ·  depois fix_vias.py + limpeza + polígono de GND'],
        ['Vias', '24 vias, todas 0,60 mm de pad e 0,30 mm de furo (medido no luxflag.kicad_pcb)'],
        ['Largura padrão de trilha', '0,20 mm (defaults.copper_line_width do projeto)'],
    ]
    F.tabela(['Item', 'Valor'], rows1, [90, 298], wrap_cols={1}, fonts=['Work', 'Work'], size=6.2, cab_size=5.85)
    F.rotulo('REGRAS DO PROJETO KICAD  (design_settings.rules)', gap_before=2.0)
    rows2 = [
        ['Folga mínima entre cobres', '0,127 mm'],
        ['Largura mínima de trilha', '0,127 mm'],
        ['Folga cobre–borda', '0,30 mm'],
        ['Folga furo–cobre', '0,25 mm  (motivo do footprint próprio do S1: a biblioteca deixava 0,099 mm)'],
        ['Furo a furo', '0,50 mm'],
        ['Via mínima (pad / anel / furo)', '0,45 / 0,10 /  —   furo PTH mínimo 0,30 mm'],
        ['Job Gerber (regras « Outer »)', 'Pad–pad, pad–trilha e trilha–trilha 0,15 mm; MinLineWidth 0,20 mm; região 0,20 mm'],
        ['Par USB', 'sem regra de impedância controlada'],
    ]
    F.tabela(['Regra', 'Valor'], rows2, [104, 284], wrap_cols={1}, fonts=['Work', 'Work'], size=6.2, cab_size=5.85)


def l_anot_top(c, n, total, skip_images=False):
    L = Lamina(c, n, total, 'VISTA ANOTADA  ·  CIMA', RODAPE, skip_images=skip_images)
    L.titulo('VISTA ANOTADA  ·  FACE DE CIMA')
    L.image_fit(JPG('pcb_top'), M, 58, 224, 182, 'anot top', anchor='c')
    L.caption(M, 48, 'Fig.  —  Face de cima anotada (luxpcb-revD/renders/annotated_top.png). LEDs D1 (baixo) a D3 (topo) na coluna da frente.', width=224)
    L.image_fit(JPG('pcb_iso2'), 256, 134, 148, 106, 'iso2', anchor='c')
    L.image_fit(JPG('pcb_side'), 256, 82, 148, 44, 'side', anchor='c')
    L.caption(256, 72, 'Fig.  —  Isometria e perfil. USB-C sobressai 0,65 mm; S1 na borda de baixo.', width=148)
    return L


def l_anot_bot(c, n, total, skip_images=False):
    L = Lamina(c, n, total, 'VISTA ANOTADA  ·  BAIXO', RODAPE, skip_images=skip_images)
    L.titulo('VISTA ANOTADA  ·  FACE DE BAIXO')
    L.image_fit(JPG('pcb_bot'), M, 58, 224, 182, 'anot bot', anchor='c')
    L.caption(M, 48, 'Fig.  —  Face de baixo anotada (annotated_bottom.png). Depois de montada no berço, o J2 fica inacessível: gravar e testar a placa antes da montagem final.', width=224)
    L.image_fit(JPG('pcb_iso_back'), 256, 106, 148, 134, 'iso back', anchor='c')
    L.caption(256, 94, 'Fig.  —  Face de baixo: Tag-Connect J2 e pads de teste TP1 VBUS, TP2 LED_DIN_5V, TP3 GND (Ø1,0 mm).', width=148)
    return L


def l_closeups(F):
    F.titulo('CLOSE-UPS E CAMADAS DE COBRE')
    L = F.L
    L.image_fit(JPG('pcb_mcu'), M, 66, 124, 170, 'mcu', anchor='c')
    L.caption(M, 56, 'Fig.  —  MCU UFQFPN-28 e desacoplos.', width=124)
    L.image_fit(JPG('pcb_leds'), 148, 66, 124, 170, 'leds', anchor='c')
    L.caption(148, 56, 'Fig.  —  Cadeia D1–D3 e capacitores C6–C8.', width=124)
    L.image_fit(JPG('pcb_usb'), 280, 66, 124, 170, 'usb', anchor='c')
    L.caption(280, 56, 'Fig.  —  USB-C, CC, TVS e LDO.', width=124)

    F.next_page()
    L = F.L
    L.image_fit(JPG('cu_top'), M, 64, 68, 174, 'cu top', anchor='c')
    L.caption(M, 52, 'F.Cu', width=68)
    L.image_fit(JPG('cu_bot'), 92, 64, 68, 174, 'cu bot', anchor='c')
    L.caption(92, 52, 'B.Cu', width=68)
    L.image_fit(JPG('cu_both'), 168, 64, 68, 174, 'cu both', anchor='c')
    L.caption(168, 52, 'As duas faces.', width=68)
    L.image_fit(JPG('fab_top'), 244, 64, 68, 174, 'fab', anchor='c')
    L.caption(244, 52, 'Vista de fabricação (serigrafia + pads).', width=84)
    last = L.para(322, 224, 'Cobre gerado por copper_views.sh a partir dos Gerbers.', 'Work', 6.5, col=P['sec'], width=82, leading=9.2, tag='cu_nota1')
    L.para(322, last - 16, '24 vias visíveis no empilhamento.', 'Work', 6.5, col=L.ink, width=82, leading=9.2, tag='cu_nota2')


def l_ercdrc(F):
    F.titulo('VERIFICAÇÃO ELÉTRICA E DE PROJETO  ·  ERC E DRC')
    F.glossario('Os relatórios integrais estão no apêndice. erc.rpt e drc.rpt não devem ser « limpos à mão »: qualquer reedição da placa precisa regenerar os dois.')
    F.para('Relatórios gerados em 22/11/2026, 15:25 (America/Sao_Paulo), a partir do projeto KiCad 9 da rev D.')
    F.rotulo('ERC  ·  reports/erc.rpt')
    F.para('ERC messages: 0     Errors 0     Warnings 0', font='MonoM', size=7.6)
    F.rotulo('DRC  ·  reports/drc.rpt', gap_before=2.0)
    rows = [
        ['Erros', '0'],
        ['Pads não conectados', '0'],
        ['Erros de footprint', '0'],
        ['Pendências de roteamento', '0  ·  paridade OK'],
        ['Avisos', '1  ·  lib_footprint_mismatch no J1'],
    ]
    F.tabela(['Item', 'Resultado'], rows, [110, 278], fonts=['Work', 'Work'])
    F.para('O único aviso é: Footprint « USB_C_Receptacle_HRO_TYPE-C-31-M-12 » não coincide com a cópia na biblioteca Connector_USB, em (105,500 mm, 141,000 mm), referência J1. Classificado como « Local override; warning ». O CHANGELOG e o README registram que a serigrafia do USB-C foi editada de propósito, igual à rev C. Não é um erro de folga nem de ligação.')
    F.para('O roteamento passou pelo Freerouting 2.1.0 com MP=80. Com MP=100 ou 150 o arquivo SES perdia as redes da cadeia de LEDs (5 pendências). Depois rodam fix_vias.py (furos de via ≥ 0,503 mm até outro cobre) e a limpeza de trechos duplicados e pontas soltas.')


def l_fab(F):
    F.titulo('SAÍDAS DE FABRICAÇÃO E PARÂMETROS JLC')
    F.glossario('KiCad 9.0.2+dfsg-1 gerou o job em 22/11/2026, 15:09 (UTC−3). Projeto no job: « luxflag », revisão « rev? » — o campo de revisão do job não foi preenchido (detalhe a corrigir numa próxima exportação).')
    F.para('Pacote em luxpcb-revD/fab/: gerber.zip (e a pasta gerber/ descompactada), bom.csv e cpl.csv, gerados por tools/export_jlc.py. Esquemático em PDF: luxflag-schematic.pdf.')
    F.rotulo('ARQUIVOS GERBER  (luxflag-job.gbrjob)')
    rows1 = [
        ['luxflag-F_Cu.gtl', 'Cobre L1 (cima)', 'positiva'],
        ['luxflag-B_Cu.gbl', 'Cobre L2 (baixo)', 'positiva'],
        ['luxflag-F_Paste.gtp / B_Paste.gbp', 'Pasta de solda', 'positiva'],
        ['luxflag-F_Silkscreen.gto / B_Silkscreen.gbo', 'Serigrafia', 'positiva'],
        ['luxflag-F_Mask.gts / B_Mask.gbs', 'Máscara de solda', 'negativa'],
        ['luxflag-Edge_Cuts.gm1', 'Contorno', 'positiva'],
        ['luxflag-PTH.drl / NPTH.drl', 'Furação PTH e NPTH (Excellon)', '—'],
    ]
    F.tabela(['Arquivo', 'Função', 'Polaridade'], rows1, [126, 192, 70],
             fonts=['Mono', 'Work', 'Work'], wrap_cols={0, 1}, size=6.2, cab_size=5.85)
    F.rotulo('PARÂMETROS SUGERIDOS NO PEDIDO  (conferir na cotação)', gap_before=2.0)
    rows2 = [
        ['Camadas / espessura', '2 camadas, 0,8 mm'],
        ['Cobre', '1 oz (35 µm) nas duas faces'],
        ['Acabamento', 'ENIG  ·  a confirmar (o job está com Finish: None)'],
        ['Máscara / serigrafia', 'cor da máscara a definir; serigrafia branca é o padrão JLC'],
        ['Contorno', 'fresa (as orelhas não podem ser quebradas num V-cut mal posicionado)'],
        ['Montagem', 'SMT de uma face (todos os componentes estão em cima; J2 e TPs são só pads embaixo)'],
        ['Firmware na fábrica', 'não gravar  —  a gravação é interna, por DFU ou SWD (teste.md)'],
        ['Ferramental', 'estêncil + setup + taxa de peças extended (7 extended, cerca de US$ 3 por pedido cada, taxa pública JLC a conferir)'],
    ]
    F.tabela(['Parâmetro', 'Valor'], rows2, [96, 292], wrap_cols={1}, fonts=['Work', 'Work'], size=6.2, cab_size=5.85)


def l_painel(F):
    F.titulo('PAINELIZAÇÃO E PENDÊNCIAS DE FABRICAÇÃO')
    F.glossario('Não enviar a placa à JLC sem passar pela prévia de montagem (CPL/rotação) e sem decidir nBOOT_SEL, acabamento e painel.')
    F.para('Na rev A/C a placa tinha 11 mm de largura e podia ir num painel simples. Na rev D as orelhas da ponta do USB levam a largura local a 15,2 mm. Elas são estruturais: apoiam na flange do berço e recebem o esforço de extração do cabo (8–20 N). Se o V-cut ou a tab de painel passar por cima das orelhas, a peça chega sem batente axial.')
    rows1 = [
        ['Largura no corpo', '11,0 mm'],
        ['Largura nas orelhas', '15,2 mm  (±7,6 mm a partir do eixo)'],
        ['Altura da orelha', '1,0 mm  ·  cantos externos r 0,3  ·  internos r 0,5'],
        ['Bounding box Edge.Cuts', '15,25 × 44,05 mm'],
        ['Recomendação', 'Trilho ou tab fora das orelhas; preferir fresa do contorno a um V-cut que atravesse o ressalto. Painel a definir com o fabricante.'],
        ['Custo do PCB', 'A mudança 11×44 → 15,2×44 é estimada em +US$ 0,01 a 0,02 por placa no painel; não foi cotada de novo.'],
    ]
    F.tabela(['Tema', 'Valor'], rows1, [94, 294], wrap_cols={1}, fonts=['Work', 'Work'])
    F.rotulo('PENDÊNCIAS ANTES DO PEDIDO  (README E CHANGELOG)', gap_before=2.0)
    rows2 = [
        ['1', 'Conferir rotação do CPL na prévia da JLC (U1–U4, J1, D1–D3).'],
        ['2', 'Footprint do WS2816B-2020 foi desenhado pelo datasheet: conferir na prévia.'],
        ['3', 'BOOT0 (JP1 ou S1 ao ligar) só vale com nBOOT_SEL = 0; com flash vazia o chip entra em DFU sozinho.'],
        ['4', 'Pinos 18/19 = PA11[PA9]/PA12[PA10]: o firmware não deve ligar o remapeamento.'],
        ['5', 'Modelo 3D de U1, J1 e LEDs nos renders da placa são substitutos visuais (os da montagem integrada em signa-3d são modelos próprios).'],
        ['6', 'Par USB sem impedância controlada (Full Speed, < 15 mm).'],
        ['7', 'Estoque do STM32C071G8U6: 109 un. na JLC em 22/11/2026 — apertado para série; reservar ou consignar.'],
        ['8', 'Confirmiar ENIG e a cor da máscara no formulário do pedido (o job não traz o acabamento).'],
    ]
    F.tabela(['#', 'Pendência'], rows2, [22, 366], wrap_cols={1}, fonts=['Mono', 'Work'])
