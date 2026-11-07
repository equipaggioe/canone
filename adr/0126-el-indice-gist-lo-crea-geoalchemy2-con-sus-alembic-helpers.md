# ADR-0126 · El índice GiST lo crea GeoAlchemy2, con sus `alembic_helpers`

- **Estado:** Aceptada
- **Fecha:** 2026-11-06
- **Alcance:** [plataformas/postgres.md](../plataformas/postgres.md), `plantilla/server/alembic/env.py`,
  `plantilla/server/src/app/models/base.py` y `plantilla/server/tests/test_conventions.py`

## Contexto

El [ADR-0004](0004-geografia-con-funciones.md) declaraba la columna con `spatial_index=False` y dejaba
el índice GiST a la migración. El `env.py` canónico no usaba los `alembic_helpers` de GeoAlchemy2.
Con GeoAlchemy2 0.21.0, SQLAlchemy 2.1.8, Alembic 1.20.1 y PostGIS en PostgreSQL 17 se comprobó:

- Sin los helpers, la autogeneración propone borrar `spatial_ref_sys`. Con `spatial_index=True`, la
  migración generada falla con `relation "idx_<tabla>_<columna>" already exists`. Con el índice solo
  en la migración, la siguiente autogeneración propone borrarlo.
- Con `include_object`, `writer` y `render_item` en `context.configure` y `spatial_index=True`, la
  migración crea un solo índice, no toca `spatial_ref_sys`, la segunda autogeneración sale vacía y
  `downgrade` funciona.

## Decisión

1. La columna geográfica lleva el `spatial_index` por defecto, y GeoAlchemy2 crea su índice GiST.
2. `env.py` le pasa a `context.configure` los `alembic_helpers` de GeoAlchemy2 cuando está instalado.

## Consecuencias

- La autogeneración no requiere editar la migración ni excluir tablas a mano.
- El índice se llama `idx_<tabla>_<columna>`, el nombre que le da GeoAlchemy2, y no sigue el `ix` de
  `NAMING_CONVENTION`.
- `test_geography_columns` exige `spatial_index` en toda columna `geography`.

## Descartado

- **`spatial_index=False` e índice en la migración** (el punto 4 del ADR-0004): la autogeneración
  borra el índice y propone borrar `spatial_ref_sys`.
- **`spatial_index=False` e índice en `__table_args__`:** evita lo primero, pero no lo segundo, y
  reemplaza a mano lo que los helpers de GeoAlchemy2 ya resuelven.
