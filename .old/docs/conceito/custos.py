"""Modelo de custo do indicador rev A (estimativa, 2026-11-08).

Preços de componentes: catálogo JLCPCB consultado em 2026-11-08 (faixas por quantidade).
Demais valores: estimativas de mercado; cotar antes de comprar. Tudo em USD.
"""

LOTS = (5, 100, 1000)
FX = 5.50          # câmbio de referência assumido, R$/USD (atualizar)

# ref, descrição, qtd/placa, preço unitário por lote (5, 100, 1000)
PARTS = [
    ("U1", "STM32C071F8P6", 1, (3.3953, 2.3388, 2.2046)),
    ("D1–D3", "SK6805-EC20", 3, (0.1100, 0.0769, 0.0583)),
    ("U2", "AP2112K-3.3", 1, (0.1829, 0.1451, 0.1100)),
    ("U3", "74AHCT1G125", 1, (0.0849, 0.0676, 0.0525)),
    ("U4", "USBLC6-2SC6", 1, (0.1623, 0.1242, 0.0889)),
    ("J1", "USB-C 16P HRO", 1, (0.1868, 0.1476, 0.1041)),
    ("C1", "10 µF 0603", 1, (0.0203, 0.0203, 0.0155)),
    ("C2", "1 µF 0402", 1, (0.0058, 0.0058, 0.0044)),
    ("C3–C8", "100 nF 0402", 6, (0.0031, 0.0031, 0.0020)),
    ("R1, R2", "5,1 kΩ 0402", 2, (0.0023, 0.0023, 0.0017)),
    ("R3", "33 Ω 0402", 1, (0.0015, 0.0015, 0.0011)),
]
EXTENDED_TYPES = 6          # peças "extended" na JLC (taxa de carga por tipo)
SMD_JOINTS = 86
THT_JOINTS = 4

# custos por LOTE (fixos do pedido)
LOT_FIXED = {
    "Fabricação da placa (2 cam., 0,8 mm, preta, ENIG)": (18.0, 45.0, 180.0),
    "Montagem: setup": (8.0, 8.0, 25.0),
    "Montagem: estêncil": (1.5, 1.5, 7.0),
    "Montagem: taxa de peças extended (6 × US$ 3)": (18.0, 18.0, 18.0),
    "Solda manual THT: setup": (3.5, 3.5, 3.5),
    "Frete internacional": (25.0, 45.0, 180.0),
    "Ferramental de injeção (molde família, 3 cavidades)": (0.0, 0.0, 6500.0),
}

# custos por UNIDADE
UNIT = {
    "Montagem: juntas SMD (86 × US$ 0,0017)": (SMD_JOINTS * 0.0017,) * 3,
    "Montagem: juntas THT (4 × US$ 0,0173)": (THT_JOINTS * 0.0173,) * 3,
    "Corpo + tampa (impressão 3D resina | injeção PC/ABS)": (3.40, 2.90, 0.30),
    "Bandeira (resina transparente polida | injeção PC difusor)": (2.20, 1.90, 0.15),
    "Ímã NdFeB Ø10 × 1,5 mm + disco VHB": (0.17, 0.12, 0.08),
    "Cabo USB-C 1,5 m": (1.60, 1.20, 0.85),
    "Embalagem (caixa kraft + berço)": (0.60, 0.40, 0.25),
    "Montagem final e teste": (0.00, 0.50, 0.30),
}

TAX_NOTE = ("II 60 % − US$ 30 + ICMS 20 % por dentro (regime simplificado, remessa até US$ 3.000);"
            " lote de 1000: importação formal, carga indicativa de 70 %")


def compute():
    res = {}
    for i, n in enumerate(LOTS):
        parts = sum(q * p[i] for _r, _d, q, p in PARTS) * n
        fixed = sum(v[i] for v in LOT_FIXED.values())
        unit = sum(v[i] for v in UNIT.values()) * n
        goods = parts + fixed + unit
        if n * 0 + goods <= 3000:
            ii = max(0.0, 0.60 * goods - 30.0)
            icms = (goods + ii) / (1 - 0.20) - (goods + ii)
            tax = ii + icms
        else:
            tax = 0.70 * goods
        total = goods + tax
        res[n] = dict(parts=parts, fixed=fixed, unit=unit, goods=goods, tax=tax, total=total,
                      per_unit=total / n, parts_per_board=parts / n)
    return res


if __name__ == "__main__":
    for n, r in compute().items():
        print(n, {k: round(v, 2) for k, v in r.items()}, "R$/un", round(r["per_unit"] * FX, 2))
