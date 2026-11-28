# ADR-0253 · Una app de Flutter recibe el 201 con cuerpo como 200, y la operación declara también ese 200

- **Estado:** Aceptada el 2026-11-28 por el desarrollador
- **Fecha:** 2026-11-28
- **Alcance:** [`plataformas/flutter.md`](../plataformas/flutter.md), «OpenAPI y clientes»;
  [`plataformas/transversal.md`](../plataformas/transversal.md), «Reintentos»; `test_conventions.py`
  de `plantilla/server/`

## Contexto

Un `PUT` que crea responde 201, y uno que reemplaza, 200 o 204 (RFC 9110 §9.3.4). La plantilla
declara el 201 y el 200 con el mismo cuerpo en cada `PUT` que crea: vincular una passkey, crear una
cuenta, el código guardado.

swagger_parser 2.4.0, en su modo por defecto (`firstSuccess`), toma de los 2xx con cuerpo solo el
más bajo, el 200, y acepta además los 2xx sin cuerpo: ante el 201 lanza
`ClientException('HTTP 201')` ([`dart_client_mapper.dart`](https://raw.githubusercontent.com/Carapacik/swagger_parser/2.4.0/swagger_parser/lib/src/dart/dart_client_mapper.dart)). Comprobado en banditore el
2026-11-27, con una prueba sobre el `passkeyLink` generado: el `PUT` que vincula una passkey nueva
falla en la app.

## Decisión

1. El `http.Client` de una app de Flutter entrega como 200 un 201 que trae cuerpo.
2. Una operación cuyo 201 lleva cuerpo declara también el 200, con el mismo cuerpo, y lo responde al
   reemplazar el recurso. `test_created_body_is_also_the_replaced_one` lo comprueba en el
   `openapi.json` de cada servidor.

## Consecuencias

- Las llamadas del cliente generado no cambian, y el arreglo vive en un solo lugar, como la
  conversión de los errores en problem+json.
- La app no distingue «creado» de «reemplazado»: el cuerpo es el mismo recurso, y el `PUT` es
  idempotente.
- La regla 1 se borra cuando swagger_parser acepte cada 2xx declarado con el mismo cuerpo.
- No cubre una operación con dos 2xx sin cuerpo, como `PUT /api/account/password`, con 201 y
  204: el cliente generado acepta solo el 201 ([pendiente](../pendientes/dos-exitos-sin-cuerpo-en-swagger-parser.md)).

## Descartado

- `response_mode: allStatuses` de swagger_parser: cambia todas las operaciones a un resultado
  sellado por status, y cada llamada necesita un `switch` con variantes 4XX y 5XX que nunca llegan,
  porque el `http.Client` ya las convierte en `ProblemException`.
- Esperar un arreglo de swagger_parser: deja sin crear recursos a las apps hasta otra versión.
- dio o retrofit, que aceptan cualquier 2xx: rehacen la red de `flutter.md`, el `http.Client` y
  `RetryClient`.
- Responder 200 también al crear: RFC 9110 §9.3.4 exige el 201.
