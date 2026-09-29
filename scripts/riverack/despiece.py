"""Riverack: toma output/riverack/riverack-modelo.blend y le agrega la animación «Despiece» por etapas (como los visores del sitio) y exporta assets/projects/riverack/riverack.glb (clip «Despiece»).

Etapas (fracción de la animación):
  1 tornillos salen por su eje · 2 travesaños suben · 3 fundas y cople se separan de los tubos interiores
  4 placas de cabeza y orejas se abren · 5 pieza superior sale del poste · 6 vigas se retiran · 7 bases bajan
"""
import bpy, math, os
from mathutils import Vector

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.normpath(os.path.join(AQUI, '..', '..'))
OUT = os.path.join(RAIZ, 'output', 'riverack'); os.makedirs(OUT, exist_ok=True)
GLB = os.path.join(RAIZ, 'assets', 'projects', 'riverack', 'riverack.glb')
bpy.ops.wm.open_mainfile(filepath=os.path.join(OUT, 'riverack-modelo.blend'))
sc = bpy.context.scene
LEAN = math.radians(11); S, C = math.sin(LEAN), math.cos(LEAN)
FRAMES, FPS = 120, 24

ETAPAS = {  # nombre: (inicio, fin)
    'tornillos': (0.00, 0.22), 'travesano': (0.14, 0.40), 'telescopio': (0.30, 0.52),
    'cabeza': (0.44, 0.64), 'superior': (0.54, 0.76), 'viga': (0.66, 0.88), 'base': (0.78, 1.00),
}
def ease(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)

obs = [o for o in bpy.data.collections['RACK'].objects if o.type == 'MESH']
piezas = [o for o in obs if not o.name.startswith('tornillo_')]
tornillos = [o for o in obs if o.name.startswith('tornillo_')]
dg = bpy.context.evaluated_depsgraph_get()

def signo(o):
    xs = -1 if 'trasero' in o.name else 1
    ys = -1 if 'izq' in o.name else 1
    return xs, ys

def movs(o):
    """Lista de (etapa, vector) de una pieza (no tornillo)."""
    n = o.name; m = []
    if n.startswith('travesano_'):
        m.append(('travesano', Vector((0, 0, 0.30))))
        if '_funda_' in n: m.append(('telescopio', Vector((0, 0.17 if n.endswith('der') else -0.17, 0))))
        if n.endswith('_cople'): m.append(('telescopio', Vector((0, 0, 0.09))))
        return m
    if n.startswith('viga_lateral_'):
        ys = -1 if n.endswith('izq') else 1
        m.append(('viga', Vector((0, ys * C, S)) * 0.30 + Vector((0, 0, -0.04))))
        return m
    xs, ys = signo(o)
    u = Vector((0, -ys * S, C))
    if '_superior' in n or '_cabeza_' in n or '_oreja_' in n:
        m.append(('superior', u * 0.24))
        if '_cabeza_' in n or '_oreja_' in n:
            # lado de la placa: a la izquierda o derecha del centro del poste en X
            cx = sum((o.matrix_world @ Vector(v)).x for v in o.bound_box) / 8
            sx = 1 if cx > xs * 0.735 else -1
            m.append(('cabeza', Vector((sx * (0.13 if '_oreja_' in n else 0.07), 0, 0))))
        return m
    if n.startswith('base_'):
        m.append(('base', Vector((0, 0, -0.11 if n.endswith('_collar') else -0.20))))
        return m
    return m                                                      # poste inferior: fijo

MOV = {o.name: movs(o) for o in piezas}
for b in tornillos:
    p = b.matrix_world.translation
    best, dmin = None, 1e9
    for o in piezas:
        ok, loc, nor, idx = o.evaluated_get(dg).closest_point_on_mesh(o.matrix_world.inverted() @ p)
        if ok:
            d = (o.matrix_world @ loc - p).length
            if d < dmin: best, dmin = o, d
    eje = (b.matrix_world.to_3x3() @ Vector((0, 0, 1))).normalized()
    MOV[b.name] = [('tornillos', eje * 0.075)] + list(MOV[best.name])

def pos(o, t):
    d = Vector()
    for et, v in MOV[o.name]:
        a, b = ETAPAS[et]; d += v * ease((t - a) / (b - a))
    return d

sc.name = 'Despiece'
sc.frame_start, sc.frame_end = 0, FRAMES; sc.render.fps = FPS
for o in obs:
    base = o.location.copy()
    if not any(v.length for _, v in MOV[o.name]): continue
    for f in range(FRAMES + 1):
        o.location = base + pos(o, f / FRAMES)
        o.keyframe_insert('location', frame=f)
    o.location = base
    for fc in o.animation_data.action.fcurves:
        for k in fc.keyframe_points: k.interpolation = 'LINEAR'
sc.frame_set(0)

bpy.ops.object.select_all(action='DESELECT')
for o in obs: o.select_set(True)
bpy.context.view_layer.objects.active = obs[0]
p = GLB
bpy.ops.export_scene.gltf(filepath=p, export_format='GLB', use_selection=True, export_apply=True, export_yup=True,
                          export_texcoords=False, export_cameras=False, export_lights=False,
                          export_animations=True, export_animation_mode='SCENE', export_force_sampling=True,
                          export_optimize_animation_size=True, export_anim_scene_split_object=False)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'riverack.blend'))
print(f'GLB: {len(obs)} piezas, {len(tornillos)} tornillos, {sum(1 for o in obs if o.animation_data)} animadas, {os.path.getsize(p)/1024:.0f} KB')
