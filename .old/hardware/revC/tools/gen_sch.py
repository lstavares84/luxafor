#!/usr/bin/env python3
"""Gera hardware/indicador/luxflag.kicad_sch a partir de netlist.py.

Cada pino ligado recebe um rótulo (label) com o nome da rede; pinos livres
recebem marcador de não conectado. O esquemático é a fonte para a placa.
"""
import copy
import os
import uuid

from netlist import PARTS, STD
from sexp import dump, find, first, parse, q, unq

HERE = os.path.dirname(os.path.abspath(__file__))
HW = os.path.dirname(HERE)
PROJ = os.path.join(HW, "project")
NS = uuid.UUID("6f1b8c1e-0000-4000-8000-000000000001")


def uid(*k):
    return str(uuid.uuid5(NS, "/".join(map(str, k))))


_libs = {}


def lib_tree(lib):
    if lib not in _libs:
        path = (os.path.join(HW, "lib", "indicador.kicad_sym") if lib == "indicador"
                else STD + lib + ".kicad_sym")
        tree = parse(open(path, encoding="utf-8").read())[0]
        _libs[lib] = {unq(s[1]): s for s in find(tree, "symbol")}
    return _libs[lib]


def flat_symbol(lib, name):
    """Símbolo com 'extends' resolvido, renomeado para 'lib:nome'."""
    syms = lib_tree(lib)
    child = syms[name]
    ext = first(child, "extends")
    if not ext:
        s = copy.deepcopy(child)
    else:
        parent = unq(ext[1])
        s = copy.deepcopy(flat_symbol(lib, parent)[1])
        s = [y for y in s if not (isinstance(y, list) and y[0] == "property")]
        props = [copy.deepcopy(p) for p in find(child, "property")]
        # mantém as propriedades do pai que o filho não redefine
        have = {unq(p[1]) for p in props}
        for p in find(flat_symbol(lib, parent)[1], "property"):
            if unq(p[1]) not in have:
                props.append(copy.deepcopy(p))
        s = s[:2] + props + s[2:]
        for sub in find(s, "symbol"):
            sub[1] = q(name + unq(sub[1])[len(parent):])
    s = [y for y in s if not (isinstance(y, list) and y[0] == "extends")]
    s[1] = q(f"{lib}:{name}")
    return f"{lib}:{name}", s


def pins_of(sym, names=None):
    out = {}
    names = {} if names is None else names
    for sub in find(sym, "symbol"):
        for p in find(sub, "pin"):
            at = first(p, "at")
            num = unq(first(p, "number")[1])
            out[num] = (float(at[1]), float(at[2]), int(float(at[3])) if len(at) > 3 else 0)
            names[num] = unq(first(p, "name")[1])
    return out


def prop(name, val, x, y, hide=False):
    eff = ["effects", ["font", ["size", "1.27", "1.27"]]]
    if hide:
        eff.append(["hide", "yes"])
    return ["property", q(name), q(val), ["at", f"{x:.2f}", f"{y:.2f}", "0"], eff]


def label(net, x, y, outward):
    just = {0: "left", 90: "left", 180: "right", 270: "right"}[outward]
    return ["label", q(net), ["at", f"{x:.2f}", f"{y:.2f}", str(outward)],
            ["fields_autoplaced", "yes"],
            ["effects", ["font", ["size", "1.27", "1.27"]], ["justify", just, "bottom"]],
            ["uuid", q(uid("lbl", net, x, y))]]


def main():
    root = uid("root")
    libsyms, items = {}, []
    for ref, (lib, name, value, fp, lcsc, conns, (X, Y)) in PARTS.items():
        lid, sym = flat_symbol(lib, name)
        libsyms[lid] = sym
        pins = pins_of(sym)
        missing = set(conns) - set(pins)
        assert not missing, f"{ref}: pinos inexistentes {missing}"
        inst = ["symbol", ["lib_id", q(lid)], ["at", f"{X:.2f}", f"{Y:.2f}", "0"],
                ["unit", "1"], ["exclude_from_sim", "no"], ["in_bom", "no" if ref.startswith("#") or not lcsc else "yes"],
                ["on_board", "no" if ref.startswith("#") else "yes"], ["dnp", "no"],
                ["uuid", q(uid("sym", ref))],
                prop("Reference", ref, X, Y - 12.7, hide=ref.startswith("#")),
                prop("Value", value, X, Y + 12.7),
                prop("Footprint", fp, X, Y, hide=True),
                prop("Datasheet", "", X, Y, hide=True),
                prop("LCSC", lcsc, X, Y, hide=True)]
        for num in pins:
            inst.append(["pin", q(num), ["uuid", q(uid("pin", ref, num))]])
        inst.append(["instances", ["project", q("luxflag"),
                     ["path", q("/" + root), ["reference", q(ref)], ["unit", "1"]]]])
        items.append(inst)

        seen = {}
        for num, (px, py, ang) in pins.items():
            pt = (round(X + px, 2), round(Y - py, 2))
            if num not in conns:
                # pinos ocultos empilhados (ex.: GND/VBUS do USB) seguem o visível
                continue
            net = conns[num]
            if pt in seen:
                assert seen[pt] == net, f"{ref}.{num}: conflito no mesmo ponto"
                continue
            seen[pt] = net
            if net is None:
                items.append(["no_connect", ["at", f"{pt[0]:.2f}", f"{pt[1]:.2f}"],
                              ["uuid", q(uid("nc", ref, num))]])
            else:
                items.append(label(net, pt[0], pt[1], (ang + 180) % 360))

    sch = ["kicad_sch", ["version", "20250114"], ["generator", q("eeschema")],
           ["generator_version", q("9.0")], ["uuid", q(root)], ["paper", q("A4")],
           ["title_block", ["title", q("Luxafor Flag clone: 3x WS2816B-2020 (16 bit) + STM32C071G8U6")],
            ["date", q("2026-11-22")], ["rev", q("C")],
            ["comment", "1", q("Gerado por tools/gen_sch.py a partir de tools/netlist.py (base: rev A de lstavares84/luxafor)")]],
           ["lib_symbols", *libsyms.values()], *items,
           ["sheet_instances", ["path", q("/"), ["page", q("1")]]],
           ["embedded_fonts", "no"]]
    os.makedirs(PROJ, exist_ok=True)
    with open(os.path.join(PROJ, "luxflag.kicad_sch"), "w", encoding="utf-8") as f:
        f.write(dump(sch) + "\n")
    with open(os.path.join(PROJ, "sym-lib-table"), "w") as f:
        f.write('(sym_lib_table\n\t(version 7)\n\t(lib (name "indicador")(type "KiCad")'
                '(uri "${KIPRJMOD}/../lib/indicador.kicad_sym")(options "")(descr ""))\n)\n')
    with open(os.path.join(PROJ, "fp-lib-table"), "w") as f:
        f.write('(fp_lib_table\n\t(version 7)\n\t(lib (name "indicador")(type "KiCad")'
                '(uri "${KIPRJMOD}/../lib/indicador.pretty")(options "")(descr ""))\n)\n')
    print("ok:", len(PARTS), "componentes")


if __name__ == "__main__":
    main()
