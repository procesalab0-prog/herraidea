# HRD 1616 — Safari AR

Modelo de referencia armado: tres postes cuadrados, siete cables por lado y pasamanos. Fuente: `hrd-1616-esquina-7-cables.glb`. USDZ integrado sin cambios desde el commit de Claude `2f2481d`.

Página pública: https://www.herraidea.com/ar/hrd-1616

- Botón rojo compartido con HRD 1525, sobre el visor para quedar accesible en iPad.
- Safari recibe un enlace nativo `rel=ar` con una sola imagen hija; escala bloqueada y acción Cotizar por WhatsApp.
- Escritorio recibe la página compartible con QR. No se envían mensajes automáticamente.
- Tamaño de referencia 1.285 × 1.285 m y 1.061 m de alto, no medidas de la calculadora.
- USDZ: 93 mallas, metros, Y arriba y base al piso. Validación ARKit sin errores, advertencias ni comprobaciones fallidas.
- Pruebas de navegador: escritorio 1440×1000, iPhone 390×844 e iPad 820×1180 con capacidad Quick Look simulada. No prueban cámara nativa.
- Prueba física HRD 1616: pendiente. HRD 1525: el usuario confirmó funcionamiento el 2026-10-17, sin especificar dispositivo o SO.

Para regenerar únicamente este sistema con Blender:

```sh
blender --background --python scripts/ar/exportar_usdz.py -- assets/projects/hrd-1616/hrd-1616-esquina-7-cables.glb assets/projects/hrd-1616/ar/hrd-1616-esquina.usdz --satinado
```

El exportador de HRD 1525 permanece separado: contiene la corrección específica del cristal usada por su visor.
