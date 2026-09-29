"""Riverack · rack de caja (solo el rack), modelado a partir de la foto de estudio.

Uso: python3 scripts/riverack/modelo.py  (bpy 4.5 o `blender -b -P`). Genera output/riverack/riverack-modelo.blend.

Metros. X a lo largo de la pickup, Y ancho, Z arriba; Z=0 es el apoyo de las bases.
Cambios contra v2: postes más anchos y bajos (sin logo), pieza superior casi del ancho del poste que abraza al
travesaño con dos placas laterales achaflanadas y oreja colgante; travesaños de tubo rectangular cerrado
telescópico (fundas, dos tubos interiores y cople central); vigas de tubo cerrado entre postes con RIVERACK
itálico tipo esténcil; bases en L con dos tornillos grandes y soporte en C hacia adentro.
Estimado desde fotografías: no son medidas de fabricación.
"""
import bpy, bmesh, math, os, time
from mathutils import Vector, Matrix

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.normpath(os.path.join(AQUI, '..', '..'))
OUT = os.path.join(RAIZ, 'output', 'riverack'); os.makedirs(OUT, exist_ok=True)
FONT = os.path.join(AQUI, 'fuentes', 'Archivo-900.ttf')
T0 = time.time()

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
COL = bpy.data.collections.new('RACK'); sc.collection.children.link(COL)
AUX = bpy.data.collections.new('AUX'); sc.collection.children.link(AUX)

# ------------------------------------------------------------------ parámetros (estimados)
T = 0.003
LEAN = math.radians(11)                      # inclinación de los postes hacia el centro (a lo ancho)
S, C = math.sin(LEAN), math.cos(LEAN)
POST_X = 0.735                               # centro de postes en X (±)
POST_Y = 0.845                               # plano del alma en la base (±)
W1, D1, A1 = 0.150, 0.050, (0.0, 0.557)      # poste inferior
W2 = 0.126                                   # pieza superior (centrada dentro del poste)
D2, A2 = 0.044, (0.330, 0.615)
ZIN = -(T + 0.0004)                          # alma de la pieza superior contra el alma del poste
BEAM_H, BEAM_D, BEAM_ZC = 0.135, 0.028, 0.262  # viga: alto, fondo, altura del centro
BEAM_N = -0.010                              # cara de la viga respecto al alma del poste
BW = W2 - 2 * T - 0.001                      # travesaño (funda): ancho entre placas de la cabeza
BH = 0.055
IW, IH = BW - 2 * T - 0.0012, BH - 2 * T - 0.0012
HEAD_LEN = 0.120                             # placa de cabeza a lo largo del travesaño

def mat(name, color, metallic, rough):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Metallic'].default_value = metallic
    b.inputs['Roughness'].default_value = rough
    return m
M_POLVO = mat('Pintura_polvo_negro', (0.010, 0.010, 0.012), 0.25, 0.48)
M_ZINC = mat('Zinc_tornilleria', (0.70, 0.72, 0.74), 1.0, 0.34)

# ------------------------------------------------------------------ utilidades
def eval_mesh(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    old = ob.data; ob.modifiers.clear(); ob.data = me
    if old.users == 0: bpy.data.meshes.remove(old)

def from_bm(name, bm, coll, material=None):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); coll.objects.link(ob)
    if material: me.materials.append(material)
    return ob

def rounded(pts, r, seg=3):
    out = [Vector(pts[0])]
    for i in range(1, len(pts) - 1):
        P, A, B = Vector(pts[i]), Vector(pts[i - 1]), Vector(pts[i + 1])
        da, db = (A - P).normalized(), (B - P).normalized()
        th = math.acos(max(-1, min(1, da.dot(db))))
        d = min(r / math.tan(th / 2), (A - P).length * .45, (B - P).length * .45)
        rr = d * math.tan(th / 2)
        p1 = P + da * d; p2 = P + db * d
        c = P + (da + db).normalized() * (rr / math.sin(th / 2))
        a1, a2 = math.atan2(p1.y - c.y, p1.x - c.x), math.atan2(p2.y - c.y, p2.x - c.x)
        dl = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi
        for k in range(seg + 1):
            a = a1 + dl * k / seg
            out.append(Vector((c.x + rr * math.cos(a), c.y + rr * math.sin(a))))
    out.append(Vector(pts[-1]))
    return out

def sweep(pr, x0, x1, closed, name, t=T):
    bm = bmesh.new()
    v0 = [bm.verts.new((x0, p.x, p.y)) for p in pr]
    v1 = [bm.verts.new((x1, p.x, p.y)) for p in pr]
    n = len(pr)
    for i in range(n if closed else n - 1):
        j = (i + 1) % n
        bm.faces.new((v0[i], v0[j], v1[j], v1[i]))
    ob = from_bm(name, bm, COL, M_POLVO)
    s = ob.modifiers.new('esp', 'SOLIDIFY'); s.thickness = t; s.offset = 0; s.use_even_offset = True
    eval_mesh(ob)
    return ob

def channel(x0, x1, w, fd, side, r=0.005, name='canal'):
    """Canal C: alma en el plano local XY (Z=0), ancho w en Y, alas de fd hacia side*Z; a lo largo de X."""
    return sweep(rounded([(-w / 2, side * fd), (-w / 2, 0), (w / 2, 0), (w / 2, side * fd)], r), x0, x1, False, name)

def tube(x0, x1, w, h, zc=0.0, r=0.006, name='tubo'):
    """Tubo rectangular cerrado a lo largo de X: ancho w en Y, alto h en Z (líneas medias de pared)."""
    pr = rounded([(0, zc - h / 2), (w / 2, zc - h / 2), (w / 2, zc + h / 2), (-w / 2, zc + h / 2),
                  (-w / 2, zc - h / 2), (0, zc - h / 2)], r)[:-1]
    return sweep(pr, x0, x1, True, name)

def stadium(cx, cy, L, W, ang=0.0, n=5):
    r, s = W / 2, max(L - W, 0) / 2
    pts = [(s + r * math.cos(-math.pi / 2 + math.pi * i / n), r * math.sin(-math.pi / 2 + math.pi * i / n)) for i in range(n + 1)]
    pts += [(-s + r * math.cos(math.pi / 2 + math.pi * i / n), r * math.sin(math.pi / 2 + math.pi * i / n)) for i in range(n + 1)]
    ca, sa = math.cos(ang), math.sin(ang)
    return [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts]

def circle(cx, cy, d, n=14):
    return [(cx + d / 2 * math.cos(2 * math.pi * i / n), cy + d / 2 * math.sin(2 * math.pi * i / n)) for i in range(n)]

def add_prism(bm, poly, z0=-0.008, z1=0.008, axis='z', xf=None):
    def P(a, b, z):
        if xf: return xf((a, b, z))                          # (u, v, espesor) -> mundo
        return (a, b, z) if axis == 'z' else (a, z, b)
    v0 = [bm.verts.new(P(a, b, z0)) for a, b in poly]
    v1 = [bm.verts.new(P(a, b, z1)) for a, b in poly]
    n = len(poly)
    bm.faces.new(v0[::-1]); bm.faces.new(v1)
    for i in range(n): bm.faces.new((v0[i], v0[(i + 1) % n], v1[(i + 1) % n], v1[i]))

def cut(ob, bm, extra=()):
    for me in extra: bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    cob = from_bm('cortador', bm, AUX)
    bo = ob.modifiers.new('cut', 'BOOLEAN'); bo.operation = 'DIFFERENCE'; bo.object = cob; bo.solver = 'EXACT'; bo.use_self = True
    eval_mesh(ob); bpy.data.objects.remove(cob)

def finish(ob, bevel=0.0007):
    b = ob.modifiers.new('bisel', 'BEVEL'); b.width = bevel; b.segments = 1; b.limit_method = 'ANGLE'; b.angle_limit = math.radians(50)
    eval_mesh(ob)

def smooth(ob):
    with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob]):
        bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))

def mat3(c1, c2, c3): return Matrix((c1, c2, c3)).transposed()
def place(ob, M, t): ob.matrix_world = Matrix.Translation(t) @ M.to_4x4()
def bake(ob): ob.data.transform(ob.matrix_world); ob.matrix_world = Matrix.Identity(4)

def clip_below(ob, z):
    bake(ob)
    bm = bmesh.new(); bm.from_mesh(ob.data)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, z), plane_no=(0, 0, 1), clear_inner=True)
    bm.to_mesh(ob.data); bm.free()

# ------------------------------------------------------------------ texto esténcil itálico
def stencil_text(body, width, cap, shear=math.radians(12)):
    cu = bpy.data.curves.new('txt', 'FONT'); cu.body = body; cu.font = bpy.data.fonts.load(FONT)
    cu.size = 0.1; cu.extrude = 0.008; cu.align_x = 'LEFT'; cu.align_y = 'BOTTOM'
    ob = bpy.data.objects.new('texto', cu); AUX.objects.link(ob); bpy.context.view_layer.update()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get())); bpy.data.objects.remove(ob)
    # letras = piezas sueltas, ordenadas de izquierda a derecha
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6); bm.to_mesh(me)
    bm.verts.ensure_lookup_table(); bm.verts.index_update()
    seen, parts = set(), []
    for v in bm.verts:
        if v.index in seen: continue
        stack, isl = [v], []
        seen.add(v.index)
        while stack:
            w = stack.pop(); isl.append(w.co.x)
            for e in w.link_edges:
                o = e.other_vert(w)
                if o.index not in seen: seen.add(o.index); stack.append(o)
        parts.append((min(isl), max(isl)))
    bm.free(); parts.sort()
    letras = []                                   # une piezas que se traslapan en X (una letra)
    for a0, a1 in parts:
        if letras and a0 < letras[-1][1] - 1e-4: letras[-1] = (letras[-1][0], max(letras[-1][1], a1))
        else: letras.append((a0, a1))
    assert len(letras) == len(body), (len(letras), letras)
    parts = letras
    x0, x1 = parts[0][0], parts[-1][1]
    y0, y1 = min(v.co.y for v in me.vertices), max(v.co.y for v in me.vertices)
    # puentes del esténcil (unen la panza de R, E, A y K con el resto de la pieza)
    frac = {'R': 0.35, 'E': 0.33, 'A': 0.50, 'K': 0.35}
    bb = bmesh.new()
    for ch, (a, b) in zip(body, parts):
        if ch in frac:
            xc = a + (b - a) * frac[ch]
            add_prism(bb, [(xc - 0.0012, y0 - 0.01), (xc + 0.0012, y0 - 0.01), (xc + 0.0012, y1 + 0.01), (xc - 0.0012, y1 + 0.01)], -0.02, 0.02)
    tob = bpy.data.objects.new('texto', me); AUX.objects.link(tob)
    cut(tob, bb)
    me = tob.data; bpy.data.objects.remove(tob)
    sx, sy = width / (x1 - x0), cap / (y1 - y0)
    k = math.tan(shear)
    for v in me.vertices:
        x = (v.co.x - (x0 + x1) / 2) * sx; y = (v.co.y - (y0 + y1) / 2) * sy
        v.co.x, v.co.y = x + y * k, y
    return me

# ------------------------------------------------------------------ marcos de cada poste
def frame(xs, ys):
    u = Vector((0, -ys * S, C))                 # eje del poste (sube hacia el centro)
    n = Vector((0, ys * C, S))                  # normal hacia afuera del alma
    M = mat3(u, (ys, 0, 0), n)                  # local: a = eje, b = X del mundo·ys, z = normal
    base = Vector((xs * POST_X, ys * POST_Y, 0))
    return u, n, M, base

def qz(a, d):
    """Punto del plano de las alas de la pieza superior: a sobre el eje, d desde el alma hacia adentro -> (q, z)."""
    k = ZIN - d
    return (POST_Y - S * a + C * k, C * a + S * k)

A_TOP_OUT = qz(A2[1], -T / 2)
ZB = A_TOP_OUT[1] + 0.0008                   # cara inferior del travesaño
ZC = ZB + T / 2 + BH / 2                     # línea media del travesaño
ZT = ZB + T + BH
def q_web(z):                                # cara exterior del alma de la pieza superior a la altura z
    k = ZIN + T / 2
    return POST_Y - S * (z - S * k) / C + C * k
E = q_web(ZB) + T / 2 + 0.045                # extremo exterior del travesaño

# ------------------------------------------------------------------ tornillería
def bolt_mesh(s, name):
    bm = bmesh.new()
    def cyl(seg, r, h, zc):
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r * s, radius2=r * s, depth=h * s, matrix=Matrix.Translation((0, 0, zc * s)))
    cyl(18, .0085, .0015, .00075); cyl(6, .0075, .0040, .0035); cyl(12, .0040, .018, -.0090); cyl(6, .0075, .0065, -.0120)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(M_ZINC)
    return me
BOLT = bolt_mesh(1.0, 'tornillo_M8'); BOLT_G = bolt_mesh(1.45, 'tornillo_M12'); NB = [0]
def bolt(pos, d, big=False):
    NB[0] += 1
    ob = bpy.data.objects.new(f'tornillo_{NB[0]:03d}', BOLT_G if big else BOLT); COL.objects.link(ob)
    ob.matrix_world = Matrix.Translation(pos) @ Vector((0, 0, 1)).rotation_difference(Vector(d).normalized()).to_matrix().to_4x4()

# ------------------------------------------------------------------ piezas
def a_of_z(z, k=0.0): return (z - S * k) / C

def poste(xs, ys, tag):
    u, n, M, base = frame(xs, ys)
    X = Vector((1, 0, 0))
    beam_top_a = a_of_z(BEAM_ZC, BEAM_N) + BEAM_H / 2
    # --- inferior: canal ancho, alma hacia afuera, alas hacia el centro
    lo = channel(A1[0], A1[1], W1, D1, -1, name=f'poste_{tag}_inferior'); finish(lo)
    bm = bmesh.new()
    k = A1[1] / 0.49
    for b in (-0.036, 0.036): add_prism(bm, circle(A1[1] - 0.020, b, 0.009))            # barrenos superiores
    for a in (0.425, 0.330, 0.225):
        for b in (-0.045, 0.045): add_prism(bm, stadium(a * k, b, 0.048, 0.011))       # pares de ranuras verticales
    for a in (0.385, 0.290, 0.262, 0.185): add_prism(bm, circle(a * k, 0, 0.0105))      # barrenos centrales
    for b in (-0.034, 0.034): add_prism(bm, stadium(0.140, b, 0.044, 0.012, math.pi / 2))  # ranuras horizontales
    for a in (0.405, 0.300, 0.250, 0.200, 0.160):                                         # alas: barrenos y ranura
        add_prism(bm, circle(a * k, -D1 * 0.55, 0.008), -W1 / 2 - 0.01, W1 / 2 + 0.01, axis='y')
    add_prism(bm, stadium(0.128, -D1 * 0.5, 0.030, 0.009), -W1 / 2 - 0.01, W1 / 2 + 0.01, axis='y')
    cut(lo, bm)
    place(lo, M, base); clip_below(lo, T + 0.0003)

    # --- superior: canal casi del mismo ancho, ranura horizontal arriba
    hi = channel(A2[0], A2[1], W2, D2, -1, name=f'poste_{tag}_superior'); finish(hi)
    bm = bmesh.new()
    add_prism(bm, stadium(A2[1] - 0.034, 0, 0.056, 0.017, math.pi / 2))
    for a in (0.36, 0.42): add_prism(bm, circle(a, 0, 0.0105))
    cut(hi, bm)
    hi.data.transform(Matrix.Translation((0, 0, ZIN)))
    place(hi, M, base)

    # --- cabeza: las alas de la pieza superior suben y abrazan al travesaño (placa achaflanada + oreja)
    zd = ZB - 0.010
    qtop = q_web(ZT - 0.006)
    qin = qtop - HEAD_LEN
    kt = ZIN - D2
    ae = (qin + zd - POST_Y - (C + S) * kt) / (C - S)
    ae = min(ae, A2[1] - 0.004)
    poly = [qz(A2[1], -T / 2), (qtop, ZT - 0.006), (qin, ZT - 0.006), (qin, zd), qz(ae, D2), qz(A2[1], D2)]
    tab_q = qin + 0.018
    for sx in (-1, 1):
        xc = xs * POST_X + sx * W2 / 2
        yz = lambda p, xc=xc: (xc + p[2], ys * p[0], p[1])     # (q, z, espesor) -> mundo
        bm = bmesh.new(); add_prism(bm, poly, -T / 2, T / 2, xf=yz)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        hp = from_bm(f'poste_{tag}_cabeza_{"a" if sx < 0 else "b"}', bm, COL, M_POLVO); finish(hp)
        # oreja colgante con barreno
        xo = xc + sx * T
        tl = (ZC + 0.016) - (ZB - 0.034)
        bm = bmesh.new(); add_prism(bm, stadium(tab_q, (ZC + 0.016 + ZB - 0.034) / 2, tl, 0.030, math.pi / 2), -T / 2, T / 2,
                                    xf=lambda p, xo=xo: (xo + p[2], ys * p[0], p[1]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        ear = from_bm(f'poste_{tag}_oreja_{"a" if sx < 0 else "b"}', bm, COL, M_POLVO); finish(ear)
        bm = bmesh.new(); add_prism(bm, circle(tab_q, ZB - 0.019, 0.011), -0.01, 0.01, xf=lambda p, xo=xo: (xo + p[2], ys * p[0], p[1]))
        cut(ear, bm)
        bolt(Vector((xc + sx * T / 2, ys * (q_web(ZC) - 0.050), ZC)), (sx, 0, 0))
        bolt(Vector((xo + sx * T / 2, ys * tab_q, ZC)), (sx, 0, 0))

    # --- base: collar alrededor del pie con dos tornillos grandes y soporte en C.
    #     En la foto de estudio las cuatro bases miran igual: placa atornillada hacia -Y y soporte hacia +Y.
    FH, FWc = 0.100, W1 + 2 * T + 0.0012
    FHc = D1 + 2 * T + 0.0012
    fs = tube(0.0, FH, FWc, FHc, zc=-D1 / 2, r=0.004, name=f'base_{tag}_collar'); finish(fs)
    bm = bmesh.new()
    for b in (-0.030, 0.0, 0.030): add_prism(bm, circle(0.030, -D1 * 0.45, 0.0075), -FWc / 2 - 0.01, FWc / 2 + 0.01, axis='y')
    cut(fs, bm)
    place(fs, M, base); clip_below(fs, T + 0.0003)
    zf = (FHc / 2 + T / 2) * (1 if ys < 0 else -1) - D1 / 2      # cara del collar que mira a -Y
    for b in (-0.036, 0.036):
        bolt(base + u * 0.055 + n * zf + X * b, n * (1 if ys < 0 else -1), big=True)
    yface = (base + n * zf).y - T / 2
    y1 = yface + 0.117
    prof = rounded([(yface, T / 2), (y1, T / 2), (y1, 0.026), (y1 - 0.045, 0.026)], 0.005)
    cb = sweep(prof, xs * POST_X - FWc / 2, xs * POST_X + FWc / 2, False, f'base_{tag}_soporte'); finish(cb)
    bm = bmesh.new(); add_prism(bm, stadium(xs * POST_X, y1 - 0.024, 0.060, 0.013), -0.01, 0.04)
    cut(cb, bm)

    # --- tornillos en las alas del poste: seguro de la pieza superior y amarre de la viga
    for sx in (-1, 1):
        for a in (A1[1] - 0.030, 0.360):
            bolt(base + u * a + n * (-D1 * 0.55) + X * (sx * (W1 / 2 + T / 2)), (sx, 0, 0))

def viga(ys, tag):
    u, n, M, base0 = frame(1, ys)
    Mb = mat3((-ys, 0, 0), u, n)
    L = POST_X - W1 / 2 - T / 2 - 0.001
    ob = channel(-L, L, BEAM_H, BEAM_D, -1, name=f'viga_lateral_{tag}'); finish(ob)
    ob.data.transform(Matrix.Translation((0, 0, BEAM_N)))
    bm = bmesh.new()
    zz = (BEAM_N - 0.008, BEAM_N + 0.008)
    k, xs_ = 0.100, []
    for i in range(-4, 5): xs_.append(i * k)
    for x in xs_:
        for row in (0.050, -0.050): add_prism(bm, stadium(x, row, 0.046, 0.012), *zz)
    for sx in (-1, 1):                                          # "#" en los extremos
        for dx in (0.050, 0.082):
            for row in (0.027, -0.027): add_prism(bm, stadium(sx * (L - dx), row, 0.042, 0.011, math.pi / 2), *zz)
        add_prism(bm, circle(sx * (L - 0.020), 0.030, 0.008), *zz)
    txt = stencil_text('RIVERACK', 0.50, 0.076)
    txt.transform(Matrix.Translation((0.015, -0.002, BEAM_N)))
    cut(ob, bm, [txt])
    a_mid = a_of_z(BEAM_ZC, BEAM_N - BEAM_D / 2)
    place(ob, Mb, Vector((0, ys * POST_Y, 0)) + u * a_mid)

def travesano(xs, tag):
    Mc = mat3((0, 1, 0), (-1, 0, 0), (0, 0, 1))
    at = Vector((xs * POST_X, 0, ZC))
    zside = (-BW / 2 - 0.01, BW / 2 + 0.01)
    top = (BH / 2 - 0.01, BH / 2 + 0.01)
    SL = 0.40
    for sy in (-1, 1):
        lab = 'der' if sy > 0 else 'izq'
        a0, a1 = sorted((sy * E, sy * (E - SL)))
        sl = tube(a0, a1, BW, BH, name=f'travesano_{tag}_funda_{lab}'); finish(sl)
        bm = bmesh.new()
        q = E - 0.050
        while q > E - SL + 0.030:
            for cy in (-0.036, 0.036): add_prism(bm, stadium(sy * q, cy, 0.030, 0.009), *top)
            add_prism(bm, circle(sy * (q - 0.027), 0, 0.008), *top)
            q -= 0.055
        add_prism(bm, stadium(sy * (E - 0.036), 0, 0.036, 0.010), *zside, axis='y')
        q = E - 0.036 - HEAD_LEN - 0.030
        while q > E - SL + 0.025:
            add_prism(bm, stadium(sy * q, 0, 0.030, 0.010), *zside, axis='y'); q -= 0.050
        cut(sl, bm); place(sl, Mc, at)
        # tubo interior (telescópico)
        b0, b1 = sorted((sy * (E - 0.012), sy * 0.004))
        it = tube(b0, b1, IW, IH, name=f'travesano_{tag}_interior_{lab}'); finish(it)
        bm = bmesh.new(); q = 0.20
        while q < E - 0.06:
            add_prism(bm, stadium(sy * q, 0, 0.026, 0.010), -IW / 2 - 0.01, IW / 2 + 0.01, axis='y')
            add_prism(bm, stadium(sy * q, 0, 0.026, 0.010), IH / 2 - 0.01, IH / 2 + 0.01)
            q += 0.045
        cut(it, bm); place(it, Mc, at)
        for q in (E - SL + 0.028, E - SL + 0.075):
            bolt(Vector((xs * POST_X, sy * q, ZC + BH / 2 + T / 2)), (0, 0, 1))
        for q in (0.055, 0.125):
            bolt(Vector((xs * POST_X, sy * q, ZC + BH / 2 + T / 2)), (0, 0, 1))
    cp = tube(-0.18, 0.18, BW, BH, name=f'travesano_{tag}_cople'); finish(cp)
    bm = bmesh.new()
    for q in (-0.09, 0.0, 0.09):
        for cy in (-0.036, 0.036): add_prism(bm, stadium(q, cy, 0.030, 0.009), *top)
    for q in (-0.10, -0.045, 0.045, 0.10): add_prism(bm, stadium(q, 0, 0.030, 0.010), *zside, axis='y')
    cut(cp, bm); place(cp, Mc, at)

# ------------------------------------------------------------------ armado
for xs in (-1, 1):
    for ys in (-1, 1):
        poste(xs, ys, f'{"trasero" if xs<0 else "delantero"}_{"izq" if ys<0 else "der"}')
for ys in (-1, 1): viga(ys, 'izq' if ys < 0 else 'der')
for xs in (-1, 1): travesano(xs, 'trasero' if xs < 0 else 'delantero')

for ob in COL.objects:
    if ob.type == 'MESH' and ob.data.materials and ob.data.materials[0] == M_POLVO: smooth(ob)
tris = sum(sum(len(p.vertices) - 2 for p in ob.data.polygons) for ob in COL.objects if ob.type == 'MESH')
bb = [(ob.matrix_world @ Vector(v)) for ob in COL.objects if ob.type == 'MESH' for v in ob.bound_box]
print(f'geometría lista en {time.time()-T0:.1f}s · {len(COL.objects)} objetos · {tris} triángulos · {NB[0]} tornillos')
print('  caja: x %.3f..%.3f  y %.3f..%.3f  z %.3f..%.3f' % (min(p.x for p in bb), max(p.x for p in bb), min(p.y for p in bb), max(p.y for p in bb), min(p.z for p in bb), max(p.z for p in bb)))
print('  ZB %.3f ZT %.3f E %.3f' % (ZB, ZT, E))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'riverack-modelo.blend'))
