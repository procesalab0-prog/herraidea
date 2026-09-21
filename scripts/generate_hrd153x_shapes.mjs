import { Shape, Path, ExtrudeGeometry } from '../assets/vendor/three/three.module.js';
const [kind,...args]=process.argv.slice(2);const [w,h,d]=args.map(Number);const s=new Shape();
if(kind.startsWith('profile')){
 // Opposing open glazing channels, with a hollow central chamber.
 const pts=kind==='profilecorner'?[[-.03,-.03],[.03,-.03],[.03,.03],[.008,.03],[.008,.017],[-.008,.017],[-.008,.03],[-.03,.03],[-.03,.008],[-.017,.008],[-.017,-.008],[-.03,-.008]]:[[-.03,-.03],[.03,-.03],[.03,-.008],[.017,-.008],[.017,.008],[.03,.008],[.03,.03],[-.03,.03],[-.03,.008],[-.017,.008],[-.017,-.008],[-.03,-.008]];
 pts.forEach(([x,y],i)=>i?s.lineTo(x,y):s.moveTo(x,y));s.closePath();
 const cavity=kind==='profilecorner'?.013:.024;const hole=new Path();hole.moveTo(-.013,-cavity);hole.lineTo(-.013,cavity);hole.lineTo(.013,cavity);hole.lineTo(.013,-cavity);hole.closePath();s.holes.push(hole);
}else{
 const r=kind==='saddle'?.012:.004;
 s.moveTo(-w/2+r,-h/2);s.lineTo(w/2-r,-h/2);s.quadraticCurveTo(w/2,-h/2,w/2,-h/2+r);s.lineTo(w/2,h/2-r);s.quadraticCurveTo(w/2,h/2,w/2-r,h/2);s.lineTo(-w/2+r,h/2);s.quadraticCurveTo(-w/2,h/2,-w/2,h/2-r);s.lineTo(-w/2,-h/2+r);s.quadraticCurveTo(-w/2,-h/2,-w/2+r,-h/2);
 const holes=kind==='plate'?[[-.041,-.041],[-.041,.041],[.041,-.041],[.041,.041]]:[[-.026,0],[.026,0]];
 for(const [x,y]of holes){const p=new Path();p.absarc(x,y,kind==='plate'?.0045:.003,0,2*Math.PI,true);s.holes.push(p);}
}
const depth=kind.startsWith('profile')?h:d;const g=new ExtrudeGeometry(s,{depth,bevelEnabled:false,steps:1,curveSegments:16});g.translate(0,0,-depth/2);g.rotateX(-Math.PI/2);
if(kind==='saddle'){const p=g.attributes.position;for(let i=0;i<p.count;i++){const z=p.getZ(i);p.setY(i,p.getY(i)+.0254-Math.sqrt(.0254**2-z*z));}g.computeVertexNormals();}
console.log(JSON.stringify({positions:Array.from(g.attributes.position.array),normals:Array.from(g.attributes.normal.array)}));
