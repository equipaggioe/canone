# ADR-0176 · La app de Flet dibuja el mapa con flet-map y teselas raster

- **Estado:** Aceptada. El usuario pidió que, si una app de Flet muestra un mapa, sea con flet-map (2026-11-17)
- **Fecha:** 2026-11-17
- **Alcance:** [`plataformas/flet.md`](../plataformas/flet.md), «Mapas»;
  [`plataformas/transversal.md`](../plataformas/transversal.md), «Mapas», y [`stack.md`](../stack.md)

## Contexto

Ningún producto usa Flet para mapas. No hay una extensión de Flet con MapLibre. Leído en el wheel de
flet-map 1.1.2: depende de flutter_map 8.3, y sus capas de teselas son `TileLayer` y
`WMSTileLayer`, sin capa vectorial.

## Decisión

1. **El mapa de una app de Flet usa flet-map, con teselas raster**, como excepción a MapLibre de
   `transversal.md`.

## Consecuencias

- El proveedor de las teselas raster, y cómo el servidor entrega su URL, quedan sin decidir, en
  [pendientes/flet-mapa-y-codigo-de-autorizacion.md](../pendientes/flet-mapa-y-codigo-de-autorizacion.md).

## Descartado

- **Escribir una extensión de Flet sobre `maplibre_gl`:** serviría solo en el teléfono, porque
  `maplibre_gl` no corre en escritorio.
