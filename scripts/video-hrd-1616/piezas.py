"""Piezas detalladas del HRD 1616 para el video promocional (Blender 4.5, metros).

Se modelan a partir de las medidas del GLB del visor y de la fotografía del catálogo:
poste cuadrado de 50 mm cepillado, placa base con cuatro barrenos avellanados, tapa con
casquillo roscado, vástago con silleta, pasamanos redondo de 2", cable 1x19 de 3.2 mm,
terminales roscados M6 con tuerca y tornillos Allen de cabeza plana M8.
"""
import math
import bpy
import bmesh
from mathutils import Vector, Matrix

TAU = math.tau


# ---------------------------------------------------------------- utilidades de malla
def malla(nombre, verts, caras, suave=True, coleccion=None):
    m = bpy.data.meshes.new(nombre)
    m.from_pydata(verts, [], caras)
    m.update()
    if suave:
        m.shade_smooth()
    o = bpy.data.objects.new(nombre, m)
    (coleccion or bpy.context.scene.collection).objects.link(o)
    return o


def revolucion(nombre, perfil, pasos=96, suave=True):
    """Gira un perfil [(r, z), ...] alrededor de Z. r=0 cierra el polo."""
    verts, caras, anillos = [], [], []
    for r, z in perfil:
        if r == 0:
            anillos.append([len(verts)]); verts.append((0, 0, z))
        else:
            anillos.append(list(range(len(verts), len(verts) + pasos)))
            verts += [(r * math.cos(TAU * i / pasos), r * math.sin(TAU * i / pasos), z) for i in range(pasos)]
    for a, b in zip(anillos, anillos[1:]):
        if len(a) == 1 and len(b) == 1:
            continue
        if len(a) == 1:
            caras += [(a[0], b[i], b[(i + 1) % pasos]) for i in range(pasos)]
        elif len(b) == 1:
            caras += [(a[i], b[0], a[(i + 1) % pasos]) for i in range(pasos)]
        else:
            caras += [(a[i], b[i], b[(i + 1) % pasos], a[(i + 1) % pasos]) for i in range(pasos)]
    o = malla(nombre, verts, caras, suave)
    return o


def tubo_radio(nombre, largo, radio_fn, pasos_t=48, pasos_z=200, tapas=True):
    """Tubo a lo largo de Z cuyo radio depende de (ángulo, z): roscas y torones."""
    verts, caras = [], []
    for j in range(pasos_z + 1):
        z = largo * j / pasos_z
        for i in range(pasos_t):
            t = TAU * i / pasos_t
            r = radio_fn(t, z)
            verts.append((r * math.cos(t), r * math.sin(t), z))
    for j in range(pasos_z):
        for i in range(pasos_t):
            a = j * pasos_t + i; b = j * pasos_t + (i + 1) % pasos_t
            caras.append((a, b, b + pasos_t, a + pasos_t))
    if tapas:
        c0 = len(verts); verts.append((0, 0, 0))
        c1 = len(verts); verts.append((0, 0, largo))
        top = pasos_z * pasos_t
        for i in range(pasos_t):
            caras.append((c0, (i + 1) % pasos_t, i))
            caras.append((c1, top + i, top + (i + 1) % pasos_t))
    return malla(nombre, verts, caras)


def rosca(nombre, r_mayor, paso, largo, chaflan=0.0006, pasos_t=48, por_paso=10):
    """Rosca métrica aproximada (perfil trapezoidal helicoidal) con punta achaflanada."""
    h = r_mayor * 0.12

    def radio(t, z):
        f = ((z - paso * t / TAU) / paso) % 1.0
        perfil = min(1.0, max(0.0, 1.6 - abs(f - 0.5) * 4.0))  # cresta plana, valle plano
        r = r_mayor - h + h * perfil
        if z > largo - chaflan:
            r -= (z - (largo - chaflan)) * 0.9
        if z < chaflan:
            r -= (chaflan - z) * 0.9
        return r
    pasos_z = max(8, int(largo / paso * por_paso))
    return tubo_radio(nombre, largo, radio, pasos_t, pasos_z)


def caja_redondeada(nombre, dx, dy, dz, radio, segmentos=5):
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.active_object; o.name = nombre
    o.scale = (dx, dy, dz); bpy.ops.object.transform_apply(scale=True)
    o.location.z = dz / 2; bpy.ops.object.transform_apply(location=True)
    if radio:
        biselar(o, radio, segmentos)
    return o


def biselar(o, ancho, segmentos=4, angulo=50):
    m = o.modifiers.new('Bisel', 'BEVEL')
    m.width = ancho; m.segments = segmentos; m.limit_method = 'ANGLE'
    m.angle_limit = math.radians(angulo); m.harden_normals = True
    o.data.shade_smooth()
    w = o.modifiers.new('Normales', 'WEIGHTED_NORMAL'); w.keep_sharp = True
    return o


def restar(o, herramienta, aplicar=True):
    m = o.modifiers.new('Resta', 'BOOLEAN'); m.operation = 'DIFFERENCE'; m.object = herramienta; m.solver = 'EXACT'
    if aplicar:
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.modifier_apply(modifier=m.name)
        bpy.data.objects.remove(herramienta)
    return o


def aplicar_todo(o):
    bpy.context.view_layer.objects.active = o
    for m in list(o.modifiers):
        bpy.ops.object.modifier_apply(modifier=m.name)


def cilindro(nombre, r, h, vertices=64, z0=0.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=r, depth=h, location=(0, 0, z0 + h / 2))
    o = bpy.context.active_object; o.name = nombre
    return o


def unir(nombre, objetos):
    for o in objetos:
        aplicar_todo(o)
    bpy.ops.object.select_all(action='DESELECT')
    for o in objetos:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objetos[0]
    bpy.ops.object.join()
    o = bpy.context.active_object; o.name = nombre
    return o


# ---------------------------------------------------------------- materiales
def _nodos(nombre):
    m = bpy.data.materials.new(nombre); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    return m, nt, b


def acero_cepillado(nombre='Acero cepillado', eje='Z', escala_veta=900.0, rugosidad=0.24, color=(0.70, 0.70, 0.69)):
    """Acero inoxidable satinado: veta fina en la dirección del cepillado y rugosidad variable."""
    m, nt, b = _nodos(nombre)
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Metallic'].default_value = 1.0
    coords = nt.nodes.new('ShaderNodeTexCoord')
    mapeo = nt.nodes.new('ShaderNodeMapping')
    s = {'X': (2.0, escala_veta, escala_veta), 'Y': (escala_veta, 2.0, escala_veta), 'Z': (escala_veta, escala_veta, 2.0)}[eje]
    mapeo.inputs['Scale'].default_value = s
    nt.links.new(coords.outputs['Object'], mapeo.inputs['Vector'])
    ruido = nt.nodes.new('ShaderNodeTexNoise'); ruido.inputs['Scale'].default_value = 1.0
    ruido.inputs['Detail'].default_value = 8; ruido.inputs['Roughness'].default_value = .65
    nt.links.new(mapeo.outputs['Vector'], ruido.inputs['Vector'])
    rampa = nt.nodes.new('ShaderNodeMapRange')
    rampa.inputs['To Min'].default_value = rugosidad - .07; rampa.inputs['To Max'].default_value = rugosidad + .07
    nt.links.new(ruido.outputs['Fac'], rampa.inputs['Value'])
    nt.links.new(rampa.outputs['Result'], b.inputs['Roughness'])
    relieve = nt.nodes.new('ShaderNodeBump'); relieve.inputs['Strength'].default_value = .18; relieve.inputs['Distance'].default_value = .00004
    nt.links.new(ruido.outputs['Fac'], relieve.inputs['Height'])
    nt.links.new(relieve.outputs['Normal'], b.inputs['Normal'])
    # manchas muy suaves que rompen la uniformidad del metal
    manchas = nt.nodes.new('ShaderNodeTexNoise'); manchas.inputs['Scale'].default_value = 18
    nt.links.new(coords.outputs['Object'], manchas.inputs['Vector'])
    mezcla = nt.nodes.new('ShaderNodeMix'); mezcla.data_type = 'RGBA'
    mezcla.inputs[6].default_value = (*color, 1); mezcla.inputs[7].default_value = tuple(c * .9 for c in color) + (1,)
    nt.links.new(manchas.outputs['Fac'], mezcla.inputs['Factor'])
    nt.links.new(mezcla.outputs[2], b.inputs['Base Color'])
    return m


def acero_pulido(nombre='Acero pulido', rugosidad=0.12, color=(0.72, 0.72, 0.71)):
    m, nt, b = _nodos(nombre)
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Metallic'].default_value = 1.0; b.inputs['Roughness'].default_value = rugosidad
    return m


def fondo_rojo(nombre='Fondo rojo', color=(0.33, 0.014, 0.016)):
    m, nt, b = _nodos(nombre)
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Roughness'].default_value = .55
    b.inputs['Specular IOR Level'].default_value = .35
    return m


def asignar(o, mat):
    o.data.materials.clear(); o.data.materials.append(mat)
    return o


# ---------------------------------------------------------------- piezas
def tornillo_avellanado(nombre='Tornillo', diametro=0.008, largo=0.030, mat=None):
    """Tornillo Allen de cabeza plana (avellanado 90°). El plano superior de la cabeza queda en z=0."""
    r = diametro / 2; rc = diametro  # cabeza = 2d
    alto_cabeza = rc - r  # cono de 90°
    cabeza = revolucion(nombre + '_cabeza', [(0, 0), (rc - .0003, 0), (rc, -.0003), (rc, -.0006), (r, -.0006 - alto_cabeza), (r * .82, -.0006 - alto_cabeza - .0001), (0, -.0006 - alto_cabeza - .0001)], pasos=96)
    hexagono = cilindro('hex', diametro * .31 / math.cos(math.pi / 6), .006, vertices=6, z0=-.0045)
    restar(cabeza, hexagono)
    cono = revolucion('cono', [(0, -.0045), (diametro * .31, -.0045), (0, -.0062)], pasos=6)
    restar(cabeza, cono)
    cuerpo = rosca(nombre + '_rosca', r, .00125, largo - alto_cabeza, pasos_t=48)
    cuerpo.location.z = -.0006 - alto_cabeza - (largo - alto_cabeza)
    o = unir(nombre, [cabeza, cuerpo])
    if mat:
        asignar(o, mat)
    return o


def tuerca(nombre='Tuerca', entre_caras=0.010, alto=0.005, rosca_r=0.003, mat=None):
    """Tuerca hexagonal con chaflán de 30° en ambas caras. Centrada en z=0..alto."""
    r = entre_caras / 2 / math.cos(math.pi / 6)
    hexa = cilindro(nombre, r, alto, vertices=6)
    hexa.rotation_euler.z = math.pi / 6; bpy.ops.object.transform_apply(rotation=True)
    # sólido de intersección: doble cono truncado que achaflana las esquinas del hexágono
    doble = revolucion('doble', [(0, 0), (entre_caras / 2 * .97, 0), (r + .0004, alto * .32), (r + .0004, alto * .68), (entre_caras / 2 * .97, alto), (0, alto)], pasos=96)
    m = hexa.modifiers.new('Chaflan', 'BOOLEAN'); m.operation = 'INTERSECT'; m.object = doble; m.solver = 'EXACT'
    bpy.context.view_layer.objects.active = hexa; bpy.ops.object.modifier_apply(modifier=m.name); bpy.data.objects.remove(doble)
    hueco = cilindro('hueco', rosca_r * .86, alto + .004, z0=-.002)
    restar(hexa, hueco)
    biselar(hexa, .00012, 2, 35)
    if mat:
        asignar(hexa, mat)
    return hexa


def terminal_roscado(nombre='Terminal', largo_rosca=0.030, largo_prensa=0.034, mat=None, mat_rosca=None):
    """Terminal prensado para cable de 3.2 mm: cuerpo liso Ø6.5 y vástago roscado M6 a lo largo de +Z."""
    prensa = revolucion(nombre + '_prensa', [(0, 0), (.0019, 0), (.0021, .0003), (.0028, .004), (.00325, .006), (.00325, largo_prensa - .0008), (.003, largo_prensa), (0, largo_prensa)], pasos=64)
    hilo = rosca(nombre + '_rosca', .003, .001, largo_rosca)
    hilo.location.z = largo_prensa
    o = unir(nombre, [prensa, hilo])
    if mat:
        asignar(o, mat)
    return o


def cable(nombre='Cable', largo=1.0, d=0.0032, mat=None, torcido=0.032):
    """Cable 1x19 aproximado: seis torones helicoidales visibles sobre el núcleo, a lo largo de +Z."""
    R = d / 2

    def radio(t, z):
        fase = (t - TAU * z / torcido) * 6 / TAU
        f = fase - math.floor(fase)
        return R * (0.84 + 0.16 * math.sqrt(max(0.0, 1 - (2 * f - 1) ** 2)))
    pasos_z = max(16, int(largo / torcido * 18))
    o = tubo_radio(nombre, largo, radio, pasos_t=36, pasos_z=pasos_z)
    if mat:
        asignar(o, mat)
    return o


def losa_redondeada(nombre, dx, dy, espesor, radio, segmentos=16):
    """Placa rectangular con esquinas redondeadas en planta, de z=0 a z=espesor."""
    contorno = []
    for cx, cy, a0 in ((dx / 2 - radio, dy / 2 - radio, 0), (-dx / 2 + radio, dy / 2 - radio, 90),
                       (-dx / 2 + radio, -dy / 2 + radio, 180), (dx / 2 - radio, -dy / 2 + radio, 270)):
        for k in range(segmentos + 1):
            a = math.radians(a0 + 90 * k / segmentos)
            contorno.append((cx + radio * math.cos(a), cy + radio * math.sin(a)))
    n = len(contorno)
    verts = [(x, y, 0) for x, y in contorno] + [(x, y, espesor) for x, y in contorno]
    caras = [tuple(reversed(range(n))), tuple(range(n, 2 * n))]
    caras += [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    return malla(nombre, verts, caras, suave=False)


def placa_base(nombre='Base', lado=0.090, espesor=0.008, barreno=0.0088, separacion=0.033, mat=None):
    o = losa_redondeada(nombre, lado, lado, espesor, .007)
    for sx in (-1, 1):
        for sy in (-1, 1):
            avellanado = revolucion('av', [(0, espesor + .001), (barreno, espesor + .001), (barreno, espesor), (barreno / 2, espesor - barreno / 2), (barreno / 2, -.002), (0, -.002)], pasos=64)
            avellanado.location = (sx * separacion, sy * separacion, 0)
            restar(o, avellanado)
    biselar(o, .0005, 3, 40)
    if mat:
        asignar(o, mat)
    return o


def poste(nombre='Poste', alto=0.900, lado=0.050, mat=None, mat_tapa=None, barrenos=()):
    """Poste cuadrado de 50 mm sobre z=0 con tapa superior; barrenos Ø6.8 [(eje 'X'|'Y', z), ...] para el cable."""
    o = caja_redondeada(nombre, lado, lado, alto, .0026, 5)
    aplicar_todo(o)
    for eje, z in barrenos:
        h = cilindro('b', .0034, lado + .01, 48)
        h.rotation_euler = (0, math.pi / 2, 0) if eje == 'X' else (math.pi / 2, 0, 0)
        h.location = (0, 0, z)
        restar(o, h)
    biselar(o, .0004, 2, 40)
    if mat:
        asignar(o, mat)
    tapa = caja_redondeada(nombre + '_tapa', lado - .0006, lado - .0006, .0025, .0008, 3)
    tapa.data.transform(Matrix.Translation((0, 0, alto - .0018)))
    aplicar_todo(tapa)
    agujero = cilindro('a', .0052, .01, 64, alto - .004)
    restar(tapa, agujero)
    if mat_tapa:
        asignar(tapa, mat_tapa)
    return o, tapa


def soporte_pasamanos(nombre='Soporte', mat=None):
    """Soporte del pasamanos según el modelo del HRD 1616: casquillo Ø20 × 31 con prisionero,
    vástago Ø12 y placa plana de 40 × 24 × 4 mm. z=0 en la tapa del poste; la placa termina en z=0.097."""
    casquillo = revolucion(nombre + '_casquillo', [(0, 0), (.0094, 0), (.01, .0006), (.01, .0304), (.0094, .031), (.006, .031), (0, .031)], pasos=96)
    prisionero = cilindro('prisionero', .0018, .004, 48)
    prisionero.rotation_euler = (0, math.pi / 2, 0); prisionero.location = (.0105, 0, .016)
    restar(casquillo, prisionero)
    tornillo = revolucion(nombre + '_prisionero', [(0, 0), (.0016, 0), (.0016, .0035), (0, .0035)], pasos=32)
    hexagono = cilindro('hex', .0009 / math.cos(math.pi / 6), .003, vertices=6, z0=.0012)
    restar(tornillo, hexagono)
    tornillo.rotation_euler = (0, math.pi / 2, 0); tornillo.location = (.0064, 0, .016)
    vastago = cilindro(nombre + '_vastago', .006, .075, 64, .018)
    biselar(vastago, .0005, 2, 40)
    placa = caja_redondeada(nombre + '_placa', .040, .024, .004, .0006, 3)
    placa.location.z = .093
    o = unir(nombre, [casquillo, tornillo, vastago, placa])
    if mat:
        asignar(o, mat)
    return o


def pasamanos(nombre='Pasamanos', largo=1.0, ancho=0.060, alto=0.030, mat=None):
    """Pasamanos rectangular de 60 × 30 mm a lo largo de +X, de x=0 a x=largo, con la base en z=0."""
    o = caja_redondeada(nombre, largo, ancho, alto, .0028, 5)
    o.data.transform(Matrix.Translation((largo / 2, 0, 0)))
    if mat:
        asignar(o, mat)
    return o

def arandela(nombre='Arandela', r_ext=0.006, r_int=0.0033, espesor=0.0016, mat=None):
    o = revolucion(nombre, [(r_int, 0), (r_ext - .0002, 0), (r_ext, .0002), (r_ext, espesor - .0002), (r_ext - .0002, espesor), (r_int, espesor), (r_int, 0)], pasos=96)
    if mat:
        asignar(o, mat)
    return o

