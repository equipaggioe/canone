# ADR-0215 · Una fecha sin hora entra al servidor solo como `AAAA-MM-DD`

- **Estado:** Aceptada. El usuario eligió lo recomendado para que una herramienta compruebe la fecha sin hora (2026-11-21)
- **Fecha:** 2026-11-21
- **Alcance:** `fastapi.md` y con `server/`

## Contexto

El [ADR-0211](0211-transversal-escribe-entero-cada-criterio-de-wcag-la-api-lleva-la-fecha-sin-hora-y-la-zona-y-tokens-dice-lo-que-no-sigue-de-dtcg.md) fijó que una fecha sin hora viaja como `full-date` de RFC 3339. Comprobado con Pydantic 2.14.3: un campo `date` sale como `"2026-01-08"`, pero acepta también `1767830400` y `"2026-01-08T00:00:00Z"`. Un cliente que manda otra forma pasaría sin que nadie lo note.

La zona horaria y el `type` de WebSocket quedan sin herramienta. Que un texto sea una zona es cuestión de significado, y la plantilla del servidor no tiene mensajes de WebSocket.

## Decisión

1. Un campo de fecha sin hora es `Day`, del esquema base, que solo lee una fecha o una cadena `AAAA-MM-DD`, como `Timestamp` con la fecha y hora.
2. `test_schema_dates_are_days` falla con un `date` de un esquema que no es `Day`, y `test_day_takes_only_a_full_date` comprueba lo que `Day` lee y escribe.

## Consecuencias

- La plantilla no tiene ningún campo de fecha sin hora: `Day` espera al primer repositorio que lo use.

## Descartado

- **Dejar `date`:** el servidor aceptaría en silencio lo que la regla no permite, en contra de «Sin fallbacks» de `principios.md`.
