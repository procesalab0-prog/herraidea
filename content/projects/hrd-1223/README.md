# HRD 1223 — variante tubular y modelo de soleras conservado

El usuario pidió conservar la versión de soleras y crear otra con cuerpo de tubo como en el CAD, manteniendo el nombre HRD 1223.

## Variante tubular vigente en la vista previa

- Modelo: `assets/projects/hrd-1223/hrd-1223-tubo.glb`.
- Fuente reproducible: `scripts/generate_hrd1223_tubo.py`.
- Portada: `assets/projects/hrd-1223/portada-tubo.png`, render del mismo GLB.
- 45 componentes y elementos de contexto; animación `Despiece`, reversible, 0–3 segundos.
- Cuerpo circular hueco, una sola base circular con tres agujeros pasantes a 120°; conserva los brazos ajustables, discos, juntas, soporte de pasamanos y vidrio del estudio anterior.
- Referencias del CAD: cuerpo hasta 900 mm, nivel inferior 210 mm, distancia vertical entre brazos 570 mm. Diámetro exterior del tubo 50.8 mm según la descripción de catálogo de 2 pulgadas.
- Espesor de tubo de 3 mm, base Ø104 mm, agujeros Ø9 mm sobre círculo de Ø80 mm y detalles de fijación son provisionales. No es un plano de fabricación. No se trasladan dimensiones de soleras al cuerpo tubular.
- El despiece ilustra componentes; no certifica piezas comerciales ni secuencia de montaje. Esquinas, anclajes y separación admisible entre postes requieren confirmación.
- El vidrio y pasamanos son contexto; no implican contenido del kit.

## Versión de soleras preservada

La geometría, el generador, las notas y el paquete de integración originales permanecen guardados en el espacio de trabajo y en la entrega local `outputs/hrd-1223/`. La web publica únicamente la variante tubular aprobada.

## Integración

La vista previa presenta el modelo tubular con el nombre HRD 1223 en el carrusel y la calculadora. La calculadora usa `sistema=hrd1223`; el alias anterior `sistema=soleras` abre ahora el estudio vigente. Las piezas de fijación no se escalan con la longitud del tramo; solo vidrio y pasamanos se adaptan. Un poste por posición, cuerpo compartido en esquina y brazos de un lado en los extremos.

Versión 1.45.2: variante tubular aprobada para publicación el 21 de septiembre de 2026.
