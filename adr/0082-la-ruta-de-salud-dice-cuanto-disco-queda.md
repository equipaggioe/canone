# ADR-0082 · La ruta de salud dice cuánto disco queda

- **Estado:** Aceptada
- **Fecha:** 2026-10-24
- **Alcance:** «Salud» de [`plataformas/fastapi.md`](../plataformas/fastapi.md) y `plantilla/server/`

## Contexto

Con el disco lleno PostgreSQL deja de escribir, y `GET /api/health` sigue respondiendo 204: su
`SELECT 1` no escribe. Quien vigila el servidor no se entera hasta que fallan las escrituras.

## Decisión

1. `GET /api/health/events` responde también `diskFreeBytes` y `diskTotalBytes`, del disco de su
   `StateDirectory=`. Quien la consulta decide cuándo avisar, como con las fechas del
   [ADR-0080](0080-la-purga-de-event-log-es-una-funcion-y-una-ruta-de-salud-dice-que-alertar.md).
2. El libre es el que puede escribir un usuario sin privilegios, el de `shutil.disk_usage`: el
   que le queda a PostgreSQL.

## Consecuencias

- En un VPS de un solo disco, es el disco de PostgreSQL. Con la base en otro volumen, la ruta mide
  el equivocado.
- Leer el disco no escribe nada: la ruta responde con el disco lleno.

## Descartado

- **Que quien vigila entre por SSH a leer el disco:** le da acceso a la máquina para leer un dato.
- **Un agente de métricas, como node_exporter:** un servicio, un puerto y una autenticación más por
  máquina, para leer un solo dato.
