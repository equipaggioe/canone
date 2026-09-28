# ADR-0015 · El sobre de error sigue el RFC 9457

- **Estado:** Aceptada
- **Fecha:** 2026-09-25
- **Alcance:** [`plataformas/fastapi.md`](../plataformas/fastapi.md), `plantilla/server/src/app/errors.py`,
  `tracing.py` y `schemas/base.py`, y todo cliente que lea errores de la API

## Contexto

El sobre de error era propio: `status`, `detail`, `errorCode`, `errors` como diccionario de campo a
mensajes, y `requestId`. FastAPI no recomienda un formato más allá de `{"detail": ...}`, y el
estándar que cubre el caso es el RFC 9457, *Problem Details for HTTP APIs*.

El sobre propio ya coincidía en `status` y `detail`. El RFC dice que el consumidor usa `type` como
identificador principal del problema, así que `errorCode` y `type` a la vez serían el mismo dato en
dos sitios.

## Decisión

1. El error se responde como *problem details* del RFC 9457, con
   `Content-Type: application/problem+json`.
2. `type` reemplaza a `errorCode` y es lo único sobre lo que ramifica un cliente.
3. `type` es un URI `tag:<dominio>,<año>:<nombre>`. Un error sin semántica propia va con
   `about:blank` y la frase de su código HTTP como `title`, como pide el RFC.
4. Toda respuesta de error sale por un solo punto: los handlers de `errors.py` convierten en
   problem+json la excepción de la app, los `HTTPException` de Starlette, los errores de validación
   y toda excepción sin atrapar.
5. Un error de validación es un 422 con la extensión `errors`, una lista de `{detail, pointer}` como
   el ejemplo de validación del RFC. En query, path y header, `parameter` toma el lugar de
   `pointer`.
6. `requestId` pasa a `traceId`, miembro de extensión con el trace-id del W3C Trace Context, que
   también va en cada línea de log. `traceparent` es el estándar para correlacionar una petición, y
   `X-Request-ID` no está definido en ninguno.
7. El servidor empieza una traza nueva en cada petición y no adopta el `traceparent`
   que llega. El estándar prevé ese reinicio en la puerta de entrada de un sistema, y ningún
   cliente lleva hoy una traza propia que valga la pena continuar.

## Consecuencias

- Cada cliente cambia `errorCode` por `type`, y `requestId` por `traceId`, en su error tipado.
- El handler de las excepciones sin atrapar corre fuera de todo middleware, así que el middleware
  de `tracing.py` no restaura el trace-id al salir: cada petición corre en su propia tarea y su
  contexto muere con ella.
- Un campo anidado o de una lista se señala con el JSON Pointer del RFC 6901, sin inventar una
  convención: `/items/0/name`.
- Un `type` con `tag:` no se resuelve. Si algún día se quiere documentación legible por tipo, pasar
  a un URI resoluble cambia la identidad de cada tipo, y todo cliente que lo compara cambia con él.

## Descartado

- **Mantener `errorCode` con `type` ausente:** sin `type` el RFC asume `about:blank`, que significa
  que el error no dice nada más que su código HTTP, y eso contradice el `errorCode`.
- **Un URN propio como `urn:problem:...`:** el espacio `problem` no está registrado.
- **Un URI absoluto, como `https://api.producto.com/problems/...`:** el RFC lo prefiere "cuando sea
  posible", pero el dominio cambia entre entornos y el cliente compara el `type` para decidir.
- **Una ruta relativa bajo `/problems/`, con `GET /problems/{slug}` para documentar cada tipo:**
  el RFC advierte que un URI relativo se resuelve contra la URI base del documento y puede
  confundir, y obliga a servir una página por cada tipo. El `tag:` cumple la URI absoluta sin eso.
