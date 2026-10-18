# Barandales en Safari AR — 1.91.0

Los ocho sistemas del visor tienen una referencia USDZ armada, página para compartir, QR y acción Cotizar por WhatsApp. En cada visor se conserva el botón rojo flotante y se agrega otro debajo de los controles. Ambos apuntan al mismo sistema; Quick Look recibe un enlace `rel=ar` con una única imagen hija y escala bloqueada.

`ar/systems.json` es el registro para exportación y `ar/systems.js` su copia para la web; las pruebas verifican que coincidan. Los proyectos especiales (domo, rack y futbolito) quedan fuera del alcance de barandales.

| Visor | Página |
| --- | --- |
| HRD 1525 | /ar/hrd-1525 |
| HRD 1518 | /ar/hrd-1518 |
| HRD 1616 | /ar/hrd-1616 |
| HRD 1223 | /ar/hrd-1223 |
| HRD 1221 | /ar/hrd-1221 |
| HRD 1220 | /ar/hrd-1220 |
| HRD 1533 / 1534 / 1535 | /ar/hrd-1533-1534-1535 |
| Conectores HRD 1301 / 1302, postes HRD 1206 | /ar/hrd-1301-1206 |

Se conserva el modelo actual de cada visor: HRD 1220 es la pinza individual, no un sistema de cristal agregado. No se altera ninguna fuente GLB, no se exporta el despiece animado y no se toman medidas de la calculadora. El cristal de referencia se conserva donde existe en el modelo y usa opacidad USD Preview Surface.

Regeneración de los seis nuevos modelos (Blender 5.2):

```sh
blender --background --python scripts/ar/export-systems.py
python3 scripts/ar/test_asset.py
```

El script no toca los USDZ ya integrados de 1525 y 1616. Cada exportación guarda en `content/projects/ar/` sus hashes, número de mallas, caja en metros, eje vertical, base al piso y resultado de la validación ARKit. Cambiar un USDZ invalida su evidencia de prueba física: volver a comprobarlo en dispositivo.

Validación automatizada: los seis nuevos pasan ARKit sin errores; las pruebas web cubren los ocho sistemas y los dos botones, escritorio/iPhone/iPad simulados, selección correcta al cambiar de sistema, QR, MIME y enlaces. La simulación no abre la cámara nativa. Prueba física: HRD 1525 confirmado por el usuario el 2026-10-17 (dispositivo/SO no indicados); el resto sigue pendiente.
