# ADR-0179 · Una app de Flet no muestra mapas

- **Estado:** Aceptada. El usuario pidió que Flet no se use para mapas y dejar pendientes las formas de hacerlo (2026-11-18)
- **Fecha:** 2026-11-18
- **Alcance:** [`plataformas/transversal.md`](../plataformas/transversal.md), «Mapas»;
  [`plataformas/flet.md`](../plataformas/flet.md); [`stack.md`](../stack.md)

## Contexto

El [ADR-0176](0176-la-app-de-flet-dibuja-el-mapa-con-flet-map-y-teselas-raster.md) llevaba el mapa
de Flet a flet-map con teselas raster, distinto de los demás clientes. Leído en pub.dev:
`maplibre_gl` no soporta escritorio; `maplibre` lista Windows y Linux, con MapLibre GL JS en un
WebView; la versión estable de `vector_map_tiles` pide flutter_map 7, y flet-map 1.1.2 usa la 8.
Flet no trae ninguna de las tres, y una extensión propia no está probada en Windows ni en Linux.

## Decisión

1. **Una app de Flet no muestra mapas.** Sale «Mapas» de `flet.md` y flet-map de `stack.md`.

## Consecuencias

- Las tres formas de dibujar un mapa en Flet quedan sin desarrollar, en
  [pendientes/flet-mapa-y-codigo-de-autorizacion.md](../pendientes/flet-mapa-y-codigo-de-autorizacion.md).

## Descartado

- **flet-map con teselas raster:** se aparta de MapLibre y de OpenFreeMap, el concepto de los
  demás clientes, para una función que ningún producto usa en Flet.
