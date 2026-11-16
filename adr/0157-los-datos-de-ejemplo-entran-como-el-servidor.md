# ADR-0157 · Los datos de ejemplo entran con la cuenta del servidor y su carpeta de archivos

- **Estado:** Aceptada
- **Fecha:** 2026-11-16
- **Alcance:** [`plataformas/despliegue.md`](../plataformas/despliegue.md), «PostgreSQL»; `PRODUCTO-mock@.service` de `plantilla/infra/`

## Contexto

`PRODUCTO-mock@` corría `python -m app.tasks mock` con la cuenta del dueño del esquema y sin
`StateDirectory=`. Los datos de ejemplo de concordia guardan fotos, y en el VPS fallaban con
`KeyError: 'STATE_DIRECTORY'`, comprobado el 2026-11-16. Aun con la variable, el dueño no puede
escribir la carpeta de los archivos, que es de la cuenta del servidor. Los datos de ejemplo no
necesitan DDL: son filas y archivos como los que escribe la app.

## Decisión

`PRODUCTO-mock@` corre con la cuenta del servidor, sus credenciales y `StateDirectory=PRODUCTO/files`.

## Consecuencias

- Los datos de ejemplo ven los permisos del servidor: una tabla sin su `GRANT` falla también aquí.
- Un archivo de ejemplo es de la cuenta del servidor, que lo sirve y lo borra.
