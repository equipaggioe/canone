# ADR-0144 · Vitest corre solo `src/`, Playwright solo `tests/`, y CI corre los dos

- **Estado:** Aceptada
- **Fecha:** 2026-11-14
- **Alcance:** [`plataformas/sveltekit.md`](../plataformas/sveltekit.md), «Proyecto»;
  `plantilla/sveltekit/vite.config.ts`, `plantilla/sveltekit/playwright.config.ts` y el job `web`
  de `plantilla/.github/workflows/ci.yml`

## Contexto

La página ponía las pruebas de Vitest en `src/` y las de Playwright en `tests/`, sin configurar
ninguna de las dos herramientas, y CI no corría Playwright.

Comprobado con Vitest 5.1.0 y `@playwright/test` 1.65.0: sin configurar, `vitest run` toma
`tests/home.spec.ts` y falla al cargarlo, y Playwright toma `src/sum.test.ts`, falla y no lista
ninguna prueba. Como CI no corría Playwright, nadie vio que la CSP no dejaba hidratar la página
([ADR-0143](0143-script-src-es-self-con-los-hashes-de-sveltekit-sin-strict-dynamic.md)).

## Decisión

1. **`vite.config.ts` limita Vitest a `src/**/*.test.ts`.**
2. **`playwright.config.ts` limita Playwright a `tests/`**, y su `webServer` construye la web y la
   levanta con `vite preview` en el puerto 4173.
3. **CI instala Chromium y corre `playwright test`** después de `vitest run`.

## Consecuencias

- Cada herramienta corre solo sus pruebas. Comprobado con las mismas versiones.
- La plantilla, con pnpm 12.18.0, construye, levanta `vite preview` y pasa una prueba que hace clic.
- CI construye la web dos veces: el `webServer` vuelve a construirla.
- Solo se instala Chromium: `playwright.config.ts` no declara `projects`.

## Descartado

- **Un `webServer` que solo levante `vite preview`:** en desarrollo probaría el build anterior, y
  daría resultados falsos sobre código que ya cambió.
