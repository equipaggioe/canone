# ADR-0112 · SvelteKit es la versión 3, y se configura en `vite.config.ts`

- **Estado:** Aceptada
- **Fecha:** 2026-11-02
- **Alcance:** «Proyecto» de [`plataformas/sveltekit.md`](../plataformas/sveltekit.md),
  `plantilla/sveltekit/` y [`scripts/verificar.py`](../scripts/verificar.py)

## Contexto

`plantilla/sveltekit/svelte.config.js` y las copias de `fuentes/sveltekit/` eran de SvelteKit 2, y
ninguna regla fijaba la versión. `sv` 1.x genera SvelteKit 3, que corta con
`config_file_unsupported` al encontrar ese archivo y con `module_removed_lib` al encontrar `$lib`.
Una superficie nueva no podía usar la plantilla.

## Decisión

1. SvelteKit es la versión 3, con `adapter-static` 4.
2. El adaptador y la CSP van en `sveltekit(...)`, en `vite.config.ts`. `plantilla/sveltekit/svelte.config.js`
   sale, y entra `vite.config.ts`.
3. `fuentes/sveltekit/` pasa a la documentación de SvelteKit 3.
4. `verificar.py` falla si una superficie no usa SvelteKit 3 o tiene `svelte.config.js`.

## Consecuencias

- Una superficie en SvelteKit 2 da incumplimientos hasta migrar: mover la configuración a
  `vite.config.ts`, y `$lib` a `#lib`.
- Probado con `sv` 1.2.0, SvelteKit 3 y la plantilla: compila, deja `200.html` y lleva la CSP.

## Descartado

- **Quedarse en SvelteKit 2 con una versión fija de `sv`.** Deja a canone en una versión que ya no es
  la que documenta su fuente.
