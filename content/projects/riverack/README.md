# Riverack — rack de caja para pickup

> **Estado: aprobado e integrado en Proyectos (1.59.0).** Autorizado por Herraidea el 29 de septiembre de 2026. Visor directo sin portada, junto al Futbolito; proyecto probado en una RAM 700. Se conserva el modelo negro aprobado sin modificar su geometría.

Solo el GLB y esta documentación se incorporan a producción. El visor privado, Blender, generadores, fotos y comparaciones de la tabla siguiente permanecen en `claude/codex-landing-review-t46rsq`; no se copian a `main`.

Modelo 3D de un rack de caja (solo el rack, sin la camioneta ni el rack de techo) que Herraidea fabrica con la marca **Riverack**. Tiene despiece por etapas con el mismo mecanismo que los demás visores de Soluciones interactivas.

## Archivos

| Archivo | Qué es |
| --- | --- |
| `assets/projects/riverack/riverack.glb` | Modelo con 100 piezas, 56 de ellas tornillos, y el clip de animación `Despiece` (96 piezas animadas; los 4 postes inferiores quedan fijos). Formato Y-arriba, metros. |
| `assets/projects/riverack/portada-provisional.png` | Render de estudio con la misma cámara que la foto de referencia. **Es provisional:** hace falta una portada aprobada antes de publicar. |
| `content/projects/riverack/visor-privado.html` | Visor independiente de un solo archivo, sin internet y con `noindex`. Incluye vistas, Desarmar/Armado, la barra de Separación y Captura. Sirve para revisarlo con Herraidea. |
| `content/projects/riverack/riverack.blend` | Archivo de Blender editable, con la animación. |
| `content/projects/riverack/comparacion-con-foto.jpg` | Foto de estudio y render del modelo con la misma cámara. |
| `content/projects/riverack/parte-alta-foto-vs-modelo.jpg` | Comparación ampliada de las tres cabezas visibles. |
| `content/source-documents/riverack/foto-estudio.png` | Foto de estudio recibida; es la referencia principal. |
| `content/source-documents/riverack/foto-piezas.jpg` | Fotografía de piezas reales (viga con RIVERACK calado y fundas). |
| `scripts/riverack/` | Generadores: `modelo.py` → `despiece.py` → `armar_visor.py`, más `render.py` y la fuente Archivo 900 (licencia SIL OFL) para el texto de la viga. |

## Cómo regenerarlo

```bash
pip install bpy==4.5.14                 # Python 3.11; alternativa: blender -b -P <script>
python3 scripts/riverack/modelo.py       # output/riverack/riverack-modelo.blend
python3 scripts/riverack/despiece.py     # assets/projects/riverack/riverack.glb + output/riverack/riverack.blend
python3 scripts/riverack/armar_visor.py  # content/projects/riverack/visor-privado.html (usa npx esbuild)
SPP=48 python3 scripts/riverack/render.py -- estudio tres_cuartos trasera detalle_cabeza detalle_base
```

`output/riverack/` es un directorio de trabajo; no se versiona.

## Qué representa

- **Postes:** 4 canales C de 150 mm con el alma hacia afuera, inclinados unos 11° hacia el centro. Tienen una pieza superior telescópica de 126 mm y no llevan logo.
- **Cabeza:** las alas de la pieza superior suben y abrazan el travesaño con placas achaflanadas. Cada placa lleva 2 tornillos y una oreja colgante con barreno.
- **Travesaños:** tubo rectangular cerrado y telescópico. Cada uno tiene 2 fundas en los extremos, 2 tubos interiores y 1 cople central.
- **Vigas laterales:** canal C entre postes con **RIVERACK** calado en itálica tipo esténcil, dos filas de ranuras y el patrón "#" en los extremos.
- **Bases:** collar con 2 tornillos grandes y soporte en C con ranura.
- **Etapas del despiece:** salen los tornillos → suben los travesaños → se separan fundas y cople → se abren placas y orejas → sale la pieza superior → se retiran las vigas → bajan las bases.

Las proporciones se calcularon resolviendo la cámara de la foto de estudio (PnP, error cercano al 1 %). La escala se fijó con un poste de 150 mm, así que **no son medidas de fabricación**. Medidas resultantes: unos 1.63 m de largo, 1.70 m de ancho en las bases y 0.66 m de alto.

## Pendiente de confirmar con Herraidea

1. Medidas reales: ancho del poste, altura total, separación entre postes y ancho entre bases.
2. **Orientación de las bases.** En la foto, las cuatro miran al mismo lado (placa atornillada hacia −Y y soporte hacia +Y) y así se modeló. Si en la pieza real van en espejo, se cambia en `modelo.py`, sección «base».
3. No se requiere portada: Herraidea solicitó expresamente visor directo sin imagen.

## Integración aprobada

- Sección nueva `#proyectos`, independiente de Soluciones interactivas (`#soluciones`). Riverack se muestra al llegar y se puede alternar con el Futbolito sin abrir un diálogo.
- Se reutilizan el motor `hrd-project-3d`, los botones Liquid Glass, despiece por etapas y controles de separación y detalle.
- El acabado negro no pasa por reemplazo de material a acero. No se añade a Sistemas ni a la calculadora.
- Los enlaces `?proyecto=riverack` y `?proyecto=futbolito` seleccionan el modelo en la sección nueva.
- Se informa de la prueba en RAM 700; no se declara compatibilidad universal ni medidas de fabricación.

## Integridad (SHA-256)

Ver `SHA256SUMS` en esta misma carpeta.
