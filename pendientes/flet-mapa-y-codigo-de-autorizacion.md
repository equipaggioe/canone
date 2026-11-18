# El mapa, el código por SMS y el código de autorización de la app móvil de Flet

Tema pendiente: lo que la app de Flet para Android todavía no tiene escrito porque falta comprobarlo o decidirlo.

## Estado (verificado 2026-11-18)

| Pieza | Estado |
| :--- | :--- |
| Un mapa en Flet, si un producto lo pide, con una de tres formas: **A**, una extensión propia de Flet sobre el paquete `maplibre` de Flutter, que lista Windows y Linux con MapLibre GL JS en un WebView; **B**, una extensión que agregue a flet-map las teselas vectoriales de `vector_map_tiles`, cuya versión estable pide flutter_map 7; **C**, flet-map con teselas raster que el servidor dibuja desde OpenFreeMap con su estilo | **Sin desarrollar**: hoy una app de Flet no muestra mapas. A es la que sigue MapLibre como los demás clientes |
| La petición de autorización con `UrlLauncher().launch_url()` en `LaunchMode.IN_APP_BROWSER_VIEW` | **Comprobado** el 2026-11-18 en un Galaxy S10e con Android 12 y Chrome: abre `CustomTabActivity`, una pestaña del navegador y no un web-view |
| El código por SMS en la app de Android | **Comprobado** el 2026-11-18 en el mismo teléfono, con el teclado y el autocompletado de Samsung: un `TextField` con `AutofillHint.ONE_TIME_CODE` no ofrece el código del SMS que llega. Leerlo solo, como `sms_autofill` en Flutter, pide una extensión de Flet: **sin decidir** |
| La vuelta a la app: un App Link `https`, con un intent filter con `autoVerify` y `delegate_permission/common.handle_all_urls` en `assetlinks.json` | **Sin comprobar**. `assetlinks.json` declara hoy solo `get_login_creds`, también para Flutter |

## Cuándo se retoma

- El mapa: cuando una app de Flet necesite uno. Se prueba primero A, con un prototipo construido para Android, Windows y Linux.
- El código por SMS: cuando se decida si vale una extensión de Flet sobre `sms_autofill`.
- El código de autorización: con un teléfono Android conectado y un dominio que sirva `assetlinks.json`. Hay que comprobar que la redirección del servidor vuelve a la app con `code` y `state` en `page.route`.
