# ADR-0039 · Las páginas públicas se prerenderizan, y las que piden sesión salen del `fallback`

- **Estado:** Propuesta
- **Fecha:** 2026-10-08
- **Alcance:** la sección «Adaptador» de [`plataformas/sveltekit.md`](../plataformas/sveltekit.md)

## Contexto

El [ADR-0007](0007-adapter-static.md) fijó `adapter-static` con `fallback: "index.html"` en toda
superficie web. La documentación de `adapter-static` pide evitar `index.html`, porque choca con una
página de inicio prerenderizada, y recomienda el `fallback` solo en casos puntuales.

## Decisión

Reemplaza el punto 1 del ADR-0007.

1. Las páginas públicas se prerenderizan.
2. Las que piden sesión llevan `ssr = false`, y las sirve el `fallback` `200.html`.

## Consecuencias

- Contradice la documentación, que recomienda el `fallback` solo en casos puntuales. Las páginas
  con sesión no necesitan SEO y dependen de los datos del usuario.
- La página de inicio prerenderizada es `index.html`, y el `fallback` no la pisa.

## Descartado

- **`fallback: "index.html"`** (el ADR-0007): pisa la página de inicio prerenderizada.
- **Todo por el `fallback`:** las páginas públicas perderían el SEO y la primera carga sin
  JavaScript.
- **Renderizar en el servidor las páginas con sesión:** el servidor es FastAPI, sin Node que las
  renderice.
