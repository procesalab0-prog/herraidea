import {buildBom} from './bom.mjs';
export function completeSystem(configuration, matrix, {quantity=1, installation='nivel'}={}) {
  if (!Number.isInteger(quantity)||quantity<1||quantity>20) throw new Error('Cantidad inválida');
  if (!['nivel','escalera'].includes(installation)) throw new Error('Instalación inválida');
  const bom=buildBom(configuration,matrix), policy=matrix.systems[configuration.system].completeSystem;
  const positions=bom.items.flatMap(item=>item.role==='final' ? [{role:'inicio',label:'Postes de inicio',quantity:quantity},{role:'final',label:'Postes finales',quantity:quantity}] : [{role:item.role,label:item.label,quantity:item.quantity*quantity}]);
  const reviewReasons=[];
  if(configuration.lengths.length>1)reviewReasons.push('Esquinas: requiere revisión de Herraidea.');
  const unavailable=configuration.system==='cable' && installation==='escalera';
  if(installation==='escalera')reviewReasons.push(unavailable?'HRD 1616 inclinado no disponible por el momento; requiere herraje articulado pendiente de importación.':'Escaleras: requiere revisión de Herraidea; la vista y las cantidades corresponden al recorrido sin inclinación.');
  if(bom.segments.some(s=>!s.exact))reviewReasons.push('Separación fuera del rango orientativo: requiere revisión de Herraidea.');
  if(!policy?.contentsConfirmed)reviewReasons.push('Contenido del sistema pendiente de confirmar para esta familia.');
  return {key:`system.${configuration.system}`,title:`${matrix.systems[configuration.system].name} · Sistema completo`,quantity,installation,configuration:bom.configuration,configurationId:bom.configurationId,positions,
    included:policy?.contentsConfirmed ? [...policy.included] : [],contentsConfirmed:Boolean(policy?.contentsConfirmed),
    exclusion:configuration.system==='cable'||configuration.system==='tubo'?'Este sistema no requiere cristal.':'Cristal no incluido; se adquiere por separado.',
    availability:unavailable?'unavailable':'pending_confirmation',reviewReasons,requiresReview:reviewReasons.length>0,price:null,purchaseEligible:false,
    cableRequirements:configuration.system==='cable'?{baseMeters:bom.geometricRequirements.cableMeters*quantity,supplyMeters:bom.geometricRequirements.cableSupplyMeters*quantity,allowanceRate:policy.cableAllowance.rate,allowanceStatus:'provisional',independentRuns:configuration.lengths.length*7*quantity,endConnections:configuration.lengths.length*14*quantity}:null,
    deliveryNote:configuration.system==='cable'?policy.deliveryRule+' · Margen de cable del 10% provisional, pendiente de validación.':'Entrega, cortes y largos por confirmar.',bom};
}
export function prepareSystemCatalog(matrix) {
  return {mode:'LOCAL_REVIEW',checkoutEnabled:false,products:Object.keys(matrix.systems).map(system=>{
    const policy=matrix.systems[system].completeSystem;
    return {internalKey:`system.${system}`,title:`${matrix.systems[system].name} · Sistema completo`,status:'DRAFT',unit:'sistema configurado',price:null,sku:null,shopifyVariantId:null,purchaseEligible:false,
      description:policy?.contentsConfirmed?`Sistema completo configurado según las medidas del proyecto. Incluye ${policy.included.join(', ')}. Siete líneas de cable. Precio y entrega por confirmar.`:'Sistema de barandal configurado según las medidas del proyecto. Contenido y compatibilidad pendientes de revisión.',
      included:policy?.contentsConfirmed?[...policy.included]:[],contentsConfirmed:Boolean(policy?.contentsConfirmed),
      internalPostNames:policy?.postNames||null,pricingMethod:policy?.pricingMethod||null,
      pending:['Precio del conjunto','Entrega y cortes','Configuraciones de esquina y escalera',...(!policy?.contentsConfirmed?['Contenido del sistema']:[])],
      glassSold:false,componentsAreNotSeparateProducts:true};
  })};
}
