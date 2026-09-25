# HRD 1220 — pinza baja y unión superior entre cristales

## Referencias

Lámina CAD HRD 1220 del 02/02/2023, fotografía de la pinza en mesa y dos fotografías de instalación recibidas en esta conversación el 21/09/2026. El usuario pidió representar expresamente el círculo que une la separación superior de los dos cristales.

## Medidas y geometría

Confirmado en CAD: base 101.60 × 101.60 mm, altura 185 mm, asiento del vidrio a 75 mm y rango de vidrio 10–12 mm. Material indicado INOX 304. El modelo usa vidrio de contexto de 12 mm.

El conjunto muestra cuatro pinzas bajas (dos por cristal), dos cristales separados por una junta de 10 mm y un conector circular superior independiente. No hay poste de altura completa ni pasamanos. Cada pinza contiene base con cuatro agujeros, tapa decorativa con abertura, cuerpo fijo, asiento de vidrio, dos empaques, pinza frontal, tornillo inferior y ajuste superior. La pinza frontal tiene aberturas en los tornillos; la tapa decorativa puede separarse durante el despiece.

El conector superior está centrado en la junta y tiene dos discos con juntas y un tornillo. Diámetro provisional 52 mm; no se ha recibido su código ni plano. No se identifica este accesorio como parte incluida del kit HRD 1220.

No acotados: ancho de pinza 48 mm, espesores de placas, posiciones/diámetros de tornillos y anclajes, altura total del vidrio de contexto 1100 mm. Son aproximaciones visuales. No se modelan roscas ni certifican cargas, montaje o perforaciones de vidrio.

## Despiece

43 elementos con pistas independientes de traslación, clip `Despiece` 0–3 segundos. El conjunto completo se puede armar/desarmar y el botón “Ver pinza” acerca la mordaza. El conector superior se separa en sus propios discos y empaques. La animación es explicativa y no prescribe una secuencia real de montaje.

## Calculadora

- Paneles propuestos con el criterio heredado de 1.20–1.40 m, sujeto a validación específica; no es separación estructural certificada.
- Dos pinzas por panel, sin compartir pinzas en juntas o esquinas.
- Un conector circular por junta recta; no se añade un disco plano atravesando una esquina a 90°.
- Total de pinzas = 2 × total de paneles.
- Total de uniones rectas = total de paneles − número de tramos.
- Ejemplo 5.30 m: 4 paneles, 8 pinzas y 3 uniones.
- Ejemplo 5.30 + 3.90 m: 7 paneles, 14 pinzas y 5 uniones rectas. Accesorio de esquina pendiente de definir.
- Los resúmenes visibles y WhatsApp distinguen pinzas, paneles y uniones del conteo de postes de los demás sistemas.

## Archivos

- `scripts/generate_hrd1220.py` y `scripts/generate_hrd1220_shapes.mjs`: geometría reproducible, Python/Node y Three.js local.
- `assets/projects/hrd-1220/hrd-1220.glb`: componentes y animación.
- `assets/projects/hrd-1220/portada.png`: render del propio modelo.
- `?proyecto=hrd1220`: visor.
- `?sistema=hrd1220#calculadora`: calculadora.

Versión 1.49.0 aprobada para publicación el 21 de septiembre de 2026. Conserva los modelos anteriores aprobados.


## Piloto Blender — 1.57.0
El visor de despiece usa hrd-1220-piloto.glb: pinza individual, acero satinado, biseles, tornillos con vástagos y seis movimientos sincronizados. El armado termina con la tapa. La calculadora conserva el GLB del sistema completo con sus pinzas y unión superior. GIF y póster en ficha rápida y página del producto, con alternativa de movimiento reducido.
