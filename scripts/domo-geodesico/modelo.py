"""Domo geodésico para glamping — modelo 3D (Blender / bpy).

Metros. X a lo ancho, Y hacia atrás (el ventanal mira a −Y), Z arriba; Z=0 es la cara superior de la terraza.
Geodésico icosaédrico 3V 5/8 (alto/ancho ≈ 0.60, como en la foto exterior), base de 15 nodos aplanada.
Estimado desde imágenes de referencia: no son medidas de fabricación.
Uso: python3 scripts/domo-geodesico/modelo.py  (bpy 4.5 o `blender -b -P`); luego despiece.py y armar_visor.py.
"""
import bpy, bmesh, math, os, sys, time
import numpy as np
from mathutils import Vector, Matrix

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from geo import geodesic
OUT = os.environ.get('DOMO_OUT', os.path.join(AQUI, '..', '..', 'output', 'domo-geodesico')); os.makedirs(OUT, exist_ok=True)
T0 = time.time()

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
COL = bpy.data.collections.new('DOMO'); sc.collection.children.link(COL)
AUX = bpy.data.collections.new('AUX'); sc.collection.children.link(AUX)

# ------------------------------------------------------------------ parámetros
R = 3.55                        # radio de la esfera geodésica (ejes de tubos)
PISO = 0.12                     # alto de la plataforma redonda sobre la terraza
ZB_UNIT = -0.1716               # corte 5/8 (anillo base de 15 nodos)
ZC = PISO - ZB_UNIT * R         # altura del centro de la esfera
TUBO = 0.021                    # radio del tubo de la estructura
LONA = 0.045                    # separación de la lona por fuera del eje de los tubos
AZ_VENT = 52                    # medio ancho angular del ventanal (grados)

# ------------------------------------------------------------------ materiales
def mat(name, color, metal=0.0, rough=0.6, alpha=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1); b.inputs['Metallic'].default_value = metal
    b.inputs['Roughness'].default_value = rough
    if alpha < 1:
        b.inputs['Alpha'].default_value = alpha
        m.blend_method = 'BLEND' if hasattr(m, 'blend_method') else None
        try: m.surface_render_method = 'BLENDED'
        except Exception: pass
    return m
M = dict(
    lona=mat('Lona_PVC_blanca', (0.86, 0.86, 0.84), 0.0, 0.62),
    acero=mat('Acero_pintado_blanco', (0.88, 0.89, 0.90), 0.35, 0.33),
    marco=mat('Marco_ventanal_grafito', (0.07, 0.075, 0.08), 0.5, 0.4),
    vidrio=mat('Vidrio_claro', (0.10, 0.12, 0.13), 0.0, 0.04, alpha=0.28),
    gris=mat('Lona_gris_vestibulo', (0.52, 0.54, 0.56), 0.0, 0.65),
    negro=mat('Acero_negro_estufa', (0.025, 0.025, 0.028), 0.6, 0.45),
    terraza=mat('Madera_terraza', (0.42, 0.25, 0.13), 0.0, 0.55),
    terraza_osc=mat('Madera_terraza_estructura', (0.25, 0.14, 0.07), 0.0, 0.6),
    piso=mat('Madera_piso_claro', (0.80, 0.66, 0.48), 0.0, 0.5),
    triplay=mat('Triplay_abedul', (0.86, 0.72, 0.52), 0.0, 0.55),
    tronco=mat('Tronco_natural', (0.62, 0.45, 0.28), 0.0, 0.7),
    blanco=mat('Textil_blanco', (0.90, 0.90, 0.88), 0.0, 0.9),
    grafito=mat('Textil_grafito', (0.18, 0.19, 0.20), 0.0, 0.95),
    petroleo=mat('Textil_verde_petroleo', (0.03, 0.26, 0.24), 0.0, 0.95),
    tapete=mat('Tapete_aqua', (0.40, 0.66, 0.66), 0.0, 1.0),
    amarillo=mat('Tapiz_amarillo', (0.95, 0.74, 0.12), 0.0, 0.85),
    hoja=mat('Follaje', (0.10, 0.32, 0.08), 0.0, 0.8),
    maceta=mat('Maceta_blanca', (0.93, 0.93, 0.91), 0.0, 0.5),
    musgo=mat('Musgo_preservado', (0.35, 0.16, 0.08), 0.0, 1.0),
    lampara=mat('Lampara_negra', (0.02, 0.02, 0.02), 0.8, 0.3),
    mimbre=mat('Mimbre', (0.55, 0.40, 0.25), 0.0, 0.8),
)

# ------------------------------------------------------------------ utilidades
def from_bm(name, bm, material, coll=None):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); (coll or COL).objects.link(ob)
    me.materials.append(material)
    return ob

def eval_mesh(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    old = ob.data; ob.modifiers.clear(); ob.data = me
    if old.users == 0: bpy.data.meshes.remove(old)

def bevel(ob, w=0.004, seg=2, ang=40):
    b = ob.modifiers.new('b', 'BEVEL'); b.width = w; b.segments = seg; b.limit_method = 'ANGLE'; b.angle_limit = math.radians(ang)
    eval_mesh(ob)

def smooth(ob, ang=35):
    with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob]):
        bpy.ops.object.shade_smooth_by_angle(angle=math.radians(ang))

def caja(name, c, s, material, rot=0.0, b=0.006, seg=2):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], v.co.z * s[2]))
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(rot, 3, 'Z'))
    bmesh.ops.translate(bm, verts=bm.verts, vec=Vector(c))
    ob = from_bm(name, bm, material)
    if b: bevel(ob, b, seg)
    return ob

def cilindro(name, c, r, h, material, seg=32, r2=None, b=0.004, eje=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=h)
    if eje is not None:
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Vector((0, 0, 1)).rotation_difference(Vector(eje)).to_matrix())
    bmesh.ops.translate(bm, verts=bm.verts, vec=Vector(c))
    ob = from_bm(name, bm, material)
    if b: bevel(ob, b, 2)
    return ob

def barra(name, a, b_, r, material, seg=12):
    a, b_ = Vector(a), Vector(b_)
    return cilindro(name, (a + b_) / 2, r, (b_ - a).length, material, seg, b=0, eje=b_ - a)

def esfera(name, c, r, material, sub=2, esc=(1, 1, 1)):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * esc[0], v.co.y * esc[1], v.co.z * esc[2])) + Vector(c)
    ob = from_bm(name, bm, material); smooth(ob, 60)
    return ob

def prisma(name, poly, z0, z1, material, b=0.004):
    bm = bmesh.new()
    v0 = [bm.verts.new((x, y, z0)) for x, y in poly]; v1 = [bm.verts.new((x, y, z1)) for x, y in poly]
    n = len(poly); bm.faces.new(v0[::-1]); bm.faces.new(v1)
    for i in range(n): bm.faces.new((v0[i], v0[(i + 1) % n], v1[(i + 1) % n], v1[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = from_bm(name, bm, material)
    if b: bevel(ob, b, 2)
    return ob

def cojin(name, c, s, material, rot=0.0, tilt=0.0):
    """Cojín / colchón: caja subdividida y redondeada."""
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=3, use_grid_fill=True)
    for v in bm.verts:
        p = v.co * 2                                       # −1..1
        q = Vector((p.x, p.y, p.z)); k = q.length
        q = q.lerp(q.normalized() * 1.2, 0.35) if k else q
        v.co = Vector((q.x * s[0] / 2, q.y * s[1] / 2, q.z * s[2] / 2))
    m = Matrix.Rotation(rot, 3, 'Z') @ Matrix.Rotation(tilt, 3, 'X')
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=m)
    bmesh.ops.translate(bm, verts=bm.verts, vec=Vector(c))
    ob = from_bm(name, bm, material)
    s_ = ob.modifiers.new('s', 'SUBSURF'); s_.levels = 1; eval_mesh(ob); smooth(ob, 60)
    return ob

def unir(name, obs):
    """Une varios objetos del mismo material en uno."""
    with bpy.context.temp_override(active_object=obs[0], selected_editable_objects=obs, selected_objects=obs):
        bpy.ops.object.join()
    obs[0].name = name; obs[0].data.name = name
    return obs[0]

# ------------------------------------------------------------------ geodésico 3V 5/8
P, F = geodesic(3)
P = np.array(P)
keep_v = P[:, 2] >= -0.19
idx_map = {}
V = []                                                        # nodos en el mundo
for i, p in enumerate(P):
    if not keep_v[i]: continue
    q = p.copy()
    if q[2] < -0.15: q[2] = ZB_UNIT                            # aplana el anillo base (15 nodos)
    idx_map[i] = len(V); V.append(Vector((q[0] * R, q[1] * R, q[2] * R + ZC)))
FACES = [tuple(idx_map[i] for i in f) for f in F if all(keep_v[i] for i in f)]
EDGES = sorted({tuple(sorted((f[a], f[(a + 1) % 3]))) for f in FACES for a in range(3)})
CEN = Vector((0, 0, ZC))
BASE = [i for i, v in enumerate(V) if abs(v.z - PISO) < 1e-6]
RB = max((V[i] - Vector((0, 0, PISO))).length for i in BASE)
print(f'domo 3V 5/8: {len(V)} nodos, {len(EDGES)} tubos, {len(FACES)} triángulos, base {len(BASE)} nodos, '
      f'diámetro base {2*RB:.2f} m, altura {ZC + R:.2f} m')

def az(p):                    # 0° = frente (−Y), +90° = derecha (+X)
    return math.degrees(math.atan2(p.x, -p.y))
def centro(f): return sum((V[i] for i in f), Vector()) / 3
def radial(p, k): return CEN + (p - CEN) * k

z_cara = lambda f: max(V[i].z for i in f)
VENTANAL = {fi for fi, f in enumerate(FACES) if z_cara(f) <= ZC + 0.52 * R and abs(az(centro(f))) <= AZ_VENT}

def cara_en(dirv):
    """Cara cuyo triángulo esférico contiene la dirección; devuelve (índice, punto sobre su plano, normal)."""
    d = Vector(dirv).normalized()
    for fi, f in enumerate(FACES):
        a, b, c = (V[i] - CEN for i in f)
        n = (b - a).cross(c - a).normalized()
        if n.dot(a) < 0: n = -n
        den = n.dot(d)
        if den <= 0: continue
        t = n.dot(a) / den; p = d * t
        ok = all(((y - x).cross(p - x)).dot(n) >= -1e-9 for x, y in ((a, b), (b, c), (c, a)))
        if ok: return fi, CEN + p, n
    raise ValueError('sin cara')

def dir_az(azg, z_unit):
    s = math.sqrt(max(0, 1 - z_unit ** 2)); a = math.radians(azg)
    return Vector((math.sin(a) * s, -math.cos(a) * s, z_unit))

# ------------------------------------------------------------------ estructura: tubos y nodos
RED = {}                                                      # nombre -> datos para el despiece
def reg(ob, grupo, **k): RED[ob.name] = dict(grupo=grupo, **k); return ob

for n_, (i, j) in enumerate(EDGES):
    a, b = V[i], V[j]; d = (b - a).normalized()
    ob = barra(f'estructura_tubo_{n_:03d}', a + d * 0.05, b - d * 0.05, TUBO, M['acero'])
    smooth(ob, 50); reg(ob, 'tubo', centro=tuple((a + b) / 2))
for i, v in enumerate(V):
    nrm = (v - CEN).normalized()
    if i in BASE: nrm = Vector((0, 0, 1))
    ob = cilindro(f'estructura_nodo_{i:02d}', v, 0.062, 0.026, M['acero'], 24, b=0.004, eje=nrm)
    smooth(ob, 40); reg(ob, 'nodo', centro=tuple(v))
    if i in BASE:
        ob = caja(f'estructura_placa_base_{i:02d}', (v.x, v.y, PISO + 0.004), (0.20, 0.20, 0.008), M['acero'],
                  rot=math.atan2(v.y, v.x), b=0.002)
        reg(ob, 'placa')

# ------------------------------------------------------------------ lona (un panel por triángulo) y ventanal
def tri_panel(name, f, k, grosor, material, inset=0.0):
    pts = [radial(V[i], k) for i in f]
    if inset:
        c = sum(pts, Vector()) / 3
        pts = [c + (p - c) * (1 - inset / max(0.01, (p - c).length)) for p in pts]
    c = sum(pts, Vector()) / 3
    n = (pts[1] - pts[0]).cross(pts[2] - pts[0]).normalized()
    if n.dot(c - CEN) < 0: n = -n
    bm = bmesh.new()
    v0 = [bm.verts.new(p) for p in pts]; v1 = [bm.verts.new(p + n * grosor) for p in pts]
    bm.faces.new(v0[::-1]); bm.faces.new(v1)
    for a in range(3): bm.faces.new((v0[a], v0[(a + 1) % 3], v1[(a + 1) % 3], v1[a]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return from_bm(name, bm, material)

KL = (R + LONA) / R
for fi, f in enumerate(FACES):
    c = centro(f)
    if fi in VENTANAL:
        g = tri_panel(f'ventanal_vidrio_{fi:03d}', f, (R + 0.030) / R, 0.008, M['vidrio'], inset=0.03)
        reg(g, 'ventanal', cara=fi)
        # marco perimetral del triángulo (perfil oscuro)
        pts = [radial(V[i], (R + 0.034) / R) for i in f]
        for a in range(3):
            p, q = pts[a], pts[(a + 1) % 3]
            ob = caja(f'ventanal_marco_{fi:03d}_{a}', (p + q) / 2, ((q - p).length - 0.02, 0.05, 0.045), M['marco'], b=0.003)
            # orientar la caja a lo largo del borde, con el ancho sobre la superficie
            nrm = ((p + q) / 2 - CEN).normalized(); x = (q - p).normalized(); y = nrm.cross(x)
            ob.data.transform(Matrix.Translation(-(p + q) / 2))
            ob.data.transform(Matrix((x, y, nrm)).transposed().to_4x4())
            ob.data.transform(Matrix.Translation((p + q) / 2))
            reg(ob, 'ventanal', cara=fi)
    else:
        ob = tri_panel(f'lona_panel_{fi:03d}', f, KL, 0.004, M['lona'])
        bevel(ob, 0.006, 2, 30)
        reg(ob, 'lona', cara=fi)

# ojo de buey (ventana redonda) y respiraderos
def disco_en(name, dirv, diam, prof, material, sobre=0.0, anillo=None):
    fi, p, n = cara_en(dirv)
    p = CEN + (p - CEN) * KL + n * (0.004 + sobre)
    if anillo:
        bm = bmesh.new()
        bmesh.ops.create_circle(bm, cap_ends=False, segments=40, radius=diam / 2)
        bmesh.ops.create_circle(bm, cap_ends=False, segments=40, radius=diam / 2 - anillo)
        ob = None
        # anillo: cono hueco simple = dos cilindros restados
        big = cilindro(name, p, diam / 2, prof, material, 40, b=0, eje=n)
        small = cilindro('hueco', p, diam / 2 - anillo, prof * 3, material, 40, b=0, eje=n)
        bo = big.modifiers.new('c', 'BOOLEAN'); bo.operation = 'DIFFERENCE'; bo.object = small; bo.solver = 'EXACT'
        eval_mesh(big); bpy.data.objects.remove(small); bevel(big, 0.003, 2)
        bm.free(); return big, fi, p, n
    ob = cilindro(name, p, diam / 2, prof, material, 32, b=0.003, eje=n)
    return ob, fi, p, n

d_ojo = dir_az(-66, 0.52)
ring, fi_ojo, p_ojo, n_ojo = disco_en('ojo_de_buey_marco', d_ojo, 0.66, 0.05, M['marco'], anillo=0.06)
reg(ring, 'lona', cara=fi_ojo)
g = cilindro('ojo_de_buey_vidrio', p_ojo - n_ojo * 0.006, 0.28, 0.008, M['vidrio'], 40, b=0, eje=n_ojo); reg(g, 'lona', cara=fi_ojo)
# hueco en el panel de lona del ojo de buey
lona_ojo = bpy.data.objects[f'lona_panel_{fi_ojo:03d}']
h = cilindro('hueco', p_ojo, 0.29, 0.4, M['lona'], 40, b=0, eje=n_ojo)
bo = lona_ojo.modifiers.new('c', 'BOOLEAN'); bo.operation = 'DIFFERENCE'; bo.object = h; bo.solver = 'EXACT'
eval_mesh(lona_ojo); bpy.data.objects.remove(h)
for k, a in enumerate((-9, 9)):
    ob, fi, p, n = disco_en(f'respiradero_{k}', dir_az(a, 0.90), 0.13, 0.035, M['marco'], sobre=0.012)
    reg(ob, 'lona', cara=fi)

# ------------------------------------------------------------------ vestíbulo de acceso (lona gris)
AZ_PUERTA = -112
a = math.radians(AZ_PUERTA); dirh = Vector((math.sin(a), -math.cos(a), 0)); lat = Vector((0, 0, 1)).cross(dirh)
def perfil_arco(w, h, n=14):
    pts = [(-w / 2, 0.0)]
    for k in range(n + 1):
        t = math.pi * k / n
        pts.append((-w / 2 * math.cos(t), h - 0.45 + 0.45 * math.sin(t)))
    pts.append((w / 2, 0.0))
    return pts
W_V, H_V, D0, D1 = 1.25, 2.15, RB - 0.55, RB + 0.95
bm = bmesh.new()
pr = perfil_arco(W_V, H_V)
def P3(u, zz, d): return Vector((0, 0, PISO)) + dirh * d + lat * u + Vector((0, 0, zz))
v0 = [bm.verts.new(P3(u, zz, D0)) for u, zz in pr]; v1 = [bm.verts.new(P3(u, zz, D1)) for u, zz in pr]
for i in range(len(pr) - 1): bm.faces.new((v0[i], v0[i + 1], v1[i + 1], v1[i]))
bm.faces.new(v1[::-1])
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
vest = from_bm('vestibulo_lona', bm, M['gris'])
s_ = vest.modifiers.new('s', 'SOLIDIFY'); s_.thickness = 0.006; eval_mesh(vest); bevel(vest, 0.01, 2); smooth(vest, 40)
reg(vest, 'vestibulo', dir=tuple(dirh))
# cierre de la puerta (línea en U) sobre la cara frontal
cu = bpy.data.curves.new('cierre', 'CURVE'); cu.dimensions = '3D'
sp = cu.splines.new('POLY'); pts = [P3(-0.36, 0.08, D1 + 0.008), P3(-0.36, 1.55, D1 + 0.008)]
for k in range(9):
    t = math.pi * k / 8; pts.append(P3(-0.36 * math.cos(t), 1.55 + 0.36 * math.sin(t), D1 + 0.008))
pts.append(P3(0.36, 0.08, D1 + 0.008))
sp.points.add(len(pts) - 1)
for pt, p in zip(sp.points, pts): pt.co = (*p, 1)
cu.bevel_depth = 0.008; cu.bevel_resolution = 2; cu.use_fill_caps = True
tmp = bpy.data.objects.new('cierre', cu); AUX.objects.link(tmp); bpy.context.view_layer.update()
me = bpy.data.meshes.new_from_object(tmp.evaluated_get(bpy.context.evaluated_depsgraph_get())); bpy.data.objects.remove(tmp)
me.materials.append(M['marco']); ob = bpy.data.objects.new('vestibulo_cierre', me); COL.objects.link(ob)
reg(ob, 'vestibulo', dir=tuple(dirh))

# ------------------------------------------------------------------ plataforma redonda y terraza
n15 = sorted(BASE, key=lambda i: math.atan2(V[i].y, V[i].x))
poly = [(V[i].x * (RB + 0.22) / RB, V[i].y * (RB + 0.22) / RB) for i in n15]
reg(prisma('piso_domo', poly, PISO - 0.035, PISO, M['piso'], b=0.004), 'fijo')
reg(prisma('piso_domo_canto', [(x * 1.004, y * 1.004) for x, y in poly], 0.0, PISO - 0.035, M['terraza_osc'], b=0.004), 'fijo')

TX, TY0, TY1 = 5.6, -6.9, 4.4                                 # terraza: x ±TX, y de TY0 a TY1
bm = bmesh.new(); y = TY0
while y < TY1 - 0.01:
    w = min(0.14, TY1 - y)
    bmesh.ops.create_cube(bm, size=1, matrix=Matrix.Translation((0, y + w / 2, -0.016)) @ Matrix.Diagonal((2 * TX, w - 0.007, 0.032, 1)))
    y += 0.146
tab = from_bm('terraza_tablas', bm, M['terraza']); bevel(tab, 0.0025, 1); reg(tab, 'fijo')
bm = bmesh.new()
for (cx, cy, sx, sy) in ((0, TY0 + 0.03, 2 * TX, 0.06), (0, TY1 - 0.03, 2 * TX, 0.06), (-TX + 0.03, (TY0 + TY1) / 2, 0.06, TY1 - TY0), (TX - 0.03, (TY0 + TY1) / 2, 0.06, TY1 - TY0)):
    bmesh.ops.create_cube(bm, size=1, matrix=Matrix.Translation((cx, cy, -0.032 - 0.11)) @ Matrix.Diagonal((sx, sy, 0.22, 1)))
for x in np.linspace(-TX + 0.25, TX - 0.25, 5):
    for y in np.linspace(TY0 + 0.25, TY1 - 0.25, 5):
        bmesh.ops.create_cube(bm, size=1, matrix=Matrix.Translation((x, y, -0.032 - 0.33)) @ Matrix.Diagonal((0.14, 0.14, 0.66, 1)))
est = from_bm('terraza_estructura', bm, M['terraza_osc']); bevel(est, 0.004, 1); reg(est, 'fijo')

# ------------------------------------------------------------------ interior (según el render de referencia)
Z = PISO
def mueble(ob): return reg(ob, 'mueble')
# tapetes redondos
for k, (x, y, r) in enumerate(((1.05, -1.75, 0.78), (-1.45, -0.35, 0.62))):
    mueble(cilindro(f'tapete_{k}', (x, y, Z + 0.006), r, 0.012, M['tapete'], 48, b=0.003))
# tapanco de triplay con escalera y repisas
LX, LY, LW, LD, LH = -0.75, 1.30, 2.30, 1.85, 1.95
tap = []
for sx in (-1, 1):
    for sy in (-1, 1):
        tap.append(caja('p', (LX + sx * (LW / 2 - 0.045), LY + sy * (LD / 2 - 0.045), Z + LH / 2), (0.09, 0.09, LH), M['triplay'], b=0.004))
tap.append(caja('p', (LX, LY, Z + LH + 0.03), (LW, LD, 0.06), M['triplay'], b=0.005))
tap.append(caja('p', (LX, LY - LD / 2 + 0.03, Z + 0.95), (LW - 0.18, 0.03, 1.55), M['triplay'], b=0.004))     # muro cabecero
tap.append(caja('p', (LX, LY - LD / 2 + 0.03, Z + LH + 0.26), (LW, 0.03, 0.40), M['triplay'], b=0.004))       # barandal frontal
tap.append(caja('p', (LX + LW / 2 - 0.03, LY, Z + LH + 0.26), (0.03, LD, 0.40), M['triplay'], b=0.004))       # barandal lateral
for zz in (0.35, 0.75, 1.15, 1.55):                                                                             # repisas
    tap.append(caja('p', (LX + LW / 2 + 0.16, LY - 0.35, Z + zz), (0.30, 0.55, 0.025), M['triplay'], b=0.003))
tap.append(caja('p', (LX + LW / 2 + 0.305, LY - 0.35, Z + 0.9), (0.02, 0.55, 1.75), M['triplay'], b=0.003))
xl = LX - LW / 2 - 0.20                                                                                         # escalera
for sy in (-0.24, 0.24): tap.append(caja('p', (xl, LY - 0.2 + sy, Z + (LH + 0.4) / 2), (0.05, 0.07, LH + 0.4), M['triplay'], b=0.003))
for k in range(7): tap.append(caja('p', (xl, LY - 0.2, Z + 0.28 + k * 0.30), (0.05, 0.48, 0.05), M['triplay'], b=0.003))
mueble(unir('tapanco', tap))
mueble(cojin('tapanco_colchon', (LX - 0.05, LY + 0.02, Z + LH + 0.17), (LW - 0.25, LD - 0.15, 0.20), M['blanco']))
mueble(cojin('tapanco_edredon', (LX - 0.05, LY - 0.05, Z + LH + 0.285), (LW - 0.20, LD - 0.40, 0.06), M['grafito']))
for k, dx in enumerate((-0.42, 0.30)):
    mueble(cojin(f'tapanco_almohada_{k}', (LX + dx, LY + LD / 2 - 0.35, Z + LH + 0.36), (0.62, 0.36, 0.16), M['blanco'], tilt=-0.25))
mueble(cilindro('tapanco_musgo', (LX + 0.05, LY - LD / 2 - 0.004, Z + 1.35), 0.36, 0.04, M['musgo'], 36, b=0.01, eje=(0, 1, 0)))
# cama matrimonial frente al tapanco
BX, BY = LX + 0.05, LY - LD / 2 - 1.08
mueble(caja('cama_base', (BX, BY, Z + 0.17), (1.70, 2.10, 0.30), M['triplay'], b=0.01))
mueble(cojin('cama_colchon', (BX, BY, Z + 0.43), (1.62, 2.02, 0.24), M['blanco']))
mueble(cojin('cama_edredon', (BX, BY - 0.18, Z + 0.57), (1.74, 1.62, 0.08), M['grafito']))
mueble(cojin('cama_cobija', (BX + 0.12, BY - 0.35, Z + 0.62), (1.30, 0.80, 0.05), M['petroleo'], rot=0.35))
mueble(cojin('cama_manta', (BX - 0.45, BY - 0.62, Z + 0.63), (0.85, 0.55, 0.05), M['petroleo'], rot=-0.2))
for k, (dx, m_, rot) in enumerate(((-0.45, 'blanco', 0.05), (0.40, 'blanco', -0.05), (-0.20, 'grafito', 0.2), (0.20, 'petroleo', -0.15))):
    mueble(cojin(f'cama_cojin_{k}', (BX + dx, BY + 0.80 - (0.12 if k > 1 else 0), Z + 0.70 - (0.03 if k > 1 else 0)), (0.58 if k < 2 else 0.42, 0.18, 0.42 if k < 2 else 0.34), M[m_], rot=rot, tilt=0.35))
mueble(esfera('cama_cojin_redondo', (BX + 0.05, BY + 0.45, Z + 0.72), 0.17, M['grafito'], esc=(1, 1, 0.6)))
# burós de tronco con lámpara
for k, sx in enumerate((-1, 1)):
    mueble(cilindro(f'buro_{k}', (BX + sx * 1.12, BY + 0.85, Z + 0.24), 0.21, 0.48, M['tronco'], 28, b=0.02))
mueble(cilindro('buro_lampara_base', (BX + 1.12, BY + 0.85, Z + 0.58), 0.05, 0.20, M['blanco'], 20))
mueble(cilindro('buro_lampara_pantalla', (BX + 1.12, BY + 0.85, Z + 0.75), 0.13, 0.16, M['blanco'], 28, r2=0.10))
# lámpara colgante hexagonal sobre la cama
hexa = []
for k in range(6):
    a0, a1 = k * math.pi / 3, (k + 1) * math.pi / 3
    for zz in (2.15, 2.45):
        hexa.append(barra('h', (BX + 0.38 * math.cos(a0), BY + 0.2 + 0.38 * math.sin(a0), Z + zz), (BX + 0.38 * math.cos(a1), BY + 0.2 + 0.38 * math.sin(a1), Z + zz), 0.008, M['lampara'], 8))
    hexa.append(barra('h', (BX + 0.38 * math.cos(a0), BY + 0.2 + 0.38 * math.sin(a0), Z + 2.15), (BX + 0.38 * math.cos(a0), BY + 0.2 + 0.38 * math.sin(a0), Z + 2.45), 0.008, M['lampara'], 8))
hexa.append(barra('h', (BX, BY + 0.2, Z + 2.45), (BX, BY + 0.2, ZC + R - 0.10), 0.004, M['lampara'], 6))
mueble(unir('lampara_colgante', hexa))
# estufa de leña con chimenea que sale por la lona
SX, SY = -1.55, -1.55
mueble(prisma('estufa_placa_piso', [(SX + 0.62 * math.cos(t) * 1.0, SY + 0.42 * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 48, endpoint=False)], Z, Z + 0.008, M['negro'], b=0.002))
est_parts = [cilindro('e', (SX, SY, Z + 0.42), 0.24, 0.62, M['negro'], 40, b=0.01)]
for k in range(3):
    a = k * 2 * math.pi / 3 + 0.3
    est_parts.append(barra('e', (SX + 0.17 * math.cos(a), SY + 0.17 * math.sin(a), Z + 0.12), (SX + 0.2 * math.cos(a), SY + 0.2 * math.sin(a), Z + 0.008), 0.018, M['negro'], 10))
est_parts.append(cilindro('e', (SX + 0.0, SY - 0.235, Z + 0.45), 0.13, 0.02, M['marco'], 32, b=0.003, eje=(0, 1, 0)))
mueble(unir('estufa', est_parts))
r_ch = math.hypot(SX, SY); z_sal = ZC + math.sqrt((R + LONA) ** 2 - r_ch ** 2)
ch = barra('chimenea_tubo', (SX, SY, Z + 0.73), (SX, SY, z_sal + 0.75), 0.075, M['negro'], 24); smooth(ch, 40)
reg(ch, 'chimenea')
reg(cilindro('chimenea_sombrero', (SX, SY, z_sal + 0.84), 0.20, 0.10, M['negro'], 28, r2=0.05, b=0.004), 'chimenea')
reg(cilindro('chimenea_tapajuntas', (SX, SY, z_sal + 0.02), 0.19, 0.10, M['marco'], 28, r2=0.09, b=0.004), 'chimenea')
lena = [caja('l', (SX + 0.30, SY - 0.55, Z + 0.20), (0.36, 0.30, 0.02), M['negro'], b=0.002)]
for sx in (-1, 1): lena.append(caja('l', (SX + 0.30 + sx * 0.18, SY - 0.55, Z + 0.20), (0.02, 0.30, 0.40), M['negro'], b=0.002))
for k in range(9):
    lena.append(cilindro('l', (SX + 0.17 + (k % 3) * 0.13 + (0.06 if (k // 3) % 2 else 0), SY - 0.55, Z + 0.28 + (k // 3) * 0.105), 0.05, 0.30, M['tronco'], 12, b=0.008, eje=(0, 1, 0)))
mueble(unir('lenero', lena))
# sillones amarillos y mesa de centro
def sillon(name, c, rot):
    pts = []
    def L(p): return (Matrix.Rotation(rot, 3, 'Z') @ Vector(p)) + Vector(c)
    base = cojin(name, L((0, 0, 0.36)), (0.74, 0.70, 0.20), M['amarillo'], rot=rot)
    resp = cojin(name + '_respaldo', L((0, 0.30, 0.72)), (0.76, 0.18, 0.66), M['amarillo'], rot=rot, tilt=-0.18)
    brazos = [cojin(name + f'_brazo{k}', L((sx * 0.36, 0.02, 0.50)), (0.12, 0.64, 0.30), M['amarillo'], rot=rot) for k, sx in enumerate((-1, 1))]
    patas = [barra(name + '_pata', L((sx * 0.30, sy * 0.28, 0.26)), L((sx * 0.34, sy * 0.33, 0.0)) + Vector((0, 0, 0.001)), 0.018, M['tronco'], 10) for sx in (-1, 1) for sy in (-1, 1)]
    mueble(unir(name, [base, resp] + brazos)); mueble(unir(name + '_patas', patas))
sillon('sillon_1', (0.55, -2.45, Z), math.radians(160))
sillon('sillon_2', (1.95, -1.20, Z), math.radians(105))
mueble(cilindro('mesa_centro', (1.15, -1.75, Z + 0.43), 0.32, 0.05, M['triplay'], 40, b=0.012))
mueble(unir('mesa_centro_patas', [barra('m', (1.15 + 0.2 * math.cos(a), -1.75 + 0.2 * math.sin(a), Z + 0.41), (1.15 + 0.25 * math.cos(a), -1.75 + 0.25 * math.sin(a), Z), 0.017, M['triplay'], 10) for a in (0.4, 2.5, 4.6)]))
mueble(cilindro('mesa_centro_florero', (1.10, -1.72, Z + 0.53), 0.06, 0.15, M['blanco'], 20))
# barra curva de trabajo con dos bancos
A0, A1, RI, RO, HB = 118, 170, 2.55, 3.02, 0.98
arc = [(RO * math.sin(math.radians(a)), -RO * math.cos(math.radians(a))) for a in np.linspace(A0, A1, 24)]
arc += [(RI * math.sin(math.radians(a)), -RI * math.cos(math.radians(a))) for a in np.linspace(A1, A0, 24)]
mueble(prisma('barra_cubierta', arc, Z + HB - 0.04, Z + HB, M['triplay'], b=0.006))
patas = []
for a in (A0 + 3, (A0 + A1) / 2, A1 - 3):
    for rr in (RI + 0.06, RO - 0.06):
        patas.append(caja('p', (rr * math.sin(math.radians(a)), -rr * math.cos(math.radians(a)), Z + (HB - 0.04) / 2), (0.045, 0.045, HB - 0.04), M['triplay'], b=0.003))
mueble(unir('barra_patas', patas))
mueble(caja('barra_cafetera', (2.75 * math.sin(math.radians(A0 + 6)), -2.75 * math.cos(math.radians(A0 + 6)), Z + HB + 0.17), (0.2, 0.28, 0.34), M['negro'], rot=math.radians(A0 + 6), b=0.01))
mueble(caja('barra_libro', (2.78 * math.sin(math.radians(A1 - 12)), -2.78 * math.cos(math.radians(A1 - 12)), Z + HB + 0.012), (0.22, 0.30, 0.025), M['blanco'], rot=math.radians(A1 - 12), b=0.003))
for k, a in enumerate((A0 + 14, A1 - 16)):
    cx, cy = 2.12 * math.sin(math.radians(a)), -2.12 * math.cos(math.radians(a))
    bn = [cilindro('b', (cx, cy, Z + 0.70), 0.17, 0.04, M['triplay'], 28, b=0.008)]
    for t in (0.5, 2.1, 3.7, 5.3):
        bn.append(barra('b', (cx + 0.11 * math.cos(t), cy + 0.11 * math.sin(t), Z + 0.68), (cx + 0.19 * math.cos(t), cy + 0.19 * math.sin(t), Z), 0.016, M['triplay'], 8))
    mueble(unir(f'banco_{k}', bn))
# plantas en maceta
def planta(name, c, h, r):
    mueble(cilindro(name + '_maceta', (c[0], c[1], Z + 0.16), 0.17, 0.32, M['maceta'], 28, r2=0.14, b=0.01))
    hojas = [esfera(name, (c[0] + dx, c[1] + dy, Z + h + dz), r * s, M['hoja'], 2) for dx, dy, dz, s in
             ((0, 0, 0, 1), (0.12, 0.05, -0.18, 0.8), (-0.1, 0.08, -0.12, 0.85), (0.03, -0.12, 0.15, 0.75), (-0.05, -0.02, 0.28, 0.6))]
    hojas.append(barra(name, (c[0], c[1], Z + 0.3), (c[0], c[1], Z + h), 0.012, M['tronco'], 8))
    mueble(unir(name + '_follaje', hojas))
planta('planta_1', (-2.75, -0.75), 0.95, 0.30)
planta('planta_2', (2.85, 0.60), 0.85, 0.28)
planta('planta_3', (1.45, 2.55), 0.75, 0.24)

# ------------------------------------------------------------------ terraza: sillas, mesa, camastro y puf (foto exterior)
def silla_adirondack(name, c, rot):
    L = lambda p: (Matrix.Rotation(rot, 3, 'Z') @ Vector(p)) + Vector(c)
    ps = []
    for k in range(5): ps.append(caja('a', L((-0.24 + k * 0.12, 0.05, 0.36 - k * 0.0)), (0.09, 0.55, 0.025), M['terraza'], b=0.004))
    for k in range(5):
        x = -0.24 + k * 0.12; top = 0.95 - abs(k - 2) * 0.05
        ob = caja('a', L((x, 0.42, 0.38 + (top - 0.38) / 2)), (0.09, 0.025, top - 0.38), M['terraza'], b=0.004)
        ob.data.transform(Matrix.Translation(-L((x, 0.42, 0.38))) ); ob.data.transform(Matrix.Rotation(-0.35, 4, Matrix.Rotation(rot, 3, 'Z') @ Vector((1, 0, 0)))); ob.data.transform(Matrix.Translation(L((x, 0.42, 0.38))))
        ps.append(ob)
    for sx in (-1, 1):
        ps.append(caja('a', L((sx * 0.36, 0.05, 0.60)), (0.13, 0.75, 0.025), M['terraza'], b=0.004))
        for sy in (-0.28, 0.35): ps.append(caja('a', L((sx * 0.33, sy, 0.30)), (0.05, 0.07, 0.60 if sy < 0 else 0.60), M['terraza'], b=0.003))
    mueble(unir(name, ps))
silla_adirondack('terraza_silla_1', (-3.55, -4.55, 0), math.radians(200))
silla_adirondack('terraza_silla_2', (-2.25, -5.05, 0), math.radians(160))
mueble(caja('terraza_mesa', (-2.85, -4.30, 0.72), (0.95, 0.6, 0.04), M['terraza'], b=0.006))
mueble(unir('terraza_mesa_patas', [barra('m', (-2.85 + sx * 0.4, -4.30 + sy * 0.24, 0.70), (-2.85 + sx * 0.42, -4.30 + sy * 0.26, 0), 0.018, M['marco'], 8) for sx in (-1, 1) for sy in (-1, 1)]))
mueble(caja('terraza_camastro_base', (3.65, -3.4, 0.22), (0.80, 1.95, 0.08), M['marco'], b=0.006))
mueble(cojin('terraza_camastro_colchon', (3.65, -3.4, 0.33), (0.78, 1.90, 0.14), M['blanco']))
mueble(unir('terraza_camastro_patas', [caja('c', (3.65 + sx * 0.34, -3.4 + sy * 0.88, 0.09), (0.05, 0.05, 0.18), M['marco'], b=0.002) for sx in (-1, 1) for sy in (-1, 1)]))
mueble(cilindro('terraza_puf_base', (0.35, -4.55, 0.18), 0.36, 0.36, M['mimbre'], 32, b=0.02))
mueble(cojin('terraza_puf_cojin', (0.35, -4.55, 0.42), (0.74, 0.74, 0.16), M['blanco']))

for ob in COL.objects:
    if ob.type == 'MESH' and ob.name.startswith(('ventanal_marco', 'estructura_placa')): smooth(ob, 30)

import json
json.dump({'RED': RED, 'CEN': list(CEN), 'R': R, 'RB': RB, 'ZC': ZC, 'PISO': PISO, 'caras': [[list(centro(f))] for f in FACES]},
          open(os.path.join(OUT, 'domo-meta.json'), 'w'))
tris = sum(sum(len(p.vertices) - 2 for p in ob.data.polygons) for ob in COL.objects if ob.type == 'MESH')
print(f'geometría lista en {time.time()-T0:.1f}s · {len(COL.objects)} objetos · {tris} triángulos · ventanal {len(VENTANAL)} caras')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'domo-modelo.blend'))
