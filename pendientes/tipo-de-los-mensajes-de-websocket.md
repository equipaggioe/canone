# El valor de `type` de un mensaje de WebSocket

Tema pendiente: **sin decidir**. Salió de la revisión de `transversal.md` del [ADR-0211](../adr/0211-transversal-escribe-entero-cada-criterio-de-wcag-la-api-lleva-la-fecha-sin-hora-y-la-zona-y-tokens-dice-lo-que-no-sigue-de-dtcg.md): «WebSocket» dice que un mensaje es `{type, data}` en camelCase, pero no cómo se escribe el valor de `type`.

## Estado (verificado 2026-11-21)

| Repositorio | Valores de `type` |
| :--- | :--- |
| `concordia` | `message.send` |
| `equipaggio` | `alive`, y los que pasa `gateway.py` |
| `presenze` | `ready`, `changed` |

## Qué empeora sin decidirlo

- Cada repositorio, y cada sesión, elige una forma distinta, y un cliente que comparte código entre productos tiene que conocer las dos.

## Propuestas

1. El valor de `type` va en snake_case, como los valores de un enum de «OpenAPI y clientes».

Falta: que el desarrollador lo confirme, y después escribirlo en «WebSocket».
