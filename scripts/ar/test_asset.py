"""Checks the distributable USDZ and its source/scale manifest, with stdlib only."""
import hashlib,json,struct,unittest,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class HRD1525AR(unittest.TestCase):
 def test_package_alignment_and_source(self):
  data=json.loads((ROOT/'content/projects/clip-system/ar-manifest.json').read_text())
  asset=ROOT/data['asset'];source=ROOT/data['source']
  self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),data['sourceSha256'])
  self.assertEqual(hashlib.sha256(asset.read_bytes()).hexdigest(),data['assetSha256'])
  with zipfile.ZipFile(asset) as z:
   self.assertTrue(z.namelist()[0].endswith(('.usdc','.usda')))
   with asset.open('rb') as f:
    for entry in z.infolist():
     self.assertEqual(entry.compress_type,zipfile.ZIP_STORED)
     f.seek(entry.header_offset+26);name_len,extra_len=struct.unpack('<HH',f.read(4))
     self.assertEqual((entry.header_offset+30+name_len+extra_len)%64,0)
 def test_reference_scope_and_units(self):
  data=json.loads((ROOT/'content/projects/clip-system/ar-manifest.json').read_text())
  self.assertEqual(data['sourceMeshes'],data['exportedMeshes'])
  self.assertEqual(data['exportedMeshes'],46)
  self.assertEqual(data['metersPerUnit'],1)
  self.assertEqual(data['upAxis'],'Y')
  self.assertEqual(data['nativeIPhoneTest'],'user_confirmed')
  self.assertAlmostEqual(data['boundsMeters']['size'][0],1.11,places=3)
  self.assertAlmostEqual(data['boundsMeters']['min'][1],0,places=6)
  self.assertEqual(data['arkitCompliance']['failedChecks'],[])
class HRD1616AR(unittest.TestCase):
 def test_reference_and_integrity(self):
  data=json.loads((ROOT/'content/projects/hrd-1616/ar-manifest.json').read_text())
  for key,sha in [('source','sourceSha256'),('asset','assetSha256')]:
   self.assertEqual(hashlib.sha256((ROOT/data[key]).read_bytes()).hexdigest(),data[sha])
  self.assertEqual(data['exportedMeshes'],93)
  self.assertEqual(data['cablesPerSide'],7)
  self.assertEqual(data['metersPerUnit'],1)
  self.assertEqual(data['upAxis'],'Y')
  self.assertAlmostEqual(data['boundsMeters']['min'][1],0,places=6)
  self.assertAlmostEqual(data['boundsMeters']['size'][0],1.285,places=3)
  self.assertEqual(data['arkitCompliance']['errors'],[])
  self.assertEqual(data['arkitCompliance']['failedChecks'],[])
  asset=ROOT/data['asset']
  with zipfile.ZipFile(asset) as z, asset.open('rb') as f:
   for entry in z.infolist():
    self.assertEqual(entry.compress_type,zipfile.ZIP_STORED)
    f.seek(entry.header_offset+26);n,e=struct.unpack('<HH',f.read(4))
    self.assertEqual((entry.header_offset+30+n+e)%64,0)
class RemainingRailingAR(unittest.TestCase):
 def test_all_sources_packages_and_units(self):
  registry=json.loads((ROOT/'ar/systems.json').read_text())
  self.assertEqual(len(registry),8)
  module=(ROOT/'ar/systems.js').read_text().removeprefix('export const systems = ').strip().removesuffix(';')
  self.assertEqual(json.loads(module),registry)
  for key in registry.keys()-{'clips','hrd1616'}:
   with self.subTest(system=key):
    data=json.loads((ROOT/f'content/projects/ar/{key}.json').read_text())
    asset=ROOT/data['asset'];source=ROOT/data['source']
    self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),data['sourceSha256'])
    self.assertEqual(hashlib.sha256(asset.read_bytes()).hexdigest(),data['assetSha256'])
    self.assertEqual(data['sourceMeshes'],data['exportedMeshes'])
    self.assertGreater(data['exportedMeshes'],0)
    if key=='hrd1220':
     self.assertEqual(data['source'],'assets/projects/hrd-1220/hrd-1220.glb')
     self.assertEqual(data['exportedMeshes'],43)
     self.assertEqual(set(data['glassMeshNames']),{'Cristal_left','Cristal_right'})
     self.assertEqual(len(data['upperConnectorMeshNames']),5)
    self.assertEqual(data['metersPerUnit'],1)
    self.assertEqual(data['upAxis'],'Y')
    self.assertAlmostEqual(data['boundsMeters']['min'][1],0,places=6)
    self.assertEqual(data['arkitCompliance']['errors'],[])
    self.assertEqual(data['arkitCompliance']['failedChecks'],[])
    self.assertTrue((ROOT/'ar'/registry[key]['slug']/'index.html').exists())
    with zipfile.ZipFile(asset) as z,asset.open('rb') as f:
     self.assertTrue(z.namelist()[0].endswith(('.usdc','.usda')))
     for e in z.infolist():
      self.assertEqual(e.compress_type,zipfile.ZIP_STORED)
      f.seek(e.header_offset+26);n,x=struct.unpack('<HH',f.read(4))
      self.assertEqual((e.header_offset+30+n+x)%64,0)
if __name__=='__main__':unittest.main()
