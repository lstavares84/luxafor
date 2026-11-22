"""Renders + GLB do conjunto SIGNA (Blender 4.2 / Cycles). Uso:
blender -b --python render_blender.py -- <cena> [amostras]
cenas: iso, explodida, corte, detalhe_usbc, em_uso, livre (em uso, LIVRE), glb (exporta signa_conjunto.glb)
"""
import bpy, sys, math, os, json
from mathutils import Vector
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['iso']
SCENE = argv[0]
SAMPLES = int(argv[1]) if len(argv) > 1 else 96
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MD = os.path.join(ROOT, 'export', 'mesh')
GEO = json.load(open(os.path.join(MD, 'geo.json')))
S = 0.001
# OCUPADO #FF3B2F e LIVRE #2FD28A (sRGB -> linear)
def lin(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)
GLOW = lin('#2FD28A') if SCENE == 'livre' else lin('#FF3B2F')
EMIT = float(os.environ.get('EMIT', '1.5'))

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = SAMPLES
sc.cycles.use_denoising = True
try:
    sc.cycles.denoiser = 'OPENIMAGEDENOISE'
except Exception:
    pass
sc.cycles.max_bounces = 12; sc.cycles.transmission_bounces = 12
sc.render.resolution_x, sc.render.resolution_y = 1200, 1600
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'


def mat(name, base, rough=0.5, metal=0.0, trans=0.0, ior=1.5, emit=None, emit_s=0.0, sss=0.0, spec=0.5):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Specular IOR Level'].default_value = spec
    b.inputs['Base Color'].default_value = (*base, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    b.inputs['Transmission Weight'].default_value = trans
    b.inputs['IOR'].default_value = ior
    if sss:
        b.inputs['Subsurface Weight'].default_value = sss
        b.inputs['Subsurface Radius'].default_value = (0.004, 0.004, 0.004)
    if emit:
        b.inputs['Emission Color'].default_value = (*emit, 1)
        b.inputs['Emission Strength'].default_value = emit_s
    return m


def frosted(on, name='PC_opal'):
    m = bpy.data.materials.new(name + ('_on' if on else '')); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.92, 0.92, 0.94, 1)
    b.inputs['Roughness'].default_value = 0.65
    b.inputs['Transmission Weight'].default_value = 0.85
    b.inputs['IOR'].default_value = 1.58
    if on:
        b.inputs['Base Color'].default_value = (*[0.6 + 0.4 * c for c in GLOW], 1)
        tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
        nt.links.new(tc.outputs['Object'], sep.inputs[0])
        mp = nt.nodes.new('ShaderNodeMapRange'); mp.inputs['From Min'].default_value = 0.0; mp.inputs['From Max'].default_value = 0.052
        nt.links.new(sep.outputs['Z'], mp.inputs['Value'])
        ramp = nt.nodes.new('ShaderNodeValToRGB'); nt.links.new(mp.outputs['Result'], ramp.inputs['Fac'])
        el = ramp.color_ramp.elements
        el[0].position = 0.0; el[0].color = (*[c * 0.8 for c in GLOW], 1)
        e = el.new(0.25); e.color = (*GLOW, 1)
        e = el.new(0.55); e.color = (*GLOW, 1)
        el[-1].position = 1.0; el[-1].color = (*[c * 0.3 for c in GLOW], 1)
        nt.links.new(ramp.outputs['Color'], b.inputs['Emission Color'])
        b.inputs['Emission Strength'].default_value = EMIT
    return m


M = dict(
    alu=mat('Al_anod_preto', (0.025, 0.025, 0.028), rough=0.42, metal=1.0),
    tpe=mat('TPE', (0.008, 0.008, 0.008), rough=0.7, spec=0.25),
    pcw=mat('PC_branco', (0.92, 0.92, 0.9), rough=0.45, sss=0.15),
    cable=mat('cabo', (0.007, 0.007, 0.008), rough=0.6, spec=0.25),
    overmold=mat('sobremolde', (0.012, 0.012, 0.014), rough=0.55, spec=0.3),
    steel=mat('aco', (0.8, 0.8, 0.82), rough=0.22, metal=1.0),
)
BOARD_M = dict(
    pcb=mat('pcb', (0.012, 0.075, 0.04), rough=0.35),
    cobre=mat('cobre_mask', (0.025, 0.12, 0.06), rough=0.35),
    pad=mat('pad', (0.85, 0.72, 0.45), rough=0.25, metal=1.0),
    metal=M['steel'],
    comp=mat('comp', (0.42, 0.30, 0.20), rough=0.5),
    preto=mat('preto', (0.02, 0.02, 0.022), rough=0.4),
    branco=mat('branco', (0.9, 0.9, 0.88), rough=0.4),
    cinza=mat('cinza', (0.08, 0.08, 0.085), rough=0.45),
    led_corpo=mat('led_corpo', (0.95, 0.95, 0.92), rough=0.35),
)


def imp(name, material, loc=(0, 0, 0), path=None):
    p = path or os.path.join(MD, name + '.stl')
    if not os.path.exists(p):
        return None
    bpy.ops.wm.stl_import(filepath=p, global_scale=S)
    o = bpy.context.selected_objects[0]; o.name = name
    o.data.materials.clear(); o.data.materials.append(material)
    o.location = Vector(loc) * S
    bpy.ops.object.shade_auto_smooth(angle=math.radians(35))
    return o


def board(loc=(0, 0, 0), on=False, cut=False):
    sfx = '_corte' if cut else ''
    for k, m in BOARD_M.items():
        imp('placa_' + k + sfx, m, loc)
    lens = mat('led_lente', (0.95, 0.95, 1.0), rough=0.2, emit=GLOW if on else None, emit_s=40.0 if on else 0)
    imp('placa_led_lente' + sfx, lens, loc)


def product(on=False, cable='curto', offs=None, cut=False):
    offs = offs or {}
    o = lambda k: offs.get(k, (0, 0, 0))
    sfx = '_corte' if cut else ''
    imp('tubo' + sfx, frosted(on), o('tube'))
    imp('tampa' + sfx, M['alu'], o('cap'))
    imp('berco' + sfx, M['pcw'], o('carrier'))
    imp('tampao' + sfx, frosted(on, 'PC_opal_tampao'), o('plug'))
    imp('botao' + sfx, frosted(on, 'PC_opal_botao'), o('button'))
    imp('passa_cabo' + sfx, M['tpe'], o('grommet'))
    board(o('board'), on, cut)
    if cable:
        imp('plugue_casca' + sfx, M['steel'], o('cable'))
        imp('sobremolde' + sfx, M['overmold'], o('cable'))
        imp('alivio' + sfx, M['overmold'], o('cable'))
        nm = {'longo': 'cabo', 'toco': 'cabo_toco'}.get(cable, 'cabo_curto' + sfx)
        imp(nm, M['cable'], o('cable'))
    if on:
        for z in GEO['LED_Z']:
            l = bpy.data.lights.new('p', 'POINT'); l.energy = 0.05; l.color = GLOW; l.shadow_soft_size = 0.002
            ob = bpy.data.objects.new('p', l); sc.collection.objects.link(ob); ob.location = (0, 0.0005, z * S)


def world(color=(0.8, 0.8, 0.82), strength=1.0):
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
    bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = (*color, 1); bg.inputs[1].default_value = strength


def area(loc, size, energy, color=(1, 1, 1), target=(0, 0, 0.04)):
    l = bpy.data.lights.new('a', 'AREA'); l.size = size; l.energy = energy; l.color = color
    o = bpy.data.objects.new('a', l); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()


def camera(loc, target, lens=85):
    c = bpy.data.cameras.new('c'); c.lens = lens; c.clip_start = 0.001
    o = bpy.data.objects.new('c', c); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = o


def backdrop(color=(0.85, 0.85, 0.87), rough=0.6, y=-0.08):
    bpy.ops.mesh.primitive_plane_add(size=2, location=(0, y, 0.04), rotation=(math.radians(90), 0, 0))
    bpy.context.object.data.materials.append(mat('fundo', color, rough=rough))


out = os.path.join(ROOT, 'renders', SCENE + '.png')
os.makedirs(os.path.dirname(out), exist_ok=True)
if SCENE == 'iso':
    world((0.9, 0.9, 0.92), 0.08); backdrop()
    product(on=False)
    area((0.12, 0.25, 0.2), 0.25, 6); area((-0.2, 0.1, 0.12), 0.3, 3); area((0.0, -0.05, 0.25), 0.2, 2.5)
    camera((0.17, 0.33, 0.005), (0, 0, 0.046), lens=100)
elif SCENE == 'explodida':
    world((0.92, 0.92, 0.94), 0.06); backdrop((0.22, 0.23, 0.25), y=-0.1)
    offs = dict(plug=(0, 0, -86), button=(0, 0, -72), tube=(0, 0, -62), carrier=(0, 0, 0), board=(30, 0, 4),
                cap=(0, 0, 40), grommet=(0, 0, 70), cable=(0, 0, 92))
    product(on=False, cable='toco', offs=offs)
    area((0.2, 0.35, 0.2), 0.4, 9); area((-0.25, 0.2, 0.0), 0.4, 4); area((0.0, 0.1, 0.4), 0.3, 3)
    camera((0.26, 0.42, 0.07), (0.012, 0, 0.050), lens=48)
    sc.render.resolution_x, sc.render.resolution_y = 1200, 1900
elif SCENE in ('corte', 'detalhe_usbc'):
    world((0.9, 0.9, 0.92), 0.08); backdrop(y=-0.05)
    product(on=False, cable='curto', cut=True)
    area((0.1, 0.3, 0.15), 0.3, 5); area((-0.2, 0.15, 0.05), 0.3, 2.5); area((0.05, 0.2, 0.0), 0.2, 1.5)
    if SCENE == 'corte':
        camera((0.09, 0.30, 0.075), (0, 0, 0.05), lens=92)
    else:
        camera((0.024, 0.058, 0.060), (0, -0.0005, 0.0495), lens=95)
        sc.render.resolution_x, sc.render.resolution_y = 1600, 1200
elif SCENE in ('em_uso', 'livre'):
    world((0.004, 0.004, 0.005), 1.0)
    top = (GEO['CABLE_RISE'] + 12.0 - 1.9) * S
    bpy.ops.mesh.primitive_plane_add(size=3, location=(0, -0.25, 0.3), rotation=(math.radians(90), 0, 0))
    bpy.context.object.data.materials.append(mat('parede', (0.06, 0.06, 0.065), rough=0.9))
    bpy.ops.mesh.primitive_plane_add(size=3, location=(0, 0.5, -0.36))
    bpy.context.object.data.materials.append(mat('mesa', (0.03, 0.025, 0.02), rough=0.5))
    # monitor: frente em y=-12 mm, 28 mm de espessura no topo, borda direita em x=+6 mm, topo sob o cabo
    W, Hm, Dm = 0.62, 0.36, 0.028
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.006 - W / 2, -0.012 - Dm / 2, top - Hm / 2))
    mon = bpy.context.object; mon.scale = (W, Dm, Hm)
    mon.data.materials.append(mat('monitor', (0.02, 0.02, 0.022), rough=0.35))
    bpy.ops.object.modifier_add(type='BEVEL'); mon.modifiers[-1].width = 0.003; mon.modifiers[-1].segments = 3
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.006 - W / 2, -0.0118, top - Hm / 2 - 0.004))
    scr = bpy.context.object; scr.scale = (W - 0.016, 0.0006, Hm - 0.03)
    scr.data.materials.append(mat('tela', (0.01, 0.012, 0.02), rough=0.08, emit=(0.10, 0.14, 0.25), emit_s=0.18))
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.006 - W / 2, -0.06, top - Hm - 0.15)); bpy.context.object.scale = (0.06, 0.03, 0.3)
    bpy.context.object.data.materials.append(mat('ped', (0.03, 0.03, 0.03), rough=0.4))
    product(on=True, cable='longo')
    l = bpy.data.lights.new('g', 'POINT'); l.energy = 1.5; l.color = GLOW; l.shadow_soft_size = 0.008
    ob = bpy.data.objects.new('g', l); sc.collection.objects.link(ob); ob.location = (0.0, 0.012, 0.03)
    area((-0.3, 0.6, 0.5), 0.8, 5, color=(0.8, 0.85, 1.0), target=(-0.1, 0, 0.05))
    area((0.5, 0.25, 0.3), 0.3, 1.0, color=(1, 0.9, 0.85), target=(0, 0, 0.05))
    camera((0.11, 0.25, 0.115), (-0.022, -0.012, 0.074), lens=44)
    sc.render.resolution_x, sc.render.resolution_y = 1600, 1200
    sc.view_settings.look = 'AgX - High Contrast'
elif SCENE == 'glb':
    product(on=False, cable='longo')
    for o in sc.objects:
        o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(ROOT, 'signa_conjunto.glb'), export_format='GLB',
                              use_selection=True, export_apply=True, export_yup=True)
    print('GLB OK')
    sys.exit(0)

sc.render.filepath = out
bpy.ops.render.render(write_still=True)
print('RENDER OK', out)
