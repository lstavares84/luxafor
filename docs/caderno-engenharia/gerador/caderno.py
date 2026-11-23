#!/usr/bin/env python3
"""Gera signa-engenharia.pdf (A3 paisagem, sistema visual Metrologia Luminosa).
Caderno de engenharia do SIGNA — continuação do caderno conceitual.
Uso: python3 prep_imagens.py && python3 caderno.py && python3 preview.py 110
"""
import io, os, sys, json, math
from reportlab.pdfgen import canvas as rcanvas
from lib_metrologia import *
from helpers import *
import dados as D

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'signa-engenharia.pdf')
NOME = D.produto['nome']
VERM = D.modos['sala_ocupado']['hex']


class Book:
    def __init__(self):
        self.items = []  # dicts: sec, title, fn, short, noite, kind ('page'|'div'|'flow')

    def add(self, sec, title, fn, short=None, noite=False):
        self.items.append({
            'sec': sec, 'title': title, 'fn': fn,
            'short': (short or title).upper(),
            'noite': noite, 'kind': 'page',
        })

    def add_flow(self, sec, title, fn, short=None, noite=False):
        self.items.append({
            'sec': sec, 'title': title, 'fn': fn,
            'short': (short or title).upper(),
            'noite': noite, 'kind': 'flow',
        })

    def divisor(self, num, title, linhas, short=None):
        def fn(c, n, total, skip_images=False):
            return pagina_divisor(c, n, total, num, title, linhas, skip_images=skip_images)
        self.items.append({
            'sec': f'{num}  {title}', 'title': f'{num}  {title}',
            'fn': fn, 'short': (short or title).upper(),
            'noite': True, 'kind': 'div',
        })


def pagina_divisor(c, n, total, num, title, linhas, skip_images=False):
    L = Lamina(c, n, total, title.upper(), RODAPE, noite=True, skip_images=skip_images)
    L.text(M, 224, num, 'JuraL', 28, L.ink, cs=5.0, tag='capnum')
    L.text(M, 188, title, 'JuraL', 18.0, L.ink, cs=1.4, tag='captitle')
    L.rect(M, 176, 60, 1.0, fill=VERM)
    y = 156
    for i, ln in enumerate(linhas):
        last = L.para(M, y, ln, 'Work', 8.1, width=368, leading=11.6, tag=f'div{i}')
        y = last - 13.5
    L.text(M, 31.5, f"{DOC_ID}  ·  REV. {DOC_REV}  ·  {DOC_DATA}", 'JuraM', 6.9, L.ink, cs=0.6)
    return L


# =====================================================================================
# Frente
# =====================================================================================
def l_capa(c, n, total, skip_images=False):
    L = Lamina(c, n, total, 'CAPA', RODAPE, noite=True, skip_images=skip_images)
    L.image_fit(JPG('capa_uso'), 236, 48, 168, 208, 'render capa', anchor='c')
    last = L.para(M, 260, 'CADERNO DE ENGENHARIA  ·  METROLOGIA LUMINOSA', 'JuraM', 7.2, L.ink, width=212, leading=9.6, tag='subcapa')
    s = NOME
    size, cs = 25.0, 4.5
    while L.width(s, 'JuraL', size, cs) > 208:
        size -= 0.5
    L.text(M, 210, s, 'JuraL', size, L.ink, cs=cs, tag='nome')
    L.text(M, 198, D.produto['nome_nota'].upper(), 'Mono', 5.8, L.ink, tag='prov')
    L.rect(M, 190, 72, 1.0, fill=VERM)
    L.nota(M, 173, 'especificações, medidas e instruções', size=9.8, col=L.ink)
    L.nota(M, 160, 'para quem vai fabricar e operar.', size=9.8, col=L.ink)
    L.italicos -= 1
    y = 142
    for k, v in [
        ('DOCUMENTO', f'{DOC_ID}  REV. {DOC_REV}'),
        ('DATA', DOC_DATA),
        ('PLACA', 'rev D  ·  STM32C071G8U6'),
        ('MECÂNICA', 'rev B  ·  P01 a P06 + cabo'),
        ('FIRMWARE / APP', '0.1  ·  17,5 KB de flash'),
        ('PÚBLICO', 'engenharia (HW, FW, mecânica, teste)'),
        ('CONTINUAÇÃO', 'caderno conceitual de 14 lâminas'),
    ]:
        L.text(M, y, k, 'JuraM', 6.45, L.ink, cs=0.25)
        v_lines = L.wrap(v, 'Mono', 6.45, 146)
        yy = y
        for vl in v_lines:
            L.text(M + 64, yy, vl, 'Mono', 6.45, L.ink)
            yy -= 8.5
        div_y = yy + 8.5 - 3.0
        L.line(M, div_y, M + 210, div_y, P['borda'], 0.14)
        y = div_y - 6.8
    L.text(M, 29.5, 'VALORES NÃO MEDIDOS APARECEM COMO  A DEFINIR', 'JuraM', 6.3, L.ink, cs=0.25)
    L.caption(236, 40, f'render do conjunto integrado · SALA: {D.modos["sala_ocupado"]["nome"]} {VERM}', width=168, size=5.8)
    return L


def l_controle(F):
    F.titulo('CONTROLE DO DOCUMENTO', 'METROLOGIA LUMINOSA')
    F.glossario('Fontes: luxpcb-revD, signa-3d, signa-sw, PROTOCOLO.md, FUNCIONAMENTO.md, caderno conceitual, pacote Pendente rev A.')
    F.rotulo('IDENTIFICAÇÃO')
    rows = [
        ('Documento', f'{DOC_ID}'),
        ('Título', 'SIGNA — caderno de engenharia'),
        ('Revisão', f'{DOC_REV}  ·  {DOC_DATA}'),
        ('Idioma', 'português do Brasil'),
        ('Formato', 'A3 paisagem (420 × 297 mm), sistema visual Metrologia Luminosa'),
        ('Público', 'engenharia de hardware, firmware, mecânica, manufatura e teste'),
        ('Continuação de', 'caderno conceitual SIGNA (14 lâminas, mesmo sistema visual)'),
        ('Placa', 'SIGNA rev D  ·  KiCad 9.0.2  ·  gerada em 22/11/2026'),
        ('Mecânica', 'SIGNA rev B  ·  conjunto integrado PCB + corpo + cabo'),
        ('Software', 'firmware 0.1 e app 0.1  ·  22/11/2026  ·  nada testado em silício'),
        ('Classificação', 'uso interno de projeto  ·  não é certificação nem dossiê de ANATEL/CE/FCC'),
    ]
    F.kv_list(rows, key_w=72, k_size=6.6, v_size=6.6, gap=3.5, line_div=True, v_font='Work')
    F.rotulo('REVISÕES', gap_before=4.0)
    F.tabela(['Rev.', 'Data', 'Descrição'],
             [['0', '22/11/2026', 'Primeira emissão: placa rev D, mecânica rev B, firmware/app 0.1.']],
             [30, 62, 296], aligns=['c', 'c', 'l'], wrap_cols={2})
    F.rotulo('REGRAS DE LEITURA', gap_before=4.0)
    for t in [
        'Nenhum número deste caderno foi inventado. O que não está nas fontes aparece como « a definir » e está reunido na seção de pendências.',
        'Cotações de mecânica, cabo, embalagem e montagem são estimativas de ordem de grandeza (ver BOM). Só a eletrônica tem preço consultado na API da JLCPCB em 22/11/2026.',
        'O pacote do Pendente rev A (montagem, materiais, teste) é a base do processo; onde a rev B/D altera a geometria (orelhas, botão P06, cabo, berço e tampão), vale o que está em signa-3d e luxpcb-revD.',
        'Considerações de conformidade (USB, EMC, fotossensibilidade, RoHS) não são certificações. Nada neste caderno substitui ensaio de laboratório.',
        'Unidades: milímetros, milissegundos, volts e ampères. Decimais no padrão brasileiro (vírgula). Projeção dos desenhos: 1.º diedro (NBR 10067). Tolerância geral dos desenhos: ISO 2768-mK, salvo cota indicada.',
    ]:
        F.para(t)


def _sumario_entry_height(L_probe, entry, col_w=186):
    sec, title, page, kind = entry
    txt_w = col_w - 22.0
    if kind == 'div':
        lines = L_probe.wrap(title, 'JuraM', 7.2, txt_w, cs=0.3)
        return len(lines) * 9.5 + 7.5
    else:
        lines = L_probe.wrap(title, 'Work', 6.45, txt_w)
        return len(lines) * 8.6 + 2.8


def l_sumario_factory(cols_pair, parte):
    def fn(c, n, total, skip_images=False):
        L = Lamina(c, n, total, 'SUMÁRIO', RODAPE, skip_images=skip_images)
        top_y = L.titulo(f'SUMÁRIO  ·  {parte}', 'MAPA DO DOCUMENTO')
        col_w = 186.0
        gap = 16.0
        x0 = M
        for col, chunk in enumerate(cols_pair):
            x = x0 + col * (col_w + gap)
            y = top_y
            for sec, title, page, kind in chunk:
                txt_w = col_w - 22.0
                if kind == 'div':
                    if y < top_y - 2:
                        y -= 3.5
                    L.text(x, y, f'{page:02d}', 'Mono', 6.6, L.sec)
                    lines = L.wrap(title, 'JuraM', 7.2, txt_w, cs=0.3)
                    yy = y
                    for ln in lines:
                        L.text(x + 22, yy, ln, 'JuraM', 7.2, L.ink, cs=0.3)
                        yy -= 9.5
                    line_y = yy + 9.5 - 3.0
                    L.line(x, line_y, x + col_w, line_y, L.ink, 0.25)
                    y = line_y - 8.0
                    continue
                L.text(x, y, f'{page:02d}', 'Mono', 6.45, L.sec)
                lines = L.wrap(title, 'Work', 6.45, txt_w)
                yy = y
                for ln in lines:
                    L.text(x + 22, yy, ln, 'Work', 6.45, L.ink)
                    yy -= 8.6
                y = yy - 2.8
        L.glossario('A numeração é contínua. Cada lâmina traz régua, marcas de registro e o rodapé SIGNA · CADERNO DE ENGENHARIA · REV. 0.')
        return L
    return fn


# =====================================================================================
# I  SISTEMA
# =====================================================================================
def l_visao(F):
    F.titulo('VISÃO GERAL DO SISTEMA')
    F.glossario('HID = Human Interface Device  ·  VBUS = 5 V do USB  ·  envelope e massas: signa-3d/README e verificacao_montagem.')
    F.L.image_fit(JPG('iso'), 256, 72, 148, 168, 'iso conjunto', anchor='c')
    F.L.caption(256, 62, 'Fig.  —  Conjunto integrado: PCB rev D + corpo P01–P06 + cabo USB-C (signa_conjunto).', width=148)
    F.set_box(M, 230, y=F.y, min_y=F.base_min_y)
    for t in [
        'O SIGNA é uma luz de status USB-C para mesa ou monitor. A sala vê se você está livre, prestes a entrar em uma reunião ou ocupado. Opcionalmente, e só quando você liga essa função, a mesma luz acompanha Claude, ChatGPT e Grok.',
        'O aparelho pendura pelo próprio cabo. Não tem parafuso nem cola: a placa rev D desliza no berço, as orelhas travam o esforço de extração do USB-C, o tubo fica preso entre a tampa de alumínio e o tampão, e um pino (P06) aciona a chave tátil na borda de baixo.',
        'No computador, um aplicativo lê o Google Calendar e o Outlook, resolve a escada de prioridade e envia um relatório HID de 8 bytes. O firmware, no STM32C071G8U6, é compatível com o protocolo do Luxafor Flag (engenharia reversa de 2026-11) e acrescenta opcodes nativos de estado (0x10–0x1F). As curvas (respiração, pulso, estrobo, pulso duplo) rodam no aparelho: o USB fica quieto entre as transições.',
        'Este caderno documenta o produto que se pretende fabricar: a placa rev D, a mecânica rev B, o firmware e o aplicativo 0.1. O firmware compila (17 504 bytes de flash) e passa nos testes de host; o aplicativo tem 32 testes passando. Nada foi testado ainda no silício da rev D.',
    ]:
        F.para(t)
    F.rotulo('ENVELOPE', gap_before=4.0)
    F.kv_list([
        ('Corpo', 'Ø19 × 78 mm  (88,2 mm com a bota do passa-cabo)'),
        ('Massa', '≈ 20 g sem o cabo (estimativa de volume × densidade)'),
        ('Placa', '11 × 44 mm  (15,2 mm nas orelhas), FR-4 0,8 mm, 2 camadas, 1 oz'),
        ('Luz', '3 × WS2816B-2020  ·  16 bit/canal  ·  PWM 10 kHz'),
        ('Interface', 'USB-C  ·  HID vendor 0xFF00  ·  8+8 bytes  ·  Full Speed  ·  100 mA'),
        ('Alimentação', 'só VBUS 5 V  ·  consumo estimado ≤ ≈ 70–80 mA no branco 100 %'),
    ], key_w=72, k_size=6.5, v_size=6.5, line_div=False)


def l_blocos(F):
    F.titulo('DIAGRAMA DE BLOCOS')
    F.glossario('Fontes: signa-sw/docs/arquitetura.md, luxpcb-revD/README.md e CHANGELOG.md. O firmware ainda não lê o botão no silício (pendência).')
    L = F.L
    L.rotulo(M, 236, 'COMPUTADOR  (Windows, macOS, Linux)')
    bloco(L, 16, 190, 92, 38, ['Google', 'Calendar API'], title='AGENDA')
    bloco(L, 114, 190, 92, 38, ['Microsoft', 'Graph'], title='AGENDA')
    bloco(L, 212, 190, 92, 38, ['CLI, bandeja,', 'atalho'], title='MANUAL')
    bloco(L, 310, 190, 94, 38, ['Claude Code,', 'Codex, extensão'], title='IA  (opt-in)')
    for ax in (62, 160, 258, 357):
        seta_linha(L, ax, 190, ax, 180)
    bloco(L, 16, 148, 388, 32, ['Motor de prioridade  ·  um comando HID por transição'], title='APLICATIVO SIGNA')
    seta_linha(L, 210, 148, 210, 138)
    bloco(L, 80, 100, 260, 38, ['HID 8 bytes  ·  EP 01 / 81  ·  1 ms', 'opcodes 01–06, 10–12, 1F, 51/52/62, 80'], title='USB FULL SPEED')
    L.rotulo(M, 88, 'APARELHO  SIGNA  (rev D)')
    bloco(L, 16, 42, 118, 38, ['STM32C071G8U6', 'TinyUSB + motor'], title='MCU  48 MHz')
    seta_linha(L, 134, 61, 151, 61)
    bloco(L, 151, 42, 118, 38, ['SN74AHCT1G125', '3,3 V → 5 V'], title='BUFFER')
    seta_linha(L, 269, 61, 286, 61)
    bloco(L, 286, 42, 118, 38, ['3 × WS2816B-2020', 'G16 R16 B16'], title='LEDs')
    seta_linha(L, 175, 100, 75, 80)

    F.next_page()
    F.rotulo('NOTAS')
    notas = [
        'A agenda e o modo manual alimentam o estado da sala. A IA só entra se o usuário ligar a opção (opt-in).',
        'Em modo misto, os LEDs 3 e 2 mostram a sala e o LED 1 mostra a IA. Se a sala está OCUPADO, os três LEDs travam em vermelho #FF3B2F (v1, não configurável).',
        'O dado dos LEDs sai no PA7 (pino 13) por SPI1 + DMA, atravessa o buffer e o R3 de 33 Ω, e entra em D1.DI. D1 é o LED de baixo.',
        'USB em PA11/PA12 (pinos 18 e 19), pinagem padrão do UFQFPN-28. Não ligar o remapeamento para PA9/PA10.',
        'Alimentação: VBUS 5 V nos LEDs, no buffer e no LDO AP2112K-3.3, que gera +3V3 para o MCU.',
        'O botão S1 (ALPS SKRTLAE010) na borda de baixo alterna OCUPADO/LIVRE em uso e, se estiver apertado ao ligar o cabo, pede o DFU da ROM — só com nBOOT_SEL = 0.',
    ]
    for t in notas:
        F.para(t)


def l_requisitos(F):
    F.titulo('REQUISITOS E ESPECIFICAÇÕES')
    F.glossario('Fontes: README e CHANGELOG da rev D, teste.md do Pendente, datasheet WS2816B-2020, caderno conceitual (especificações da capa).')
    F.rotulo('ELÉTRICAS')
    rows1 = [
        ['Alimentação', 'VBUS 5 V apenas (sem bateria, sem fonte externa)'],
        ['Descritor USB MaxPower', '100 mA  (100 unidades de 2 mA, Full Speed)'],
        ['Consumo apagado (est.)', '≈ 10–15 mA  ·  reprovação se > 30 mA  (a confirmar no 1.º lote)'],
        ['Consumo branco 100 % (est.)', '≈ 70–80 mA (3 × 20 mA nos LEDs + MCU/LDO)  ·  reprovação se > 100 mA'],
        ['Orçamento da capa do conceito', '≤ 0,5 W a 5 V (datasheet)'],
        ['LDO', 'AP2112K-3.3  ·  +3V3 para o MCU'],
        ['Proteção USB', 'USBLC6-2SC6 em D+/D−  ·  CC1/CC2 com 5,1 kΩ a GND'],
        ['ESD no botão', 'sem TVS dedicado; R5 1 kΩ em série  ·  caminho de fuga ≈ 6 mm até o cobre (P06 isolante)'],
    ]
    F.tabela(['Item', 'Especificação'], rows1, [104, 284], wrap_cols={1}, fonts=['Work', 'Work'])
    F.rotulo('ÓPTICAS', gap_before=2.0)
    rows2 = [
        ['Emissores', '3 × WS2816B-2020 (Worldsemi), 16 bit/canal, gamma interna 4 bit, PWM 10 kHz'],
        ['Corrente por LED', '20 mA com R+G+B no máximo (datasheet)'],
        ['Difusão', 'tubo PC opalino Ø16/13; distância LED–difusor 7,27 mm (altura real do LED 0,84 mm)'],
        ['Estados', '8 estados visuais na escada de prioridade; ver lâminas de estados. ERRO a 2,5 Hz (pulso 130 ms), abaixo do limite WCAG 2.3.1 de 3 Hz'],
        ['Aceite qualitativo', 'branco 100 % a 0,5 m: sem pontos quentes visíveis; ponta inferior (tampão) também acesa'],
        ['Fotometria (cd, lx)', 'a definir  —  não medida'],
    ]
    F.tabela(['Item', 'Especificação'], rows2, [104, 284], wrap_cols={1}, fonts=['Work', 'Work'])


def l_requisitos2(F):
    F.titulo('REQUISITOS E ESPECIFICAÇÕES  ·  MECÂNICA E USB')
    F.glossario('MaxPower 100 mA é o valor do descritor, não o limite de 500 mA de um dispositivo USB 2.0 de alta potência. O aceite de produção reprova acima de 100 mA.')
    F.rotulo('MECÂNICAS')
    rows1 = [
        ['Envelope', 'Ø19 × 78 mm  ·  88,2 mm com a bota do passa-cabo  ·  o botão P06 sai 0,3 mm abaixo do tampão'],
        ['Massa', '≈ 20 g sem cabo (tubo 3,94 + tampa 10,97 + berço 2,10 + tampão 0,95 + passa-cabo 0,97 + botão 0,06 + placa ≈ 1,0)'],
        ['Fixação', 'nenhum parafuso nem cola; encaixes e press-fit (tampão ≈ 20–40 N, pacote Pendente)'],
        ['Retenção da placa', 'orelhas 15,2 mm apoiam nas fendas da flange (Z = 50,75) e ficam 0,25 mm abaixo do ressalto da tampa'],
        ['Cabo C01', 'USB-C ↔ USB-C, 1,5 m, USB 2.0; casca exposta ≥ 5,8 mm; sobremolde ≤ 11,6 × 6,4 mm; capa Ø3,5–4,0 mm'],
        ['Extração do cabo', 'teste de aceite: 10 N por 5 s, o plugue não sai e a tampa não se solta (força típica de extração USB-C 8–20 N)'],
        ['Botão', 'ALPS SKRTLAE010, 1,6 N; P06 em PC opalino, curso nominal 0,60 mm (0,40 de folga + 0,20 elétrico), pior caso 1,00 mm'],
        ['Tolerância geral', 'ISO 2768-mK nos desenhos, salvo cota indicada'],
    ]
    F.tabela(['Item', 'Especificação'], rows1, [104, 284], wrap_cols={1}, fonts=['Work', 'Work'])
    F.rotulo('USB E AMBIENTE', gap_before=2.0)
    rows2 = [
        ['Velocidade', 'USB 2.0 Full Speed apenas (sem SuperSpeed, sem áudio, sem carregamento rápido)'],
        ['Classe', 'HID, página vendor 0xFF00, 8 bytes IN + 8 bytes OUT, sem Report ID'],
        ['Endpoints', 'EP 0x81 IN e 0x01 OUT, interrupt, intervalo 1 ms, MaxPower 100 mA'],
        ['VID:PID (dev)', '1209:0001  —  Test PID do pid.codes, só para desenvolvimento  ·  definitivo: a definir'],
        ['bcdUSB / bcdDevice', '0x0200  ·  0x0001 no padrão SIGNA  (0x3C00 se compilado com USB_IDS=luxafor)'],
        ['DFU de fábrica', 'bootloader da ROM, 0483:df11, endereço 0x08000000'],
        ['Ambiente (T, UR, IP, queda)', 'a definir  —  uso previsto: interior, mesa ou monitor, alimentado pelo USB do computador'],
        ['Ensaios de durabilidade', 'vida do botão, flexão do cabo, ciclos de inserção USB-C: a definir'],
    ]
    F.tabela(['Item', 'Especificação'], rows2, [104, 284], wrap_cols={1}, fonts=['Work', 'Work'])


def l_estados_sala(F):
    F.titulo('ESTADOS DA SALA')
    F.glossario('Imagens do caderno conceitual (lâmina 5). Fórmulas das curvas: caderno.py::brilho_estado = firmware signa_tables. OCUPADO não é configurável no v1.')
    L = F.L
    imgs = [
        ('p5_sala_livre', 'LIVRE', '#2FD28A', 'prioridade 7  ·  contínuo 0,28', 'pode interromper'),
        ('p5_sala_prestes', 'PRESTES A ENTRAR', '#FF8A1A', 'prioridade 2  ·  pulso 3,0 s', 'aviso padrão: 5 min, configurável no app'),
        ('p5_sala_ocupado', 'OCUPADO', '#FF3B2F', 'prioridade 1  ·  contínuo 1,0', 'trava os 3 LEDs (0xFF); a IA some no v1'),
    ]
    xs = [16, 148, 280]
    for x, (img, nome, hx_c, sinal, nota) in zip(xs, imgs):
        L.image_fit(JPG(img), x, 102, 124, 138, img, anchor='c')
        L.rect(x, 89, 10, 5.5, fill=hx_c)
        L.text(x + 14, 90, nome, 'JuraM', 6.9, L.ink, cs=0.3)
        L.para(x, 78, sinal, font='Mono', size=5.8, col=L.sec, width=124, leading=8.0, tag='sinal')
        L.para(x, 60, nota, font='Work', size=6.0, col=L.ink, width=124, leading=8.4, tag='nota_est')

    F.next_page()
    F.rotulo('FONTES E REGRAS DA SALA')
    F.para(
        'A sala é o modo principal. Fontes: Google Calendar e Microsoft Graph / Outlook, mais comando manual (CLI, bandeja ou atalho) e, no futuro, sensor de chamada (microfone/câmera: a definir por sistema operacional).'
    )
    F.para(
        '« Prestes a entrar » usa lead_minutes, padrão 5 minutos, configurável no aplicativo. Eventos cancelados, recusados, marcados como livre, de dia inteiro (se ignore_all_day) e do tipo local de trabalho são ignorados; « talvez » conta como ocupado (tentative_is_busy, configurável).'
    )


def l_estados_ia(F):
    F.titulo('ESTADOS DA IA  ·  MODO MISTO')
    F.glossario('ERRO a 2,5 Hz está abaixo do limite WCAG 2.3.1 (3 Hz). LIMITE diferencia a janela de 5 h (pulso duplo) do teto semanal (contínuo 0,28) no mesmo LED. IA é opt-in.')
    grupos = [
        [
            ('p5_ia_livre', 'IA DESOCUPADA', '#7C8EA6', 'prio. 8  ·  fixo 0,08'),
            ('p5_ia_processando', 'PROCESSANDO', '#3D8BFF', 'prio. 5  ·  respiração 2,4 s'),
            ('p5_ia_atencao', 'PRECISA DE ATENÇÃO', '#FFE02E', 'prio. 4  ·  quadrada 1 Hz'),
        ],
        [
            ('p5_ia_erro', 'ERRO', '#FF3FC8', 'prio. 3  ·  2,5 Hz / 130 ms'),
            ('p5_ia_limite', 'LIMITE ATINGIDO', '#9B5CFF', 'prio. 6  ·  5 h ou semanal'),
            ('p5_misto', 'MODO MISTO', '#1B1E21', 'LEDs 3+2 sala  ·  LED 1 IA'),
        ],
    ]
    xs = [16, 148, 280]
    for idx_g, grp in enumerate(grupos):
        if idx_g > 0:
            F.next_page()
        L = F.L
        for x, (img, nome, hx_c, sinal) in zip(xs, grp):
            L.image_fit(JPG(img), x, 92, 124, 148, img, anchor='c')
            L.rect(x, 79, 10, 5.5, fill=hx_c if hx_c != '#1B1E21' else P['tinta'])
            n_lines = L.wrap(nome, 'JuraM', 6.8, 110, cs=0.25)
            yy = 80
            for nl in n_lines:
                L.text(x + 14, yy, nl, 'JuraM', 6.8, L.ink, cs=0.25)
                yy -= 9.0
            sig_y = min(65, yy - 3)
            L.para(x, sig_y, sinal, font='Mono', size=5.8, col=L.sec, width=124, leading=8.0, tag='sinal_ia')


def l_prioridade(F):
    F.titulo('ESCADA DE PRIORIDADE E MODOS DE EXIBIÇÃO')
    F.glossario('Fonte: signa-sw/docs/arquitetura.md §4 e data/produto.json. O teste tests/test_engine.py cobre todas as combinações sala × IA nos modos escada e misto.')
    rows = []
    for i, m in enumerate(D.MODOS_PRIO, 1):
        rows.append([str(i), m['grupo'].upper(), m['nome'], m['hex'], m['sinal'], m['leds']])
    F.tabela(['Prio.', 'Modo', 'Estado', 'Cor', 'Comportamento', 'LEDs'],
             rows, [22, 28, 68, 36, 124, 110],
             aligns=['c', 'l', 'l', 'l', 'l', 'l'],
             fonts=['Mono', 'Work', 'WorkM', 'Mono', 'Work', 'Mono'],
             size=6.2, cab_size=5.85, wrap_cols={2, 4, 5})
    F.rotulo('RESOLUÇÃO NO APLICATIVO', gap_before=2.0)
    for t in [
        'Se há um comando manual ativo, a sala usa esse valor (com prazo opcional, p. ex. —por 45m). Senão, a agenda decide: dentro do evento → OCUPADO; começa em até N minutos → PRESTES A ENTRAR; caso contrário → LIVRE.',
        'Se a IA está desligada ou o modo de exibição é « sala », o aparelho recebe 0x10 com o estado da sala nos 3 LEDs.',
        'Se a IA está ligada, o estado da IA é o mais forte entre as fontes e sessões: ERRO > ATENÇÃO > PROCESSANDO > LIMITE 5 h > LIMITE semanal > DESOCUPADA. No modo misto o aparelho recebe 0x11 (sala, IA). No modo escada, recebe 0x10 com o vencedor da escada global desta tabela.',
        'Validade dos relatos de IA (configurável): PROCESSANDO sem sinal por 15 min vira DESOCUPADA; ERRO dura 10 min; LIMITE 5 h dura 5 h; LIMITE semanal dura 24 h — até chegar outro evento.',
    ]:
        F.para(t)


def l_identidade(F):
    F.titulo('IDENTIDADE E NOMENCLATURA')
    F.glossario('INPI = Instituto Nacional da Propriedade Industrial. O nome não deve ser tratado como marca registrada até a busca e o depósito.')
    rows = [
        ['Nome', 'SIGNA  ·  provisório, a verificar no INPI'],
        ['Documentos', 'SIGNA-ENG-001 (este caderno)  ·  caderno conceitual anexo de origem'],
        ['Placa', 'LXE-E01  ·  rev D  ·  projeto KiCad luxflag'],
        ['Conjunto mecânico', 'LXP-A00  ·  rev B'],
        ['Peças de plástico / metal', 'LXP-P01 tubo  ·  P02 tampa  ·  P02b tampa impressa (protótipo)  ·  P03 berço  ·  P04 tampão  ·  P05 passa-cabo  ·  P06 botão'],
        ['Cabo', 'C01  USB-C ↔ USB-C 1,5 m  ·  C02 adaptador USB-A (opcional, decisão em aberto)'],
        ['Firmware', '0.1  ·  identificador nativo 0x1F: "SG" + maj min proto nleds'],
        ['Compatibilidade', 'protocolo HID do Luxafor Flag, firmware original 0x3C, VID:PID 04d8:f372 — só como referência; não usar esse par em produto vendido'],
    ]
    F.tabela(['Campo', 'Valor'], rows, [86, 302], wrap_cols={1}, fonts=['Work', 'Work'])
    F.rotulo('ORIENTAÇÃO DO PRODUTO', gap_before=2.0)
    for t in [
        'LED 1 = baixo = D1 (primeiro da cadeia) = zona da IA no modo misto. LED 2 = meio = D2. LED 3 = topo = D3. No desenho e no CAD, o USB-C aponta para cima (passa-cabo na tampa) e o botão para baixo (tampão).',
        'A face da frente é a que aponta para a sala (LEDs voltados ao tubo). A face de trás, mais escura, fica contra o monitor. Isso é aceitável no critério de aceite, desde que não apareça uma linha escura nítida.',
        'Serigrafia da placa: « SIGNA rev D ». O descritor USB ainda diz « SIGNA rev C » — a definir na próxima revisão de software.',
    ]:
        F.para(t)
    # fotos de uso (garantir espaço de 130 mm ou nova página)
    F.need(135)
    y_bot = F.min_y + 18.0
    h_img = min(132.0, F.y - y_bot - 6.0)
    F.L.image_fit(JPG('livre'), M, y_bot, 186, h_img, 'livre uso', anchor='c')
    F.L.image_fit(JPG('em_uso'), M + 202, y_bot, 186, h_img, 'ocupado uso', anchor='c')
    F.L.caption(M, y_bot - 8.0, 'Fig.  —  Em uso no monitor: LIVRE (#2FD28A) e OCUPADO (#FF3B2F).', width=388)


# =====================================================================================
# Registro e execução em dois passos (contagem/sumário + geração)
# =====================================================================================
def registrar():
    b = Book()
    b.add('FRENTE', 'Capa', l_capa, short='CAPA', noite=True)
    b.add_flow('FRENTE', 'Controle do documento', l_controle, short='CONTROLE DO DOCUMENTO')
    b.divisor('I', 'SISTEMA', [
        'O SIGNA é o produto; este capítulo descreve o que ele é, como os blocos se ligam, o que precisa cumprir e como os estados se organizam.',
        'As lâminas de estados retomam o recorte visual da lâmina 5 do caderno conceitual, agora com a escada de prioridade e os modos de exibição que o firmware implementa.',
    ], short='SISTEMA')
    b.add_flow('I  SISTEMA', 'Visão geral do sistema', l_visao)
    b.add_flow('I  SISTEMA', 'Diagrama de blocos', l_blocos)
    b.add_flow('I  SISTEMA', 'Requisitos e especificações', l_requisitos, short='REQUISITOS')
    b.add_flow('I  SISTEMA', 'Requisitos  ·  mecânica e USB', l_requisitos2, short='REQUISITOS · MECÂNICA')
    b.add_flow('I  SISTEMA', 'Estados da sala', l_estados_sala)
    b.add_flow('I  SISTEMA', 'Estados da IA e modo misto', l_estados_ia, short='ESTADOS · IA E MISTO')
    b.add_flow('I  SISTEMA', 'Escada de prioridade e modos', l_prioridade, short='ESCADA DE PRIORIDADE')
    b.add_flow('I  SISTEMA', 'Identidade e nomenclatura', l_identidade)
    from laminas.eletronica import register as r2
    from laminas.mecanica import register as r3
    from laminas.firmware import register as r4
    from laminas.aplicativo import register as r5
    from laminas.operacao import register as r6
    from laminas.conformidade import register as r7
    from laminas.anexos import register as r8
    r2(b); r3(b); r4(b); r5(b); r6(b); r7(b); r8(b)
    return b


def _expand_item(item, c, start_n, total, skip_images, emit_pages):
    kind = item['kind']
    if kind == 'flow':
        F = Flow(c, start_n, total, item['sec'], item['title'],
                 short=item['short'], noite=item['noite'],
                 skip_images=skip_images, emit_pages=emit_pages)
        item['fn'](F)
        pages, probs = F.finish()
        return pages, probs
    else:
        L = item['fn'](c, start_n, total, skip_images=skip_images)
        probs = L.verifica()
        out_probs = [(start_n, item['title'], probs)] if probs else []
        if emit_pages:
            c.showPage()
        return [{
            'sec': item['sec'], 'title': item['title'],
            'short': item['short'], 'noite': item['noite'],
            'kind': kind, 'page': start_n,
        }], out_probs


def _pack_sumario(entries, L_probe):
    """Empacota entradas do sumário em páginas de 2 colunas respeitando altura real."""
    col_top = 242.0
    col_min_y = 46.0
    max_col_h = col_top - col_min_y  # ~196 mm por coluna
    col_w = 186.0

    chunks_cols = []
    cur_col = []
    cur_h = 0.0
    cols_list = []

    for e in entries:
        eh = _sumario_entry_height(L_probe, e, col_w)
        pre = 3.5 if (e[3] == 'div' and cur_col) else 0.0
        if cur_col and cur_h + pre + eh > max_col_h:
            cols_list.append(cur_col)
            cur_col = [e]
            cur_h = eh
        else:
            cur_col.append(e)
            cur_h += pre + eh
    if cur_col:
        cols_list.append(cur_col)

    pages = []
    for i in range(0, len(cols_list), 2):
        c1 = cols_list[i]
        c2 = cols_list[i + 1] if i + 1 < len(cols_list) else []
        pages.append([c1, c2])
    return pages


def build_and_render(out_path):
    b = registrar()
    dummy_c = rcanvas.Canvas(io.BytesIO(), pagesize=(W * MM, H * MM))
    L_probe = Lamina(dummy_c, 1, 1, 'PROBE', RODAPE, skip_images=True)

    # Passo 1: expandir frente (capa + controle) e conteúdo para contar páginas
    frente_items = b.items[:2]
    cont_items = b.items[2:]

    frente_pages = []
    cur_n = 1
    for it in frente_items:
        pgs, _ = _expand_item(it, dummy_c, cur_n, 999, skip_images=True, emit_pages=False)
        for p in pgs:
            p['kind'] = it['kind']
        frente_pages.extend(pgs)
        cur_n += len(pgs)

    n_frente = len(frente_pages)
    cont_raw_pages = []
    for it in cont_items:
        pgs, _ = _expand_item(it, dummy_c, cur_n, 999, skip_images=True, emit_pages=False)
        for p in pgs:
            p['kind'] = it['kind']
        cont_raw_pages.extend(pgs)
        cur_n += len(pgs)

    # Iterar ponto fixo para número de páginas de sumário
    n_sumario = 4
    sum_pages_cols = []
    for _ in range(8):
        base = n_frente + n_sumario
        entries = []
        for idx, p in enumerate(cont_raw_pages):
            pg = base + idx + 1
            entries.append((p['sec'], p['title'], pg, p['kind']))
        sum_pages_cols = _pack_sumario(entries, L_probe)
        if len(sum_pages_cols) == n_sumario:
            break
        n_sumario = len(sum_pages_cols)

    total = n_frente + n_sumario + len(cont_raw_pages)

    # Passo 2: render real
    c = rcanvas.Canvas(out_path, pagesize=(W * MM, H * MM))
    from lib_metrologia import GLIFOS_FALTANDO
    GLIFOS_FALTANDO.clear()

    problemas = []
    sumario_final = []
    cur_n = 1

    for it in frente_items:
        pgs, probs = _expand_item(it, c, cur_n, total, skip_images=False, emit_pages=True)
        for p in pgs:
            sumario_final.append((p['title'], p['page']))
        problemas.extend(probs)
        cur_n += len(pgs)

    for i, cols_pair in enumerate(sum_pages_cols):
        parte = f'{i + 1} / {len(sum_pages_cols)}'
        sfn = l_sumario_factory(cols_pair, parte)
        L = sfn(c, cur_n, total, skip_images=False)
        probs = L.verifica()
        if probs:
            problemas.append((cur_n, f'Sumário {i + 1}', probs))
        c.showPage()
        sumario_final.append((f'Sumário {i + 1}', cur_n))
        cur_n += 1

    for it in cont_items:
        pgs, probs = _expand_item(it, c, cur_n, total, skip_images=False, emit_pages=True)
        for p in pgs:
            sumario_final.append((p['title'], p['page']))
        problemas.extend(probs)
        cur_n += len(pgs)

    c.save()
    return total, problemas, sumario_final


def main():
    total, problemas, sumario = build_and_render(OUT)
    ver = {
        'paginas': total,
        'arquivo': OUT,
        'problemas': [{'pagina': p, 'titulo': t, 'itens': pr} for p, t, pr in problemas],
        'glifos_faltando': GLIFOS_FALTANDO,
        'sumario': sumario,
    }
    json.dump(ver, open(os.path.join(HERE, 'verificacao.json'), 'w'), ensure_ascii=False, indent=2)
    print(f'{OUT}  ·  {total} páginas  ·  {len(problemas)} páginas com avisos  ·  {len(GLIFOS_FALTANDO)} glifos')
    for p, t, pr in problemas[:40]:
        print(f'  p.{p:02d} {t}:')
        for x in pr[:8]:
            print('    ', x)
        if len(pr) > 8:
            print(f'     … +{len(pr)-8}')
    if GLIFOS_FALTANDO:
        print('glifos:')
        for g in GLIFOS_FALTANDO[:20]:
            print(' ', g)


if __name__ == '__main__':
    main()
