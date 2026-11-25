# ADR-0247 · swagger_parser genera los modelos y el cliente de la API en Flutter

- **Estado:** Aceptada. El usuario pidió reevaluarla y aplicarla si se sostenía (2026-11-25)
- **Fecha:** 2026-11-25
- **Alcance:** [`flutter.md`](../plataformas/flutter.md), «OpenAPI y clientes», y
  [`stack.md`](../stack.md)

## Contexto

swagger_parser estaba aplicado desde el 2026-11-11 de forma provisional: la 2.1.1 no generaba con el
`openapi.json` del servidor, porque fallaba con un campo opcional de Pydantic
([#489](https://github.com/Carapacik/swagger_parser/issues/489), cerrado el 2026-11-16).

El generador tiene que leer OpenAPI 3.1, rechazar un campo y un valor de enum que no conoce
([transversal.md](../plataformas/transversal.md#openapi-y-clientes)), y dar modelos de freezed, que
recomienda la [arquitectura de Flutter](../fuentes/flutter/architecture-recommendations.yml), y un
cliente de `package:http`.

Comprobado el 2026-11-25 con Flutter 3.47.5, Dart 3.13 y el `openapi.json` de la plantilla, salvo
tonik, que se probó el 2026-11-11 con un esquema mínimo:

| Generador | Resultado |
| :--- | :--- |
| swagger_parser 2.4.0 | Genera 93 archivos y compila sin avisos. `FailureView` acepta un valor válido y una IP `null`, y rechaza un campo de más, un enum desconocido, un campo que falta y un tipo equivocado |
| openapi-generator 7.27.0, `dart` | Genera, y no compila: 8 errores |
| openapi-generator 7.27.0, `dart-dio` con json_serializable o con freezed | build_runner falla. Los dos piden dio |
| swagger_dart_code_generator 4.1.1 | build_runner falla con `List<FieldError>?`. Pide chopper |
| space_gen 1.6.0 | Compila, pero leer una unión lanza `UnimplementedError`, y no revisa los campos de más |
| tonik 0.11.1 | Genera y compila, pero acepta un campo desconocido |

Con `serializer` y `http_client` fuera de `generation`, swagger_parser 2.4.0 falla con `Unknown option`.

## Decisión

1. **swagger_parser genera los modelos del cable y el cliente de la API**, con freezed y
   `package:http`, y deja de ser provisional.
2. `swagger_parser.yaml` lleva las dos opciones en `generation`.

## Consecuencias

- Rechazar un campo desconocido depende de que el servidor declare `additionalProperties: false`.
- Una unión de dos tipos, como `ipAddress`, IPv4 o IPv6, sale como una clase que la envuelve.
- La serie 2.x es del 2026-11-10 y casi todo el trabajo es de una persona: una versión nueva se prueba
  con el `openapi.json` de la plantilla antes de subirla.

## Descartado

- **openapi-generator, el de Android:** en Dart no compila con el contrato del servidor.
- **swagger_dart_code_generator, space_gen y tonik:** por lo que muestra la tabla.
- **Un script propio:** hay que escribirlo y mantenerlo, y swagger_parser ya cumple todo.
