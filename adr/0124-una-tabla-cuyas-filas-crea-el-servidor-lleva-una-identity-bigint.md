# ADR-0124 · Una tabla cuyas filas crea el servidor lleva una identity `bigint`

- **Estado:** Aceptada
- **Fecha:** 2026-11-06
- **Alcance:** [plataformas/postgres.md](../plataformas/postgres.md)

## Contexto

El [ADR-0024](0024-la-clave-primaria-se-elige-por-lo-que-guarda-la-tabla.md) daba `bigint` a una
lista del equipo cuyo tope no cabe en el entero menor, y `uuid` al resto de las tablas. Una lista del
equipo con más de 2 147 483 647 filas no existe, y `event_log` de la plantilla, cuyas filas inserta
el servidor, ya usaba una identity `bigint` sin regla que la cubriera.

## Decisión

1. Una tabla cuyas filas crea el propio servidor, como el registro de eventos, lleva una identity
   `bigint`.

## Consecuencias

- Una tabla que crece sin tope, como un registro, no se queda sin ids: *Integer Types* da `bigint`
  cuando el rango de `integer` no alcanza.
- El id de esas filas se puede enumerar. Ningún cliente las crea ni son de un usuario, que son los
  casos del `uuid`.

## Descartado

- **`uuid`**, la regla anterior para estas tablas: ocupa 16 bytes donde bastan 8, y no hay un
  cliente que genere el id ni un dueño al que ocultárselo.
