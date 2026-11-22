"""Plano de negócio do indicador rev A: ciclo de vida, fluxo de caixa e preço (R$).

Todas as premissas são hipóteses de planejamento, explícitas abaixo, para serem
revistas com dados reais de mercado. TMA = 14 % a.a. (nominal).
"""
import custos

TMA = 0.14
FX = custos.FX

# ciclo de vida: unidades vendidas por ano (ano 1 = lançamento)
PHASES = ["introdução", "crescimento", "crescimento", "maturidade", "declínio"]
UNITS = [300, 1200, 2400, 2800, 1300]

# custo unitário posto no Brasil (R$), sem o molde: ano 1 em lotes pequenos, depois lotes de 1000
_r = custos.compute()[1000]
UNIT_COST_SERIE = (_r["total"] - 6500 * 1.70) / 1000 * FX         # ~R$ 50
UNIT_COST = [UNIT_COST_SERIE * 1.25] + [UNIT_COST_SERIE] * 4

INVEST = [  # ano 0
    ("Molde de injeção (família, 3 cavidades)", 6500 * FX),
    ("Engenharia e protótipos (lotes de 5 e 100, ferramentas)", 15000.0),
    ("Ensaios EMC de pré-conformidade", 8000.0),
    ("Marca (INPI), site, fotos e lançamento", 7000.0),
]
WC_MONTHS = 3                 # capital de giro: estoque de 3 meses do custo do ano seguinte

CHANNEL = 0.14                # comissão de marketplace / gateway sobre o preço
SHIPPING = 14.0               # frete absorvido por pedido (R$)
TAX = 0.08                    # Simples Nacional, alíquota efetiva estimada sobre a receita
WARRANTY = 0.03               # devoluções e garantia sobre a receita
FIXED = [30000, 30000, 27000, 24000, 15000]   # marketing, ferramentas, contabilidade (R$/ano)


def cashflow(price, units=UNITS):
    inv = sum(v for _, v in INVEST)
    years = []
    wc_prev = WC_MONTHS / 12 * units[0] * UNIT_COST[0]
    fcf0 = -inv - wc_prev
    for i, (q, uc, fx) in enumerate(zip(units, UNIT_COST, FIXED)):
        rev = price * q
        var = q * (uc + SHIPPING) + rev * (CHANNEL + TAX + WARRANTY)
        ebitda = rev - var - fx
        wc_next = WC_MONTHS / 12 * units[i + 1] * UNIT_COST[i + 1] if i + 1 < len(units) else 0.0
        dwc = wc_next - wc_prev
        wc_prev = wc_next
        fcf = ebitda - dwc
        years.append(dict(year=i + 1, units=q, rev=rev, var=var, fixed=fx, ebitda=ebitda, dwc=dwc, fcf=fcf))
    return fcf0, years, inv


def npv(rate, flows):
    return sum(f / (1 + rate) ** t for t, f in enumerate(flows))


def irr(flows):
    lo, hi = -0.99, 10.0
    if npv(hi, flows) > 0:
        return float("inf")
    for _ in range(200):
        mid = (lo + hi) / 2
        if npv(mid, flows) > 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def payback(flows, rate=0.0):
    acc = 0.0
    for t, f in enumerate(flows):
        d = f / (1 + rate) ** t
        if acc + d >= 0 and t > 0:
            return t - 1 + (-acc) / d
        acc += d
    return None


def evaluate(price, units=UNITS):
    f0, ys, inv = cashflow(price, units)
    flows = [f0] + [y["fcf"] for y in ys]
    return dict(price=price, flows=flows, years=ys, invest=inv, wc0=-f0 - inv,
                npv=npv(TMA, flows), irr=irr(flows), pb=payback(flows), dpb=payback(flows, TMA),
                roi=sum(flows[1:]) / -flows[0] - 1)


def breakeven_price(units=UNITS):
    lo, hi = 50.0, 2000.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if evaluate(mid, units)["npv"] > 0:
            hi = mid
        else:
            lo = mid
    return hi


P_MIN = breakeven_price()
P_SUG = 179.0      # preço sugerido (R$): VPL > 0 mesmo com 50 % do volume previsto


def unit_build(price):
    """Composição do preço sugerido por unidade, ano de maturidade."""
    uc = UNIT_COST_SERIE
    parts = [("custo do produto", uc), ("frete", SHIPPING), ("canal", price * CHANNEL),
             ("impostos", price * TAX), ("garantia", price * WARRANTY),
             ("fixos rateados", FIXED[3] / UNITS[3])]
    margin = price - sum(v for _, v in parts)
    return parts + [("margem", margin)]


if __name__ == "__main__":
    print("custo unitário série R$", round(UNIT_COST_SERIE, 2))
    print("preço mínimo (VPL=0) R$", round(P_MIN, 2))
    for p in (P_MIN, P_SUG):
        e = evaluate(p)
        print(round(p, 2), "VPL", round(e["npv"]), "TIR", round(e["irr"] * 100, 1), "%",
              "payback", e["pb"] and round(e["pb"], 2), "desc", e["dpb"] and round(e["dpb"], 2),
              "ROI", round(e["roi"] * 100), "%", "inv", round(e["invest"]), "giro", round(e["wc0"]))
        for y in e["years"]:
            print("  ", {k: round(v) for k, v in y.items()})
    print(unit_build(P_SUG))
