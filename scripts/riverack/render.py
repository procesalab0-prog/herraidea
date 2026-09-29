"""Renders de estudio del Riverack: python3 scripts/riverack/render.py <vista> [...]  (SPP=muestras, 36 por omisión).
La vista «estudio» reproduce la cámara calculada de la foto de estudio (content/source-documents/riverack/foto-estudio.png)."""
import bpy, math, sys, time
from mathutils import Vector
from PIL import Image

import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'output', 'riverack')
bpy.ops.wm.open_mainfile(filepath=os.path.join(OUT, 'riverack-modelo.blend'))
sc = bpy.context.scene

VISTAS = {  # cámara, objetivo, lente, ancho, alto
    'estudio':       ((1.539, -2.620, 0.996), (0.251, -0.590, 0.306), 44.9, 1536, 1024),
    'tres_cuartos':  ((-2.45, -2.35, 1.30), (0.0, 0.0, 0.29), 40, 1400, 1000),
    'trasera':       ((-5.2, 0.0, 0.33), (0.0, 0.0, 0.32), 70, 1400, 800),
    'lateral':       ((0.0, -5.2, 0.33), (0.0, 0.0, 0.32), 70, 1400, 800),
    'superior':      ((-1.6, -1.2, 2.6), (0.0, 0.0, 0.25), 38, 1400, 1000),
    'detalle_cabeza':((-0.25, -1.45, 1.00), (-0.68, -0.74, 0.60), 45, 1200, 900),
    'detalle_base':  ((1.15, -1.30, 0.34), (0.70, -0.84, 0.08), 45, 1200, 900),
}

def setup(v, samples):
    cam_loc, tgt, lens, w, h = VISTAS[v]
    for o in [o for o in bpy.data.objects if o.type in ('CAMERA', 'LIGHT') or o.name == 'suelo']:
        bpy.data.objects.remove(o)
    cam = bpy.data.cameras.new('cam'); cam.lens = lens; cam.clip_end = 60
    co = bpy.data.objects.new('cam', cam); sc.collection.objects.link(co); co.location = cam_loc
    co.rotation_euler = (Vector(tgt) - Vector(cam_loc)).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0)); fl = bpy.context.active_object; fl.name = 'suelo'; fl.is_shadow_catcher = True
    wd = bpy.data.worlds.new('w'); sc.world = wd; wd.use_nodes = True
    bg = wd.node_tree.nodes['Background']; bg.inputs['Color'].default_value = (.80, .82, .86, 1); bg.inputs['Strength'].default_value = 0.75
    def area(name, loc, energy, size, target):
        L = bpy.data.lights.new(name, 'AREA'); L.energy = energy; L.size = size
        o = bpy.data.objects.new(name, L); sc.collection.objects.link(o); o.location = loc
        o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    area('key', (-1.6, -2.2, 3.4), 900, 3.0, (0, 0, 0.2))
    area('fill', (2.6, -1.6, 1.8), 260, 3.0, (0, 0, 0.2))
    area('rim', (1.8, 2.4, 2.4), 420, 2.0, (0, 0, 0.3))
    area('top', (0.0, 0.0, 4.0), 300, 3.5, (0, 0, 0))
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = samples; sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.film_transparent = True
    sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Punchy'; sc.view_settings.exposure = -1.05

def compose(path):
    im = Image.open(path).convert('RGBA'); w, h = im.size
    bg = Image.new('RGBA', (w, h))
    top, bot = (222, 226, 232), (245, 246, 248)
    col = Image.new('RGBA', (1, h))
    for y in range(h):
        f = y / (h - 1); col.putpixel((0, y), tuple(int(top[i] + (bot[i] - top[i]) * f) for i in range(3)) + (255,))
    bg = col.resize((w, h)); bg.alpha_composite(im); bg.convert('RGB').save(path)

args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
for v in args:
    t0 = time.time(); setup(v, int(__import__('os').environ.get('SPP', 36)))
    sc.render.filepath = f'{OUT}/{v}.png'
    bpy.ops.render.render(write_still=True); compose(sc.render.filepath)
    print(f'{v}: {time.time()-t0:.0f}s', flush=True)
