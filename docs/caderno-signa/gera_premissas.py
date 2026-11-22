"""Gera premissas.md a partir de dados/*.json e dados/resultados.json (rodar depois de modelo.py)."""
import json, os
from lib_metrologia import br, brl
HERE = os.path.dirname(os.path.abspath(__file__))
J = lambda n: json.load(open(os.path.join(HERE, 'dados', n)))
PR, CU, NG, EN, R = J('produto.json'), J('custos.json'), J('negocio.json'), J('energia.json'), J('resultados.json')
I = R['indicadores']; FX = R['cambio']
pc = lambda v, d=1: br(v * 100, d) + ' %'
L = []
a = L.append
a(f"# Ficha de premissas · {PR['nome']} {PR['revisao']} · caderno conceitual")
a(f"\nData do estudo: {PR['data']}. Toda premissa abaixo tem uma de três origens: **ficha** (dado do usuário), **cotação** (fornecedor, código e data) ou **estimativa** (com o raciocínio). Impostos, câmbio e mercado foram consultados em 2026-11-22 e **precisam ser revistos antes de qualquer decisão**.\n")
a("## 0. Ficha do produto (preenchida)\n")
for k, v in [('NOME', f"{PR['nome']} ({PR['nome_nota']})"), ('REVISÃO', PR['revisao']), ('DATA', PR['data']), ('CATEGORIA', PR['categoria']),
             ('FRASE-SÍNTESE', PR['frase']), ('PROBLEMA', PR['problema']), ('USUÁRIO FINAL', PR['usuario']),
             ('COMO FUNCIONA', ' → '.join(PR['funcionamento'])),
             ('MODOS (SALA + IA)', '; '.join(f"[{m['grupo'].upper()}] {m['nome']} {m['hex']}: {m['sinal']} ({m['leds']})" for m in PR['modos'])),
             ('ALOCAÇÃO 3 LEDS', f"SALA: {PR['alocacao_leds']['sala_exclusivo']} | IA: {PR['alocacao_leds']['ia_exclusivo']} | MISTO: {PR['alocacao_leds']['misto']}"),
             ('DIFERENCIAL', '; '.join(PR['diferencial'])), ('ENVELOPE', 'Ø19 × 78 mm (88,2 mm com o passa-cabo), ≈ 20 g sem cabo (estimativa)'),
             ('SUBSISTEMA CENTRAL', 'placa rev C, 11 × 44 × 0,8 mm, 2 camadas (KiCad: `.old/hardware/revC/`; a placa atual é `hardware/revD/`)'),
             ('CARCAÇA', 'proposta "Pendente" (conjunto atual em `mecanica/`): tubo PC opalino Ø16, tampa Al Ø19, berço, tampão, passa-cabo; não prototipada'),
             ('MERCADO', 'Brasil, R$'), ('LOTES', '5 / 100 / 1.000'), ('TMA', '14 % a.a. (ficha)'), ('HORIZONTE', '5 anos (ficha)'),
             ('PÚBLICO-ALVO', 'investidores'), ('IDIOMA', 'pt-BR'), ('SAÍDA', 'PDF + código'), ('PESQUISA DE PREÇOS', 'sim')]:
    a(f"- **{k}:** {v}")
a("\n## 1. Câmbio\n")
a(f"- US$ 1 = R$ {br(FX, 4)} — **cotação**: {CU['cambio']['origem']}. O fechamento comercial de 20/11/2026 foi R$ 5,9488 (+1,0 %).")
a("- Sensibilidade (estimativa): o custo unitário importado é ~90 % dolarizado; +10 % no dólar ≈ +9 % no custo unitário.")
a("\n## 2. Custo por lote (lâmina 11)\n")
a(f"- **Peças eletrônicas:** {CU['pecas_origem']}. Arquivo: `dados/jlc_precos_2026-11-22.json`. Placa por unidade: US$ {br(R['lotes'][0]['pecas_un_usd'], 2)} (lote 5), US$ {br(R['lotes'][1]['pecas_un_usd'], 2)} (lote 100), US$ {br(R['lotes'][2]['pecas_un_usd'], 2)} (lote 1.000).")
for k, lab in [('pcb_usd_lote', 'PCB'), ('pcba_fixo_usd', 'Montagem SMT, custos fixos'), ('mecanica_usd_un', 'Mecânica'), ('molde_usd', 'Moldes'),
               ('cabo_usd_un', 'Cabo'), ('frete_usd_lote', 'Frete'), ('embalagem_brl_un', 'Embalagem')]:
    d = CU[k]; vals = ' / '.join(f"{br(d[str(n)], 2)}" for n in CU['lotes'])
    a(f"- **{lab}** ({vals} para 5 / 100 / 1.000): {d['origem']}.")
a(f"- **Juntas de solda:** {CU['juntas_por_placa']} × US$ {CU['usd_por_junta']} — {CU['juntas_origem']}.")
a(f"- **Montagem final, gravação e teste:** {CU['montagem_min_un']['5']} / {CU['montagem_min_un']['100']} / {CU['montagem_min_un']['1000']} min por unidade × R$ {br(CU['hora_brl'], 2)}/h — {CU['montagem_origem']}.")
a(f"- **Impostos de importação:** {CU['importacao']['origem']}. Fator RTS = (1 + 0,60) ÷ (1 − 0,20) − 1 = 100 %. Fator formal = {pc(R['lotes'][2]['fator_imp'])} (II 16 %; IPI 15 % sobre valor + II; PIS 2,1 %; COFINS 9,65 %; ICMS 18 % por dentro). Despachante no lote 1.000: R$ 2.500 (estimativa).")
a("- **Limite do RTS:** remessa até US$ 3.000; o lote 1.000 passa disso e vai para importação formal.")
a("- **Não incluídos:** perdas de peças (attrition) da JLC, armazenagem, seguro, IOF sobre o pagamento internacional (alíquota a confirmar).")
a("\n| lote | total R$ | R$/un. | US$/un. |\n|---|---|---|---|")
for l in R['lotes']:
    a(f"| {br(l['lote'])} | {br(l['total_brl'])} | {br(l['unit_brl'], 2)} | {br(l['unit_usd'], 2)} |")
a(f"| 1.000 sem molde | {br(R['lote1000_sem_molde']['total_brl'])} | {br(R['lote1000_sem_molde']['unit_brl'], 2)} | {br(R['lote1000_sem_molde']['unit_usd'], 2)} |")
a("\n## 3. Plano de negócio (lâminas 12 a 14)\n")
a(f"- **Volumes:** {', '.join(br(u) for u in NG['unidades'])} un. nos anos 1–5 (total {br(sum(NG['unidades']))}). {NG['unidades_origem']}. Raciocínio: nicho de acessório de mesa; o pico supõe ≈ 1 em cada 2.640 trabalhadores em casa comprando por ano.")
a(f"- **Custo unitário no plano:** R$ {br(R['custo_un_plano'], 2)} = lote 1.000 sem o molde (o molde entra como investimento do ano 0). Supõe compras sempre em lotes de 1.000.")
a(f"- **Comissão de canal:** {pc(NG['comissao'], 0)} — {NG['comissao_origem']}.")
a(f"- **Frete absorvido:** R$ {br(NG['frete_absorvido_brl'], 2)}/un. — {NG['frete_origem']}.")
a(f"- **Impostos sobre a receita:** {NG['impostos_origem']} Alíquotas efetivas resultantes: " + ', '.join(f"ano {x['ano']} {pc(x['aliq'])}" for x in R['anos']) + '.')
a(f"- **Garantia:** {pc(NG['garantia'], 0)} da receita — {NG['garantia_origem']}.")
a(f"- **Despesas fixas:** R$ {br(NG['fixos_ano_brl'])}/ano — {NG['fixos_origem']}. Não inclui pró-labore do fundador.")
a(f"- **Capital de giro:** {pc(NG['giro_pct_cpv'], 0)} do CPV do ano — {NG['giro_origem']}. Investido no ano 0 (giro do ano 1), ajustado a cada ano pelo giro do ano seguinte e liberado no ano 5.")
a(f"- **IR/CSLL:** não há linha separada; no Simples Nacional eles estão dentro da alíquota única.")
a("\n### Investimento do ano 0\n\n| item | R$ | origem |\n|---|---|---|")
for (n, v), it in zip(R['investimento'], NG['investimento']):
    o = it.get('origem', 'calculado: ' + {'molde': 'moldes US$ 4.000 × (1 + 77 %) × câmbio (o molde entra no valor aduaneiro)', 'prototipos': '2 × total do lote 5 (lâmina 11)', 'giro': '30 % do CPV do ano 1'}.get(it.get('tipo'), ''))
    a(f"| {n} | {br(v)} | {o} |")
a(f"| **total** | **{br(R['I0'])}** | |")
a("\n- **Certificações:** Anatel — periféricos USB com fio e sem rádio não são classificáveis como produto para telecomunicações (Requisitos Técnicos Cat. I, nota ORCN de 08/11/2024), logo R$ 0; confirmar no sistema Mosaico. INMETRO — não identificamos certificação compulsória para acessório USB de 5 V; confirmar com um OCP. EMC — ensaio voluntário de pré-conformidade (estimativa R$ 9.000), recomendado antes de exportar (FCC/CE).")
a("- **VID:PID:** o 04d8:f372 pertence a terceiros e não pode ser usado. Caso base: VID próprio da USB-IF, US$ 6.000 taxa única (cotação usb.org, 2026-11-22). Alternativas: pid.codes (gratuito, exige hardware e firmware abertos) ou sublicença de PID do fabricante do MCU (a verificar com a ST). Com pid.codes o investimento cai R$ 35.333 e o preço mínimo cai junto.")
a("\n## 4. Resultados\n")
a(f"- VPL a 14 % a.a.: **{brl(I['vpl'])}** · TIR: **{pc(I['tir'])}** · payback simples **{br(I['payback'], 2)} anos**, descontado **{br(I['payback_desc'], 2)} anos** · ROI no ciclo **{pc(I['roi'], 0)}** (soma dos FCL dos anos 1–5 ÷ investimento − 1).")
a(f"- Preço mínimo (VPL = 0, TIR = 14 %): **{brl(R['preco_min'], 2)}**. Conferência: VPL no mínimo = {brl(R['vpl_no_minimo'], 2)}; TIR no mínimo = {pc(R['tir_no_minimo'], 2)}.")
a(f"- Preço sugerido: **{brl(R['preco_sug'])}** = mínimo × (1 + {pc(NG['margem_seguranca'], 0)}) arredondado para cima com final 9.")
a(f"- Volume de equilíbrio no preço sugerido: {br(R['volume_equilibrio_un'])} un. em 5 anos ({pc(R['volume_equilibrio_mult'], 0)} do plano, mesmo perfil de anos).")
a(f"- Referência de mercado: {NG['referencia_mercado']}.")
a("\n## 5. Riscos\n")
for r in NG['riscos']: a(f"- {r}")
a("\n## 6. Engenharia e software\n")
a(f"- Consumo: {sum(i['mA'] for i in EN['itens'])} mA a 5 V no pior caso, com margem de 30 %; " + '; '.join(f"{i['nome']} {i['mA']} mA ({i['origem']})" for i in EN['itens']) + f". {EN['nota']}.")
a("- Massa ≈ 20 g: estimativa do CAD do Pendente (volumes × densidades), sem cabo.")
a("- Renders: conceituais, gerados a partir do CAD (KiCad → STL → Blender 4.2 Cycles). Não são fotos de protótipo. A carcaça, os materiais e o difusor não foram testados.")
a("- Firmware da rev C e daemon desktop (Google Calendar OAuth, Microsoft Graph/Outlook OAuth, hooks Claude Code, notify Codex CLI, extensão browser para ChatGPT/Claude/Grok web sem API oficial) ainda não foram implementados; a compatibilidade HID parte do protocolo decodificado (0x01–0x04, 0x06, 0x80 testados no Flag; 0x05 e 0x07–0x0F inexistentes).")
a("- **Aviso PRESTES A ENTRAR:** padrão 5 min antes do evento; configurável no app.")
a("- **Trava OCUPADO (v1):** SALA = OCUPADO sempre envia 0xFF em vermelho #FF3B2F e suprime o LED 1 da IA; não configurável nesta versão.")
a("- **Em aberto (a validar):** detecção dos limites de 5 h e semanal nas IAs (Claude, ChatGPT, Grok) e da extensão web (sem API oficial).")
open(os.path.join(HERE, 'premissas.md'), 'w').write('\n'.join(L) + '\n')
print('premissas.md ok')
