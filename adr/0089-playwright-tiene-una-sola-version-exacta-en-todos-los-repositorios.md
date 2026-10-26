# ADR-0089 · Playwright tiene una sola versión exacta en todos los repositorios

- **Estado:** Aceptada
- **Fecha:** 2026-10-26
- **Alcance:** «Pruebas» de [`plataformas/sveltekit.md`](../plataformas/sveltekit.md) y
  `scripts/verificar.py`

## Contexto

Cada versión de Playwright descarga sus propios navegadores, y los repositorios declaraban
`^1.49.0`, `^1.55.0` y `^1.63.0`, que npm resolvía en 1.61.1 y 1.63.0. La carpeta de navegadores
tenía dos Chromium completos, cada uno con su versión sin interfaz: 1148 y 1243, unos 1.2 GB.

## Decisión

1. Todos los repositorios usan la misma versión de Playwright, la más nueva.
2. *(propuesta)* La versión va exacta en `package.json`, sin rango.
3. *(propuesta)* La regla va en «Pruebas» de `sveltekit.md` y alcanza todo `package.json` del
   repositorio que declare `playwright` o `@playwright/test`, también los que no son de SvelteKit.
4. *(propuesta)* `verificar.py` lo comprueba.

## Consecuencias

- Hay un solo juego de navegadores para todos los repositorios. Playwright borra los de una versión
  cuando ya ninguna instalación la usa.
- Subir de versión cambia `sveltekit.md` y `PLAYWRIGHT` de `verificar.py`, y se actualizan todos
  los `package.json` en la misma pasada.
- Comprobado con 1.64.1: `npx playwright --version` da 1.64.1 en los cinco `package.json` que lo
  declaran, y las 206 pruebas de `banditore/landing` pasan. Al instalar Chromium 1248, Playwright
  borró el 1243.

## Descartado

- **Un rango, como `^1.64.1`:** npm lo resuelve según el día de la instalación, y dos repositorios
  terminan con navegadores distintos.
- **La versión de cada repositorio:** deja un juego de navegadores por versión, como antes.
