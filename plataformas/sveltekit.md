# SvelteKit

> **En desarrollo; no se implementa:** [README.md](README.md#en-desarrollo).

Una superficie web con SvelteKit y UnoCSS.

## Proyecto

Estándar: [*Project structure*](../fuentes/sveltekit/project-structure.md) de SvelteKit.

- Node es el 26.13.0, la última LTS, y solo se usa para construir.
- `package.json` declara estas versiones exactas, sin `^` ni `~`:
  - SvelteKit 3.1.1, `@sveltejs/adapter-static` 4.0.1, Svelte 5.57.3, Vite 8.3.6 y `@sveltejs/vite-plugin-svelte` 7.3.1.
  - TypeScript 6.0.3, `svelte-check` 4.7.8 y `@types/node` 26.6.6.
  - Prettier 3.9.10, `prettier-plugin-svelte` 4.1.1, ESLint 10.14.0, `eslint-plugin-svelte` 3.24.1, `typescript-eslint` 8.72.1, `@eslint/js` 10.0.1, `globals` 17.14.0 y `eslint-config-prettier` 10.1.8.
  - UnoCSS 66.12.0, Paraglide 3.2.1, `openapi-typescript` 7.13.0, `openapi-fetch` 0.17.0, Leaflet 1.9.4 y `@types/leaflet` 1.9.22.
  - Vitest 5.1.0, Playwright 1.65.0 y `@axe-core/playwright` 4.14.0.
- pnpm maneja las dependencias. No deja importar un paquete que no esté declarado.
- `package.json` declara la versión exacta de pnpm en `packageManager`, `pnpm@12.18.0`: `pnpm/action-setup` la toma de ahí en CI, y falla si no la encuentra.
- TypeScript va en modo strict, y `svelte-check` lo revisa. Es la 6 y no la 7: SvelteKit 3.1.1 y `svelte-check` 4.7.8 piden `^6`.
- Prettier formatea, con `prettier-plugin-svelte`, tabulaciones, comillas simples, sin coma final y líneas de 99.
- ESLint revisa con `@eslint/js`, `typescript-eslint` y `eslint-plugin-svelte`, con las variables globales del navegador y de Node de `globals`. `eslint-config-prettier` apaga las reglas que chocan con Prettier.
- `eslint.config.js` ignora lo que ignora `.gitignore`, con `includeIgnoreFile`, y `.prettierignore` ignora `pnpm-lock.yaml`: sin eso, los tipos generados no pasan `typescript-eslint` y el lockfile no pasa `prettier --check`.

```text
<pieza>/
  .gitignore
  .prettierignore
  .prettierrc
  eslint.config.js
  package.json
  pnpm-lock.yaml
  tsconfig.json
  uno.config.ts       el preset y los tokens
  vite.config.ts      el adaptador y la CSP
  messages/
  project.inlang/
  src/
    app.html
    hooks.server.ts
    hooks.ts
    lib/
      colors.ts
      api/            los tipos de openapi-typescript y el cliente de openapi-fetch
      components/
      state/          las clases con $state, en módulos .svelte.ts
    routes/
    service-worker/
  static/
  tests/
```

Plantilla: [plantilla/sveltekit/](../plantilla/sveltekit/): `.prettierrc`, que se copia sin editar, y `vite.config.ts`, `uno.config.ts`, `eslint.config.js`, `.gitignore` y `.prettierignore`, puntos de partida.

## Carga de datos

Estándar: [*Loading data*](../fuentes/sveltekit/load.md) de SvelteKit.

Contrato: [transversal.md](transversal.md#openapi-y-clientes).

- Los datos de la API se cargan en `load` universales (`+page.ts`, `+layout.ts`). En producción no hay servidor de SvelteKit que corra un `load` de servidor, y por eso no rigen *Cookies*, *Headers*, *Implications for authentication* ni *Using getRequestEvent*.
- Una página prerenderizada no carga datos de la API en su `load`: el build llama a la API y falla si no responde, y el HTML muestra el dato del momento del build hasta que el navegador vuelve a correr el `load`.
- Los tipos de la API se generan con `openapi-typescript` en `src/lib/api/schema.d.ts`, que no se versiona: generados, no pasan `prettier --check`. El script `api` de `package.json` es `openapi-typescript ../server/openapi.json -o src/lib/api/schema.d.ts`, y `dev` y `check` empiezan por `pnpm api && `. CI lo corre antes de `svelte-check`.
- Las llamadas se hacen con `openapi-fetch`, sin una función por ruta escrita a mano. En un `load`, el cliente recibe el `fetch` del evento: con el `fetch` global, `invalidate(url)` no vuelve a correr ese `load`.

## Opciones de página

Estándar: [*Page options*](../fuentes/sveltekit/page-options.md) de SvelteKit.

- Las páginas públicas se prerenderizan, y las que piden sesión llevan `ssr = false` y `prerender = false`: si heredan el `prerender = true` de un layout, una ruta dinámica a la que no llega ningún enlace rompe el build. Contradice *ssr*, que no lo recomienda en la mayoría de los casos: esas páginas no necesitan SEO, dependen de los datos del usuario, y el servidor es FastAPI, sin Node para renderizarlas.

## Componentes

Estándar: [*Best practices*](../fuentes/svelte/best-practices.md) de Svelte, salvo *$state*, *$derived*, *$effect*, *$props* y *Context*, que rigen en «Estado», y *Using JavaScript variables in CSS* y *Styling child components*, en «Estilos».

## Estado

Estándares: [*State management*](../fuentes/sveltekit/state-management.md) de SvelteKit y, de Svelte, [$state](../fuentes/svelte/state.md), [$props](../fuentes/svelte/props.md) y las partes *$state*, *$derived*, *$effect*, *$props* y *Context* de [*Best practices*](../fuentes/svelte/best-practices.md).

- El estado compartido son clases con `$state` en módulos `.svelte.ts` de `src/lib/state/`, y un layout entrega cada instancia con `createContext`. Endurece *Context*, que lo propone, y deja sin efecto el último párrafo de *Using state and stores with context*, que permite un módulo compartido sin SSR: desde un módulo, lo que escribe una página prerenderizada pasa a las otras del build.
- La expresión de `$derived` no tiene efectos secundarios. [Svelte 5.57.3](https://raw.githubusercontent.com/sveltejs/svelte/svelte@5.57.3/documentation/docs/02-runes/03-$derived.md)

## Accesibilidad

Estándar: [*Accessibility*](../fuentes/sveltekit/accessibility.md) de SvelteKit, salvo *The "lang" attribute*, que rige en «Idiomas».

Contrato: [transversal.md](transversal.md#accesibilidad).

- `svelte-check` corre con `--fail-on-warnings`. Las advertencias `a11y_*` de la [lista del compilador](https://raw.githubusercontent.com/sveltejs/svelte/svelte@5.57.3/documentation/docs/98-reference/.generated/compile-warnings.md) rompen CI, y ningún `svelte-ignore` las apaga: con él, la advertencia desaparece sin dejar rastro.
- Cada página tiene una prueba de Playwright que corre `@axe-core/playwright` con las etiquetas `wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa` y `wcag22aa`, y falla con cualquier violación: el compilador no ve el contraste de la página dibujada.

## Código por SMS

Contrato: [transversal.md](transversal.md#código-por-sms).

- El campo del código lleva `autocomplete="one-time-code"`: Safari no implementa WebOTP y llena el código por ese atributo.
- Donde el navegador implementa WebOTP, el código se pide con `navigator.credentials.get` y `otp: { transport: ['sms'] }`. [WebOTP](https://raw.githubusercontent.com/WICG/web-otp/7c4a606a085b44d9de75001f7e801f07a4d85f8c/index.bs)

## CSP

Estándares: de OWASP, el [*Content Security Policy Cheat Sheet*](../fuentes/owasp/Content_Security_Policy.md) y el párrafo sobre la CSP de *X-XSS-Protection* del [*HTTP Security Response Headers Cheat Sheet*](../fuentes/owasp/HTTP_Headers.md), y el requisito V3.2.2 de [ASVS 5.0](../fuentes/owasp/ASVS_V3_Web_Frontend_Security.md); y la sección *Authoring Considerations* de [CSP Level 3](../fuentes/w3c/csp3.bs) de W3C.

- La CSP la genera SvelteKit con la opción `csp` de `sveltekit()` en modo `hash`, sobre `default-src 'self'`. El script de arranque de SvelteKit va en línea y necesita su hash.
- La CSP lleva el host de las teselas en `img-src`.
- Con un formulario de pago incrustado, la CSP lleva los dominios que documenta su pasarela en `script-src`, `frame-src` y `connect-src`.

## Estilos

Estándares: de UnoCSS, el [preset Wind4](../fuentes/unocss/presets-wind4.md), entero, y el modo `global` y las secciones *Svelte* y *Sveltekit* del [plugin de Vite](../fuentes/unocss/integrations-vite.md); y las partes *Using JavaScript variables in CSS* y *Styling child components* de [*Best practices*](../fuentes/svelte/best-practices.md) de Svelte.

Contrato: [transversal.md](transversal.md#tema).

- El preset es Wind4. Trae el reset y genera las variables CSS del tema.
- La configuración va en `uno.config.ts`, y no en `vite.config.ts`: funciona mejor con el editor y las integraciones. [UnoCSS 66.12.0](https://raw.githubusercontent.com/unocss/unocss/v66.12.0/docs/guide/config-file.md)
- Los tokens van en el `theme` de `uno.config.ts`, sin tamaños literales fuera de él. Los colores son `colors`, generado en `src/lib/colors.ts`, y sus variables CSS entran como preflight desde `colorsCss`, con el modo oscuro de `prefers-color-scheme`.
- Las clases de utilidad se escriben en archivos `.svelte`. UnoCSS no lee `.ts` por defecto.
- `uno.config.ts` fija `separators: [':']`. Con los separadores por defecto, `:` y `-`, un atajo como `link-primary` u `open-panel` se lee como una variante seguida de una clase, y no se genera, sin error.

## Idiomas

Estándares: de Paraglide, [*Basics*](../fuentes/paraglide/basics.md), [*Compiling Messages*](../fuentes/paraglide/compiling-messages.md) y [*Locale Detection*](../fuentes/paraglide/strategy.md); y la parte *The "lang" attribute* de [*Accessibility*](../fuentes/sveltekit/accessibility.md) de SvelteKit.

Contrato: [transversal.md](transversal.md#idiomas).

- `paraglideVitePlugin` va en `vite.config.ts`, con `outdir: './src/lib/paraglide'` y `emitTsDeclarations: true`: los mensajes se generan al construir, y el editor ve los que cambian. `src/lib/paraglide` no se versiona, y CI construye antes de `svelte-check`, que lo necesita.
- `app.html` lleva `<html lang="%lang%" dir="%dir%">`, y un `handle` de `src/hooks.server.ts` los reemplaza dentro de `paraglideMiddleware`: cada página prerenderizada declara su idioma. El `handle` no reasigna `event.request`, que en SvelteKit 3 es de solo lectura.
- `reroute`, en `src/hooks.ts`, quita el idioma de la URL con `deLocalizeUrl`.
- Los tipos `Handle` y `Reroute` se importan de `@sveltejs/kit/hooks`: `@sveltejs/kit` no los exporta.
- `paths.relative` es `false`: con el `fallback`, una ruta relativa a un recurso daría 404 en una URL con idioma.
- Un enlace que cambia de idioma lleva `data-sveltekit-reload`: el documento y el idioma del cliente quedan iguales.
- `@types/node` va en `devDependencies`: el `tsconfig.json` que genera sv declara los tipos de `node`, y sin ellos `svelte-check` avisa.

## Mapas

Contrato: [transversal.md](transversal.md#mapas).

- El mapa usa Leaflet.
- El contenido de un popup se arma con texto o con nodos del DOM, nunca con HTML que traiga datos del usuario: Leaflet inserta como HTML el que recibe.

## Push

Estándares: las secciones *Permission*, *PushManager interface*, *PushMessageData interface* y *Events* de la [*Push API*](../fuentes/w3c/push-api.html) de W3C; el [*Notifications API Standard*](../fuentes/whatwg/notifications.bs) de WHATWG, y el párrafo sobre la Cache API de *Cache-Control* del [*HTTP Security Response Headers Cheat Sheet*](../fuentes/owasp/HTTP_Headers.md) de OWASP.

Contrato: [transversal.md](transversal.md#push).

- El service worker muestra el mensaje declarativo en el evento `push` y abre su `navigate` al tocarlo: Safari lo muestra sin el service worker, pero Chrome y Firefox todavía no.

## Pruebas

- Las pruebas en el navegador usan Playwright. La misma versión va en todo `package.json` del repositorio que declare Playwright: cada versión descarga sus propios navegadores.
- `.vitest` va en `.gitignore`: guarda artefactos generados. [Vitest 5.1.0](https://raw.githubusercontent.com/vitest-dev/vitest/v5.1.0/docs/guide/index.md)
- En una prueba concurrente, los snapshots y las aserciones usan el `expect` de su contexto. [Vitest 5.1.0](https://raw.githubusercontent.com/vitest-dev/vitest/v5.1.0/docs/guide/features.md)

## Adaptador

Estándar: [*Static site generation*](../fuentes/sveltekit/adapter-static.md) de SvelteKit.

- El adaptador es `adapter-static`, y el `fallback` `200.html` sirve las páginas con `ssr = false` de [Opciones de página](#opciones-de-página). Contradice *fallback*, que lo recomienda solo en casos puntuales, por las mismas razones.

## Cumplimiento

| Convención | Herramienta |
| :--- | :--- |
| Las advertencias `a11y_*` | `svelte-check --fail-on-warnings` en CI |
| Ningún `svelte-ignore` de una advertencia `a11y_*` | [scripts/verificar.py](../scripts/verificar.py) |
| La misma versión de Playwright en todo `package.json` | [scripts/verificar.py](../scripts/verificar.py) |
| Node en CI, pnpm en `packageManager` y las versiones exactas de «Proyecto» | [scripts/verificar.py](../scripts/verificar.py) |
| Los tipos de la API salen de `server/openapi.json` | `pnpm api` en CI, antes de `svelte-check` |
| El script `api`, y que `dev` y `check` lo corran primero | [scripts/verificar.py](../scripts/verificar.py) |
| `includeIgnoreFile` en `eslint.config.js` y `pnpm-lock.yaml` en `.prettierignore` | [scripts/verificar.py](../scripts/verificar.py) |
| `separators: [':']` en `uno.config.ts` | [scripts/verificar.py](../scripts/verificar.py) |
