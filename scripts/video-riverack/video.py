"""Video promocional del Riverack a partir del modelo publicado en la web (assets/projects/riverack/riverack.glb).

La geometría, las medidas y el despiece son los del GLB. Solo se sustituyen las mallas de los tornillos
por versiones con las mismas medidas y más resolución (cabeza hexagonal con brida, rosca y tuerca)
para que resistan las tomas macro. El estudio, las luces y los ajustes de render son los del video HRD 1616.

Uso:
    python3 scripts/video-riverack/video.py --toma 1 --salida carpeta/ [--muestras 20] [--escala 75]
    python3 scripts/video-riverack/video.py --toma 1 --fija 30 --salida prueba.png
"""
import argparse
import importlib.util
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.normpath(os.path.join(AQUI, '..', '..'))
sys.path.insert(0, os.path.join(RAIZ, 'scripts', 'video-hrd-1616'))
import piezas as P  # noqa: E402

_spec = importlib.util.spec_from_file_location('video_hrd', os.path.join(RAIZ, 'scripts', 'video-hrd-1616', 'video.py'))
H = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(H)

FPS = 24
TOMAS = {1: 60, 2: 62, 3: 58, 4: 56, 5: 78, 6: 96}  # 17.1 s
GLB = os.path.join(RAIZ, 'assets', 'projects', 'riverack', 'riverack.glb')
LEAN = math.radians(11)
S, C = math.sin(LEAN), math.cos(LEAN)


# ---------------------------------------------------------------- materiales
def pintura_polvo():
    """Pintura electrostática negra: satinada, con piel de naranja muy fina."""
    m, nt, b = P._nodos('Pintura polvo negra')
    b.inputs['Base Color'].default_value = (.012, .012, .014, 1)
    b.inputs['Metallic'].default_value = .0
    b.inputs['Coat Weight'].default_value = .04; b.inputs['Coat Roughness'].default_value = .3
    b.inputs['Specular IOR Level'].default_value = .22
    coords = nt.nodes.new('ShaderNodeTexCoord')
    ruido = nt.nodes.new('ShaderNodeTexNoise'); ruido.inputs['Scale'].default_value = 2600; ruido.inputs['Detail'].default_value = 3
    nt.links.new(coords.outputs['Object'], ruido.inputs['Vector'])
    relieve = nt.nodes.new('ShaderNodeBump'); relieve.inputs['Strength'].default_value = .08; relieve.inputs['Distance'].default_value = .0002
    nt.links.new(ruido.outputs['Fac'], relieve.inputs['Height']); nt.links.new(relieve.outputs['Normal'], b.inputs['Normal'])
    manchas = nt.nodes.new('ShaderNodeTexNoise'); manchas.inputs['Scale'].default_value = 9
    nt.links.new(coords.outputs['Object'], manchas.inputs['Vector'])
    rango = nt.nodes.new('ShaderNodeMapRange'); rango.inputs['To Min'].default_value = .45; rango.inputs['To Max'].default_value = .6
    nt.links.new(manchas.outputs['Fac'], rango.inputs['Value']); nt.links.new(rango.outputs['Result'], b.inputs['Roughness'])
    return m


def zinc():
    return P.acero_pulido('Zinc', .3, (.70, .72, .74))


# ---------------------------------------------------------------- tornillos detallados (mismas medidas del GLB)
def malla_tornillo(nombre, escala, mat):
    """Tornillo M8 de cabeza hexagonal con brida: brida Ø17 × 1.5, hexágono 13 mm × 4 y vástago Ø8 de 18 mm
    con rosca, como la malla del GLB. La tuerca se omite: queda dentro del tubo y, si viajara con el
    tornillo, se vería flotando sobre el vástago mientras entra."""
    brida = P.revolucion('brida', [(0, 0), (.0085, 0), (.0085, .0011), (.0081, .0015), (0, .0015)], pasos=96)
    cabeza = P.tuerca('cabeza', entre_caras=.013, alto=.004, rosca_r=.0001)
    cabeza.location.z = .0015
    tapa = P.revolucion('tapa', [(0, .0015), (.0045, .0015), (.0045, .0055), (0, .0055)], pasos=48)   # rellena el centro
    vastago = P.rosca('vastago', .004, .00125, .018)
    vastago.location.z = -.018
    o = P.unir(nombre, [brida, cabeza, tapa, vastago])
    o.data.transform(Matrix.Scale(escala, 4))
    P.asignar(o, mat)
    malla = o.data; malla.name = nombre
    bpy.data.objects.remove(o)
    return malla


# ---------------------------------------------------------------- escena
def cargar(M):
    bpy.ops.import_scene.gltf(filepath=GLB)
    sc = bpy.context.scene
    rack = [o for o in sc.objects if o.type == 'MESH' and o.name != 'Ciclorama']
    polvo, zn = pintura_polvo(), zinc()
    m8, m12 = malla_tornillo('tornillo_M8_detalle', 1.0, zn), malla_tornillo('tornillo_M12_detalle', 1.45, zn)
    for o in rack:
        if o.name.startswith('tornillo'):
            o.data = m12 if o.data.name.startswith('tornillo_M12') else m8
        else:
            o.data.materials.clear(); o.data.materials.append(polvo)
    piezas = {o.name: o for o in rack}
    sc.frame_set(0); bpy.context.view_layer.update()
    acomodar_tornillos(piezas)
    taladrar(piezas)
    return piezas


def mover_animado(o, d):
    """Desplaza una pieza animada sin alterar su despiece: suma d a su posición y a todas sus claves."""
    from bpy_extras import anim_utils
    ad = o.animation_data
    if ad and ad.action:
        cb = anim_utils.action_get_channelbag_for_slot(ad.action, ad.action_slot)
        for fc in cb.fcurves:
            if fc.data_path == 'location':
                for k in fc.keyframe_points:
                    for p in (k.co, k.handle_left, k.handle_right):
                        p.y += d[fc.array_index]
                fc.update()
    o.location += d


def acomodar_tornillos(piezas):
    """En el GLB, los tornillos superiores de cada funda quedan junto a los barrenos y no sobre ellos
    (|y| = 0.400 y 0.447 contra barrenos en 0.420 y 0.475). Se pasan al barreno más cercano."""
    for o in piezas.values():
        if not o.name.startswith('tornillo'):
            continue
        p = o.matrix_world.translation
        if p.z > .65 and eje(o).z > .9 and .38 < abs(p.y) < .46:
            destino = .420 if abs(p.y) < .42 else .475
            mover_animado(o, Vector((0, math.copysign(destino, p.y) - p.y, 0)))
    bpy.context.view_layer.update()


def taladrar(piezas):
    """Barreno pasante donde cada tornillo atraviesa una pieza que no lo tiene en el modelo
    (placas de la cabeza, alas de los postes, coples). Donde ya hay barreno, no cambia nada visible."""
    brocas = {}
    tornillos = [o for o in piezas.values() if o.name.startswith('tornillo')]
    otras = [o for o in piezas.values() if not o.name.startswith('tornillo')]
    for t in tornillos:
        grande = t.data.name.startswith('tornillo_M12')
        r, largo = (.0066, .03) if grande else (.0046, .022)
        d = eje(t); p = t.matrix_world.translation
        a, b = p + d * .001, p - d * largo
        for o in otras:
            caja = [o.matrix_world @ Vector(c) for c in o.bound_box]
            mn = Vector([min(v[i] for v in caja) for i in range(3)]); mx = Vector([max(v[i] for v in caja) for i in range(3)])
            if all(min(a[i], b[i]) - r < mx[i] and max(a[i], b[i]) + r > mn[i] for i in range(3)):
                brocas.setdefault(o.name, []).append((a, b, r))
    for nombre, lista in brocas.items():
        cilindros = []
        for a, b, r in lista:
            c = P.cilindro('broca', r, (b - a).length, 32)
            c.data.transform(Matrix.Translation((0, 0, -(b - a).length / 2)))
            c.location = (a + b) / 2 + (a - b) / 2
            c.rotation_mode = 'QUATERNION'; c.rotation_quaternion = Vector((0, 0, 1)).rotation_difference((a - b).normalized())
            cilindros.append(c)
        broca = P.unir('broca_' + nombre, cilindros) if len(cilindros) > 1 else cilindros[0]
        P.restar(piezas[nombre], broca)


def girar_estudio(luces):
    """El estudio de HRD 1616 mira hacia -Y; aquí la cámara ve el rack de frente (+X), a lo ancho."""
    R = Matrix.Rotation(math.radians(90), 4, 'Z')
    bpy.context.view_layer.update()            # matrix_world de los objetos recién creados
    for o in luces.values():
        o.matrix_world = R @ o.matrix_world


def hornear_despiece(piezas, cuadros, desde=120.0, hasta=0.0, curva=None):
    """Reproduce el clip «Despiece» del GLB con otro ritmo: graba la posición de cada pieza por cuadro."""
    sc = bpy.context.scene
    curva = curva or (lambda t: t * t * (3 - 2 * t))
    animadas = [o for o in piezas.values() if o.animation_data and o.animation_data.action]
    registro = {o.name: [] for o in animadas}
    for c in range(1, cuadros + 1):
        t = desde + (hasta - desde) * curva((c - 1) / (cuadros - 1))
        sc.frame_set(int(t), subframe=t - int(t))
        for o in animadas:
            registro[o.name].append(o.matrix_world.copy())
    for o in animadas:
        o.animation_data_clear()
        o.rotation_mode = 'QUATERNION'
        for c, mw in enumerate(registro[o.name], 1):
            o.matrix_world = mw
            o.keyframe_insert('location', frame=c); o.keyframe_insert('rotation_quaternion', frame=c)
    return registro


def asentamientos(registro, tolerancia=.0015):
    """Cuadro en que cada pieza llega a su lugar en el armado horneado: sirve para sincronizar los golpes."""
    eventos = []
    for nombre, mats in registro.items():
        final = mats[-1].translation
        movio = any((m.translation - final).length > .01 for m in mats)
        if not movio:
            continue
        llegada = next(c for c in range(len(mats), 0, -1) if (mats[c - 1].translation - final).length > tolerancia) + 1
        tipo = 'tornillo' if nombre.startswith('tornillo') else ('travesano' if 'travesano' in nombre else 'pieza')
        eventos.append((llegada, tipo, nombre))
    return sorted(eventos)


def armado(piezas):
    """Deja el rack armado (cuadro 0 del despiece) y sin animación."""
    sc = bpy.context.scene
    sc.frame_set(0)
    for o in piezas.values():
        mw = o.matrix_world.copy()
        o.animation_data_clear()
        o.matrix_world = mw


def lado(o):
    """'der', 'izq' o 'centro' (cople, tubos interiores y tornillos centrales del travesaño)."""
    n = o.name
    if 'cople' in n or 'interior' in n:
        return 'centro'
    if n.startswith('tornillo'):
        y = o.matrix_world.translation.y
        return 'centro' if abs(y) < .3 else ('der' if y > 0 else 'izq')
    return 'der' if '_der' in n else 'izq'


def parte_alta(o):
    """Piezas que suben con el ajuste de altura: pieza superior, cabezas, orejas, travesaños y su tornillería."""
    n = o.name
    if n.startswith('tornillo'):
        return o.matrix_world.translation.z > .58
    return any(k in n for k in ('superior', 'cabeza', 'oreja', 'travesano'))


BASE = {}


def ajustar(piezas, ancho, alto, c):
    """Fija y graba en el cuadro c el ajuste: `ancho` por lado (m, hacia afuera) y `alto` (m, a lo largo del poste)."""
    for o in piezas.values():
        mw = BASE.setdefault(o.name, o.matrix_world.copy())
        l = lado(o)
        d = Vector((0, 0, 0))
        if l in ('der', 'izq'):
            ys = 1 if l == 'der' else -1
            d.y += ys * ancho
            if parte_alta(o):
                d += Vector((0, -ys * S, C)) * alto
        elif parte_alta(o):
            d.z += alto * C
        o.matrix_world = Matrix.Translation(d) @ mw
        o.keyframe_insert('location', frame=c)


def animar_ajuste(piezas, claves):
    """claves: [(cuadro, ancho, alto), ...]; entre claves se interpola con aceleración y frenado suaves."""
    for (c0, a0, h0), (c1, a1, h1) in zip(claves, claves[1:]):
        for c in range(c0, c1 + 1):
            t = (c - c0) / max(1, c1 - c0); t = t * t * (3 - 2 * t)
            ajustar(piezas, a0 + (a1 - a0) * t, h0 + (h1 - h0) * t, c)


def eje(o):
    return (o.matrix_world.to_3x3() @ Vector((0, 0, 1))).normalized()


def atornillar(o, c0, c1, distancia=.03, vueltas=3.5):
    """El tornillo entra a lo largo de su eje girando y se detiene al asentar; antes de c0 espera afuera."""
    o.animation_data_clear()
    if o.name in BASE:
        o.matrix_world = BASE[o.name]
    asiento = o.matrix_world.translation.copy(); d = eje(o)
    o.rotation_mode = 'QUATERNION'
    base = o.rotation_quaternion.copy()
    from mathutils import Quaternion
    for c in range(c0, c1 + 1):
        t = (c - c0) / max(1, c1 - c0); s = 1 - (1 - t) ** 3
        o.location = asiento + d * distancia * (1 - s)
        o.rotation_quaternion = Quaternion(d, -math.tau * vueltas * s) @ base
        o.keyframe_insert('location', frame=c); o.keyframe_insert('rotation_quaternion', frame=c)
    return asiento


# ---------------------------------------------------------------- tomas
def toma_1(R):
    """Macro: tornillo con brida que aprieta la placa de la cabeza del poste delantero derecho."""
    armado(R)
    t = R['tornillo_033']
    asiento = atornillar(t, 1, 48)
    cam, mira = H.camara('Camara', 100, 3.2)
    mira.location = asiento + Vector((.002, 0, 0))
    H.mover(cam, asiento + Vector((.1, .13, .06)), asiento + Vector((.085, .11, .048)), 1, TOMAS[1])


def toma_2(R):
    """Recorrido lateral por el RIVERACK calado en la viga derecha."""
    armado(R)
    cam, mira = H.camara('Camara', 50, 2.8)
    H.mover(mira, (.22, .79, .262), (-.30, .79, .262), 1, TOMAS[2], lambda t: t)
    H.mover(cam, (.42, 1.22, .34), (-.10, 1.22, .32), 1, TOMAS[2], lambda t: t)


def toma_3(R):
    """Ajuste a lo ancho: la funda del travesaño corre sobre el tubo interior y se fija con dos tornillos."""
    armado(R)
    animar_ajuste(R, [(1, .10, 0), (40, 0, 0), (TOMAS[3], 0, 0)])
    for nombre, c0 in (('tornillo_053', 36), ('tornillo_054', 41)):
        atornillar(R[nombre], c0, c0 + 14, .035, 3)
    cam, mira = H.camara('Camara', 70, 3.5)
    H.mover(mira, (.735, .46, .645), (.735, .445, .64), 1, TOMAS[3])
    H.mover(cam, (1.0, .23, .78), (.96, .26, .75), 1, TOMAS[3])


def toma_4(R):
    """Ajuste de altura: la pieza superior sube dentro del poste y se asegura con el tornillo del ala."""
    armado(R)
    animar_ajuste(R, [(1, 0, 0), (30, 0, .075), (TOMAS[4], 0, .075)])
    atornillar(R['tornillo_039'], 32, 48, .03, 3)
    cam, mira = H.camara('Camara', 55, 4.5)
    H.mover(mira, (.75, .74, .5), (.75, .73, .54), 1, TOMAS[4])
    H.mover(cam, (1.42, 1.18, .72), (1.34, 1.1, .74), 1, TOMAS[4])


def toma_5(R):
    """El rack completo se arma con el despiece del modelo, en reversa."""
    eventos = asentamientos(hornear_despiece(R, TOMAS[5]))
    if os.environ.get('EVENTOS'):
        import json
        with open(os.environ['EVENTOS'], 'w') as f:
            json.dump(eventos, f)
    cam, mira = H.camara('Camara', 35, 8)
    mira.location = (0, 0, .4)
    H.mover(cam, (3.95, 1.0, 2.85), (3.55, .8, 2.5), 1, TOMAS[5])


def toma_6(R):
    """Toma final: el rack se abre y se cierra a lo ancho (cualquier camioneta) y queda armado."""
    armado(R)
    animar_ajuste(R, [(1, 0, 0), (10, 0, 0), (30, .09, .04), (42, .09, .04), (60, .03, .015), (TOMAS[6], .03, .015)])
    cam, mira = H.camara('Camara', 35, 9)
    H.mover(mira, (0, 0, .42), (0, 0, .4), 1, TOMAS[6])
    H.mover(cam, (3.75, .3, 2.25), (3.45, .25, 2.05), 1, TOMAS[6])


def principal():
    ap = argparse.ArgumentParser()
    ap.add_argument('--toma', type=int, required=True)
    ap.add_argument('--salida', required=True)
    ap.add_argument('--cuadros')
    ap.add_argument('--fija', type=int)
    ap.add_argument('--muestras', type=int, default=20)
    ap.add_argument('--escala', type=int, default=75)
    a = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:])
    bpy.ops.wm.read_factory_settings(use_empty=True)
    rojo = P.fondo_rojo()
    luces = H.estudio(rojo)
    girar_estudio(luces)
    luces['frente'].data.energy = 260         # el negro satinado refleja mucho el panel frontal
    H.ajustes(a.muestras, a.escala)
    R = cargar(None)
    globals()[f'toma_{a.toma}'](R)
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, TOMAS[a.toma]
    if a.fija:
        sc.frame_set(a.fija); sc.render.filepath = os.path.abspath(a.salida)
        bpy.ops.render.render(write_still=True)
        return
    if a.cuadros:
        sc.frame_start, sc.frame_end = map(int, a.cuadros.split('-'))
    os.makedirs(a.salida, exist_ok=True)
    sc.render.filepath = os.path.join(os.path.abspath(a.salida), f'toma{a.toma}_')
    bpy.ops.render.render(animation=True)


if __name__ == '__main__':
    principal()
