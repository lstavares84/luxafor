"""Cena Blender (Cycles) do indicador rev A.

Uso:
  blender -b -P blender_cena.py -- <board.glb> <pasta_saida> [shot ...]
Shots: pcb_top pcb_bottom pcb_iso prod_hero prod_front prod_usb prod_monitor prod_states prod_exploded
Unidade de trabalho: 1 BU = 1 mm.
"""
import math
import sys

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
GLB, OUTDIR = argv[0], argv[1]
SHOTS = argv[2:] or ["pcb_top", "pcb_bottom", "pcb_iso", "prod_hero", "prod_front", "prod_usb",
                     "prod_monitor", "prod_states", "prod_exploded"]

PAPER = (0.93, 0.915, 0.885)
STATE = {"livre": (0.18, 0.82, 0.54), "processando": (0.24, 0.55, 1.0), "atencao": (1.0, 0.70, 0.12),
         "erro": (1.0, 0.25, 0.78), "reuniao": (1.0, 0.23, 0.18)}

BODY_W, BODY_D, BODY_H = 12.0, 15.0, 48.0
FLAG = dict(x0=5.3, x1=34.0, z0=27.0, z1=46.0, t=2.5)
CAP_H = 6.0
BOARD_FACE_X = 4.4
LIGHT_K = 300.0


def srgb(c):
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c)


# ------------------------------------------------------------------ cena base
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"
    sc.unit_settings.scale_length = 0.001
    sc.render.engine = "CYCLES"
    cy = sc.cycles
    import os as _os
    cy.samples = int(_os.environ.get('SAMPLES', '384'))
    cy.use_denoising = False
    cy.use_adaptive_sampling = True
    cy.adaptive_threshold = 0.005
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        for dev in ("OPTIX", "CUDA", "HIP"):
            try:
                prefs.compute_device_type = dev
                prefs.get_devices()
                if any(d.type == dev for d in prefs.devices):
                    for d in prefs.devices:
                        d.use = True
                    cy.device = "GPU"
                    break
            except TypeError:
                continue
    except Exception:
        pass
    sc.view_settings.view_transform = "Khronos PBR Neutral"
    sc.view_settings.look = "None"
    sc.render.film_transparent = False
    sc.world = bpy.data.worlds.new("W")
    sc.world.use_nodes = True
    return sc


def world(color, strength=1.0):
    bg = bpy.context.scene.world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (*srgb(color), 1)
    bg.inputs[1].default_value = strength


def mat(name, base, rough=0.5, metal=0.0, coat=0.0, emit=None, emit_s=0.0, trans=0.0, sss=0.0, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*srgb(base), 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    p.inputs["Coat Weight"].default_value = coat
    p.inputs["Transmission Weight"].default_value = trans
    p.inputs["Subsurface Weight"].default_value = sss
    p.inputs["Alpha"].default_value = alpha
    if emit:
        p.inputs["Emission Color"].default_value = (*srgb(emit), 1)
        p.inputs["Emission Strength"].default_value = emit_s
    return m


def flag_material(color, strength):
    """Policarbonato difusor aceso pela borda: emissão decai da raiz para a ponta."""
    m = bpy.data.materials.new("flag")
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    tint = color
    p.inputs["Base Color"].default_value = (*srgb(tint), 1)
    p.inputs["Roughness"].default_value = 0.35
    p.inputs["Subsurface Weight"].default_value = 0.2
    p.inputs["Coat Weight"].default_value = 0.25
    p.inputs["Emission Color"].default_value = (*srgb(color), 1)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = strength
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (1, 1, 1, 1)
    ramp.color_ramp.elements[1].position = 1.0
    ramp.color_ramp.elements[1].color = (0.35, 0.35, 0.35, 1)
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    nt.links.new(sep.outputs["X"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], mul.inputs[0])
    nt.links.new(mul.outputs[0], p.inputs["Emission Strength"])
    return m


def box(name, x0, y0, z0, x1, y1, z1, material, bevel=0.0, segs=6):
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.active_object
    o.name = name
    o.scale = (x1 - x0, y1 - y0, z1 - z0)
    o.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        b = o.modifiers.new("bevel", "BEVEL")
        b.width = bevel
        b.segments = segs
        b.limit_method = "ANGLE"
    o.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    return o


def cyl(name, r, h, loc, rot, material, verts=64):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=loc, rotation=rot, vertices=verts)
    o = bpy.context.active_object
    o.name = name
    o.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    return o


def cut(target, cutter):
    m = target.modifiers.new("cut", "BOOLEAN")
    m.operation = "DIFFERENCE"
    m.object = cutter
    cutter.hide_render = True
    cutter.hide_viewport = True


def area(name, loc, target, size, energy, color=(1, 1, 1)):
    bpy.ops.object.light_add(type="AREA", location=loc)
    L = bpy.context.active_object
    L.name = name
    L.data.size = size
    L.data.energy = energy * LIGHT_K   # distâncias em mm: a potência precisa de escala
    L.data.color = color
    d = Vector(target) - Vector(loc)
    L.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    return L


def camera(loc, target, lens=85, ortho=None, res=(2000, 2000)):
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.active_object
    d = Vector(target) - Vector(loc)
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    cam.data.clip_start = 0.5
    cam.data.clip_end = 20000
    if ortho:
        cam.data.type = "ORTHO"
        cam.data.ortho_scale = ortho
    else:
        cam.data.lens = lens
    sc = bpy.context.scene
    sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    return cam


def sweep(color, z=0.0, size=4000):
    """Fundo infinito (piso + parede curva)."""
    m = mat("sweep", color, rough=0.9)
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, z))
    fl = bpy.context.active_object
    fl.data.materials.append(m)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.object.mode_set(mode="OBJECT")
    # parede curva atrás
    bpy.ops.mesh.primitive_cylinder_add(radius=size / 4, depth=size, location=(0, size / 4, z + size / 4),
                                        rotation=(0, math.pi / 2, 0), vertices=128)
    wl = bpy.context.active_object
    wl.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    return m


def dark_studio(target, scale=1.0):
    world((0.02, 0.022, 0.028), 1.0)
    sweep((0.05, 0.052, 0.058))
    t = Vector(target)
    area("key", t + Vector((-120, -160, 90)) * scale, target, 140 * scale, 2600 * scale ** 2, (0.95, 0.96, 1.0))
    area("rimL", t + Vector((-110, 120, 140)) * scale, target, 30 * scale, 9000 * scale ** 2, (0.85, 0.9, 1.0))
    area("rimR", t + Vector((130, 110, 150)) * scale, target, 30 * scale, 8000 * scale ** 2, (0.85, 0.9, 1.0))
    area("top", t + Vector((0, 0, 220)) * scale, target, 160 * scale, 1200 * scale ** 2)


def soften(k):
    """Cenas claras: reduz as luzes de estúdio (o fundo claro já devolve muita luz)."""
    for o in bpy.context.scene.objects:
        if o.type == "LIGHT" and o.name.split(".")[0] in ("key", "fill", "rim"):
            o.data.energy *= k


def render(name):
    bpy.context.scene.render.filepath = f"{OUTDIR}/{name}.png"
    bpy.ops.render.render(write_still=True)
    print("RENDER OK", name)


# ------------------------------------------------------------------ placa
PCB_MATS = {}


def pcb_materials():
    PCB_MATS.update(
        mask=mat("mask", (0.035, 0.038, 0.045), rough=0.42, coat=0.25),
        gold=mat("enig", (0.93, 0.74, 0.42), rough=0.22, metal=1.0),
        silk=mat("silk", (0.93, 0.92, 0.88), rough=0.6),
        fr4=mat("fr4", (0.55, 0.50, 0.36), rough=0.7),
        epoxy=mat("epoxy", (0.06, 0.06, 0.065), rough=0.55),
        ceramic=mat("ceramic", (0.62, 0.52, 0.38), rough=0.45),
        tin=mat("tin", (0.80, 0.80, 0.80), rough=0.25, metal=1.0),
        steel=mat("steel", (0.78, 0.79, 0.80), rough=0.18, metal=1.0),
        ledbody=mat("ledbody", (0.93, 0.92, 0.88), rough=0.35),
        lens=mat("lens", (0.97, 0.96, 0.92), rough=0.15, trans=0.4, coat=0.5),
    )


def classify(m):
    """Reatribui materiais do GLB do KiCad pela cor original (o KiCad marca quase tudo como metálico)."""
    if not m or not m.use_nodes:
        return PCB_MATS["epoxy"]
    p = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if not p:
        return PCB_MATS["epoxy"]
    r, g, b, _ = p.inputs["Base Color"].default_value
    lum = (r + g + b) / 3
    if g > r * 1.25 and g > b * 1.1:                            # máscara verde -> preta fosca
        return PCB_MATS["mask"]
    if r > 0.5 and b < 0.1:                                     # cobre exposto -> ENIG
        return PCB_MATS["gold"]
    if r > 0.6 and 0.35 < g < 0.6 and b < 0.3:                  # corpo cerâmico
        return PCB_MATS["ceramic"]
    if lum < 0.16:                                              # epóxi, plásticos pretos
        return PCB_MATS["epoxy"]
    if lum > 0.95:                                              # serigrafia
        return PCB_MATS["silk"]
    if 0.35 < lum < 0.45 and r > b:                             # borda do FR-4
        return PCB_MATS["fr4"]
    if lum < 0.35:
        return PCB_MATS["epoxy"]
    return PCB_MATS["tin"]                                      # terminais, carcaça USB


def import_board():
    """Importa o GLB, normaliza para mm, centraliza e devolve o empty pai.
    Sistema local resultante: placa no plano XY, componentes em +Z, USB-C em -Y,
    origem no centro da placa e Z=0 na face de cima do FR-4."""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=GLB)
    objs = [o for o in bpy.data.objects if o not in before and o.type == "MESH"]
    for o in [o for o in bpy.data.objects if o not in before]:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    for o in objs:
        for i, sl in enumerate(o.material_slots):
            sl.material = classify(sl.material)
    # bbox global
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    span = max(mx - mn)
    k = 1000.0 if span < 1.0 else 1.0
    print("GLB bbox", mn, mx, "escala", k)
    bpy.ops.object.empty_add(location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = "BOARD"
    tops = [o for o in bpy.data.objects if o not in before and o.parent is None and o is not root]
    for o in tops:
        o.parent = root
    root.scale = (k, k, k)
    bpy.context.view_layer.update()
    # descobre eixos: comprimento da placa e lado do USB
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    ctr = (mn + mx) / 2
    print("bbox mm", mn, mx)
    # assume placa no XY (KiCad exporta Z para cima no Blender)
    for o in tops:
        o.location -= Vector((ctr.x / k, ctr.y / k, 0))
    bpy.context.view_layer.update()
    usb = [o for o in objs if "J1" in o.name or "USB" in o.name.upper()]
    longy = (mx.y - mn.y) > (mx.x - mn.x)
    print("usb objs", [o.name for o in usb][:5], "comprimento em Y", longy)
    if not longy:
        root.rotation_euler.z = math.pi / 2
        bpy.context.view_layer.update()
    if usb:
        uy = sum((o.matrix_world @ Vector(c)).y for o in usb for c in o.bound_box) / (8 * len(usb))
        if uy > 0:
            root.rotation_euler.z += math.pi
    bpy.context.view_layer.update()
    # Z=0 na face superior do FR-4 (placa de 0,8 mm; base do GLB = face inferior)
    masks = [o for o in objs if any(sl.material == PCB_MATS["mask"] for sl in o.material_slots)]
    top_z = max((o.matrix_world @ Vector(c)).z for o in masks for c in o.bound_box)
    root.location.z -= top_z
    bpy.context.view_layer.update()
    add_leds(root)
    return root


def add_leds(root):
    """SK6805-EC20 (não há STEP no KiCad): corpo branco + difusor."""
    for ky in (3.0, 10.0, 17.0):
        ly = 22.0 - ky
        b = box(f"LED_{ky}", -1, ly - 1, 0.035, 1, ly + 1, 0.5, PCB_MATS["ledbody"], bevel=0.04, segs=2)
        l = box(f"LENS_{ky}", -0.85, ly - 0.85, 0.5, 0.85, ly + 0.85, 0.65, PCB_MATS["lens"], bevel=0.05, segs=2)
        for o in (b, l):
            o.parent = root
            o.matrix_parent_inverse = root.matrix_world.inverted()


# ------------------------------------------------------------------ produto
def product(state="processando", strength=9.0, explode=0.0, with_board=False, name="P"):
    body_m = mat("pcabs", (0.11, 0.115, 0.125), rough=0.48, coat=0.15)
    parts = {}
    # corpo e tampa: inteiros com ranhura de junta; separados na vista explodida
    if explode:
        body = box(name + "_corpo", 0, -BODY_D / 2, CAP_H + 0.08, BODY_W, BODY_D / 2, BODY_H, body_m, bevel=0.9, segs=8)
        capm = box(name + "_tampa", 0, -BODY_D / 2, 0, BODY_W, BODY_D / 2, CAP_H, body_m, bevel=0.9, segs=8)
    else:
        body = box(name + "_corpo", 0, -BODY_D / 2, 0, BODY_W, BODY_D / 2, BODY_H, body_m, bevel=0.9, segs=8)
        capm = body
        ring = box(name + "_ring", -1, -BODY_D / 2 - 1, CAP_H - 0.09, BODY_W + 1, BODY_D / 2 + 1, CAP_H + 0.09, body_m)
        inner = box(name + "_ringin", 0.18, -BODY_D / 2 + 0.18, CAP_H - 1, BODY_W - 0.18, BODY_D / 2 - 0.18, CAP_H + 1, body_m)
        cut(ring, inner)
        ring.hide_viewport = False
        cut(body, ring)
    # rasgo da bandeira no corpo
    slot = box(name + "_slot", FLAG["x0"] - 0.2, -FLAG["t"] / 2 - 0.1, FLAG["z0"] - 0.1, BODY_W + 1,
               FLAG["t"] / 2 + 0.1, FLAG["z1"] + 0.1, body_m)
    cut(body, slot)
    # boca do USB-C na tampa
    ux = BOARD_FACE_X + 1.63
    usb_cut = box(name + "_usbcut", ux - 1.7, -4.6, -1, ux + 1.7, 4.6, 3.5, body_m, bevel=1.2, segs=6)
    cut(capm, usb_cut)
    # receptáculo visível pela boca
    steel = mat("steel_p", (0.78, 0.79, 0.80), rough=0.2, metal=1.0)
    shell = box(name + "_usbshell", ux - 1.6, -4.45, 0.55, ux + 1.6, 4.45, 5.5, steel, bevel=1.1, segs=6)
    tongue = box(name + "_usbtongue", ux - 0.35, -3.3, 0.9, ux + 0.35, 3.3, 5.0,
                 mat("tongue", (0.03, 0.03, 0.03), rough=0.5), bevel=0.2, segs=2)
    # recesso do ímã nas costas (-Y)
    mag = cyl(name + "_ima", 5.0, 1.5, (BODY_W / 2, BODY_D / 2 - 0.6, 30.0), (math.pi / 2, 0, 0),
              mat("ndfeb", (0.75, 0.76, 0.77), rough=0.3, metal=1.0))
    flag = box(name + "_bandeira", FLAG["x0"], -FLAG["t"] / 2, FLAG["z0"], FLAG["x1"], FLAG["t"] / 2, FLAG["z1"],
               flag_material(STATE[state], strength) if state else mat("pcoff", (0.92, 0.92, 0.9), rough=0.3, sss=0.5),
               bevel=0.6, segs=6)
    parts.update(corpo=body, tampa=capm, bandeira=flag, ima=mag, usb=shell, lingua=tongue)
    if state:
        # luz real que sai da bandeira (ilumina o entorno)
        bpy.ops.object.light_add(type="AREA", location=((FLAG["x0"] + FLAG["x1"]) / 2, 0, (FLAG["z0"] + FLAG["z1"]) / 2))
        L = bpy.context.active_object
        L.data.shape = "RECTANGLE"
        L.data.size, L.data.size_y = FLAG["x1"] - BODY_W, FLAG["z1"] - FLAG["z0"]
        L.rotation_euler = (math.pi / 2, 0, 0)
        L.data.energy = strength * 0.25 * LIGHT_K * 0.4
        L.data.color = STATE[state]
        parts["luz"] = L
    if explode:
        shell.hide_render = True      # o receptáculo real está na placa
        tongue.hide_render = True
        e = explode
        capm.location.z -= 1.4 * e if capm is not body else 0
        shell.location.z -= 0
        flag.location.x += 1.2 * e
        mag.location.y += 1.0 * e
        if "luz" in parts:
            parts["luz"].location.x += 1.2 * e
    return parts


def board_in_product(root, dx=0.0):
    """Placa em pé: componentes para +X (bandeira), USB-C para baixo."""
    root.rotation_euler = (math.pi / 2, 0, math.pi / 2)
    root.location = (BOARD_FACE_X + dx, 0, 2.0 + 22.0)
    bpy.context.view_layer.update()


# ------------------------------------------------------------------ shots
def shot_pcb(view):
    reset()
    pcb_materials()
    world(PAPER, 0.3)
    root = import_board()
    floor = sweep(PAPER, z=-0.8 - 0.01)
    if view == "bottom":
        root.rotation_euler.y = math.pi
        root.location.z = 0.0
    area("key", (-60, -40, 120), (0, 0, 0), 120, 16000)
    area("fill", (80, -20, 60), (0, 0, 0), 120, 5000)
    area("rim", (0, 90, 40), (0, 0, 0), 80, 2000)
    if view in ("top", "bottom"):
        soften(0.12)
        camera((0, 0, 300), (0, 0, 0), ortho=47.5, res=(900, 3150))
        bpy.context.scene.camera.rotation_euler.z = 0
    else:
        root.rotation_euler.z += math.radians(-28)
        soften(0.12)
        camera((-62, -78, 70), (0, 1, 0), lens=150, res=(2400, 2400))
    render(f"pcb_{view}")


def shot_hero():
    reset()
    pcb_materials()
    world(PAPER, 0.25)
    sweep(PAPER)
    product("processando", 5.0)
    area("key", (-120, -160, 200), (15, 0, 24), 160, 26000)
    area("fill", (160, -80, 80), (15, 0, 24), 160, 6000)
    area("rim", (40, 180, 120), (15, 0, 24), 120, 9000)
    soften(0.11)
    camera((-120, -215, 105), (15, 0, 23), lens=105, res=(2700, 2450))
    render("prod_hero")


def shot_front():
    reset()
    dark_studio((12, 0, 24))
    product("reuniao", 6.0)
    camera((40, -300, 40), (17, 0, 24), lens=135, res=(2000, 1650))
    render("prod_front")


def shot_usb():
    reset()
    world(PAPER, 0.25)
    sweep(PAPER)
    before = set(bpy.data.objects)
    product(None)
    bpy.ops.object.empty_add(location=(0, 0, 0))
    piv = bpy.context.active_object
    for o in bpy.data.objects:
        if o not in before and o is not piv and o.parent is None:
            o.parent = piv
    piv.rotation_euler = (math.radians(-90), 0, math.radians(-18))
    piv.location.z = BODY_D / 2
    area("key", (-100, -140, 160), (6, 10, 8), 140, 26000)
    area("fill", (140, -60, 50), (6, 10, 8), 120, 7000)
    area("rim", (0, 160, 80), (6, 10, 8), 100, 6000)
    soften(0.11)
    camera((-30, -120, 48), (4, 8, 6), lens=120, res=(2000, 1400))
    render("prod_usb")


def shot_monitor():
    reset()
    world((0.05, 0.05, 0.055), 1.0)
    desk = mat("desk", (0.30, 0.26, 0.22), rough=0.55)
    bpy.ops.mesh.primitive_plane_add(size=4000, location=(0, 0, -330))
    bpy.context.active_object.data.materials.append(desk)
    wall = mat("wall", (0.20, 0.20, 0.21), rough=0.9)
    bpy.ops.mesh.primitive_plane_add(size=4000, location=(0, 600, 0), rotation=(math.pi / 2, 0, 0))
    bpy.context.active_object.data.materials.append(wall)
    bezel = mat("bezel", (0.03, 0.03, 0.035), rough=0.35, coat=0.3)
    box("monitor", -620, -4, -300, 4, 6, 4, bezel, bevel=2.0, segs=4)
    scr = mat("screen", (0.0, 0.0, 0.0), rough=0.1, emit=(0.45, 0.55, 0.75), emit_s=0.35)
    box("tela", -612, -4.3, -292, -4, -3.9, -4, scr)
    before = set(bpy.data.objects)
    product("livre", 5.0)
    for o in bpy.data.objects:
        if o not in before and o.parent is None:
            o.location += Vector((-34, 2, 4))
    area("key", (-200, -300, 200), (-20, 0, 30), 200, 40000, (1.0, 0.92, 0.85))
    area("rimR", (110, 120, 90), (-20, 0, 30), 40, 30000, (0.85, 0.9, 1.0))
    area("top", (-20, -40, 260), (-20, 0, 30), 160, 12000)
    camera((-150, -230, 95), (-28, 0, 22), lens=50, res=(2200, 1200))
    render("prod_monitor")


def shot_states():
    reset()
    dark_studio((100, 0, 24), scale=2.2)
    keys = ["livre", "processando", "atencao", "erro", "reuniao"]
    for i, k in enumerate(keys):
        before = set(bpy.data.objects)
        product(k, 3.5 if k == "livre" else 6.0, name=f"S{i}")
        for o in bpy.data.objects:
            if o not in before and o.parent is None:
                o.location.x += i * 46
    camera((92, -520, 110), (100, 0, 22), lens=70, res=(2200, 1100))
    render("prod_states")


def shot_exploded():
    reset()
    pcb_materials()
    world(PAPER, 0.25)
    sweep(PAPER, z=-40)
    parts = product(None, explode=12.0)
    root = import_board()
    root.rotation_euler = (math.pi / 2, 0, 0)
    root.location = (-24.0, 0, 26.0)
    for o in parts.values():
        if o.type == "MESH":
            o.location.z += 0
    area("key", (-160, -180, 220), (10, 0, 20), 200, 30000)
    area("fill", (180, -80, 60), (10, 0, 20), 180, 8000)
    area("rim", (0, 200, 120), (10, 0, 20), 140, 9000)
    soften(0.11)
    camera((-30, -330, 70), (6, 0, 16), lens=100, res=(2000, 2700))
    render("prod_exploded")


DISPATCH = {
    "pcb_top": lambda: shot_pcb("top"), "pcb_bottom": lambda: shot_pcb("bottom"),
    "pcb_iso": lambda: shot_pcb("iso"), "prod_hero": shot_hero, "prod_front": shot_front,
    "prod_usb": shot_usb, "prod_monitor": shot_monitor, "prod_states": shot_states,
    "prod_exploded": shot_exploded,
}
for s in SHOTS:
    DISPATCH[s]()
