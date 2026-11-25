# Generador de los modelos del cable en Flutter

Tema pendiente: se documenta para retomarlo en otra ocasión. **La elección de swagger_parser es provisional**: está aplicada en la página y en la plantilla, pero todavía no se considera una decisión sólida.

## Estado (verificado 2026-11-25)

El [#489](https://github.com/Carapacik/swagger_parser/issues/489) se cerró el 2026-11-16, y **swagger_parser 2.4.0 genera con el `openapi.json` del servidor**. Falta confirmar la elección. Lo que sigue a «De dónde sale el tema» es de antes del arreglo.

Comprobado el 2026-11-25 con Flutter 3.47.5, freezed 4.0.3, json_serializable 6.15.2 y `environment.sdk` en `^3.13.0`, con swagger_parser 2.3.0 y 2.4.0:

| Prueba | Resultado |
| :--- | :--- |
| `dart run swagger_parser` con el [openapi.json](../plantilla/server/openapi.json) de la plantilla | Genera 93 archivos, sin errores |
| `dart run build_runner build` y `dart analyze lib` | Compila, con 0 errores |
| Un campo opcional | Sale como `T?`: `final String? userAgent` |
| `FailureView.fromJson` con un campo o un valor de enum que no conoce | Lo rechaza, con la 2.4.0 |
| `serializer` y `http_client` en el primer nivel de `swagger_parser.yaml` | Falla con `Unknown option`: van en `generation` |

Commits: `9c0aa39` (`extra="forbid"` en el esquema base) y `f0916d0` (swagger_parser en la página, la plantilla y `verificar.py`).

## De dónde sale el tema

[transversal.md](../plataformas/transversal.md#openapi-y-clientes) pide que cada cliente genere del `openapi.json` del servidor los modelos del cable, y que ninguno los escriba a mano. Al reescribir `flutter.md` (2026-11-11) se vio que la página no decía cómo lo cumple la app de Flutter: solo nombraba freezed para los modelos de `domain/models/` y `package:http` para el servicio del cliente de la API. Quedó como pendiente: elegir el generador.

## Qué tiene que cumplir el generador

| Requisito | De dónde sale |
| :--- | :--- |
| Generar los modelos desde `openapi.json`, nunca escribirlos a mano | [transversal.md](../plataformas/transversal.md#openapi-y-clientes) |
| Fallar ante un campo que el cliente no conoce | [transversal.md](../plataformas/transversal.md#openapi-y-clientes) |
| Fallar ante un valor de enum que no conoce | [principios.md](../principios.md#sin-fallbacks): un valor por defecto silencioso esconde el error |
| Leer OpenAPI 3.1, la versión que genera FastAPI | `plantilla/server/openapi.json` |
| Modelos con freezed y cliente con `package:http` | [flutter.md](../plataformas/flutter.md#arquitectura) |

El criterio para elegir es la eficacia y la eficiencia de la herramienta, no quién la recomienda ni el costo de cambiar.

## Cómo se llegó a la elección actual

1. **2026-11-11, primera revisión de `flutter.md`:** quedó como propuesta enlazar «OpenAPI y clientes» de transversal.md y elegir un generador, sin recomendar ninguno.
2. **Opciones sin probar:** se listaron swagger_parser, tonik, openapi-generator, swagger_dart_code_generator y escribir a mano. La recomendación fue swagger_parser con freezed y `package:http`, sujeta a probarlo contra el `openapi.json` del servidor.
3. **Primeras pruebas:** swagger_parser 2.1.1 abortó con el `openapi.json` de la plantilla; la 1.46.0 generó, pero solo con retrofit y dio; tonik generó, pero acepta campos desconocidos. Se intentó probar openapi-generator y el permiso fue denegado. La recomendación cambió a no fijar ningún generador todavía: reportar el error a swagger_parser y, si no lo arreglan, escribir un script propio.
4. **Se pidió reevaluar por eficacia y eficiencia** y avisar del error, o buscar si ya estaba reportado. No lo estaba, y se abrió el #489.
5. **Una prueba más:** con `additionalProperties: false` en el esquema, swagger_parser 2.1.1 rechaza el campo desconocido. Para que eso funcione con el servidor real, `extra="forbid"` pasó al esquema base de la plantilla del servidor.
6. **swagger_parser ya se había aceptado** como la recomendación, así que se aplicó en la página, la plantilla y `verificar.py`.
7. **2026-11-12:** se probaron variantes del esquema para buscar una salida que no dependa del #489 (ver «Lo encontrado el 2026-11-12»).
8. **La elección no se considera sólida todavía.** Este documento la deja escrita para retomarla.

## Opciones evaluadas

### Antes de probar

| Opción | Pro | Contra |
| :--- | :--- | :--- |
| swagger_parser | Dart puro; OpenAPI 3.0 a 3.2; modelos con freezed o json_serializable; cliente con `package:http`; `--check` compara lo generado sin escribir | También genera los clientes; no estaba confirmado cómo trata los campos desconocidos |
| tonik | Dart puro; OpenAPI 3.0 y 3.1 | Versión 0.x; solo se había leído su descripción |
| openapi-generator (en Java) | El más difundido | Necesita el JDK; sus generadores de Dart no usan freezed y `dart-dio` trae dio; soporte de 3.1 sin confirmar |
| swagger_dart_code_generator | Usa json_serializable | Trae chopper en vez de `package:http` |
| Escribirlos a mano | — | Lo prohíbe transversal.md |

### Después de probar

Todo se probó el 2026-11-11 y el 2026-11-12 contra el `openapi.json` de la plantilla, o contra un esquema mínimo cuando la herramienta no generaba con el real.

| Opción | Resultado | Evidencia |
| :--- | :--- | :--- |
| **swagger_parser 2.1.1** | Cumple todo, salvo los campos opcionales del #489 | Comprobado; detalle abajo |
| swagger_parser 1.46.0 | Genera, pero no sirve: los clientes salen solo con retrofit y dio | Comprobado; detalle abajo |
| tonik 0.11.1 | Genera y compila, pero **acepta el campo desconocido** | Comprobado; detalle abajo |
| openapi-generator 7.x (en Java) | **Sin probar**: el permiso para descargar y correr el jar fue denegado | — |
| swagger_dart_code_generator 4.1.1 | **Sin probar**; trae chopper | Leído en pub.dev |
| Un script propio en `scripts/`, como `tokens.py` | Cumpliría todo, porque solo necesita el subconjunto de OpenAPI que produce el servidor de Canone. Hay que escribirlo y mantenerlo | Sin hacer |
| Escribir los modelos a mano | Lo prohíbe transversal.md | — |

### Detalle de las pruebas

**swagger_parser 2.1.1**, con `serializer: freezed` y `http_client: http`:

- Con el `openapi.json` de la plantilla aborta: `Invalid default for FieldError/pointer: Cannot represent FieldErrorPointer as a constant default.` Pasa lo mismo con `serializer: json_serializable` y con `serializer: plain`. Es el #489.
- Con un esquema sin campos opcionales genera, compila con freezed 4.0.3 y json_serializable 6.15.2, y pasa estas pruebas de `flutter test`: lee un modelo válido, rechaza un valor de enum desconocido y, solo si el esquema declara `additionalProperties: false`, rechaza un campo desconocido.
- Sin `additionalProperties: false`, el modelo lleva `disallowUnrecognizedKeys: false` y guarda los campos desconocidos en un mapa `additionalProperties`. Un `disallow_unrecognized_keys: true` global en `build.yaml` no cambia eso, porque el generador escribe la opción en cada clase. Con `additionalProperties: false`, el modelo lleva `disallowUnrecognizedKeys: true`.
- Los modelos usan la sintaxis de constructor primario de Dart 3.13 (`class const Thing({...})`).
- Lo generado no pasa las reglas del analizador de la plantilla: 3 `no_leading_underscores_for_local_identifiers`, 1 `prefer_final_locals` y 2 `non_constant_identifier_names` (como `_read_level`). Por eso `analysis_options.yaml` excluye su carpeta.
- Los enums rechazan un valor desconocido por defecto (`unknown_enum_values: reject`).

**swagger_parser 1.46.0**, con `json_serializer: freezed`:

- Genera con el `openapi.json` de la plantilla, y un campo opcional sale como `String?`.
- Los clientes salen solo con retrofit y dio. build_runner falla sin ellos: `Could not resolve annotation for abstract class HealthClient`.
- Los enums traen un valor `$unknown` por defecto, que se usa ante un valor desconocido; `unknown_enum_value: false` lo quita.
- Los modelos se declaran `@Freezed() class X with _$X`, sin `abstract` ni `sealed`. No está comprobado que compilen con freezed 4.0.3, porque el build falló antes por retrofit.
- `ipAddress` y `details` de `LoggedEvent` salen como `dynamic`.
- Los archivos llevan `// ignore_for_file: type=lint`.

**tonik 0.11.1**, con `--backend http`:

- Genera un paquete aparte, que la app agrega como dependencia por ruta junto a `tonik_util`.
- Rechaza un valor de enum desconocido.
- **Acepta un campo desconocido**, y su documentación (`docs/additional_properties.md`) dice que `additionalProperties: false` no cambia nada.
- Cada campo nullable sale envuelto en una clase propia, como `FieldErrorPointerAnyOfModel`.
- No usa freezed: genera sus propias clases.

## Por qué swagger_parser

- Es la única opción probada que cumple los cinco requisitos, salvo el #489.
- Genera lo que la página ya eligió: freezed para los modelos y `package:http` para el cliente.
- Es Dart puro: no pide el JDK ni otra herramienta en CI.
- Se mantiene activo: los últimos reportes de otras personas se cerraron entre el mismo día y 12 días después (#473, #477 y #476).

**Por qué todavía no es sólida:**
- Hoy no genera con el servidor real.
- La serie 2.x salió el 2026-11-10, con cuatro versiones en dos días (2.0.0, 2.0.1, 2.1.0 y 2.1.1), y el #489 es una regresión respecto de la 1.46.0.
- Que rechace los campos desconocidos depende de que el servidor declare `additionalProperties: false`.
- No se probaron openapi-generator ni swagger_dart_code_generator.

## Los problemas del #489

Son dos, y los dos vienen de la forma en que Pydantic escribe un campo opcional, `str | None = None`, en OpenAPI 3.1: `{"anyOf": [{"type": "string"}, {"type": "null"}], "default": null}`.

| Problema | Qué pasa | Evidencia |
| :--- | :--- | :--- |
| Con `default: null` | La generación aborta: `Invalid default for Thing/note: Cannot represent ThingNote as a constant default.` | Comprobado con los tres serializadores |
| Sin `default` | Genera, pero el campo sale como una clase envoltorio, `ThingNote`, con `hasString`, `hasNull`, `asString` y `asNull`, en vez de `String?`. La 1.46.0 generaba `String?` | Comprobado |

En el `openapi.json` de la plantilla hay 12 campos nullables de un solo tipo, 4 de ellos con `default: null`; uno de tres tipos, `ipAddress` de `LoggedEvent` (IPv4, IPv6 o null), y ningún `$ref` nullable.

### Lo encontrado el 2026-11-12

Al buscar una salida que no dependa del #489, se probaron cinco variantes del campo `note` del esquema mínimo, con swagger_parser 2.1.1, freezed y `package:http`:

| Variante de `note` | Resultado |
| :--- | :--- |
| `{"anyOf": [{"type": "string"}, {"type": "null"}], "default": null}`, la que escribe Pydantic | Aborta |
| `{"anyOf": [{"type": "string"}, {"type": "null"}]}` | Genera la clase envoltorio `ThingNote` |
| `{"type": ["string", "null"], "default": null}` | Genera `final String? note = null` |
| `{"type": ["string", "null"]}` | Genera `final String? note` |
| `{"anyOf": [{"$ref": "#/components/schemas/Owner"}, {"type": "null"}]}`, con o sin `default: null` | Aborta con `default` y envuelve sin él |

Conclusiones:

- La falla está en cómo swagger_parser lee un `anyOf` con un miembro `null`, no en el `default`: sin `default` también sale mal, solo que no aborta.
- La forma `type: [T, "null"]` funciona, y en OpenAPI 3.1 significa lo mismo. Es la base de la opción 1 de «Qué haremos si no hay respuesta».
- Esa forma no existe para un `$ref`: un objeto anidado opcional solo se escribe con `anyOf`, y sigue fallando. Hoy la plantilla no tiene ninguno, pero el primer esquema de respuesta con un objeto opcional lo traería.
- El hallazgo todavía no está en el #489.

## Por qué falla hoy el paso de CI

**Falla por el error de swagger_parser, no por una regla de Canone.** El esquema que lo hace fallar es el que FastAPI y Pydantic escriben para cualquier campo opcional; ninguna convención de Canone lo pide. El ejemplo mínimo del #489 no tiene `additionalProperties`, ni freezed, ni `package:http`, y falla igual con cualquier serializador.

Lo que sí viene de una regla de Canone es **dónde** se ve el fallo. Lo generado no se versiona y CI lo genera en cada corrida, así que un generador que falla rompe CI en el momento. Si lo generado se versionara, el fallo aparecería recién al regenerar. Es lo que pide [principios.md](../principios.md#sin-fallbacks): que falle ruidosamente y en el momento.

La regla de `additionalProperties: false` del servidor no interviene en el #489: hace falta para que el cliente rechace los campos desconocidos.

## El cambio del servidor

- `extra="forbid"` pasó de `InputSchema` al esquema base `Schema` de [schemas/base.py](../plantilla/server/src/app/schemas/base.py). `InputSchema` conserva `from_attributes=False` y `validate_by_name=False`.
- `openapi.json` se regeneró con `python -m app.openapi`: cada esquema de objeto declara ahora `additionalProperties: false`, también los de respuesta (6 líneas nuevas).
- Comprobado: armar una respuesta desde una fila de la base, que tiene columnas de más como `xid`, sigue funcionando, porque con `from_attributes` Pydantic solo lee los campos declarados. Un diccionario con un campo de más se rechaza.
- `ruff format --check` y `ruff check` pasan. De las pruebas del servidor pasan 64; las otras 29 necesitan Postgres y Valkey, que no corrían en la máquina donde se probó, así que **no se corrieron**.

## El aviso

- El 2026-11-11 se abrió el [#489](https://github.com/Carapacik/swagger_parser/issues/489) desde la cuenta de GitHub del autor de Canone, siguiendo la plantilla `bug_report.yml` del repositorio: paquete afectado, entorno (swagger_parser 2.1.1, Dart 3.13.4, Flutter 3.47.5, Windows 10), pasos, esquema mínimo, resultado esperado (`String?`, como en la 1.46.0) y los dos errores. No lleva nada del proyecto.
- Antes de abrirlo se buscaron en los issues los textos «default null», «constant default», «anyOf null» e «Invalid default», y se revisaron los últimos 30: ninguno lo reportaba. El más parecido, el #440 (envoltorios nullables de un `allOf`), está cerrado y trata otro caso.
- Al 2026-11-12 sigue abierto y sin comentarios. La última versión es la 2.1.1, y el último commit del repositorio es del 2026-11-11.

## Qué haremos si no hay respuesta

Es una **propuesta**: no está decidido.

| Opción | Costo | Cubre |
| :--- | :--- | :--- |
| 1. El servidor escribe los nullables de un solo tipo como `type: [T, "null"]`, con una pasada sobre el OpenAPI en `errors.py`, donde ya se agregan los esquemas de los problemas | Una función chica, con su prueba. El esquema no cambia de significado: las dos formas son equivalentes en OpenAPI 3.1 | Los 12 campos de un solo tipo. `ipAddress` quedaría como `type: ["string", "null"]` y perdería el formato, **sin probar**. Un `$ref` nullable seguiría fallando |
| 2. Mandar el arreglo a swagger_parser en un pull request | Entender su generador; sin plazo de que lo acepten | Todo, si lo aceptan |
| 3. El script propio en `scripts/` | El más caro: escribir y mantener un generador | Todo |
| 4. Volver a la 1.46.0 | Rompe `package:http` y obliga a traer retrofit y dio | No sirve |

**Recomiendo** esperar hasta el **2026-11-26**. Si para entonces no hay respuesta ni versión nueva, aplicar la opción 1: es chica, ya está comprobado que swagger_parser la acepta y no cambia el contrato. Si antes aparece un `$ref` nullable que la 1 no cubre, pasar a la 2.

## Preguntas para retomar

- ¿Se confirma swagger_parser, o se prueban antes openapi-generator y swagger_dart_code_generator?
- ¿El cliente de la API también se genera, o se generan solo los modelos y el servicio del cliente se escribe con `package:http`, como decía la página antes?
- ¿`ipAddress` acepta perder el formato con la opción 1, o necesita otra forma?
- ¿Se agrega el hallazgo del 2026-11-12 al #489?

## Para cerrar el tema

1. Cuando salga una versión que arregle el #489: generar con el `openapi.json` de la plantilla y comprobar que no aborta, que un campo opcional sale como `T?` y que se rechazan el campo y el valor de enum desconocidos.
2. Fijar esa versión en el bloque de Flutter de `stack.md` y en `PUB` de `scripts/verificar.py`.
3. Si se aplicó la opción 1, decidir si se queda o se quita, y escribirlo en fastapi.md.
4. Borrar este documento en el mismo commit.

## Cómo repetir las pruebas

Esquema mínimo del #489:

```json
{
  "openapi": "3.1.0",
  "info": {"title": "Repro", "version": "1.0.0"},
  "paths": {
    "/thing": {
      "get": {
        "operationId": "getThing",
        "responses": {"200": {"description": "OK", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Thing"}}}}}
      }
    }
  },
  "components": {
    "schemas": {
      "Thing": {
        "type": "object",
        "required": ["name"],
        "properties": {
          "name": {"type": "string"},
          "note": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": null}
        }
      }
    }
  }
}
```

En una app de Flutter con swagger_parser 2.1.1, freezed 4.0.3, freezed_annotation 3.1.0, json_serializable 6.15.2, json_annotation 4.12.0, build_runner 2.17.1 y http 1.6.0:

```yaml
swagger_parser:
  schema_path: min.json
  output_directory: lib/data/services/api
  generation:
    serializer: freezed
    http_client: http
    page_width: 99
```

```bash
dart run swagger_parser
dart run build_runner build
```

Para las variantes del 2026-11-12, se reemplaza `note` en `min.json` por cada una de la tabla de «Lo encontrado el 2026-11-12», con `Owner` definido como `{"type": "object", "required": ["id"], "properties": {"id": {"type": "string"}}, "additionalProperties": false}` para la del `$ref`, y se vuelve a generar.

Para el rechazo de campos y enums desconocidos: un esquema sin campos nullables, con `additionalProperties: false` en el objeto y un enum, y una prueba que llama a `fromJson` con un campo de más y con un valor de enum que no está en la lista; las dos tienen que lanzar.

Para tonik: `dart pub global activate tonik 0.11.1` y `tonik --package-name=api --spec=openapi.json --backend http`, y un programa que llama a `fromJson` con un campo de más.
