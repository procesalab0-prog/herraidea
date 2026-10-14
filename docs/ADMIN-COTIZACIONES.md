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
6. Revisar cotización e imprimir/guardar como PDF carta.
7. Guardar archivo JSON para continuar después. Abrir valida todo antes de reemplazar; el cliente y sus contactos se incluyen sólo al guardar el archivo deliberadamente.

Sólo HRD1616 tiene tarifas de referencia existentes; el resto permanece pendiente hasta editar sus precios. El extra de cable es ajustable y no se aprueba automáticamente. No hay cristal en el desglose generado. Ninguna modificación de esta herramienta cambia los precios de ecommerce.

## PDF y diseño

Referencia: rama claude/codex-landing-review-t46rsq, commit cbbd8f9, carpeta admin-prototipo. Se adaptan carga.html y cotizacion.html a entradas del formulario, sin importar precios, clientes ni condiciones ficticias. Fuentes y licencias se conservan localmente. El PDF contiene logo, cliente, proyecto, asesor, folio, fecha/vigencia, tabla editable, descuento, IVA, total con letra, notas, firmas y crédito ProcesaLab. Campos pendientes generan borrador.

## Privacidad y siguientes pasos

No base de datos, llamadas Shopify, historial compartido, envío de cotizaciones ni pagos. No se guardan contactos en localStorage. Se necesita guardar manualmente para conservar una cotización al cerrar.

Antes de alojar: crear proyecto separado de Vercel, aplicar autenticación real a todas las páginas/API/archivos, comprobar solicitud sin sesión rechazada, y verificar acceso de cada administrador. No publicar esta carpeta en la landing ni usar el prototipo de contraseña del archivo de referencia como autenticación.

El servidor local de revisión no es un mecanismo de autorización para crear pedidos ni se conectará a Shopify.


## Acceso compartido y exportación (1.85.0)

En `http://127.0.0.1:8768/` el responsable define el usuario compartido y una contraseña de al menos 12 caracteres. La contraseña debe introducirla directamente el usuario; no se genera ni se imprime en herramientas. Configuración local en `admin-quotation/.admin-access.json`, modo 0600, excluida de Git y de la web. Sólo contiene hash scrypt, usuario y secreto de firma. No existe base de datos.

Sesión de ocho horas, cookie HttpOnly/SameSite Strict y Secure al usar HTTPS. Reiniciar no revoca sesiones; eliminar/rotar la configuración con un secreto nuevo sí. Salir borra la cookie de ese equipo, no revoca copias en otros equipos. Guardar JSON antes de salir; no hay persistencia automática ni almacenamiento de contactos. Límite de cinco intentos por quince minutos y dirección, en memoria del proceso; no es un control distribuido para Vercel.

Para alojamiento separado HTTPS: configurar ADMIN_ORIGIN (origen exacto), ADMIN_USERNAME, ADMIN_PASSWORD_HASH y ADMIN_SESSION_SECRET como secretos del servidor; verificar límite de intentos en plataforma. No publicar la carpeta como sitio estático: servir siempre por el control de acceso. No se ha creado ni publicado un proyecto Vercel. No copiar secretos de Shopify.

Públicos: formulario de acceso, marca, imagen social `/share.png`, manifest e iconos. Privados: interfaz de cotización, módulos, API y datos comerciales. La PWA requiere conexión; el worker no almacena páginas, clientes o cotizaciones. WhatsApp y la instalación remota requieren un enlace HTTPS accesible; localhost sólo funciona en esta computadora.

PDF directo mediante pdf-lib vendorizado (MIT, licencia adjunta), generado sólo en navegador con los datos recalculados del servidor. Logo ampliado, cliente, partidas, descuento, IVA, total con letra, notas y firmas. Sin crédito de ProcesaLab en el PDF por instrucción del usuario, conservado en el panel. El archivo JSON sigue siendo la copia editable; el PDF es el documento para compartir.
