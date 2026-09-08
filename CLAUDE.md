# Herraidea — contexto del proyecto

Versión actual: **1.11.0**

Sitio de producción: `https://herraidea-landing.vercel.app/`

## Estado actual

Landing estática para Herraidea, enfocada en barandales, soluciones y fabricación a la medida. Incluye hero de día a noche, presentación editorial de capacidades, recorrido técnico Three.js, diseño sonoro opcional, catálogo desplegable de 66 productos, cobertura animada, ventanas con planos y especificaciones, historia institucional, contacto por WhatsApp y PWA.

## Archivos principales

- `index.html`: estructura completa del sitio y diálogos.
- `styles.css`: estilos, responsive y animaciones.
- `hero.js`: scroll, catálogo, ventanas, WhatsApp y easter egg.
- `sound.js`: motor Web Audio, preferencia del usuario y señales sonoras.
- `hrd-3d.js`: geometría, materiales, iluminación y animación Three.js.
- `hrd-map.js`: mapa animado de cobertura nacional desde León.
- `assets/fabricacion/`: imágenes optimizadas de maquinaria, producción y empaque recibidas para la primera etapa.
- `content/catalog/details.json`: 66 fichas y 159 referencias a imágenes técnicas.
- `content/source-documents/catalogo-herraidea-2023.pdf`: catálogo original completo recibido como fuente documental.
- `content/design-references/`: inspiración visual recibida para tipografía, UI industrial y presentación de producto.
- `content/jimdo-backup/`: respaldo original de páginas y recursos públicos de Jimdo.
- `content/version-history.json`: versiones mostradas en el easter egg.
- `docs/PLAN_MAESTRO.md`: estrategia viva, decisiones aprobadas e información pendiente para la siguiente etapa.
- `docs/FASE_1_DEFINICION.md`: estado de la primera fase, información confirmada y cuestionario de validación para Herraidea.
- `docs/FUENTE_CATALOGO_2023.md`: inventario preliminar, mapa de páginas y reglas para conciliar el PDF con Jimdo.
- `docs/DIRECCION_VISUAL.md`: principios aprobados para trasladar las referencias visuales a una identidad propia de Herraidea.
- `docs/RECORRIDO_3D_SOLUCIONES.md`: concepto futuro para sustituir las piezas aisladas por un barandal completo, despiece animado y adaptación a la medida.
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
