# ADR-0158 · Las teselas son vectoriales, de OpenFreeMap, y cada cliente las dibuja con MapLibre

- **Estado:** Aceptada
- **Fecha:** 2026-11-16
- **Alcance:** [`plataformas/transversal.md`](../plataformas/transversal.md), «Mapas»; «Mapas» de [`sveltekit.md`](../plataformas/sveltekit.md), [`android.md`](../plataformas/android.md) y [`flutter.md`](../plataformas/flutter.md); «CSP» de `sveltekit.md`; [`stack.md`](../stack.md); `scripts/verificar.py`

## Contexto

Las teselas eran raster, de `tile.openstreetmap.org`: la web las dibujaba con Leaflet, Android con
MapLibre y una capa raster, y Flutter no tenía mapa escrito. Las teselas raster de OSM solo existen
en claro, y cada cliente tiene modo oscuro.

Comprobado el 2026-11-16: OpenFreeMap sirve teselas vectoriales del esquema OpenMapTiles, sin
límites, sin llave y sin registro, y publica los estilos `positron` y `dark` sobre las mismas
teselas. Su TileJSON atribuye a OpenFreeMap, a OpenMapTiles y a OpenStreetMap.

Comprobado el 2026-11-16 en Chromium, con MapLibre GL JS 6.18.0, el estilo `dark` y la CSP de la
plantilla más `connect-src https://tiles.openfreemap.org`: el mapa se dibuja sin ninguna violación
de la CSP. Sin `setWorkerUrl`, el worker no carga. Sin `img-src data: blob:`, que pide la
documentación de MapLibre, el mapa se dibuja igual.

En pub.dev, flutter_map 8.3.2 dibuja raster, y lo vectorial depende de `vector_map_tiles`, sin
versión nueva desde agosto de 2024.

## Decisión

1. Las teselas son vectoriales, de OpenFreeMap.
2. El modo claro usa el estilo `positron`, y el oscuro, `dark`.
3. El servidor entrega en su configuración pública la URL de cada estilo y la atribución.
4. La web dibuja con MapLibre GL JS, en lugar de Leaflet; Android, con MapLibre Android, y
   Flutter, con maplibre_gl.
5. Cada cliente muestra la atribución como texto y apaga el control de atribución de MapLibre.

## Consecuencias

- El mapa sigue el modo oscuro sin otro juego de teselas.
- La web suma `https://tiles.openfreemap.org` a `connect-src`. Si un caso pide `img-src data: blob:`,
  la prueba de Playwright de la página falla con su `securitypolicyviolation`.
- En Flutter, lo que se dibuja sobre el mapa va como capas de MapLibre, no como widgets.
- maplibre_gl no corre en escritorio. La app de Flutter sale en Android y en iOS.
- OpenFreeMap se sostiene con donaciones y no ofrece garantía de servicio.
- banditore, cadenza y navetta usan flutter_map: pasan a maplibre_gl cuando adopten esta página.

## Descartado

- **Teselas raster de OSM:** solo existen en claro.
- **PMTiles propios, como vettore:** generar y servir cada país pide un proceso propio en el
  servidor, y canone no necesita que un tercero no vea qué se mira.
- **Un proveedor comercial:** cobra por uso y pide llave, sin una necesidad que OpenFreeMap no
  cubra.
- **flutter_map:** dibuja raster, y su camino vectorial está detenido desde 2024.
- **Leaflet con `maplibre-gl-leaflet`:** dos motores sincronizados por eventos.
