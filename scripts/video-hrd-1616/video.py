"""Video promocional del HRD 1616: estudio rojo, tomas macro y armado de la esquina.

Uso (Blender 4.5 como módulo de Python):
    python3 scripts/video-hrd-1616/video.py --toma 1 --salida carpeta/ [--cuadros 1-62] [--muestras 32] [--escala 100]
    python3 scripts/video-hrd-1616/video.py --toma 1 --fija 30 --salida prueba.png   (un solo cuadro)

Las seis tomas se renderizan por separado a 24 cuadros por segundo y luego se montan con el audio.
"""
import argparse
import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import piezas as P  # noqa: E402

FPS = 24
TOMAS = {1: 62, 2: 62, 3: 58, 4: 68, 5: 74, 6: 60}  # duración en cuadros (16 s en total)

LADO = 0.050                     # poste cuadrado
PLACA = 0.008                    # espesor de la placa base
ALTO = 0.900                     # poste sobre la placa
TOPE = PLACA + ALTO              # asiento del soporte
ANCHO_PAS, ALTO_PAS = 0.060, 0.030   # pasamanos rectangular del modelo
Z_PAS = TOPE + 0.097             # base del pasamanos sobre la placa del soporte
TRAMO = 1.15                     # distancia entre postes, como en el modelo
VUELO = 0.090                    # el pasamanos rebasa 9 cm el poste extremo
CABLES = [PLACA + 0.100 + i * 0.115 for i in range(7)]
PRENSA = 0.034


# ---------------------------------------------------------------- estudio
def estudio(rojo):
    """Ciclorama rojo (piso curvo hacia el muro), luces de estudio y ajustes de render."""
    verts, caras = [], []
    perfil = [(-8 + i * .5, 0.0) for i in range(17)]  # piso de y=-8 a y=0
    R = 2.5
    perfil += [(R * math.sin(a), R - R * math.cos(a)) for a in [math.radians(5 * k) for k in range(1, 19)]]
    perfil += [(R, R + 1.0 * k) for k in range(1, 7)]
    ancho = 12
    for y, z in perfil:
        verts += [(-ancho, y + 2.0, z), (ancho, y + 2.0, z)]
    for k in range(len(perfil) - 1):
        caras.append((2 * k, 2 * k + 1, 2 * k + 3, 2 * k + 2))
    ciclo = P.malla('Ciclorama', verts, caras)
    P.asignar(ciclo, rojo)

    sc = bpy.context.scene
    mundo = bpy.data.worlds.new('Mundo'); sc.world = mundo; mundo.use_nodes = True
    fondo = mundo.node_tree.nodes['Background']
    fondo.inputs['Color'].default_value = (0.12, 0.006, 0.008, 1); fondo.inputs['Strength'].default_value = 0.6

    def luz(nombre, tam, energia, pos, objetivo=(0, 0, .5), color=(1, 1, 1), forma='RECTANGLE', tam_y=None):
        l = bpy.data.lights.new(nombre, 'AREA'); l.shape = forma; l.size = tam; l.size_y = tam_y or tam
        l.energy = energia; l.color = color
        o = bpy.data.objects.new(nombre, l); sc.collection.objects.link(o); o.location = pos
        o.rotation_euler = (Vector(objetivo) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
        return o
    luces = {
        'clave': luz('Clave', 1.6, 520, (-1.6, -2.2, 2.6), color=(1, .97, .93)),
        'contra': luz('Contra', .35, 520, (2.2, 1.4, 1.6), color=(.92, .96, 1), tam_y=2.4),
        'cenital': luz('Cenital', 2.2, 260, (.4, -.2, 3.4)),
        'tira': luz('Tira', .18, 300, (-2.4, .6, 1.2), tam_y=2.0),
        # panel frontal grande: da a las caras del acero un gris luminoso en lugar de reflejar solo rojo
        'frente': luz('Frente', 3.0, 900, (.6, -3.6, 1.3), objetivo=(.6, 0, .6), color=(1, .98, .96), tam_y=1.6),
    }
    # Enlace de luces: las luces del producto no tocan el ciclorama, que se ilumina aparte
    # con una luz suave y tenue para conservar el rojo profundo y el degradado del fondo.
    sin_fondo = bpy.data.collections.new('Sin ciclorama'); sin_fondo.objects.link(ciclo)
    sin_fondo.collection_objects[0].light_linking.link_state = 'EXCLUDE'
    solo_fondo = bpy.data.collections.new('Solo ciclorama'); solo_fondo.objects.link(ciclo)
    solo_fondo.collection_objects[0].light_linking.link_state = 'INCLUDE'
    for o in luces.values():
        o.light_linking.receiver_collection = sin_fondo
    luces['fondo'] = luz('Fondo', 3.0, 320, (-.8, -2.6, 2.4), color=(1, .95, .92))
    luces['fondo'].light_linking.receiver_collection = solo_fondo
    luces['ciclo'] = ciclo
    return luces


def ajustes(muestras, escala):
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
    sc.cycles.samples = muestras; sc.cycles.adaptive_threshold = .02; sc.cycles.use_denoising = True
    sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    sc.cycles.max_bounces = 8; sc.cycles.glossy_bounces = 5; sc.cycles.diffuse_bounces = 2
    sc.cycles.transmission_bounces = 2; sc.cycles.caustics_reflective = False; sc.cycles.caustics_refractive = False
    sc.cycles.sample_clamp_indirect = 6
    sc.render.resolution_x = 1080; sc.render.resolution_y = 1920; sc.render.resolution_percentage = escala
    sc.render.fps = FPS
    sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = .45
    sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Punchy'
    sc.view_settings.exposure = -.35
    sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_depth = '8'


def camara(nombre, lente=85, fstop=4.0):
    sc = bpy.context.scene
    cam = bpy.data.cameras.new(nombre); cam.lens = lente; cam.sensor_width = 36; cam.sensor_fit = 'AUTO'
    cam.clip_start = .005; cam.clip_end = 60
    cam.dof.use_dof = True; cam.dof.aperture_fstop = fstop; cam.dof.aperture_blades = 7
    o = bpy.data.objects.new(nombre, cam); sc.collection.objects.link(o); sc.camera = o
    mira = bpy.data.objects.new(nombre + '_mira', None); sc.collection.objects.link(mira)
    c = o.constraints.new('TRACK_TO'); c.target = mira; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
    cam.dof.focus_object = mira
    return o, mira


def clave(obj, cuadro, **valores):
    for k, v in valores.items():
        setattr(obj, k, v)
        obj.keyframe_insert(k, frame=cuadro)


def suavizar(obj, tipo='BEZIER', facil='AUTO'):
    ad = obj.animation_data
    if ad and ad.action:
        for fc in ad.action.fcurves:
            for k in fc.keyframe_points:
                k.interpolation = tipo
                if tipo == 'BEZIER':
                    k.handle_left_type = k.handle_right_type = 'AUTO_CLAMPED'


# ---------------------------------------------------------------- esquina completa
def materiales():
    return {
        'Z': P.acero_cepillado('Acero cepillado Z', 'Z'),
        'X': P.acero_cepillado('Acero cepillado X', 'X', rugosidad=.2),
        'pulido': P.acero_pulido(),
        'cable': P.acero_pulido('Cable', .2, (.62, .62, .61)),
        'rojo': P.fondo_rojo(),
    }


def copia(o, nombre):
    c = o.copy(); c.name = nombre; bpy.context.scene.collection.objects.link(c)
    return c


def orientar(o, d):
    """Gira un objeto modelado a lo largo de +Z para que apunte en la dirección d (eje mundial)."""
    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(Vector(d))


def esquina(M, postes=('E', 'A', 'B'), con_cables=True, con_pasamanos=True):
    """Construye la esquina HRD 1616: poste de esquina en el origen, tramo A hacia +X y tramo B hacia -Y."""
    piezas = {}
    centros = {'E': Vector((0, 0, 0)), 'A': Vector((TRAMO, 0, 0)), 'B': Vector((0, -TRAMO, 0))}
    alturas = [z - PLACA for z in CABLES]          # el poste se modela desde su propio pie
    barrenos = {'E': [('X', z) for z in alturas] + [('Y', z) for z in alturas], 'A': [('X', z) for z in alturas], 'B': [('Y', z) for z in alturas]}
    base0 = P.placa_base('Base_modelo', mat=M['X']); P.aplicar_todo(base0)
    tornillo0 = P.tornillo_avellanado('Tornillo_modelo', mat=M['pulido'])
    soporte0 = P.soporte_pasamanos('Soporte_modelo', mat=M['Z'])
    for k in postes:
        c = centros[k]
        poste, tapa = P.poste('Poste_' + k, ALTO, LADO, M['Z'], M['pulido'], barrenos[k])
        P.aplicar_todo(poste)
        for o in (poste, tapa):
            o.location = c + Vector((0, 0, PLACA))
        base = copia(base0, 'Base_' + k); base.location = c
        tornillos = []
        for i, (sx, sy) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1))):
            t = copia(tornillo0, f'Tornillo_{k}_{i}'); t.location = c + Vector((sx * .033, sy * .033, PLACA - .00005))
            tornillos.append(t)
        soporte = copia(soporte0, 'Soporte_' + k); soporte.location = c + Vector((0, 0, TOPE))
        if k == 'B':
            soporte.rotation_euler.z = math.pi / 2
        piezas[k] = {'poste': poste, 'tapa': tapa, 'base': base, 'tornillos': tornillos, 'soporte': soporte}
    for o in (base0, tornillo0, soporte0):
        bpy.data.objects.remove(o)

    if con_cables:
        terminal_largo = P.terminal_roscado('Terminal_largo', .064, PRENSA, M['pulido'])
        terminal_corto = P.terminal_roscado('Terminal_corto', .020, PRENSA, M['pulido'])
        tuerca0 = P.tuerca('Tuerca_modelo', mat=M['pulido'])
        arandela0 = P.arandela('Arandela_modelo', mat=M['pulido'])
        piezas['cables'] = []
        for tramo, d in (('A', Vector((1, 0, 0))), ('B', Vector((0, -1, 0)))):
            if tramo not in postes:
                continue
            for i, z in enumerate(CABLES):
                cara_e = d * (LADO / 2) + Vector((0, 0, z))
                cara_f = centros[tramo] - d * (LADO / 2) + Vector((0, 0, z))
                te = copia(terminal_corto, f'Terminal_{tramo}_esquina_{i}'); orientar(te, -d); te.location = cara_e + d * PRENSA
                tf = copia(terminal_largo, f'Terminal_{tramo}_extremo_{i}'); orientar(tf, d); tf.location = cara_f - d * PRENSA
                ar = copia(arandela0, f'Arandela_{tramo}_{i}'); orientar(ar, d); ar.location = cara_f + d * LADO
                tu = copia(tuerca0, f'Tuerca_{tramo}_{i}'); orientar(tu, d); tu.location = cara_f + d * (LADO + .0016)
                largo = (cara_f - cara_e).length - 2 * PRENSA + .02
                ca = P.cable(f'Cable_{tramo}_{i}', largo, mat=M['cable']); orientar(ca, d)
                ca.location = cara_e + d * (PRENSA - .01)
                piezas['cables'].append({'tramo': tramo, 'i': i, 'cable': ca, 'esquina': te, 'extremo': tf, 'arandela': ar, 'tuerca': tu, 'd': d})
        for o in (terminal_largo, terminal_corto, tuerca0, arandela0):
            bpy.data.objects.remove(o)

    if con_pasamanos:
        # Dos tramos rectangulares unidos en inglete a 45° sobre el poste de esquina (plano x + y = 0).
        piezas['pasamanos'] = []
        r = ANCHO_PAS / 2
        diagonal = Vector((1, 1, 0)).normalized()
        for tramo, giro, inicio, lado in (('A', 0, (-r, 0), -1), ('B', -math.pi / 2, (0, r), 1)):
            if tramo not in postes:
                continue
            tubo = P.pasamanos('Pasamanos_' + tramo, TRAMO + VUELO + r, ANCHO_PAS, ALTO_PAS, M['X'])
            tubo.rotation_euler.z = giro
            tubo.location = (inicio[0], inicio[1], Z_PAS)
            corte = P.caja_redondeada('corte', .3, .3, .3, 0, 1)
            corte.rotation_euler.z = math.pi / 4
            corte.location = diagonal * (.15 * lado) + Vector((0, 0, Z_PAS - .15))
            P.restar(tubo, corte)
            piezas['pasamanos'].append(tubo)
    return piezas


# ---------------------------------------------------------------- tomas
def girar(o, eje, vueltas_inicio, vueltas_fin, c0, c1):
    """Anima el giro de un objeto (cuaternión) alrededor de un eje mundial, conservando su orientación base."""
    from mathutils import Quaternion
    base = o.rotation_quaternion.copy()
    for c in range(c0, c1 + 1):
        t = (c - c0) / max(1, c1 - c0)
        s = 1 - (1 - t) ** 3                               # termina despacio, como al apretar
        v = vueltas_inicio + (vueltas_fin - vueltas_inicio) * s
        o.rotation_quaternion = Quaternion(Vector(eje), -math.tau * v) @ base
        o.keyframe_insert('rotation_quaternion', frame=c)
    return o


def mover(o, desde, hasta, c0, c1, curva=lambda t: t * t * (3 - 2 * t)):
    for c in range(c0, c1 + 1):
        t = curva((c - c0) / max(1, c1 - c0))
        o.location = Vector(desde).lerp(Vector(hasta), t)
        o.keyframe_insert('location', frame=c)


def salida_lenta(t):
    return 1 - (1 - t) ** 3


def toma_1(M):
    """Macro: tornillo Allen de cabeza plana entrando en la placa base del poste A."""
    e = esquina(M)
    t = e['A']['tornillos'][3]                  # esquina frontal derecha (+x, -y)
    asiento = t.location.copy()
    orientar(t, (0, 0, 1))
    mover(t, asiento + Vector((0, 0, .040)), asiento, 1, 52, salida_lenta)
    girar(t, (0, 0, 1), 0, 4.2, 1, 52)
    cam, mira = camara('Camara', 100, 3.2)
    mira.location = asiento + Vector((0, 0, .004))
    mover(cam, asiento + Vector((.075, -.15, .10)), asiento + Vector((.05, -.125, .078)), 1, TOMAS[1])
    return cam


def toma_2(M):
    """Macro: tuerca girando sobre el vástago roscado del terminal en la cara exterior del poste A."""
    e = esquina(M)
    c = next(x for x in e['cables'] if x['tramo'] == 'A' and x['i'] == 3)
    tu, d = c['tuerca'], c['d']
    asiento = tu.location.copy()
    mover(tu, asiento + d * .045, asiento + d * .0075, 1, 12, salida_lenta)
    mover(tu, asiento + d * .0075, asiento, 12, 50, lambda t: 1 - (1 - t) ** 2)
    girar(tu, d, 0, 7.5, 12, 50)
    cam, mira = camara('Camara', 100, 3.5)
    mira.location = asiento + d * .004
    mover(cam, asiento + Vector((.075, -.115, .04)), asiento + Vector((.06, -.098, .028)), 1, TOMAS[2])
    return cam


def toma_3(M):
    """Remate superior: el soporte baja al poste y el pasamanos se asienta en la silleta."""
    e = esquina(M)
    s = e['A']['soporte']; asiento = s.location.copy()
    mover(s, asiento + Vector((0, 0, .11)), asiento, 1, 26, salida_lenta)
    clave(s, 1, rotation_euler=(0, 0, -1.2)); clave(s, 26, rotation_euler=(0, 0, 0))
    for tubo in e['pasamanos']:
        base = tubo.location.copy()
        mover(tubo, base + Vector((0, 0, .16)), base, 24, 44, salida_lenta)
    cam, mira = camara('Camara', 70, 4.5)
    mover(mira, asiento + Vector((.02, 0, .06)), asiento + Vector((.025, 0, .09)), 1, TOMAS[3])
    mover(cam, asiento + Vector((.40, -.34, .2)), asiento + Vector((.33, -.28, .16)), 1, TOMAS[3])
    return cam


def toma_4(M):
    """El poste completo flota inclinado y gira despacio sobre el fondo rojo."""
    e = esquina(M, postes=('A',), con_cables=False, con_pasamanos=False)
    ancla = bpy.data.objects.new('Ancla', None); bpy.context.scene.collection.objects.link(ancla)
    ancla.location = (TRAMO, 0, .5)
    bpy.context.view_layer.update()
    for o in [e['A']['poste'], e['A']['tapa'], e['A']['base'], e['A']['soporte'], *e['A']['tornillos']]:
        o.parent = ancla; o.matrix_parent_inverse = ancla.matrix_world.inverted()
    ancla.rotation_mode = 'XYZ'
    for c, (z, giro) in ((1, (.62, math.radians(-30))), (TOMAS[4], (.66, math.radians(38)))):
        ancla.location.z = z
        ancla.rotation_euler = (math.radians(14), math.radians(-9), giro)
        ancla.keyframe_insert('location', frame=c); ancla.keyframe_insert('rotation_euler', frame=c)
    cam, mira = camara('Camara', 60, 5.6)
    mira.location = (TRAMO, 0, .66)
    mover(cam, (TRAMO + .45, -1.85, .92), (TRAMO + .3, -1.68, .88), 1, TOMAS[4])
    return cam


def toma_5(M):
    """La esquina se arma: cables, soportes, pasamanos y tuercas llegan a su lugar."""
    e = esquina(M)
    fin = TOMAS[5]
    for c in e['cables']:
        lado = Vector((0, -1, 0)) if c['tramo'] == 'A' else Vector((1, 0, 0))
        retraso = c['i'] * 3 + (0 if c['tramo'] == 'A' else 5)
        for o in (c['cable'], c['esquina'], c['extremo']):
            mover(o, o.location + lado * .45 + Vector((0, 0, .05)), o.location.copy(), 1 + retraso, 26 + retraso)
        for o, dist in ((c['arandela'], .10), (c['tuerca'], .16)):
            mover(o, o.location + c['d'] * dist, o.location.copy(), 34 + retraso // 2, 52 + retraso // 2)
    for k in ('E', 'A', 'B'):
        s = e[k]['soporte']
        mover(s, s.location + Vector((0, 0, .35)), s.location.copy(), 22, 44)
    for i, tubo in enumerate(e['pasamanos']):
        mover(tubo, tubo.location + Vector((0, 0, .55)), tubo.location.copy(), 38 + 4 * i, 62 + 4 * i)
    # vista desde fuera de la esquina, sobre la diagonal: los dos tramos se alejan y caben en 9:16
    cam, mira = camara('Camara', 35, 8)
    mira.location = (.42, -.42, .5)
    mover(cam, (-2.15, 2.0, 1.75), (-1.9, 1.8, 1.5), 1, fin)
    return cam


def toma_6(M):
    """Toma final: la esquina armada, vista baja y acercamiento lento (el logotipo se añade al montar)."""
    esquina(M)
    cam, mira = camara('Camara', 32, 9)
    mover(mira, (.45, -.45, .72), (.45, -.45, .68), 1, TOMAS[6])
    mover(cam, (-1.85, 1.7, .5), (-1.62, 1.5, .46), 1, TOMAS[6])
    return cam


def principal():
    ap = argparse.ArgumentParser()
    ap.add_argument('--toma', type=int, required=True)
    ap.add_argument('--salida', required=True)
    ap.add_argument('--cuadros')
    ap.add_argument('--fija', type=int)
    ap.add_argument('--muestras', type=int, default=32)
    ap.add_argument('--escala', type=int, default=100)
    ap.add_argument('--guardar')
    a = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:])
    bpy.ops.wm.read_factory_settings(use_empty=True)
    M = materiales()
    estudio(M['rojo'])
    ajustes(a.muestras, a.escala)
    globals()[f'toma_{a.toma}'](M)
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, TOMAS[a.toma]
    if a.guardar:
        bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(a.guardar))
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
