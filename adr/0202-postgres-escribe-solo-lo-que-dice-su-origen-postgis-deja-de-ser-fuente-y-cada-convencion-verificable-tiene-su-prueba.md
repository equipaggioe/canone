# ADR-0202 · `postgres.md` escribe solo lo que dice su origen, PostGIS deja de ser fuente y cada convención verificable tiene su prueba

- **Estado:** Aceptada. El usuario pidió escribir los cambios de los veredictos de la revisión (2026-11-20)
- **Fecha:** 2026-11-20
- **Alcance:** [plataformas/postgres.md](../plataformas/postgres.md), «Base de datos» y «Migraciones» de [plataformas/fastapi.md](../plataformas/fastapi.md), `fuentes/` y `plantilla/server/tests/test_conventions.py`

## Contexto

Se revisó `postgres.md` con los cinco pasos de [plataformas/README.md](../plataformas/README.md#revisión). Cada fila de «Cumplimiento» se probó con tablas armadas para pasar o fallar, en una copia de la plantilla del servidor, en Debian 13 con PostgreSQL 17.12 y PostGIS 3.5.2, SQLAlchemy 2.1.9 y GeoAlchemy2 0.21.0.

| Prueba | Resultado |
| :--- | :--- |
| `test_primary_key_is_allowed` | Aceptaba una clave de tres `text`; la página dice «par» |
| `test_strings_are_text` | `ARRAY(String(10))` pasaba |
| `test_datetimes_are_aware` | `time with time zone` pasaba: la fila no decía si cubría la regla de `timestamp` o la de `time with time zone` |
| `test_foreign_keys_declare_on_delete` | `ondelete="cascade"`, válido y conforme, fallaba |
| `test_foreign_keys_are_indexed` | Una clave foránea cubierta solo por un índice parcial pasaba. Con solo ese índice, la consulta con que PostgreSQL comprueba la clave hace `Seq Scan`; con uno completo, `Bitmap Index Scan` |
| `smallint` fuera de la clave, `json`, `timestamptz` sin `_at`, clave de una columna que no se llama `id`, índice repetido sobre la clave, `money`, tabla `pg_x` | Ninguna prueba fallaba |
| Un `Geography` compartido en un `Annotated` | La columna `nullable=True` sale `NOT NULL` en el DDL |
| `spatial_index` | `True` crea un índice GiST; `False`, ninguno |
| El enum de la `Base` | Sale `TEXT` con `CHECK`, y un valor fuera de la lista da `CheckViolation` |

Contra su origen:

- *Monetary Types* de PostgreSQL no toma posición contra `money`: solo advierte de `lc_monetary`.
- *Partition Maintenance* describe («It is common to want to… add new partitions»), no fija crearlas por delante.
- *Foreign Keys* dice que `SET NULL` y `SET DEFAULT` «can be appropriate if a foreign-key relationship represents optional information»: no usarlos es una excepción, no algo que la fuente establece.
- PostGIS siempre mide `geography` en metros, y que la clave de una tabla particionada incluya sus columnas de partición lo exige PostgreSQL: una sola forma correcta.
- *Tuning Index Usage* de PostGIS pide «regularly vacuum», no `autovacuum`, que es el valor por defecto de PostgreSQL.

Sin esas dos convenciones, *Data Management* de PostGIS quedaba como origen de dos, y no cumple «Aporta».

## Decisión

1. **La clave de una tabla particionada** es su id seguido de las columnas de partición, y la prueba exige ese orden.
2. **PostGIS deja de ser fuente.** Las columnas `geography(<tipo>, 4326)` y su índice GiST quedan como convenciones propias; salen las distancias en metros, que PostGIS fija, y la sección «Mantenimiento». `fuentes/postgis/` se borra.
3. **Lo que es código del servidor va en `fastapi.md`:** `geo_point()`, `geo_line()` y sus alias, en «Base de datos»; los `alembic_helpers` de `env.py`, en «Migraciones», para un servidor que guarda geografía. Sale «El ORM declara las columnas espaciales con GeoAlchemy2», que ya dice `stack.md`.
4. **Una convención con origen dice solo lo que dice su origen:**
   - «Toda clave foránea declara su `ON DELETE`, y nunca `SET NULL` ni `SET DEFAULT`» es propia, con su razón; `CASCADE` o `RESTRICT` según lo que representan las tablas sigue a *Foreign Keys*.
   - Las particiones de los próximos meses son propia, sin origen.
   - «Una columna ancha no va en `INCLUDE`» es un endurecimiento aparte, con la razón de la fuente: una entrada que excede el máximo del índice hace fallar la inserción.
   - «Nunca por herencia ni con vistas `UNION ALL`» lleva la razón de la fuente: no tienen parte de las ventajas de rendimiento del particionado declarativo.
   - «Nunca `money`» sale de *Arbitrary Precision Numbers*, no de *Monetary Types*.
5. **Toda clave foránea encabeza un índice no parcial**, y la prueba no cuenta los parciales.
6. **Cada convención verificable tiene su prueba:** `test_single_keys_are_id`, `test_timestamps_end_in_at`, `test_tables_avoid_pg_prefix`, `test_keys_have_no_twin_index`, `test_json_is_jsonb`, `test_integers_are_not_small`, `test_amounts_are_not_money` y `test_times_have_no_zone`. `test_strings_are_text` mira también el tipo de los elementos de un array, `test_foreign_keys_declare_on_delete` compara sin distinguir mayúsculas, y una clave natural es de dos columnas.

## Consecuencias

- Un repositorio con una columna que rompe una de las convenciones con prueba nueva falla en su CI al copiar la plantilla.
- `postgres.md` ya no tiene sección «Mantenimiento»: `autovacuum` rige por ser el valor por defecto.
- Quedan sin resolver la clave de una tabla 1:1, que ninguna regla admite, y cuándo se usa un array.

## Descartado

- **Conservar PostGIS adoptando más posiciones suyas:** una fuente no se busca para completar el mínimo de «Aporta».
- **Escribir `autovacuum` en `despliegue.md`:** es el valor por defecto y ninguna fuente lo exige.
