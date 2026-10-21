# Lista privada de costos compartidos

El panel guarda los materiales en un único archivo de Vercel Blob privado. No utiliza base de datos ni depende de almacenamiento del navegador. La lectura y edición requieren el login existente; el token de almacenamiento vive sólo en el servidor. Nunca añadir libros Excel, precios de proveedores ni credenciales a Git o a la web pública.

Cada material guarda precio de compra, cantidad/unidad de consumo, proveedor, fecha, tratamiento de IVA y estado. Se activa sólo después de confirmar precio, fecha e IVA. El costo aplicado a fabricación se convierte a neto y se captura junto con la versión de la lista. Actualizar el catálogo no recalcula cotizaciones antiguas. Los archivos de cotización incluyen su armado y las tarifas numéricas usadas.

Las escrituras son condicionales al ETag leído y cada cambio se agrega al historial en la misma operación. Si dos equipos editan a la vez, se rechaza la segunda escritura obsoleta con HTTP 409; la UI pide recargar sin descartar silenciosamente el formulario. Las lecturas de Blob usan `useCache: false`. El respaldo JSON incluye lista, referencias e historial. El historial no se trunca: al superar el límite de 5 MB se requiere revisar almacenamiento/respaldo antes de continuar.

Importación inicial de 21/10/2026: 95 materiales desde COTIZADOR.xlsx y 71 armados históricos desde LISTA DE CODIGOS Y RENDIMIENTOS .xlsx. Los materiales quedan pendientes, sin fecha vigente ni tratamiento de IVA asumido. Las cantidades por compra prellenadas se derivan de factores históricos y deben confirmarse. Los armados históricos son referencias, no recetas calculables todavía. Los datos se cargaron directamente a Blob; el repositorio contiene sólo código.

Variables de producción:

- `BLOB_READ_WRITE_TOKEN`: credencial privada del almacenamiento, nunca al navegador.
- Acceso del panel: conservar `ADMIN_USERNAME`, `ADMIN_PASSWORD_HASH`, `ADMIN_SESSION_SECRET` y `ADMIN_ORIGIN` existentes.
- Desarrollo/pruebas: `ADMIN_COSTBOOK_FILE` apunta a un archivo local persistente y privado. La UI lo identifica como prueba local. No usar este modo en Vercel.

Comprobaciones: persistencia tras reinicio, historial, dos ediciones simultáneas, IVA una sola vez, conservación de precios capturados, origen y sesión obligatorios; flujo de edición/guardado/recarga/aplicación en escritorio y teléfono. Se verificó también la escritura condicional real en Blob con un archivo temporal eliminado después.
