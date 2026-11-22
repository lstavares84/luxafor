"""Renders do caderno conceitual (Blender 4.2/Cycles). Reaproveita geometria do Pendente.
uso: blender -b --python scenes.py -- <cena> [amostras]"""
import sys, os, json
sys.argv_saved = list(sys.argv)
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'base.py')).read())
OUTD = '/workspace/caderno-revC/img'
PROD = json.load(open('/workspace/caderno-revC/dados/produto.json'))

def lin(h):
    h = h.lstrip('#'); c = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)

MODE = {m['id']: m['hex'] for m in PROD['modos']}
BRI = {m['id']: m.get('brilho_render', 1.0) for m in PROD['modos']}
IVORY = lin('#EEEAE2')


def ivory_studio(y=-0.08, z0=None):
    """estúdio marfim: fundo transparente (composto sobre o papel #EEEAE2 depois) + piso 'shadow catcher' opcional"""
    world(IVORY, 0.25)
    sc.view_settings.exposure = float(os.environ.get('EXPO', '-1.0'))
    sc.render.film_transparent = True
    sc.render.image_settings.color_mode = 'RGBA'
    if z0 is not None:
        bpy.ops.mesh.primitive_plane_add(size=4, location=(0, 0, z0))
        bpy.context.object.is_shadow_catcher = True


def shift_new(before, dx=0, dz=0):
    for o in sc.objects:
        if o.name not in before:
            o.location.x += dx; o.location.z += dz


def apply_bri(objs, hx, bri, em_scale=1.0):
    scl = bri ** 2.2
    off_base = (0.92, 0.92, 0.94)
    col = lin(hx)
    on_base = tuple(0.15 + 0.85 * c for c in col)
    mix_base = tuple(off_base[i] * (1 - bri) + on_base[i] * bri for i in range(3))
    for o in objs:
        if o.type == 'LIGHT' and o.data.type == 'POINT':
            o.data.energy = 0.025 * scl
            o.data.color = col
        if getattr(o, 'data', None) is not None and hasattr(o.data, 'materials'):
            for m in o.data.materials:
                if not m or not m.use_nodes:
                    continue
                b = m.node_tree.nodes.get('Principled BSDF')
                if not b:
                    continue
                if m.name.startswith('led'):
                    b.inputs['Emission Strength'].default_value = 1.6 * scl
                    b.inputs['Emission Color'].default_value = (*col, 1)
                if m.name.startswith('PC_opal'):
                    b.inputs['Base Color'].default_value = (*mix_base, 1)
                    b.inputs['Emission Strength'].default_value = em_scale * scl


def apply_misto(objs, hx_sala='#2FD28A', bri_sala=0.58, hx_ia='#3D8BFF', bri_ia=0.88):
    """LED 1 (baixo, z=10 mm) = IA; LED 2+3 (meio+topo, z=17,24 mm) = SALA."""
    col_s, col_i = lin(hx_sala), lin(hx_ia)
    scl_s, scl_i = bri_sala ** 2.2, bri_ia ** 2.2
    for o in objs:
        if o.type == 'LIGHT' and o.data.type == 'POINT':
            z = o.location.z
            if z < 0.0135:
                o.data.color = col_i
                o.data.energy = 0.025 * scl_i
            else:
                o.data.color = col_s
                o.data.energy = 0.032 * scl_s
        if getattr(o, 'data', None) is not None and hasattr(o.data, 'materials'):
            for m in o.data.materials:
                if not m or not m.use_nodes:
                    continue
                nt = m.node_tree
                b = nt.nodes.get('Principled BSDF')
                if not b:
                    continue
                if m.name.startswith('led'):
                    tc = nt.nodes.new('ShaderNodeTexCoord')
                    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
                    nt.links.new(tc.outputs['Object'], sep.inputs[0])
                    mp = nt.nodes.new('ShaderNodeMapRange')
                    mp.inputs['From Min'].default_value = 0.0135
                    mp.inputs['From Max'].default_value = 0.0155
                    nt.links.new(sep.outputs['Z'], mp.inputs['Value'])
                    ramp = nt.nodes.new('ShaderNodeValToRGB')
                    ramp.color_ramp.elements[0].position = 0.0
                    ramp.color_ramp.elements[0].color = (*[c * scl_i for c in col_i], 1)
                    ramp.color_ramp.elements[-1].position = 1.0
                    ramp.color_ramp.elements[-1].color = (*[c * scl_s for c in col_s], 1)
                    nt.links.new(mp.outputs['Result'], ramp.inputs['Fac'])
                    nt.links.new(ramp.outputs['Color'], b.inputs['Emission Color'])
                    b.inputs['Emission Strength'].default_value = 1.8
                if m.name.startswith('PC_opal'):
                    for l in list(nt.links):
                        if l.to_socket == b.inputs['Emission Color']:
                            nt.links.remove(l)
                    tc = nt.nodes.new('ShaderNodeTexCoord')
                    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
                    nt.links.new(tc.outputs['Object'], sep.inputs[0])
                    mp = nt.nodes.new('ShaderNodeMapRange')
                    mp.inputs['From Min'].default_value = 0.004
                    mp.inputs['From Max'].default_value = 0.048
                    nt.links.new(sep.outputs['Z'], mp.inputs['Value'])
                    ramp = nt.nodes.new('ShaderNodeValToRGB')
                    ramp.color_ramp.elements[0].position = 0.0
                    ramp.color_ramp.elements[0].color = (*[c * 1.0 * scl_i for c in col_i], 1)
                    e1 = ramp.color_ramp.elements.new(0.16); e1.color = (*[c * 0.85 * scl_i for c in col_i], 1)
                    e2 = ramp.color_ramp.elements.new(0.27); e2.color = (*[c * 0.90 * scl_s for c in col_s], 1)
                    e3 = ramp.color_ramp.elements.new(0.55); e3.color = (*[c * 0.85 * scl_s for c in col_s], 1)
                    ramp.color_ramp.elements[-1].position = 1.0
                    ramp.color_ramp.elements[-1].color = (*[c * 0.45 * scl_s for c in col_s], 1)
                    nt.links.new(mp.outputs['Result'], ramp.inputs['Fac'])
                    nt.links.new(ramp.outputs['Color'], b.inputs['Emission Color'])
                    b.inputs['Emission Strength'].default_value = 1.1
                    b.inputs['Base Color'].default_value = (0.60, 0.72, 0.65, 1)

out = os.path.join(OUTD, SCENE + '.png')
if SCENE in ('capa', 'p8_alerta', 'p9_modos') or SCENE.startswith('p5_'):
    sc.render.film_transparent = True
    sc.render.image_settings.color_mode = 'RGBA'

if SCENE == 'capa':
    GLOW = lin(MODE['sala_ocupado'])
    world((0.004, 0.005, 0.007), 1.0)
    product(on=True, cable_len=300)
    area((-0.25, 0.05, 0.15), 0.15, 1.2, color=(0.75, 0.82, 1.0))
    camera((0.16, 0.30, 0.10), (0, 0, 0.045), lens=95)
    sc.render.resolution_x, sc.render.resolution_y = 1200, 1600
elif SCENE == 'p8_principal':
    GLOW = lin(MODE['sala_ocupado'])
    ivory_studio()
    product(on=True, cable_len=120)
    area((0.12, 0.25, 0.2), 0.3, 4)
    area((-0.2, 0.1, 0.12), 0.3, 2)
    camera((0.16, 0.30, 0.10), (0, 0, 0.05), lens=100)
    sc.render.resolution_x, sc.render.resolution_y = 1200, 1500
elif SCENE == 'p8_alerta':
    GLOW = lin(MODE['sala_prestes'])
    world((0.003, 0.003, 0.004), 1.0)
    product(on=True, cable_len=120)
    area((-0.18, -0.02, 0.10), 0.08, 1.5, color=(0.8, 0.85, 1.0), target=(0, 0, 0.05))
    area((0.18, -0.02, 0.10), 0.08, 1.0, color=(0.8, 0.85, 1.0), target=(0, 0, 0.05))
    camera((0.0, 0.40, 0.045), (0, 0, 0.045), lens=110)
    sc.render.resolution_x, sc.render.resolution_y = 900, 1200
elif SCENE == 'p8_detalhe':
    ivory_studio()
    sd = os.path.join(EXP, 'section')
    imp(os.path.join(sd, 'tube_corte.stl'), 'tubo', frosted(False))
    imp(os.path.join(sd, 'cap_corte.stl'), 'tampa', M['alu'])
    imp(os.path.join(sd, 'grommet_corte.stl'), 'passa', M['tpe'])
    imp(os.path.join(sd, 'carrier.stl'), 'berco', M['pcw'])
    imp(os.path.join(sd, 'cable_corte.stl'), 'cabo', M['cable'])
    board()
    area((0.1, 0.3, 0.15), 0.3, 5)
    area((-0.2, 0.15, 0.05), 0.3, 2.5)
    camera((0.045, 0.14, 0.085), (0, 0, 0.064), lens=100)
    sc.render.resolution_x, sc.render.resolution_y = 1200, 1200
elif SCENE == 'p9_uso':
    GLOW = lin(MODE['sala_ocupado'])
    exec(open('/workspace/pendente/cad/render_blender.py').read().split("elif SCENE == 'pendurado':")[1].split("if SCENE.startswith('passo')")[0].replace('\n    ', '\n').replace("sc.view_settings.look = 'AgX - High Contrast'", ''))
elif SCENE == 'p9_modos':
    world((0.004, 0.005, 0.007), 1.0)
    seq = ['sala_livre', 'sala_prestes', 'sala_ocupado', 'misto', 'ia_processando', 'ia_atencao', 'ia_erro', 'ia_limite']
    for i, k in enumerate(seq):
        before = set(o.name for o in sc.objects)
        if k == 'misto':
            GLOW = lin(MODE['sala_livre'])
            product(on=True, cable_len=60)
            new_objs = [o for o in sc.objects if o.name not in before]
            apply_misto(new_objs, MODE['sala_livre'], 0.65, MODE['ia_erro'], 0.85)
        else:
            GLOW = lin(MODE[k])
            product(on=True, cable_len=60)
            new_objs = [o for o in sc.objects if o.name not in before]
            apply_bri(new_objs, MODE[k], BRI[k])
        shift_new(before, dx=(3.5 - i) * 0.029)
    area((0.0, 0.35, 0.25), 0.8, 0.6)
    area((-0.3, 0.05, 0.12), 0.25, 1.0, color=(0.8, 0.85, 1.0))
    camera((0.0, 0.64, 0.055), (0, 0, 0.040), lens=65)
    sc.render.resolution_x, sc.render.resolution_y = 2400, 960
elif SCENE == 'p2_iso':
    ivory_studio()
    product(on=False, cable_len=60)
    area((0.12, 0.25, 0.2), 0.3, 4)
    area((-0.2, 0.1, 0.12), 0.3, 2)
    camera((0.20, 0.26, 0.16), (0, 0, 0.044), lens=110)
    sc.render.resolution_x, sc.render.resolution_y = 1000, 1400
elif SCENE == 'p9_explodida':
    ivory_studio()
    offs = dict(plug=(0, 0, -78), tube=(0, 0, -58), carrier=(0, 0, 0), board=(26, 0, 4), cap=(0, 0, 38), grommet=(0, 0, 66))
    product(on=False, cable_len=0, offs=offs)
    area((0.2, 0.35, 0.2), 0.4, 7)
    area((-0.25, 0.2, 0.0), 0.4, 3)
    camera((0.24, 0.36, 0.07), (0.012, 0, 0.034), lens=60)
    sc.render.resolution_x, sc.render.resolution_y = 1200, 1800
elif SCENE.startswith('p7_'):
    ivory_studio(z0=0.0)
    board(loc=(0, 0, -6.5))
    area((0.1, 0.3, 0.15), 0.3, 4)
    area((-0.2, 0.15, 0.05), 0.3, 2)
    area((0.0, -0.2, 0.2), 0.3, 1.5)
    if SCENE == 'p7_frente':
        camera((0, 0.25, 0.0225), (0, 0, 0.0225), lens=135)
        sc.render.resolution_x, sc.render.resolution_y = 700, 1500
    elif SCENE == 'p7_verso':
        camera((0, -0.25, 0.0225), (0, 0, 0.0225), lens=135)
        sc.render.resolution_x, sc.render.resolution_y = 700, 1500
    else:
        camera((0.09, 0.13, 0.065), (0, -0.001, 0.0225), lens=95)
        sc.render.resolution_x, sc.render.resolution_y = 1400, 1400
elif SCENE == 'p5_misto':
    GLOW = lin(MODE['sala_livre'])
    world((0.004, 0.005, 0.007), 1.0)
    product(on=True, cable_len=80)
    apply_misto(list(sc.objects), MODE['sala_livre'], 0.65, MODE['ia_erro'], 0.85)
    area((0.0, 0.35, 0.25), 0.6, 0.35)
    area((-0.22, 0.08, 0.12), 0.18, 0.55, color=(0.8, 0.85, 1.0))
    camera((0.055, 0.40, 0.055), (0, 0, 0.040), lens=105)
    sc.render.resolution_x, sc.render.resolution_y = 800, 1500
elif SCENE.startswith('p5_'):
    key = SCENE[3:]
    hx, bri = MODE[key], BRI[key]
    GLOW = lin(hx)
    EMIT = 1.0 * (bri ** 2.2)
    world((0.004, 0.005, 0.007), 1.0)
    product(on=True, cable_len=80)
    apply_bri(list(sc.objects), hx, bri)
    area((0.0, 0.35, 0.25), 0.6, 0.35)
    area((-0.22, 0.08, 0.12), 0.18, 0.55, color=(0.8, 0.85, 1.0))
    camera((0.055, 0.40, 0.055), (0, 0, 0.040), lens=105)
    sc.render.resolution_x, sc.render.resolution_y = 800, 1500

sc.render.filepath = out
bpy.ops.render.render(write_still=True)
print('RENDER OK', out)
