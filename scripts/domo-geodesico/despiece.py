"""Domo geodésico: agrega la animación «Despiece» por etapas a out/domo-modelo.blend y exporta el GLB.

Uso: python3 scripts/domo-geodesico/despiece.py (después de modelo.py).
Etapas: 1 la lona se abre en pétalos (cada triángulo sale en dirección radial) · 2 salen los vidrios y marcos del
ventanal · 3 se retiran el vestíbulo y la chimenea · 4 la estructura se separa: los nodos se alejan más que los tubos
para dejar ver cada unión. La terraza y el mobiliario quedan fijos.
"""
import bpy, json, math, os
from mathutils import Vector
AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get('DOMO_OUT', os.path.join(AQUI, '..', '..', 'output', 'domo-geodesico'))
GLB = os.environ.get('DOMO_GLB', os.path.join(AQUI, '..', '..', 'assets', 'projects', 'domo-geodesico', 'domo-geodesico.glb'))
bpy.ops.wm.open_mainfile(filepath=os.path.join(OUT, 'domo-modelo.blend'))
meta = json.load(open(os.path.join(OUT, 'domo-meta.json')))
CEN = Vector(meta['CEN'])
sc = bpy.context.scene
FRAMES, FPS = 60, 24
ETAPAS = {'lona': (0.00, 0.34), 'ventanal': (0.12, 0.44), 'retiro': (0.26, 0.52), 'nodo': (0.46, 0.86), 'tubo': (0.50, 0.90)}
def ease(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
obs = [o for o in bpy.data.collections['DOMO'].objects if o.type == 'MESH']
def centro(o): return sum((o.matrix_world @ v.co for v in o.data.vertices), Vector()) / len(o.data.vertices)
def movs(o):
    n = o.name; c = centro(o); r = (c - CEN).normalized()
    if n.startswith(('lona_', 'ojo_de_buey', 'respiradero')): return [('lona', r * 1.45 + Vector((0, 0, 0.25)))]
    if n.startswith('ventanal_'): return [('ventanal', r * 1.2 + Vector((0, 0, 0.1)))]
    if n.startswith('vestibulo'):
        h = Vector((c.x, c.y, 0)).normalized(); return [('retiro', h * 1.6)]
    if n.startswith('chimenea'): return [('retiro', Vector((0, 0, 1.6)))]
    if n.startswith('estructura_nodo') or n.startswith('estructura_placa'):
        return [('nodo', (r if n.startswith('estructura_nodo_') and c.z > meta['PISO'] + 0.05 else Vector((c.x, c.y, 0)).normalized()) * 0.95)]
    if n.startswith('estructura_tubo'): return [('tubo', r * 0.62)]
    return []
MOV = {o.name: movs(o) for o in obs}
sc.name = 'Despiece'; sc.frame_start, sc.frame_end = 0, FRAMES; sc.render.fps = FPS
animadas = 0
for o in obs:
    if not MOV[o.name]: continue
    animadas += 1; base = o.location.copy()
    for f in range(FRAMES + 1):
        t = f / FRAMES; d = Vector()
        for et, v in MOV[o.name]:
            a, b = ETAPAS[et]; d += v * ease((t - a) / (b - a))
        o.location = base + d; o.keyframe_insert('location', frame=f)
    o.location = base
    for fc in o.animation_data.action.fcurves:
        for k in fc.keyframe_points: k.interpolation = 'LINEAR'
sc.frame_set(0)
bpy.ops.object.select_all(action='DESELECT')
for o in obs: o.select_set(True)
bpy.context.view_layer.objects.active = obs[0]
os.makedirs(os.path.dirname(GLB), exist_ok=True)
bpy.ops.export_scene.gltf(filepath=GLB, export_format='GLB', use_selection=True, export_apply=True, export_yup=True,
                          export_texcoords=False, export_cameras=False, export_lights=False,
                          export_animations=True, export_animation_mode='SCENE', export_anim_scene_split_object=False,
                          export_force_sampling=True, export_optimize_animation_size=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'domo-geodesico.blend'))
print(f'GLB: {len(obs)} piezas, {animadas} animadas, {os.path.getsize(GLB)/1024:.0f} KB')
