"""SIGNA Pendente rev B: STEP/STL/3MF por peca + conjunto integrado signa_conjunto.step
(placa rev D com componentes + pecas plasticas/metalicas + botao + cabo USB-C)."""
import os
from build123d import *
from parts import *
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'export')
for d in ('step', 'stl', '3mf'):
    os.makedirs(os.path.join(OUT, d), exist_ok=True)

FAB = {
    'P01_tubo_difusor': (tube(), Color(0.95, 0.95, 0.97, 0.6)),
    'P02_tampa_Al6061': (cap(), Color(0.08, 0.08, 0.09)),
    'P02b_tampa_impressa': (cap(printed=True), Color(0.12, 0.12, 0.12)),
    'P03_berco_PC': (carrier(), Color(0.98, 0.98, 0.98)),
    'P04_tampao_inferior': (end_plug(), Color(0.93, 0.93, 0.95, 0.7)),
    'P05_passa_cabo_TPE': (grommet(), Color(0.10, 0.10, 0.10)),
    'P06_botao_PC': (plunger(), Color(0.93, 0.93, 0.95, 0.8)),
}
for name, (p, col) in FAB.items():
    p.label, p.color = name, col
    export_step(p, os.path.join(OUT, 'step', name + '.step'))
    export_stl(p, os.path.join(OUT, 'stl', name + '.stl'), tolerance=0.01, angular_tolerance=0.1)
    try:
        m = Mesher(); m.add_shape(p, linear_deflection=0.01, angular_deflection=0.1); m.write(os.path.join(OUT, '3mf', name + '.3mf'))
    except Exception as e:
        print('3mf falhou', name, e)
    print('ok', name, round(p.volume, 1))

b = board()
export_step(b, os.path.join(OUT, 'step', 'E01_placa_SIGNA_revD.step'))
export_stl(b, os.path.join(OUT, 'stl', 'E01_placa_SIGNA_revD.stl'), tolerance=0.01, angular_tolerance=0.2)

shell, ov, boot = cable_plug()
shell.color = Color(0.80, 0.80, 0.82); ov.color = Color(0.13, 0.13, 0.14); boot.color = Color(0.10, 0.10, 0.11)
cab = cable(); cab.color = Color(0.10, 0.10, 0.11)
cabo = Compound(children=[shell, ov, boot, cab], label='C01_cabo_USB-C')
export_step(cabo, os.path.join(OUT, 'step', 'C01_cabo_USB-C.step'))
export_stl(cabo, os.path.join(OUT, 'stl', 'C01_cabo_USB-C.stl'), tolerance=0.02, angular_tolerance=0.2)

asm = Compound(children=[FAB[k][0] for k in FAB if k != 'P02b_tampa_impressa'] + [b, cabo], label='SIGNA_conjunto_revB')
export_step(asm, os.path.join(OUT, '..', 'signa_conjunto.step'))
print('conjunto ok; cabo modelado %.0f mm' % cable_length())
