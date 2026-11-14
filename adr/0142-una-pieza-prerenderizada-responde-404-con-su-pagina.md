# ADR-0142 · Una pieza toda prerenderizada responde 404 con su página, y una carpeta sin `index.html` no es una página

- **Estado:** Aceptada
- **Fecha:** 2026-11-13
- **Alcance:** [`plataformas/despliegue.md`](../plataformas/despliegue.md), «Versiones»;
  [`plataformas/sveltekit.md`](../plataformas/sveltekit.md), «Adaptador»; el `Caddyfile` de
  `plantilla/infra/` y [`scripts/infra/caddy.sh`](../scripts/infra/caddy.sh)
- **Modifica:** el [ADR-0039](0039-las-paginas-publicas-se-prerenderizan-y-las-que-piden-sesion-salen-del-fallback.md),
  que fijaba el `fallback` `200.html` en toda pieza

## Contexto

El ADR-0039 hizo que toda pieza de SvelteKit llevara el `fallback` `200.html`, para servir sus
páginas con sesión. Una pieza toda prerenderizada, como una landing, no tiene esas páginas: con
`200.html`, una ruta que no existe responde 200 y el error lo dibuja el navegador, un 404 suave.
`adapter-static` pide el `fallback` solo para una SPA, y para un sitio estático, un `404.html`.

El Caddyfile probaba `{path}/` antes que `{path}.html`. Una página prerenderizada con datos deja
`<página>.html` y una carpeta `<página>/` con su `__data.json`: Caddy tomaba la carpeta, que no
tiene `index.html`, y respondía 404 a una página que existe. Se vio con la landing de banditore,
con `/privacy` y `/terms`, en el Caddy 2.6.2 de Debian 13.

## Decisión

1. **Una pieza con páginas `ssr = false` lleva el `fallback` `200.html`; una toda prerenderizada,
   `404.html`.**
2. **Caddy responde a una ruta que no existe con el `404.html` de la pieza y un 404**, si la pieza
   no tiene `200.html`. Lo sirve en la misma ruta que las páginas, con `file_server` y
   `status 404`, para que lleve las mismas cabeceras.
3. **Una página es `<página>.html` o `<página>/index.html`.** `try_files` prueba
   `{path} {path}.html {path}/index.html /200.html`: una carpeta sin `index.html` no es una
   página.

## Consecuencias

- Una ruta que no existe de la landing es un 404 de verdad, para quien la visita y para un
  buscador.
- Una pieza sin `200.html` ni `404.html` responde 404 sin página, como antes.
- Una petición a `/<carpeta>/` con la barra, sin `index.html`, es un 404: SvelteKit escribe sus
  rutas sin la barra final.

## Descartado

- **`handle_errors` con el `404.html`:** la ruta de errores de Caddy no lleva las cabeceras que la
  directiva `header` pone en la ruta normal. Se probó en Caddy 2.6.2.
- **`200.html` en toda pieza** (el ADR-0039): un 404 suave en una pieza que sabe qué rutas tiene.
