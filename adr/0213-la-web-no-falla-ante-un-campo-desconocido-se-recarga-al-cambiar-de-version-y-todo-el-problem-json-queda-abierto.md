# ADR-0213 · La web no falla ante un campo desconocido: se recarga al cambiar de versión, y todo el problem+json queda abierto

- **Estado:** Aceptada. El usuario eligió que la web se recargue al cambiar de versión, y pidió comprobar y arreglar lo que hiciera falta (2026-11-21)
- **Fecha:** 2026-11-21
- **Alcance:** [plataformas/transversal.md](../plataformas/transversal.md), `sveltekit.md`, `fastapi.md`, `android.md` y con `server/`

## Contexto

Comprobado el 2026-11-21:

- swagger_parser 2.3.0 genera `disallowUnrecognizedKeys: true` en un esquema cerrado y `false` en uno abierto. Con freezed 4.0.3 y json_serializable 6.15.2, el modelo de Flutter falla con `UnrecognizedKeysException` ante un campo de más en `HealthEvents`. Con el `openapi.json` del [ADR-0212](0212-un-problem-json-deja-pasar-una-extension-desconocida-y-el-type-de-websocket-va-en-snake-case.md), `Problem` acepta una extensión; con el anterior, fallaba.
- openapi-fetch 0.17.0 devuelve una respuesta con un campo que el esquema no tiene, sin error: la web no valida nada en ejecución.
- La web sale en el mismo artefacto que el servidor ([despliegue.md](../plataformas/despliegue.md#versiones)). Una pestaña abierta o la PWA siguen con el build viejo después de un despliegue. Según la documentación de SvelteKit 3.2.0, SvelteKit detecta una versión nueva y pone `updated.current` en `true`, pero solo recarga sola si la navegación falla.
- El ADR-0212 dejó `FieldError` cerrado. El `Json` aparte de Android ignora un miembro desconocido en todo el problem+json, también dentro de `errors`, así que Flutter, Flet y Qt fallaban donde Android no.

## Decisión

1. La web queda fuera de «un cliente falla ante un campo que no conoce». A cambio, el `+layout.svelte` raíz hace una navegación completa con `beforeNavigate` cuando `updated.current` es `true`.
2. `FieldError` lleva `extra="ignore"`, como `Problem` y `ValidationProblem`: ningún cliente falla ante un miembro desconocido de un problem+json. Lo prueba `test_problems_let_extensions_through`.

## Consecuencias

- La web no ve un error de contrato en ejecución. Corre el build que sale con su servidor, y lo cambia en la navegación siguiente cuando el servidor cambia.
- Ninguna herramienta comprueba la recarga: la plantilla de SvelteKit no tiene `+layout.svelte`.

## Descartado

- **Validar cada respuesta de la web con Ajv contra `openapi.json`:** suma una dependencia y trabajo en cada respuesta, y no evita que una PWA vieja siga corriendo, solo la hace fallar.
- **Dejar `FieldError` cerrado:** Android lo leería distinto que los demás clientes.
