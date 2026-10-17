"""Blender background: prepare the existing assembled HRD 1525 for Apple Quick Look.
The GLB stays untouched. This is a reference model, not approved fabrication geometry.
"""
import bpy, json, sys
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2]
out=root/'assets/projects/clip-system/hrd-1525-ar.usdz'
report=root/'content/projects/clip-system/ar-manifest.json'
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(root/'assets/projects/clip-system/herraje-cristal.glb'))
scene=bpy.context.scene
scene.frame_set(1)
objects=[o for o in scene.objects if o.type=='MESH']
for o in objects:o.animation_data_clear()
glass=next((o for o in objects if o.name=='Cristal_central'),None)
if not glass:raise RuntimeError('Missing original glass mesh')
# Same correction as prepareModel(profile="clips") in the published web viewer.
glass.scale.x *= (.96-.0592)/.838
bpy.context.view_layer.update()
original_glass=[]
for m in bpy.data.materials:
 if m.use_nodes and 'Cristal' in m.name:
  bsdf=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
  original_glass.append(m.name)
  # Preview Surface opacity is supported by Quick Look; glTF transmission alone is not portable.
  bsdf.inputs['Base Color'].default_value=(.82,.95,.91,1)
  bsdf.inputs['Alpha'].default_value=.14
  bsdf.inputs['Roughness'].default_value=.09
  bsdf.inputs['Transmission Weight'].default_value=0
  bsdf.inputs['Metallic'].default_value=0
  m.diffuse_color=(.82,.95,.91,.14)
  m.surface_render_method='DITHERED'
coords=[o.matrix_world@Vector(c) for o in objects for c in o.bound_box]
lo=Vector(tuple(min(v[i] for v in coords) for i in range(3)))
hi=Vector(tuple(max(v[i] for v in coords) for i in range(3)))
shift=Vector((-(lo.x+hi.x)/2,-(lo.y+hi.y)/2,-lo.z))
for o in objects:o.location+=shift
bpy.context.view_layer.update()
for o in scene.objects:o.select_set(o in objects)
scene.unit_settings.system='METRIC'
scene.unit_settings.scale_length=1
options=bpy.ops.wm.usd_export.get_rna_type().properties
print('USD_ENUMS',[(key,[v.identifier for v in options[key].enum_items]) for key in ['export_global_forward_selection','export_global_up_selection','convert_scene_units','export_textures_mode']])
bpy.ops.wm.usd_export(filepath=str(out),selected_objects_only=True,export_animation=False,export_materials=True,generate_preview_surface=True,generate_materialx_network=False,convert_orientation=True,export_global_forward_selection='NEGATIVE_Z',export_global_up_selection='Y',export_lights=False,export_cameras=False,export_curves=False,export_points=False,export_volumes=False,export_hair=False,export_armatures=False,export_shapekeys=False,relative_paths=True,root_prim_path='/Herraidea_HRD1525',convert_scene_units='METERS',meters_per_unit=1,accessibility_label='Herraidea HRD 1525: barandal con postes, clips y vidrio',accessibility_description='Tramo recto de referencia basado en el modelo web. Medidas por confirmar con Herraidea.')
from pxr import Usd,UsdGeom,Gf,UsdUtils
stage=Usd.Stage.Open(str(out))
if not stage:raise RuntimeError('USDZ could not be opened')
cache=UsdGeom.BBoxCache(Usd.TimeCode.Default(),[UsdGeom.Tokens.default_,UsdGeom.Tokens.render])
box=cache.ComputeWorldBound(stage.GetPseudoRoot()).ComputeAlignedBox()
meshes=[p for p in stage.Traverse() if p.IsA(UsdGeom.Mesh)]
data={'source':'assets/projects/clip-system/herraje-cristal.glb','asset':'assets/projects/clip-system/hrd-1525-ar.usdz','profile':'clips','code':'HRD 1525','kind':'assembled_reference','sourceMeshes':len(objects),'exportedMeshes':len(meshes),'metersPerUnit':UsdGeom.GetStageMetersPerUnit(stage),'upAxis':str(UsdGeom.GetStageUpAxis(stage)),'boundsMeters':{'min':list(box.GetMin()),'max':list(box.GetMax()),'size':list(box.GetSize())},'glassCorrection':(.96-.0592)/.838,'glassOpacity':.14,'sourceGeometryUnchanged':True,'byteLength':out.stat().st_size,'nativeIPhoneTest':'pending','note':'Modelo conceptual de referencia. No corresponde a las medidas de la calculadora ni a una especificación de instalación.'}
report.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print('HERRAIDEA_AR_EXPORT',json.dumps(data,ensure_ascii=False))
