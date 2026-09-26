# ADR-0015 · El sobre de error sigue el RFC 9457

- **Estado:** Aceptada
- **Fecha:** 2026-09-25
- **Alcance:** `server/app/schemas/base.py`, `server/app/core/`, y todo cliente que lea errores de la
  API

## Contexto

El sobre de error era propio: `status`, `detail`, `errorCode`, `errors` como diccionario de campo a
mensajes, y `requestId`. FastAPI no recomienda un formato más allá de `{"detail": ...}`, así que
por el [ADR-0014](0014-una-pagina-se-escribe-desde-la-recomendacion-oficial.md) vale la práctica
establecida: el RFC 9457, *Problem Details for HTTP APIs*.

El sobre propio ya coincidía en `status` y `detail`. El RFC dice que el consumidor usa `type` como
identificador principal del problema, así que `errorCode` y `type` a la vez serían el mismo dato en
dos sitios.

## Decisión

1. El error se responde como *problem details* del RFC 9457, con
   `Content-Type: application/problem+json`.
2. `type` reemplaza a `errorCode` y es lo único sobre lo que ramifica un cliente. El enum
   `ProblemType` reemplaza a `ErrorCode`.
3. `title` es un resumen fijo por tipo. `requestId` pasa a `traceId`, miembro de extensión con el
   trace-id del W3C Trace Context: el header `traceparent` es el estándar para correlacionar un
   request, y `X-Request-ID` no está definido en ninguno.
4. *(propuesta)* `type` es una ruta completa bajo `/problems/`, estable entre versiones de la API.
5. *(propuesta)* `errors` es una lista de `{detail, pointer}`, con un JSON Pointer al campo, como el
   ejemplo de validación del RFC.
6. *(propuesta)* La validación de Pydantic sale con `type` `/problems/validation-error`.
7. Un error sin semántica propia va con `about:blank` y la frase de su código HTTP como `title`,
   como pide el RFC.
8. `GET /problems/{slug}` responde la documentación legible de cada tipo, como pide el RFC. El
   `title`, el `status` y la descripción de cada `ProblemType` están en un solo lugar, `PROBLEMS`,
   del que leen esa ruta y `AppError`.
9. Toda operación declara en OpenAPI sus errores 4XX, 5XX y 422 como `ProblemDetails` con
   `application/problem+json`.

## Consecuencias

- `ErrorResponse` pasa a `ProblemDetails` en `app/schemas/base.py`, que es canónico.
- Cada cliente cambia `errorCode` por `type`, y `requestId` por `traceId`, en su error tipado.
- `app/core/tracing.py`, canónico, toma el trace-id del `traceparent` o empieza una traza, y lo
  pone en el log y en el error.
- Un campo anidado o de una lista se señala sin inventar una convención: `#/items/0/name`.
- FastAPI documenta el `model` de una respuesta bajo el tipo de medio de la ruta, `application/json`,
  así que `PROBLEM_RESPONSES` apunta también `application/problem+json` al mismo esquema, y en
  `openapi.json` el error figura con los dos.

## Descartado

- **Mantener `errorCode` con `type` ausente:** sin `type` el RFC asume `about:blank`, que significa
  que el error no dice nada más que su código HTTP, y eso contradice el `errorCode`.
- **Un URN propio como `urn:problem:...`:** el espacio `problem` no está registrado.
- **Un URI absoluto, como `https://api.producto.com/problems/...`:** el RFC lo prefiere "cuando sea
  posible", pero el dominio cambia entre entornos y el cliente compara el `type` para decidir.
