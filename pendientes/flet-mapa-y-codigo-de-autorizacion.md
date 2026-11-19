# El mapa, el código por SMS y el código de autorización de la app móvil de Flet

Tema pendiente: lo que la app de Flet para el teléfono todavía no tiene escrito porque falta comprobarlo o decidirlo.

## Estado (verificado 2026-11-18)

| Pieza | Estado |
| :--- | :--- |
| Un mapa en Flet, si un producto lo pide, con una de tres formas: **A**, una extensión propia de Flet sobre el paquete `maplibre` de Flutter, que lista Windows y Linux con MapLibre GL JS en un WebView; **B**, una extensión que agregue a flet-map las teselas vectoriales de `vector_map_tiles`, cuya versión estable pide flutter_map 7; **C**, flet-map con teselas raster que el servidor dibuja desde OpenFreeMap con su estilo | **Sin desarrollar**: hoy una app de Flet no muestra mapas. A es la que sigue MapLibre como los demás clientes |
| El código por SMS en la app de Android | **Comprobado** el 2026-11-18 en un Galaxy S10e con Android 12, con el teclado y el autocompletado de Samsung: un `TextField` con `AutofillHint.ONE_TIME_CODE` no ofrece el código del SMS que llega. Leerlo solo, como `sms_autofill` en Flutter, pide una extensión de Flet: **sin decidir** |
| El código de autorización en iOS: cómo vuelve el retorno a la app, que en Flutter llega a un esquema propio por `ASWebAuthenticationSession` | **Sin comprobar**: no hay un iPhone |
| El retorno `https` cuando la página de autorización está en el mismo dominio que la URI de retorno | **Sin comprobar**, también en Flutter: la prueba de Android tuvo la página en otro origen. Pide un dominio que sirva la página, la redirección y `assetlinks.json` |

## Cuándo se retoma

- El mapa: cuando una app de Flet necesite uno. Se prueba primero A, con un prototipo construido para Android, Windows y Linux.
- El código por SMS: cuando se decida si vale una extensión de Flet sobre `sms_autofill`.
- El código de autorización en iOS: con un iPhone.
- El retorno en el mismo dominio: con un dominio de prueba.
