// A single solid circular plate with three true through-holes, 120 degrees apart.
import { Shape, Path, ExtrudeGeometry } from '../assets/vendor/three/three.module.js';
const [radius, thickness, boltRadius, holeRadius] = process.argv.slice(2).map(Number);
const plate = new Shape();
plate.absarc(0, 0, radius, 0, Math.PI * 2, false);
for (let i = 0; i < 3; i++) {
  const angle = i * Math.PI * 2 / 3;
  const hole = new Path();
  hole.absarc(boltRadius * Math.cos(angle), boltRadius * Math.sin(angle), holeRadius, 0, Math.PI * 2, true);
  plate.holes.push(hole);
}
const geometry = new ExtrudeGeometry(plate, { depth: thickness, bevelEnabled: false, curveSegments: 24, steps: 1 });
geometry.rotateX(-Math.PI / 2);
geometry.translate(0, -thickness / 2, 0);
console.log(JSON.stringify({ positions: Array.from(geometry.attributes.position.array), normals: Array.from(geometry.attributes.normal.array) }));
