"""Lâminas de firmware."""
from lib_metrologia import *
from helpers import *
import dados as D


def register(book):
    book.divisor('IV', 'FIRMWARE', [
        'STM32C071G8U6, TinyUSB, motor de animação em C puro, compatível com o protocolo HID do Luxafor Flag e com opcodes nativos 0x10–0x1F.',
        'Compila em 17 504 bytes de flash (de 62 KB úteis; 2 KB reservados para o serial). Testes de host com ASan e UBSan. Nada testado em silício.',
        'Pendências de produção: nBOOT_SEL = 0, leitura do botão, VID:PID definitivo e validação da ordem GRB e do SPI no hardware.',
    ], short='FIRMWARE')
    book.add_flow('IV  FIRMWARE', 'Arquitetura do firmware', l_arq)
    book.add_flow('IV  FIRMWARE', 'Laço principal e relógios', l_laco)
    book.add_flow('IV  FIRMWARE', 'Descritores USB', l_desc)
    book.add_flow('IV  FIRMWARE', 'Protocolo HID  ·  opcodes compatíveis', l_proto1, 'PROTOCOLO · COMPATÍVEL')
    book.add_flow('IV  FIRMWARE', 'Protocolo HID  ·  endereços, tempos, padrões', l_proto2, 'PROTOCOLO · TEMPOS')
    book.add_flow('IV  FIRMWARE', 'Protocolo HID  ·  opcodes nativos SIGNA', l_proto3, 'PROTOCOLO · NATIVO')
    book.add_flow('IV  FIRMWARE', 'NVM e número de série', l_nvm)
    book.add_flow('IV  FIRMWARE', 'DFU, option bytes e botão', l_dfu)
    book.add_flow('IV  FIRMWARE', 'Driver WS2816 e gamma', l_ws)
    book.add_flow('IV  FIRMWARE', 'Compilação e gravação', l_build)
    book.add_flow('IV  FIRMWARE', 'Testes de host e lacunas no silício', l_testes_fw, 'TESTES DE FIRMWARE')


def l_arq(F):
    F.titulo('ARQUITETURA DO FIRMWARE')
    F.glossario('Fonte: signa-sw/docs/arquitetura.md, Makefile, linker script e saída de arm-none-eabi-size sobre firmware/build/signa.elf.')
    F.para('O firmware é C11, sem RTOS, compilado com arm-none-eabi-gcc (testado com 14.2.1). O motor (engine.c) é C puro e também roda no PC, nos testes. Versão entregue: 0.1, de 22/11/2026. Identidade ainda rotulada « SIGNA rev C » em usb_ids.h e no README do software.')
    rows = [
        ['src/engine.c/.h', 'parser HID + motor de animação (C puro, sem hardware)', 'sim, tests/test_engine.c com ASan/UBSan'],
        ['src/signa_tables.c/.h', 'gerado por tools/gen_tables.py a partir de produto.json: gamma, respiração, estados', 'vetores Python × C'],
        ['src/ws2816.c e ws2816_encode.c', 'driver SPI1 + DMA1 e codificação dos bits', 'codificação e margens, tests/test_ws.c'],
        ['src/nvm_log.c / nvm.c', 'serial em flash com nivelamento de desgaste', 'sim, tests/test_nvm.c (inclui corte de energia)'],
        ['src/board.c/.h', 'relógios, SysTick, flash, option bytes', 'não (precisa da placa)'],
        ['src/usb_descriptors.c, usb_ids.h, tusb_config.h', 'identidade e descritores USB', 'não'],
        ['src/main.c', 'laço principal', 'não'],
    ]
    F.tabela(['Módulo', 'Papel', 'Testado no PC'], rows, [112, 166, 110],
             wrap_cols={0, 1, 2}, fonts=['Mono', 'Work', 'Work'], size=6.2, cab_size=5.85)
    F.para('Memória (ld/stm32c071g8.ld): 64 KB de flash em páginas de 2 KB, das quais 62 KB para o programa (0x08000000) e 2 KB para o NVM do serial (0x0800F800). RAM: 24 KB em 0x20000000, pilha mínima 0x600, heap 0. Tamanho medido no binário de 22/11/2026: text 17 460 + data 44 = 17 504 bytes de flash (coincide com signa.bin); data + bss = 4 912 bytes de RAM estática, mais 1 536 bytes de pilha reservada. O README do software cita « 2,9 KB de RAM » — o valor medido pelo arm-none-eabi-size é o desta tabela.')


def l_laco(F):
    F.titulo('LAÇO PRINCIPAL E RELÓGIOS')
    F.glossario('Fonte: arquitetura.md §2.2 e §2.3. « Um comando por transição »: as curvas rodam no aparelho e o USB fica quieto entre mudanças de estado.')
    L = F.L
    bloco(L, 16, 194, 104, 42, ['OUT 8 bytes', 'EP 0x01'], title='HOST')
    seta_linha(L, 120, 215, 142, 215)
    bloco(L, 142, 194, 120, 42, ['tud_task', 'engine_handle_report'], title='TinyUSB')
    seta_linha(L, 262, 215, 284, 215)
    bloco(L, 284, 194, 120, 42, ['fila IN:', '42, 00 01, eco'], title='RESPOSTA')
    seta_linha(L, 202, 194, 202, 180)
    bloco(L, 142, 136, 120, 44, ['engine_tick_1ms', 'a cada 1 ms (SysTick)'], title='MOTOR')
    seta_linha(L, 262, 158, 284, 158)
    bloco(L, 284, 136, 120, 44, ['engine_output16', 'a cada 2 ms se mudou'], title='WS2816')
    F.y = 122
    rows = [
        ['SYSCLK', 'HSISYS = HSI48 / 1 = 48 MHz (o reset deixa /4); 1 wait state'],
        ['USB', 'HSIUSB48 aparado pelo CRS a partir do SOF de 1 kHz, sem cristal. USBSEL = 0'],
        ['Pinos USB', 'PA11/PA12 (18/19), padrão do UFQFPN-28; não ligar o remapeamento PA9/PA10'],
        ['LEDs', 'PA7 (pino 13) = SPI1_MOSI AF0 + DMA (DMAMUX req 17), só transmissão, 12 MHz, palavras de 16 bit'],
        ['DMA', 'sem interrupção: o laço consulta TCIF1 e BSY'],
        ['Flash do serial', 'nvm_task no laço principal, nunca dentro do callback USB'],
        ['Tick', 'SysTick 1 ms avança o motor (fade, strobe, wave, padrões, curvas nativas)'],
    ]
    F.tabela(['Tema', 'Valor'], rows, [68, 320], wrap_cols={1}, fonts=['Work', 'Work'], size=6.2, cab_size=5.85)


def l_desc(F):
    F.titulo('DESCRITORES USB')
    F.glossario('Fontes: firmware/src/usb_descriptors.c, usb_ids.h, tusb_config.h e arquitetura.md §2.3 / §3.')
    rows = [
        ['bcdUSB', '0x0200  (USB 2.0)'],
        ['Classe do dispositivo', '0 (classe na interface)'],
        ['VID:PID padrão', '0x1209:0x0001  —  Test PID do pid.codes, só para desenvolvimento  ·  definitivo: a definir'],
        ['VID:PID USB_IDS=luxafor', '0x04D8:0xF372  —  só no protótipo pessoal; nunca em unidade vendida'],
        ['bcdDevice', '0x0001 no padrão SIGNA  ·  0x3C00 no modo luxafor'],
        ['iManufacturer / iProduct', '« SIGNA » / « SIGNA rev C »  (string do produto: a definir na próxima revisão)'],
        ['iSerial', '12 dígitos hex, derivados dos 6 bytes do serial (UID dobrado se não houver NVM)'],
        ['Configuração', '1 interface, MaxPower 100 mA, attributes 0 (alimentado pelo barramento)'],
        ['HID', 'página vendor 0xFF00, Usage 1, Collection Application'],
        ['Relatórios', 'Input 8 × uint8 e Output 8 × uint8, sem Report ID'],
        ['Endpoints', 'EP 0x01 OUT e 0x81 IN, interrupt, 8 bytes, intervalo 1 ms'],
        ['EP0', '64 bytes (CFG_TUD_ENDPOINT0_SIZE)'],
        ['Velocidade', 'Full Speed apenas (CFG_TUD_MAX_SPEED / RHPORT0_MODE)'],
        ['DFU (ROM)', '0483:df11, não faz parte deste descritor — é o bootloader de fábrica da ST'],
    ]
    F.tabela(['Campo', 'Valor'], rows, [90, 298], wrap_cols={1}, fonts=['Mono', 'Work'], size=6.2, cab_size=5.85)
    F.para('O descritor HID tem 33 bytes e reproduz o envelope do Flag. No Linux, o hidraw prefixa 0x00 (Report ID 0) na escrita; o firmware recebe os 8 bytes crus, opcode no byte 0. O app nunca envia endereço fora de {1, 2, 3, FF}.')


def l_proto1(F):
    F.titulo('PROTOCOLO HID  ·  OPCODES COMPATÍVEIS COM O FLAG')
    F.glossario('Fontes: PROTOCOLO.md (unidade original fw 0x3C), firmware_comportamento.md, arquitetura.md §3.1, engine.h. 0x05 e 0x07–0x0F não existem (varredura sistemática).')
    rows = [
        ['00', '00 …', '42', '—', 'ACK solto'],
        ['01', '01 alvo R G B', '42', '—', 'cor fixa, imediato'],
        ['02', '02 alvo R G B tempo', '42', 'sim (imediato se cor = atual ou tempo = 0)', 'fade; duração = max |dR,dG,dB| × tempo × 0,252 ms'],
        ['03', '03 alvo R G B tempo 00 rep', '42', 'sim, exceto rep = 0', 'strobe; rep × tempo × 65,5 ms, 50 % aceso; restaura a cor anterior'],
        ['04', '04 tipo R G B 00 rep vel', '42', 'só tipo 5', 'wave; ciclo ≈ vel × 65 ms; tipo fora de 1–5 = silêncio'],
        ['06', '06 id rep', '42', 'sim, exceto id 2', 'padrões 1–8; id 0 e 9+ = silêncio'],
        ['51', '51 b1…b6', 'eco', '—', 'grava 6 bytes do serial na NVM (fora do callback)'],
        ['52', '52 b1…b4', 'eco', '—', 'grava os 4 primeiros bytes do serial'],
        ['62', '62', '62 b1 b2 b3 b4', '—', 'lê os 4 primeiros bytes do serial atual'],
        ['80', '80', '80 3c s1 s2 s3 s4', '—', 'versão compatível (padrão 0x3C) + serial do boot'],
        ['05, 07–0F, demais', 'qualquer', 'silêncio', '—', 'opcodes inexistentes; não ACK'],
    ]
    F.tabela(['Op', 'Bytes', 'Resposta', 'Fim 00 01', 'Notas'],
             rows, [46, 76, 52, 74, 140], wrap_cols={0, 1, 2, 3, 4},
             fonts=['Mono', 'Mono', 'Mono', 'Work', 'Work'], size=6.1, cab_size=5.85)
    F.para('Qualquer comando novo de LED interrompe a animação em curso. Consultas 00, 62, 80 e 1F não interrompem. rep = 0 em strobe, wave e padrão = repetir até o próximo comando; sem evento de fim. Os padrões e as waves do clone são aproximações visuais do original: a temporização bate; a forma exata, não necessariamente.')


def l_proto2(F):
    F.titulo('PROTOCOLO HID  ·  ENDEREÇOS, TEMPOS E PADRÕES')
    F.glossario('A medida antiga « tempo 1 → 0,12 s » no fade 0→255 é o dobro da fórmula (≈ 0,064 s) e ficou como outlier. Wave tipos 1–4: descrições visuais no PROTOCOLO.md.')
    F.rotulo('ENDEREÇO DE LED  (byte 1)')
    rows1 = [
        ['01', 'LED 1, baixo (D1, primeiro da cadeia; zona da IA no modo misto)'],
        ['02', 'LED 2, meio (D2)'],
        ['03', 'LED 3, topo (D3)'],
        ['FF', 'todos'],
        ['04–06, 41, 42', 'ACK 42 e não acendem (herança do Flag de 6 LEDs). O clone nunca indexa um buffer com o valor cru.'],
        ['13 e demais', 'silêncio, sem efeito. No Flag original, 0x13 trava o firmware (OUT para de aceitar dados). O clone foi testado com os 256 valores e com fuzz de 200 mil relatórios.'],
    ]
    F.tabela(['Valor', 'Efeito'], rows1, [58, 330], wrap_cols={1}, fonts=['Mono', 'Work'], size=6.2, cab_size=5.85)
    F.rotulo('TEMPORIZAÇÃO DO FLAG ORIGINAL  (fw 0x3C)  —  O CLONE REPRODUZ', gap_before=2.0)
    rows2 = [
        ['Passo de fade', '0,252 ms × tempo por degrau de brilho', 'duração ≈ max(|dR|, |dG|, |dB|) × tempo × 0,252 ms'],
        ['Strobe (uma piscada)', '65,5 ms × tempo', 'no fim, restaura a cor anterior'],
        ['Wave tipo 5 (um ciclo)', '≈ 65 ms × vel', 'vel maior = mais lento; só o tipo 5 envia 00 01'],
        ['rep = 0', 'infinito', 'strobe, wave e padrão, até outro comando'],
        ['Padrão 1', '2,1 s / rep', 'semáforo: vermelho → vermelho+amarelo → verde'],
        ['Padrão 2', '3,6 s / ciclo, sem evento de fim', 'sobe um a um, fica branco, troca de cor e repete'],
        ['Padrão 3 / 4', '11,5 s / 15,8 s', 'arco-íris / 3 cores, forte e depois clareando'],
        ['Padrão 5 / 6 / 7 / 8', '0,9 / 2,6 / 1,35 / 3,5 s', 'polícia R/B; arco-íris→azul; verde→rosa→azul; arco-íris'],
        ['Padrões 0 e 9+', 'silêncio', 'no original não foram testados (risco de índice)'],
        ['PWM do original', '8 bit linear por canal', 'até o valor 1 acende, fraco'],
    ]
    F.tabela(['Fenômeno', 'Fórmula / valor', 'Notas'], rows2, [74, 108, 206],
             wrap_cols={1, 2}, fonts=['Work', 'Mono', 'Work'], size=6.2, cab_size=5.85)


def l_proto3(F):
    F.titulo('PROTOCOLO HID  ·  OPCODES NATIVOS SIGNA  (0x10–0x1F)')
    F.glossario('As curvas nativas são as mesmas de caderno.py::brilho_estado. ERRO a 2,5 Hz (período 0,4 s, pulso 130 ms) respeita WCAG 2.3.1. SIGNA_COMPAT_VERSION padrão: 0x3C.')
    F.para('A faixa 0x10–0x1F é silêncio no Flag original, portanto é segura para extensões. Estado inválido ou fora da zona certa = silêncio. Reenviar o mesmo estado não reinicia a fase da curva.')
    rows1 = [
        ['10', '10 estado', '42', 'os 3 LEDs mostram o estado'],
        ['11', '11 estado_sala estado_ia', '42', 'LED 3+2 = sala, LED 1 = IA; sala = OCUPADO trava os 3 em #FF3B2F'],
        ['12', '12 brilho', '42', 'escala global 0–255'],
        ['1F', '1F', "1F 'S' 'G' maj min proto nleds 00", 'identificação (hoje maj=0, min=1, proto=1, nleds=3)'],
    ]
    F.tabela(['Op', 'Bytes', 'Resposta', 'Efeito'], rows1, [24, 80, 92, 192],
             wrap_cols={2, 3}, fonts=['Mono', 'Mono', 'Mono', 'Work'], size=6.2, cab_size=5.85)
    F.rotulo('CÓDIGOS DE ESTADO', gap_before=2.0)
    rows2 = [[str(i), zona, nome, cor, curva] for i, nome, cor, curva, zona in D.ESTADOS_FW]
    F.tabela(['Cód.', 'Zona', 'Nome', 'Cor', 'Curva no firmware'],
             rows2, [24, 30, 66, 38, 230],
             fonts=['Mono', 'Work', 'Work', 'Mono', 'Work'],
             wrap_cols={2, 4}, size=6.2, cab_size=5.85)


def l_nvm(F):
    F.titulo('NVM E NÚMERO DE SÉRIE')
    F.glossario('Fontes: arquitetura.md §2.6, nvm_log.c, PROTOCOLO.md (comandos 51/52/62 e o incidente do serial). Não gravar NVM em aparelhos do Lucas sem pedir.')
    rows = [
        ['Região', 'última página da flash, 0x0800F800, 2 KB, fora do .text no linker (região NVM)'],
        ['Registro', "16 bytes: 'S' 'G' | seq | serial[6] | crc16 | 00000000"],
        ['Nivelamento', '128 gravações por apagamento da página'],
        ['Corte de energia', 'gravação interrompida fica inválida (CRC) e vale a anterior — coberto por tests/test_nvm.c'],
        ['Sem registro', 'serial = 6 bytes do UID de 96 bit dobrados (único por chip); iSerial = 12 dígitos hex'],
        ['0x51', 'grava 6 bytes (eco dos argumentos, como no original)'],
        ['0x52', 'grava os 4 primeiros bytes (eco)'],
        ['0x62', 'lê o valor atual (4 primeiros bytes)'],
        ['0x80 e descritor', 'mostram a cópia carregada no boot, não o valor escrito depois do boot'],
        ['Idempotência', 'gravação igual à atual não toca a flash'],
        ['Onde grava', 'no laço principal (nvm_task), nunca no callback USB'],
        ['Incidente no original', 'o iSerial do Flag de engenharia reversa era 000000002498 e virou 000000000000 durante os testes de NVM — motivo para tratar 0x51/0x52 com respeito e pedir confirmação antes de gravar NVM em unidades reais'],
    ]
    F.tabela(['Tema', 'Valor'], rows, [76, 312], wrap_cols={1}, fonts=['Work', 'Work'], size=6.2, cab_size=5.85)


def l_dfu(F):
    F.titulo('DFU, OPTION BYTES E BOTÃO')
    F.glossario('Fontes: docs/README.md do software, CHANGELOG da rev D, arquitetura.md §2.7, AN2606/DS14693 (option bytes, não reproduzidos aqui além do que o projeto documenta).')
    rows = [
        ['Chip novo (flash vazia)', 'o bootloader da ROM entra sozinho em DFU, 0483:df11'],
        ['Depois da 1.ª gravação', 'o JP1 (ou o botão S1 ao ligar) só devolve o DFU se nBOOT_SEL = 0 nos option bytes'],
        ['nBOOT_SEL = 0', 'o pino BOOT0 (PA14) passa a decidir: aberto/solto → firmware; fechado/apertado ao ligar → bootloader da ROM'],
        ['nBOOT1', 'deixar em 1 (padrão), para que BOOT0 = 1 escolha o bootloader da ROM'],
        ['Como gravar o option byte', 'STM32_Programmer_CLI -c port=SWD -ob nBOOT_SEL=0  (Tag-Connect)  ou  -c port=usb1  (no próprio DFU da 1.ª gravação). Conferir com -ob displ'],
        ['Alternativa de firmware', 'make AUTO_NBOOT_SEL=1: o firmware zera só esse bit no 1.º boot (o resto do OPTR é regravado igual). Padrão da compilação: não mexe'],
        ['Botão em uso', 'leitura prevista do IDR de PA14 sem sair de AF SWCLK; ainda é pendência de implementação'],
        ['Botão ao ligar', 'segura S1, pluga o cabo → BOOT0 = 1 → DFU, desde que nBOOT_SEL = 0'],
        ['SWD', 'TC2030-IDC-NL, pinos 1 VCC, 2 SWDIO, 3 nRESET, 4 SWCLK, 5 GND, 6 NC. Manter JP1 aberto e não apertar o botão durante o debug'],
        ['OpenOCD', 'a release 0.12.0 (2023) não reconhece o STM32C071. Usar um build com o commit 250ab10 (jan. 2025) ou mais novo, ou o STM32CubeProgrammer'],
    ]
    F.tabela(['Tema', 'Valor'], rows, [80, 308], wrap_cols={1}, fonts=['Work', 'Work'], size=6.2, cab_size=5.85)


def l_ws(F):
    F.titulo('DRIVER WS2816 E GAMMA')
    F.glossario('Fontes: arquitetura.md §2.4–2.5, ws2816_encode.c, datasheet WS2816B-2020. A captura lógica do Flag original é opcional e não bloqueia esta implementação.')
    F.para('O protocolo no fio USB continua com R, G, B de 8 bit (compatibilidade com o Flag e com software antigo). Dentro do aparelho a cor é Q8.8, o nível do estado é Q12 e o brilho global (opcode 0x12) escala o resultado. Uma LUT de gamma 2,2 com 257 pontos e interpolação gera os 16 bit enviados ao WS2816B. O fade do 0x02 interpola em 16 bit, então não deve haver degraus visíveis.')
    F.para('Compatibilidade de aparência: o Flag original é PWM linear de 8 bit. No SIGNA, cores intermediárias ficam mais escuras, de propósito (lei de Stevens / sRGB). Isso está documentado na §6 da especificação de comportamento e na arquitetura §2.5. Não é um defeito, mas é uma diferença visível lado a lado com um Flag.')
    rows = [
        ['Codificação', 'bit 0 = 0xE000 (250 ns alto), bit 1 = 0xFF00 (667 ns alto), ciclo 1,333 µs'],
        ['Ordem', 'G16 R16 B16, MSB primeiro; D1 primeiro na cadeia = LED 1 (baixo)'],
        ['Validação pendente', '01 FF FF 00 00 tem de acender vermelho; se acender verde, a ordem está trocada em ws2816_encode.c'],
        ['Osciloscópio no R3', 'sem intervalo entre palavras do SPI; T0H ≈ 250 ns, T1H ≈ 667 ns'],
        ['Reset', 'linha baixa > 280 µs; na prática > 1,8 ms entre quadros'],
        ['PWM do LED', '10 kHz no WS2816B (elimina cintilação no verde/âmbar, limite do SK6805 a ~1 kHz usado na rev B da placa)'],
    ]
    F.tabela(['Tema', 'Valor'], rows, [76, 312], wrap_cols={1}, fonts=['Work', 'Work'], size=6.2, cab_size=5.85)


def l_build(F):
    F.titulo('COMPILAÇÃO E GRAVAÇÃO')
    F.glossario('Toolchain: arm-none-eabi-gcc 14.2.1 (pacote gcc-arm-none-eabi do Debian 13). Nunca aplicar USBDEVFS_RESET no PC do Lucas — se o USB travar, pedir para replugar o cabo.')
    F.rotulo('COMPILAR')
    F.code_lines([
        'cd firmware',
        'tools/fetch_deps.sh        # TinyUSB, cmsis-device-c0, CMSIS 5',
        'make                       # build/signa.elf, .bin, .hex',
        'make test                  # testes de host (gcc, ASan + UBSan)',
        'make tables                # regenera tabelas se produto.json mudou',
        'make USB_IDS=luxafor       # 04d8:f372, só protótipo pessoal',
        'make AUTO_NBOOT_SEL=1      # zera nBOOT_SEL no 1.º boot',
    ])
    F.rotulo('GRAVAR POR DFU', gap_before=2.0)
    F.code_lines([
        'dfu-util -l                                   # deve listar 0483:df11',
        'make flash-dfu                                # -s 0x08000000:leave -D build/signa.bin',
    ])
    F.para('Linux: regra udev em app/examples/99-signa.rules para gravar sem root. Windows: WinUSB no 0483:df11 (Zadig) ou STM32CubeProgrammer (traz o driver).')
    F.rotulo('GRAVAR POR SWD', gap_before=2.0)
    F.code_lines([
        'make flash-swd     # openocd … program build/signa.elf verify reset exit',
        'STM32_Programmer_CLI -c port=SWD -w build/signa.hex -v -rst',
    ])
    F.rotulo('PRIMEIRO TESTE NA PLACA  (CHECKLIST DO README)', gap_before=2.0)
    rows = [
        ['1', 'lsusb mostra 1209:0001 SIGNA rev C, serial de 12 dígitos hex (derivado do UID).'],
        ['2', 'signa-cli devices responde « SIGNA nativo ».'],
        ['3', '01 FF FF 00 00 acende vermelho. Se acender verde, trocar a ordem em ws2816_encode.c.'],
        ['4', 'Analisador ou osciloscópio no R3: bit 0 ≈ 250 ns alto, bit 1 ≈ 667 ns, sem intervalo entre palavras.'],
        ['5', 'ERRO pisca a 2,5 Hz (câmera lenta: 12 piscadas em 4,8 s).'],
    ]
    F.tabela(['#', 'Verificação'], rows, [22, 366], wrap_cols={1}, fonts=['Mono', 'Work'])


def l_testes_fw(F):
    F.titulo('TESTES DE HOST E LACUNAS NO SILÍCIO')
    F.glossario('Contagens de teste: arquitetura.md §7 e README do software, estado em 22/11/2026.')
    rows = [
        ['Motor (tests/test_engine.c)', '262 verificações: temporização de fade, strobe, wave e padrão, endereços, serial, fuzz, curvas, modo misto e gamma'],
        ['NVM (tests/test_nvm.c)', '2 005 verificações, inclusive corte de energia no meio da gravação'],
        ['WS2816 (tests/test_ws.c)', '16 verificações de codificação e margens de temporização'],
        ['Sanitizers', 'ASan e UBSan ligados nos testes de host'],
        ['Integração com o app', 'o app conversa com o mesmo engine.c compilado como biblioteca, no caminho nativo e no fallback Luxafor'],
        ['Não testado', 'nada em silício: USB real, CRS, SPI/DMA, gravação de flash, option bytes, botão, óptica e corrente'],
    ]
    F.tabela(['Conjunto', 'Cobertura'], rows, [96, 292], wrap_cols={1}, fonts=['Work', 'Work'], size=6.2, cab_size=5.85)
    F.para('O firmware 0.1 ainda não implementa a leitura do botão S1 (pendência explícita do CHANGELOG da rev D). Até isso entrar, OCUPADO/LIVRE manual só existe pelo aplicativo, e o DFU pelo botão depende apenas do nível de BOOT0 no instante da alimentação — o que já é um comportamento de hardware/option byte, não do firmware de aplicação.')
    F.para('Não usar reset de software USB (USBDEVFS_RESET) no computador do Lucas: essa operação já travou o kernel e forçou um reboot. Se um teste HID travar o dispositivo, pedir o replugue físico do cabo.')
