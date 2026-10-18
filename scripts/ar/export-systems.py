"""Blender --background --python scripts/ar/export-systems.py
Export the remaining six railing references; keep the already tested 1525/1616 assets untouched.
"""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from pxr import Usd,UsdGeom,UsdUtils
ROOT=Path(__file__).resolve().parents[2]
systems=json.loads((ROOT/'ar/systems.json').read_text())
for key,config in systems.items():
 if key in ('clips','hrd1616'):continue
 source=ROOT/'assets/projects'/config['source'];out=ROOT/config['asset'].lstrip('/');out.parent.mkdir(parents=True,exist_ok=True)
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.gltf(filepath=str(source));scene=bpy.context.scene;scene.frame_set(0);bpy.context.view_layer.update()
 transforms={o:o.matrix_world.copy() for o in scene.objects}
 for o in scene.objects:o.animation_data_clear()
 for o in scene.objects:o.parent=None;o.matrix_world=transforms[o]
 for a in list(bpy.data.actions):bpy.data.actions.remove(a)
 meshes=[o for o in scene.objects if o.type=='MESH']
 for o in list(scene.objects):
  if o.type!='MESH':bpy.data.objects.remove(o,do_unlink=True)
 # glTF transmission alone is not portable to Quick Look. Preserve tint with Preview Surface alpha.
 glass=[]
 for m in bpy.data.materials:
  if not m.use_nodes:continue
  bsdf=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
  if bsdf and any(t in m.name.lower() for t in ('vidrio','cristal')):
   bsdf.inputs['Alpha'].default_value=.14;bsdf.inputs['Transmission Weight'].default_value=0;bsdf.inputs['Roughness'].default_value=.09;bsdf.inputs['Metallic'].default_value=0
   m.surface_render_method='DITHERED';glass.append(m.name)
 bpy.context.view_layer.update()
 points=[o.matrix_world@Vector(v) for o in meshes for v in o.bound_box]
 lo=Vector([min(v[i] for v in points) for i in range(3)]);hi=Vector([max(v[i] for v in points) for i in range(3)])
 shift=Matrix.Translation(Vector((-(lo.x+hi.x)/2,-(lo.y+hi.y)/2,-lo.z)))
 for o in meshes:o.matrix_world=shift@o.matrix_world;o.select_set(True)
 scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
 bpy.ops.wm.usd_export(filepath=str(out),selected_objects_only=True,export_animation=False,export_materials=True,generate_preview_surface=True,generate_materialx_network=False,convert_orientation=True,export_global_forward_selection='NEGATIVE_Z',export_global_up_selection='Y',export_lights=False,export_cameras=False,triangulate_meshes=True,root_prim_path='/Herraidea_'+key,convert_scene_units='METERS',meters_per_unit=1)
 stage=Usd.Stage.Open(str(out));cache=UsdGeom.BBoxCache(Usd.TimeCode.Default(),[UsdGeom.Tokens.default_,UsdGeom.Tokens.render]);box=cache.ComputeWorldBound(stage.GetPseudoRoot()).ComputeAlignedRange();exported=[p for p in stage.Traverse() if p.IsA(UsdGeom.Mesh)]
 checker=UsdUtils.ComplianceChecker(arkit=True);checker.CheckCompliance(str(out))
 data=dict(code=config['title'],profile=key,source=str(source.relative_to(ROOT)),asset=str(out.relative_to(ROOT)),sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),assetSha256=hashlib.sha256(out.read_bytes()).hexdigest(),sourceMeshes=len(meshes),exportedMeshes=len(exported),metersPerUnit=UsdGeom.GetStageMetersPerUnit(stage),upAxis=str(UsdGeom.GetStageUpAxis(stage)),boundsMeters=dict(min=list(box.GetMin()),max=list(box.GetMax()),size=list(box.GetSize())),glassMaterials=glass,byteLength=out.stat().st_size,nativeIPhoneTest='pending',arkitCompliance=dict(errors=checker.GetErrors(),failedChecks=checker.GetFailedChecks(),warnings=checker.GetWarnings()),kind='assembled_reference',note='Modelo del visor, no configuración calculada ni especificación de instalación.')
 report=ROOT/'content/projects/ar'/f'{key}.json';report.parent.mkdir(parents=True,exist_ok=True);report.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 assert len(meshes)==len(exported);assert not checker.GetErrors() and not checker.GetFailedChecks(),data
 assert abs(box.GetMin()[1])<1e-5;assert data['metersPerUnit']==1 and data['upAxis']=='Y'
 print('AR_EXPORT_OK',key,len(meshes),list(box.GetSize()),out.stat().st_size,flush=True)
