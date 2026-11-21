# ADR-0212 · Un problem+json deja pasar una extensión desconocida, y el `type` de WebSocket va en snake_case

- **Estado:** Aceptada. El usuario eligió lo recomendado para el problem+json en los clientes generados, para Android y para el `type` de WebSocket (2026-11-21)
- **Fecha:** 2026-11-21
- **Alcance:** [plataformas/transversal.md](../plataformas/transversal.md), `fastapi.md`, `android.md` y con `server/`

## Contexto

El [ADR-0211](0211-transversal-escribe-entero-cada-criterio-de-wcag-la-api-lleva-la-fecha-sin-hora-y-la-zona-y-tokens-dice-lo-que-no-sigue-de-dtcg.md) dejó al problem+json fuera de «un cliente falla ante un campo que no conoce». Pero `openapi.json` declaraba `additionalProperties: false` en `Problem` y `ValidationProblem`, y datamodel-code-generator, en Flet y en Qt, genera `extra="forbid"` en cada esquema que lo declara. En Android, el `Json` de Retrofit deja `ignoreUnknownKeys` en `false`, y ahí falla cualquier campo desconocido, diga lo que diga el esquema.

`concordia` nombra el `type` de un mensaje de WebSocket con un punto (`message.send`), y `equipaggio` y `presenze`, con palabras sueltas.

## Decisión

1. `Problem` y `ValidationProblem` llevan `extra="ignore"`, y el OpenAPI no les declara `additionalProperties: false`. Lo prueba `test_problems_let_extensions_through`.
2. Android lee el problem+json con un `Json` aparte, con `ignoreUnknownKeys = true`, donde traduce la `HttpException`. Los demás modelos siguen fallando ante un campo desconocido.
3. El valor de `type` de un mensaje de WebSocket va en snake_case, como los valores de un enum.

## Consecuencias

- Flet y Qt generan `Problem` sin `extra="forbid"`, sin cambiar su configuración.
- `concordia` tiene que renombrar `message.send`.

## Descartado

- **Que cada página de cliente escriba su excepción para el problem+json:** son cinco reglas con la configuración de cada generador, cuando el esquema del servidor las resuelve para Flet y Qt.
- **Anotar el `Problem` generado de Android con `@JsonIgnoreUnknownKeys`:** obliga a cambiar la plantilla del generador, y la anotación es experimental.
- **Un `type` con punto por dominio, o en camelCase:** agrega una forma que no es la de los enums de la API.
