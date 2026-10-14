import {completeSystem} from './lib/complete-system.mjs';
const clean=(v,n)=>String(v??'').trim().slice(0,n);
const number=(v,min,max,label)=>{if(typeof v!=='number'||!Number.isFinite(v)||v<min||v>max)throw Error(label+' fuera de rango.');return v;};
export function validateQuote(raw){
 if(raw?.kind!=='herraidea_admin_quote'||raw.version!==1||!Array.isArray(raw.lines)||raw.lines.length>100)throw Error('Archivo de cotización inválido.');
 const lines=raw.lines.map((l,i)=>({id:String(i+1),description:clean(l.description,500)||'Concepto especial',quantity:number(l.quantity,0.01,100000,'Cantidad'),unit:clean(l.unit,20)||'servicio',priceCents:l.priceCents===null?null:Math.round(number(l.priceCents,0,1000000000,'Precio'))}));
 return {kind:'herraidea_admin_quote',version:1,folio:clean(raw.folio,60),date:/^\d{4}-\d{2}-\d{2}$/.test(raw.date||'')?raw.date:'',validDays:Math.round(number(raw.validDays,1,365,'Vigencia')),client:{name:clean(raw.client?.name,120),company:clean(raw.client?.company,120),contact:clean(raw.client?.contact,150),location:clean(raw.client?.location,200)},project:clean(raw.project,120),notes:clean(raw.notes,4000),priceBasis:['included','excluded'].includes(raw.priceBasis)?raw.priceBasis:'included',taxRate:number(raw.taxRate,0,50,'IVA'),discountRate:number(raw.discountRate,0,100,'Descuento'),lines};
}
export function calculateQuote(raw){const quote=validateQuote(raw),pending=quote.lines.some(l=>l.priceCents===null),sum=quote.lines.reduce((s,l)=>s+Math.round(l.quantity*(l.priceCents??0)),0);if(!Number.isSafeInteger(sum)||sum>10000000000)throw Error('Importe total fuera de rango.');
 const discount=Math.round(sum*quote.discountRate/100),after=sum-discount;
 const subtotal=quote.priceBasis==='included'?Math.round(after/(1+quote.taxRate/100)):after;
 const tax=quote.priceBasis==='included'?after-subtotal:Math.round(subtotal*quote.taxRate/100);
 return {quote,totals:{beforeDiscountCents:sum,discountCents:discount,subtotalCents:subtotal,taxCents:tax,totalCents:subtotal+tax,pending,empty:!quote.lines.length}};
}
export function configureSystem(input,matrix,rates){
 const system=completeSystem({system:input.system,lengths:input.lengths,finish:input.finish},matrix,{quantity:input.quantity,installation:'nivel'});
 const allowance=number(input.allowance,0,50,'Extra de cable')/100;
 const priced=input.system==='cable'&&['satin','negro'].includes(input.finish);
 const prefix=matrix.systems[input.system].name+' · '+(input.finish==='negro'?'Negro':'Satinado');
 const lines=system.positions.map(p=>({description:prefix+' · '+p.label+(priced?' · pasamanos incluido':''),quantity:p.quantity,unit:'pieza',priceCents:priced?rates.postCents[input.finish][p.role]??null:null}));
 if(input.system==='cable'){const base=Math.round(input.lengths.reduce((a,b)=>a+b,0)*100)*7;const meters=Math.ceil(base*(1+allowance)-1e-8)/100*input.quantity;lines.push({description:'Cable de acero inoxidable · 7 líneas · extra '+input.allowance+'%',quantity:meters,unit:'m',priceCents:rates.cableCentsPerMeter});}
 return {title:prefix,lengths:input.lengths,lines,warnings:[...system.reviewReasons,system.exclusion,...(input.system==='cable'?['Los herrajes forman parte del sistema completo. Extra de cable editable; revisar cortes y suministro.']:['Completar precios de este sistema.'])],spaces:system.bom.spaces,meters:input.lengths.reduce((a,b)=>a+b,0)*input.quantity};
}
