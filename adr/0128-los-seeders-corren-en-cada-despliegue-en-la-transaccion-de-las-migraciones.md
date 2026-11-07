# ADR-0128 · Los seeders corren en cada despliegue, en la transacción de las migraciones

- **Estado:** Aceptada
- **Fecha:** 2026-11-07
- **Alcance:** «Migraciones» y «Seeders» de [plataformas/fastapi.md](../plataformas/fastapi.md),
  «PostgreSQL» y «Versiones» de [plataformas/despliegue.md](../plataformas/despliegue.md),
  `plantilla/server/`, `plantilla/infra/` y `scripts/infra/deploy.sh`

## Contexto

La plantilla no tenía dónde poner los datos que una app necesita para funcionar, ni los de ejemplo.
Consola los sembraba con una convención propia, los paquetes `seeders` y `mock_data`, que no llegaba
a una máquina de canone. Además, en desarrollo las migraciones se juntan de vez en cuando en una
inicial ([ADR-0127](0127-database-py-vacia-la-base-solo-en-desarrollo-y-quien-administra-la-lee-como-app-read.md)).
Juntarlas con `alembic revision --autogenerate` escribe solo el esquema, nunca datos.

## Decisión

1. Los datos van en dos paquetes de `app`. `seeders/` lleva los que tiene que haber en todo entorno,
   producción incluida. `mock_data/` lleva los de ejemplo, solo para una máquina en desarrollo.
2. Un seeder es una función `async def seed_<nombre>(session)`. Los seeders corren en el orden de los
   nombres del módulo y de la función, y son idempotentes: escriben lo que falta y nunca duplican una
   fila.
3. `python -m app.tasks migrate` aplica las migraciones y después los seeders, en una sola
   transacción. La unidad `<app>-migrate@<versión>` lo corre en cada despliegue.
4. Si un seeder falla, se deshacen también las migraciones, y `deploy.py` hace lo mismo que cuando
   falla una migración: borra la versión y vuelve la anterior.
5. `database.py seed` corre los seeders de la versión activa. `database.py seed --mock` corre
   `mock_data/` con la unidad `<app>-mock@<versión>`, y falla sin la marca de desarrollo.

## Consecuencias

- Una máquina nueva queda con sus datos en el primer despliegue, sin un paso a mano.
- Juntar las migraciones no pierde datos, porque los datos no viven en ellas.
- Un seeder que no es idempotente duplica filas en producción en cada despliegue. Ninguna prueba
  de la plantilla lo detecta.
- El CI de un producto arma la base de prueba con `app.tasks migrate`, así que también corre sus
  seeders.

## Descartado

- **Los datos en migraciones de Alembic, como recomienda Django:** se pierden al juntar el
  historial. Rails y Laravel los ponen en seeders.
- **Los seeders en otra transacción, después de migrar:** un seeder que falla dejaría la base
  migrada con la versión anterior corriendo encima, o una versión nueva sin sus datos.
- **Que alguien corra los seeders a mano en producción:** una máquina nueva quedaría sin los datos
  que necesita hasta que alguien lo haga.
