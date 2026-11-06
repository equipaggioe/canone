# SvelteKit

> **En desarrollo; no se implementa:** [README.md](README.md#en-desarrollo).

Una superficie web con SvelteKit y UnoCSS.

## Proyecto

Estándar: [*Project structure*](../fuentes/sveltekit/project-structure.md) de SvelteKit.

- Node es el 26.13.0, la última LTS, y solo se usa para construir. No es el de Debian 13, el 20.19.2: SvelteKit 3.1.1 pide `>=22.17`, y Vitest 5.1.0, `^22.12 || ^24 || >=26`.
- Svelte 5.57.3, sv 1.3.0, Vite 8.3.5, `@sveltejs/vite-plugin-svelte` 7.3.1, UnoCSS 66.12.0, Vitest 5.1.0 y Paraglide 3.1.0: `package.json` los declara exactos, con `^` o con `~`.
- SvelteKit es la 3.1.1, y su configuración va en `vite.config.ts`: rechaza `svelte.config.js` y el alias `$lib`, que pasa a `#lib`.
- pnpm maneja las dependencias. No deja importar un paquete que no esté declarado.
- `package.json` declara la versión exacta de pnpm en `packageManager`, `pnpm@12.16.1`: `pnpm/action-setup` la toma de ahí en CI, y falla si no la encuentra.
- TypeScript es la 6.0.3, la que genera sv 1.3.0, y va en modo strict, y `svelte-check` lo revisa.
- Prettier formatea, con `prettier-plugin-svelte` y líneas de 99, y ESLint revisa con `eslint-plugin-svelte`.

```text
<pieza>/
  .prettierrc
  eslint.config.js
  package.json
  pnpm-lock.yaml
  tsconfig.json
  uno.config.ts       el preset y los tokens
  vite.config.ts      el adaptador y la CSP
  src/
    app.html
    lib/
      colors.ts
      api/            los tipos de openapi-typescript y el cliente de openapi-fetch
      components/
      state/          las clases con $state, en módulos .svelte.ts
    routes/
  static/
```

Plantilla: [plantilla/sveltekit/](../plantilla/sveltekit/): `.prettierrc`, que se copia sin editar, y `vite.config.ts`, `uno.config.ts` y `.gitignore`, puntos de partida.

## Carga de datos

Estándar: [*Loading data*](../fuentes/sveltekit/load.md) de SvelteKit.

- Los datos de la API se cargan en `load` universales (`+page.ts`, `+layout.ts`). En producción no hay servidor de SvelteKit que corra un `load` de servidor.
- Los tipos de la API se generan del OpenAPI de [fastapi.md](fastapi.md) con `openapi-typescript`, y las llamadas se hacen con `openapi-fetch`. Ni los tipos ni una función por ruta se escriben a mano.

## Opciones de página

Estándar: [*Page options*](../fuentes/sveltekit/page-options.md) de SvelteKit.

## Estado

Estándares: [*State management*](../fuentes/sveltekit/state-management.md) de SvelteKit y, de Svelte, [$effect](../fuentes/svelte/effect.md) y [$props](../fuentes/svelte/props.md).

- El estado compartido son clases con `$state` en módulos `.svelte.ts` de `src/lib/state/`.
- Un módulo no exporta directamente un `$state` que se reasigna: quien lo importa recibe el contenedor y no el valor. [Svelte 5.57.3](https://raw.githubusercontent.com/sveltejs/svelte/svelte@5.57.3/documentation/docs/02-runes/02-$state.md)
- Un proxy propio envuelve el objeto después de `$state`. [Svelte 5.57.3](https://raw.githubusercontent.com/sveltejs/svelte/svelte@5.57.3/documentation/docs/02-runes/02-$state.md)
- La expresión de `$derived` no tiene efectos secundarios. [Svelte 5.57.3](https://raw.githubusercontent.com/sveltejs/svelte/svelte@5.57.3/documentation/docs/02-runes/03-$derived.md)
- `$bindable` se usa poco: abusar de él vuelve impredecible el flujo de datos. [Svelte 5.57.3](https://raw.githubusercontent.com/sveltejs/svelte/svelte@5.57.3/documentation/docs/02-runes/06-$bindable.md)
- Con `bind:`, el padre no pasa `undefined` a una prop `$bindable` con valor por defecto. [Svelte 5.57.3](https://raw.githubusercontent.com/sveltejs/svelte/svelte@5.57.3/documentation/docs/02-runes/06-$bindable.md)

## Accesibilidad

Contrato: [transversal.md](transversal.md#accesibilidad).

- `svelte-check` corre con `--fail-on-warnings`. Las advertencias `a11y_*` de la [lista del compilador](https://raw.githubusercontent.com/sveltejs/svelte/svelte@5.57.3/documentation/docs/98-reference/.generated/compile-warnings.md) rompen CI.

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

Estándares: de UnoCSS, el [preset Wind4](../fuentes/unocss/presets-wind4.md), entero, y el modo `global` y las secciones *Svelte* y *Sveltekit* del [plugin de Vite](../fuentes/unocss/integrations-vite.md).

Contrato: [transversal.md](transversal.md#tema).

- El preset es Wind4. Trae el reset y genera las variables CSS del tema.
- La configuración va en `uno.config.ts`, y no en `vite.config.ts`: funciona mejor con el editor y las integraciones. [UnoCSS 66.12.0](https://raw.githubusercontent.com/unocss/unocss/v66.12.0/docs/guide/config-file.md)
- Los tokens van en el `theme` de `uno.config.ts`, sin tamaños literales fuera de él. Los colores son `colors`, generado en `src/lib/colors.ts`, y sus variables CSS entran como preflight desde `colorsCss`, con el modo oscuro de `prefers-color-scheme`.
- Las clases de utilidad se escriben en archivos `.svelte`. UnoCSS no lee `.ts` por defecto.

## Idiomas

Estándares: de Paraglide, [*Basics*](../fuentes/paraglide/basics.md), [*Compiling Messages*](../fuentes/paraglide/compiling-messages.md) y [*Locale Detection*](../fuentes/paraglide/strategy.md).

Contrato: [transversal.md](transversal.md#idiomas).

- `paraglideVitePlugin` va en `vite.config.ts`, con `outdir: './src/lib/paraglide'` y `emitTsDeclarations: true`: los mensajes se generan al construir, y el editor ve los que cambian.
- `app.html` lleva `<html lang="%lang%" dir="%dir%">`, y un `handle` de `src/hooks.server.ts` los reemplaza dentro de `paraglideMiddleware`: cada página prerenderizada declara su idioma. El `handle` no reasigna `event.request`, que en SvelteKit 3 es de solo lectura.
- `reroute`, en `src/hooks.ts`, quita el idioma de la URL con `deLocalizeUrl`.
- Los tipos `Handle` y `Reroute` se importan de `@sveltejs/kit/hooks`: `@sveltejs/kit` no los exporta.
- `paths.relative` es `false`: con el `fallback`, una ruta relativa a un recurso daría 404 en una URL con idioma.
- Un enlace que cambia de idioma lleva `data-sveltekit-reload`: el documento y el idioma del cliente quedan iguales.
- `@types/node` va en `devDependencies`: `svelte-check` revisa el `server.js` que genera Paraglide, que usa `async_hooks`.

## Mapas

Contrato: [transversal.md](transversal.md#mapas).

- El mapa usa Leaflet.
- El contenido de un popup se arma con texto o con nodos del DOM, nunca con HTML que traiga datos del usuario: Leaflet inserta como HTML el que recibe.

## Push

Estándares: las secciones *Permission*, *PushManager interface*, *PushMessageData interface* y *Events* de la [*Push API*](../fuentes/w3c/push-api.html) de W3C; el [*Notifications API Standard*](../fuentes/whatwg/notifications.bs) de WHATWG, y el párrafo sobre la Cache API de *Cache-Control* del [*HTTP Security Response Headers Cheat Sheet*](../fuentes/owasp/HTTP_Headers.md) de OWASP.

Contrato: [transversal.md](transversal.md#push).

- El service worker muestra el mensaje declarativo en el evento `push` y abre su `navigate` al tocarlo: Safari lo muestra sin el service worker, pero Chrome y Firefox todavía no.

## Pruebas

- Las pruebas en el navegador usan Playwright 1.64.1, con la versión exacta en `package.json`. La misma versión va en todo `package.json` del repositorio que declare Playwright: cada versión descarga sus propios navegadores.
- `.vitest` va en `.gitignore`: guarda artefactos generados. [Vitest 5.1.0](https://raw.githubusercontent.com/vitest-dev/vitest/v5.1.0/docs/guide/index.md)
- En una prueba concurrente, los snapshots y las aserciones usan el `expect` de su contexto. [Vitest 5.1.0](https://raw.githubusercontent.com/vitest-dev/vitest/v5.1.0/docs/guide/features.md)

## Adaptador

Estándar: [*Static site generation*](../fuentes/sveltekit/adapter-static.md) de SvelteKit.

- El adaptador es `adapter-static`. Las páginas públicas se prerenderizan; las que piden sesión llevan `ssr = false` y las sirve el `fallback` `200.html`. Contradice la documentación, que recomienda el `fallback` solo en casos puntuales: esas páginas no necesitan SEO, dependen de los datos del usuario, y el servidor es FastAPI, sin Node para renderizarlas.

## Cumplimiento

| Convención | Herramienta |
| :--- | :--- |
| Las advertencias `a11y_*` | `svelte-check --fail-on-warnings` en CI |
| Playwright 1.64.1 | [scripts/verificar.py](../scripts/verificar.py) |
| Node en CI, `pnpm@12.16.1` en `packageManager` y las versiones de «Proyecto» | [scripts/verificar.py](../scripts/verificar.py) |
| Sin `svelte.config.js` | [scripts/verificar.py](../scripts/verificar.py) |
