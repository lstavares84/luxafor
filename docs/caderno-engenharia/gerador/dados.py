"""Leitura das fontes de engenharia. Nada inventado: se faltar, o chamador marca 'a definir'."""
import csv, json, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))


def _pasta(env, relativos, reserva):
    """Caminho da fonte: SIGNA_* se definida; senão a pasta deste repositório; senão /workspace."""
    v = os.environ.get(env, '').strip()
    if v:
        return v
    raiz = os.path.abspath(os.path.join(ROOT, '..', '..', '..'))
    for rel in relativos:
        p = os.path.join(raiz, rel)
        if os.path.isdir(p):
            return p
    return reserva


REV_D = _pasta('SIGNA_REVD', ('hardware/revD',), '/workspace/luxpcb-revD')
SW = _pasta('SIGNA_SW', ('software',), '/workspace/signa-sw')
MECH = _pasta('SIGNA_MECH', ('mecanica',), '/workspace/signa-3d')
CONC = _pasta('SIGNA_CONC', ('docs/caderno-signa', '.old/docs/conceito'), '/workspace/caderno-revC')

produto = json.load(open(os.path.join(CONC, 'dados/produto.json')))
jlc_revd = json.load(open(os.path.join(REV_D, 'docs/jlc_revD_2026-11-22.json')))
estoque = json.load(open(os.path.join(REV_D, 'docs/estoque_stm32c071.json')))
parts = json.load(open(os.path.join(REV_D, 'docs/parts-check.json')))
folgas_doc = json.load(open(os.path.join(MECH, 'docs/verificacao_montagem.json')))

# BOM eletrônica (fab)
bom_elec = list(csv.DictReader(open(os.path.join(REV_D, 'fab/bom.csv'))))
cpl = list(csv.DictReader(open(os.path.join(REV_D, 'fab/cpl.csv'))))

# BOM completa do produto
bom_prod = list(csv.DictReader(open(os.path.join(MECH, 'bom/bom_completa.csv'))))

modos = {m['id']: m for m in produto['modos']}
MODOS_PRIO = [modos[i] for i in produto['prioridade_ordem']]

# Pinagem UFQFPN-28 GP (DS14693, figura do encapsulamento _GxU, não N)
MCU_PINS = [
    (1, 'PC14-OSCX_IN', 'NC', 'não conectar'),
    (2, 'PC15-OSCX_OUT', 'NC', 'não conectar'),
    (3, 'VDD/VDDA', '+3V3', 'alimentação do MCU (U2)'),
    (4, 'VSS/VSSA', 'GND', 'terra'),
    (5, 'PF2-NRST', 'NRST', 'reset; C4 100 nF a GND; J2 pino 3'),
    (6, 'PA0', 'NC', 'não conectar'),
    (7, 'PA1', 'NC', 'não conectar'),
    (8, 'PA2', 'NC', 'não conectar'),
    (9, 'PA3', 'NC', 'não conectar'),
    (10, 'PA4', 'NC', 'não conectar'),
    (11, 'PA5', 'NC', 'não conectar'),
    (12, 'PA6', 'NC', 'não conectar'),
    (13, 'PA7', 'LED_DIN_3V3', 'SPI1_MOSI (AF0) → U3.A; dado dos LEDs'),
    (14, 'PB0', 'NC', 'não conectar'),
    (15, 'PB1', 'NC', 'não conectar'),
    (16, 'PA8', 'NC', 'não conectar'),
    (17, 'PC6', 'NC', 'no GP é PC6; na versão N este pino é VDDIO2 — não trocar'),
    (18, 'PA11 [PA9]', 'USB_DM', 'USB FS D− (padrão no UFQFPN-28; não remapear)'),
    (19, 'PA12 [PA10]', 'USB_DP', 'USB FS D+ (padrão; não remapear)'),
    (20, 'PA13', 'SWDIO', 'J2 pino 2'),
    (21, 'PA14-BOOT0', 'SWCLK_BOOT0', 'SWCLK + BOOT0; S1/R5 e JP1; J2 pino 4'),
    (22, 'PA15', 'NC', 'não conectar'),
    (23, 'PB3', 'NC', 'não conectar'),
    (24, 'PB4', 'NC', 'não conectar'),
    (25, 'PB5', 'NC', 'não conectar'),
    (26, 'PB6', 'NC', 'não conectar'),
    (27, 'PB7', 'NC', 'não conectar'),
    (28, 'PB8', 'NC', 'não conectar'),
]

# Preços JLC da BOM completa (já por produto)
def money(v):
    try:
        return float(v)
    except Exception:
        return None

# estados nativos firmware
ESTADOS_FW = [
    (0, 'apagado', '—', '—', 'LEDs apagados'),
    (1, 'LIVRE', '#2FD28A', 'fixo 0,28', 'SALA'),
    (2, 'PRESTES A ENTRAR', '#FF8A1A', 'respiração 3,0 s, piso 0,20, expoente 1,4', 'SALA'),
    (3, 'OCUPADO', '#FF3B2F', 'fixo 1,0', 'SALA'),
    (4, 'IA DESOCUPADA', '#7C8EA6', 'fixo 0,08', 'IA'),
    (5, 'PROCESSANDO', '#3D8BFF', 'respiração 2,4 s, piso 0,15, expoente 1,6', 'IA'),
    (6, 'PRECISA DE ATENÇÃO', '#FFE02E', 'quadrada 1 Hz, 50 %, piso 0,06', 'IA'),
    (7, 'ERRO', '#FF3FC8', 'estrobo 2,5 Hz, pulso 130 ms, piso 0,04', 'IA'),
    (8, 'LIMITE 5 h', '#9B5CFF', 'pulso duplo a cada 3 s (250/250/250 ms) a 0,55, piso 0,06', 'IA'),
    (9, 'LIMITE semanal', '#9B5CFF', 'fixo 0,28', 'IA'),
]

# Itens em aberto / a definir (só o que as fontes não fecham)
A_DEFINIR = [
    ('Nome comercial', 'SIGNA é provisório até verificação no INPI.'),
    ('VID:PID USB', 'Padrão de desenvolvimento 1209:0001 (Test PID do pid.codes). Par definitivo a decidir (pid.codes próprio, VID USB-IF ou sublicença). Nunca usar 04d8:f372 em unidade vendida.'),
    ('String USB do produto', 'O firmware ainda identifica o produto como "SIGNA rev C" (usb_ids.h).'),
    ('Byte de versão 0x80', 'Manter 0x3C (compatível com software antigo) ou usar um valor próprio. A versão real do SIGNA sai no 0x1F (hoje 0.1).'),
    ('nBOOT_SEL na produção', 'Precisa ser gravado como 0 para o DFU pelo botão/JP1 funcionar depois da 1.ª gravação. Processo de fábrica a definir (CubeProgrammer ou make AUTO_NBOOT_SEL=1).'),
    ('Posição do botão', 'S1 + P06 ficam embaixo do pendente. A chave pede 1,6 N e o produto pesa cerca de 0,2 N: é preciso segurar o tubo para apertar. Alternativas (chave mais leve ou botão na tampa, que exigiria flex ou fio) estão em aberto.'),
    ('Gesto longo do botão', 'O CHANGELOG da rev D sugere debounce de 30 ms e pressão longa de 2 s, e deixa o gesto longo em aberto. A leitura de PA14 ainda é pendência do firmware (nada testado em silício).'),
    ('Ordem GRB na placa', 'O driver envia G16 R16 B16 conforme o datasheet. Validar no primeiro silício: 01 FF FF 00 00 tem de acender vermelho.'),
    ('SPI/DMA contínuo', 'Validar com analisador ou osciloscópio no R3 que não há intervalo entre palavras (bit 0 ≈ 250 ns alto, bit 1 ≈ 667 ns).'),
    ('Acabamento e máscara da PCB', 'O README da rev D especifica ENIG; o arquivo gerber job está com Finish: "None". Cor da máscara (verde ou preta) não foi decidida.'),
    ('Painelização', 'A placa tem 15,2 mm de largura nas orelhas. O trilho/V-cut precisa preservar as orelhas.'),
    ('Prévia JLC', 'Conferir rotação do CPL (U1–U4, J1, D1–D3) e o footprint do WS2816B-2020 feito pelo datasheet.'),
    ('Estoque do MCU', 'STM32C071G8U6: 109 un. na JLC e 36 na LCSC em 22/11/2026. Alternativa GBU6 (128 KB, mesma pinagem GP): estoque 0 na JLC. Não usar sufixo N (pino 17 = VDDIO2).'),
    ('Amostra do cabo C01', 'Exigir amostra: casca exposta ≥ 5,8 mm, sobremolde ≤ 11,6 × 6,4 mm, sobremolde+alívio ≤ 24,5 mm, alívio ≤ Ø6,4 nos últimos 4,5 mm, capa Ø3,5 a 4,0 mm.'),
    ('Part numbers mecânicos', 'P01–P06 e C01 sem part number de fornecedor. Graus exatos de PC opalino, PC branco refletivo e TPE 60A: a verificar (materiais.md).'),
    ('Adaptador USB-A (C02)', 'Entra no custo total (US$ 0,45 @100 / 0,25 @1000). Decisão de incluir ou não está com o Lucas.'),
    ('Gravação a laser L02', 'Opcional; não entra no critério de aceite mínimo.'),
    ('Limites de IA na web (5 h / semanal)', 'Detecção por texto da página ou da mensagem de erro: heurística frágil, a validar. A extensão MV3 é experimental.'),
    ('Microfone e câmera', 'Não implementado. Fonte de "em reunião" a definir por sistema operacional.'),
    ('Ambiente e ensaios', 'Temperatura de operação e armazenamento, umidade, grau IP, altura de queda e vida do botão: não especificados nas fontes.'),
    ('Fotometria', 'Fluxo, luminância e uniformidade dos estados não foram medidos (só critério qualitativo: sem pontos quentes a 0,5 m).'),
    ('Corrente de produção', 'Orçamento 10–15 mA apagado e 70–80 mA no branco 100 % é estimativa de datasheet. Confirmar no primeiro lote e fixar o limite (reprovação > 100 mA).'),
    ('Impedância do par USB', 'Não há controle de impedância (Full Speed, trecho < 15 mm). Aceito no projeto; não é certificação.'),
    ('Certificações', 'USB-IF, CE, FCC, ANATEL, IEC 62471 e RoHS formal: não foram feitas. O caderno traz só considerações.'),
    ('Pressão de montagem do P06', 'O press-fit do tampão é 20–40 N (pacote do Pendente). A força de inserção do pino P06 no rebaixo não está quantificada além do curso e da força da chave (1,6 N).'),
]
