# Herraidea — contexto del proyecto

Versión actual: **1.48.0**

El dominio oficial `www.herraidea.com` sirve la web desde Vercel y `herraidea.com` redirige de forma segura a esa dirección. Las referencias canónicas, la tarjeta social, los datos estructurados y el catálogo descargable usan el dominio oficial. Los registros de correo preexistentes se conservaron al migrar los servidores DNS desde Jimdo a Vercel.

Sitio de producción: `https://www.herraidea.com/`

## Estado actual

La tarjeta de Soluciones interactivas del HRD 1221 usa su portada de estudio aprobada con postes tubulares, soleras planas, cristales y pasamanos. La nueva ruta queda vinculada con el modelo 3D existente y evita conservar la imagen provisional en caché.

La tarjeta de Soluciones interactivas del HRD 1223 usa su portada de estudio aprobada y la vincula con el modelo 3D tubular ya publicado. La nueva ruta de imagen evita que los navegadores conserven la portada provisional.

Se añade el HRD 1221 con cuerpo tubular, dos soleras horizontales continuas con fijación central y base circular de tres agujeros. Cuenta con despiece y calculadora propios, conservando el HRD 1223 aprobado.

El HRD 1223 tubular usa una sola placa circular con tres agujeros pasantes a 120 grados. Se retiran el segundo aro y las fijaciones que ocultaban los agujeros, en el despiece y la calculadora.

Se conserva el estudio de soleras y se añade una variante HRD 1223 con tubo circular hueco, base redonda y brazos ajustables. El visor y la calculadora presentan ahora la variante tubular; las dimensiones no indicadas en el CAD siguen siendo provisionales.

Se incorpora un estudio 3D del HRD 1223 de soleras planas, según las fotografías y la variante elegida: 51 elementos, despiece reversible, detalle de brazo y distribución en la calculadora. Se identifican expresamente las medidas y esquinas pendientes de validación.

Vercel Web Analytics y Speed Insights están integrados en las 87 páginas públicas y en sus generadores. La fase actual mide tráfico, rutas, referencias, países, dispositivos y Core Web Vitals con las capacidades incluidas en Hobby y sin cookies. Los eventos personalizados de calculadora, WhatsApp, catálogo y descargas se reservan para la entrega final, cuando se evaluará el plan Pro.

Los destinos principales declarados en la portada coinciden con la barra de navegación: Sistemas, Proyectos, Calculadora, Asesoría, Catálogo y Contacto. Las cuatro familias permanecen como rutas individuales dentro del catálogo, conservando sus fichas y jerarquía para búsquedas por producto.

La calculadora visual y los controles de exploración 3D incorporan cápsulas de vidrio translúcido, reflejos que siguen el cursor y respuesta suave al pulsar. Se conservan los materiales reales y se respeta el movimiento reducido.

La portada declara una sola identidad de sitio y organización, y destaca Sistemas, Pipetas, Postes, Conectores, Jaladeras y Contacto como destinos principales. Las páginas de sistemas, familias y las 81 fichas de producto incorporan rutas de navegación estructuradas para que Google entienda la jerarquía completa y pueda elegir enlaces de sitio útiles en la búsqueda de marca.

Las 70 rutas públicas conocidas del sitio anterior de Jimdo cuentan con redirecciones permanentes hacia sus páginas equivalentes en la web vigente. Las rutas de “catálogo” contemplan la codificación URL del acento. Esto evita que los resultados antiguos de Google terminen en páginas inexistentes y ayuda a consolidar gradualmente el índice en las URLs nuevas.

El botón para copiar el enlace de la calculadora usa un icono SVG de línea en lugar del carácter Unicode `↗`, para impedir que iOS lo convierta en emoji.

El contacto presenta dos líneas directas de Ventas por WhatsApp: +52 477 256 1695 y +52 477 274 0349. El Hero muestra una indicación más visible para continuar desplazándose, disponible también en celular. En el catálogo, las familias reaccionan en rojo solo al pasar el cursor o enfocarlas con teclado; el scroll ya no activa esa apariencia. Un nuevo acceso “Quiero diseñar un barandal” conduce desde el catálogo a la guía de sistemas completos.

La calculadora genera enlaces con `sistema` y `tramos`, restaura hasta ocho medidas válidas al abrirlos y permite copiar la configuración. El enlace también viaja en el mensaje de WhatsApp para que Herraidea pueda reconstruir el mismo recorrido, modelo 3D y estimación sin base de datos. Los límites exactos de separación de 1.20 m y 1.40 m se calculan sin desviaciones por redondeo decimal.

La selección de `/sistemas` se integra con la calculadora mediante `?sistema=clips`, `?sistema=tubo` o `?sistema=cable`. Al llegar, la herramienta activa el sistema y su modelo 3D automáticamente; si el visitante cambia la selección, la URL permanece sincronizada y el resumen de WhatsApp conserva el sistema, tramos, espacios, postes y esquinas estimadas.

La página `/sistemas` reúne HRD 1525, HRD 1518 y HRD 1616 en una guía comparativa con acceso a sus experiencias 3D, la calculadora y las piezas disponibles. La línea de solera conduce al catálogo de Postes sin presentarse como un sistema completo validado. El menú principal y las cuatro páginas de familia enlazan esta nueva ruta.

La familia Jaladeras cuenta con una página propia en `/familias/jaladeras`: compara sus dos modelos tipo H por diámetro, acabado y código, con búsqueda, fichas técnicas y cotización. El menú Familias y el acceso rápido del catálogo enlazan la nueva guía.

El menú principal agrupa Pipetas, Postes, Conectores y Jaladeras dentro de “Familias” en computadora y teléfono, evitando saturar la barra superior.

La familia Conectores cuenta con una página propia en `/familias/conectores`: reúne sus 29 modelos, cuatro puntos de partida por aplicación, búsqueda y filtros para vidrio, tubo, pasamanos y puertas. El acceso rápido de Conectores abre esta guía y sus fichas técnicas enlazan de regreso a ella.

La familia Pipetas cuenta con una página propia en `/familias/pipetas`: reúne sus 13 modelos, cuatro puntos de partida por función, búsqueda y filtros por montaje, ajuste y tipo de cabeza. El acceso rápido de Pipetas en el catálogo abre esta guía y sus fichas técnicas enlazan de regreso a ella.

La página de Postes muestra el punto rojo de la letra i en los logotipos del encabezado y del pie.

La familia Postes cuenta con una página propia en `/familias/postes`: presenta cuatro sistemas como puntos de partida, búsqueda por código o nombre, filtros por tipo y acceso a las 37 fichas técnicas. Enlaza las soluciones 3D, la calculadora y la asesoría sin declarar compatibilidades que aún no hayan sido confirmadas. El acceso rápido de Postes en el catálogo abre esta página y las fichas individuales permiten regresar a ella.

Cada uno de los 81 modelos del catálogo cuenta con una página técnica estática y una URL descriptiva propia bajo `/productos/`. Las páginas reúnen fotografía principal, vistas técnicas disponibles, especificaciones, descarga de ficha PDF, cotización por WhatsApp, metadatos para buscadores y datos estructurados de producto. La ficha rápida del catálogo enlaza y comparte estas URLs. `sitemap.xml` incluye todas las piezas y `robots.txt` identifica el mapa del sitio.

Las configuraciones recientes de Postes extraídas de las tres láminas del catálogo 2026 incluyen una segunda vista CAD en su ficha web y PDF. HRD 1221 inicio/final y HRD 1221 intermedio usan archivos técnicos distintos para evitar intercambiar sus configuraciones de dos y cuatro brazos.

HRD 1221 intermedio muestra dos soleras continuas y planas con fijación central y base circular de tres agujeros, según el CAD y la corrección del usuario. Se retiran las vistas borrosas antiguas de HRD 1220, HRD 1221 y HRD 1223 de sus galerías; quedan la foto principal y el CAD HD.

HRD 1221 inicio/final usa dos brazos planos de solera en un lado y HRD 1221 intermedio usa cuatro brazos planos opuestos a 180 grados, según su CAD. Se conservan las vistas técnicas y HRD 1223 mantiene sus brazos ajustables.

Se publican las imágenes aprobadas de HRD 1220, HRD 1221 y HRD 1223 y las vistas técnicas HD del catálogo recibido para diez fichas. Se conservan las imágenes anteriores y se actualizan las fichas PDF con la lámina HD preferente.

Imagen de estudio aprobada para HRD 1221 y HRD 1223: cuerpo y base circulares, brazos opuestos a 180 grados y vela articulada como HRD 1519. Las imágenes originales se conservan como vistas técnicas en la ficha web y el PDF.

Landing estática para Herraidea, enfocada en barandales, soluciones y fabricación a la medida. Incluye hero de producto con transición de día a noche y mensaje editorial despejado, presentación de capacidades, carrusel de cuatro soluciones y proyectos con experiencias 3D ampliables y controles tipo cápsula, calculadora visual de postes por tramos y esquinas compartidas para HRD 1525, HRD 1518 y HRD 1616, canalizador visual de proyectos sin base de datos con sugerencias iniciales, captación de proyectos fuera de catálogo, catálogo desplegable de 81 herrajes y configuraciones con dos caminos de entrada, buscador desplegable por código o nombre, filtros por familia, aplicación y sistema, relaciones entre piezas de sistemas validados y pictogramas propios, 13 configuraciones de postes ya normalizadas con imágenes de estudio aprobadas, catálogo 2026 descargable sincronizado con esas imágenes y logotipo protagonista, cobertura animada, ventanas con planos y especificaciones, historia institucional animada, contacto por WhatsApp y PWA.

## Archivos principales

- `index.html`: estructura completa del sitio y diálogos.
- `styles.css`: estilos, responsive y animaciones.
- `hero.js`: scroll, catálogo, canalizador, ventanas, WhatsApp y easter egg.
- `assets/vendor/three/`: Three.js 0.160.0 y sus complementos (GLTFLoader, OrbitControls, RoomEnvironment, BufferGeometryUtils) alojados en el propio sitio. Los visores 3D y la calculadora no dependen de ningún CDN externo. Al actualizar la biblioteca hay que reemplazar estos archivos, no cambiar los imports.
- `hrd-3d.js`: versión anterior del recorrido 3D; **no se carga en la página** y requiere el `THREE` global que ya se retiró. Se conserva solo como referencia.
- `project-3d.js`: versión anterior del visor de proyectos; **no se carga en la página**, la vigente es `project-3d-v2.js`.
- `hrd-map.js`: mapa animado de cobertura nacional desde León.
- `project-3d-v2.js`: carrusel, visor reutilizable para diferentes soluciones, interacción táctil y control de sus animaciones de despiece; el cristal del HRD 1525 cubre la zona de sujeción sin rebasarla, las cabezas del HRD 1518 permanecen unidas a cada pin y el HRD 1616 sustituye el negro por acero satinado durante la visualización.
- `calculator-3d.js`: cálculo de espacios y postes, manejo de tramos conectados y ensamblaje de la vista a partir de los modelos GLB reales del HRD 1525, HRD 1518 y HRD 1616; conserva las pinzas en ambas caras del poste compartido HRD 1525 y recorta únicamente los extremos interiores del pasamanos para que se encuentren en el centro de la esquina, centra el encuentro del pasamanos HRD 1616 sobre su poste y mantiene íntegra la unión articulada del HRD 1518.
- `assets/fabricacion/`: imágenes optimizadas de maquinaria, producción y empaque recibidas para la primera etapa.
- `assets/hero-barandal-v2-day.png` y `assets/hero-barandal-v2-night.png`: escenas vigentes del hero, fieles al sistema de postes, clips y cristal.
- `assets/brand/herraidea-social-v2.png`: tarjeta social vigente para WhatsApp y redes, alineada con el nuevo hero y el mensaje principal.
- `output/pdf/catalogo-herraidea-2026-adelanto.pdf`: catálogo descargable vigente; se genera desde las mismas imágenes y datos que utiliza la web.
- `output/pdf/fichas/`: 81 fichas PDF individuales, una por modelo, generadas sin precios desde la fotografía y la vista o plano técnico disponible.
- `scripts/generate_product_sheet.py`: generador individual o por lote de fichas a partir de `details.json`, la fotografía del producto y la vista o plano técnico disponible.
- `scripts/generate_product_pages.py`: genera las 81 páginas técnicas estáticas y actualiza `sitemap.xml` desde la misma fuente del catálogo.
- `product-page.css`: presentación adaptable de las páginas técnicas individuales.
- `productos/`: páginas encontrables por código con fotografía, vistas técnicas, especificaciones, PDF y cotización.
- `familias/postes.html`: página de exploración de la familia Postes por sistema, función y código.
- `familias/pipetas.html`: página de exploración de la familia Pipetas por montaje, ajuste, cabeza y código.
- `familias/conectores.html`: página de exploración de la familia Conectores por aplicación, función y código.
- `familias/jaladeras.html`: página comparativa de las jaladeras tipo H por diámetro y código.
- `sistemas.html` y `systems-page.css`: guía central para comparar los sistemas HRD 1525, HRD 1518 y HRD 1616, y continuar a sus herramientas o productos.
- `family-page.css` y `family-page.js`: presentación adaptable, búsqueda y filtros de la página de familia.
- `scripts/generate_posts_family_page.py`, `scripts/generate_pipetas_family_page.py`, `scripts/generate_connectors_family_page.py` y `scripts/generate_handles_family_page.py`: generan las páginas públicas de las cuatro familias desde los datos vigentes del catálogo.
- `.github/workflows/catalog-pdf.yml`: regenera y publica el catálogo general y las 81 fichas PDF al cambiar sus generadores, los datos o las imágenes, manteniendo todas las descargas sincronizadas.
- `assets/hero-barandal.png` y `assets/hero-night.png`: pareja anterior del hero, reutilizada en la composición animada de “Nuestra evolución”.
- `assets/projects/futbolito/`: modelo GLB y portada de estudio del Futbolito Herraidea.
- `assets/projects/clip-system/`: modelo GLB y portada de estudio de la solución de postes con clips y vidrio.
- `assets/projects/hrd-1518/`: modelos GLB principal y lateral, más la portada de estudio del poste HRD 1518.
- `assets/projects/hrd-1616/`: modelo GLB de esquina y portada oficial del sistema de poste cuadrado con cable de acero; `portada-final-v1240.png` conserva sin cambios la última imagen entregada por Herraidea.
- `content/catalog/details.json`: 81 fichas de herrajes y configuraciones, incluidas 38 opciones de postes; 13 de ellas ya utilizan las imágenes de estudio aprobadas en esta etapa y se presentan con el mismo encuadre completo que las demás familias.
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
