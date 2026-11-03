# SvelteKit

Una superficie web con SvelteKit y UnoCSS.

## Proyecto

Estándar: [*Project structure*](../fuentes/sveltekit/project-structure.md) de SvelteKit.

- Node es el de Debian 13, y solo se usa para construir.
- SvelteKit es la versión 3, y su configuración va en `vite.config.ts`: rechaza `svelte.config.js`
  y el alias `$lib`, que pasa a `#lib` ([ADR-0112](../adr/0112-sveltekit-es-la-version-3-y-se-configura-en-vite-config.md)).
- pnpm maneja las dependencias. No deja importar un paquete que no esté declarado.
- `package.json` declara la versión exacta de pnpm en `packageManager`, como `pnpm@10.34.6`:
  `pnpm/action-setup` la toma de ahí en CI, y falla si no la encuentra.
- TypeScript va en modo strict, y `svelte-check` lo revisa.
- Prettier formatea, con `prettier-plugin-svelte` y líneas de 99, y ESLint revisa con
  `eslint-plugin-svelte`.

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

Plantilla: [`plantilla/sveltekit/`](../plantilla/sveltekit/): `.prettierrc`, que se copia sin
editar, y `vite.config.ts`, `uno.config.ts` y `.gitignore`, puntos de partida.

## Carga de datos

Estándar: [*Loading data*](../fuentes/sveltekit/load.md) de SvelteKit.

- Los datos de la API se cargan en `load` universales (`+page.ts`, `+layout.ts`). En producción no
  hay servidor de SvelteKit que corra un `load` de servidor.
- Los tipos de la API se generan del OpenAPI de [fastapi.md](fastapi.md) con `openapi-typescript`,
  y las llamadas se hacen con `openapi-fetch`. Ni los tipos ni una función por ruta se escriben a
  mano.

## Opciones de página

Estándar: [*Page options*](../fuentes/sveltekit/page-options.md) de SvelteKit.

## Estado

Estándares: [*State management*](../fuentes/sveltekit/state-management.md) de SvelteKit y, de
Svelte, [`$state`](../fuentes/svelte/state.md), [`$derived`](../fuentes/svelte/derived.md),
[`$effect`](../fuentes/svelte/effect.md), [`$props`](../fuentes/svelte/props.md) y
[`$bindable`](../fuentes/svelte/bindable.md).

- El estado compartido son clases con `$state` en módulos `.svelte.ts` de `src/lib/state/`.

## Accesibilidad

Estándar: la opción `--fail-on-warnings` de [`sv check`](../fuentes/svelte/sv-check.md) de Svelte.

Contrato: [transversal.md](transversal.md#accesibilidad).

- `svelte-check` corre con `--fail-on-warnings`. Las advertencias `a11y_*` de la
  [lista del compilador](https://raw.githubusercontent.com/sveltejs/svelte/main/documentation/docs/98-reference/.generated/compile-warnings.md) rompen CI.

## Código por SMS

Estándar: [*WebOTP API*](../fuentes/wicg/webotp.bs) de WICG.

Contrato: [transversal.md](transversal.md#código-por-sms).

- El campo del código lleva `autocomplete="one-time-code"`: Safari no implementa WebOTP y llena el
  código por ese atributo.

## CSP

Estándares: de OWASP, el
[*Content Security Policy Cheat Sheet*](../fuentes/owasp/Content_Security_Policy.md) y el párrafo
sobre la CSP de *X-XSS-Protection* del
[*HTTP Security Response Headers Cheat Sheet*](../fuentes/owasp/HTTP_Headers.md), y el requisito
V3.2.2 de [ASVS 5.0](../fuentes/owasp/ASVS_V3_Web_Frontend_Security.md); y
[CSP Level 3](../fuentes/w3c/csp3.bs) de W3C.

- La CSP la genera SvelteKit con `kit.csp` en modo `hash`, sobre `default-src 'self'`. El script de
  arranque de SvelteKit va en línea y necesita su hash.
- La CSP lleva el host de las teselas en `img-src`.
- Con un formulario de pago incrustado, la CSP lleva los dominios que documenta su pasarela en
  `script-src`, `frame-src` y `connect-src`.

## Estilos

Estándares: de UnoCSS, el [archivo de configuración](../fuentes/unocss/guide-config-file.md), el
[preset Wind4](../fuentes/unocss/presets-wind4.md) y el
[plugin de Vite](../fuentes/unocss/integrations-vite.md), enteros, y las entradas `presets`,
`preflights` y `theme` de la [configuración](../fuentes/unocss/config-index.md) y del
[tema](../fuentes/unocss/config-theme.md).

- El preset es Wind4. Trae el reset y genera las variables CSS del tema.
- Los tokens van en el `theme` de `uno.config.ts`, sin tamaños literales fuera de él. Los colores
  son `colors`, generado en `src/lib/colors.ts`, y sus variables CSS entran como preflight desde
  `colorsCss`, con el modo oscuro de `prefers-color-scheme`.

Contrato: [transversal.md](transversal.md#tema).
- Las clases de utilidad se escriben en archivos `.svelte`. UnoCSS no lee `.ts` por defecto.

## Idiomas

Estándares: de Paraglide, [*Basics*](../fuentes/paraglide/basics.md),
[*Compiling Messages*](../fuentes/paraglide/compiling-messages.md),
[*Locale Detection*](../fuentes/paraglide/strategy.md) y
[*SvelteKit i18n*](../fuentes/paraglide/sveltekit.md).

Contrato: [transversal.md](transversal.md#idiomas).

## Mapas

Contrato: [transversal.md](transversal.md#mapas).

- El mapa usa Leaflet.
- El contenido de un popup se arma con texto o con nodos del DOM, nunca con HTML que traiga datos
  del usuario: Leaflet inserta como HTML el que recibe.

## Push

Estándares: las secciones *Permission*, *PushManager interface*, *PushMessageData interface* y
*Events* de la [*Push API*](../fuentes/w3c/push-api.html) de W3C; el
[*Notifications API Standard*](../fuentes/whatwg/notifications.bs) de WHATWG, y el párrafo sobre la
Cache API de *Cache-Control* del
[*HTTP Security Response Headers Cheat Sheet*](../fuentes/owasp/HTTP_Headers.md) de OWASP.

Contrato: [transversal.md](transversal.md#push).

- El service worker muestra el mensaje declarativo en el evento `push` y abre su `navigate` al
  tocarlo: Safari lo muestra sin el service worker, pero Chrome y Firefox todavía no.

## Pruebas

Estándares: [*Getting Started*](../fuentes/vitest/guide.md) y
[*Features*](../fuentes/vitest/features.md) de Vitest.

- Las pruebas en el navegador usan Playwright 1.64.1, con la versión exacta en `package.json`. La
  misma versión va en todo `package.json` del repositorio que declare Playwright: cada versión
  descarga sus propios navegadores.

## Adaptador

Estándar: [*Static site generation*](../fuentes/sveltekit/adapter-static.md) de SvelteKit.

- El adaptador es `adapter-static`. Las páginas públicas se prerenderizan; las que piden sesión
  llevan `ssr = false` y las sirve el `fallback` `200.html`. Contradice la documentación, que
  recomienda el `fallback` solo en casos puntuales: esas páginas no necesitan SEO, dependen de los
  datos del usuario, y el servidor es FastAPI, sin Node para renderizarlas.

## Cómo se hace cumplir

| Qué | Con qué |
|---|---|
| Las advertencias `a11y_*` | `svelte-check --fail-on-warnings` en CI |
| Playwright 1.64.1 | [`scripts/verificar.py`](../scripts/verificar.py) |
| La versión exacta de pnpm en `packageManager` | [`scripts/verificar.py`](../scripts/verificar.py) |
| SvelteKit 3, sin `svelte.config.js` | [`scripts/verificar.py`](../scripts/verificar.py) |
