"""Renders del domo: python3 scripts/domo-geodesico/render.py -- exterior interior estructura frente   (SPP=muestras)"""
import bpy, math, sys, os, time
from mathutils import Vector
from PIL import Image
AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get('DOMO_OUT', os.path.join(AQUI, '..', '..', 'output', 'domo-geodesico'))
bpy.ops.wm.open_mainfile(filepath=os.path.join(OUT, os.environ.get('DOMO_BLEND', 'domo-modelo.blend')))
sc = bpy.context.scene
OCULTAR = {
    'interior': ('lona_', 'ventanal_', 'ojo_de_buey', 'respiradero', 'terraza', 'chimenea_sombrero', 'chimenea_tapajuntas'),
    'estructura': ('lona_', 'ventanal_', 'ojo_de_buey', 'respiradero', 'vestibulo'),
}
VISTAS = {  # cámara, objetivo, lente, ancho, alto, ocultar
    'exterior':  ((-5.2, -12.2, 2.3), (0.5, 0.0, 1.75), 38, 1500, 1040, None),
    'interior':  ((0.0, -7.2, 9.6), (0.0, 0.1, 0.6), 34, 1200, 1200, 'interior'),
    'estructura':((-8.5, -9.5, 4.2), (0.0, 0.0, 1.7), 36, 1400, 1000, 'estructura'),
    'frente':    ((0.0, -15.0, 2.2), (0.0, 0.0, 1.9), 45, 1400, 900, None),
    'despiece':  ((-6.6, -14.4, 3.2), (0.4, 0.0, 2.0), 38, 1500, 1040, None),
}
def setup(v, spp):
    cam_loc, tgt, lens, w, h, hide = VISTAS[v]
    sc.frame_set(sc.frame_end if v == 'despiece' else 0)
    for o in [o for o in bpy.data.objects if o.type in ('CAMERA', 'LIGHT') or o.name == 'suelo']: bpy.data.objects.remove(o)
    for o in bpy.data.objects:
        if o.type == 'MESH': o.hide_render = bool(hide) and o.name.startswith(OCULTAR[hide])
    cam = bpy.data.cameras.new('cam'); cam.lens = lens; cam.clip_end = 200
    co = bpy.data.objects.new('cam', cam); sc.collection.objects.link(co); co.location = cam_loc
    co.rotation_euler = (Vector(tgt) - Vector(cam_loc)).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -0.66 if hide != 'interior' else -0.03)); fl = bpy.context.active_object; fl.name = 'suelo'; fl.is_shadow_catcher = True
    wd = bpy.data.worlds.new('w'); sc.world = wd; wd.use_nodes = True
    bg = wd.node_tree.nodes['Background']; bg.inputs['Color'].default_value = (.85, .87, .9, 1); bg.inputs['Strength'].default_value = 0.8
    sun = bpy.data.lights.new('sol', 'SUN'); sun.energy = 3.2; sun.angle = math.radians(3); sun.color = (1.0, 0.93, 0.82)
    so = bpy.data.objects.new('sol', sun); sc.collection.objects.link(so); so.rotation_euler = (math.radians(52), 0, math.radians(-35))
    L = bpy.data.lights.new('int', 'POINT'); L.energy = 250; L.color = (1, .85, .65); L.shadow_soft_size = 0.4
    lo = bpy.data.objects.new('int', L); sc.collection.objects.link(lo); lo.location = (0, -0.5, 2.6)
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = spp; sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = w, h; sc.render.film_transparent = True
    sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Base Contrast'; sc.view_settings.exposure = -0.2
def compose(path):
    im = Image.open(path).convert('RGBA'); w, h = im.size
    col = Image.new('RGBA', (1, h)); top, bot = (214, 222, 232), (244, 245, 247)
    for y in range(h):
        f = y / (h - 1); col.putpixel((0, y), tuple(int(top[i] + (bot[i] - top[i]) * f) for i in range(3)) + (255,))
    bg = col.resize((w, h)); bg.alpha_composite(im); bg.convert('RGB').save(path)
args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
for v in args:
    t0 = time.time(); setup(v, int(os.environ.get('SPP', 32)))
    sc.render.filepath = os.path.join(OUT, f'{v}.png'); bpy.ops.render.render(write_still=True); compose(sc.render.filepath)
    print(f'{v}: {time.time()-t0:.0f}s', flush=True)
