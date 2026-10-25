# ADR-0081 · La purga de `event_log` la corre el dueño del esquema

- **Estado:** Aceptada
- **Fecha:** 2026-10-24
- **Alcance:** «Registro de eventos» de [`plataformas/fastapi.md`](../plataformas/fastapi.md),
  «Procesos» de [`plataformas/despliegue.md`](../plataformas/despliegue.md), `plantilla/server/` y
  `plantilla/infra/`

## Contexto

Los puntos 3 y 4 del
[ADR-0080](0080-la-purga-de-event-log-es-una-funcion-y-una-ruta-de-salud-dice-que-alertar.md)
ponían la purga en una función `SECURITY DEFINER` de la base. canone no escribe código dentro de
PostgreSQL: el resto de la lógica vive en Python, y la función era la única pieza en SQL.

La credencial del dueño del esquema ya existe: `<app>-migrate/database_url`, que el servidor no
recibe.

## Decisión

1. La purga es un `DELETE` en `services/events.py` de lo que pasó la retención. La corre la tarea
   diaria, y su unidad carga `app_database_url` desde `<app>-migrate/`, como la de las
   migraciones. Reemplaza el punto 3 del ADR-0080.
2. La retención es una constante en días en `services/events.py`, y la plantilla guarda 365.
   Reemplaza el punto 4 del ADR-0080.

## Consecuencias

- El servidor sigue sin poder borrar `event_log`: solo tiene `INSERT` y `SELECT`.
- Cambiar la retención es cambiar una constante, sin migración.
- La tarea de la purga corre con todos los permisos del dueño del esquema.
- Comprobado en Debian 13 con systemd 257: la unidad del servidor, con su aislamiento, no ve la
  credencial del dueño ni el proceso de la purga; un proceso del mismo usuario sin aislamiento sí la
  lee mientras la purga corre. Se acepta, como en las migraciones: llegar ahí exige salir del
  aislamiento de la unidad.

## Descartado

- **La función `SECURITY DEFINER`:** deja lógica dentro de la base, fuera de Python y de sus
  herramientas.
- **Un usuario del sistema aparte para la purga y las migraciones:** cierra un riesgo que ya exige
  salir del aislamiento, y lo común es un usuario por servicio con roles de base separados.
