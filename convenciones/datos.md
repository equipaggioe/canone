# Convención: datos

PostgreSQL es la única base. Los modelos usan tipos de PostgreSQL directamente, no los genéricos de
SQLAlchemy: nada tiene que correr sobre otro motor.

## `models/base.py` es un archivo canónico

Vive en [`plantilla/server/app/models/base.py`](../plantilla/) y se copia sin editar. Hoy hay seis
copias distintas, y dos de las diferencias son defectos: ver `homologacion.md`, filas 1 y 2.

Si un repositorio necesita un tipo propio (`Amount`, `TaxRate`, `ExchangeRate` en vettore), lo
declara **en otro archivo**, no dentro del canónico.

## Mapa de tipos

| Python | PostgreSQL |
|---|---|
| `bool` | `BOOLEAN` |
| `bytes` | `BYTEA` |
| `date` / `time` | `DATE` / `TIME` |
| `datetime` | `TIMESTAMP(timezone=True)` |
| `dict` / `list` | `JSONB` |
| `float` | `DOUBLE PRECISION` |
| `int` | `INTEGER` |
| `str` | `TEXT` |
| `UUID` | `uuid` |

`str` es `TEXT`, sin longitud. Un límite de negocio se valida en el schema de Pydantic, donde el
error es legible; un `VARCHAR(50)` en la base solo produce un error de driver.

## Alias declarados

| Alias | Columna |
|---|---|
| `PkUuid` | `uuid PRIMARY KEY DEFAULT gen_random_uuid()` |
| `PkBigint` / `PkInt` / `PkSmallint` | Identidad autoincremental |
| `Money` | `NUMERIC(8, 2)` |
| `Percent` | `NUMERIC(5, 2)` |
| `IsActive` | `BOOLEAN DEFAULT true` |
| `CreatedAt` | `TIMESTAMPTZ DEFAULT now()` |
| `UpdatedAt` | `TIMESTAMPTZ DEFAULT now() ON UPDATE now()` |

Importes: nunca `float`. `Money` topa en 999,999.99, que alcanza para una cuota individual pero no
para un total agregado; para eso se declara un `NUMERIC(14, 2)` propio.

Un importe **opcional** se declara a mano y sin `server_default`: dejarle el `"0.00"` convierte «no
aplica» en «cero», que no es lo mismo.

## Enums

`class X(str, Enum)` en `core/enums.py`, y la columna con `StringEnumType(X)`, que produce
`VARCHAR` + `CHECK`.

**`create_constraint=True` es obligatorio y no es el valor por defecto.** Desde SQLAlchemy 1.4 vale
`False`, con lo cual `native_enum=False` deja un TEXT pelado: `validate_strings` solo valida del
lado de Python, y la base acepta cualquier cadena escrita por SQL directo, una carga masiva o un job
de mantenimiento.

No se usa el tipo `ENUM` nativo de PostgreSQL: agregar un valor exige `ALTER TYPE` y no se puede
quitar ninguno.

## Geografía

`Geography(srid=4326)`, no `Geometry`: las distancias salen en metros sin proyectar.

Las columnas se declaran con las funciones `geo_point()` / `geo_line()`, **nunca con un
`Annotated`**. geoalchemy2 guarda `nullable` en la instancia del tipo y la muta al crear cada
columna; un `Annotated` comparte una única instancia entre todas las columnas que lo usan, así que
la última procesada le impone su `nullable` a todas las demás — en silencio, y solo se nota al
generar la migración.

`spatial_index=False` en la declaración: el índice GiST se crea en la migración, donde se elige
sobre qué columnas vale la pena.

## Nombres

| Objeto | Forma | Ejemplo |
|---|---|---|
| Tabla | `snake_case`, plural, inglés | `vehicle_locations` |
| Columna | `snake_case`, inglés | `created_at` |
| Clave foránea | `<singular>_id` | `vehicle_id` |
| Booleano | `is_` / `has_` | `is_active` |
| Instante | `_at` | `deleted_at` |
| Índice | `ix_<tabla>_<columnas>` | `ix_trips_vehicle_id` |
| Restricción | `ck_` / `uq_` / `fk_` + tabla + qué | `uq_users_email` |

## Migraciones

- Alembic, autogeneradas y **siempre revisadas a mano**: no detecta renombres (los ve como drop +
  add, y eso pierde datos), ni cambios de CHECK, ni índices GiST.
- Una migración por commit que cambia el esquema.
- `alembic/versions/` queda fuera de ruff: son archivos generados.
- Ningún repositorio está en producción: si una migración se complica, el camino correcto es
  rehacer la base, no escribir una migración defensiva.

## Borrado

Cada entidad declara explícitamente qué pasa con sus hijos: `ON DELETE CASCADE` en la FK o borrado
en el servicio, pero escrito. Antes de cerrar una entidad nueva se prueban los caminos de purgado y
borrado, igual que los de su entidad hermana — ver `principios.md`.
