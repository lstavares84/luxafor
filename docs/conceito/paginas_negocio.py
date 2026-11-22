"""Lâminas 12–14: plano de negócio (ciclo de vida, retorno, preço)."""
from reportlab.lib.colors import HexColor

import negocio as N
from gerar_conceito import INK, INK2, INK3, INK4, M, PH, PW, STATES, dot_grid, frame, line, new_page, text
from paginas_extra import title

RED, AMB, GRN, BLU = STATES[4][1], STATES[2][1], STATES[0][1], STATES[1][1]


def brl(v, dec=0):
    s = f"{abs(v):,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("−" if v < 0 else "") + "R$ " + s


def num(v):
    return f"{v:,.0f}".replace(",", ".")


def kv(c, x, y, k, v, w=110, vcol=INK, big=False):
    text(c, x, y, k, "JuraM", 1.95, INK3, spacing=0.6)
    text(c, x + w, y, v, "Mono", 2.6 if big else 2.2, vcol, "r")
    line(c, x, y - 2.8, x + w, y - 2.8, 0.05, INK4)


def page_lifecycle(c):
    new_page(c)
    dot_grid(c, M + 4, M + 4, PW - M - 4, PH - M - 4, 5.0, HexColor("#E2DED5"), 0.14)
    top = PH - M - 24
    title(c, M + 6, top + 6, "CICLO DE VIDA")
    text(c, M + 6, top - 6.5, "cinco anos de mercado, do lançamento à substituição pela rev B", "Serif", 4.4, INK2)
    # gráfico de barras + curva
    gx, gy, gw, gh = M + 16, 92.0, 228.0, 118.0
    umax = 3000
    for k in range(0, umax + 1, 500):
        y = gy + gh * k / umax
        line(c, gx, y, gx + gw, y, 0.05 if k else 0.12, INK4 if k else INK)
        text(c, gx - 3, y - 0.8, num(k), "Mono", 1.8, INK3, "r")
    n = len(N.UNITS)
    bw = gw / n
    cols = [HexColor("#B9B4A8"), INK2, INK2, INK, HexColor("#8A857A")]
    pts = []
    for i, (q, ph) in enumerate(zip(N.UNITS, N.PHASES)):
        x = gx + i * bw + bw * 0.28
        h = gh * q / umax
        c.setFillColor(cols[i])
        c.rect(x, gy, bw * 0.44, h, stroke=0, fill=1)
        text(c, x + bw * 0.22, gy + h + 2.2, num(q), "Mono", 2.2, INK, "c")
        text(c, x + bw * 0.22, gy - 6, f"ANO {i + 1}", "JuraM", 1.95, INK2, "c", spacing=0.6)
        pts.append((x + bw * 0.22, gy + h))
    # curva suave do ciclo
    c.setStrokeColor(BLU)
    c.setLineWidth(0.35)
    p = c.beginPath()
    p.moveTo(gx, gy)
    prev = (gx, gy)
    for q in pts + [(gx + gw, gy + 6)]:
        mx = (prev[0] + q[0]) / 2
        p.curveTo(mx, prev[1], mx, q[1], q[0], q[1])
        prev = q
    c.drawPath(p, stroke=1, fill=0)
    # faixas de fase
    phases = [("INTRODUÇÃO", 0, 1), ("CRESCIMENTO", 1, 3), ("MATURIDADE", 3, 4), ("DECLÍNIO", 4, 5)]
    for nm, a, b in phases:
        xa, xb = gx + a * bw + 1.5, gx + b * bw - 1.5
        line(c, xa, gy + gh + 8, xb, gy + gh + 8, 0.25, INK)
        text(c, (xa + xb) / 2, gy + gh + 10.5, nm, "JuraM", 2.0, INK, "c", spacing=0.8)
    text(c, gx, gy - 14, f"total no ciclo: {num(sum(N.UNITS))} unidades", "Mono", 2.1, INK2)

    # estratégia por fase
    sy = 64.0
    strat = [
        ("INTRODUÇÃO", "lote piloto · venda direta a devs", "preço cheio, comunidade e reviews"),
        ("CRESCIMENTO", "molde · marketplaces · B2B", "kits para times, integrações abertas"),
        ("MATURIDADE", "custo mínimo · revendas", "rev B (multiagente, USB-C 2.0 sem LDO)"),
        ("DECLÍNIO", "liquidação de estoque", "suporte de firmware e peças de reposição"),
    ]
    cw = gw / 4
    for i, (nm, a, b) in enumerate(strat):
        x = gx + i * cw
        text(c, x, sy, nm, "JuraM", 1.9, INK3, spacing=0.6)
        text(c, x, sy - 5, a, "Sans", 2.1, INK)
        text(c, x, sy - 9.2, b, "Sans", 2.0, INK2)

    # investimento inicial
    rx = 290.0
    text(c, rx, top + 6, "INVESTIMENTO INICIAL", "Jura", 5.0, INK, spacing=1.2)
    y = top - 14
    e = N.evaluate(N.P_SUG)
    for k, v in N.INVEST:
        text(c, rx, y, k, "Sans", 2.1, INK)
        text(c, PW - M - 6, y, brl(v), "Mono", 2.2, INK, "r")
        line(c, rx, y - 2.8, PW - M - 6, y - 2.8, 0.05, INK4)
        y -= 8
    text(c, rx, y, "Capital de giro (3 meses de estoque)", "Sans", 2.1, INK)
    text(c, PW - M - 6, y, brl(e["wc0"]), "Mono", 2.2, INK, "r")
    line(c, rx, y - 2.8, PW - M - 6, y - 2.8, 0.12, INK)
    y -= 9
    text(c, rx, y, "TOTAL NO ANO 0", "JuraM", 2.2, INK, spacing=0.6)
    text(c, PW - M - 6, y, brl(e["invest"] + e["wc0"]), "Mono", 2.8, INK, "r")
    y -= 20
    text(c, rx, y, "PREMISSAS", "JuraM", 2.0, INK3, spacing=0.6)
    y -= 7
    prem = [
        ("Custo unitário (lotes de 1000)", brl(N.UNIT_COST_SERIE, 2)),
        ("Custo unitário no ano 1", brl(N.UNIT_COST[0], 2)),
        ("Comissão de canal", f"{N.CHANNEL * 100:.0f} %"),
        ("Frete absorvido por pedido", brl(N.SHIPPING, 2)),
        ("Simples Nacional (efetivo)", f"{N.TAX * 100:.0f} %"),
        ("Garantia e devoluções", f"{N.WARRANTY * 100:.0f} %"),
        ("Câmbio de referência", f"R$ {N.FX:.2f}".replace(".", ",")),
        ("TMA", f"{N.TMA * 100:.0f} % a.a."),
    ]
    for k, v in prem:
        kv(c, rx, y, k.upper(), v, w=PW - M - 6 - rx)
        y -= 6.4
    frame(c, 12, "PLANO DE NEGÓCIO · CICLO DE VIDA")


def page_return(c):
    new_page(c)
    top = PH - M - 24
    e = N.evaluate(N.P_SUG)
    title(c, M + 6, top + 6, "RETORNO SOBRE O CAPITAL")
    text(c, M + 6, top - 6.5, f"fluxo de caixa livre ao preço sugerido de {brl(N.P_SUG)} · TMA de 14 % a.a.",
         "Serif", 4.4, INK2)
    # tabela anual
    cols = ["", "ANO 0", "ANO 1", "ANO 2", "ANO 3", "ANO 4", "ANO 5"]
    x0, cw = M + 6, 30.0
    xl = x0 + 64
    y = top - 22
    for i, h in enumerate(cols):
        if h:
            text(c, xl + (i - 1) * cw + cw, y, h, "JuraM", 1.9, INK3, "r", spacing=0.6)
    line(c, x0, y - 2.6, xl + 6 * cw, y - 2.6, 0.12, INK)
    y -= 8.5
    ys = e["years"]
    rows = [
        ("Unidades", [None] + [y_["units"] for y_ in ys], num),
        ("Receita", [None] + [y_["rev"] for y_ in ys], brl),
        ("Custos variáveis", [None] + [-y_["var"] for y_ in ys], brl),
        ("Despesas fixas", [None] + [-y_["fixed"] for y_ in ys], brl),
        ("Resultado operacional", [None] + [y_["ebitda"] for y_ in ys], brl),
        ("Investimento e giro", [-(e["invest"] + e["wc0"])] + [-y_["dwc"] for y_ in ys], brl),
        ("Fluxo de caixa livre", e["flows"], brl),
    ]
    acc, accd = [], []
    a = ad = 0.0
    for t, f in enumerate(e["flows"]):
        a += f
        ad += f / (1 + N.TMA) ** t
        acc.append(a)
        accd.append(ad)
    rows += [("Acumulado", acc, brl), ("Acumulado descontado (14 %)", accd, brl)]
    for k, vals, fmt in rows:
        strong = k in ("Fluxo de caixa livre", "Acumulado descontado (14 %)")
        text(c, x0, y, k, "JuraM" if strong else "Sans", 2.1, INK, spacing=0.4 if strong else 0)
        for i, v in enumerate(vals):
            if v is None:
                continue
            col = INK if v >= 0 else HexColor("#9A3B32")
            text(c, xl + i * cw + cw, y, fmt(v), "Mono", 2.0, col, "r")
        line(c, x0, y - 2.8, xl + 6 * cw, y - 2.8, 0.12 if strong else 0.05, INK if strong else INK4)
        y -= 7.4

    # curva J do caixa acumulado descontado
    gx, gy, gw, gh = x0 + 10, 40.0, 225.0, 72.0
    vmin, vmax = min(accd + [0]), max(accd)
    span = vmax - vmin
    zero = gy + gh * (-vmin) / span
    line(c, gx, zero, gx + gw, zero, 0.12, INK)
    text(c, gx - 2, zero - 0.8, "0", "Mono", 1.8, INK3, "r")
    xs = [gx + gw * t / 5 for t in range(6)]
    c.setStrokeColor(BLU)
    c.setLineWidth(0.45)
    p = c.beginPath()
    for t, v in enumerate(accd):
        yy = gy + gh * (v - vmin) / span
        (p.moveTo if t == 0 else p.lineTo)(xs[t], yy)
    c.drawPath(p, stroke=1, fill=0)
    for t, v in enumerate(accd):
        yy = gy + gh * (v - vmin) / span
        c.setFillColor(BLU if v >= 0 else HexColor("#9A3B32"))
        c.circle(xs[t], yy, 0.9, stroke=0, fill=1)
        text(c, xs[t], gy - 6, f"ANO {t}", "JuraM", 1.8, INK3, "c", spacing=0.5)
    # payback descontado
    if e["dpb"]:
        xp = gx + gw * e["dpb"] / 5
        line(c, xp, gy, xp, gy + gh, 0.1, INK2, (1.0, 0.8))
        text(c, xp + 1.5, gy + gh - 2, f"payback descontado · {e['dpb']:.1f} anos".replace(".", ","), "Mono", 1.9, INK2)
    text(c, gx, gy + gh + 4, "CAIXA ACUMULADO DESCONTADO", "JuraM", 1.9, INK3, spacing=0.6)

    # indicadores
    rx = 300.0
    text(c, rx, top + 6, "INDICADORES", "Jura", 5.0, INK, spacing=1.2)
    kpis = [
        ("VPL a 14 % a.a.", brl(e["npv"]), GRN),
        ("TIR", f"{e['irr'] * 100:.1f}".replace(".", ",") + " % a.a.", BLU),
        ("PAYBACK SIMPLES", f"{e['pb']:.1f} anos".replace(".", ","), AMB),
        ("ROI NO CICLO", f"{e['roi'] * 100:.0f} %", INK2),
    ]
    yy = top - 18
    for k, v, col in kpis:
        c.setFillColor(col)
        c.rect(rx, yy - 11, 1.2, 15, stroke=0, fill=1)
        text(c, rx + 5, yy, k, "JuraM", 2.0, INK3, spacing=0.6)
        text(c, rx + 5, yy - 9, v, "Jura", 8.0, INK)
        yy -= 26
    text(c, rx, yy, "ROI = soma dos fluxos dos anos 1–5", "Mono", 1.85, INK3)
    text(c, rx, yy - 4, "dividida pelo investimento do ano 0, menos 1.", "Mono", 1.85, INK3)
    text(c, rx, yy - 13, "A TIR supera a TMA em", "Serif", 4.2, INK2)
    text(c, rx, yy - 18.5, f"{(e['irr'] - N.TMA) * 100:.0f} pontos: o projeto paga o capital".replace(".", ","),
         "Serif", 4.2, INK2)
    text(c, rx, yy - 24, "e ainda cria valor no ciclo previsto.", "Serif", 4.2, INK2)
    frame(c, 13, "PLANO DE NEGÓCIO · RETORNO")


def be_vol():
    lo, hi = 0.05, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if N.evaluate(N.P_SUG, [round(u * mid) for u in N.UNITS])["npv"] > 0:
            hi = mid
        else:
            lo = mid
    return hi


def page_price(c):
    new_page(c)
    dot_grid(c, M + 4, M + 4, PW - M - 4, PH - M - 4, 5.0, HexColor("#E2DED5"), 0.14)
    top = PH - M - 24
    title(c, M + 6, top + 6, "PREÇO DE VENDA")
    text(c, M + 6, top - 6.5, "o mínimo que remunera a TMA e o preço sugerido com margem de segurança", "Serif", 4.4, INK2)

    # VPL x preço
    gx, gy, gw, gh = M + 22, 120.0, 200.0, 100.0
    prices = list(range(100, 261, 2))
    vols = [(1.0, INK, "volume previsto"), (0.6, INK3, "60 % do volume")]
    allv = [N.evaluate(p, [round(u * k) for u in N.UNITS])["npv"] for k, _, _ in vols for p in prices]
    vmin, vmax = min(allv), max(allv)
    X = lambda p: gx + gw * (p - prices[0]) / (prices[-1] - prices[0])
    Y = lambda v: gy + gh * (v - vmin) / (vmax - vmin)
    line(c, gx, Y(0), gx + gw, Y(0), 0.14, INK)
    text(c, gx - 2, Y(0) - 0.8, "VPL 0", "Mono", 1.8, INK3, "r")
    for p in range(100, 261, 20):
        line(c, X(p), gy - 1.5, X(p), gy, 0.08, INK3)
        text(c, X(p), gy - 5.5, f"{p}", "Mono", 1.8, INK3, "c")
    text(c, gx + gw, gy - 10, "preço de venda (R$)", "Mono", 1.8, INK3, "r")
    for k, col, nm in vols:
        c.setStrokeColor(col)
        c.setLineWidth(0.45)
        pth = c.beginPath()
        for i, p in enumerate(prices):
            v = N.evaluate(p, [round(u * k) for u in N.UNITS])["npv"]
            (pth.moveTo if i == 0 else pth.lineTo)(X(p), Y(v))
        c.drawPath(pth, stroke=1, fill=0)
    # legenda
    ly = gy + gh + 4
    for i, (k, col, nm) in enumerate(vols):
        line(c, gx + i * 46, ly + 0.7, gx + i * 46 + 6, ly + 0.7, 0.45, col)
        text(c, gx + i * 46 + 8, ly, nm, "Mono", 1.9, INK2)
    # marcadores
    for p, col, nm in ((N.P_MIN, AMB, "mínimo"), (N.P_SUG, GRN, "sugerido")):
        line(c, X(p), gy, X(p), gy + gh, 0.12, col, (1.0, 0.8))
        text(c, X(p) + 1.5, gy + gh - 3 if nm == "sugerido" else gy + 3, f"{nm} · {brl(p)}", "Mono", 2.0, INK)

    # composição do preço sugerido
    by = 66.0
    text(c, gx, by + 14, f"COMPOSIÇÃO DE {brl(N.P_SUG)} POR UNIDADE · ANO DE MATURIDADE", "JuraM", 1.95, INK3, spacing=0.6)
    parts = N.unit_build(N.P_SUG)
    shades = [INK, INK2, HexColor("#8A857A"), INK3, HexColor("#C9C4B8"), HexColor("#DDD8CC"), GRN]
    x = gx
    for (nm, v), col in zip(parts, shades):
        w = gw * v / N.P_SUG
        c.setFillColor(col)
        c.rect(x, by, w, 6, stroke=0, fill=1)
        x += w
    yy = by - 6
    for i, ((nm, v), col) in enumerate(zip(parts, shades)):
        cx = gx + (i % 4) * 52
        ry = yy - (i // 4) * 5
        c.setFillColor(col)
        c.rect(cx, ry - 0.4, 2.2, 2.2, stroke=0, fill=1)
        text(c, cx + 4, ry, f"{nm} {brl(v, 2)}", "Mono", 1.85, INK2)

    # bloco do preço
    rx = 290.0
    e = N.evaluate(N.P_SUG)
    e6 = N.evaluate(N.P_SUG, [round(u * 0.6) for u in N.UNITS])
    text(c, rx, top + 6, "PREÇO SUGERIDO", "Jura", 5.0, INK, spacing=1.2)
    c.setFillColor(GRN)
    c.rect(rx, top - 31, 1.6, 26, stroke=0, fill=1)
    text(c, rx + 6, top - 22, brl(N.P_SUG), "Jura", 15.0, INK)
    text(c, rx + 6, top - 29.5, f"≈ US$ {N.P_SUG / N.FX:.0f} · margem líquida unitária {parts[-1][1] / N.P_SUG * 100:.0f} %",
         "Mono", 1.95, INK2)
    y = top - 46
    rowsk = [
        ("PREÇO MÍNIMO (VPL = 0, TIR = TMA)", brl(N.P_MIN, 2)),
        ("MARGEM SOBRE O MÍNIMO", f"{(N.P_SUG / N.P_MIN - 1) * 100:.0f} %"),
        ("VPL NO VOLUME PREVISTO", brl(e["npv"])),
        ("TIR NO VOLUME PREVISTO", f"{e['irr'] * 100:.1f} %".replace(".", ",")),
        ("VPL COM 60 % DO VOLUME", brl(e6["npv"])),
        ("TIR COM 60 % DO VOLUME", f"{e6['irr'] * 100:.1f} %".replace(".", ",")),
        (f"VOLUME DE EQUILÍBRIO A {brl(N.P_SUG)}", f"{be_vol() * 100:.0f} % do previsto"),
    ]
    for k, v in rowsk:
        kv(c, rx, y, k, v, w=PW - M - 6 - rx)
        y -= 7.2
    # sensibilidade preço x volume
    y -= 8
    text(c, rx, y, "VPL (R$ MIL) · PREÇO × VOLUME", "JuraM", 1.95, INK3, spacing=0.6)
    y -= 8
    ps = [149, 179, 199, 229]
    ks = [0.5, 0.7, 1.0, 1.3]
    cw = (PW - M - 6 - rx - 22) / len(ps)
    for j, p in enumerate(ps):
        text(c, rx + 22 + j * cw + cw / 2, y, f"R$ {p}", "Mono", 1.9, INK2, "c")
    y -= 6
    for k in ks:
        text(c, rx, y, f"{k * 100:.0f} %", "Mono", 1.9, INK2)
        for j, p in enumerate(ps):
            v = N.evaluate(p, [round(u * k) for u in N.UNITS])["npv"] / 1000
            col = GRN if v > 0 else HexColor("#C9705F")
            c.setFillColor(col)
            c.setFillAlpha(0.18 if v > 0 else 0.22)
            c.rect(rx + 22 + j * cw + 0.6, y - 1.8, cw - 1.2, 5.2, stroke=0, fill=1)
            c.setFillAlpha(1)
            text(c, rx + 22 + j * cw + cw / 2, y, f"{v:,.0f}".replace(",", "."), "Mono", 1.9, INK, "c")
        y -= 6.2
    text(c, rx, y - 3, "Premissas de volume e custo são hipóteses de planejamento;", "Mono", 1.8, INK3)
    text(c, rx, y - 7, "validar com pré-venda e cotações reais antes do molde.", "Mono", 1.8, INK3)
    frame(c, 14, "PLANO DE NEGÓCIO · PREÇO")


BUSINESS_PAGES = (page_lifecycle, page_return, page_price)
