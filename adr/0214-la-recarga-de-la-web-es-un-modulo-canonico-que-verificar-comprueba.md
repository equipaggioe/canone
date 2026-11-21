# ADR-0214 · La recarga de la web es un módulo canónico que `verificar.py` comprueba

- **Estado:** Aceptada. El usuario pidió resolver lo que había quedado abierto del [ADR-0213](0213-la-web-no-falla-ante-un-campo-desconocido-se-recarga-al-cambiar-de-version-y-todo-el-problem-json-queda-abierto.md) (2026-11-21)
- **Fecha:** 2026-11-21
- **Alcance:** `sveltekit.md`, `plantilla/sveltekit/` y `scripts/verificar.py`

## Contexto

El ADR-0213 dejó la recarga de la web sin herramienta que la compruebe, y sin comprobar qué pasa con la PWA.

Comprobado el 2026-11-21 con SvelteKit 3.2.0, Vite 8.3.8, adapter-static 4.0.1 y Chromium: se construye la app con la versión `a`, se navega entre dos páginas para que su código quede cargado, se despliega el build `b` y se vuelve a navegar. Sin `reloadOnNewVersion()`, la página siguiente muestra `a`; con ella, muestra `b`.

Ni las reglas de «Service worker» ni los service workers de `concordia` y `equipaggio` guardan el build ni atienden `fetch`. Por eso la navegación completa llega al servidor y trae el build nuevo.

## Decisión

1. La recarga vive en `src/lib/version.ts`, que se copia sin editar: `reloadOnNewVersion()` llama a `beforeNavigate`, y cuando `updated.current` es `true` hace una navegación completa.
2. `verificar.py` comprueba que la copia sea igual a la de la plantilla y que el `+layout.svelte` raíz de cada superficie llame a `reloadOnNewVersion()`, sin contar una llamada comentada.

## Consecuencias

- Cada superficie SvelteKit copia `src/lib/version.ts` y lo llama desde su layout raíz: hasta entonces, `verificar.py` falla.
- Si un service worker llega a guardar el build, la recarga puede traer el viejo. Eso se decide si la web llega a funcionar sin conexión.

## Descartado

- **Escribir el `beforeNavigate` en cada layout:** el texto de la regla no se puede comprobar, y una copia mal escrita recarga mal sin que nadie lo note.
- **Una prueba de Playwright en cada repositorio:** pide dos builds y un servidor por prueba, para comprobar un código que no cambia entre repositorios.
