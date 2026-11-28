# ADR-0254 · El cliente de swagger_parser devuelve una variante por status, y los errores los sigue leyendo el `http.Client`

- **Estado:** Aceptada el 2026-11-28 por el desarrollador
- **Fecha:** 2026-11-28
- **Alcance:** [`plataformas/flutter.md`](../plataformas/flutter.md), «OpenAPI y clientes» y
  «Errores»; `scripts/verificar.py`

## Contexto

Un `PUT` que crea responde 201, y uno que reemplaza, 200 (RFC 9110 §9.3.4). swagger_parser 2.4.0,
en su modo por defecto (`first_success`), acepta de los 2xx con cuerpo solo el más bajo, el 200, y
ante el 201 lanza `ClientException('HTTP 201')` ([`dart_client_mapper.dart`](https://raw.githubusercontent.com/Carapacik/swagger_parser/2.4.0/swagger_parser/lib/src/dart/dart_client_mapper.dart)).
Comprobado en banditore el 2026-11-27: el `PUT` que vincula una passkey nueva falla en la app.

Con `response_mode: all_statuses`, comprobado el 2026-11-28 en una copia de `packages/mobile` de
banditore, con respuestas simuladas sin el `http.Client` de la app de por medio:

| Respuesta | Resultado |
| :--- | :--- |
| 201 con su cuerpo | La variante del 201, con su valor |
| problem+json con una extensión desconocida | La variante del error, con la extensión aparte |
| problem+json con `detail` de otro tipo | `_TypeError` |
| problem+json sin `traceId` | `MissingRequiredKeysException` |
| 502 en HTML | `FormatException` |

## Decisión

1. `swagger_parser.yaml` lleva `response_mode: all_statuses`, y quien llama al cliente generado
   toma el valor de las variantes 2xx.
2. El `http.Client` de la app sigue convirtiendo una respuesta que no es 2xx en la excepción tipada
   del sobre: las variantes de error que genera swagger_parser no cumplen las reglas del cliente de
   «Errores» de `transversal.md`. Las demás variantes son un error de programación.

## Consecuencias

- El 201 llega con su status, sin que nada lo convierta.
- Toda operación devuelve un resultado sellado, también la que tiene un solo 2xx, y cada llamada lo
  abre con un `switch`.
- Si swagger_parser acepta un día cada 2xx declarado en su modo por defecto, se vuelve a él quitando
  esa línea y los `switch`.

## Descartado

- Que el `http.Client` entregue el 201 como 200: compensa al generador cambiando el status de una
  respuesta, en lugar de usar el modo que el generador ofrece para varias respuestas.
- Esperar un arreglo de swagger_parser: deja a las apps sin crear recursos hasta otra versión.
- Que las variantes de error reemplacen la conversión del `http.Client`: fallan ante las respuestas
  de la tabla.
- Responder 200 también al crear: RFC 9110 §9.3.4 exige el 201.
