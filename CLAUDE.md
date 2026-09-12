# Herraidea — contexto del proyecto

Versión actual: **1.24.2**

La tarjeta HRD 1616 incorpora el video promocional aprobado de Higgsfield (`project-cover.js`): reproducción breve, silenciosa y solo al estar visible; conserva la foto con movimiento reducido, ahorro de datos o error de carga. No modifica los modelos, la calculadora ni el despiece. Fuente: recurso Higgsfield `7a51a150-dbf4-4478-a256-10a7bc79b04a`.

Sitio de producción: `https://herraidea-landing.vercel.app/`

## Estado actual

Landing estática para Herraidea, enfocada en barandales, soluciones y fabricación a la medida. Incluye hero de producto con transición de día a noche y mensaje editorial despejado, presentación de capacidades, carrusel de cuatro soluciones y proyectos con experiencias 3D ampliables y controles tipo cápsula, calculadora visual de postes por tramos y esquinas compartidas para HRD 1525, HRD 1518 y HRD 1616, canalizador visual de proyectos sin base de datos con sugerencias iniciales, captación de proyectos fuera de catálogo, catálogo desplegable de 82 herrajes y configuraciones con pictogramas propios, catálogo 2026 descargable con logotipo protagonista, diseño sonoro opcional, cobertura animada, ventanas con planos y especificaciones, historia institucional animada, contacto por WhatsApp y PWA.

## Archivos principales

- `index.html`: estructura completa del sitio y diálogos.
- `styles.css`: estilos, responsive y animaciones.
- `hero.js`: scroll, catálogo, canalizador, ventanas, WhatsApp y easter egg.
- `sound.js`: motor Web Audio, preferencia del usuario y señales sonoras.
- `hrd-3d.js`: geometría, materiales, iluminación y animación Three.js.
- `hrd-map.js`: mapa animado de cobertura nacional desde León.
- `project-3d-v2.js`: carrusel, visor reutilizable para diferentes soluciones, interacción táctil y control de sus animaciones de despiece; el cristal del HRD 1525 cubre la zona de sujeción sin rebasarla, las cabezas del HRD 1518 permanecen unidas a cada pin y el HRD 1616 sustituye el negro por acero satinado durante la visualización.
- `calculator-3d.js`: cálculo de espacios y postes, manejo de tramos conectados y ensamblaje de la vista a partir de los modelos GLB reales del HRD 1525, HRD 1518 y HRD 1616; conserva las pinzas a ambos lados de cada poste compartido del HRD 1525, centra el encuentro del pasamanos HRD 1616 sobre el poste de esquina y mantiene íntegra la unión articulada del HRD 1518.
- `assets/fabricacion/`: imágenes optimizadas de maquinaria, producción y empaque recibidas para la primera etapa.
- `assets/hero-barandal-v2-day.png` y `assets/hero-barandal-v2-night.png`: escenas vigentes del hero, fieles al sistema de postes, clips y cristal.
- `assets/brand/herraidea-social-v2.png`: tarjeta social vigente para WhatsApp y redes, alineada con el nuevo hero y el mensaje principal.
- `output/pdf/catalogo-herraidea-2026-adelanto.pdf`: catálogo descargable vigente; se genera desde las mismas imágenes y datos que utiliza la web.
- `assets/hero-barandal.png` y `assets/hero-night.png`: pareja anterior del hero, reutilizada en la composición animada de “Nuestra evolución”.
- `assets/projects/futbolito/`: modelo GLB y portada de estudio del Futbolito Herraidea.
- `assets/projects/clip-system/`: modelo GLB y portada de estudio de la solución de postes con clips y vidrio.
- `assets/projects/hrd-1518/`: modelos GLB principal y lateral, más la portada de estudio del poste HRD 1518.
- `assets/projects/hrd-1616/`: modelo GLB de esquina y portada oficial del sistema de poste cuadrado con cable de acero; `portada-final-v1240.png` conserva sin cambios la última imagen entregada por Herraidea.
- `content/catalog/details.json`: 82 fichas de herrajes y configuraciones, incluidas 38 opciones de postes.
- `assets/catalog/pictograms/`: recortes PNG transparentes de los pictogramas proporcionados por Herraidea para Pipetas, Postes, Conectores y Jaladeras.
- `content/design-references/pictogramas-familias-herraidea.png`: lámina original recibida con los cuatro pictogramas, conservada sin modificaciones como fuente.
- `content/source-documents/catalogo-herraidea-2023.pdf`: catálogo original completo recibido como fuente documental.
- `content/source-documents/calculadora-postes/regla-separacion-postes.jpeg`: regla original recibida para separación, número de espacios, postes y ejemplo de obra real.
- `content/source-documents/Futbolito-Herraidea-3D.zip`: paquete original del primer proyecto interactivo.
- `content/source-documents/Herraidea-Pinza-Despiece.zip`: paquete fuente del sistema de postes, pinzas, vidrio y pasamanos.
- `content/source-documents/Herraidea-HRD-1518-3D.zip`: paquete fuente del poste HRD 1518 con sus dos variantes.
- `content/source-documents/Herraidea-Esquina-90-3D.zip`: paquete fuente de la esquina articulada del HRD 1518.
- `content/source-documents/Herraidea-Barandal-Cables-Esquina.zip`: paquete fuente del sistema HRD 1616.
- `content/source-documents/hrd-1518/`: fotografía original usada como referencia del poste HRD 1518.
- `content/source-documents/catalogo-postes-2026/`: tres páginas originales del catálogo de postes recibido el 8 de septiembre de 2026; se conservan como respaldo interno y sus precios no se publican.
- `content/projects/futbolito/README.md`: alcance, integridad y restricciones del modelo del futbolito.
- `content/projects/clip-system/README.md`: alcance y restricciones de la solución de barandal con clips.
- `content/projects/hrd-1518/README.md`: fuente, integridad, alcance y restricciones del modelo HRD 1518.
- `content/projects/hrd-1616/README.md`: fuente, presentación aprobada e integridad del modelo HRD 1616.
- `content/design-references/`: inspiración visual recibida para tipografía, UI industrial y presentación de producto.
- `content/jimdo-backup/`: respaldo original de páginas y recursos públicos de Jimdo.
- `content/version-history.json`: versiones mostradas en el easter egg.
- `docs/PLAN_MAESTRO.md`: estrategia viva, decisiones aprobadas e información pendiente para la siguiente etapa.
- `docs/FASE_1_DEFINICION.md`: estado de la primera fase, información confirmada y cuestionario de validación para Herraidea.
- `docs/FASE_2_PROFESIONALIZACION.md`: avance de recursos técnicos y SEO, próximos bloques y datos necesarios para completar la segunda fase.
- `docs/FUENTE_CATALOGO_2023.md`: inventario preliminar, mapa de páginas y reglas para conciliar el PDF con Jimdo.
- `docs/FUENTE_CATALOGO_POSTES_2026.md`: comparación con el catálogo vigente y detalle de las 18 configuraciones incorporadas sin precios.
- `docs/DIRECCION_VISUAL.md`: principios aprobados para trasladar las referencias visuales a una identidad propia de Herraidea.
- `docs/RECORRIDO_3D_SOLUCIONES.md`: estado del piloto interactivo y especificación futura para un barandal completo, despiece animado y adaptación a la medida.
- `CHANGELOG.md`: historial humano completo.
- `VERSION`: versión semántica actual.

## Reglas de actualización

En cada cambio visible o funcional:

1. Incrementar `VERSION` usando versionado semántico.
2. Actualizar la versión indicada en este archivo.
3. Agregar la nueva entrada al principio de `CHANGELOG.md`.
4. Agregar la misma versión a `content/version-history.json`.
5. Mantener el crédito “Creado por ProcesaLab”.
6. Probar en escritorio y en teléfono antes de desplegar.

No modificar ni borrar el respaldo de `content/jimdo-backup/`. No editar el sitio original de Jimdo.
