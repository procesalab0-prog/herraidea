# Herraidea — contexto del proyecto

Versión actual: **1.9.0**

Sitio de producción: `https://herraidea-landing.vercel.app/`

## Estado actual

Landing estática para Herraidea, fabricante de herrajes para vidrio templado. Incluye hero de día a noche, recorrido técnico Three.js, diseño sonoro opcional, catálogo de 66 productos, ventanas con planos y especificaciones, historia institucional, contacto por WhatsApp y PWA.

## Archivos principales

- `index.html`: estructura completa del sitio y diálogos.
- `styles.css`: estilos, responsive y animaciones.
- `hero.js`: scroll, catálogo, ventanas, WhatsApp y easter egg.
- `sound.js`: motor Web Audio, preferencia del usuario y señales sonoras.
- `hrd-3d.js`: geometría, materiales, iluminación y animación Three.js.
- `content/catalog/details.json`: 66 fichas y 159 referencias a imágenes técnicas.
- `content/jimdo-backup/`: respaldo original de páginas y recursos públicos de Jimdo.
- `content/version-history.json`: versiones mostradas en el easter egg.
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
