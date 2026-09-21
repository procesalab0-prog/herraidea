# HRD 1223 — estudio de soleras planas

## Fuente y elección

El usuario eligió el 21 de septiembre de 2026 **soleras planas como las fotografías instaladas**, en lugar del poste circular de la lámina HRD 1223. La tercera fotografía es la referencia principal: dos soleras, eje transversal, brazos hacia el vidrio, discos con juntas y vela para pasamanos. Las imágenes fueron visibles en la conversación; sus rutas temporales de Fotos ya no estaban disponibles para copiarlas. No se modifica la ficha comercial existente HRD 1223 INICIO, que corresponde al poste circular.

## Alcance de esta entrega

- `assets/projects/hrd-1223/hrd-1223-soleras.glb`: 51 componentes/elementos, 51 pistas de traslación en la animación `Despiece` (0–3 segundos), metros, eje Y vertical.
- `scripts/generate_hrd1223.py`: fuente paramétrica reproducible sin dependencias externas.
- `portada-soleras.png`: render del mismo modelo, no fotografía de producto.
- Dos soleras independientes, separadores, fijaciones simplificadas, soporte superior, cuatro brazos, articulaciones, discos, juntas, tapas y contexto de vidrio/pasamanos.
- El despiece es explicativo. No define secuencia de desmontaje, número comercial de piezas ni detalles internos reales.
- La calculadora utiliza una sola geometría de poste por posición, con brazos de un lado en los extremos y de ambos en los intermedios; la esquina utiliza un cuerpo compartido y brazos orientados por tramo.

## Medidas de trabajo, NO confirmadas para esta variante

La lámina de **poste circular** muestra 900 mm de cuerpo, 210 mm al eje inferior y 570 mm entre ejes. Solo se utilizan como proporción provisional del estudio de soleras; no prueban las medidas de la pieza fotografiada.

| Parámetro | Valor de estudio |
|---|---:|
| Soleras | 900 × 50 × 8 mm cada una |
| Distancia entre centros de soleras | 28 mm |
| Ejes de brazos | 210 / 780 mm |
| Ejes de discos respecto al centro del poste | ±112 mm |
| Separación del plano de vidrio respecto al poste | 120 mm |
| Diámetro de discos | 46 mm |
| Vidrio de contexto | 12 mm |
| Pasamanos de contexto | Ø50.8 mm |

La pequeña placa inferior representa un apoyo provisional; no reconstruye el anclaje oculto de las fotografías. Los tornillos son simplificados y sin roscas. El vidrio no incluye perforaciones de fabricación. La geometría de esquina y el encuentro del pasamanos son una distribución visual: requiere confirmar la unión real antes de declararla solución constructiva. No se modelan escaleras ni cargas.

## Validación pendiente con Herraidea

Confirmar ancho/espesor y separación de soleras, altura real, montaje inferior (lateral o al piso), dimensiones y recorrido de articulaciones, tipo de fijación/perforación del vidrio, vela y encuentro de esquina. Confirmar que esta variante se comercializa como HRD 1223; el catálogo vigente describe un poste circular.

El rango de 1.20–1.40 m de la calculadora se conserva como estimación orientativa existente, **no se ha validado estructuralmente para estas soleras**. El aviso se presenta en la calculadora y el mensaje preparado de WhatsApp indica estudio pendiente de validar.

## Publicación

Propuesta local sobre 1.44.0, con versión de trabajo 1.45.0. No publicada en producción durante la elaboración de este modelo.
