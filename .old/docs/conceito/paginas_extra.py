"""Lâminas 07–11: renders, lista de material completa e custos."""
import os

from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader

import custos
from gerar_conceito import (INK, INK2, INK3, INK4, M, MASK, PAPER, PH, PW, SHELL, STATES,
                            dot_grid, frame, line, new_page, text)

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "renders")


def title(c, x, y, s):
    text(c, x, y, s, "Jura", 7.0, INK, spacing=1.6)
    line(c, x, y - 4.5, x + 26, y - 4.5, 0.15, INK)


def plate(c, name, x, y, w, h, code, caption, fit="cover"):
    """Imagem com moldura fina e legenda técnica abaixo."""
    path = os.path.join(IMG, name.replace(".png", ".jpg"))
    if not os.path.exists(path):
        path = os.path.join(IMG, name)
    if os.path.exists(path):
        img = ImageReader(path)
        iw, ih = img.getSize()
        c.saveState()
        p = c.beginPath()
        p.rect(x, y, w, h)
        c.clipPath(p, stroke=0, fill=0)
        k = max(w / iw, h / ih) if fit == "cover" else min(w / iw, h / ih)
        dw, dh = iw * k, ih * k
        c.drawImage(img, x + (w - dw) / 2, y + (h - dh) / 2, dw, dh)
        c.restoreState()
    else:
        c.setFillColor(INK4)
        c.rect(x, y, w, h, stroke=0, fill=1)
        text(c, x + w / 2, y + h / 2, "render pendente", "Mono", 2.4, INK2, "c")
    c.setStrokeColor(INK)
    c.setLineWidth(0.12)
    c.rect(x, y, w, h, stroke=1, fill=0)
    text(c, x, y - 5.0, code, "Mono", 2.2, INK)
    text(c, x + 12, y - 5.0, caption, "Sans", 2.2, INK2)


def page_pcb_renders(c):
    new_page(c)
    top = PH - M - 24
    title(c, M + 6, top + 6, "PLACA · RENDERS")
    text(c, M + 6, top - 6.5, "ray tracing sobre a geometria exportada do KiCad", "Serif", 4.4, INK2)
    h = 202
    y0 = 40
    plate(c, "pcb_top.png", M + 6, y0, 56, h, "R1", "face de cima")
    plate(c, "pcb_bottom.png", M + 72, y0, 56, h, "R2", "face de baixo")
    plate(c, "pcb_iso.png", M + 140, y0, PW - 2 * M - 146, h, "R3", "isometria · luz de estúdio")
    frame(c, 7, "PLACA · RENDERS")


def page_product_a(c):
    new_page(c)
    top = PH - M - 24
    title(c, M + 6, top + 6, "PRODUTO · RENDERS")
    y0, h = 40, 214
    big_w = 236
    plate(c, "prod_hero.png", M + 6, y0, big_w, h, "P1", "três quartos · processando")
    rx = M + 6 + big_w + 10
    rw = PW - M - 6 - rx
    plate(c, "prod_front.png", rx, y0 + h / 2 + 6, rw, h / 2 - 6, "P2", "frente · em reunião")
    plate(c, "prod_usb.png", rx, y0, rw, h / 2 - 12, "P3", "base · USB-C")
    frame(c, 8, "PRODUTO · RENDERS I")


def page_product_b(c):
    new_page(c)
    top = PH - M - 24
    title(c, M + 6, top + 6, "PRODUTO · EM USO E MONTAGEM")
    y0, h = 40, 214
    lw = 186
    plate(c, "prod_monitor.png", M + 6, y0 + h / 2 + 6, lw, h / 2 - 6, "P4", "no monitor · livre")
    plate(c, "prod_states.png", M + 6, y0, lw, h / 2 - 12, "P5", "os cinco estados")
    rx = M + 6 + lw + 10
    plate(c, "prod_exploded.png", rx, y0, PW - M - 6 - rx, h, "P6", "vista explodida")
    frame(c, 9, "PRODUTO · RENDERS II")


BOM_ROWS = [
    # grupo, item, descrição, especificação, qtd, origem/código, processo
    ("ELETRÔNICA", "U1", "Microcontrolador", "STM32C071F8P6 · TSSOP-20", "1", "JLC C43650205", "SMT"),
    ("", "D1–D3", "LED RGB endereçável", "SK6805-EC20 · 2020", "3", "JLC C2890036", "SMT"),
    ("", "U2", "Regulador 3,3 V", "AP2112K-3.3 · SOT-23-5", "1", "JLC C51118", "SMT"),
    ("", "U3", "Buffer de nível", "74AHCT1G125 · SC-70-5", "1", "JLC C53114384", "SMT"),
    ("", "U4", "Proteção ESD USB", "USBLC6-2SC6 · SOT-23-6", "1", "JLC C7519", "SMT"),
    ("", "J1", "Receptáculo USB-C 16P", "HRO TYPE-C-31-M-12", "1", "JLC C165948", "SMT + THT"),
    ("", "C1", "Capacitor", "10 µF 10 V X5R · 0603", "1", "JLC C19702", "SMT"),
    ("", "C2", "Capacitor", "1 µF 25 V X5R · 0402", "1", "JLC C52923", "SMT"),
    ("", "C3–C8", "Capacitor", "100 nF 16 V X7R · 0402", "6", "JLC C1525", "SMT"),
    ("", "R1, R2", "Resistor", "5,1 kΩ 1 % · 0402", "2", "JLC C25905", "SMT"),
    ("", "R3", "Resistor", "33 Ω 1 % · 0402", "1", "JLC C25105", "SMT"),
    ("PLACA", "PCB", "Placa de circuito", "FR-4 0,8 mm · 2 cam. · preta · ENIG", "1", "JLCPCB", "fabricação"),
    ("MECÂNICA", "M1", "Corpo", "PC/ABS grafite · 12 × 48 × 15 mm", "1", "proposta", "injeção / 3D"),
    ("", "M2", "Tampa inferior", "PC/ABS grafite · janela USB-C", "1", "proposta", "injeção / 3D"),
    ("", "M3", "Bandeira / guia de luz", "PC difusor · 22 × 19 × 2,5 mm", "1", "proposta", "injeção / 3D"),
    ("", "M4", "Ímã de fixação", "NdFeB N52 Ø10 × 1,5 mm · Ni", "1", "proposta", "comprado"),
    ("", "M5", "Fita dupla face", "VHB acrílica · disco Ø10 mm", "1", "proposta", "corte"),
    ("ACESSÓRIOS", "A1", "Cabo", "USB-C ↔ USB-A/C · 1,5 m", "1", "proposta", "comprado"),
    ("", "A2", "Embalagem", "caixa kraft + berço", "1", "proposta", "comprado"),
]


def page_full_bom(c):
    new_page(c)
    top = PH - M - 24
    title(c, M + 6, top + 6, "LISTA DE MATERIAL")
    text(c, M + 6, top - 6.5, "rev A · por unidade montada", "Serif", 4.4, INK2)
    cols = [M + 6, M + 40, M + 60, M + 112, M + 202, M + 218, M + 262, M + 300]
    heads = ["GRUPO", "ITEM", "DESCRIÇÃO", "ESPECIFICAÇÃO", "QTD", "ORIGEM / CÓDIGO", "PROCESSO", ""]
    y = top - 20
    for x, hd in zip(cols, heads):
        if hd:
            text(c, x, y, hd, "JuraM", 1.9, INK3, spacing=0.7)
    line(c, M + 6, y - 2.6, PW - M - 6, y - 2.6, 0.12, INK)
    y -= 9.6
    pitch = 9.4
    for g, it, desc, spec, q, src, proc in BOM_ROWS:
        if g and y < top - 25:
            line(c, M + 6, y + 6.2, PW - M - 6, y + 6.2, 0.12, INK)
        if g:
            text(c, cols[0], y, g, "JuraM", 2.0, INK, spacing=0.6)
        text(c, cols[1], y, it, "Mono", 2.3, INK)
        text(c, cols[2], y, desc, "Sans", 2.3, INK)
        text(c, cols[3], y, spec, "Mono", 2.1, INK)
        text(c, cols[4], y, q, "Mono", 2.3, INK)
        text(c, cols[5], y, src, "Mono", 2.1, INK2 if src == "proposta" else INK)
        text(c, cols[6], y, proc, "Mono", 2.1, INK2)
        line(c, M + 6, y - 3.4, PW - M - 6, y - 3.4, 0.05, INK4)
        y -= pitch
    text(c, M + 6, y - 3, "Itens marcados como proposta dependem do protótipo mecânico; os demais estão no catálogo JLCPCB.",
         "Mono", 2.0, INK3)
    frame(c, 10, "LISTA DE MATERIAL")


def money(v):
    return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def page_costs(c):
    new_page(c)
    dot_grid(c, M + 4, M + 4, PW - M - 4, PH - M - 4, 5.0, HexColor("#E2DED5"), 0.14)
    r = custos.compute()
    top = PH - M - 24
    title(c, M + 6, top + 6, "CUSTOS ESTIMADOS")
    text(c, M + 6, top - 6.5, "valores em US$ · componentes pela tabela JLCPCB de 2026-11-08 · demais itens estimados",
         "Serif", 4.4, INK2)
    # cabeçalho dos lotes
    x_lab, xs = M + 6, [M + 168, M + 204, M + 240]
    y = top - 22
    text(c, x_lab, y, "ITEM", "JuraM", 1.9, INK3, spacing=0.7)
    names = ["LOTE MÍNIMO · 5", "PILOTO · 100", "SÉRIE · 1000"]
    for x, nm in zip(xs, names):
        text(c, x + 30, y, nm, "JuraM", 1.9, INK3, "r", spacing=0.5)
    line(c, x_lab, y - 2.6, xs[-1] + 30, y - 2.6, 0.12, INK)
    y -= 8.6
    rows = [("Componentes eletrônicos (BOM × lote)", [r[n]["parts"] for n in custos.LOTS])]
    for k, v in custos.LOT_FIXED.items():
        rows.append((k, list(v)))
    for k, v in custos.UNIT.items():
        rows.append((k + "  × lote", [v[i] * n for i, n in enumerate(custos.LOTS)]))
    for k, vals in rows:
        text(c, x_lab, y, k, "Sans", 2.15, INK)
        for x, v in zip(xs, vals):
            text(c, x + 30, y, "—" if v == 0 else money(v), "Mono", 2.15, INK if v else INK3, "r")
        line(c, x_lab, y - 2.7, xs[-1] + 30, y - 2.7, 0.05, INK4)
        y -= 7.0
    y -= 1.5
    sums = [("Subtotal (mercadoria + serviços + frete)", "goods", INK),
            ("Impostos de importação (estimativa)", "tax", INK2),
            ("TOTAL DO LOTE", "total", INK)]
    for k, key, col in sums:
        bold = key == "total"
        text(c, x_lab, y, k, "JuraM" if bold else "Sans", 2.3 if bold else 2.15, col, spacing=0.5 if bold else 0)
        for x, n in zip(xs, custos.LOTS):
            text(c, x + 30, y, money(r[n][key]), "Mono", 2.5 if bold else 2.15, col, "r")
        line(c, x_lab, y - 2.8, xs[-1] + 30, y - 2.8, 0.12 if bold else 0.05, INK if bold else INK4)
        y -= 7.6
    text(c, x_lab, y - 1, custos.TAX_NOTE, "Mono", 1.8, INK3)

    # coluna direita: custo unitário em destaque
    rx = 300.0
    text(c, rx, top + 6, "CUSTO POR UNIDADE", "Jura", 5.0, INK, spacing=1.2)
    yy = top - 18
    for n, nm, col in zip(custos.LOTS, names, (STATES[4][1], STATES[2][1], STATES[0][1])):
        pu = r[n]["per_unit"]
        c.setFillColor(col)
        c.rect(rx, yy - 13.5, 1.2, 17, stroke=0, fill=1)
        text(c, rx + 5, yy, nm, "JuraM", 2.0, INK3, spacing=0.6)
        text(c, rx + 5, yy - 10.5, f"US$ {money(pu)}", "Jura", 9.0, INK)
        text(c, rx + 5, yy - 15.5, f"≈ R$ {money(pu * custos.FX)} · total do lote US$ {money(r[n]['total'])}",
             "Mono", 1.9, INK2)
        yy -= 31
    # composição do lote mínimo
    n = custos.LOTS[0]
    parts, fixed, unit, tax = r[n]["parts"], r[n]["fixed"], r[n]["unit"], r[n]["tax"]
    tot = r[n]["total"]
    text(c, rx, yy - 2, "COMPOSIÇÃO · LOTE MÍNIMO", "JuraM", 2.0, INK3, spacing=0.6)
    bx, bw = rx, PW - M - 6 - rx
    by = yy - 12
    segs = [("componentes", parts, INK), ("taxas e frete", fixed, INK2), ("mecânica e acessórios", unit, INK3),
            ("impostos", tax, HexColor("#C9C4B8"))]
    x = bx
    for nm, v, col in segs:
        w = bw * v / tot
        c.setFillColor(col)
        c.rect(x, by, w, 4, stroke=0, fill=1)
        x += w
    ly = by - 6
    for nm, v, col in segs:
        c.setFillColor(col)
        c.rect(bx, ly - 0.4, 2.2, 2.2, stroke=0, fill=1)
        text(c, bx + 4, ly, nm, "Mono", 1.95, INK2)
        text(c, bx + bw, ly, f"{100 * v / tot:4.0f} %", "Mono", 1.95, INK, "r")
        ly -= 4.4
    text(c, rx, ly - 4, "No lote de 1000, o molde (US$ 6.500) pesa", "Serif", 4.0, INK2)
    text(c, rx, ly - 9, "US$ 6,50 por peça; sem ele, a unidade cai", "Serif", 4.0, INK2)
    no_tool = (r[1000]["total"] - 6500 * 1.70) / 1000
    text(c, rx, ly - 14, f"para cerca de US$ {money(no_tool)}.", "Serif", 4.0, INK2)
    frame(c, 11, "CUSTOS")


EXTRA_PAGES = (page_pcb_renders, page_product_a, page_product_b, page_full_bom, page_costs)
