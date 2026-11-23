"""Apêndices: BOM completa, CPL, relatórios, glossário."""
from lib_metrologia import *
from helpers import *
import dados as D
VERM = D.modos["sala_ocupado"]["hex"]


def register(book):
    book.divisor('VIII', 'APÊNDICES', [
        'BOM completa do produto, arquivo de posições (CPL), relatórios ERC/DRC na íntegra e um glossário dos termos deste caderno.',
        'Os números destas páginas são os mesmos das fontes; se divergirem de uma lâmina anterior, valem as fontes e este apêndice deve ser corrigido.',
    ], short='APÊNDICES')
    book.add_flow('VIII  APÊNDICES', 'BOM completa  ·  eletrônica', l_bom1, 'APÊNDICE · BOM ELETR.')
    book.add_flow('VIII  APÊNDICES', 'BOM completa  ·  mecânica e resto', l_bom2, 'APÊNDICE · BOM REST.')
    book.add_flow('VIII  APÊNDICES', 'Arquivo de posições (CPL)', l_cpl)
    book.add_flow('VIII  APÊNDICES', 'Relatórios ERC e DRC', l_relatorios)
    book.add_flow('VIII  APÊNDICES', 'Glossário', l_glossario)
    book.add('VIII  APÊNDICES', 'Colofão', l_colofao, noite=True)


def _fmt(v):
    try:
        x = float(v)
        return br(x, 3 if abs(x) < 10 else 2)
    except Exception:
        return str(v) if v is not None else '—'


def l_bom1(F):
    F.titulo('APÊNDICE  ·  BOM COMPLETA  ·  ELETRÔNICA')
    F.glossario('Fonte: signa-3d/bom/bom_completa.csv. Valores em US$ por produto. Status « verificado » refere-se ao preço/estoque do dia 22/11/2026; PCB/PCBA/FW são estimativa.')
    rows = []
    for r in D.bom_prod:
        cat = (r.get('categoria') or r.get('Cat.') or '').strip()
        if cat.lower().startswith('eletr'):
            item = r.get('item') or r.get('Item') or ''
            desc = r.get('descricao') or r.get('Descrição') or ''
            pn = r.get('part_number') or r.get('Part number') or ''
            q = r.get('qtd_por_unidade') or r.get('Qtd') or ''
            c100 = r.get('custo_usd_por_produto_lote100') or r.get('US$ @100') or ''
            c1000 = r.get('custo_usd_por_produto_lote1000') or r.get('US$ @1000') or ''
            st = r.get('status') or r.get('Status') or ''
            rows.append([item, desc, pn, str(q), _fmt(c100), _fmt(c1000), st])
    if not rows:
        F.para('Não foi possível ler as linhas de eletrônica de bom_completa.csv com os nomes de coluna esperados. Ver o arquivo em signa-3d/bom/bom_completa.csv e a tabela da seção II.')
    else:
        F.tabela(['Item', 'Descrição', 'Part number', 'Qtd', '@100', '@1000', 'Status'],
                 rows, [26, 90, 74, 22, 43, 43, 90],
                 aligns=['l', 'l', 'l', 'c', 'r', 'r', 'l'],
                 fonts=['Mono', 'Work', 'Mono', 'Mono', 'Mono', 'Mono', 'Work'],
                 wrap_cols={1, 2, 6}, size=6.0, cab_size=5.7)


def l_bom2(F):
    F.titulo('APÊNDICE  ·  BOM COMPLETA  ·  MECÂNICA, CABO, EMBALAGEM, MONTAGEM')
    F.glossario('P02b e F02 não entram no total do produto. Ferramental aparece como item FERR no lote 1 000. C02 (adaptador) entra no total até decisão em contrário.')
    rows = []
    for r in D.bom_prod:
        cat = (r.get('categoria') or '').strip()
        if cat.lower().startswith('eletr'):
            continue
        item = r.get('item') or ''
        desc = r.get('descricao') or ''
        q = r.get('qtd_por_unidade') or ''
        c100 = r.get('custo_usd_por_produto_lote100') or ''
        c1000 = r.get('custo_usd_por_produto_lote1000') or ''
        st = r.get('status') or ''
        rows.append([cat, item, desc, str(q), _fmt(c100), _fmt(c1000), st])
    F.tabela(['Cat.', 'Item', 'Descrição', 'Qtd', '@100', '@1000', 'Status'],
             rows, [46, 26, 104, 22, 43, 43, 104],
             aligns=['l', 'l', 'l', 'c', 'r', 'r', 'l'],
             fonts=['Work', 'Mono', 'Work', 'Mono', 'Mono', 'Mono', 'Work'],
             wrap_cols={0, 2, 6}, size=6.0, cab_size=5.7)


def l_cpl(F):
    F.titulo('APÊNDICE  ·  ARQUIVO DE POSIÇÕES  (CPL)')
    F.glossario('Arquivo-fonte: luxpcb-revD/fab/cpl.csv. S1 está com rotação 180°. Origem das coordenadas: sistema do projeto KiCad (não é o canto da placa).')
    F.para('Gerado por export_jlc.py a partir da placa rev D. Coordenadas no sistema do KiCad (mm). Face: todas as peças montadas estão em Top; J2 e TP1–TP3 são apenas pads na face de baixo e não aparecem como componentes no CPL. Conferir rotação na prévia da JLC (pendência explícita: U1–U4, J1, D1–D3).')
    rows = []
    for r in D.cpl:
        rows.append([r['Designator'], r['Mid X'].replace('mm', ''), r['Mid Y'].replace('mm', ''), r['Layer'], r['Rotation']])
    F.tabela(['Ref.', 'X (mm)', 'Y (mm)', 'Face', 'Rotação (°)'],
             rows, [54, 84, 84, 80, 86],
             aligns=['l', 'r', 'r', 'c', 'r'],
             fonts=['Mono', 'Mono', 'Mono', 'Work', 'Mono'], size=6.2, cab_size=5.85)


def l_relatorios(F):
    F.titulo('APÊNDICE  ·  RELATÓRIOS ERC E DRC  (ÍNTEGRA)')
    F.glossario('Reproduzir estes relatórios a cada revisão da placa. Não editar os arquivos .rpt à mão.')
    F.rotulo('reports/erc.rpt')
    erc = [
        'ERC report (2026-11-22T15:25:23-0300, Encoding UTF8)',
        '',
        '***** Sheet /',
        '',
        ' ** ERC messages: 0  Errors 0  Warnings 0',
    ]
    F.code_lines(erc, size=6.2, step=9.0, gap=6.0)
    F.rotulo('reports/drc.rpt', gap_before=2.0)
    drc = [
        '** Drc report for luxflag.kicad_pcb **',
        '** Created on 2026-11-22T15:25:23-0300 **',
        '',
        '** Found 1 DRC violations **',
        "[lib_footprint_mismatch]: Footprint 'USB_C_Receptacle_HRO_TYPE-C-31-M-12' does not match copy in library 'Connector_USB'.",
        '    Local override; warning',
        '    @(105.5000 mm, 141.0000 mm): Footprint J1',
        '',
        '** Found 0 unconnected pads **',
        '',
        '** Found 0 Footprint errors **',
        '',
        '** End of Report **',
    ]
    F.code_lines(drc, size=6.2, step=9.0, gap=8.0)
    F.para('O aviso do J1 é a serigrafia editada de propósito (CHANGELOG/README). Zero erros, zero pads abertos, zero pendências de roteamento, paridade OK. Horário dos relatórios: 22/11/2026, 15:25, UTC−3 (America/Sao_Paulo).')


def l_glossario(F):
    F.titulo('APÊNDICE  ·  GLOSSÁRIO')
    rows = [
        ['ACK 42', 'resposta de reconhecimento do protocolo Flag/SIGNA, byte 0x42'],
        ['AF', 'função alternativa do pino do STM32 (aqui, SWCLK no PA14 e MOSI no PA7)'],
        ['ANATEL', 'agência brasileira de telecomunicações; homologação a definir'],
        ['BOOT0 / nBOOT_SEL', 'pino e option byte que escolhem firmware ou bootloader da ROM (DFU)'],
        ['CPL', 'component placement list, arquivo de posições para montagem SMT'],
        ['CRS', 'Clock Recovery System: ajusta o HSIUSB48 pelo SOF de 1 kHz, sem cristal'],
        ['DFU', 'Device Firmware Upgrade, aqui o bootloader em ROM da ST (0483:df11)'],
        ['DRC / ERC', 'verificação de regras da placa / do esquemático no KiCad'],
        ['ENIG', 'acabamento electroless nickel immersion gold, especificado no README da rev D'],
        ['EP', 'endpoint USB (0x01 OUT, 0x81 IN)'],
        ['Escada', 'modo de exibição em que um único estado vence (prioridade global) e vai aos 3 LEDs'],
        ['Flag', 'Luxafor Flag, aparelho original cujo protocolo HID o SIGNA reproduz'],
        ['HID', 'Human Interface Device; aqui, página vendor 0xFF00, 8+8 bytes, sem Report ID'],
        ['hidraw', 'interface Linux; o kernel prefixa 0x00 (Report ID 0) na escrita'],
        ['INPI', 'Instituto Nacional da Propriedade Industrial; o nome SIGNA é provisório'],
        ['JLC / LCSC', 'JLCPCB (fabricação e montagem) e seu catálogo de componentes'],
        ['Misto', 'modo em que LEDs 3 e 2 mostram a sala e o LED 1 mostra a IA'],
        ['NVM', 'memória não volátil; aqui, a última página de flash com o serial'],
        ['OE', 'output enable do buffer 74AHCT1G125; nesta placa está a GND (sempre habilitado)'],
        ['Opt-in', 'a monitoração de IA só liga se o usuário escolher'],
        ['Option bytes', 'configuração persistente do STM32 (entre elas nBOOT_SEL)'],
        ['pid.codes', 'programa de PIDs USB gratuitos para hardware aberto; 1209:0001 é Test PID'],
        ['Press-fit', 'encaixe por interferência, sem parafuso e sem cola (tampão × berço)'],
        ['PWM', 'modulação por largura de pulso; no WS2816B, 10 kHz e 16 bit'],
        ['Q12 / Q8.8', 'formatos fracionários do motor (nível de estado e cor interna)'],
        ['Rev A/B/C/D', 'A = Pendente mecânico original; B = mecânica atual; C = placa anterior; D = placa atual'],
        ['SOF', 'Start of Frame USB, 1 kHz, usado pelo CRS'],
        ['SWD / SWCLK / SWDIO', 'depuração serial do ARM; no C071 o SWCLK coincide com BOOT0 (PA14)'],
        ['Tag-Connect / TC2030', 'conector de programação por pads, sem header soldado (J2)'],
        ['TP1–TP3', 'pontos de teste na face de baixo: VBUS, dado 5 V dos LEDs, GND'],
        ['UFP', 'upstream-facing port, o lado dispositivo do USB-C (resistores de 5,1 kΩ nos CC)'],
        ['V-cut', 'risco de painelização; não pode atravessar as orelhas de 15,2 mm'],
        ['VBUS', '5 V fornecidos pelo computador no USB'],
        ['VID:PID', 'identificadores USB de fabricante e produto'],
        ['WCAG 2.3.1', 'critério de acessibilidade de flashes (limite 3 Hz); o ERRO do SIGNA está a 2,5 Hz'],
        ['WS2816B', 'LED RGB endereçável 16 bit, PWM 10 kHz, dado duplo DI/DO + BI/BO'],
        ['1.º diedro', 'convenção de vistas da NBR 10067 (vista de cima abaixo da frontal)'],
    ]
    F.tabela(['Termo', 'Significado neste caderno'], rows, [84, 304],
             fonts=['WorkM', 'Work'], wrap_cols={0, 1}, size=6.2, cab_size=5.85)


def l_colofao(c, n, total, skip_images=False):
    L = Lamina(c, n, total, 'COLOFÃO', RODAPE, noite=True, skip_images=skip_images)
    L.text(M, 212, D.produto['nome'], 'JuraL', 24, L.ink, cs=4.0, tag='cf')
    L.rect(M, 198, 60, 1.0, fill=VERM)
    y = 176
    linhas = [
        f'{DOC_ID}  ·  revisão {DOC_REV}  ·  {DOC_DATA}',
        'Caderno de engenharia, continuação do caderno conceitual de 14 lâminas.',
        'Sistema visual Metrologia Luminosa. Formato A3 paisagem.',
        'Nenhum número foi inventado. O que faltava nas fontes está marcado « a definir ».',
        'Este PDF não é certificação, não é cotação e não autoriza gravação de NVM nem pedido de fabricação por si só.',
        'Placa rev D  ·  mecânica rev B  ·  firmware e aplicativo 0.1  ·  nada testado em silício.',
    ]
    for ln in linhas:
        last = L.para(M, y, ln, 'Work', 7.8, width=376, leading=11.0)
        y = last - 13.0
    L.text(M, 31.5, 'FIM DO CADERNO', 'JuraM', 7.2, L.ink, cs=1.0)
    return L
