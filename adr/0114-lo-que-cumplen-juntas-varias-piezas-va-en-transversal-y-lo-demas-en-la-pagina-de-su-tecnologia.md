# ADR-0114 · Lo que cumplen juntas varias piezas va en `transversal.md`, y lo demás en la página de su tecnología

- **Estado:** Aceptada
- **Fecha:** 2026-11-03
- **Alcance:** «Alcance» de [`plataformas/README.md`](../plataformas/README.md) y
  [`plataformas/transversal.md`](../plataformas/transversal.md)

## Contexto

Había una página por tecnología y otra por cada contrato que cruzaba piezas: `seguridad.md`,
`tiempo-real.md`, `notificaciones.md`, `pagos.md`, `archivos.md`, `mapas.md`, `i18n.md` y
`accesibilidad.md`. El commit 74a1118, del 2026-10-03, las borró sin registrar la decisión en un
ADR; este la registra.

## Decisión

1. Una página reúne las convenciones de una tecnología o ámbito, y dice solo lo que hace su pieza.
2. Lo que deben cumplir juntas varias piezas va en `transversal.md`, y la sección de cada pieza que
   lo implementa enlaza ahí.
3. Las páginas de contrato no existen. Lo de `pagos.md` quedó así: el contrato, en «Pagos» de
   `transversal.md`; lo que hace solo el servidor, en `fastapi.md`, y el monto en `numeric`, en
   `postgres.md`.

## Consecuencias

- Quien trabaja en una pieza encuentra sus convenciones en su página, y lee de `transversal.md` solo
  las secciones que esta enlaza.
- `transversal.md` es una página larga, con temas que no se relacionan entre sí.
- Los ADR anteriores nombran páginas que ya no existen. Un enlace a una de ellas se corrige.

## Descartado

- **Una página por contrato:** quien trabaja en una pieza tendría que buscar sus convenciones en
  varias páginas, y cada una tendría que decir lo que hace cada cliente.
