const finite=(x,min,max)=>typeof x==='number'&&Number.isFinite(x)&&x>=min&&x<=max;
const text=(x,max=160)=>String(x??'').trim().slice(0,max);
const optional=(x,min=0,max=1e9)=>{if(x===null||x===undefined||x==='')return null;if(!finite(x,min,max))throw Error('Valor de fabricación fuera de rango.');return x;};
const shapes=['solid','tube','plate','sheet','custom'];
export function validateFabrication(raw){
 if(!raw||raw.kind!=='herraidea_fabrication'||raw.version!==1||!Array.isArray(raw.parts)||raw.parts.length>50||!Array.isArray(raw.accessories)||raw.accessories.length>100)throw Error('Armado de fabricación inválido.');
 const process=p=>{if(!['piece','minute','cut_mm','surface_mm2'].includes(p.unit))throw Error('Unidad de proceso inválida.');return {name:text(p.name),unit:p.unit,amount:optional(p.amount),rate:optional(p.rate)};};
 const parts=raw.parts.map(p=>{if(!shapes.includes(p.shape)||!['mm','m','mm2','m2','kg','piece'].includes(p.rateUnit)||!Array.isArray(p.processes)||p.processes.length>12)throw Error('Pieza de fabricación inválida.');const o={name:text(p.name),material:text(p.material),shape:p.shape,quantity:optional(p.quantity,.01,100000),rateUnit:p.rateUnit,rate:optional(p.rate),wastePercent:optional(p.wastePercent,0,100),processes:p.processes.map(process)};for(const k of ['length','diameter','wall','width','thickness','area','perimeter','weight'])o[k]=optional(p[k],0,1e9);return o;});
 return {example:raw.example===true,kind:'herraidea_fabrication',version:1,name:text(raw.name),quantity:optional(raw.quantity,1,100000),markupPercent:optional(raw.markupPercent,0,1000),parts,accessories:raw.accessories.map(a=>({name:text(a.name),quantity:optional(a.quantity,.01,100000),rate:optional(a.rate)}))};
}
export function calculateFabrication(raw){
 const input=validateFabrication(raw),missing=[],costs=[];let knownCents=0;
 const need=(condition,message)=>{if(!condition)missing.push(message);return condition;};
 need(input.name,'Escribe el nombre del herraje.');need(input.quantity!==null,'Indica cuántos herrajes necesitas.');need(input.markupPercent!==null,'Indica el recargo sobre costo, incluso si es 0%.');need(input.parts.length+input.accessories.length>0,'Agrega piezas o accesorios al herraje.');
 for(const [i,p] of input.parts.entries()){
  const label=p.name||'Pieza '+(i+1);let valid=true;const check=(ok,message)=>{if(!need(ok,label+': '+message))valid=false;};
  check(Boolean(p.material),'indica el material.');check(p.quantity!==null,'indica la cantidad por herraje.');check(p.wastePercent!==null,'indica la merma del material, incluso si es 0%.');check(p.rate!==null,'falta el precio de materia prima.');
  let area=null,perimeter=null,volume=null;
  if(['solid','tube'].includes(p.shape)){check(p.length>0,'indica la longitud en mm.');check(p.diameter>0,'indica el diámetro exterior en mm.');if(p.shape==='tube')check(p.wall>0&&p.wall*2<p.diameter,'el espesor debe ser mayor que cero y menor que el radio exterior.');const inner=p.shape==='tube'?p.diameter-2*p.wall:0;if(p.length>0&&p.diameter>0&&(p.shape==='solid'||p.wall>0&&inner>0))volume=Math.PI/4*(p.diameter**2-inner**2)*p.length;}
  if(['plate','sheet'].includes(p.shape)){check(p.length>0&&p.width>0,'indica largo y ancho en mm.');check(p.thickness>0,'indica el espesor en mm.');if(p.length>0&&p.width>0){area=p.length*p.width;perimeter=2*(p.length+p.width);if(p.thickness>0)volume=area*p.thickness;}}
  if(p.shape==='custom'){check(p.area>0,'indica el área real en mm².');check(p.thickness>0,'indica el espesor en mm.');area=p.area;perimeter=p.perimeter;volume=area!==null&&p.thickness>0?area*p.thickness:null;}
  const consumed=p.rateUnit==='mm'?p.length:p.rateUnit==='m'?(p.length===null?null:p.length/1000):p.rateUnit==='mm2'?area:p.rateUnit==='m2'?(area===null?null:area/1e6):p.rateUnit==='kg'?p.weight:1;
  check(!['mm2','m2'].includes(p.rateUnit)||['plate','sheet','custom'].includes(p.shape),'la tarifa por área se aplica a placa o lámina.');
  check(consumed!==null&&consumed>0,p.rateUnit==='kg'?'indica el peso de materia prima por pieza en kg.':'falta el consumo para la tarifa seleccionada.');
  const rawMaterialCents=valid?consumed*p.rate*100*(1+p.wastePercent/100):null,materialCents=rawMaterialCents===null?null:Math.round(rawMaterialCents);
  let processesCents=0,processPending=false;const processes=[];
  for(const [j,process] of p.processes.entries()){const name=process.name||'Proceso '+(j+1),amount=process.unit==='piece'?1:process.unit==='cut_mm'?perimeter:process.amount;
   const ok=need(Boolean(process.name),label+': nombra el proceso '+(j+1)+'.')&need(process.rate!==null,label+' · '+name+': falta tarifa.')&need(amount!==null&&amount>0,label+' · '+name+': indica consumo o duración.');
   const rawCents=ok?amount*process.rate*100:null,cents=rawCents===null?null:Math.round(rawCents);if(cents===null)processPending=true;else processesCents+=rawCents;processes.push({name,amount,cents});
  }
  const cents=materialCents!==null&&!processPending&&p.quantity!==null?Math.round((rawMaterialCents+processesCents)*p.quantity):null;
  if(cents!==null)knownCents+=cents;costs.push({name:label,quantity:p.quantity,areaMm2:area,cutMm:perimeter,volumeMm3:volume,materialCents,processes,cents});
 }
 const accessories=input.accessories.map((a,i)=>{const ok=need(Boolean(a.name),'Nombra el accesorio '+(i+1)+'.')&need(a.quantity!==null,'Indica cantidad del accesorio '+(i+1)+'.')&need(a.rate!==null,'Falta precio del accesorio '+(i+1)+'.');const cents=ok?Math.round(a.quantity*a.rate*100):null;if(cents!==null)knownCents+=cents;return {...a,cents};});
 if(!Number.isSafeInteger(knownCents)||knownCents>1e10)throw Error('Costo de fabricación fuera de rango.');
 const ready=missing.length===0,unitCostCents=ready?knownCents:null,unitPriceCents=ready?Math.round(knownCents*(1+input.markupPercent/100)):null;
 if(unitPriceCents!==null&&(!Number.isSafeInteger(unitPriceCents)||unitPriceCents>1e9||unitPriceCents*input.quantity>1e10))throw Error('Precio de fabricación fuera de rango.');
 return {input,ready,missing:[...new Set(missing)],costs,accessories,knownCents,unitCostCents,unitPriceCents,totalPriceCents:ready?Math.round(unitPriceCents*input.quantity):null,priceBasis:'excluded'};
}
