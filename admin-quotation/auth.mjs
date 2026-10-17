import {scryptSync,randomBytes,timingSafeEqual,createHmac} from 'node:crypto';
const ttl=8*60*60;
export function makeConfig(username,password){if(!/^[a-zA-Z0-9_.-]{3,40}$/.test(username)||typeof password!=='string'||password.length<12||password.length>128)throw Error('Usa un usuario de 3 a 40 letras y una contraseña de 12 a 128 caracteres.');const salt=randomBytes(16).toString('hex');return {username,passwordHash:salt+':'+scryptSync(password,salt,64).toString('hex'),secret:randomBytes(32).toString('hex')};}
export function configured(c){return !!(c&&/^[a-zA-Z0-9_.-]{3,40}$/.test(c.username)&&/^[a-f0-9]{32}:[a-f0-9]{128}$/.test(c.passwordHash)&&typeof c.secret==='string'&&c.secret.length>=64);}
const equal=(a,b)=>{const x=Buffer.from(a),y=Buffer.from(b);return x.length===y.length&&timingSafeEqual(x,y);};
export function checkPassword(c,u,p){if(!configured(c)||typeof p!=='string'||p.length>128)return false;const [salt,hash]=c.passwordHash.split(':');const actual=scryptSync(p,salt,64).toString('hex');return equal(actual,hash)&&equal(u,c.username);}
const sign=(c,p)=>createHmac('sha256',c.secret).update(p).digest('base64url');
export function issueSession(c,now=Date.now()){const p=Buffer.from(JSON.stringify({u:c.username,exp:Math.floor(now/1000)+ttl})).toString('base64url');return p+'.'+sign(c,p);}
export function validSession(c,token,now=Date.now()){if(!configured(c)||typeof token!=='string'||token.length>1000)return false;const [p,s,...rest]=token.split('.');if(rest.length||!s||!equal(s,sign(c,p)))return false;try{const v=JSON.parse(Buffer.from(p,'base64url'));return v.u===c.username&&Number.isInteger(v.exp)&&v.exp>Math.floor(now/1000)&&v.exp<=Math.floor(now/1000)+ttl;}catch{return false;}}
export const sessionSeconds=ttl;
