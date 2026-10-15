# Cotizaciones especiales · Herraidea Admin

Ecommerce en pausa. Esta herramienta es independiente de Shopify.

## Iniciar vista local

`node admin-quotation/server.mjs`

Abrir http://127.0.0.1:8768/. El servidor escucha exclusivamente loopback y sólo sirve archivos permitidos. Carpeta excluida de la web pública mediante .vercelignore. No confundir esta vista local con un servicio autenticado remoto.

## Recorrido

1. Completar cliente, proyecto, folio y fecha.
2. Elegir sistema, acabado, medidas y conjuntos; agregar sus cantidades orientativas.
3. Modificar conceptos, precios y cantidades. Agregar conceptos especiales de instalación, flete o fabricación.
4. Elegir precios con IVA incluido o sin IVA. Aplicar descuento global sobre los importes de la base seleccionada; IVA se desglosa o agrega una sola vez.
5. Completar notas, condiciones y vigencia.
6. Revisar cotización y descargar PDF carta; impresión disponible como alternativa.
7. Guardar archivo JSON para continuar después. Abrir valida todo antes de reemplazar; el cliente y sus contactos se incluyen sólo al guardar el archivo deliberadamente.

Sólo HRD1616 tiene tarifas de referencia existentes; el resto permanece pendiente hasta editar sus precios. El extra de cable es ajustable y no se aprueba automáticamente. No hay cristal en el desglose generado. Ninguna modificación de esta herramienta cambia los precios de ecommerce.

## PDF y diseño

Referencia: rama claude/codex-landing-review-t46rsq, commit cbbd8f9, carpeta admin-prototipo. Se adaptan carga.html y cotizacion.html a entradas del formulario, sin importar precios, clientes ni condiciones ficticias. Fuentes y licencias se conservan localmente. El PDF contiene logo, cliente, proyecto, asesor, folio, fecha/vigencia, tabla editable, descuento, IVA, total con letra, notas y firmas. El crédito ProcesaLab se conserva en el panel, no en el PDF. Campos pendientes generan borrador.

## Privacidad y siguientes pasos

No base de datos, llamadas Shopify, historial compartido, envío de cotizaciones ni pagos. No se guardan contactos en localStorage. Se necesita guardar manualmente para conservar una cotización al cerrar.

El alojamiento separado y el acceso real ya fueron aplicados y verificados; véase Publicación verificada al final. No publicar esta carpeta en la landing ni usar el prototipo de contraseña del archivo de referencia como autenticación.

El servidor local de revisión no es un mecanismo de autorización para crear pedidos ni se conectará a Shopify.


## Acceso compartido y exportación (1.85.0)

En `http://127.0.0.1:8768/` el responsable define el usuario compartido y una contraseña de al menos 12 caracteres. La contraseña debe introducirla directamente el usuario; no se genera ni se imprime en herramientas. Configuración local en `admin-quotation/.admin-access.json`, modo 0600, excluida de Git y de la web. Sólo contiene hash scrypt, usuario y secreto de firma. No existe base de datos.

Sesión de ocho horas, cookie HttpOnly/SameSite Strict y Secure al usar HTTPS. Reiniciar no revoca sesiones; eliminar/rotar la configuración con un secreto nuevo sí. Salir borra la cookie de ese equipo, no revoca copias en otros equipos. Guardar JSON antes de salir; no hay persistencia automática ni almacenamiento de contactos. Límite de cinco intentos por quince minutos y dirección, en memoria del proceso; no es un control distribuido para Vercel.

Para alojamiento separado HTTPS: configurar ADMIN_ORIGIN (origen exacto), ADMIN_USERNAME, ADMIN_PASSWORD_HASH y ADMIN_SESSION_SECRET como secretos del servidor; verificar límite de intentos en plataforma. No publicar la carpeta como sitio estático: servir siempre por el control de acceso. Publicado en el proyecto independiente herraidea-admin, con secretos de producción y login propio de Herraidea. No copiar secretos de Shopify.

Públicos: formulario de acceso, marca, imagen social `/share.png`, manifest e iconos. Privados: interfaz de cotización, módulos, API y datos comerciales. La PWA requiere conexión; el worker no almacena páginas, clientes o cotizaciones. WhatsApp y la instalación remota requieren un enlace HTTPS accesible; localhost sólo funciona en esta computadora.

PDF directo mediante pdf-lib vendorizado (MIT, licencia adjunta), generado sólo en navegador con los datos recalculados del servidor. Logo ampliado, cliente, partidas, descuento, IVA, total con letra, notas y firmas. Sin crédito de ProcesaLab en el PDF por instrucción del usuario, conservado en el panel. El archivo JSON sigue siendo la copia editable; el PDF es el documento para compartir.


## Publicación verificada · 2026-10-14

- Enlace principal: https://admin.herraidea.com/
- Proyecto: herraidea-admin (`prj_Kf3Ayv8vsYMaBeZqxU1o2lJuGg2L`), equipo ProcesaLab.
- Despliegue listo: `dpl_3Z8jqxoqJBWrLPGWTcsgoD9GTnh4`.
- Código subido a main: `07d273b8b640992bc22d9360f6a21f4a820eb362`.
- Usuario y hash de contraseña existentes conservados como secretos de producción, junto con la clave de sesión; nada de ello en Git ni en el paquete. Configuración inicial remota deshabilitada.
- SSO de Vercel desactivado únicamente en este proyecto nuevo con autorización específica; login propio permanece obligatorio.
- Verificación real: escritorio y móvil, entrada protegida, API sin sesión 401, archivos internos 404, cálculo 10 m HRD 1616 $22,142.08, PDF descargado sin crédito ProcesaLab, sin errores ni desbordamiento.
- PWA e imagen social accesibles; no se guardan cotizaciones/clientes en caché.
- Publicación inicial realizada mediante API desde la carpeta revisada. No se configuró todavía despliegue automático por Git. Para próximas publicaciones ejecutar el mismo build protegido; nunca servir admin-quotation como contenido estático.
- La landing excluye admin-quotation y Shopify permanece en pausa.


## Dominio propio · 1.87.0

admin.herraidea.com pertenece al proyecto independiente herraidea-admin. Verificación Vercel válida y DNS sin conflictos mediante la zona existente. ADMIN_ORIGIN se actualizó sólo en producción a https://admin.herraidea.com; las credenciales no cambiaron. El enlace compartido herraidea-admin.vercel.app redirige al nuevo dominio con HTTP 307. No se alteraron los registros de correo ni el dominio público de la landing.

Despliegue del dominio: dpl_6sQZk3qso5Q3nraMdsuRzRuNwvTx. HTTPS y recorrido real escritorio/móvil verificados: acceso, cálculo HRD1616 por $22,142.08, descarga PDF y ausencia de desbordamiento/errores. El alias interno generado del equipo no es el enlace para compartir.


## Fabricación por componentes · 1.88.0

Primer bloque funcional en «Fabricar un herraje»: capturar piezas y accesorios por herraje, procesos y consumo; ajustar recargo sobre costo y llevar un concepto por herraje terminado a la cotización. Las tarifas de este módulo siempre se capturan SIN IVA. El traspaso respeta la base de IVA elegida en el presupuesto.

Sólido/tubo redondo: diámetro exterior, longitud y pared; placa/lámina rectangular: largo, ancho y espesor; forma especial: área real y perímetro por separado. Tarifas por mm, metro, mm², m², peso conocido en kg o pieza. El volumen es informativo; no se presume densidad para cobrar por peso. Merma sólo de materia prima, nunca de procesos o accesorios. Los procesos pueden cobrarse por pieza, minuto, mm de contorno o mm² de superficie real de trabajo (no se asume igual a área de material). Se conserva precisión de tarifas hasta redondear el total de cada componente.

No se inventan factores CNC, listas, precios ni tiempos. La captura inicial está vacía y un dato/tarifa faltante deja el precio pendiente. Cada pieza nueva propone una fila CNC sin tarifa ni minutos, que el administrador puede ajustar o retirar si no aplica. La selección automática desde listas reales no está implementada: sigue pendiente recibirlas y definir criterios y vigencia.

«Cargar ejemplo ficticio» arma dos separadores, una placa con corte/pulido y accesorios; todos sus importes son sintéticos. Se advierte en pantalla y en la descripción del concepto/PDF. Ejemplo: costo $462.00, recargo 25%, precio sin IVA $577.50, total con IVA de referencia 16% $669.90. Estas cantidades NO son una cotización comercial ni tarifas Herraidea.

El JSON guarda el armado actual. Al importarlo restaura las entradas y recalcula; no confía en totales serializados. Tras cambiar un armado, el concepto previamente agregado NO cambia automáticamente: revisar o quitar el concepto previo para evitar duplicación. El archivo conserva el último armado de fabricación, no una biblioteca de armados históricos por concepto. No hay almacenamiento compartido ni base de datos.

Verificación: cálculo de geometría, cantidades, CNC, merma, precisión, unidades, pendientes, límites y conservación de entradas; flujo navegador escritorio/móvil con ejemplo, edición, guardado/importación y PDF. Pendiente validar un herraje real con Herraidea antes de aprobar reglas comerciales.
