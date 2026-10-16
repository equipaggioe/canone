# ADR-0055 · El cliente de una web SvelteKit se genera con openapi-typescript y llama con openapi-fetch

- **Estado:** Aceptada
- **Fecha:** 2026-10-15
- **Alcance:** la sección «Carga de datos» de [plataformas/sveltekit.md](../plataformas/sveltekit.md#carga-de-datos);
  toda web SvelteKit que consume el `openapi.json` del servidor

## Contexto

`sveltekit.md` pedía generar el cliente con Hey API (`@hey-api/openapi-ts`) y no decía por qué. El
[ADR-0052](0052-el-openapi-se-versiona-y-de-el-generan-sus-modelos-todos-los-clientes.md) solo pide
que los modelos del cable salgan del `openapi.json`. El 2026-10-15, Hey API iba en la versión
`0.99.0`, y su documentación lo declara en desarrollo inicial y pide fijar la versión exacta porque
publica cambios incompatibles.

## Decisión

1. Los tipos de la API se generan del `openapi.json` con `openapi-typescript`, en un solo archivo
   `.d.ts` de `src/lib/api/`.
2. Las llamadas se hacen con `openapi-fetch`, tipado con esos tipos.
3. No se escriben a mano ni los tipos del cable ni una función por ruta.

## Consecuencias

- Lo generado es un archivo de tipos: no hay código generado que revisar en cada cambio.
- El generador va en una versión mayor estable (`7.13.0` el 2026-10-15). `openapi-fetch` sigue en
  `0.x` (`0.17.0`), aunque su superficie es pequeña.
- Una web que quiera validar en tiempo de ejecución o hooks de consulta no los obtiene del
  generador.

## Descartado

- **Hey API:** genera funciones por ruta y plugins que una web de este tamaño no usa, y sigue en
  desarrollo inicial, con cambios incompatibles entre versiones.
- **Tipos escritos a mano:** el ADR-0052 lo prohíbe.
