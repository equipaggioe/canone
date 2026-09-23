# PostgreSQL y PostGIS

Cómo se modelan los datos. PostgreSQL es la única base, y los modelos usan sus tipos directamente en
vez de los genéricos de SQLAlchemy: nada tiene que correr sobre otro motor.

## `models/base.py` es un archivo canónico

Se copia de [`plantilla/`](../plantilla/server/app/models/base.py) sin editar. Un tipo propio del
dominio (`Amount`, `TaxRate`, `ExchangeRate`) se declara **en otro archivo**, no dentro del
canónico.

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
para un total agregado; para eso se declara un `NUMERIC(14, 2)` propio. Una tasa fiscal necesita
seis decimales: con dos, una retención de dos terceras partes (10.666667 %) se trunca y el importe
no cuadra.

Un importe **opcional** se declara a mano y sin `server_default`: dejarle el `"0.00"` convierte «no
aplica» en «cero», que en un documento fiscal no es lo mismo.

## Enums

`class X(str, Enum)` en `core/enums.py`, y la columna con `StringEnumType(X)`, que produce
`VARCHAR` + `CHECK`.

**`create_constraint=True` es obligatorio y no es el valor por defecto.** Desde SQLAlchemy 1.4 vale
`False`, con lo cual `native_enum=False` deja un TEXT pelado: `validate_strings` solo valida del lado
de Python, y la base acepta cualquier cadena escrita por SQL directo, una carga masiva o un job de
mantenimiento.

No se usa el tipo `ENUM` nativo de PostgreSQL: agregar un valor exige `ALTER TYPE` y no se puede
quitar ninguno.

Que agregar un valor al enum pida una migración es deseable: en estos dominios, cambiar el conjunto
de valores permitidos **es** un cambio de esquema y conviene que se note.

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

## Idempotencia

Cuando un efecto no se puede aplicar dos veces —acreditar un pago, consumir un cupón—, **el árbitro
es la base, no el código**: se inserta una fila con un `UNIQUE` sobre el identificador del evento
dentro de la misma transacción que aplica el efecto, y si el `UNIQUE` la rechaza, el evento ya se
procesó.

Comprobar primero y luego insertar no sirve: dos llegadas concurrentes pasan las dos la
comprobación —ninguna ve la fila de la otra, que todavía no existe— y ambas aplican el efecto.

## Migraciones

- Alembic, autogeneradas y **siempre revisadas a mano**: no detecta renombres (los ve como drop +
  add, y eso pierde datos), ni cambios de CHECK, ni índices GiST.
- Una migración por commit que cambia el esquema.
- **Las revisiones se generan en local y se commitean; en el servidor solo se aplican**
  (`alembic upgrade head`). Autogenerar contra la base desplegada produce revisiones a partir de un
  modelo que quizá ni está commiteado.
- `alembic/versions/` queda fuera de ruff: son archivos generados.
- Mientras un producto no esté en producción, si una migración se complica el camino correcto es
  rehacer la base, no escribir una migración defensiva.

## Retención

Una tabla que crece con el uso **declara su ventana al nacer**, junto a su regla de borrado. Una
variable por tabla, y **`0` significa retención indefinida**: cero es una decisión escrita, la
ausencia de la variable es un olvido.

Las bitácoras siguen además el ADR-0008: se escriben en la transacción de la acción que registran,
**ninguna API las escribe ni las edita**, y los valores anteriores se guardan con lista blanca por
tabla y por campo. Sin la lista blanca, la bitácora se vuelve un segundo almacén de datos
personales que sobrevive al derecho de supresión.

Hoy se borra por edad. **La forma correcta a volumen es particionar por mes y soltar la
partición**: un `DELETE` masivo genera WAL, deja bloat y exige VACUUM. Es la meta declarada, no una
obligación mientras no haya volumen que lo justifique.

## Borrado

Cada entidad declara explícitamente qué pasa con sus hijos: `ON DELETE CASCADE` en la FK o borrado
en el servicio, pero escrito. Antes de cerrar una entidad nueva se prueban los caminos de purgado y
borrado, igual que los de su entidad hermana.

Una fila que representa algo externo que se invalidó —una suscripción de push caducada, un
dispositivo desvinculado— se **desactiva**, no se borra: `is_active = false` dice «no la uses» sin
perder el rastro de qué hubo.
