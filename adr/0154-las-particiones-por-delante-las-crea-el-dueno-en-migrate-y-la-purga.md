# ADR-0154 · Las particiones por delante las crea el dueño del esquema, en `migrate` y en la purga

- **Estado:** Aceptada
- **Fecha:** 2026-11-16
- **Alcance:** [`plataformas/postgres.md`](../plataformas/postgres.md), «Particiones»; [`plataformas/fastapi.md`](../plataformas/fastapi.md), «Registro de eventos»

## Contexto

`postgres.md` decía cuándo y por qué columna se particiona, pero no quién crea las particiones
nuevas. El rol del servidor no tiene DDL, y las únicas tareas del dueño del esquema son
`python -m app.tasks migrate` y la purga diaria. Concordia crea los meses de `message` en las dos.
El manual de PostgreSQL dice que lo habitual es quitar las particiones viejas y agregar las nuevas
periódicamente (*Partition Maintenance*).

## Decisión

1. Una tabla particionada por rango de fechas tiene creadas las particiones de los próximos
   meses, cuántos dice una constante del módulo que las crea.
2. Las crean `migrate`, en la transacción de las migraciones, y la purga diaria, con el rol dueño
   del esquema.

## Consecuencias

- La partición del mes falta solo si pasan tantos meses como la constante sin desplegar y sin que
  corra la purga.
