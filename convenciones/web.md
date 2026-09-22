# Convención: superficies web

SvelteKit 2 + Svelte 5 + UnoCSS + TypeScript + Vite. Igual en landing, panel, backoffice y pwa.

## Adaptador

**`adapter-static` siempre.** Todo se sirve con Caddy desde el VPS; no hay SSR ni funciones de
plataforma. `adapter-auto` elige un adaptador de Vercel o Netlify que no se usa, y el build que
produce el servidor no lo sabe servir.

Una superficie montada bajo una ruta (`/panel`, `/backoffice`) declara su `base` en
`svelte.config.js` y Caddy sirve `index.html` como respaldo para las rutas del cliente.

## Layout

```
panel/
  src/
    lib/
      api/        cliente HTTP y tipos generados del openapi
      components/
      stores/
    routes/
  uno.config.ts
  svelte.config.js
  vite.config.ts
```

## UnoCSS

Dos trampas verificadas, las dos silenciosas:

| Trampa | Qué hacer |
|---|---|
| Un atajo con prefijo de variante (`link-`, `first-`, `open-`) no genera nada | No se usan prefijos de variante en los atajos |
| UnoCSS no escanea `.ts` | Toda clase que salga de un `.ts` se declara en `content.pipeline.include` |

Los colores y tamaños se declaran como tokens en `uno.config.ts`. Ningún componente escribe un
color literal.

## El cliente de la API

- Un solo módulo arma las peticiones y aplica el token. Ningún componente llama a `fetch` directo.
- Los tipos salen del `openapi.json` del servidor. El archivo generado se commitea; el
  `openapi.json` no.
- Los errores se leen por `errorCode`, nunca por `detail` — ver [api.md](api.md).

## Tipos y tests

- `npm run check` (svelte-check) corre en CI y tiene que pasar limpio.
- `vitest` en toda superficie con lógica propia: cálculo, protocolo, tokens de diseño. Una landing
  sin lógica no lo necesita.
- El contraste de los tokens de color se prueba en CI (concordia ya lo hace): una regresión de
  accesibilidad rompe el build en vez de esperar a que alguien mire la pantalla.

## Versiones

Una sola línea para todos los repositorios, la más nueva que ya esté corriendo en alguno. Hoy es la
de vettore: Vite 8, TypeScript 6, plugin-svelte 7. Ningún repositorio está en producción, así que
sostener dos líneas mayores es costo sin beneficio.
