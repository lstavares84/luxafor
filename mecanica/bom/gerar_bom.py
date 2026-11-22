"""Gera BOM completa (CSV + MD) do SIGNA (mecânica rev B + placa rev D).
Eletronica: precos reais da API de pecas da JLCPCB (jlc_precos_eletronica.json, 2026-11-22).
Demais itens: ESTIMATIVAS (marcadas) - validar com cotacao (ver rfq_checklist.md)."""
import csv, json, os
H = os.path.dirname(os.path.abspath(__file__))
J = json.load(open(os.path.join(H, 'jlc_precos_eletronica.json')))['parts']
REVD_BOM = '../../hardware/revD/fab/bom.csv'  # relativo a mecanica/bom/

def price(code, qty):
    p = J[code]['prices']
    best = p[0]['productPrice']
    for b in p:
        if qty >= b['startNumber']:
            best = b['productPrice']
    return best

ELEC = [  # designators, qty/placa, LCSC, descricao
    ('U1', 1, 'C44521811', 'MCU STM32C071G8U6 (QFN-28)'),
    ('D1-D3', 3, 'C4154877', 'LED RGB WS2816B-2020'),
    ('J1', 1, 'C165948', 'USB-C HRO TYPE-C-31-M-12'),
    ('U2', 1, 'C51118', 'LDO AP2112K-3.3TRG1'),
    ('U3', 1, 'C7484', 'Buffer TI SN74AHCT1G125DBVR'),
    ('U4', 1, 'C7519', 'ESD ST USBLC6-2SC6'),
    ('C1', 1, 'C19702', 'Cap. 10 uF 0603 X5R'),
    ('C2', 1, 'C52923', 'Cap. 1 uF 0402 X5R'),
    ('C3-C8', 6, 'C1525', 'Cap. 100 nF 0402 X7R'),
    ('R1,R2', 2, 'C25905', 'Res. 5,1 k 0402'),
    ('R3', 1, 'C25105', 'Res. 33 R 0402'),
    ('R4,R5', 2, 'C11702', 'Res. 1 k 0402 (pull-up BOOT0 + série do botão)'),
    ('S1', 1, 'C110293', 'Chave tátil lateral ALPS SKRTLAE010 (1,6 N)'),
]
rows = []
def add(cat, item, desc, ref, supplier, pn, qty, c100, c1000, src, status):
    rows.append(dict(categoria=cat, item=item, descricao=desc, ref_desenho=ref, fornecedor=supplier, part_number=pn,
                     qtd_por_unidade=qty, custo_usd_por_produto_lote100=round(c100, 3), custo_usd_por_produto_lote1000=round(c1000, 3),
                     fonte=src, status=status))

# ---------- eletronica (componentes)
ext = 0
for ref, q, code, d in ELEC:
    p100, p1000 = price(code, 100 * q), price(code, 1000 * q)
    lib = J[code]['lib']
    ext += lib == 'expand'
    add('Eletrônica', ref, d, 'LXE-E01', 'LCSC/JLCPCB', f"{J[code]['model']} ({code})", q, p100 * q, p1000 * q,
        f"API JLCPCB 2026-11-22, faixa de qtd; estoque JLC {J[code]['stock']}", 'verificado (preço/estoque do dia)')
# ---------- eletronica (fabricacao)
add('Eletrônica', 'PCB', 'PCB 2 camadas 11×44×0,8 mm (15,2 nas orelhas), ENIG, painelizada', 'LXE-E01', 'JLCPCB', 'gerber.zip (luxpcb-revD/fab)', 1, 0.20, 0.06,
    'estimativa a partir da tabela pública JLC (não cotado neste pacote)', 'ESTIMATIVA')
add('Eletrônica', 'PCBA', f'Montagem SMT 1 face (setup + estêncil + {ext} peças "extended" × US$3 + juntas)', 'LXE-E01', 'JLCPCB', '—', 1,
    (8 + 1.5 + 3 * ext) / 100 + 0.20, (8 + 1.5 + 3 * ext) / 1000 + 0.12, 'estimativa: taxas públicas JLC (setup ~US$8, extended US$3/peça, ~US$0,0017/junta)', 'ESTIMATIVA')
add('Eletrônica', 'FW', 'Gravação de firmware via USB DFU (ROM) + teste', 'teste.md', 'interno', '—', 1, 0.10, 0.05, 'estimativa de tempo de operador', 'ESTIMATIVA')
# ---------- mecanica
add('Mecânica', 'P01', 'Tubo difusor PC opalino Ø16/13 × 48, cortado e jateado', 'LXP-P01', 'fornecedor de tubos PC difusor (China) / serralheria plástica (BR)', 'não definido', 1, 0.90, 0.30,
    'estimativa: tubo extrudado ~US$2–5/m + corte/jateamento', 'ESTIMATIVA — cotar')
add('Mecânica', 'P02', 'Tampa Al 6061-T6 torneada, anodizada preta', 'LXP-P02', 'JLCCNC / PCBWay CNC (protótipo); torno CNC tipo suíço (série)', 'não definido', 1, 5.50, 1.60,
    'estimativa: torneamento simples Ø19×32 + anodização', 'ESTIMATIVA — cotar')
add('Mecânica', 'P02b', 'Tampa impressa (só protótipo; não soma no custo de série)', 'LXP-P02', 'JLC3DP (MJF PA12 preto / SLA preto)', '—', 0, 1.50, 0.0,
    'estimativa', 'ESTIMATIVA (opcional)')
add('Mecânica', 'P03', 'Berço PC branco', 'LXP-P03', '100 un.: SLA/MJF (JLC3DP); 1000 un.: injeção (molde família P03+P04)', 'não definido', 1, 1.80, 0.10,
    'estimativa: impressão 3D vs. peça injetada (sem ferramental)', 'ESTIMATIVA — cotar')
add('Mecânica', 'P04', 'Tampão PC opalino', 'LXP-P04', 'idem P03', 'não definido', 1, 0.90, 0.06, 'estimativa', 'ESTIMATIVA — cotar')
add('Mecânica', 'P06', 'Botão (pino) PC opalino Ø3/Ø4,4 × 7,4', 'LXP-P06', '100 un.: SLA translúcido (JLC3DP); 1000 un.: cavidade extra no molde família P03+P04', 'não definido', 1, 0.40, 0.02,
    'estimativa (peça minúscula; custo dominado pelo ferramental)', 'ESTIMATIVA — cotar')
add('Mecânica', 'P05', 'Passa-cabo TPE 60A bipartido', 'LXP-P05', '100 un.: silicone fundido em molde impresso / TPU 3D; 1000 un.: injeção TPE', 'não definido', 1, 0.60, 0.05,
    'estimativa', 'ESTIMATIVA — cotar')
add('Mecânica', 'FERR', 'Ferramental amortizado (molde família P03+P04+P06 em alumínio ~US$3.300 + molde P05 ~US$1.000)', 'manufatura.md', 'ferramentaria (China/BR)', '—', 1, 0.0, 4.30,
    'estimativa de mercado (rev B: +~US$300 pela cavidade do P06 e pelo furo/rebaixo no P04); ver manufatura.md; só entra no lote de 1000', 'ESTIMATIVA')
# ---------- cabo
add('Cabo', 'C01', 'Cabo USB-C ↔ USB-C 1,5 m, USB 2.0, capa Ø3,5–4,0; casca ≥5,8 mm, sobremolde ≤11,6×6,4, sobremolde+bota ≤24,5 mm, bota ≤Ø6,4', 'LXP-A00 item 7', 'fabricante de cabos OEM (Shenzhen) / distribuidor BR', 'não definido', 1, 1.80, 1.00,
    'estimativa de mercado', 'ESTIMATIVA — exigir amostra e medir plugue')
add('Cabo', 'C02', 'Adaptador USB-A macho → USB-C fêmea (opcional, p/ PCs sem USB-C)', '—', 'idem', 'não definido', 1, 0.45, 0.25, 'estimativa', 'ESTIMATIVA (decisão Lucas)')
# ---------- embalagem / etiquetas / insumos
add('Embalagem', 'K01', 'Caixa kraft/cartão 60×40×130 mm com berço de papelão', '—', 'gráfica BR / fornecedor China', 'não definido', 1, 1.00, 0.35, 'estimativa', 'ESTIMATIVA')
add('Embalagem', 'K02', 'Cartão de instruções A7 + QR para software', '—', 'gráfica', '—', 1, 0.10, 0.03, 'estimativa', 'ESTIMATIVA')
add('Embalagem', 'K03', 'Saco/manga de proteção para o tubo', '—', 'genérico', '—', 1, 0.05, 0.02, 'estimativa', 'ESTIMATIVA')
add('Etiquetas', 'L01', 'Etiqueta de série/lote (dentro da caixa) + etiqueta da caixa', '—', 'genérico', '—', 2, 0.06, 0.02, 'estimativa', 'ESTIMATIVA')
add('Etiquetas', 'L02', 'Gravação a laser no topo da tampa (logo/nº série)', 'LXP-P02 nota 6', 'fornecedor CNC', '—', 1, 0.30, 0.10, 'estimativa', 'ESTIMATIVA (opcional)')
add('Fixação/adesivos', 'F01', 'Nenhum parafuso nem cola no projeto (encaixes + press-fit)', '—', '—', '—', 0, 0, 0, 'decisão de projeto', 'n/a')
add('Fixação/adesivos', 'F02', 'Cola UV (gota) de contingência no pino do berço, se o press-fit soltar', '—', 'ex.: adesivo UV para PC (a escolher)', 'não definido', 0, 0.02, 0.01, 'estimativa; não somado', 'opcional')
# ---------- mao de obra
add('Montagem', 'M01', 'Montagem final (≈4 min) + teste funcional (≈1 min) + embalagem', 'montagem.md / teste.md', 'interno', '—', 1, 1.20, 0.60, 'estimativa (mão de obra BR)', 'ESTIMATIVA')

fields = list(rows[0].keys())
with open(os.path.join(H, 'bom_completa.csv'), 'w', newline='') as fcsv:
    w = csv.DictWriter(fcsv, fieldnames=fields); w.writeheader(); w.writerows(rows)

def tot(cat=None, col='custo_usd_por_produto_lote100', skip=('P02b', 'F02')):
    return sum(r[col] * (1 if r['qtd_por_unidade'] or r['item'] in () else 1) for r in rows
               if (cat is None or r['categoria'] == cat) and r['item'] not in skip and not (r['qtd_por_unidade'] == 0))
cats = ['Eletrônica', 'Mecânica', 'Cabo', 'Embalagem', 'Etiquetas', 'Fixação/adesivos', 'Montagem']
elec_parts100 = sum(r['custo_usd_por_produto_lote100'] for r in rows if r['categoria'] == 'Eletrônica' and r['item'] not in ('PCB', 'PCBA', 'FW'))
elec_parts1000 = sum(r['custo_usd_por_produto_lote1000'] for r in rows if r['categoria'] == 'Eletrônica' and r['item'] not in ('PCB', 'PCBA', 'FW'))
md = ['# BOM completa — SIGNA (mecânica rev B, placa rev D)', '',
      'Gerada por `bom/gerar_bom.py` (2026-11-22). Valores em **US$ por produto montado** (qtd × preço unitário), em dois lotes (100 e 1000 unidades).',
      '**Só os componentes eletrônicos têm preço consultado** (API de peças da JLCPCB, faixa de quantidade do lote; arquivo `jlc_precos_eletronica.json`).',
      'Todo o resto é **ESTIMATIVA** de ordem de grandeza e precisa de cotação (ver `rfq_checklist.md`). Não inclui frete, impostos de importação (Brasil: II/IPI/ICMS podem somar 60–100 %), margem nem certificações.',
      '', f'BOM da placa (fonte única): `../../hardware/revD/fab/bom.csv`. Componentes da placa: **US$ {elec_parts100:.2f}** (lote 100) / **US$ {elec_parts1000:.2f}** (lote 1000).', '',
      '| Cat. | Item | Descrição | Desenho/ref. | Fornecedor | Part number | Qtd | US$ @100 | US$ @1000 | Status |', '|---|---|---|---|---|---|---|---|---|---|']
for r in rows:
    md.append(f"| {r['categoria']} | {r['item']} | {r['descricao']} | {r['ref_desenho']} | {r['fornecedor']} | {r['part_number']} | {r['qtd_por_unidade']} | {r['custo_usd_por_produto_lote100']:.3f} | {r['custo_usd_por_produto_lote1000']:.3f} | {r['status']} |")
md += ['', '## Totais por unidade (US$)', '', '| Categoria | Lote 100 | Lote 1000 |', '|---|---|---|']
T100 = T1000 = 0
for c in cats:
    a, b = tot(c), tot(c, 'custo_usd_por_produto_lote1000')
    T100 += a; T1000 += b
    md.append(f'| {c} | {a:.2f} | {b:.2f} |')
md.append(f'| **Total** | **{T100:.2f}** | **{T1000:.2f}** |')
md += ['', 'Notas:', '- P02b (tampa impressa) e F02 (cola de contingência) não entram no total.',
       '- Lote 1000 inclui ferramental amortizado (US$ 4,30/un.). Sem ele: US$ %.2f.' % (T1000 - 4.3),
       '- Cabo C02 (adaptador USB-A) entra no total; retirar se Lucas decidir não incluir.',
       '- **Risco de suprimento:** STM32C071G8U6 tinha só %d un. no estoque JLC em 2026-11-22 (preço do lote 1000 usa a faixa de preço, não garante estoque). Alternativa pino a pino STM32C071GBU6 (C42113261): %d un., US$ 3,54 @100.' % (J['C44521811']['stock'], J['C42113261']['stock']),
       '- Rev D vs. rev C: +S1 (C110293, extended) +R5 (C11702, basic). A peça extended a mais custa ~US$ 3 por pedido de montagem (taxa pública JLC; conferir na cotação).']
open(os.path.join(H, 'bom_completa.md'), 'w').write('\n'.join(md) + '\n')
print(f'TOTAL @100 = {T100:.2f}  @1000 = {T1000:.2f}  (eletronica pecas {elec_parts100:.2f}/{elec_parts1000:.2f})')
for c in cats: print(c, round(tot(c), 2), round(tot(c, 'custo_usd_por_produto_lote1000'), 2))
