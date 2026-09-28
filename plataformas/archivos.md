# Archivos

Los archivos que suben los usuarios.

## Subida

Estándares: [*File Upload Cheat Sheet*](../estandares/owasp/File_Upload.md) de OWASP,
[*Request Files*](../estandares/fastapi/request-files.md) de FastAPI y la directiva
[`request_body`](../estandares/caddy/request_body.md) de Caddy.

- Un archivo se sube solo, como `multipart/form-data`, y el servidor lo recibe como `UploadFile`.
  No pasa por base64 dentro de un JSON.
- Caddy corta el cuerpo con `request_body`: 1 MB en la API y 10 MB en las rutas de subida. El
  límite actúa antes de que el cuerpo llegue a Python.
- Cada ruta de subida declara su lista de tipos permitidos.
- Toda imagen se vuelve a codificar con Pillow antes de guardarse. Endurece la recomendación de
  OWASP: destruye contenido inyectado y borra los metadatos, como la ubicación de la foto.

## Almacenamiento

Estándar: [`systemd.exec`](../estandares/systemd/systemd.exec.xml).

- Cada archivo es una fila de una tabla hija de su recurso, `<recurso>_files`, con
  `ON DELETE CASCADE`. La fila guarda el tipo, el tamaño y el nombre original.
- El archivo en disco se llama con el ID de su fila y vive en el `StateDirectory=` del servicio,
  `/var/lib/<app>/files/`. Está en la misma máquina y el respaldo de
  [despliegue.md](despliegue.md) lo cubre junto con la base.
- El servidor entrega un archivo después de comprobar el permiso sobre su recurso. Caddy nunca sirve
  ese directorio.

## Borrado

Estándar: [`systemd.timer`](../estandares/systemd/systemd.timer.xml).

- Un timer de systemd borra cada día los archivos con más de una hora en disco y sin fila en
  ninguna tabla `_files`. El borrado en cascada y una subida cuyo commit falló dejan archivos sin
  fila, y un solo barrido cubre los dos caminos.

## Cómo se hace cumplir

| Regla | Con qué |
|---|---|
| Tamaño del cuerpo | `request_body` en el Caddyfile |
| Archivos sin fila | El timer de barrido |
