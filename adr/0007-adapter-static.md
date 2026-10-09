# ADR-0007 · Toda superficie web usa `adapter-static`

- **Estado:** Propuesta. El punto 1 lo reemplaza el [ADR-0039](0039-las-paginas-publicas-se-prerenderizan-y-las-que-piden-sesion-salen-del-fallback.md)
- **Fecha:** 2026-09-22
- **Alcance:** `landing/`, `panel/`, `backoffice/`, `pwa/`

## Contexto

Las landings, el panel y el backoffice de vettore y la pwa de concordia usan `adapter-static`. El
panel de navetta y presenze y el backoffice de banditore y cadenza usan `adapter-auto`, que es lo
que deja `npx sv create` por defecto.

Todo se sirve con Caddy desde el VPS. Ninguna superficie usa SSR, endpoints de servidor ni funciones
de plataforma.

## Decisión

1. `adapter-static` en todas, con `fallback: "index.html"` para las rutas del cliente.
2. Una superficie montada bajo una ruta declara su `base` en `svelte.config.js`, y Caddy la sirve
   desde ahí.
3. Si alguna superficie llegara a necesitar SSR, es un ADR de ese repositorio que explique qué
   necesita del servidor y por qué no puede resolverlo la API.

## Consecuencias

- El build es un directorio de archivos, que es lo que Caddy sabe servir.
- `adapter-auto` deja de elegir un adaptador de Vercel o Netlify que nadie usa.
- Las cuatro superficies que lo usan hoy pueden tener código que dependa de `+page.server.ts` sin
  que nadie lo haya notado; el build con `adapter-static` falla y eso es el inventario.

## Descartado

- **`adapter-node` detrás de Caddy:** agrega un proceso que hay que supervisar para servir archivos
  que no cambian entre peticiones.
