# SvelteKit + UnoCSS

Cómo se construye una superficie web: landing, panel, backoffice o PWA. Es la única forma de hacer
web; otra tecnología de interfaz web exige un ADR.

## Base

SvelteKit 2 + Svelte 5 + TypeScript + Vite + UnoCSS.

## Adaptador

**`adapter-static` siempre**, con `fallback: "index.html"`. Todo se sirve con Caddy desde el VPS: no
hay SSR ni funciones de plataforma. `adapter-auto` —lo que deja `npx sv create`— elige un adaptador
de Vercel o Netlify que no se usa, y produce un build que el servidor no sabe servir.

Una superficie montada bajo una ruta declara su `base` en `svelte.config.js` (`/panel`,
`/backoffice`) y Caddy la sirve desde ahí.

Si alguna superficie llegara a necesitar SSR, es un ADR de su repositorio que explique qué necesita
del servidor y por qué no lo resuelve la API.

## Layout

```
panel/
  uno.config.ts
  svelte.config.js
  vite.config.ts
  src/
    lib/
      api/          cliente HTTP y tipos generados del openapi
      api-types/    schema.d.ts generado; se commitea
      components/
      styles/
      *.svelte.ts   estado con runes
    routes/
```

## UnoCSS

**La configuración va en `uno.config.ts`, no dentro de `vite.config.ts`.** Inline, la extensión del
editor no la lee y `content.pipeline.include` no tiene dónde declararse.

Preset: **`presetWind4`**. Se agregan `presetIcons` y `presetAttributify` donde hagan falta.

Los colores y tamaños se declaran como tokens en la config; **ningún componente escribe un color
literal**. Si dos superficies del mismo producto comparten marca, el tema sale a un `uno.theme.ts`
que las dos importan.

Dos trampas, las dos silenciosas:

| Trampa | Qué hacer |
|---|---|
| Un atajo con prefijo de variante (`link-`, `first-`, `open-`) no genera nada | No se usan prefijos de variante en los atajos |
| UnoCSS no escanea `.ts` | Toda clase que salga de un `.ts` se declara en `content.pipeline.include` |

## Estado

**Runes de Svelte 5** (`$state`, `$derived`) en un archivo `.svelte.ts`. Los `stores` de Svelte 4 se
mantienen donde ya estén escritos; no se agregan nuevos.

## El cliente de la API

- Un solo módulo arma las peticiones y aplica el token. Ningún componente llama a `fetch` directo.
- Los tipos salen del `openapi.json` del servidor. Se commitea el archivo generado; el
  `openapi.json`, no.
- Los errores se leen por `errorCode`, nunca por `detail` — ver [fastapi.md](fastapi.md).

## Tipos y tests

- `npm run check` (svelte-check) corre en CI y pasa limpio.
- `vitest` en toda superficie con lógica propia: cálculo, protocolo, tokens. Una landing sin lógica
  no lo necesita.
- **El contraste de los tokens de color se prueba**: una regresión de accesibilidad rompe el build
  en vez de esperar a que alguien mire la pantalla.

## Versiones

Una sola línea para todas las superficies de todos los repositorios, la más nueva que ya esté
corriendo en alguna. Sostener dos líneas mayores de Vite o TypeScript es costo sin beneficio.

## CI

```yaml
- run: npm ci
- run: npm run check
- run: npm run test:unit   # si la superficie tiene tests
- run: npm run build
```
