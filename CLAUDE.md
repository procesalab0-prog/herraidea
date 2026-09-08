# Herraidea — contexto del proyecto

Versión actual: **1.14.0**

Sitio de producción: `https://herraidea-landing.vercel.app/`

## Estado actual

Landing estática para Herraidea, enfocada en barandales, soluciones y fabricación a la medida. Incluye hero de día a noche, presentación editorial de capacidades, carrusel de soluciones y proyectos con experiencias 3D ampliables, diseño sonoro opcional, catálogo desplegable de 82 herrajes y configuraciones, cobertura animada, ventanas con planos y especificaciones, historia institucional, contacto por WhatsApp y PWA.

## Archivos principales

- `index.html`: estructura completa del sitio y diálogos.
- `styles.css`: estilos, responsive y animaciones.
- `hero.js`: scroll, catálogo, ventanas, WhatsApp y easter egg.
- `sound.js`: motor Web Audio, preferencia del usuario y señales sonoras.
- `hrd-3d.js`: geometría, materiales, iluminación y animación Three.js.
- `hrd-map.js`: mapa animado de cobertura nacional desde León.
- `project-3d-v2.js`: carrusel, visor reutilizable para diferentes soluciones, interacción táctil y control de sus animaciones de despiece.
- `assets/fabricacion/`: imágenes optimizadas de maquinaria, producción y empaque recibidas para la primera etapa.
- `assets/projects/futbolito/`: modelo GLB usado por la experiencia del primer proyecto.
- `assets/projects/clip-system/`: modelo GLB y portada de estudio de la solución de postes con clips y vidrio.
- `content/catalog/details.json`: 82 fichas de herrajes y configuraciones, incluidas 38 opciones de postes.
- `content/source-documents/catalogo-herraidea-2023.pdf`: catálogo original completo recibido como fuente documental.
- `content/source-documents/Futbolito-Herraidea-3D.zip`: paquete original del primer proyecto interactivo.
- `content/source-documents/Herraidea-Pinza-Despiece.zip`: paquete fuente del sistema de postes, pinzas, vidrio y pasamanos.
- `content/source-documents/catalogo-postes-2026/`: tres páginas originales del catálogo de postes recibido el 8 de septiembre de 2026; se conservan como respaldo interno y sus precios no se publican.
- `content/projects/futbolito/README.md`: alcance, integridad y restricciones del modelo del futbolito.
- `content/projects/clip-system/README.md`: alcance y restricciones de la solución de barandal con clips.
- `content/design-references/`: inspiración visual recibida para tipografía, UI industrial y presentación de producto.
- `content/jimdo-backup/`: respaldo original de páginas y recursos públicos de Jimdo.
- `content/version-history.json`: versiones mostradas en el easter egg.
- `docs/PLAN_MAESTRO.md`: estrategia viva, decisiones aprobadas e información pendiente para la siguiente etapa.
- `docs/FASE_1_DEFINICION.md`: estado de la primera fase, información confirmada y cuestionario de validación para Herraidea.
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
