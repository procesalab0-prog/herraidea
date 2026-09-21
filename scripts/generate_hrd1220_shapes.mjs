import { Shape, Path, ExtrudeGeometry } from '../assets/vendor/three/three.module.js';
const [kind,...args]=process.argv.slice(2); const [w,h,d]=args.map(Number);
const r=kind==='base'||kind==='cover'?.006:.0015;
const s=new Shape();
s.moveTo(-w/2+r,-h/2);s.lineTo(w/2-r,-h/2);s.quadraticCurveTo(w/2,-h/2,w/2,-h/2+r);s.lineTo(w/2,h/2-r);s.quadraticCurveTo(w/2,h/2,w/2-r,h/2);s.lineTo(-w/2+r,h/2);s.quadraticCurveTo(-w/2,h/2,-w/2,h/2-r);s.lineTo(-w/2,-h/2+r);s.quadraticCurveTo(-w/2,-h/2,-w/2+r,-h/2);
if(kind==='base')for(const x of [-.04,.04])for(const y of [-.04,.04]){const p=new Path();p.absarc(x,y,.004,0,Math.PI*2,true);s.holes.push(p);}
if(kind==='cover'){const p=new Path();p.moveTo(-.026,-.025);p.lineTo(-.026,.025);p.lineTo(.026,.025);p.lineTo(.026,-.025);p.closePath();s.holes.push(p);}
if(kind==='jaw')for(const [y,radius] of [[-.0505,.006],[.0185,.0028]]){const p=new Path();p.absarc(0,y,radius,0,Math.PI*2,true);s.holes.push(p);}
const g=new ExtrudeGeometry(s,{depth:d,bevelEnabled:false,curveSegments:12,steps:1});
g.translate(0,0,-d/2);
if(kind==='base'||kind==='cover')g.rotateX(-Math.PI/2);
console.log(JSON.stringify({positions:Array.from(g.attributes.position.array),normals:Array.from(g.attributes.normal.array)}));
