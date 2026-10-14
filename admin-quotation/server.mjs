import {createServer} from 'node:http';
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {pathToFileURL} from 'node:url';
import {calculateQuote,configureSystem} from './engine.mjs';
import {configured,makeConfig,checkPassword,issueSession,validSession,sessionSeconds} from './auth.mjs';
const root=new URL('./',import.meta.url),read=p=>JSON.parse(readFileSync(new URL(p,root))),configFile=new URL('.admin-access.json',import.meta.url);
export function createAdminHandler(options={}){
 let config=options.config??(process.env.ADMIN_PASSWORD_HASH?{username:process.env.ADMIN_USERNAME,passwordHash:process.env.ADMIN_PASSWORD_HASH,secret:process.env.ADMIN_SESSION_SECRET}:existsSync(configFile)?JSON.parse(readFileSync(configFile)):null);
 const origin=options.origin||process.env.ADMIN_ORIGIN||'http://127.0.0.1:8768',base=new URL(origin),secure=base.protocol==='https:',cookieName=secure?'__Host-herraidea_admin':'herraidea_admin',attempts=new Map();
 const publicFiles={'/logo.png':['branding/logo.png','image/png'],'/style.css':['style.css','text/css'],'/login.css':['login.css','text/css'],'/login.mjs':['login.mjs','text/javascript'],'/fonts.css':['fuentes/fuentes.css','text/css'],'/manifest.webmanifest':['manifest.webmanifest','application/manifest+json'],'/pwa.mjs':['pwa.mjs','text/javascript'],'/sw.js':['sw.js','text/javascript'],'/share.png':['share.png','image/png'],'/icon-180.png':['icon-180.png','image/png'],'/icon-192.png':['icon-192.png','image/png'],'/icon-512.png':['icon-512.png','image/png']};
 const privateFiles={'/':['index.html','text/html'],'/app.mjs':['app.mjs','text/javascript'],'/pdf-export.mjs':['pdf-export.mjs','text/javascript'],'/pdf-lib.mjs':['pdf-lib.mjs','text/javascript'],'/loading.css':['loading.css','text/css'],'/document-reference.css':['document-reference.css','text/css'],'/intro-logo.png':['branding/intro-logo.png','image/png'],'/pl-palabra.png':['procesalab-palabra-blanco.png','image/png'],'/pl-engrane.png':['procesalab-engrane-blanco.png','image/png'],'/amount-words.mjs':['amount-words.mjs','text/javascript']};
 return async(req,res)=>{
 if(secure)res.setHeader('Strict-Transport-Security','max-age=31536000');res.setHeader('Cache-Control','no-store');res.setHeader('X-Content-Type-Options','nosniff');res.setHeader('X-Robots-Tag','noindex, nofollow');res.setHeader('Referrer-Policy','no-referrer');res.setHeader('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; manifest-src 'self'; worker-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'");
 const send=(status,data)=>{res.writeHead(status,{'Content-Type':'application/json; charset=utf-8'});res.end(JSON.stringify(data));};
 const cookie=(value,maxAge)=>res.setHeader('Set-Cookie',`${cookieName}=${value}; Path=/; HttpOnly; SameSite=Strict; Max-Age=${maxAge}${secure?'; Secure':''}`);
 const redirect=p=>{res.writeHead(303,{Location:p});res.end();};
 const path=new URL(req.url,'http://127.0.0.1').pathname;
 const token=(req.headers.cookie||'').split(';').map(v=>v.trim()).find(v=>v.startsWith(cookieName+'='))?.slice(cookieName.length+1),authed=validSession(config,token);
 const localSetup=!process.env.VERCEL&&!options.config&&!secure&&['127.0.0.1','localhost'].includes(base.hostname)&&['127.0.0.1','::1','::ffff:127.0.0.1'].includes(req.socket.remoteAddress)&&req.headers.host===base.host&&!configured(config);
 const body=async(limit=150000)=>{if(req.headers.origin!==origin)throw Object.assign(Error('Origen no autorizado.'),{status:403});if(req.headers['content-type']!=='application/json')throw Object.assign(Error('Formato inválido.'),{status:415});let text='';for await(const chunk of req){text+=chunk;if(Buffer.byteLength(text)>limit)throw Object.assign(Error('Archivo demasiado grande.'),{status:413});}return JSON.parse(text);};
 try{
 if(req.method==='GET'&&path==='/auth/status')return send(200,{ready:configured(config),setup:localSetup});
 if(req.method==='POST'&&path==='/auth/setup'){
 if(!localSetup)return send(403,{error:'La configuración inicial no está disponible.'});const input=await body(2000),next=makeConfig(input.username,input.password);
 writeFileSync(configFile,JSON.stringify(next),{mode:0o600,flag:'wx'});config=next;cookie(issueSession(config),sessionSeconds);return send(200,{ok:true});}
 if(req.method==='POST'&&path==='/auth/login'){
 const input=await body(2000);if(!configured(config))return send(503,{error:'Acceso sin configurar.'});
 const key=process.env.VERCEL?(req.headers['x-real-ip']||req.socket.remoteAddress):req.socket.remoteAddress,now=Date.now();for(const [k,v] of attempts)if(v.until<now)attempts.delete(k);const row=attempts.get(key)||{count:0,until:now+15*60*1000};row.count++;attempts.set(key,row);if(row.count>5){res.setHeader('Retry-After',Math.ceil((row.until-now)/1000));return send(429,{error:'Demasiados intentos. Espera 15 minutos.'});}
 if(typeof input.username!=='string'||!checkPassword(config,input.username,input.password))return send(401,{error:'Usuario o contraseña incorrectos.'});attempts.delete(key);cookie(issueSession(config),sessionSeconds);return send(200,{ok:true});}
 if(req.method==='POST'&&path==='/auth/logout'){await body(2000);cookie('',0);return send(200,{ok:true});}
 if(req.method==='GET'&&(path==='/login'||path==='/'&&!authed)){const html=readFileSync(new URL('login.html',root),'utf8').replaceAll('{{ORIGIN}}',base.origin);res.writeHead(200,{'Content-Type':'text/html; charset=utf-8'});return res.end(html);}
 if(/^\/archivo(-narrow)?-latin-(400|500|600|700|800|900)-normal\.woff2$/.test(path))publicFiles[path]=['fuentes'+path,'font/woff2'];
 if(path.startsWith('/api/')||privateFiles[path]){if(!authed)return path.startsWith('/api/')?send(401,{error:'Inicia sesión para continuar.'}):redirect('/login');}
 if(req.method==='GET'&&path==='/api/systems'){const m=read('server-data/matrix.json');return send(200,{systems:Object.entries(m.systems).map(([key,s])=>({key,name:s.name}))});}
 if(req.method==='POST'&&['/api/configure','/api/calculate'].includes(path)){const input=await body();return send(200,path==='/api/configure'?configureSystem(input,read('server-data/matrix.json'),read('server-data/cable-rates.json')):calculateQuote(input));}
 const file=publicFiles[path]||privateFiles[path];if(req.method!=='GET'||!file){res.writeHead(404);return res.end('No disponible');}res.writeHead(200,{'Content-Type':file[1]});res.end(readFileSync(new URL(file[0],root)));
 }catch(error){return send(error.status||400,{error:error.status?error.message:'Revisa los datos enviados.'});}
 };
}
export function createAdminServer(options={}){return createServer(createAdminHandler(options));}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href)createAdminServer().listen(8768,'127.0.0.1',()=>console.log('Admin Herraidea: http://127.0.0.1:8768 · acceso privado, sin base de datos.'));
