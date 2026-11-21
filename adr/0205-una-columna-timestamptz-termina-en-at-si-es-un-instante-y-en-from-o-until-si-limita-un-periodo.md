# ADR-0205 · Una columna `timestamptz` termina en `_at` si es un instante, y en `_from` o `_until` si limita un periodo

- **Estado:** Aceptada. El usuario eligió la opción recomendada (2026-11-20)
- **Fecha:** 2026-11-20
- **Alcance:** «Nombres» y «Cumplimiento» de [plataformas/postgres.md](../plataformas/postgres.md) y `plantilla/server/tests/test_conventions.py`

## Contexto

`test_timestamps_end_in_at`, del [ADR-0202](0202-postgres-escribe-solo-lo-que-dice-su-origen-postgis-deja-de-ser-fuente-y-cada-convencion-verificable-tiene-su-prueba.md), corrido sobre los modelos de los productos, falló en concordia, consegne, equipaggio y navetta con columnas que limitan un periodo: `locked_until`, `valid_from`, `valid_to`, `period_start`, `period_end`, `current_period_end`, `scheduled_for`. Con solo `_at` quedarían nombres como `locked_until_at`.

## Decisión

1. Una columna `timestamptz` termina en `_at` si marca un instante, y en `_from` o `_until` si marca el inicio o el fin de un periodo.
2. `test_timestamps_have_suffix` acepta esas tres terminaciones y ninguna otra.

## Consecuencias

- `locked_until` y `valid_from` cumplen sin cambios; `valid_to`, `period_start`, `period_end` y `scheduled_for` se renombran en sus productos.

## Descartado

- **Solo `_at`:** obliga a nombres como `valid_from_at`.
- **Quitar la regla:** cada repositorio vuelve a elegir sus nombres.
- **Una lista abierta de terminaciones (`_since`, `_to`, `_start`, `_end`, `_for`):** dos nombres para lo mismo, y la prueba deja de ser cerrada.
