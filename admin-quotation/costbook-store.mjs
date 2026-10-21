import {readFile,writeFile,rename,mkdir,open,unlink} from 'node:fs/promises';
import {dirname} from 'node:path';
import {createHash,randomUUID} from 'node:crypto';
const path='herraidea-private/costbook-v1.json';
const error=(message,status=400)=>Object.assign(new Error(message),{status});
export const emptyBook=()=>({kind:'herraidea_costbook',version:1,revision:0,updatedAt:null,items:[],history:[],references:[]});
const hash=b=>createHash('sha256').update(b).digest('hex');
export function createCostbookStore({file=process.env.ADMIN_COSTBOOK_FILE,blob,token=process.env.BLOB_READ_WRITE_TOKEN}={}){
 const configured=Boolean(file||token||blob);
 const sdk=async()=>blob||await import('@vercel/blob');
 return {configured,mode:file?'local':configured?'shared':'unconfigured',
 async read(){if(!configured)return {book:emptyBook(),etag:null};
  if(file){try{const bytes=await readFile(file,'utf8');return {book:JSON.parse(bytes),etag:hash(bytes)};}catch(e){if(e.code==='ENOENT')return {book:emptyBook(),etag:null};throw e;}}
  const result=await(await sdk()).get(path,{access:'private',token,useCache:false});if(!result)return {book:emptyBook(),etag:null};
  if(result.statusCode!==200||!result.stream)throw error('No se pudo leer la lista compartida.',503);
  const bytes=await new Response(result.stream).text();return {book:JSON.parse(bytes),etag:result.blob.etag};
 },
 async write(book,etag){if(!configured)throw error('El almacenamiento compartido todavía no está conectado.',503);const bytes=JSON.stringify(book);if(Buffer.byteLength(bytes)>5000000)throw error('La lista requiere respaldo antes de agregar más historial.',413);
  if(file){await mkdir(dirname(file),{recursive:true});let lock;
   for(let n=0;n<20;n++){try{lock=await open(file+'.lock','wx');break;}catch(e){if(e.code!=='EEXIST')throw e;await new Promise(r=>setTimeout(r,20));}}
   if(!lock)throw error('Hay otro guardado en curso. Intenta de nuevo.',409);
   let tmp;try{const current=await this.read();if(current.etag!==etag)throw error('Otro administrador cambió la lista. Recarga antes de guardar.',409);tmp=file+'.'+randomUUID()+'.tmp';await writeFile(tmp,bytes,{mode:0o600});await rename(tmp,file);return {book,etag:hash(bytes)};}finally{await lock.close();await unlink(file+'.lock').catch(()=>{});if(tmp)await unlink(tmp).catch(()=>{});}}
  try{const r=await(await sdk()).put(path,bytes,{access:'private',token,contentType:'application/json',addRandomSuffix:false,allowOverwrite:etag!==null,...(etag!==null?{ifMatch:etag}:{}),cacheControlMaxAge:60});return {book,etag:r.etag};}
  catch(e){if(['BlobPreconditionFailedError','BlobAlreadyExistsError'].includes(e.constructor?.name)||['BlobPreconditionFailedError','BlobAlreadyExistsError'].includes(e.name))throw error('Otro administrador cambió la lista. Recarga antes de guardar.',409);throw error('No se confirmó el guardado compartido. Revisa la conexión y recarga la lista.',503);}
 }};
}
export function editCostbook(current,input,actor='Herraidea'){
 if(input?.revision!==current.revision)throw error('La lista cambió. Recarga antes de guardar.',409);
 const v=input.item;if(!v||typeof v!=='object')throw error('Material inválido.');const clean=(x,n=180)=>String(x??'').trim().slice(0,n);
 const num=(x,min,max,nullable=false)=>{if(nullable&&(x===null||x===''))return null;if(typeof x!=='number'||!Number.isFinite(x)||x<min||x>max)throw error('Revisa precio, unidad de compra y cantidad.');return x;};
 const id=clean(v.id,80)||randomUUID();if(!/^[\w-]{1,80}$/.test(id))throw error('Identificador inválido.');
 const old=current.items.find(m=>m.id===id);if(!old&&current.items.length>=2000)throw error('Máximo 2000 materiales.');
 const item={id,name:clean(v.name),supplier:clean(v.supplier),unit:v.unit,stockQuantity:num(v.stockQuantity,.000001,1e12),price:num(v.price,0,1e9,true),taxBasis:v.taxBasis,taxRate:num(v.taxRate,0,50),status:v.status,effectiveDate:clean(v.effectiveDate,10),source:old?.source??null,updatedAt:new Date().toISOString()};
 if(!item.name||!['mm','m','mm2','m2','kg','piece'].includes(item.unit)||!['unknown','included','excluded'].includes(item.taxBasis)||!['pending','active'].includes(item.status)||(item.effectiveDate!==''&&!/^\d{4}-\d{2}-\d{2}$/.test(item.effectiveDate)))throw error('Completa nombre, unidad, fecha y tratamiento de IVA.');
 if(item.status==='active'&&(item.price===null||item.taxBasis==='unknown'||!item.effectiveDate))throw error('Confirma el precio y si incluye IVA antes de activar el material.');
 return {...current,revision:current.revision+1,updatedAt:item.updatedAt,items:old?current.items.map(m=>m.id===id?item:m):[...current.items,item],history:[...current.history,{revision:current.revision+1,at:item.updatedAt,actor:clean(actor,80),before:old??null,after:item}]};
}
export function materialRate(item){if(!item||item.status!=='active'||item.price===null||item.taxBasis==='unknown'||!item.effectiveDate)throw error('Revisa y activa el material antes de usarlo.');const net=item.taxBasis==='included'?item.price/(1+item.taxRate/100):item.price;return net/item.stockQuantity;}
