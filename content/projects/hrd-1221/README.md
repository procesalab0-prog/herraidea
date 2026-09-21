# HRD 1221 — cuerpo circular y soleras horizontales

Reconstrucción solicitada el 21 de septiembre de 2026 según la lámina de CAD adjunta y la fotografía de instalación. Es un modelo diferente del HRD 1223, que conserva su geometría aprobada.

## Geometría

- Tubo circular hueco de Ø50.8 mm, cuerpo hasta 900 mm.
- Dos soleras planas CONTINUAS de 230 × 26 × 6 mm, delante del tubo, con una fijación central cada una.
- Discos en x = ±100 mm respecto al eje del poste, siguiendo la cota 100 de la lámina.
- Alturas de fijación: 210 y 780 mm (570 mm entre ejes).
- Una sola base redonda con tres agujeros pasantes distribuidos a 120°, igual a la del HRD 1223.
- Cuatro juegos de discos y juntas; vela, soporte superior, vidrio y pasamanos de contexto.
- 33 elementos, animación `Despiece` reversible de 0 a 3 segundos.

## Alcance

Las cotas 900 / 210 / 570 / 100 se toman de la lámina adjunta. Diámetro del tubo apoyado en la descripción del catálogo; espesor, ancho y espesor de solera, discos, tornillos, vela y anclajes son aproximaciones visuales pendientes de confirmar. El vidrio no incluye perforaciones de fabricación y no se representa rosca de tornillos. El modelo no es un plano de fabricación ni un cálculo estructural.

En la calculadora, los postes intermedios conservan las dos soleras completas. En extremos se usa media solera; en esquinas se muestran medias soleras orientadas según los tramos. Estas variantes son conceptuales y requieren validar la unión constructiva. El rango heredado de 1.20–1.40 m no queda certificado para este sistema.

## Archivos

- `scripts/generate_hrd1221.py`: generador reproducible, Python y Node.js.
- `scripts/generate_hrd1223_base.mjs`: base circular con perforaciones, común a ambos modelos.
- `assets/projects/hrd-1221/hrd-1221.glb`: archivo 3D con piezas y animación.
- `assets/projects/hrd-1221/portada.png`: render del propio modelo.
- Visor: `?proyecto=hrd1221`.
- Calculadora: `?sistema=hrd1221#calculadora`.

No se reemplazan las fotografías ni los datos comerciales del catálogo. Versión 1.46.0 aprobada para publicación el 21 de septiembre de 2026 sobre la versión pública 1.45.2.
