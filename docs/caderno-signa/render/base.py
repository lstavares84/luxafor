"""Renders do LUXCLONE Pendente (Blender/Cycles). Uso:
blender -b --python render_blender.py -- <cena> [amostras]
cenas: iso_desligado, iso_ligado, explodida, corte, pendurado
"""
import bpy, sys, math, os, ast
from mathutils import Vector
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['iso_desligado']
SCENE = argv[0]
SAMPLES = int(argv[1]) if len(argv) > 1 else 96
ROOT = '/workspace/pendente'
EXP = os.path.join(ROOT, 'export')
GLOW = tuple(float(x) for x in os.environ.get('GLOW','0.9,0.05,0.04').split(','))
S = 0.001                  # mm -> m
EMIT = float(os.environ.get('EMIT', '1.1'))

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'
sc.cycles.samples = SAMPLES
sc.cycles.use_denoising = bool(os.environ.get('DENOISE', '1') == '1')
try:
    sc.cycles.denoiser = 'OPENIMAGEDENOISE'
except Exception:
    pass
sc.cycles.max_bounces = 12
sc.cycles.transmission_bounces = 12
sc.render.resolution_x, sc.render.resolution_y = 1600, 1200
sc.view_settings.view_transform = 'Standard'
sc.view_settings.look = 'None'


def mat(name, base, rough=0.5, metal=0.0, trans=0.0, ior=1.5, emit=None, emit_s=0.0, alpha=1.0, sss=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*base, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    b.inputs['Transmission Weight'].default_value = trans
    b.inputs['IOR'].default_value = ior
    if sss:
        b.inputs['Subsurface Weight'].default_value = sss
        b.inputs['Subsurface Radius'].default_value = (0.004, 0.004, 0.004)
        b.inputs['Subsurface Scale'].default_value = 1.0
    if emit:
        b.inputs['Emission Color'].default_value = (*emit, 1)
        b.inputs['Emission Strength'].default_value = emit_s
    return m


def frosted(on):
    """PC opalino: transmissao difusa + glow opcional (gradiente mais forte perto dos LEDs)."""
    m = bpy.data.materials.new('PC_opal_on' if on else 'PC_opal')
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.92, 0.92, 0.94, 1)
    b.inputs['Roughness'].default_value = 0.65
    b.inputs['Transmission Weight'].default_value = 0.85
    b.inputs['IOR'].default_value = 1.58
    if on:
        b.inputs['Base Color'].default_value = (*[0.15 + 0.85 * c for c in GLOW], 1)
        tc = nt.nodes.new('ShaderNodeTexCoord')
        sep = nt.nodes.new('ShaderNodeSeparateXYZ')
        nt.links.new(tc.outputs['Object'], sep.inputs[0])
        ramp = nt.nodes.new('ShaderNodeValToRGB')
        mp = nt.nodes.new('ShaderNodeMapRange')
        mp.inputs['From Min'].default_value = 0.0
        mp.inputs['From Max'].default_value = 0.052
        nt.links.new(sep.outputs['Z'], mp.inputs['Value'])
        nt.links.new(mp.outputs['Result'], ramp.inputs['Fac'])
        ramp.color_ramp.elements[0].position = 0.0
        ramp.color_ramp.elements[0].color = (*[c * 1.0 for c in GLOW], 1)
        e = ramp.color_ramp.elements.new(0.45); e.color = (*GLOW, 1)
        ramp.color_ramp.elements[-1].position = 1.0
        ramp.color_ramp.elements[-1].color = (*[c * 0.35 for c in GLOW], 1)
        nt.links.new(ramp.outputs['Color'], b.inputs['Emission Color'])
        b.inputs['Emission Strength'].default_value = EMIT
    return m


M = dict(
    alu=mat('Al_anod_preto', (0.025, 0.025, 0.028), rough=0.42, metal=1.0),
    alu_cut=mat('Al_corte', (0.75, 0.75, 0.77), rough=0.3, metal=1.0),
    tpe=mat('TPE', (0.02, 0.02, 0.02), rough=0.75),
    pcw=mat('PC_branco', (0.92, 0.92, 0.9), rough=0.45, sss=0.15),
    cable=mat('cabo', (0.015, 0.015, 0.017), rough=0.8),
)


def imp(path, name, material, loc=(0, 0, 0)):
    bpy.ops.wm.stl_import(filepath=path, global_scale=S)
    o = bpy.context.selected_objects[0]
    o.name = name
    o.data.materials.clear()
    o.data.materials.append(material)
    o.location = Vector(loc) * S
    bpy.ops.object.shade_auto_smooth(angle=math.radians(35))
    return o


def board(loc=(0, 0, 0), on=False):
    d = os.path.join(EXP, 'board_parts')
    objs = []
    for f in sorted(os.listdir(d)):
        if not f.endswith('.stl'):
            continue
        col = ast.literal_eval(open(os.path.join(d, f.replace('.stl', '.color'))).read())
        base = tuple(col[:3]) if col else (0.5, 0.5, 0.5)
        if base == (0.31, 0.48, 0.41):
            m = mat('pcb', (0.015, 0.09, 0.045), rough=0.3)
        elif base[0] > 0.85:
            m = mat('led', (0.95, 0.95, 0.9), rough=0.3, emit=GLOW if on else None, emit_s=6.0 if on else 0)
        elif base == (0.82, 0.82, 0.78):
            m = mat('metal', (0.8, 0.8, 0.78), rough=0.25, metal=1.0)
        else:
            m = mat('comp' + f, base, rough=0.5)
        objs.append(imp(os.path.join(d, f), 'placa_' + f[:-4], m, loc))
    return objs


def world(color=(0.8, 0.8, 0.82), strength=1.0):
    w = bpy.data.worlds.new('w'); sc.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes['Background']
    bg.inputs[0].default_value = (*color, 1)
    bg.inputs[1].default_value = strength


def area(loc, size, energy, color=(1, 1, 1), target=(0, 0, 0.04)):
    l = bpy.data.lights.new('a', 'AREA'); l.size = size; l.energy = energy; l.color = color
    o = bpy.data.objects.new('a', l); sc.collection.objects.link(o)
    o.location = loc
    d = Vector(target) - Vector(loc)
    o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return o


def point(loc, energy, color, radius=0.002):
    l = bpy.data.lights.new('p', 'POINT'); l.energy = energy; l.color = color; l.shadow_soft_size = radius
    o = bpy.data.objects.new('p', l); sc.collection.objects.link(o); o.location = loc
    return o


def camera(loc, target, lens=85, roll=0.0, ortho=None):
    c = bpy.data.cameras.new('c'); c.lens = lens; c.clip_start = 0.001
    if ortho:
        c.type = 'ORTHO'; c.ortho_scale = ortho
    o = bpy.data.objects.new('c', c); sc.collection.objects.link(o)
    o.location = loc
    d = Vector(target) - Vector(loc)
    o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    o.rotation_euler.rotate_axis('Z', math.radians(roll))
    sc.camera = o
    return o


def backdrop(color=(0.85, 0.85, 0.87), rough=0.6, y=-0.08):
    bpy.ops.mesh.primitive_plane_add(size=2, location=(0, y, 0.04), rotation=(math.radians(90), 0, 0))
    p = bpy.context.object
    p.data.materials.append(mat('fundo', color, rough=rough))
    return p


def product(on=False, cable_len=120, offs=None):
    offs = offs or {}
    o = lambda k: offs.get(k, (0, 0, 0))
    st = os.path.join(EXP, 'stl')
    imp(os.path.join(st, 'P01_tubo_difusor.stl'), 'tubo', frosted(on), o('tube'))
    imp(os.path.join(st, 'P02_tampa_Al6061.stl'), 'tampa', M['alu'], o('cap'))
    imp(os.path.join(st, 'P03_berco_PC.stl'), 'berco', M['pcw'], o('carrier'))
    imp(os.path.join(st, 'P04_tampao_inferior.stl'), 'tampao', frosted(on), o('plug'))
    imp(os.path.join(st, 'P05_passa_cabo_TPE.stl'), 'passa', M['tpe'], o('grommet'))
    board(o('board'), on)
    if cable_len:
        imp(os.path.join(EXP, 'section', 'cable.stl'), 'cabo', M['cable'], o('cable'))
        # extensao do cabo para fora do quadro
        bpy.ops.mesh.primitive_cylinder_add(radius=0.002, depth=cable_len * S, location=(0, 0.00005, (137.5 + cable_len / 2) * S))
        bpy.context.object.data.materials.append(M['cable'])
    if on:
        for z in (10, 17, 24):
            point((0, 0.0005, z * S), 0.08, GLOW)


