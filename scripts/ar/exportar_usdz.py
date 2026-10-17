"""Convierte un GLB de los visores en USDZ para Realidad Aumentada en Safari (AR Quick Look).

Uso:  python3 scripts/ar/exportar_usdz.py ENTRADA.glb SALIDA.usdz [--satinado]

- Deja el modelo armado (primer cuadro del clip «Despiece») y sin animación.
- Conserva la escala real en metros y apoya la pieza en el piso, centrada.
- --satinado sustituye «Acero inoxidable» y «Negro» por el acero satinado que usa el visor web.
"""
import sys
import bpy  # bpy primero: habilita mathutils
import mathutils

args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
entrada, salida = args[0], args[1]
satinado = '--satinado' in args

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=entrada)
escena = bpy.context.scene

# Modelo armado: cuadro inicial del despiece, luego se fija cada transformación y se quita la animación.
escena.frame_set(0)
bpy.context.view_layer.update()
mundo = {o: o.matrix_world.copy() for o in escena.objects}
for o in escena.objects:
    o.animation_data_clear()
for o in escena.objects:
    o.parent = None
    o.matrix_world = mundo[o]
for a in list(bpy.data.actions):
    bpy.data.actions.remove(a)
bpy.context.view_layer.update()

mallas = [o for o in escena.objects if o.type == 'MESH']
puntos = [o.matrix_world @ mathutils.Vector(v) for o in mallas for v in o.bound_box]
mn = mathutils.Vector([min(p[i] for p in puntos) for i in range(3)])
mx = mathutils.Vector([max(p[i] for p in puntos) for i in range(3)])
desplazamiento = mathutils.Vector(((mn.x + mx.x) / -2, (mn.y + mx.y) / -2, -mn.z))
for o in escena.objects:
    o.matrix_world = mathutils.Matrix.Translation(desplazamiento) @ o.matrix_world
for o in [o for o in escena.objects if o.type != 'MESH']:
    bpy.data.objects.remove(o)

if satinado:
    # Mismo acero que project-3d-v2.js: color #d1d5d8, metalness .82, roughness .26.
    acero = bpy.data.materials.new('Acero_inoxidable_satinado')
    acero.use_nodes = True
    bsdf = acero.node_tree.nodes['Principled BSDF']
    srgb = lambda c: c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4
    bsdf.inputs['Base Color'].default_value = (*[srgb(int('d1d5d8'[i:i + 2], 16) / 255) for i in (0, 2, 4)], 1)
    bsdf.inputs['Metallic'].default_value = .82
    bsdf.inputs['Roughness'].default_value = .26
    for o in mallas:
        for s in o.material_slots:
            if s.material and s.material.name in ('Acero inoxidable', 'Negro'):
                s.material = acero

for o in mallas:
    o.select_set(True)
print(f'piezas {len(mallas)}  medidas {tuple(round(v, 3) for v in (mx - mn))} m')

bpy.ops.wm.usd_export(
    filepath=salida, export_animation=False, export_materials=True, generate_preview_surface=True,
    generate_materialx_network=False, export_textures=True, convert_orientation=True,
    export_global_forward_selection='NEGATIVE_Z', export_global_up_selection='Y',
    export_lights=False, export_cameras=False, triangulate_meshes=True,
    root_prim_path='/Herraidea', convert_scene_units='METERS')
