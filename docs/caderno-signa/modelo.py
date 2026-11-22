"""Modelo de custos e de negócio do caderno conceitual.
Lê só dados/*.json e grava dados/resultados.json. Nenhum desenho aqui."""
import json, math, os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dados')
J = lambda n: json.load(open(os.path.join(D, n)))
C, N = J('custos.json'), J('negocio.json')
JLC = J('jlc_precos_2026-11-22.json')['parts']
FX = C['cambio']['usd_brl']


def preco_faixa(lcsc, qtd):
    p = None
    for f in JLC[lcsc]['prices']:
        if qtd >= f['startNumber']:
            p = f['productPrice']
    return p


def fator_importacao(lote):
    r = C['importacao'][str(lote)]
    if r['regime'].startswith('RTS'):
        return (1 + r['ii']) / (1 - r['icms_por_dentro']) - 1
    ii = r['ii']; ipi = r['ipi'] * (1 + ii)
    base = 1 + ii + ipi + r['pis'] + r['cofins']
    icms = base / (1 - r['icms_por_dentro']) - base
    return ii + ipi + r['pis'] + r['cofins'] + icms


def custo_lote(n, com_molde=True):
    k = str(n)
    pecas_un = sum(q * preco_faixa(code, q * n) for _, code, q in C['pecas_placa'])
    pecas = pecas_un * n + C['pcb_usd_lote'][k]                       # peças eletrônicas + PCB
    taxas = C['pcba_fixo_usd'][k] + C['juntas_por_placa'] * C['usd_por_junta'] * n
    frete = C['frete_usd_lote'][k]
    mec = (C['mecanica_usd_un'][k] + C['cabo_usd_un'][k]) * n
    molde = C['molde_usd'][k] if com_molde else 0
    sub_usd = pecas + taxas + frete + mec + molde                     # valor aduaneiro (CIF) em US$
    f = fator_importacao(n)
    R = lambda v: float(round(v))                                       # tabelas em R$ inteiros: os totais fecham
    b = dict(pecas=R(pecas * FX), pcba=R(taxas * FX), frete=R(frete * FX), mec=R(mec * FX), molde=R(molde * FX))
    b['subtotal'] = sum(b.values())
    b['impostos'] = R(b['subtotal'] * f)
    b['despachante'] = R(C['importacao'][k]['despachante_brl'])
    b['embalagem'] = R(C['embalagem_brl_un'][k] * n)
    b['montagem'] = R(C['montagem_min_un'][k] / 60 * C['hora_brl'] * n)
    total_brl = b['subtotal'] + b['impostos'] + b['despachante'] + b['embalagem'] + b['montagem']
    return dict(lote=n, pecas_un_usd=pecas_un, subtotal_usd=sub_usd, fator_imp=f, brl=b,
                total_brl=total_brl, total_usd=total_brl / FX, unit_brl=total_brl / n, unit_usd=total_brl / n / FX,
                comp=dict(pecas=b['pecas'], taxas_frete=b['pcba'] + b['frete'] + b['despachante'],
                          mecanica_acess=b['mec'] + b['molde'] + b['embalagem'] + b['montagem'], impostos=b['impostos']))


def simples(receita):
    for teto, aliq, ded in N['simples_anexo_ii']:
        if receita <= teto:
            return max(0.0, (receita * aliq - ded) / receita) if receita > 0 else 0
    return N['simples_anexo_ii'][-1][1]


CUSTO_UN = custo_lote(1000, com_molde=False)['unit_brl']
L5 = custo_lote(5)


def investimento(cpv1):
    itens = []
    for it in N['investimento']:
        t = it.get('tipo')
        if t == 'molde':
            v = C['molde_usd']['1000'] * (1 + fator_importacao(1000)) * FX
        elif t == 'prototipos':
            v = it['rodadas'] * L5['total_brl']
        elif t == 'giro':
            v = N['giro_pct_cpv'] * cpv1
        elif 'usd' in it:
            v = it['usd'] * FX
        else:
            v = it['brl']
        itens.append((it['item'], float(round(v))))
    return itens


def fluxo(preco, vol_mult=1.0, custo_un=None):
    cu = CUSTO_UN if custo_un is None else custo_un
    un = [u * vol_mult for u in N['unidades']]
    cpv = [u * cu for u in un]
    inv = investimento(cpv[0]); I0 = sum(v for _, v in inv)
    giro = [N['giro_pct_cpv'] * c for c in cpv]
    anos = []
    for t in range(len(un)):
        R = lambda v: float(round(v))
        rec = R(un[t] * preco)
        aliq = simples(rec)
        imp = R(rec * aliq); com = R(rec * N['comissao']); fre = R(un[t] * N['frete_absorvido_brl']); gar = R(rec * N['garantia'])
        cp = R(cpv[t])
        var = cp + com + fre + imp + gar
        fix = N['fixos_ano_brl']
        op = rec - var - fix
        dg = R((giro[t + 1] - giro[t]) if t + 1 < len(un) else -giro[t])
        fcl = op - dg
        anos.append(dict(ano=t + 1, unidades=un[t], receita=rec, aliq=aliq, cpv=cp, comissao=com, frete=fre,
                         impostos=imp, garantia=gar, variaveis=var, fixos=fix, operacional=op, dgiro=dg, fcl=fcl))
    return I0, inv, anos


def indicadores(I0, anos, tma=N['tma']):
    fl = [-I0] + [a['fcl'] for a in anos]
    vpl = sum(f / (1 + tma) ** t for t, f in enumerate(fl))
    def npv(r): return sum(f / (1 + r) ** t for t, f in enumerate(fl))
    lo, hi = -0.99, 10.0
    tir = None
    if npv(lo) * npv(hi) < 0:
        for _ in range(200):
            m = (lo + hi) / 2
            if npv(lo) * npv(m) <= 0: hi = m
            else: lo = m
        tir = (lo + hi) / 2
    def payback(disc):
        acc = -I0; prev = acc
        for t, f in enumerate(fl[1:], 1):
            v = f / (1 + tma) ** t if disc else f
            acc += v
            if acc >= 0:
                return t - 1 + (-prev) / v
            prev = acc
        return None
    acum, acum_d = [], []
    a = 0; ad = 0
    for t, f in enumerate(fl):
        a += f; ad += f / (1 + tma) ** t
        acum.append(a); acum_d.append(ad)
    roi = sum(fl[1:]) / I0 - 1
    return dict(vpl=vpl, tir=tir, payback=payback(False), payback_desc=payback(True), roi=roi,
                fluxos=fl, acumulado=acum, acumulado_desc=acum_d)


def vpl_preco(p, vm=1.0):
    I0, _, an = fluxo(p, vm)
    return indicadores(I0, an)['vpl']


def resolve(f, lo, hi):
    for _ in range(200):
        m = (lo + hi) / 2
        if f(lo) * f(m) <= 0: hi = m
        else: lo = m
    return (lo + hi) / 2


def main():
    lotes = [custo_lote(n) for n in C['lotes']]
    sem_molde = custo_lote(1000, com_molde=False)
    pmin = resolve(lambda p: vpl_preco(p), 50, 2000)
    psug = math.ceil(pmin * (1 + N['margem_seguranca']) / 10) * 10 - 1
    if psug < pmin * (1 + N['margem_seguranca']):
        psug += 10
    I0, inv, anos = fluxo(psug)
    ind = indicadores(I0, anos)
    _, _, anos_min = fluxo(pmin)
    ind_min = indicadores(I0, anos_min)
    vm_eq = resolve(lambda v: vpl_preco(psug, v), 0.05, 1.0)
    curva = [(p, vpl_preco(p)) for p in range(100, 361, 10)]
    precos_m = [pmin, psug * 0.9, psug, psug * 1.15]
    matriz = [[vpl_preco(p, v) for v in N['matriz_volumes']] for p in precos_m]
    U = sum(a['unidades'] for a in anos); R = sum(a['receita'] for a in anos)
    comp = dict(custo=CUSTO_UN, comissao=psug * N['comissao'], frete=N['frete_absorvido_brl'],
                impostos=sum(a['impostos'] for a in anos) / U, garantia=psug * N['garantia'],
                fixos=N['fixos_ano_brl'] * len(anos) / U, investimento=I0 / U)
    comp['margem'] = psug - sum(comp.values())
    res = dict(cambio=FX, lotes=lotes, lote1000_sem_molde=sem_molde, custo_un_plano=CUSTO_UN,
               investimento=inv, I0=I0, anos=anos, indicadores=ind, preco_min=pmin, preco_sug=psug,
               vpl_no_minimo=ind_min['vpl'], tir_no_minimo=ind_min['tir'],
               volume_equilibrio_mult=vm_eq, volume_equilibrio_un=vm_eq * sum(N['unidades']),
               curva_vpl_preco=curva, matriz_precos=precos_m, matriz_volumes=N['matriz_volumes'], matriz_vpl=matriz,
               composicao_preco=comp, unidades_total=U, receita_total=R)
    json.dump(res, open(os.path.join(D, 'resultados.json'), 'w'), ensure_ascii=False, indent=1)
    return res


if __name__ == '__main__':
    r = main()
    for l in r['lotes']:
        print(f"lote {l['lote']:>5}: total R$ {l['total_brl']:,.2f}  un R$ {l['unit_brl']:,.2f} (US$ {l['unit_usd']:.2f}) fator imp {l['fator_imp']:.3f}")
    print('1000 sem molde un R$', round(r['lote1000_sem_molde']['unit_brl'], 2))
    for n, v in r['investimento']: print(f'  {n}: {v:,.0f}')
    print('I0', round(r['I0']), 'pmin', round(r['preco_min'], 2), 'psug', r['preco_sug'])
    i = r['indicadores']; print('VPL', round(i['vpl']), 'TIR', i['tir'], 'pb', i['payback'], i['payback_desc'], 'ROI', i['roi'])
    print('vpl@min', r['vpl_no_minimo'], 'tir@min', r['tir_no_minimo'], 'veq', r['volume_equilibrio_mult'], r['volume_equilibrio_un'])
    for a in r['anos']: print({k: round(v, 3) if isinstance(v, float) else v for k, v in a.items()})
    print(r['composicao_preco'])
    print([[round(x) for x in row] for row in r['matriz_vpl']], [round(p) for p in r['matriz_precos']])
