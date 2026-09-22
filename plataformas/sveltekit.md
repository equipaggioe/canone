# SvelteKit + UnoCSS

Aplica a cualquier superficie web: `landing/`, `panel/`, `backoffice/`, `pwa/`. Hoy hay 15 en seis
repositorios, y **es la única forma de hacer web**: no hay React, Vue ni Astro en ninguna, y no se
agrega otra sin un ADR.

Un repositorio sin superficie web no lee esta página. Nada obliga a tener una.

## Base

SvelteKit 2 + Svelte 5 + TypeScript + Vite + UnoCSS. Sin excepción en las 15 superficies.

## Adaptador

**`adapter-static` siempre**, con `fallback: "index.html"` — ver
[ADR-0007](../adr/0007-adapter-static.md). Todo se sirve con Caddy desde el VPS; no hay SSR ni
funciones de plataforma. `adapter-auto` es lo que deja `npx sv create` por defecto y elige un
adaptador de Vercel o Netlify que no se usa.

Siguen con `adapter-auto`: `navetta/panel`, `presenze/panel`, `banditore/backoffice`,
`cadenza/backoffice`.

Una superficie montada bajo una ruta declara su `base` en `svelte.config.js` (`/panel`,
`/backoffice`) y Caddy la sirve desde ahí.

## Layout

```
panel/
  uno.config.ts
  svelte.config.js
  vite.config.ts
  src/
    lib/
      api/          cliente HTTP y tipos generados del openapi
      components/
      stores/       o *.svelte.ts con runes
      styles/
    routes/
```

## UnoCSS

**La configuración va en `uno.config.ts`, no dentro de `vite.config.ts`.** banditore y cadenza la
tienen inline; así la extensión de UnoCSS del editor no la lee y `content.pipeline.include` no tiene
dónde declararse.

Preset: **`presetWind4`**, que es el más nuevo y el que usa concordia. `presetUno` (presenze,
vettore/panel, banditore, cadenza) es el alias viejo de Wind3. Se agregan `presetIcons` y
`presetAttributify` donde hagan falta.

Los colores y tamaños se declaran como tokens en `uno.config.ts`; ningún componente escribe un color
literal. Si dos superficies del mismo producto comparten marca, el tema sale a un `uno.theme.ts`
importado por las dos, como hacen `concordia/pwa` y `concordia/landing`.

Dos trampas verificadas, las dos silenciosas:

| Trampa | Qué hacer |
|---|---|
| Un atajo con prefijo de variante (`link-`, `first-`, `open-`) no genera nada | No se usan prefijos de variante en los atajos |
| UnoCSS no escanea `.ts` | Toda clase que salga de un `.ts` se declara en `content.pipeline.include` |

## Estado

**Runes de Svelte 5** (`$state`, `$derived`) en un archivo `.svelte.ts`, que es lo que hacen
concordia (`theme.svelte.ts`, `i18n.svelte.ts`) y las superficies más nuevas. Los `stores/` de
Svelte 4 quedan para lo que ya está escrito; no se agregan nuevos.

## El cliente de la API

- Un solo módulo arma las peticiones y aplica el token. Ningún componente llama a `fetch` directo.
- Los tipos salen del `openapi.json` del servidor. Se commitea el archivo generado
  (`src/lib/api-types/schema.d.ts` en concordia); el `openapi.json` no.
- Los errores se leen por `errorCode`, nunca por `detail` — ver [fastapi.md](fastapi.md).

## Textos

**Paraglide**, que compila `messages/*.json` a funciones estáticas tree-shakeables en
`src/lib/paraglide`, sin catálogo JSON cargado en runtime. Lo usan `concordia/pwa` y
`banditore/landing`, cada uno con su propio ADR.

- La elección de idioma persiste en la cookie `PARAGLIDE_LOCALE`; sin cookie, el idioma base.
- Un envoltorio delgado (`i18n.svelte.ts`) agrega la reactividad de Svelte: Paraglide persiste y
  recarga, lo que falta es el `$state` que refresca los componentes.
- **Nada se guarda traducido en la base.** El servidor guarda el tipo y los datos, o un `slug`, y el
  cliente traduce. El contenido escrito por el usuario no se traduce.

## Tipos y tests

- `npm run check` (svelte-check) corre en CI y pasa limpio.
- `vitest` en toda superficie con lógica propia: cálculo, protocolo, tokens. Una landing sin lógica
  no lo necesita. Hoy lo tienen `navetta/panel`, `vettore/panel`, `vettore/backoffice` y
  `concordia/pwa`.
- El contraste de los tokens de color se prueba en CI (`contrast.ts` de concordia): una regresión de
  accesibilidad rompe el build en vez de esperar a que alguien mire la pantalla.

## Versiones

Una sola línea para todas las superficies, la más nueva que ya esté corriendo en alguna. Hoy es la
de vettore: **Vite 8, TypeScript 6, plugin-svelte 7**; las otras cinco están en Vite 7 / TS 5.
Ningún repositorio está en producción, así que sostener dos líneas mayores es costo sin beneficio.

## CI

```yaml
- run: npm ci
- run: npm run check
- run: npm run test:unit   # si la superficie tiene tests
- run: npm run build
```
