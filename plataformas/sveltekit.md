# SvelteKit

> **En desarrollo; no se implementa:** [README.md](README.md#en-desarrollo).

Una superficie web con SvelteKit y UnoCSS.

## Proyecto

Estándar: [*Project structure*](../fuentes/sveltekit/project-structure.md) de SvelteKit.

- Node solo se usa para construir.
- `package.json` declara las versiones exactas, sin `^` ni `~`.
- TypeScript es la 6 y no la 7: SvelteKit 3.2.0 y `svelte-check` 4.7.8 piden `^6`.
- `@types/node` va en `devDependencies`: el `tsconfig.json` que genera sv declara los tipos de `node`, y sin ellos `svelte-check` avisa. [sv 1.3.0](https://raw.githubusercontent.com/sveltejs/cli/sv%401.3.0/packages/sv/src/addons/eslint.ts)
- pnpm maneja las dependencias. No deja importar un paquete que no esté declarado, aunque otro paquete ya lo traiga: un import que funciona porque otro paquete lo trajo se rompe cuando ese paquete cambia. [pnpm](https://raw.githubusercontent.com/pnpm/pnpm.io/19a2f01816126e8c1140f262674ef9be213ffef1/docs/motivation.md)
- Toda dependencia declarada se usa, en el código o en la configuración.
- CI corre `pnpm exec knip --dependencies` después de `pnpm build`, que escribe `.svelte-kit/`: sin él, knip no resuelve los `./$types`. Falla con una dependencia que no se usa o un paquete importado sin declarar.
- `knip.json` ignora los paquetes sin declarar que knip ve en `tsconfig.json`: toma por paquete el `$app/tsconfig` que extiende SvelteKit 3. [knip 6.45.1](https://raw.githubusercontent.com/webpro-nl/knip/knip%406.45.1/packages/docs/src/content/docs/reference/configuration.md)
- `package.json` declara la versión exacta de pnpm en `packageManager`: `pnpm/action-setup` la toma de ahí en CI, y falla si no la encuentra. [pnpm/action-setup 6.1.1](https://raw.githubusercontent.com/pnpm/action-setup/v6.1.1/README.md)
- `package.json` declara en `imports` `"#lib/*": "./src/lib/*"`: SvelteKit 3 quitó `$lib`. [SvelteKit 3.2.0](https://raw.githubusercontent.com/sveltejs/kit/%40sveltejs/kit%403.2.0/documentation/docs/98-reference/26-%24lib.md)
- Un import de `#lib/` lleva la extensión `.js`, como `#lib/api/client.js`: TypeScript resuelve `imports` como Node, que no completa la extensión. [TypeScript](https://raw.githubusercontent.com/microsoft/TypeScript-Website/4ec663ac4412c3a7086401bd5a8811565589b11d/packages/documentation/copy/en/modules-reference/Reference.md)
- Las pruebas de Vitest van en `src/`, con `.test.ts`, y las de Playwright, en `tests/`.
- `vite.config.ts` limita Vitest a `src/**/*.test.ts`: sin eso toma también las pruebas de Playwright de `tests/`, y falla al cargarlas. [Vitest 5.1.0](https://raw.githubusercontent.com/vitest-dev/vitest/v5.1.0/docs/config/include.md)
- `playwright.config.ts` limita Playwright a `tests/`: sin eso toma también las pruebas de Vitest de `src/`, y falla al cargarlas. [Playwright 1.65.1](https://raw.githubusercontent.com/microsoft/playwright/v1.65.1/docs/src/test-api/class-testconfig.md)
- El código importa de `src/lib/` con `#lib/` ([Project structure, *src*](../fuentes/sveltekit/project-structure.md)).
- En `static/` va solo lo que se sirve con su nombre sin cambios, como `robots.txt`. Lo demás se importa, y Vite le pone un nombre con el hash de su contenido ([Project structure, *static*](../fuentes/sveltekit/project-structure.md)).
- `%sveltekit.body%` va dentro de un `<div>` de `app.html`, y no directo en `<body>`: la hidratación destruye lo que las extensiones del navegador insertan ahí ([Project structure, *src*](../fuentes/sveltekit/project-structure.md)).
- `package.json` declara `@sveltejs/kit`, `svelte` y `vite` en `devDependencies` ([Project structure, *package.json*](../fuentes/sveltekit/project-structure.md)).
- `tsconfig.json` extiende `$app/tsconfig`, la configuración que genera SvelteKit ([Project structure, *tsconfig.json*](../fuentes/sveltekit/project-structure.md)).

```text
<pieza>/
  .gitignore
  .prettierignore
  .prettierrc
  eslint.config.js
  knip.json
  package.json
  playwright.config.ts
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

Plantilla: [plantilla/sveltekit/](../plantilla/sveltekit/): `.prettierrc` y `knip.json`, que se copian sin editar, y `vite.config.ts`, `playwright.config.ts`, `uno.config.ts`, `eslint.config.js`, `.gitignore` y `.prettierignore`, puntos de partida.

## Estilo

- Prettier formatea, con `prettier-plugin-svelte`, tabulaciones, comillas simples, sin coma final y líneas de 99.
- ESLint revisa con `@eslint/js`, `typescript-eslint` y `eslint-plugin-svelte`, con las variables globales del navegador y de Node de `globals`. `eslint-config-prettier` apaga las reglas que chocan con Prettier, y el plugin de `@inlang/paraglide-js/eslint` agrega `paraglide/no-dynamic-message-access`.
- `eslint.config.js` ignora lo que ignora `.gitignore`, con `includeIgnoreFile`, y `.prettierignore` ignora `pnpm-lock.yaml`: sin eso, los tipos generados no pasan `typescript-eslint` y el lockfile no pasa `prettier --check`.

## Tipos

- TypeScript va en modo strict, y `svelte-check` lo revisa.

## Opciones de página

Estándar: [*Page options*](../fuentes/sveltekit/page-options.md) de SvelteKit.

- Las páginas que piden sesión llevan `ssr = false` y `prerender = false`: no necesitan SEO, dependen de los datos del usuario y el servidor es FastAPI, sin Node para renderizarlas. Si heredaran el `prerender = true` del layout raíz, una ruta dinámica a la que no llega ningún enlace rompería el build.
- `trailingSlash` es `'never'`, su valor por defecto: Caddy sirve `/a.html` para `/a` ([despliegue.md](despliegue.md#versiones)) ([Page options, *trailingSlash*](../fuentes/sveltekit/page-options.md)).
- El código que solo corre en el navegador se importa en `+page.svelte` o `+layout.svelte`, nunca en `+page.ts` ni `+layout.ts`, que el build importa en Node ([Page options, *ssr*](../fuentes/sveltekit/page-options.md)).
- Una página se prerenderiza solo si dos usuarios que llegan a ella reciben el mismo contenido del servidor ([Page options, *When not to prerender*](../fuentes/sveltekit/page-options.md)).
- Una página prerenderizada lee `url.searchParams` solo en el navegador, como en `onMount` ([Page options, *When not to prerender*](../fuentes/sveltekit/page-options.md)).
- Una ruta `+server.ts` lleva en su nombre la extensión del archivo que genera, como `sitemap.xml/+server.ts` ([Page options, *Route conflicts*](../fuentes/sveltekit/page-options.md)).

## Carga de datos

Estándar: [*Loading data*](../fuentes/sveltekit/load.md) de SvelteKit.

Contrato: [transversal.md](transversal.md#openapi-y-clientes).

- Una página prerenderizada no carga datos de la API en su `load`: el build llama a la API y falla si no responde, y el HTML muestra el dato del momento del build hasta que el navegador vuelve a correr el `load`.
- Los tipos de la API se generan con `openapi-typescript` en `src/lib/api/schema.d.ts`, que no se versiona: generados, no pasan `prettier --check`. El script `api` de `package.json` es `openapi-typescript ../server/openapi.json -o src/lib/api/schema.d.ts`, y `dev` y `check` empiezan por `pnpm api && `. CI lo corre antes de `svelte-check`.
- Las llamadas se hacen con `openapi-fetch`, sin una función por ruta escrita a mano.
- El cliente no lleva `baseUrl`: las rutas del OpenAPI ya empiezan por `/api`, en el mismo origen que la web ([despliegue.md](despliegue.md#caddy)). En desarrollo, `server.proxy` de `vite.config.ts` manda `/api` a `http://localhost:8000` con `ws: true`, para que también pase el WebSocket.
- Los datos de la API se cargan en `load` universales, en `+page.ts` y `+layout.ts`: en producción no hay servidor de SvelteKit que corra un `load` de servidor ([Loading data, *When to use which*](../fuentes/sveltekit/load.md)).
- En un `load`, el cliente de `openapi-fetch` recibe el `fetch` del evento: solo ese `fetch` registra la URL con la que `invalidate(url)` vuelve a correr el `load` ([Loading data, *Making fetch requests*](../fuentes/sveltekit/load.md) y [*Manual invalidation*](../fuentes/sveltekit/load.md)).
- Un `load` redirige con `redirect()` de `@sveltejs/kit`, fuera de un bloque `try`, que atraparía la redirección ([Loading data, *Redirects*](../fuentes/sveltekit/load.md)).
- Un error de un `load` se lanza con `error()` de `@sveltejs/kit`, con su código de estado ([Loading data, *Errors*](../fuentes/sveltekit/load.md)).
- Un `load` llama a `await parent()` después de pedir lo que no depende de su resultado ([Loading data, *Using parent data*](../fuentes/sveltekit/load.md)).
- Un `load` lee `params` y `url` en su cuerpo, no dentro de una promesa que devuelve: lo que lee después de volver no lo hace correr de nuevo ([Loading data, *Rerunning load functions*](../fuentes/sveltekit/load.md)).
- El `load` universal de una página prerenderizada no devuelve promesas: no se transmiten, y el navegador las vuelve a crear ([Loading data, *Streaming with promises*](../fuentes/sveltekit/load.md)).

## Componentes

Estándares: [*Best practices*](../fuentes/svelte/best-practices.md) y [$props](../fuentes/svelte/props.md) de Svelte, y el capítulo [V3 *Web Frontend Security*](../fuentes/owasp/ASVS_V3_Web_Frontend_Security.md) de ASVS 5.0.

- La expresión de `$derived` no tiene efectos secundarios. [Svelte 5.57.3](https://raw.githubusercontent.com/sveltejs/svelte/svelte@5.57.3/documentation/docs/02-runes/03-$derived.md)
- Los componentes compilan en modo runas: `sveltekit()` lleva `compilerOptions: { runes: true }` ([Best practices, *Avoid legacy features*](../fuentes/svelte/best-practices.md)).
- Una biblioteca externa, como MapLibre GL JS, se sincroniza con el estado con `{@attach}`, no con un `$effect` ([Best practices, *$effect*](../fuentes/svelte/best-practices.md)).
- `{#key}` se usa solo para repetir una transición o una animación cuando cambia una expresión. Para volver a calcular una expresión de un hijo va un `$derived` ([Best practices, *`#key` block*](../fuentes/svelte/best-practices.md)).
- Todo `{#each}` lleva una clave que identifica el elemento, y nunca es el índice ([Best practices, *Each blocks*](../fuentes/svelte/best-practices.md)).
- `$state` va solo en una variable que actualiza un `$effect`, un `$derived` o el template ([Best practices, *$state*](../fuentes/svelte/best-practices.md)).
- Un objeto o un arreglo grande que solo se reasigna, como una respuesta de la API, va en `$state.raw` ([Best practices, *$state*](../fuentes/svelte/best-practices.md)).
- Lo que se calcula de un estado o de una prop es un `$derived`, nunca un `$effect` ni una variable común, que no cambia cuando cambia la prop ([Best practices, *$derived*](../fuentes/svelte/best-practices.md) y [*$props*](../fuentes/svelte/best-practices.md)).
- Un `$effect` no actualiza estado ([Best practices, *$effect*](../fuentes/svelte/best-practices.md)).
- Lo que responde a una interacción va en su manejador o en un `bind:` de función, un valor se registra con `$inspect` y lo externo a Svelte se observa con `createSubscriber`, no con un `$effect` ([Best practices, *$effect*](../fuentes/svelte/best-practices.md)).
- El contenido de un `$effect` no va dentro de `if (browser)`: un `$effect` no corre en el servidor ([Best practices, *$effect*](../fuentes/svelte/best-practices.md)).
- Un evento de `window` o de `document` se escucha con `<svelte:window>` o `<svelte:document>`, no con `onMount` ni con `$effect` ([Best practices, *Events*](../fuentes/svelte/best-practices.md)).
- Un `{#each}` que muta el elemento no lo desestructura ([Best practices, *Each blocks*](../fuentes/svelte/best-practices.md)).
- El código usa runas y no las formas que reemplazan: `$state` y no la reactividad implícita; `$derived` y `$effect` y no `$:`; `$props` y no `export let`, `$$props` ni `$$restProps`; `onclick` y no `on:click`; `{#snippet}` y `{@render}` y no `<slot>`, `$$slots` ni `<svelte:fragment>`; el componente dinámico y no `<svelte:component>`; el import del propio componente y no `<svelte:self>`; `{@attach}` y no `use:`, y arreglos y objetos en `class` y no la directiva `class:` ([Best practices, *Avoid legacy features*](../fuentes/svelte/best-practices.md)).
- Un componente no muta sus props: un cambio sube por una prop de callback, o la prop es `$bindable` ([$props, *Updating props*](../fuentes/svelte/props.md)).
- Las props llevan tipo, y una prop de snippet, como `children`, el tipo `Snippet` de `svelte` ([$props, *Type safety*](../fuentes/svelte/props.md)).
- Lo que se muestra como texto se inserta con la interpolación `{…}` de Svelte, `textContent` o `createTextNode`, nunca con `{@html}` ni `innerHTML` ([ASVS 5.0 §3.2.2](../fuentes/owasp/ASVS_V3_Web_Frontend_Security.md)).

## Estado

Estándar: [*State management*](../fuentes/sveltekit/state-management.md) de SvelteKit.

- El estado compartido son clases con `$state` en módulos `.svelte.ts` de `src/lib/state/`.
- Un layout entrega cada instancia con `createContext`, que da tipos ([State management, *Using state and stores with context*](../fuentes/sveltekit/state-management.md)).
- Lo que debe sobrevivir a una recarga, como los filtros o el orden de una tabla, va en los parámetros de búsqueda de la URL ([State management, *Storing state in the URL*](../fuentes/sveltekit/state-management.md)).
- El estado compartido se entrega por context, nunca desde una variable de un módulo: el build renderiza en el servidor las páginas prerenderizadas, y lo que escribe una pasaría a las otras ([State management, *Avoid shared state on the server*](../fuentes/sveltekit/state-management.md) y [*Using state and stores with context*](../fuentes/sveltekit/state-management.md)).
- El estado compartido usa la reactividad de Svelte 5, no los stores de `svelte/store` ([State management, *Using state and stores with context*](../fuentes/sveltekit/state-management.md)).
- El estado baja de un componente a sus hijos, y no sube ([State management, *Using state and stores with context*](../fuentes/sveltekit/state-management.md)).
- Un `load` no tiene efectos secundarios: devuelve sus datos, y no escribe en un estado compartido ([State management, *No side-effects in load*](../fuentes/sveltekit/state-management.md)).

## Accesibilidad

Estándar: [*Accessibility*](../fuentes/sveltekit/accessibility.md) de SvelteKit.

Contrato: [transversal.md](transversal.md#accesibilidad).

- `svelte-check` corre con `--fail-on-warnings`. Las advertencias `a11y_*` de la [lista del compilador](https://raw.githubusercontent.com/sveltejs/svelte/svelte@5.57.3/documentation/docs/98-reference/.generated/compile-warnings.md) rompen CI, y ningún `svelte-ignore` las apaga: con él, la advertencia desaparece sin dejar rastro.
- Cada página tiene una prueba de Playwright que corre `@axe-core/playwright` con las etiquetas `wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa` y `wcag22aa`, y falla con cualquier violación: el compilador no ve el contraste de la página dibujada.
- Cada página pone en `<svelte:head>` un `<title>` único y descriptivo: SvelteKit lo anuncia al navegar ([Accessibility, *Route announcements*](../fuentes/sveltekit/accessibility.md)).
- Un `goto` con `reset: false` deja en la página el elemento que tiene el foco ([Accessibility, *Focus management*](../fuentes/sveltekit/accessibility.md)).

## Código por SMS

Contrato: [autenticacion.md](autenticacion.md#código-por-sms).

- El campo del código lleva `autocomplete="one-time-code"`: Safari no implementa WebOTP y llena el código por ese atributo. [BCD 8.1.8](https://raw.githubusercontent.com/mdn/browser-compat-data/v8.1.8/api/OTPCredential.json)
- Donde el navegador implementa WebOTP, el código se pide con `navigator.credentials.get` y `otp: { transport: ['sms'] }`. [WebOTP](https://raw.githubusercontent.com/WICG/web-otp/7c4a606a085b44d9de75001f7e801f07a4d85f8c/index.bs)
- La llamada a `navigator.credentials.get` lleva un `AbortSignal`, y el componente la cancela al desmontarse: SvelteKit navega sin recargar, y la petición seguiría pidiendo permiso fuera del flujo. [WebOTP](https://raw.githubusercontent.com/WICG/web-otp/7c4a606a085b44d9de75001f7e801f07a4d85f8c/index.bs)

## CSP

Estándar: el [*Content Security Policy Cheat Sheet*](../fuentes/owasp/Content_Security_Policy.md) de OWASP.

- SvelteKit genera la CSP con la opción `csp` de `sveltekit()` en modo `hash`: los nonces piden un HTML que cambie en cada respuesta, y las páginas son estáticas.
- La CSP va en una etiqueta `meta` de cada página: el hash cambia en cada página y en cada build. `frame-ancestors`, que una `meta` no admite, va en la cabecera que pone Caddy ([despliegue.md](despliegue.md#caddy)).
- La CSP lleva además `default-src 'self'` y `form-action 'self'`, que no cae en `default-src`. [CSP Level 3](https://raw.githubusercontent.com/w3c/webappsec-csp/251d288dad4d6166e73541877ca2073864edeb8f/index.bs)
- `script-src` es `'self'`, con los hashes que agrega SvelteKit, y no lleva `'strict-dynamic'`: SvelteKit carga su código con `import()`, `'strict-dynamic'` solo deja pasar lo que carga un `<script>` creado desde el código, y la página no hidrata. Las demás respuestas del origen, JSON e imágenes, no corren como script porque Caddy las sirve con `nosniff` ([despliegue.md](despliegue.md#caddy)). [CSP Level 3](https://raw.githubusercontent.com/w3c/webappsec-csp/251d288dad4d6166e73541877ca2073864edeb8f/index.bs)
- `style-src-attr` lleva `'unsafe-inline'`: SvelteKit solo lo agrega en desarrollo, y sin él los atributos `style` y la directiva `style:` no se aplican en una página prerenderizada. [SvelteKit 3.2.0](https://raw.githubusercontent.com/sveltejs/kit/@sveltejs%2Fkit@3.2.0/packages/kit/src/runtime/server/page/csp.js)
- `vite.config.ts` fija `build.assetsInlineLimit: 0`: Vite incrusta como `data:` los archivos de menos de 4 KiB, y la CSP los bloquea. [Vite 8.3.8](https://raw.githubusercontent.com/vitejs/vite/v8.3.8/docs/config/build-options.md)
- Con un mapa, la CSP lleva en `connect-src` `https://tiles.openfreemap.org`, de donde MapLibre baja estilos, teselas, fuentes e íconos.
- Con un formulario de pago incrustado, los dominios que documenta su pasarela van en `script-src`, `frame-src` y `connect-src`.
- La prueba de Playwright de cada página falla también con un evento `securitypolicyviolation`, y corre sobre el build, con `vite preview`: en desarrollo SvelteKit afloja la CSP, y lo que la CSP bloquea no da error.
- La CSP lleva `object-src 'none'` y `base-uri 'none'` ([CSP Cheat Sheet, *Hash-based Strict Policy*](../fuentes/owasp/Content_Security_Policy.md)).
- Ningún script ni manejador de eventos va escrito en el HTML: van en el código ([CSP Cheat Sheet, *Refactoring inline code*](../fuentes/owasp/Content_Security_Policy.md)).
- No se usa `X-Content-Security-Policy` ni `X-WebKit-CSP` ([CSP Cheat Sheet, *WARNING*](../fuentes/owasp/Content_Security_Policy.md)).

## Estilos

Estándares: de UnoCSS, el [preset Wind4](../fuentes/unocss/presets-wind4.md) y el [plugin de Vite](../fuentes/unocss/integrations-vite.md), y [*Best practices*](../fuentes/svelte/best-practices.md) de Svelte.

Contrato: [transversal.md](transversal.md#tema).

- El preset es Wind4: trae el reset y genera las variables CSS del tema.
- La configuración va en `uno.config.ts`, y no en `vite.config.ts`: funciona mejor con el editor y las integraciones. [UnoCSS 66.13.0](https://raw.githubusercontent.com/unocss/unocss/v66.13.0/docs/guide/config-file.md)
- Los tokens van en el `theme` de `uno.config.ts`, sin tamaños literales fuera de él. Los colores son `colors`, generado en `src/lib/colors.ts`, y sus variables CSS entran como preflight desde `colorsCss`, con el modo oscuro de `prefers-color-scheme` cuando `<html>` no lleva `data-theme`, y con `data-theme="dark"`. La elección del usuario va en `localStorage`, y la app la escribe en `data-theme`; con «sistema», lo quita.
- `uno.config.ts` fija `separators: [':']`. Con los separadores por defecto, `:` y `-`, un atajo como `link-primary` u `open-panel` se lee como una variante seguida de una clase, y no se genera, sin error. [UnoCSS 66.13.0](https://raw.githubusercontent.com/unocss/unocss/v66.13.0/docs/config/index.md)
- `app.html` no lleva clases de utilidad: SvelteKit 3 no le pasa `app.html` a UnoCSS, que no las genera, sin error, ni en el build ni en `vite dev`. Por eso el build avisa `transform_index_html_unsupported` con los plugins de UnoCSS. [SvelteKit 3.2.0](https://raw.githubusercontent.com/sveltejs/kit/%40sveltejs/kit%403.2.0/packages/kit/src/messages/build-warnings.js)
- Las clases de utilidad no van en archivos `.ts`: UnoCSS no los lee por defecto ([UnoCSS Vite Plugin, *VanillaJS / TypeScript*](../fuentes/unocss/integrations-vite.md)).
- Un padre cambia el estilo de un hijo con propiedades personalizadas de CSS, como `<Child --color="red" />`, y usa `:global` solo con un hijo de una biblioteca ([Best practices, *Styling child components*](../fuentes/svelte/best-practices.md)).
- Un valor de JavaScript que usa el `<style>` de un componente entra como propiedad personalizada con la directiva `style:`, como `style:--columns={columns}` ([Best practices, *Using JavaScript variables in CSS*](../fuentes/svelte/best-practices.md)).
- `src/routes/+layout.svelte` importa `virtual:uno.css` ([UnoCSS Vite Plugin, *Sveltekit*](../fuentes/unocss/integrations-vite.md)).
- `UnoCSS()` va antes de `sveltekit()` en los `plugins` de `vite.config.ts` ([UnoCSS Vite Plugin, *Svelte*](../fuentes/unocss/integrations-vite.md)).
- No se instala otro reset, como `@unocss/reset` o `normalize.css`: Wind4 trae el suyo ([Wind4 preset, *Reset*](../fuentes/unocss/presets-wind4.md)).
- Las variables del tema no se apagan: `preflights.theme` no es `false` ([Wind4 preset, *Mode*](../fuentes/unocss/presets-wind4.md)).

## Idiomas

Estándares: de Paraglide, [*Basics*](../fuentes/paraglide/basics.md) y [*Compiling Messages*](../fuentes/paraglide/compiling-messages.md), y [*Accessibility*](../fuentes/sveltekit/accessibility.md) de SvelteKit.

Contrato: [transversal.md](transversal.md#idiomas).

- `paraglideVitePlugin` lleva `outdir: './src/lib/paraglide'`. `src/lib/paraglide` no se versiona, y CI construye antes de `svelte-check`, que lo necesita.
- El `handle` de `src/hooks.server.ts` corre dentro de `paraglideMiddleware`, y `app.html` lleva también `dir="%dir%"`, que el `handle` reemplaza con la dirección del idioma.
- `reroute`, en `src/hooks.ts`, quita el idioma de la URL con `deLocalizeUrl`.
- `paths.relative` es `false`: con el `fallback`, una ruta relativa a un recurso daría 404 en una URL con idioma.
- Un código que el mapa de mensajes no tiene lanza un error, sin texto de reemplazo: un valor fuera del contrato tiene que verse. El `type` de un error sigue [transversal.md](transversal.md#errores).
- `paraglideVitePlugin` lleva `devErrorResponse: true`: con un mensaje que no compila, `vite dev` responde 500 en vez de servir la última traducción que compiló ([Compiling Messages, *Stop serving stale translations during development*](../fuentes/paraglide/compiling-messages.md)).
- Un enlace a otro idioma lleva `data-sveltekit-reload`: el documento y el idioma del cliente quedan iguales ([Basics, *Routing*](../fuentes/paraglide/basics.md)).
- `app.html` lleva `<html lang="%lang%">`, y el `handle` lo reemplaza con el idioma de la página: cada página prerenderizada declara su idioma ([Accessibility, *The "lang" attribute*](../fuentes/sveltekit/accessibility.md)).
- Los mensajes se compilan con `paraglideVitePlugin` en `vite.config.ts`: se generan al construir ([Compiling Messages, *Compiling Messages*](../fuentes/paraglide/compiling-messages.md)).
- `paraglideVitePlugin` lleva `emitTsDeclarations: true`: el editor ve los mensajes que cambian ([Compiling Messages, *TypeScript Configuration*](../fuentes/paraglide/compiling-messages.md)).
- `setLocale()` no lleva `reload: false` ([Basics, *Advanced: stay on the current document*](../fuentes/paraglide/basics.md)).
- Las claves de los mensajes son planas, sin anidar ([Basics, *Message keys*](../fuentes/paraglide/basics.md)).
- Cada mensaje se nombra directo, como `m.greeting()`. Un código que llega de la API se traduce con un mapa de sus valores a sus mensajes, nunca con `m[name]()` ([Basics, *Dynamic messages*](../fuentes/paraglide/basics.md)).
- Nada se escribe a mano en `src/lib/paraglide`: Paraglide puede borrar lo que encuentra ahí ([Compiling Messages, *Migrating to Paraglide JS 3*](../fuentes/paraglide/compiling-messages.md)).

## Mapas

Contrato: [transversal.md](transversal.md#mapas).

- El mapa usa MapLibre GL JS, con el estilo del modo de la app, y lo cambia con `setStyle` cuando cambia el modo.
- El worker de MapLibre sale del mismo origen: `setWorkerUrl` recibe el `maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url` de Vite. Sin él, MapLibre lo arranca desde una URL `blob:`, que la CSP no deja pasar. [MapLibre GL JS 6.18.0](https://raw.githubusercontent.com/maplibre/maplibre-gl-js/v6.18.0/docs/index.md)
- El mapa se crea con `attributionControl: false`, y la página muestra la atribución de la configuración ([transversal.md](transversal.md#mapas)).
- El contenido de un popup va con `setText` o `setDOMContent`, nunca con `setHTML`: `setHTML` lo inserta con `innerHTML`. [MapLibre GL JS 6.18.0](https://raw.githubusercontent.com/maplibre/maplibre-gl-js/v6.18.0/src/ui/popup.ts)

## Push

Estándar: la [*Push API*](../fuentes/w3c/push-api.html) de W3C.

Contrato: [transversal.md](transversal.md#push).

- El service worker muestra el mensaje declarativo en el evento `push` y abre su `navigate` al tocarlo: Safari lo muestra sin el service worker, pero Chrome y Firefox no implementan el mensaje declarativo. [BCD 8.1.8](https://raw.githubusercontent.com/mdn/browser-compat-data/v8.1.8/api/PushEvent.json)
- En `pushsubscriptionchange`, el service worker vuelve a llamar a `subscribe()` con la misma `applicationServerKey` y le manda al servidor el `toJSON()` de la suscripción que recibe: Firefox lanza el evento sin `newSubscription`. [BCD 8.1.8](https://raw.githubusercontent.com/mdn/browser-compat-data/v8.1.8/api/ServiceWorkerGlobalScope.json)
- Al iniciar sesión, y cada vez que abre con una sesión, la web le manda al servidor el `toJSON()` de `getSubscription()`: Safari en iOS no lanza `pushsubscriptionchange`. [BCD 8.1.8](https://raw.githubusercontent.com/mdn/browser-compat-data/v8.1.8/api/ServiceWorkerGlobalScope.json)
- `subscribe()` lleva `userVisibleOnly: true`: cada push muestra una notificación ([Push API, *PushSubscriptionOptionsInit dictionary*](../fuentes/w3c/push-api.html)).
- El permiso de push se pide con `subscribe()` ([Push API, *PushManager interface*](../fuentes/w3c/push-api.html)).

## Service worker

Estándar: el [*HTTP Security Response Headers Cheat Sheet*](../fuentes/owasp/HTTP_Headers.md) de OWASP.

- El service worker no guarda en la Cache API ninguna respuesta de `/api/*`: toda respuesta de la API se trata como sensible, y la Cache API no respeta `Cache-Control` ([HTTP Security Response Headers Cheat Sheet, *Cache-Control*](../fuentes/owasp/HTTP_Headers.md)).

## Pruebas

- Las pruebas en el navegador usan Playwright. La misma versión va en todo `package.json` del repositorio que declare Playwright: cada versión descarga sus propios navegadores.
- `.vitest` va en `.gitignore`: guarda artefactos generados. [Vitest 5.1.0](https://raw.githubusercontent.com/vitest-dev/vitest/v5.1.0/docs/guide/index.md)
- En una prueba concurrente, los snapshots y las aserciones usan el `expect` de su contexto. [Vitest 5.1.0](https://raw.githubusercontent.com/vitest-dev/vitest/v5.1.0/docs/guide/features.md)

## Adaptador

Estándar: [*Static site generation*](../fuentes/sveltekit/adapter-static.md) de SvelteKit.

- El adaptador es `adapter-static`: Caddy sirve la web como archivos estáticos.
- `adapter-static` lleva un `fallback`, que sirve las páginas con `ssr = false` de [Opciones de página](#opciones-de-página): no tienen HTML prerenderizado.
- Una pieza con páginas `ssr = false` lleva el `fallback` `200.html`, y no `index.html`, que chocaría con la portada prerenderizada ([Static site generation, *fallback*](../fuentes/sveltekit/adapter-static.md)).
- Una pieza sin páginas `ssr = false`, toda prerenderizada como una landing, lleva el `fallback` `404.html`: Caddy lo sirve con un 404 a una ruta que no existe, y SvelteKit dibuja en él la página de error ([Static site generation, *GitHub Pages*](../fuentes/sveltekit/adapter-static.md), [ADR-0142](../adr/0142-una-pieza-prerenderizada-responde-404-con-su-pagina.md)).
- El layout raíz exporta `prerender = true`, y se prerenderizan todas las páginas que pueden prerenderizarse ([Static site generation, *Usage*](../fuentes/sveltekit/adapter-static.md)).
- Una página prerenderizada no lleva `ssr = false`: se guardaría vacía ([Static site generation, *Usage*](../fuentes/sveltekit/adapter-static.md)).

## Cumplimiento

| Convención | Herramienta |
| :--- | :--- |
| Las advertencias `a11y_*` | `svelte-check --fail-on-warnings` en CI |
| Todo paquete que importa el código está declarado, y toda dependencia declarada se usa | `pnpm exec knip --dependencies` en CI |
| `knip.json` igual al de la plantilla | [scripts/verificar.py](../scripts/verificar.py) |
| Ningún `svelte-ignore` de una advertencia `a11y_*` | [scripts/verificar.py](../scripts/verificar.py) |
| La misma versión de Playwright en todo `package.json` | [scripts/verificar.py](../scripts/verificar.py) |
| pnpm en `packageManager`, y las versiones de [stack.md](../stack.md), exactas | [scripts/verificar.py](../scripts/verificar.py) |
| Los tipos de la API salen de `server/openapi.json` | `pnpm api` en CI, antes de `svelte-check` |
| El script `api`, y que `dev` y `check` lo corran primero | [scripts/verificar.py](../scripts/verificar.py) |
| `includeIgnoreFile` en `eslint.config.js` y `pnpm-lock.yaml` en `.prettierignore` | [scripts/verificar.py](../scripts/verificar.py) |
| El proxy de `/api` en `vite.config.ts` | [scripts/verificar.py](../scripts/verificar.py) |
| El modo `hash`, `script-src 'self'`, `object-src 'none'`, `base-uri 'none'`, `form-action 'self'`, `style-src-attr 'unsafe-inline'` y `assetsInlineLimit: 0` en `vite.config.ts` | [scripts/verificar.py](../scripts/verificar.py) |
| `script-src` sin `'strict-dynamic'` | La prueba de Playwright de cada página en CI, que falla con el `securitypolicyviolation` del `import()` bloqueado |
| `separators: [':']` en `uno.config.ts` | [scripts/verificar.py](../scripts/verificar.py) |
| Ni `$:`, `export let`, `$$props`, `$$restProps`, `on:`, `<slot>`, `<svelte:component>` ni `<svelte:self>` | `compilerOptions: { runes: true }` y `svelte-check --fail-on-warnings` en CI |
| Ningún acceso dinámico al catálogo de mensajes, como `m[name]()` | `paraglide/no-dynamic-message-access` de ESLint en CI |
