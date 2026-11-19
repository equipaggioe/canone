# El mapa y el código de autorización de la app móvil de Flet

Tema pendiente: lo que la app de Flet para el teléfono todavía no tiene escrito porque falta comprobarlo o decidirlo.

## Estado (verificado 2026-11-18)

| Pieza | Estado |
| :--- | :--- |
| Un mapa en Flet, si un producto lo pide, con una de tres formas: **A**, una extensión propia de Flet sobre el paquete `maplibre` de Flutter, que lista Windows y Linux con MapLibre GL JS en un WebView; **B**, una extensión que agregue a flet-map las teselas vectoriales de `vector_map_tiles`, cuya versión estable pide flutter_map 7; **C**, flet-map con teselas raster que el servidor dibuja desde OpenFreeMap con su estilo | **Sin desarrollar**: hoy una app de Flet no muestra mapas. A es la que sigue MapLibre como los demás clientes |
| El código de autorización en iOS: `SFSafariViewController`, el retorno al esquema propio y el cierre de la pestaña que escribe [flet.md](../plataformas/flet.md#código-de-autorización) | **Leído** en url_launcher_ios 6.4.2, en WebKit y en la documentación de Apple. **Sin comprobar** en un iPhone |

## Cuándo se retoma

- El mapa: cuando una app de Flet necesite uno. Se prueba primero A, con un prototipo construido para Android, Windows y Linux.
- El código de autorización en iOS: con un iPhone. Si no funciona, se cambia la regla.
