"""Conformidade, custo, riscos e pendências."""
from lib_metrologia import *
from helpers import *
import dados as D


def register(book):
    book.divisor('VII', 'CONFORMIDADE, CUSTO E RISCOS', [
        'As notas desta seção são considerações de projeto, não certificações e não laudos de laboratório.',
        'O custo do produto montado é US$ 18,53 no lote de 100 e US$ 11,32 no de 1 000, com a eletrônica cotada e o resto em estimativa.',
        'As decisões em aberto e os itens a definir estão listados para não se perderem entre as lâminas técnicas.',
    ], short='CONFORMIDADE E RISCOS')
    book.add_flow('VII  CONFORMIDADE, CUSTO E RISCOS', 'Considerações de conformidade', l_conf, 'CONFORMIDADE')
    book.add_flow('VII  CONFORMIDADE, CUSTO E RISCOS', 'Custo do produto', l_custo)
    book.add_flow('VII  CONFORMIDADE, CUSTO E RISCOS', 'Riscos e decisões em aberto', l_riscos, 'RISCOS E DECISÕES')
    book.add_flow('VII  CONFORMIDADE, CUSTO E RISCOS', 'Itens a definir', l_adefinir)
    book.add_flow('VII  CONFORMIDADE, CUSTO E RISCOS', 'Fontes e referências', l_fontes)


def l_conf(F):
    F.titulo('CONSIDERAÇÕES DE CONFORMIDADE')
    F.glossario('Marcar qualquer citação externa desta lâmina como « consideração de projeto, sem ensaio ».')
    F.para('Nada nesta lâmina é certificação, declaração de conformidade ou substituto de ensaio. O SIGNA ainda não passou por laboratório de USB-IF, EMC, ANATEL, CE, FCC, IEC 62471 ou RoHS formal.')
    rows = [
        ['USB', 'O descritor declara um dispositivo HID Full Speed de 100 mA, com envelope igual ao Flag. Isso não equivale a uma certificação USB-IF. O par 1209:0001 é um Test PID e não pode ir em unidade distribuída. O par 04d8:f372 é da Microchip/Luxafor e não pode ir em produto vendido. Impedância do par D+/D− não é controlada (trecho curto, Full Speed).'],
        ['EMC / EMI', 'Não há ensaio. Fatores a favor, ainda não provados: Full Speed, transceptor no silício com CRS, TVS nas linhas USB, plano de GND, trilhas curtas. Fatores de risco: PWM dos LEDs e o burst SPI a 12 MHz no PA7. Qualquer declaração CE/FCC/ANATEL depende de ensaio no produto montado, com cabo de série.'],
        ['Fotossensibilidade (WCAG 2.3.1)', 'O estado ERRO foi especificado a 2,5 Hz com pulso de 130 ms, abaixo do limite de 3 Hz. Os demais ritmos estão em 1 Hz ou mais lentos. Isso é uma decisão de projeto, não um laudo de acessibilidade, e não cobre IEC 62471 (segurança fotobiológica), que não foi avaliada.'],
        ['RoHS / REACH / substâncias', 'Os componentes eletrônicos escolhidos na JLC/LCSC são, em regra, linha RoHS do catálogo — mas isso não foi auditado peça a peça neste caderno, e as resinas, o TPE, a anodização e o cabo OEM não têm ficha confirmada. Exigir declarações no RFQ.'],
        ['Elétrica / segurança', 'Alimentação só por VBUS 5 V, sem rede elétrica própria, sem bateria. A proteção é a da porta do computador mais o TVS das linhas de dados. Não há ensaio de isolamento, surto ou aquecimento além do orçamento de corrente estimado.'],
        ['ANATEL / mercado Brasil', 'Produto USB de baixa potência em geral se enquadra em regras específicas (produto de telecomunicação ou isenção). O enquadramento e o caminho de homologação: a definir com assessoria, não neste caderno.'],
    ]
    F.tabela(['Tema', 'Consideração  (não é certificação)'], rows, [76, 312],
             wrap_cols={1}, fonts=['WorkM', 'Work'], size=6.2, cab_size=5.85)


def l_custo(F):
    F.titulo('CUSTO DO PRODUTO  ·  LOTES DE 100 E 1 000')
    F.glossario('Fonte: signa-3d/bom/bom_completa.md, gerada por bom/gerar_bom.py em 22/11/2026, e CHANGELOG da rev D (delta).')
    F.para('Valores em US$ por produto montado. Só a eletrônica tem preço consultado (API de peças da JLCPCB, 22/11/2026). O restante é estimativa de ordem de grandeza e precisa de cotação. Não inclui frete, impostos de importação (no Brasil, II/IPI/ICMS podem somar 60–100 %), margem nem certificações.')
    rows1 = [
        ['Eletrônica (peças + PCB + PCBA + FW)', '3,47', '2,52'],
        ['Mecânica (P01–P06 + ferramental amortizado no lote 1 000)', '10,10', '6,43'],
        ['Cabo (C01 + adaptador C02)', '2,25', '1,25'],
        ['Embalagem', '1,15', '0,40'],
        ['Etiquetas (inclui laser opcional L02 na soma desta linha)', '0,36', '0,12'],
        ['Fixação / adesivos', '0,00', '0,00'],
        ['Montagem final + teste + embalagem', '1,20', '0,60'],
        ['Total', '18,53', '11,32'],
    ]
    F.tabela(['Categoria', 'US$ @100', 'US$ @1000'], rows1, [244, 72, 72],
             aligns=['l', 'r', 'r'], fonts=['Work', 'Mono', 'Mono'], bold_rows=(7,))
    rows2 = [
        ['Componentes eletrônicos (só peças)', '2,67', '2,26', 'consultado'],
        ['Delta eletrônico rev C → rev D (S1+R5+taxa)', '+0,15', '+0,10', 'consultado + rateio'],
        ['Delta de produto vs. Pendente rev A', '17,98 → 18,53  (+0,55)', '10,91 → 11,32  (+0,41)', 'estimativa'],
        ['P02b tampa impressa (protótipo, fora do total)', '1,50', '—', 'estimativa'],
        ['Ferramental no lote 1 000 (já dentro da mecânica)', '0,00', '4,30', 'estimativa (≈ 3 300 + 1 000)'],
        ['Lote 1 000 sem amortizar ferramental', '—', '7,02  (só mecânica) / total a recalcular', 'estimativa'],
    ]
    F.tabela(['Nota', '@100', '@1000', 'Base'], rows2, [120, 82, 92, 94],
             wrap_cols={0, 1, 2, 3}, fonts=['Work', 'Mono', 'Mono', 'Work'], size=6.1, cab_size=5.85)
    F.para('C02 (adaptador USB-A) entra no total; retirar se a decisão for não incluir. L02 (laser) está na linha de etiquetas da BOM. P02b e a cola de contingência F02 não entram no total. Risco de suprimento: o G8U6 tinha só 109 un. na JLC em 22/11/2026 — o preço do lote 1 000 usa a faixa de preço, não garante estoque.')


def l_riscos(F):
    F.titulo('RISCOS E DECISÕES EM ABERTO')
    F.glossario('Várias destas linhas reaparecem como « a definir » na lâmina seguinte, com o enunciado operacional.')
    rows = [
        ['Estoque do MCU', '109 un. na JLC, 36 na LCSC (22/11/2026). Apertado até para um lote de 100 com folga de falha. GBU6 e versões N: estoque 0, e o N não é drop-in. Ação: reservar, consignar ou achar distribuição (Mouser/Digi-Key citados no estoque, não verificados na página).'],
        ['Botão embaixo', '1,6 N contra ≈ 0,2 N de peso: o usuário segura o tubo. Decisão: aceitar, trocar por chave mais leve, ou levar o botão à tampa (flex ou fio, nova revisão de placa e de P02).'],
        ['nBOOT_SEL na produção', 'Sem isso, o DFU pelo botão/JP1 morre depois da 1.ª gravação. Precisa entrar no roteiro do posto de teste.'],
        ['Cabo OEM', 'O envelope é apertado (casca, sobremolde, capa). Sem amostra medida, o risco é lote inteiro que não assenta ou não passa no Ø12,8.'],
        ['Painelização', 'Orelhas de 15,2 mm quebradas no V-cut = perda da retenção axial, o modo de falha que a rev D veio corrigir.'],
        ['VID:PID', '1209:0001 não pode ir a mercado. Decisão de identidade USB trava embalagem, infografia e o app.'],
        ['Software ainda « rev C »', 'Strings, README e parte dos comentários não acompanharam a placa rev D (botão não lido). Risco de documentação divergente no campo.'],
        ['IA na web e limites 5 h/semanal', 'Heurística frágil; vai quebrar quando os sites mudarem. Não vender como recurso garantido no v1.'],
        ['Nada em silício', 'USB, CRS, SPI, flash, option bytes, botão, corrente e óptica só existem como testes de host e CAD. O primeiro lote é o ensaio verdadeiro.'],
        ['Custo mecânico', 'A tampa de alumínio domina o custo @100 (US$ 5,50 est.). Sem cotação, o total de 18,53 pode andar bastante.'],
        ['Nome SIGNA', 'Provisório até o INPI. Embalagem, serigrafia e descritor USB dependem disso.'],
        ['Reset USB no PC de desenvolvimento', 'USBDEVFS_RESET já travou o kernel. Procedimento de laboratório: só replugue físico.'],
    ]
    F.tabela(['Risco', 'Por que importa'], rows, [78, 310], wrap_cols={1}, fonts=['WorkM', 'Work'], size=6.2, cab_size=5.85)


def l_adefinir(F):
    F.titulo('ITENS A DEFINIR')
    F.glossario('Qualquer número que apareça em outra lâmina como « a definir » deve ter correspondência nesta lista. A lista completa tem %d itens e está em dados.py, extraída das fontes.' % len(D.A_DEFINIR))
    rows = [[str(i + 1), t, d] for i, (t, d) in enumerate(D.A_DEFINIR)]
    F.tabela(['#', 'Item', 'Enunciado'], rows, [22, 76, 290],
             wrap_cols={1, 2}, fonts=['Mono', 'WorkM', 'Work'], size=6.15, cab_size=5.85)


def l_fontes(F):
    F.titulo('FONTES E REFERÊNCIAS')
    F.glossario('Datas das fontes: 8 a 22 de novembro de 2026. Qualquer reedição deve reler os arquivos, não só este PDF.')
    rows = [
        ['Placa rev D', 'luxpcb-revD/  ·  CHANGELOG.md, README.md, tools/netlist.py, project/, fab/, reports/, docs/ (firmware_comportamento.md, pendencias.md, captura_logica.md, estoque, jlc_revD, parts-check, DS14693 em c071.txt)'],
        ['Mecânica rev B', 'signa-3d/  ·  README.md, cad/, desenhos LXP-A00 e P01–P06, bom/, docs/verificacao_montagem, renders/, export/ (STEP/GLB do conjunto)'],
        ['Pendente rev A', 'pendente/  ·  materiais.md, manufatura.md, montagem.md, teste.md, rfq_checklist.md (base de processo; não vale onde a rev B alterou a geometria)'],
        ['Software 0.1', 'signa-sw/  ·  docs/README.md, docs/arquitetura.md, firmware/src/*, Makefile, linker, app/signa/*, testes'],
        ['Protocolo original', 'PROTOCOLO.md e docs/FUNCIONAMENTO.md (luxafor, firmware 0x3C, 2026-11)'],
        ['Conceito', 'caderno-revC/  ·  signa-conceito.pdf, dados/produto.json, premissas.md, escolhas_design.md, lib_metrologia.py'],
        ['Datasheets', 'WS2816B-2020, STM32C071 (DS14693), SN74AHCT1G125, AP2112K-3.3, USBLC6-2SC6, SKRTLAE010 — em luxpcb-revD/docs/ds e docs/c071'],
        ['Preços', 'API JLCPCB 22/11/2026; LCSC no parts-check do mesmo dia. Mecânica: estimativa, sem cotação formal.'],
    ]
    F.tabela(['Bloco', 'Onde está'], rows, [72, 316], wrap_cols={1}, fonts=['WorkM', 'Work'], size=6.2, cab_size=5.85)
    F.para('Este caderno não altera as fontes. Foi gerado em 22/11/2026 no mesmo sistema visual do caderno conceitual (Metrologia Luminosa: Jura, Geist Mono, Work Sans, Instrument Serif).')
