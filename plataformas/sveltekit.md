# SvelteKit

Una superficie web con SvelteKit y UnoCSS.

## Proyecto

Estándar: [*Project structure*](../estandares/sveltekit/project-structure.md) de SvelteKit.

- Node es el de Debian 13, y solo se usa para construir.
- pnpm maneja las dependencias. No deja importar un paquete que no esté declarado.
- TypeScript va en modo strict, y `svelte-check` lo revisa.
- Prettier formatea, con `prettier-plugin-svelte` y líneas de 99, y ESLint revisa con
  `eslint-plugin-svelte`.

```text
<pieza>/
  .prettierrc
  eslint.config.js
  package.json
  pnpm-lock.yaml
  svelte.config.js    el adaptador y la CSP
  tsconfig.json
  uno.config.ts       el preset y los tokens
  vite.config.ts
  src/
    app.html
    lib/
      api/            el cliente generado por Hey API
      components/
      state/          las clases con $state, en módulos .svelte.ts
    routes/
  static/
```

Plantilla: [`plantilla/sveltekit/`](../plantilla/sveltekit/): `.prettierrc`, que se copia sin
editar, y `svelte.config.js`, `uno.config.ts` y `.gitignore`, puntos de partida.

## Carga de datos

Estándar: [*Loading data*](../estandares/sveltekit/load.md) de SvelteKit.

- Los datos de la API se cargan en `load` universales (`+page.ts`, `+layout.ts`). En producción no
  hay servidor de SvelteKit que corra un `load` de servidor.
- El cliente de la API se genera del OpenAPI de [fastapi.md](fastapi.md) con Hey API. Los tipos
  salen del contrato.

## Opciones de página

Estándar: [*Page options*](../estandares/sveltekit/page-options.md) de SvelteKit.

## Estado

Estándares: [*State management*](../estandares/sveltekit/state-management.md) de SvelteKit y, de
Svelte, [*What are runes?*](../estandares/svelte/what-are-runes.md),
[`$state`](../estandares/svelte/state.md), [`$derived`](../estandares/svelte/derived.md),
[`$effect`](../estandares/svelte/effect.md), [`$props`](../estandares/svelte/props.md),
[`$bindable`](../estandares/svelte/bindable.md), [`$inspect`](../estandares/svelte/inspect.md) y
[`$host`](../estandares/svelte/host.md).

- El estado compartido son clases con `$state` en módulos `.svelte.ts` de `src/lib/state/`.

## Accesibilidad

Estándares: las [advertencias del compilador](../estandares/svelte/compile-warnings.md) de Svelte y
[`sv check`](../estandares/svelte/sv-check.md).

Contrato: [transversal.md](transversal.md#accesibilidad).

- `svelte-check` corre con `--fail-on-warnings`. Las advertencias `a11y_*` del compilador rompen
  CI.

## Código por SMS

Estándar: [*WebOTP API*](../estandares/wicg/webotp.bs) de WICG.

- El campo del código lleva `autocomplete="one-time-code"`: Safari no implementa WebOTP y llena el
  código por ese atributo.

## CSP

Estándares: [*Content Security Policy Cheat Sheet*](../estandares/owasp/Content_Security_Policy.md)
de OWASP y [CSP Level 3](../estandares/w3c/csp3.bs) de W3C.

- La CSP la genera SvelteKit con `kit.csp` en modo `hash`, sobre `default-src 'self'`. El script de
  arranque de SvelteKit va en línea y necesita su hash.
- La CSP lleva el host de las teselas en `img-src`.

## Estilos

Estándares: de UnoCSS, la [guía](../estandares/unocss/guide-index.md), el
[archivo de configuración](../estandares/unocss/guide-config-file.md), la
[configuración](../estandares/unocss/config-index.md), las
[reglas](../estandares/unocss/config-rules.md), los
[atajos](../estandares/unocss/config-shortcuts.md), el [tema](../estandares/unocss/config-theme.md),
el [preset Wind4](../estandares/unocss/presets-wind4.md) y el
[plugin de Vite](../estandares/unocss/integrations-vite.md).

- El preset es Wind4. Trae el reset y genera las variables CSS del tema.
- Los tokens van en el `theme` de `uno.config.ts`.
- Las clases de utilidad se escriben en archivos `.svelte`. UnoCSS no lee `.ts` por defecto.

## Idiomas

Estándares: de Paraglide, [*Basics*](../estandares/paraglide/basics.md),
[*Architecture*](../estandares/paraglide/architecture.md),
[*Compiling Messages*](../estandares/paraglide/compiling-messages.md),
[*Configuration File*](../estandares/paraglide/configuration.md),
[*Translation File Formats*](../estandares/paraglide/file-formats.md),
[*Locale Detection*](../estandares/paraglide/strategy.md) y
[*SvelteKit i18n*](../estandares/paraglide/sveltekit.md).

Contrato: [transversal.md](transversal.md#idiomas).

## Mapas

Estándar: [*Quick Start Guide*](../estandares/leaflet/quick-start.md) de Leaflet.

Contrato: [transversal.md](transversal.md#mapas).

- El mapa usa Leaflet.

## Pruebas

Estándares: [*Getting Started*](../estandares/vitest/guide.md) y
[*Features*](../estandares/vitest/features.md) de Vitest.

## Adaptador

Estándar: [*Static site generation*](../estandares/sveltekit/adapter-static.md) de SvelteKit.

- El adaptador es `adapter-static`. Las páginas públicas se prerenderizan; las que piden sesión
  llevan `ssr = false` y las sirve el `fallback` `200.html`. Contradice la documentación, que
  recomienda el `fallback` solo en casos puntuales: esas páginas no necesitan SEO, dependen de los
  datos del usuario, y el servidor es FastAPI, sin Node para renderizarlas.

## Cómo se hace cumplir

| Qué | Con qué |
|---|---|
| Las advertencias `a11y_*` | `svelte-check --fail-on-warnings` en CI |
