# El problem+json en los modelos que genera cada cliente

Tema pendiente: **decidido y sin construir**. Salió del [ADR-0211](../adr/0211-transversal-escribe-entero-cada-criterio-de-wcag-la-api-lleva-la-fecha-sin-hora-y-la-zona-y-tokens-dice-lo-que-no-sigue-de-dtcg.md): un cliente ignora una extensión desconocida de un problem+json ([transversal.md](../plataformas/transversal.md#errores)), y falla ante un campo desconocido en las demás respuestas del servidor.

## Estado (verificado 2026-11-21)

| Pieza | Estado |
| :--- | :--- |
| `plantilla/server/openapi.json` | `Problem`, `ValidationProblem` y `FieldError` declaran `additionalProperties: false` |
| «OpenAPI y clientes» de `flet.md` | Genera `extra="forbid"` en cada esquema que declara `additionalProperties: false`, también en `Problem` |
| Flutter, SvelteKit, Android y Qt | Sin revisar cómo trata su generador un campo de más en `Problem` |

## Qué empeora sin construirlo

- Un problem+json con una extensión nueva hace fallar al cliente al leer el error, y el usuario ve un error de lectura en vez del texto del error.

## Propuestas

1. El servidor declara `Problem` y `ValidationProblem` sin `additionalProperties: false`, y su prueba de `openapi.json` lo comprueba.
2. O cada página de cliente dice que su modelo del problem+json ignora los campos que no conoce.

Falta: elegir una, escribirla en la página de cada pieza y probarla.
