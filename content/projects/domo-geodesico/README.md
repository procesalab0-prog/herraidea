# Domo geodésico — glamping

> **Estado: privado, pendiente de visto bueno.** Nada de esta carpeta está enlazado desde el sitio. No se debe integrar a la página ni cambiar `VERSION` hasta que Herraidea lo apruebe.

Modelo 3D de un domo geodésico para glamping hecho a partir de dos imágenes de referencia: una exterior con terraza y otra interior en corte. Tiene despiece por etapas con el mismo mecanismo que los demás visores de Soluciones interactivas.

## Archivos

| Archivo | Qué es |
| --- | --- |
| `assets/projects/domo-geodesico/domo-geodesico.glb` | Modelo de 467 piezas con el clip `Despiece` (409 piezas animadas; la terraza y el mobiliario quedan fijos). Formato Y-arriba, metros. |
| `assets/projects/domo-geodesico/portada-provisional.png` | Render exterior. **Es provisional:** hace falta una portada aprobada antes de publicar. |
| `content/projects/domo-geodesico/visor-privado.html` | Visor independiente de un solo archivo, sin internet y con `noindex`. Tiene vistas Exterior, Interior, Frente y Planta, capas Lona y Terraza, Desarmar/Armado y la barra de Separación. |
| `content/projects/domo-geodesico/comparacion-exterior.jpg`, `comparacion-interior.jpg` | Referencia junto al render del modelo. |
| `content/projects/domo-geodesico/render-estructura.jpg`, `render-despiece.jpg` | Estructura sin lona y despiece completo. |
| `content/source-documents/domo-geodesico/` | Imágenes de referencia recibidas: `referencia-exterior.webp` y `referencia-interior.jpg`. |
| `scripts/domo-geodesico/` | Generadores: `modelo.py` (usa `geo.py`) → `despiece.py` → `armar_visor.py`, más `render.py`. |

## Cómo regenerarlo

```bash
pip install bpy==4.5.14                       # Python 3.11; alternativa: blender -b -P <script>
python3 scripts/domo-geodesico/modelo.py       # output/domo-geodesico/domo-modelo.blend + domo-meta.json
python3 scripts/domo-geodesico/despiece.py     # assets/projects/domo-geodesico/domo-geodesico.glb + output/.../domo-geodesico.blend
python3 scripts/domo-geodesico/armar_visor.py  # content/projects/domo-geodesico/visor-privado.html (usa npx esbuild)
SPP=40 python3 scripts/domo-geodesico/render.py -- exterior interior estructura frente
SPP=40 DOMO_BLEND=domo-geodesico.blend python3 scripts/domo-geodesico/render.py -- despiece
```

`output/domo-geodesico/` es un directorio de trabajo; no se versiona.

## Qué representa

- **Geometría:** geodésico icosaédrico **3V 5/8**. La proporción alto/ancho es 0.60, igual que en la foto exterior. Tiene **61 nodos, 165 tubos y 105 triángulos**, con el anillo base de 15 nodos aplanado sobre la plataforma.
- **Tamaño estimado:** 7.0 m de diámetro de base y 4.16 m de altura sobre la plataforma. Se dedujo del mobiliario de las referencias: cama, sillas y tapanco.
- **Estructura:** tubo blanco de 42 mm con nodos de disco y 15 placas base.
- **Lona:** PVC blanco, con un panel por triángulo. Lleva ojo de buey de 66 cm a la izquierda del ventanal y dos respiraderos en la parte alta.
- **Ventanal panorámico:** 18 triángulos de vidrio con marco grafito, en las dos franjas inferiores y unos 100° de arco al frente.
- **Vestíbulo:** acceso de lona gris con cierre en U, a la izquierda-atrás (como en la vista interior).
- **Interior:** tapanco de triplay con escalera, repisas y cama superior; cama matrimonial con burós de tronco y lámpara hexagonal; estufa de leña con leñero y chimenea que sale por la lona; dos sillones amarillos con mesa de centro y tapetes; barra curva con dos bancos; plantas.
- **Terraza:** 11.2 × 11.3 m sobre postes, con plataforma redonda para el domo, dos sillas Adirondack con mesa, camastro y puf.
- **Etapas del despiece:**
  1. La lona se abre en pétalos.
  2. Salen los vidrios y marcos del ventanal.
  3. Se retiran el vestíbulo y la chimenea.
  4. La estructura se separa: los nodos se alejan más que los tubos para que se vea cada unión.

**No son medidas de fabricación.**

## Pendiente de confirmar con Herraidea

1. Diámetro real, frecuencia (3V u otra) y diámetro y espesor del tubo.
2. Tipo de nodo o unión que se fabricará (disco, tubo aplastado, conector).
3. Posición real de la puerta y del ventanal. Falta decidir si la chimenea se queda.
4. Si el mobiliario y la terraza forman parte de lo que se va a mostrar o si solo se presenta la estructura.
5. Portada aprobada para la tarjeta.

## Integración sugerida (solo con visto bueno)

1. En `project-3d-v2.js`, agregar un perfil y un proyecto. Valores iniciales para verificar en el navegador:
   `domo: { target: [.4, 1.6, 0], camera: [-5.6, 2.6, 13], min: 2, detailTarget: [0, .5, -.1], detailCamera: [.2, 9.4, 7.6] }`
   con `src: '/assets/projects/domo-geodesico/domo-geodesico.glb?v=<versión>'`. El vidrio usa `alphaMode: BLEND`; conviene `depthWrite = false`, como hace `scripts/domo-geodesico/visor.js`.
2. **Peso:** el GLB pesa unos 5 MB. Antes de publicarlo conviene comprimirlo con meshopt o Draco (el visor del sitio necesitaría el decodificador correspondiente en `assets/vendor/three`) o simplificar el mobiliario.
3. Añadir la tarjeta en Soluciones interactivas de `index.html` con la portada aprobada.
4. Seguir las reglas de `CLAUDE.md`: subir `VERSION`, la versión en `CLAUDE.md`, `CHANGELOG.md` y `content/version-history.json`, y probar en escritorio y teléfono.
5. Decidir si `visor-privado.html` se conserva: al publicarse en `main` quedaría accesible por URL aunque tenga `noindex`.

## Integridad (SHA-256)

Ver `SHA256SUMS` en esta misma carpeta.
