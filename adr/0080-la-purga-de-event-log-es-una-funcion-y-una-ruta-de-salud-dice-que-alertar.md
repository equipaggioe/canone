# ADR-0080 · La purga de `event_log` es una función, y una ruta de salud dice qué alertar

- **Estado:** Aceptada, salvo los puntos 6, 7 y 8, en propuesta
- **Fecha:** 2026-10-24
- **Alcance:** «Registro de eventos» y «Salud» de [`plataformas/fastapi.md`](../plataformas/fastapi.md),
  «Procesos» de [`plataformas/despliegue.md`](../plataformas/despliegue.md), `plantilla/server/` y
  `plantilla/infra/`

## Contexto

Nadie se enteraba de un evento grave ni de un respaldo que dejó de correr. El registro de eventos
era solo una regla: la plantilla no traía `event_log`. La purga usaba un rol aparte, con una
segunda credencial de base, y canone no decía quién da los permisos de una tabla.

Comprobado en PostgreSQL 17, en Debian 13: el rol de la app con solo `INSERT` y `SELECT` recibe
`permission denied` al cambiar, borrar o vaciar `event_log`. Una función `SECURITY DEFINER` del
dueño borra solo lo vencido, y un rol aparte con `DELETE` borra todo. Con el aislamiento de su
unidad, el servidor lee la fecha de `/var/lib/<app>/last-backup`.

## Decisión

1. `GET /api/health/events` responde la hora del último evento `critical` y la del último respaldo
   bueno, o `null`. Quien la consulta decide cuándo avisar. Es una regla propia: *Monitoring of
   events* del *Logging Cheat Sheet* sigue fuera de la cita, porque fija procesos de operación.
2. La ruta exige el token de `health_token` en `Authorization: Bearer`, comparado en tiempo
   constante, y sin él responde 401.
3. La purga es `purge_event_log()`, una función `SECURITY DEFINER` del dueño del esquema que solo
   borra lo que pasó la retención. El rol de la app solo la ejecuta, desde una tarea diaria.
4. La retención está en la migración que crea la función, y la plantilla guarda 365 días.
5. Los permisos de una tabla los da la migración que la crea.
6. *(propuesta)* El rol de la app se llama como la app.
7. *(propuesta)* `actor_id` es un `uuid` sin clave foránea, e `ip_address`, un `inet`.
8. *(propuesta)* El servidor lee `last-backup` en la carpeta padre de su `StateDirectory=`.

## Consecuencias

- Una inyección en la app, a lo sumo, adelanta una purga. No hace falta otra credencial de base.
- Cambiar la retención es una migración que reemplaza la función.
- El CI crea el rol de la app antes de migrar.
- La copia fuera del servidor que pide *Protection* ya la da el respaldo: la receptora no deja
  borrar ni reescribir.

## Descartado

- **El rol aparte para la purga:** suma una credencial y una unidad, y quien la robe borra todo
  el rastro.
- **Particionar `event_log` por mes:** sirve para tablas muy grandes, y suma piezas que hoy no
  hacen falta.
- **Que el servidor avise a un monitor:** el servidor tendría que conocer a quien lo vigila.
