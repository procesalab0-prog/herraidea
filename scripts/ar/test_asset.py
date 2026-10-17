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
  self.assertEqual(data['nativeIPhoneTest'],'pending')
  self.assertAlmostEqual(data['boundsMeters']['size'][0],1.11,places=3)
  self.assertAlmostEqual(data['boundsMeters']['min'][1],0,places=6)
  self.assertEqual(data['arkitCompliance']['failedChecks'],[])
if __name__=='__main__':unittest.main()
