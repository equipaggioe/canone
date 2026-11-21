# ADR-0203 · Una tabla que amplía otra lleva su clave foránea como clave, una lista que se busca va en una tabla, y el CI de Canone prueba la plantilla del servidor

- **Estado:** Aceptada. El usuario pidió escribir las opciones recomendadas (2026-11-20)
- **Fecha:** 2026-11-20
- **Alcance:** «Nombres», «Clave primaria», «Geografía», «Tipos» y «Cumplimiento» de [plataformas/postgres.md](../plataformas/postgres.md), «Base de datos» de [plataformas/fastapi.md](../plataformas/fastapi.md), `fuentes/postgresql/array.sgml`, `plantilla/server/tests/test_conventions.py` y [.github/workflows/infra.yml](../.github/workflows/infra.yml)

## Contexto

El [ADR-0202](0202-postgres-escribe-solo-lo-que-dice-su-origen-postgis-deja-de-ser-fuente-y-cada-convencion-verificable-tiene-su-prueba.md) dejó sin resolver la clave de una tabla 1:1 y cuándo se usa un array.

- banditore tiene tablas 1:1 (`customer_profile.user_id`, `vendor_profile.user_id`) cuya clave es la clave foránea al usuario, con `CASCADE`; `test_primary_key_is_allowed` las rechazaba.
- raccolta guarda los `transports` de una passkey en `ARRAY(Text)` y una lista de enums en un array; presenze, plantillas biométricas en `ARRAY(LargeBinary)`.
- PostgreSQL 17, [Arrays, *Searching in Arrays*](../fuentes/postgresql/array.sgml): «Arrays are not sets; searching for specific array elements can be a sign of database misdesign. Consider using a separate table with a row for each item».
- Una regla de `postgres.md` exigía un índice GiST en toda columna espacial; otra, que un índice que ninguna consulta usa se borre.
- El caso de ejemplo `country.code` de `test_primary_key_rules` contradecía «la clave de una sola columna se llama `id`».
- Ningún workflow de Canone corría las pruebas de `plantilla/server`.

Comprobado en Debian 13 con PostgreSQL 17.12, PostGIS 3.5.2, Valkey, SQLAlchemy 2.1.9, Alembic 1.20.1 y GeoAlchemy2 0.21.0:

| Prueba | Resultado |
| :--- | :--- |
| `ARRAY` de un `Enum` no nativo con `create_constraint=True` | SQLAlchemy da `CompileError`: «cannot produce the CHECK constraint for ARRAY of non-native ENUM» |
| `text[]` con `CHECK (kinds <@ ARRAY['a', 'b'])` | `['a', 'b']` y `[]` entran; `['zzz']` y `['a', NULL]` dan `CheckViolation` |
| La plantilla del servidor como el job nuevo: `ruff`, `pyrefly`, `deptry`, `migrate`, `alembic check` y `pytest` | Pasa: 110 pruebas, una saltada (la de geografía, sin GeoAlchemy2). Con `PRODUCTO_owner` en la URL, la autenticación falla: PostgreSQL guarda el rol en minúsculas |
| Sin los `alembic_helpers` | La autogeneración propone borrar `spatial_ref_sys`; la migración no importa `geoalchemy2` y falla con `NameError`; con el import, falla con `relation "idx_place_spot" already exists` |
| Con los `alembic_helpers` | Crea el índice una vez y `alembic check` no detecta cambios |
| Los hechos que enlazan las convenciones de «Tipos» | `'abcdef'::varchar(3)` da `abc` sin error, e insertarlo en `varchar(3)` falla; `'…10:00+05'::timestamp` da `10:00` sin la zona; en `America/New_York`, sumar `1 day` y `24 hours` el 7 de marzo de 2026 da horas distintas, y `2026-01-31 + 1 month` da el 28 de febrero; `ALTER TYPE … DROP VALUE` no existe; `1.005::numeric(5,2)` da `1.01` |

## Decisión

1. **Una tabla cuyas filas amplían una a una las de otra lleva como clave la clave foránea a esa tabla**, con `ON DELETE CASCADE` y sin id propio. «La clave primaria de una sola columna se llama `id`» vale para la que no es clave foránea.
2. **Una lista cuyos elementos se buscan uno por uno va en una tabla con una fila por elemento**, no en un array: endurece *Searching in Arrays*, con su razón.
3. **Una lista de valores enumerados es `text[]` con un `CHECK` que use `<@`.** En el servidor, el `Enum` del array lleva `create_constraint=False` y la tabla declara el `CHECK`; `test_enums_are_checked_text` exige ese `CHECK`.
4. **El índice GiST deja de ser obligatorio en toda columna espacial:** rige el `spatial_index` por defecto de GeoAlchemy2, y una columna que no se busca puede ir sin índice. `test_geography_columns` mira solo `geography` y 4326.
5. **El caso de ejemplo de un código estándar** llama `id` a su clave.
6. **El job `server` de `infra.yml`** corre sobre `plantilla/server` los pasos del job `server` de la plantilla del CI, sin la pieza en Java ni la geografía, con los roles en minúsculas en las URL.

## Consecuencias

- Las tablas 1:1 de banditore cumplen sin cambios.
- Un cambio de `plantilla/server` que rompe sus pruebas falla en el CI de Canone, no recién en un producto.
- `geo_point()` y `geo_line()` siguen creando siempre el índice: una columna sin índice todavía no se puede declarar con ellas.

## Descartado

- **Id propio más una clave foránea `UNIQUE` en una tabla 1:1:** una columna y un índice de más.
- **Prohibir los arrays:** obliga a una tabla para listas que se leen y escriben enteras.
- **Guardar las listas en `jsonb`:** pierde el tipo de los elementos y su `CHECK`.
- **Conservar el GiST obligatorio:** contradice que un índice que ninguna consulta usa se borre.
- **Reemplazar `PRODUCTO` en la copia del job:** cambia el nombre del proyecto y `uv sync --locked` falla.
