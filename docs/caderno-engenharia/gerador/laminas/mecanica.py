"""Lâminas de mecânica — SIGNA rev B, conjunto integrado."""
from lib_metrologia import *
from helpers import *
import dados as D


def register(book):
    book.divisor('III', 'MECÂNICA', [
        'Conjunto integrado: peças P01 a P06, a placa rev D completa e o cabo USB-C num único STEP e num GLB.',
        'A rev B corrige a retenção axial da placa (orelhas), acrescenta o botão P06 e aperta a especificação do cabo.',
        'Desenhos LXP-A00 e P01–P06 em projeção do 1.º diedro, cotas em milímetros, tolerância geral ISO 2768-mK.',
    ], short='MECÂNICA')
    book.add_flow('III  MECÂNICA', 'Visão da mecânica rev B', l_visao_m)
    book.add('III  MECÂNICA', 'Isometria e corte', l_iso_corte)
    book.add_flow('III  MECÂNICA', 'Vista explodida', l_explodida)
    book.add('III  MECÂNICA', 'Desenho de conjunto A00', l_a00)
    book.add_flow('III  MECÂNICA', 'Folgas e interferências', l_folgas)
    book.add_flow('III  MECÂNICA', 'Folgas  ·  botão e USB-C', l_folgas2)
    book.add_flow('III  MECÂNICA', 'P01  ·  tubo difusor', lambda F: l_peca(F, 'P01', 'TUBO DIFUSOR', 'des_P01',
        'Policarbonato opalino extrudado, Ø16/13 × 48 mm, cantos chanfrados 0,2, fosco externo. Grau exato (família Makrolon LED/diffuser ou Lexan difusor) a verificar. Transmitância alvo 50–65 %, UV-estabilizado, V-2 ou melhor.'))
    book.add_flow('III  MECÂNICA', 'P02  ·  tampa de alumínio', lambda F: l_peca(F, 'P02', 'TAMPA', 'des_P02',
        'Alumínio 6061-T6, barra Ø20 ou Ø22, torneada e anodizada preta tipo II (MIL-A-8625 Tipo II Classe 2, 10–15 µm, jato de microesfera, Ra 0,8–1,6 µm). Gravação a laser no topo é opcional (L02). P02b (PA12 MJF ou SLA preto) serve só de protótipo e não entra no custo de série.'))
    book.add_flow('III  MECÂNICA', 'P03  ·  berço', lambda F: l_peca(F, 'P03', 'BERÇO', 'des_P03',
        'PC branco de alta refletância (refletância > 90 %, grau a verificar). Na rev B: fundo da ranhura 0,30 mm abaixo da placa (sem apoio duplo); recorte da flange com 12,2 mm de largura e duas fendas para as orelhas; alívio THT do J1 atravessa a flange; rebaixo de sobremolde removido. Cotas críticas no RFQ: ranhura 0,9 +0,05/0; largura entre fundos 11,3 +0,1/0; flange Ø16 −0,05/−0,10; dente R8,45 ±0,05.'))
    book.add_flow('III  MECÂNICA', 'P04  ·  tampão', lambda F: l_peca(F, 'P04', 'TAMPÃO', 'des_P04',
        'PC opalino, mesmo grau do tubo, para a ponta de baixo também brilhar. Na rev B: furo Ø3,2 coaxial com a haste do S1 e rebaixo Ø4,8 × 1,0 para o colar do P06. Press-fit no berço (interferência medida 1,40 mm³). Cota crítica no RFQ (rev A, conferir no desenho rev B): Ø12,85 ±0,03; o furo do botão passou a Ø3,2.'))
    book.add_flow('III  MECÂNICA', 'P05  ·  passa-cabo', lambda F: l_peca(F, 'P05', 'PASSA-CABO', 'des_P05',
        'TPE 60 Shore A preto, bipartido por fenda. Na rev B o furo foi de Ø3,6 para Ø3,3, para apertar cabos de Ø3,5 a Ø4,0. Interferência intencional com o cabo: 27,6 mm³. Alternativa: silicone 60A (fundido, lotes pequenos). Pedir amostras 50/60/70A.'))
    book.add_flow('III  MECÂNICA', 'P06  ·  botão', lambda F: l_peca(F, 'P06', 'BOTÃO', 'des_P06',
        'Peça nova da rev B. Pino de PC opalino Ø3,0 com colar Ø4,4, retido por gravidade no rebaixo do tampão, e empurrador Ø2,2. Fica 0,40 mm abaixo da haste do S1 (0,0 a 0,8 mm no pior caso) e sai 0,3 mm abaixo do tampão. Curso até acionar: 0,60 mm nominal, 1,00 mm no pior caso. Protótipo: SLA translúcido; série: cavidade extra no molde família P03+P04.'))
    book.add_flow('III  MECÂNICA', 'Cabo C01  ·  especificação', l_cabo, 'CABO C01')
    book.add_flow('III  MECÂNICA', 'Materiais e acabamentos', l_materiais)
    book.add_flow('III  MECÂNICA', 'Massas e envelope', l_massas)
    book.add_flow('III  MECÂNICA', 'Montagem  ·  preparação', l_monta_prep)
    book.add_flow('III  MECÂNICA', 'Montagem  ·  passos 1 a 3', l_monta_13)
    book.add_flow('III  MECÂNICA', 'Montagem  ·  passos 4 a 6', l_monta_46)
    book.add_flow('III  MECÂNICA', 'Desmontagem e assistência', l_desmonta)
    book.add_flow('III  MECÂNICA', 'Manufatura  ·  protótipo e série', l_manufatura, 'MANUFATURA')


def l_visao_m(F):
    F.titulo('MECÂNICA REV B  ·  O QUE MUDOU EM RELAÇÃO AO PENDENTE REV A')
    F.glossario('Fonte: signa-3d/README.md. O pacote /workspace/pendente não foi alterado; a rev B parte dele e documenta só o delta.')
    F.L.image_fit(JPG('iso'), 266, 68, 138, 162, 'iso', anchor='c')
    F.L.caption(266, 60, 'Fig.  —  Conjunto SIGNA rev B, isometria, botão visível embaixo.', width=138)
    F.set_box(M, 240, y=F.y, min_y=F.base_min_y)
    rows = [
        ['Orelhas da placa', 'Batente axial: apoiam nas fendas da flange (Z = 50,75) e ficam 0,25 mm abaixo do ressalto da tampa. Na rev A nada segurava a placa por cima: puxar o cabo (8–20 N) a arrancaria. A placa subiu 0,75 mm (PCB_Z0 = 7,75).'],
        ['P03 berço', 'Fundo da ranhura 0,30 mm abaixo da placa (evita apoio duplo). Recorte da flange 12,2 mm + 2 fendas. Alívio THT do J1 atravessa a flange. Rebaixo de sobremolde removido: a boca do USB-C fica 0,40 mm acima da flange.'],
        ['P04 tampão', 'Furo Ø3,2 coaxial com a haste do S1 + rebaixo Ø4,8 × 1,0.'],
        ['P06 botão', 'Peça nova: pino Ø3,0, colar Ø4,4, empurrador Ø2,2. Sai 0,3 mm abaixo do tampão.'],
        ['P05 passa-cabo', 'Furo Ø3,6 → Ø3,3, para capas de Ø3,5 a Ø4,0.'],
        ['Cabo C01', 'Modelado: casca 8,25 × 2,4 inserida 6,2 mm; sobremolde 11,6 × 6,4 × 17 (r 2,8; diagonal 11,65 passa no Ø12,8); alívio Ø6,0→Ø4,2 × 7; capa Ø3,8. Trajeto de 225 mm até atrás do monitor (o restante do 1,5 m não é modelado).'],
        ['Óptica', 'LED → difusor: 7,27 mm (altura real do WS2816B: 0,84 mm).'],
    ]
    F.tabela(['Tema', 'Mudança'], rows, [56, 184], cont_larg=[76, 312],
             wrap_cols={1}, fonts=['Work', 'Work'], size=6.2, cab_size=5.85)


def l_iso_corte(c, n, total, skip_images=False):
    L = Lamina(c, n, total, 'ISOMETRIA E CORTE', RODAPE, skip_images=skip_images)
    L.titulo('ISOMETRIA E CORTE')
    L.image_fit(JPG('iso'), M, 56, 186, 186, 'iso', anchor='c')
    L.image_fit(JPG('corte'), 218, 56, 186, 186, 'corte', anchor='c')
    L.caption(M, 46, 'Fig.  —  Esquerda: isometria do conjunto. Direita: corte com a placa no berço, o plugue encaixado e o botão P06 no tampão.', width=388)
    return L


def l_explodida(F):
    F.titulo('VISTA EXPLODIDA')
    F.L.image_fit(JPG('explodida'), M, 56, 178, 186, 'explodida', anchor='c')
    F.L.caption(M, 46, 'Fig.  —  Explodida com a placa ao lado (signa-3d/renders/explodida.png). Sem parafusos e sem cola.', width=178)
    F.set_box(208, 196, y=F.y, min_y=F.base_min_y)
    F.rotulo('ORDEM DE PILHA  (cima para baixo)')
    F.kv_list([
        ('C01', 'cabo USB-C (casca + sobremolde + alívio)'),
        ('P05', 'passa-cabo TPE'),
        ('P02', 'tampa Al 6061-T6 anodizada'),
        ('P03', 'berço PC branco'),
        ('E01', 'placa rev D (LEDs à frente, USB para cima)'),
        ('P01', 'tubo difusor PC opalino'),
        ('P04', 'tampão PC opalino'),
        ('P06', 'botão (retido no rebaixo de P04)'),
    ], key_w=26, k_size=6.5, v_size=6.5, gap=4.0, line_div=False, v_font='Work')


def l_a00(c, n, total, skip_images=False):
    L = Lamina(c, n, total, 'DESENHO LXP-A00', RODAPE, skip_images=skip_images)
    L.titulo('DESENHO DE CONJUNTO  ·  LXP-A00')
    L.image_fit(JPG('des_A00'), M, 52, 388, 190, 'A00', anchor='c')
    L.caption(M, 44, 'Fig.  —  LXP-A00, conjunto SIGNA rev B. Projeção 1.º diedro, cotas em mm. Também em desenhos/LXP-A00_conjunto.pdf e SIGNA_revB_desenhos_completos.pdf.', width=388)
    return L


def l_folgas(F):
    F.titulo('FOLGAS E INTERFERÊNCIAS  ·  PLACA, CORPO E ÓPTICA')
    F.glossario('Valores de verificacao_montagem.json / .txt, gerados no CAD em 22/11/2026. « mín. 3D » é o mínimo medido na malha, que pode ser menor que o nominal.')
    F.para('Medidas no CAD (docs/verificacao_montagem). Unidades: mm. Interferências listadas são intencionais (press-fit ou aperto de elastômero); o relatório registra zero interferências não intencionais.')
    F.rotulo('INTERFERÊNCIAS INTENCIONAIS  (volume em mm³)', gap_before=2.0)
    rows1 = [
        ['Tampão × berço (press-fit)', '1,40'],
        ['Passa-cabo × cabo (aperto)', '27,61'],
        ['Sobremolde × alívio (mesmo objeto)', '13,28'],
        ['Alívio × capa (mesmo objeto)', '15,31'],
    ]
    F.tabela(['Par', 'Volume (mm³)'], rows1, [300, 88], aligns=['l', 'r'], fonts=['Work', 'Mono'])
    F.rotulo('FOLGAS  ·  PLACA E CORPO', gap_before=2.0)
    items = [
        ('placa (PCB) – berço', '0,00', 'contato nas faces previstas do deslizamento'),
        ('orelhas da placa – ressalto da tampa (axial)', '0,25', 'batente; medido 0,155 mm no mínimo 3D'),
        ('borda de baixo da placa – fundo das ranhuras', '0,30', 'evita apoio duplo (hiperestático)'),
        ('orelhas – fundo lateral da fenda (por lado)', '0,15', ''),
        ('orelhas – tubo (mín. 3D)', '0,499', ''),
        ('placa na ranhura: folga por face (espessura)', '0,05', ''),
        ('placa na ranhura: folga lateral total', '0,30', ''),
        ('placa (com componentes) – tubo', '0,499', ''),
        ('placa (com componentes) – tampão', '2,05', ''),
        ('LED (topo) – difusor, frente', '7,265', 'altura do WS2816B: 0,84 mm  ·  README: 7,27 mm'),
        ('corpo do botão S1 – tubo', '3,683', ''),
    ]
    rows2 = [[a, b, c] for a, b, c in items]
    F.tabela(['Folga', 'mm', 'Nota'], rows2, [156, 36, 196],
             aligns=['l', 'r', 'l'], fonts=['Work', 'Mono', 'Work'], wrap_cols={2}, size=6.2, cab_size=5.85)


def l_folgas2(F):
    F.titulo('FOLGAS  ·  BOTÃO P06 E ENCAIXE USB-C')
    F.glossario('LEDs em Z = 12,9 / 19,9 / 26,9 mm; botão em Y = 0,10 (quase no eixo); eixo USB em Y = 0,03. Massa do conjunto ≈ 20 g sem cabo.')
    F.rotulo('BOTÃO P06')
    rows1 = [
        ['botão P06 – haste do S1 (axial, nominal)', '0,40', 'tubo 48 ±0,2 e orelhas ±0,2 → 0,0 a 0,8 mm no pior caso; curso elétrico 0,2 mm'],
        ['botão P06 – tampão (radial no furo)', '0,10', 'colar apoiado no fundo do rebaixo por gravidade (contato)'],
        ['colar P06 – parede do rebaixo (radial)', '0,20', ''],
        ['botão P06 – berço', '0,695', ''],
        ['botão P06 – placa', '0,941', ''],
        ['curso total até acionar (pior caso)', '1,00', 'folga máx. 0,8 + curso 0,2; nominal 0,60 mm'],
        ['saída abaixo do tampão', '0,30', 'signa-3d/README'],
    ]
    F.tabela(['Folga', 'mm', 'Nota'], rows1, [152, 36, 200],
             aligns=['l', 'r', 'l'], fonts=['Work', 'Mono', 'Work'], wrap_cols={2}, size=6.2, cab_size=5.85)
    F.rotulo('USB-C E CABO', gap_before=2.0)
    rows2 = [
        ['casca do plugue – cavidade (lateral / altura)', '0,045 / 0,080', 'especificação 8,34 × 2,56 vs casca modelada 8,25 × 2,40'],
        ['casca – carcaça J1 (mín. 3D)', '0,045', ''],
        ['língua J1 – interior do plugue (mín. 3D)', '0,091', ''],
        ['ponta da casca – fundo da cavidade (axial)', '0,40', 'boca do USB-C 0,40 mm acima da flange: casca exposta ≥ 5,80 mm assenta'],
        ['espaço para sobremolde + alívio', '25,60', 'cabos com sobremolde+alívio até ~24,5 mm e alívio ≤ Ø6,4 nos últimos 4,5 mm'],
        ['sobremolde – boca do receptáculo (axial)', '0,45', ''],
        ['sobremolde – flange do berço', '0,85', ''],
        ['sobremolde – tampa (cavidade Ø13,6)', '0,969', ''],
        ['sobremolde – passa-cabo / alívio – passa-cabo', '3,65 / 0,663', ''],
        ['casca do plugue – placa', '0,52', ''],
        ['sobremolde no furo Ø12,8 (diagonal 11,65)', '0,573 / lado', 'plugues até 12,3 × 6,8 com r ≥ 3 também passam'],
        ['cabo – tampa (furo do topo)', '4,47', ''],
    ]
    F.tabela(['Folga', 'mm', 'Nota'], rows2, [146, 52, 190],
             aligns=['l', 'r', 'l'], fonts=['Work', 'Mono', 'Work'], wrap_cols={2}, size=6.2, cab_size=5.85)


def l_peca(F, codigo, nome, img, texto):
    F.titulo(f'{codigo}  ·  {nome}')
    F.glossario('Tolerância geral ISO 2768-mK, salvo cota indicada no desenho. Projeção 1.º diedro. Não usar o desenho da rev A onde a rev B alterou a peça (P03, P04, P05 e a nova P06).')
    F.L.image_fit(JPG(img), M, 68, 268, 174, codigo, anchor='c')
    F.L.caption(M, 58, f'Fig.  —  Desenho LXP-{codigo} (signa-3d/desenhos). Arquivos também em PDF, DXF, STEP, STL e 3MF na pasta export/.', width=268)
    F.set_box(294, 110, y=F.y, min_y=F.base_min_y)
    F.rotulo('ESPECIFICAÇÃO')
    F.para(texto)


def l_cabo(F):
    F.titulo('CABO C01  ·  ESPECIFICAÇÃO PARA FORNECEDOR')
    F.glossario('Fontes: signa-3d/README, verificacao_montagem, bom_completa.md (item C01), rfq_checklist.md (atualizado pela rev B no que diz respeito às cotas do plugue).')
    F.L.image_fit(JPG('detalhe_usbc_anotado'), M, 120, 240, 120, 'usbc anotado', anchor='c')
    F.L.image_fit(JPG('detalhe_usbc'), 264, 120, 140, 120, 'usbc', anchor='c')
    F.L.caption(M, 110, 'Fig.  —  Corte do encaixe USB-C, com chamadas (detalhe_usbc_anotado.png).', width=240)
    F.y = 94
    rows = [
        ['Tipo', 'USB-C macho ↔ USB-C macho, USB 2.0, 3 A, 1,5 m, trançado preto (nylon)  ·  condutores 28/24 AWG no pacote Pendente, a confirmar com o OEM'],
        ['Casca exposta do plugue', '≥ 5,8 mm  (para assentar até o fundo; a boca do receptáculo fica 0,40 mm acima da flange)'],
        ['Casca, seção', 'modelada 8,25 × 2,4 mm; a cavidade do receptáculo é 8,34 × 2,56 mm'],
        ['Sobremolde', '≤ 11,6 × 6,4 mm  (modelo: 11,6 × 6,4 × 17 mm, r 2,8)'],
        ['Sobremolde + alívio', '≤ 24,5 mm de comprimento total'],
        ['Alívio (bota)', '≤ Ø6,4 mm nos últimos 4,5 mm  ·  modelo: Ø6,0 → Ø4,2 × 7 mm'],
        ['Capa (jaqueta)', 'Ø3,5 a 4,0 mm  (modelo: Ø3,8)  ·  o passa-cabo P05 foi aberto em Ø3,3 para este intervalo'],
        ['Passagem na tampa', 'o sobremolde (diagonal 11,65 mm) passa no furo Ø12,8 com 0,57 mm por lado; plugues até 12,3 × 6,8 com r ≥ 3 também passam'],
        ['Retenção', 'especificação USB-C de força de retenção do plugue ≥ 8 N; aceite do produto: 10 N por 5 s sem soltar a tampa'],
        ['Amostra', 'obrigatória: medir casca, sobremolde, alívio e capa antes de fechar o pedido'],
        ['Não modelado', 'os 225 mm do CAD vão do alívio até atrás do monitor; o restante do 1,5 m não está no STEP'],
    ]
    F.tabela(['Item', 'Especificação'], rows, [80, 308], wrap_cols={1}, fonts=['Work', 'Work'], size=6.2, cab_size=5.85)


def l_materiais(F):
    F.titulo('MATERIAIS, TOLERÂNCIAS E ACABAMENTOS')
    F.glossario('Nenhum part number de material está confirmado. Lista de possíveis fornecedores no Brasil e na China: pendente/materiais.md (a verificar).')
    F.para('Fornecedores abaixo são opções para cotar, não fornecedores validados. Nenhum foi contatado neste pacote. Graus exatos de resina: a verificar (materiais.md do Pendente).')
    rows = [
        ['P01 tubo', 'PC opalino extrudado', 'Makrolon LED/diffuser ou Lexan difusor, 50–65 % de transmitância, UV, V-2 ou melhor  ·  a verificar', 'PMMA opalino; vidro jateado'],
        ['P02 tampa', 'Al 6061-T6', 'Barra Ø20–22, ASTM B211 ou equivalente ABNT', '6082-T6; latão niquelado preto'],
        ['P02 acabamento', 'Anodização tipo II preta, selada', 'MIL-A-8625 Tipo II Classe 2, 10–15 µm, microesfera, Ra 0,8–1,6 µm', 'Tipo III (mais cara, mais acinzentada)'],
        ['P02b protótipo', 'PA12 MJF preto ou SLA preto fosco', 'tolerância ±0,1–0,2 mm sem molde', 'FDM PETG (só encaixe)'],
        ['P03 berço', 'PC branco refletivo', 'refletância > 90 %, grau a verificar', 'PC+ABS branco; POM branco'],
        ['P04 tampão', 'PC opalino (mesmo do tubo)', 'mesma cor e difusão da ponta inferior', 'PMMA opalino'],
        ['P06 botão', 'PC opalino', 'mesmo sistema visual do tampão', 'SLA translúcido no protótipo'],
        ['P05 passa-cabo', 'TPE 60 Shore A preto (TPE-S/SEBS)', 'soft touch, fenda moldada ou cortada 0,3 mm', 'silicone 60A; amostras 50/60/70A'],
        ['C01 cabo', 'USB-C ↔ USB-C 1,5 m, trançado', 'USB 2.0, 3 A; envelope do plugue nesta seção', 'USB-C ↔ USB-A (decisão em aberto)'],
    ]
    F.tabela(['Peça', 'Material', 'Especificação / nota', 'Alternativa'],
             rows, [56, 80, 152, 100], wrap_cols={2, 3},
             fonts=['Work', 'Work', 'Work', 'Work'], size=6.1, cab_size=5.85)


def l_massas(F):
    F.titulo('MASSAS E ENVELOPE')
    F.glossario('Fontes: signa-3d/docs/verificacao_montagem.txt (bloco de massas) e caderno conceitual, dados/produto.json (envelope).')
    F.L.image_fit(JPG('iso'), 246, 126, 158, 114, 'mini iso', anchor='c')
    F.set_box(M, 214, y=F.y, min_y=F.base_min_y)
    rows = [
        ['P01 tubo', '3,94'],
        ['P02 tampa Al', '10,97'],
        ['P03 berço', '2,10'],
        ['P04 tampão', '0,95'],
        ['P05 passa-cabo', '0,97'],
        ['P06 botão', '0,06'],
        ['E01 placa (est.)', '≈ 1,0'],
        ['Total sem cabo', '≈ 20,0'],
    ]
    F.tabela(['Peça', 'Massa (g)'], rows, [134, 80], aligns=['l', 'r'], fonts=['Work', 'Mono'], bold_rows=(7,))
    F.set_box(M, W - 2 * M, y=min(F.y, 120.0), min_y=F.base_min_y)
    F.rotulo('ENVELOPE')
    F.kv_list([
        ('Diâmetro da tampa', 'Ø19 mm'),
        ('Diâmetro do tubo', 'Ø16 mm'),
        ('Altura do corpo', '78,0 mm'),
        ('Com a bota do passa-cabo', '88,2 mm'),
        ('Botão abaixo do tampão', '0,3 mm'),
        ('Massa (origem)', 'volumes do CAD × densidade'),
        ('Densidades usadas', 'Al 2,70  ·  PC 1,20  ·  TPE 1,10  ·  FR-4 1,85 g/cm³'),
        ('Escala dos desenhos de peça', 'ver cota em cada LXP-P0n'),
        ('Projeção', '1.º diedro, NBR 10067'),
        ('Tolerância geral', 'ISO 2768-mK'),
    ], key_w=120, k_size=6.5, v_size=6.5, line_div=False)
    F.para('As massas são estimativas (não foram pesadas peças reais). O cabo C01 de 1,5 m não entra nos 20 g. O botão adiciona 0,06 g — irrelevante para o envelope, relevante só para o critério de « peça solta » na assistência.')


def l_monta_prep(F):
    F.titulo('INSTRUÇÕES DE MONTAGEM  ·  PREPARAÇÃO')
    F.glossario('Fontes: pendente/montagem.md (base) + signa-3d/README e verificacao_montagem (delta rev B). Tempo e forças de press-fit não foram remedidos na rev B.')
    F.para('Sem parafusos e sem cola. Tempo-alvo ≈ 4 min (pacote Pendente), mais o encaixe do P06. Ferramentas: luvas de algodão (não marcar a anodização), gabarito de apoio impresso (opcional), dinamômetro de mão para o teste final. A sequência abaixo atualiza a do Pendente rev A para a rev B (orelhas, botão, cabo). As fotos dos passos 1–5 são do Pendente rev A e servem só de referência visual da ordem geral — a geometria das orelhas e do P06 não aparece nelas.')
    rows = [
        ['Antes', 'A placa rev D já deve estar gravada e testada (procedimento de teste, seções elétricas). Depois de montada, o Tag-Connect J2 fica coberto pelo berço.'],
        ['Orientação', 'LEDs para a frente (sala), USB-C para cima (tampa), botão S1 para baixo (tampão).'],
        ['Inspeção da placa', 'Sem rebarba de V-cut ou fresa nas orelhas e na borda de baixo. Orelhas íntegras (não quebradas no despainel). S1 presente e alinhado à borda.'],
        ['Inspeção das peças', 'Tubo sem riscos na superfície fosca; anodização da tampa sem marcas; trilhos de 0,6 mm do berço íntegrros; colar do P06 livre de rebarba.'],
        ['P06 no tampão', 'Antes ou na hora do passo do tampão: deixar o pino P06 cair no rebaixo Ø4,8 do P04, colar para baixo, empurrador para cima. Retido por gravidade; não cola.'],
        ['Forças de referência', 'Press-fit do tampão ≈ 20–40 N (Pendente). Extração do cabo no aceite: 10 N por 5 s. Chave S1: 1,6 N (é preciso segurar o tubo para apertar). Força de inserção do P06: a definir (não quantificada além do curso).'],
        ['Não fazer', 'Não forçar a placa se ela prender na ranhura. Não apoiar a borda de baixo como se fosse o batente — o batente são as orelhas na flange. Não apertar o botão com a sonda SWD conectada.'],
    ]
    # preserve exact spelling 'íntegros'
    rows[3][1] = 'Tubo sem riscos na superfície fosca; anodização da tampa sem marcas; trilhos de 0,6 mm do berço íntegros; colar do P06 livre de rebarba.'
    F.tabela(['Tema', 'Instrução'], rows, [76, 312], wrap_cols={1}, fonts=['Work', 'Work'], size=6.2, cab_size=5.85)


def l_monta_13(F):
    F.titulo('MONTAGEM  ·  PASSOS 1 A 3')
    F.glossario('A folga placa–tampão após a montagem deve ser cerca de 2,05 mm. O corpo do S1 deve ficar a 3,68 mm do tubo.')
    F.L.image_fit(JPG('passo1'), M, 134, 120, 104, 'p1', anchor='c')
    F.L.image_fit(JPG('passo2'), 148, 134, 120, 104, 'p2', anchor='c')
    F.L.image_fit(JPG('passo3'), 280, 134, 120, 104, 'p3', anchor='c')
    F.L.caption(M, 124, 'Fig.  —  Referência visual da ordem (fotos do Pendente rev A). Na rev B a placa entra até as orelhas apoiarem, e o P06 vai no tampão.', width=388)
    F.y = 104
    rows = [
        ['1  ·  Placa no berço',
         'Deslizar a placa (LEDs à frente, USB-C para cima) pelas ranhuras do berço P03, de cima para baixo, até as orelhas apoiarem no piso das fendas da flange (Z = 50,75). A borda de baixo deve ficar cerca de 0,30 mm acima do fundo da ranhura — não é batente. Não forçar: se prender, verificar rebarba da borda ou das orelhas.'],
        ['2  ·  Botão no tampão',
         'Colocar o P06 no rebaixo Ø4,8 × 1,0 do tampão P04 (colar para o fundo, empurrador para o lado da haste do S1). Conferir se o pino corre no furo Ø3,2 com folga e não cai para fora quando o tampão está com a boca para baixo — o colar é o retentor.'],
        ['3  ·  Tubo',
         'Passar o tubo P01 por baixo, cobrindo a placa, até encostar na flange do berço. Segurar o tubo pelas pontas (evitar dedos na superfície fosca). O tubo tem 48 ±0,2 mm; essa tolerância entra no pior caso da folga do botão (0,0 a 0,8 mm).'],
    ]
    F.tabela(['Passo', 'Instrução'], rows, [74, 314], wrap_cols={1}, fonts=['WorkM', 'Work'], size=6.2, cab_size=5.85)


def l_monta_46(F):
    F.titulo('MONTAGEM  ·  PASSOS 4 A 6')
    F.glossario('« O tubo entra 4 mm na tampa » vem de montagem.md do Pendente; a geometria da tampa não mudou na rev B. Revalidar no primeiro lote da rev B.')
    F.L.image_fit(JPG('passo4'), M, 134, 186, 104, 'p4', anchor='c')
    F.L.image_fit(JPG('passo5'), 214, 134, 186, 104, 'p5', anchor='c')
    F.L.caption(M, 124, 'Fig.  —  Referência visual: tampa e cabo (Pendente rev A). Na rev B a boca do USB-C está 0,40 mm acima da flange; não há rebaixo de sobremolde.', width=388)
    F.y = 104
    rows = [
        ['4  ·  Tampão',
         'Encaixar o tampão P04 (já com o P06) na ponta de baixo, alinhando o furo à haste do S1, e apertar até o tampão encostar no tubo (press-fit, ≈ 20–40 N). O tubo deve ficar sem folga axial. Conferir: o botão sai ≈ 0,3 mm e, ao ser apertado, aciona a chave (curso nominal 0,60 mm) sem emperrar.'],
        ['5  ·  Tampa',
         'Empurrar o conjunto para dentro da tampa P02 (alinhar os dentes da flange com a frente/trás) até o clique dos dois dentes na ranhura interna. Conferir: o tubo entra 4 mm na tampa e não gira com facilidade; as orelhas ficam sob o ressalto da tampa (0,25 mm de folga axial).'],
        ['6  ·  Cabo e passa-cabo',
         'Passar o plugue C01 pelo furo Ø12,8 do topo da tampa e encaixar no USB-C da placa até travar (casca exposta ≥ 5,8 mm). Abrir o passa-cabo P05 pela fenda, envolver o cabo logo acima da tampa e empurrar no furo até a garra travar sob a parede. Teste final: puxar o cabo com 10 N por 5 s; acender branco; conferir aparência e o botão.'],
    ]
    F.tabela(['Passo', 'Instrução'], rows, [74, 314], wrap_cols={1}, fonts=['WorkM', 'Work'], size=6.2, cab_size=5.85)


def l_desmonta(F):
    F.titulo('DESMONTAGEM E ASSISTÊNCIA')
    F.glossario('Base: pendente/montagem.md, seção Desmontagem, adaptada à rev B (P06 e orelhas).')
    rows = [
        ['1', 'Tirar o passa-cabo: puxar para cima e abrir pela fenda.'],
        ['2', 'Desconectar o cabo do receptáculo (não puxar só pela capa: o alívio e a casca devem sair juntos).'],
        ['3', 'Puxar o tampão com uma alavanca plástica na junta com o tubo. O P06 deve vir junto, retido no rebaixo; se cair, não é defeito elétrico — recolocar.'],
        ['4', 'Tirar o tubo pelas pontas, sem arrastar a superfície fosca na mesa.'],
        ['5', 'Deslizar a placa para cima, saindo pelas ranhuras. Não fazer alavanca nas orelhas.'],
        ['6', 'Para soltar o berço da tampa, pressionar os dois dentes por dentro com uma pinça. Em uso normal não é preciso.'],
    ]
    F.tabela(['Passo', 'Instrução'], rows, [28, 360], wrap_cols={1}, fonts=['Mono', 'Work'])
    F.para('A placa pode ser regravada por DFU (botão ao ligar o cabo, com nBOOT_SEL = 0) sem abrir o corpo. Só é preciso abrir para acessar o Tag-Connect, trocar a placa ou inspecionar o press-fit. Não usar cola UV (F02) a não ser como contingência se o press-fit do pino do berço soltar — e nesse caso registrar o desvio.')
    F.para('Peças de desgaste esperadas: passa-cabo (elastômero), cabo (flexão) e, a longo prazo, a chave S1. Vida útil em ciclos: a definir. O tubo e a tampa devem ser tratados como peças de aparência: um risco na anodização ou no fosco é motivo de troca estética, não de falha funcional.')


def l_manufatura(F):
    F.titulo('MANUFATURA  ·  PROTÓTIPO E SÉRIE')
    F.glossario('Estimativas de ferramental e rotas: pendente/manufatura.md e bom_completa.md. Nenhuma cotação formal foi pedida. Ver também o checklist de RFQ no apêndice de pendências.')
    rows = [
        ['P01 tubo', 'Protótipo e série: corte de tubo PC opalino extrudado, 48 ±0,2 mm, chanfro 0,2, jateado/fosco externo. Cotar MOQ em metros e matriz de extrusão se Ø16/13 não for padrão.'],
        ['P02 tampa', 'Protótipo: JLCCNC / PCBWay CNC + anodização preta. Série: torno CNC tipo suíço + anodização. Laser no topo opcional.'],
        ['P02b', 'Só protótipo: MJF PA12 preto ou SLA preto fosco (JLC3DP). Não soma no custo de série.'],
        ['P03 + P04 + P06', 'Protótipo: SLA branco (P03), SLA translúcido + jateado (P04 e P06); trilhos de 0,6 mm íntegros. Série: molde família em alumínio ou P20, cavidade extra para o P06. Ferramental estimado ≈ US$ 3 300 (família) — ver BOM.'],
        ['P05', 'Protótipo: silicone fundido em molde impresso ou TPU 3D. Série: injeção de TPE, molde 2–4 cavidades, ≈ US$ 1 000 de ferramental (estimativa). Fenda de 0,3 mm moldada ou cortada.'],
        ['C01 cabo', 'OEM de cabo em Shenzhen (ou distribuidor no Brasil). Exigir amostra medida contra o envelope desta seção e certificado de flexão.'],
        ['PCB + PCBA', 'JLCPCB (ou equivalente): gerber.zip + BOM + CPL da rev D, SMT de uma face, sem firmware na fábrica. Confirmar estoque do G8U6 e a prévia de rotação.'],
        ['Gravação e teste', 'Internos: DFU (ou SWD na primeira placa), option byte nBOOT_SEL = 0, procedimento de teste, etiqueta de série.'],
        ['Embalagem', 'Caixa 60 × 40 × 130 mm, berço de papelão, cartão A7 com QR, saco do tubo, etiqueta de série/lote.'],
    ]
    F.tabela(['Item', 'Rota'], rows, [68, 320], wrap_cols={1}, fonts=['Work', 'Work'], size=6.2, cab_size=5.85)
