# Mapas

Teselas, búsqueda de direcciones y atribución.

## Teselas

Estándar: la [política de uso de teselas](../estandares/osm/tile-usage-policy.md) de OpenStreetMap.

- Las teselas son raster, con URL `{z}/{x}/{y}`. Todas las bibliotecas de abajo las dibujan.
- Mientras el uso quepa en la política, las teselas son las de `tile.openstreetmap.org`.
- La URL de las teselas y su atribución las entrega el servidor en su configuración pública.
  Ningún cliente las escribe en su código. Endurece la recomendación de la política: cambiar de
  proveedor no exige publicar otra versión de las apps.
- La CSP de la web lleva el host de las teselas en `img-src`.

## Búsqueda de direcciones

Estándar: la [política de uso de Nominatim](../estandares/osm/nominatim-usage-policy.md).

- Los clientes buscan direcciones en el servidor, que consulta a Nominatim. Guarda cada respuesta en
  Redis y no pasa de una consulta por segundo en total. El límite de la política es por
  aplicación, y solo el servidor ve el total.

## Atribución

Estándar: la [guía de atribución](../estandares/osm/attribution-guidelines.md) de OpenStreetMap.

## Web

Estándar: [*Quick Start Guide*](../estandares/leaflet/quick-start.md) de Leaflet.

- El mapa usa Leaflet.

## Flutter

Estándar: [flutter_map](../estandares/pub/flutter_map/README.md).

## Android

Estándar: [*Quickstart*](../estandares/maplibre/android-getting-started.md) de MapLibre Android.

- El mapa usa MapLibre Android, con un estilo de una sola capa raster que arma la app con la
  configuración del servidor. Va dentro de Compose con `AndroidView`.

## Flet

Estándar: [flet-map](../estandares/flet/map.md).
