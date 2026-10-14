export const RULES_VERSION = 'preview-1';
export function bestDistribution(length) {
  const minSpaces = Math.max(1, Math.ceil(length / 1.4 - 1e-9));
  const maxSpaces = Math.max(1, Math.floor(length / 1.2 + 1e-9));
  const exact = length >= 1.2 - 1e-9 && minSpaces <= maxSpaces;
  const candidates = exact ? Array.from({ length: maxSpaces - minSpaces + 1 }, (_, index) => minSpaces + index) : [minSpaces];
  const spaces = candidates.reduce((best, candidate) => Math.abs(length / candidate - 1.3) < Math.abs(length / best - 1.3) ? candidate : best, candidates[0]);
  return { spaces, spacing: length / spaces, exact };
}
const labels = { final:'Postes finales', central:'Postes centrales', esquina:'Postes de esquina', apoyo:'Apoyos', union_recta:'Uniones rectas', union_esquina:'Uniones de esquina' };
export function buildBom({system, lengths, finish = 'por confirmar', endpoints = 'libres'}, matrix) {
  const config = matrix.systems[system];
  if (!config) throw new Error('Sistema desconocido');
  if (endpoints !== 'libres') throw new Error('Extremos a muro pendientes de validar');
  if (!Array.isArray(lengths) || lengths.length < 1 || lengths.length > 8 || lengths.some(n => typeof n !== 'number' || !Number.isFinite(n) || n < .2 || n > 100 || Math.abs(n*100-Math.round(n*100)) > 1e-7)) throw new Error('Tramos inválidos: de 0.20 a 100 m, máximo ocho, precisión 0.01 m');
  const segments = lengths.map(length => ({length, ...bestDistribution(length)}));
  const spaces = segments.reduce((sum,s) => sum+s.spaces,0);
  const corners = lengths.length-1;
  const counts = config.kind === 'posts' ? {final:2, central:spaces-1-corners, esquina:corners} : {apoyo:2*spaces, union_recta:spaces-lengths.length, union_esquina:corners};
  const items = Object.entries(counts).filter(([,quantity])=>quantity>0).map(([role,quantity])=>({id:system+'.'+role,role,label:labels[role],quantity,unit:'pieza',price:null,status:'por validar'}));
  const unresolvedItems = config.items.filter(row => !row.approved).map(row=>({id:row.id,reason:row.pending.join('; ')}));
  const warnings = ['Despiece preliminar pendiente de validación de Herraidea.'];
  if (segments.some(s=>!s.exact)) warnings.push('Separación fuera del rango orientativo de 1.20 a 1.40 m.');
  const configuration = {system, lengths:[...lengths], finish, endpoints};
  // A deterministic reference for the same inputs, not a unique order identifier.
  const configurationId = [RULES_VERSION,system,lengths.map(n=>n.toFixed(2)).join('-'),encodeURIComponent(finish),endpoints].join(':');
  return {configurationId,schemaVersion:1,rulesVersion:RULES_VERSION,configuration,segments,items,referenceOnly:system==='cable'||system==='tubo'?[]:[{type:'cristal',quantity:spaces,sold:false,dimensionsStatus:'Orientativas; validar antes de fabricar'}],geometricRequirements:{pasamanosMeters:config.kind==='posts'?lengths.reduce((a,b)=>a+b,0):0,...(system==='cable'?{cableLines:7,cableMeters:Math.round(lengths.reduce((a,b)=>a+b,0)*100)*7/100,cableSupplyMeters:Math.ceil(Math.round(lengths.reduce((a,b)=>a+b,0)*100)*7*(1+(config.completeSystem?.cableAllowance?.rate||0))-1e-8)/100,cableAllowanceRate:config.completeSystem?.cableAllowance?.rate||0,cableAllowanceStatus:'provisional'}:{})},warnings,unresolvedItems,purchaseEligible:false,priceStatus:'pending',exclusion:'Cristal no incluido; se adquiere por separado'};
}
export function summarizeBom(bom) {
  return [bom.configuration.system, ...bom.items.map(i=>`${i.label}: ${i.quantity}`), 'Precio pendiente', bom.exclusion, ...bom.warnings].join('\n');
}
