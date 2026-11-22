#!/usr/bin/env python3
"""Confere peças na LCSC (página do produto) e na JLC (API de busca) e grava docs/parts-check.json."""
import json, os, re, subprocess, datetime, sys
sys.path.insert(0, "/tmp")
UA = "Mozilla/5.0"
def sh(*a): return subprocess.check_output(a).decode("utf-8", "replace")
def lcsc(c):
    t = sh("curl", "-sL", "-A", UA, f"https://www.lcsc.com/product-detail/{c}.html")
    title = re.search(r"<title>(.*?)</title>", t)
    st = re.search(r'"stockNumber":([0-9]+)', t)
    ds = re.search(r"https://datasheet\.lcsc\.com/datasheet/pdf/[0-9a-f]+\.pdf", t)
    return (title.group(1) if title else None, int(st.group(1)) if st else None, ds.group(0) if ds else None)
def jlc(c):
    d = json.loads(sh("curl", "-sL", "-A", UA, "-H", "Content-Type: application/json", "-X", "POST",
        "https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList",
        "-d", json.dumps({"keyword": c, "currentPage": 1, "pageSize": 5})))
    for x in d["data"]["componentPageInfo"]["list"] or []:
        if x["componentCode"] == c:
            return x["stockCount"], x.get("componentLibraryType"), x.get("componentBrandEn"), x["componentModelEn"]
    return None, None, None, None
CHOSEN = [  # ref, função, LCSC, motivo
 ("D1-D3", "LEDs RGB endereçáveis", "C4154877", "16 bit/canal + gamma interna, PWM 10 kHz (SK6805: 8 bit, ~1 kHz), sinal duplo BI/BO, 2,2x2,0 mm"),
 ("U1", "MCU USB", "C44521811", "USB FS sem cristal (HSI48+CRS), DFU na ROM, Cortex-M0+ 48 MHz, QFN-28 4x4"),
 ("U3", "conversor de nível 3,3->5 V", "C7484", "TI, entrada TTL (VIH 2 V) com VCC 5 V; estoque alto; WS2816 exige VIH 0,7*VDD = 3,5 V"),
 ("U2", "LDO 3,3 V", "C51118", "600 mA, 55 uA Iq, VIN máx. 6 V (margem acima do VBUS), mantido"),
 ("U4", "ESD USB", "C7519", "ST original, 3,5 pF, IEC 61000-4-2, mantido"),
 ("J1", "USB-C 16P", "C165948", "o USB-C mais usado na JLC (estoque ~480 mil), SMD + THT de fixação, mantido"),
 ("C1", "10 uF 0603", "C19702", "Samsung X5R"), ("C2", "1 uF 0402", "C52923", "Samsung X5R"),
 ("C3-C8", "100 nF 0402", "C1525", "Samsung X7R"), ("R1,R2", "5,1 k 0402", "C25905", "UNI-ROYAL 1%"),
 ("R3", "33 R 0402", "C25105", "UNI-ROYAL 1%"), ("R4", "1 k 0402", "C11702", "UNI-ROYAL 1%"),
]
CANDIDATES = [  # avaliados e não escolhidos
 ("LED", "C2890036", "SK6805-EC20 (rev B): 8 bit, PWM ~1 kHz"),
 ("LED", "C2890035", "SK6805-EC15 1,5 mm: 8 bit"),
 ("LED", "C2909055", "SK6805-EC14 1,4 mm: 8 bit, brilho menor"),
 ("LED", "C55109522", "WS2812C-2020-V6: 8 bit, PWM 2 kHz"),
 ("LED", "C5349954", "XL-1615RGBC-2812B: 8 bit"),
 ("LED", "C5149201", "SK6812MINI-E: emissão reversa (furo na placa), 3,2x2,8 mm, 8 bit"),
 ("LED", "C965561", "WS2816C-2121: 16 bit, 10,5 mA total (mais fraco), alternativa direta"),
 ("LED", "C42417612", "WS2816C-1313/4P: 16 bit, 1,3 mm, VDD 3,3-5,5 V; menor e mais difícil de inspecionar"),
 ("LED", "C22371534", "WS2816B 5050: 16 bit, grande demais para 11 mm"),
 ("MCU", "C7437027", "CH32X035G8U6: USB sem cristal, estoque alto, mas outro ecossistema e pinagem"),
 ("Nível", "C53114384", "74AHCT1G125 JSMSEMI (rev B): estoque baixo"),
 ("Nível", "C100024", "SN74LV1T34DBVR: tradutor de 1 bit, também serve"),
 ("LDO", "C404027", "TLV75533PDBVR: 25 uA Iq, mas VIN máx. 5,5 V (sem margem no VBUS)"),
]
today = datetime.date.today().isoformat()
out = {"date": today, "sources": "LCSC product page (stockNumber) + JLCPCB parts API (stockCount)", "chosen": [], "evaluated": []}
for ref, fn, c, why in CHOSEN:
    t, st, ds = lcsc(c); js, lib, brand, model = jlc(c)
    out["chosen"].append(dict(ref=ref, function=fn, lcsc=c, model=model, brand=brand, lcsc_title=t, lcsc_stock=st,
        jlc_stock=js, jlc_library=lib, url=f"https://www.lcsc.com/product-detail/{c}.html", datasheet=ds, reason=why))
for kind, c, note in CANDIDATES:
    t, st, ds = lcsc(c); js, lib, brand, model = jlc(c)
    out["evaluated"].append(dict(kind=kind, lcsc=c, model=model, brand=brand, lcsc_stock=st, jlc_stock=js,
        url=f"https://www.lcsc.com/product-detail/{c}.html", datasheet=ds, note=note))
out["distributors_web_search_snapshot"] = {
  "note": "Mouser/DigiKey bloqueiam acesso direto do box (403/desafio). Números abaixo vêm de resultados de busca, não de página aberta; tratar como não verificados.",
  "STM32C071G8U6": {"mouser": "2.781 em estoque (busca)", "digikey": "42 imediatos (busca)"},
}
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "parts-check.json")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=2, ensure_ascii=False)
for x in out["chosen"]: print(x["ref"], x["lcsc"], x["model"], x["brand"], "LCSC", x["lcsc_stock"], "JLC", x["jlc_stock"], x["jlc_library"])
for x in out["evaluated"]: print("  cand", x["lcsc"], x["model"], x["lcsc_stock"], x["jlc_stock"])
