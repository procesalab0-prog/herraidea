# Sistema de postes con clips + vidrio

Segunda experiencia 3D integrada en el carrusel de soluciones de Herraidea.

## Fuente

- Paquete recibido: `content/source-documents/Herraidea-Pinza-Despiece.zip`.
- Modelo publicado: `assets/projects/clip-system/herraje-cristal.glb`.
- Portada: `assets/projects/clip-system/portada-estudio.jpg`, imagen de estudio original generada a partir de las fotografías proporcionadas por Herraidea.

## Alcance del modelo

El archivo contiene 46 nodos independientes y una animación `Despiece` de 0 a 3 segundos. Representa un tramo recto con dos postes, cuatro pinzas laterales, un paño de cristal, soportes superiores y pasamanos continuo.

En la visualización publicada, el paño de cristal termina exactamente en el borde exterior de los clips: cubre completamente su zona de sujeción sin rebasarla. En las esquinas de la calculadora, cada paño conserva ese límite y el poste compartido reúne los herrajes de ambos tramos a 90 grados.

El visor permite girar, acercar, desarmar, volver a armar, controlar manualmente el avance y enfocar una pinza.

## Restricciones

Es una reconstrucción conceptual basada en fotografías. No debe presentarse como plano, instructivo o especificación aprobada hasta confirmar con Herraidea el modelo/SKU, dimensiones, vidrio compatible, empaques, anclajes, cargas y aprietes.


## Piloto AR · HRD 1525 (1.89.0)

Página compartible: `/ar/hrd-1525`. El botón en la solución 01 abre Apple Quick Look en navegadores que anuncian soporte `rel=ar`; en escritorio lleva a la página con QR/enlace para teléfono. El archivo USDZ se sirve con `model/vnd.usdz+zip` y el enlace contiene un único hijo `img`, con `allowsContentScaling=0` y página canónica de esta experiencia.

Archivo estático `assets/projects/clip-system/hrd-1525-ar.usdz`, generado mediante `scripts/ar/export-hrd1525.py` con Blender. Se conservan 46 mallas, postura armada, ajuste de ancho de cristal idéntico al visor, eje Y arriba y unidades en metros. Se centra horizontalmente y apoya en el piso. Adaptación del vidrio a opacidad de Preview Surface para Quick Look, sin modificar el GLB de origen. Tamaño del modelo de referencia: 1.11 m ancho, 1.012 m alto y 0.10 m profundidad.

Es el tramo ilustrativo del modelo; no corresponde a los largos de la calculadora ni es plano de fabricación. Exportación de la configuración completa quedará para otra fase. El póster de la página AR es un render del propio USDZ; la portada original de la solución se conserva.

Validación ARKit/UsdUtils sin errores, comprobación de ZIP sin compresión y alineación de 64 bytes, 46 mallas y escala; ver `ar-manifest.json`. Pruebas navegador de botón/fallback y visibilidad exclusiva en HRD1525; la emulación de capacidad sólo valida el enlace, no ejecuta Quick Look ni la cámara. **Prueba física en Safari de iPhone/iPad pendiente.**
