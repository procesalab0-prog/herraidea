# Recorrido 3D — Soluciones completas

Especificación conceptual para evolucionar la sección 3D actual de piezas individuales hacia una experiencia centrada en soluciones, barandales y proyectos completos.

Estado: **carrusel de soluciones en implementación**
Fecha: 2026-09-08

La versión 1.15.0 presenta tres tarjetas grandes. El sistema de postes con clips, vidrio y pasamanos ocupa la primera posición y se identifica con HRD 1525; el poste HRD 1518 ocupa la segunda posición con su sistema de tres barras; el Futbolito queda en la tercera como proyecto especial. Las tres tarjetas abren un visor ampliado con giro, acercamiento táctil, vista de detalle y despiece reversible.

Las portadas del HRD 1518 y el Futbolito comparten un estudio gris claro, acero con reflejos controlados y un acento rojo ambiental. La portada final proporcionada para el HRD 1518 muestra los pines al exterior y las barras delgadas atravesándolos; se usa sin alteraciones. El modelo GLB se conserva como referencia geométrica principal.

El modelo del futbolito es una reconstrucción visual aproximada basada en fotografías. No representa todavía medidas verificadas, un modelo de fabricación ni una secuencia física de ensamble.

## 1. Objetivo narrativo

La sección debe demostrar que Herraidea no solo vende piezas: diseña y fabrica una solución completa que puede adaptarse a las medidas de cada proyecto.

El usuario debe comprender visualmente esta secuencia:

**Piezas → sistema armado → adaptación a la medida → acabado final → solución lista para el proyecto**

## 2. Concepto principal

Sustituir el protagonismo de las tres piezas aisladas por un barandal o proyecto completo modelado en 3D. El sistema incluirá, cuando corresponda:

- Vidrios.
- Postes o minipostes.
- Conectores y pinzas.
- Pasamanos.
- Tapas, tornillos y fijaciones.
- Base o superficie de montaje.

Las piezas 3D existentes pueden conservarse como acercamientos o capítulos secundarios dentro de recuadros técnicos. Así se aprovecha el trabajo actual, pero se subordina a la explicación de la solución completa.

## 3. Secuencia de animación propuesta

### Capítulo 1 — La solución completa

- Aparece el barandal terminado, limpio y centrado.
- La cámara realiza un movimiento breve y preciso para mostrar profundidad.
- Un texto corto introduce la idea: **“Una solución completa.”**

### Capítulo 2 — Cada pieza tiene una función

- El barandal se separa mediante un despiece controlado.
- Vidrios, postes, conectores, tornillos y pasamanos se desplazan sobre ejes claros.
- Los componentes importantes pueden entrar en recuadros técnicos con nombre, código o función.
- El movimiento debe ser ordenado y reversible, evitando explosiones caóticas.

### Capítulo 3 — Hecho a la medida

- El sistema vuelve a ensamblarse.
- Aparecen líneas de cota para ancho, altura, separación entre postes y espesor del vidrio.
- Al avanzar el desplazamiento, el barandal crece o se ajusta a nuevas dimensiones.
- Las piezas deben reubicarse o extenderse según su lógica real; no se deformarán tornillos, conectores ni elementos que conservarían medidas fijas.
- Texto sugerido: **“Tu proyecto define la medida.”**

### Capítulo 4 — Acabado satín

- El material evoluciona suavemente hacia acero inoxidable satinado.
- La transición debe modificar textura, rugosidad, reflejos y dirección del cepillado, no limitarse a cambiar el color.
- Una luz recorre la superficie para revelar el acabado sin producir reflejos exagerados.
- Texto sugerido: **“Acero inoxidable. Acabado preciso.”**

### Capítulo 5 — Del sistema al proyecto

- La solución terminada se integra en un espacio arquitectónico sencillo.
- Se muestra el conjunto completo y aparece la llamada: **“Cuéntanos qué necesitas.”**
- Puede ofrecerse acceso al canalizador, la ficha de solución o WhatsApp.

## 4. Recuadros para las piezas existentes

Los modelos actuales pueden presentarse como módulos editoriales alrededor de la solución:

- Cada recuadro muestra una pieza, su nombre y una función breve.
- Al activarse, la pieza crece dentro del recuadro para revelar forma y acabado.
- Una línea o señal visual conecta el recuadro con su posición real en el barandal.
- Al cerrar el detalle, la pieza vuelve al sistema completo.
- Los recuadros conservarán el lenguaje negro, blanco, gris metálico y rojo de la landing.

El crecimiento debe comunicar capacidad de adaptación. Para evitar una lectura incorrecta, las dimensiones variables se animarán en perfiles, postes o separación del sistema; los herrajes de medida fija se sustituirán por la variante correspondiente en lugar de estirarse de manera irreal.

## 5. Interacción por desplazamiento

- La experiencia será controlada por el desplazamiento y dividida en capítulos claros.
- El usuario podrá avanzar y retroceder sin perder el estado del modelo.
- Una barra de progreso mostrará en qué parte del proceso se encuentra.
- La indicación de desplazamiento aparecerá al inicio y desaparecerá después de la primera interacción.
- Los textos y etiquetas cambiarán junto con la animación, sin tapar la pieza principal.
- Las transiciones tendrán inercia suave, pero cada capítulo deberá llegar a una posición estable y legible.

### Alternativa opcional de controles simples

Se conserva como referencia opcional el escaparate interactivo de Apple compartido el 9 de septiembre de 2026. El aspecto relevante es la simplicidad de los botones, no su composición completa:

- Controles pequeños con forma de cápsula y esquinas completamente redondeadas.
- Fondo gris claro o transparente, borde mínimo y contraste discreto.
- Etiquetas muy breves acompañadas, cuando sea útil, por un signo de suma o indicador sencillo.
- Un solo control activo a la vez, con su explicación desplegada cerca del botón.
- El modelo 3D mantiene el protagonismo y los controles no invaden la escena.

Esta navegación podría emplearse para **Armado**, **Despiece**, **Componentes**, **Fijación** y **Acabado**. Queda registrada únicamente como opción para comparar posteriormente con la navegación por desplazamiento y no constituye todavía una decisión de implementación.

## 6. Escritorio y teléfono

### Escritorio

- Solución central de gran escala.
- Recuadros técnicos distribuidos alrededor o en una columna lateral.
- Espacio suficiente para cotas, etiquetas y despiece.

### Teléfono

- Experiencia de pantalla completa con el modelo siempre centrado.
- Recuadros convertidos en tarjetas inferiores o laterales que no corten el producto.
- Textos breves y máximo dos niveles de información simultánea.
- Respeto por barras del navegador, áreas seguras y diferentes alturas de pantalla.
- La pieza no debe desplazarse hacia la parte superior durante el recorrido.

## 7. Sonido y accesibilidad

- Mantener el sonido opcional y discreto.
- Usar señales suaves en ensamble, aparición de cotas y cambio de acabado.
- No reproducir sonido si la sección no está visible.
- Incluir una versión reducida para `prefers-reduced-motion`.
- Toda la información esencial deberá existir también en texto, sin depender únicamente de la animación.

## 8. Requisitos antes de modelar

- Elegir el primer barandal o solución real que se representará.
- Confirmar sus componentes y códigos.
- Recibir planos, medidas y fotografías del sistema armado.
- Definir cuáles dimensiones pueden variar realmente.
- Confirmar materiales y acabados de cada componente.
- Determinar qué piezas actuales pueden reutilizarse.
- Aprobar los textos cortos de cada capítulo.

## 9. Criterio de éxito

La experiencia debe hacer evidente, incluso sin leer toda la ficha, que Herraidea entrega un sistema completo y puede adaptarlo a un proyecto específico. La espectacularidad de la animación debe reforzar esa idea y no convertirse en un efecto separado del mensaje comercial.
