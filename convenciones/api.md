# Convención: la API

`schemas/base.py` es un archivo canónico y hoy es idéntico en los seis repositorios. Vive en
[`plantilla/server/app/schemas/base.py`](../plantilla/) y se copia sin editar.

## Forma de los datos

- **Entrada y salida en camelCase.** `alias_generator=to_camel`, con `validate_by_name` y
  `validate_by_alias`: el servidor acepta las dos formas al entrar y siempre responde en camelCase.
  Así los clientes TypeScript y Dart no traducen nombres.
- `bytes` se serializa en base64.
- Fechas en ISO 8601 con zona.

## Bases de schema

| Clase | Para qué | Config |
|---|---|---|
| `SchemaBase` | Salida | `from_attributes=True` |
| `SchemaInputBase` | Entrada | `extra="forbid"` — un campo de más es un error, no algo que se ignora |
| `QueryParamsBase` | Parámetros de query | |

`extra="forbid"` es la aplicación directa de «sin fallbacks»: un cliente que manda un campo mal
escrito se entera en el momento.

## Prefijo y rutas

- Prefijo `/api`, aplicado en `include_router`. Sin `v1`.
- Un router por recurso, en plural: `/api/vehicles`, `/api/trips`.
- Verbos HTTP para las operaciones; nada de `/api/getVehicles`.
- Las rutas de operación interna van bajo `/api/backoffice/...`.

## Respuestas

| Caso | Cuerpo |
|---|---|
| Un recurso | El schema del recurso, sin envoltorio |
| Una lista paginada | `PageResponse[T]`: `items` + `meta` |
| Un error | `ErrorResponse` |

`PageMeta` calcula `totalPages`, `hasNext` y `hasPrev` como campos computados: el cliente no los
recalcula.

Paginación: `page` (>= 1), `perPage` (1 a 200, por defecto 50), `sort`, `order` (`asc` / `desc`).

## Errores

```json
{
  "status": 422,
  "detail": "El correo ya está registrado",
  "errorCode": "EMAIL_TAKEN",
  "errors": { "email": ["Ya está registrado"] },
  "requestId": "..."
}
```

| Campo | Para quién |
|---|---|
| `status` | El HTTP |
| `detail` | La persona: se puede mostrar tal cual |
| `errorCode` | El cliente: es lo único sobre lo que ramifica. Enum `ErrorCode` en `core/enums.py` |
| `errors` | El formulario: errores por campo |
| `requestId` | El log |

**Un cliente nunca ramifica sobre `detail`.** El texto cambia; el `errorCode` es el contrato.

Los handlers se registran en `main.py`, uno por familia de excepción. Un router no arma un error a
mano.

## Enums hacia el cliente

`EnumOption` (`value` + `label`) es la forma de mandar un catálogo de enum a un select. El `label`
en español lo produce el servidor: es la misma lista que valida, y así no hay dos traducciones que
se desincronicen.

## Tipos en el cliente web

El servidor exporta `openapi.json` con un script, y la superficie web genera sus tipos a partir de
él. Se commitea el archivo de tipos generado (lo importa el resto del código) y **no** el
`openapi.json` intermedio.

## WebSocket

- Bajo `/ws`, autenticado igual que el resto.
- Cada mensaje lleva un campo de tipo, y el payload es un schema de Pydantic serializado igual que
  una respuesta HTTP: camelCase, mismo formato de fecha.
- Un registro de conexiones en memoria solo sirve con un proceso. Con varios workers se necesita
  pub/sub en Redis, y entonces **Redis es obligatorio**: arrancar con varios workers y sin Redis
  tiene que fallar al arranque, no partir las conexiones en silencio.
