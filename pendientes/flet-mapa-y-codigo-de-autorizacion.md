# El mapa y el código de autorización de la app móvil de Flet

Tema pendiente: lo que la app de Flet para Android todavía no tiene escrito porque falta comprobarlo o decidirlo.

## Estado (verificado 2026-11-17)

| Pieza | Estado |
| :--- | :--- |
| Las teselas raster del mapa de Flet: el proveedor, y cómo el servidor entrega su URL y su atribución | **Sin decidir**: OpenFreeMap da teselas vectoriales, y flet-map solo dibuja raster |
| La petición de autorización con `UrlLauncher().launch_url()` en `LaunchMode.IN_APP_BROWSER_VIEW` | Leído en Flet 1.1.2: el modo es una pestaña del navegador, como Custom Tabs. **Sin comprobar** en un teléfono |
| La vuelta a la app: un App Link `https`, con un intent filter con `autoVerify` y `delegate_permission/common.handle_all_urls` en `assetlinks.json` | **Sin comprobar**. `assetlinks.json` declara hoy solo `get_login_creds`, también para Flutter |

## Cuándo se retoma

- El mapa: cuando una app de Flet necesite uno.
- El código de autorización: con un teléfono Android conectado y un dominio que sirva `assetlinks.json`. Hay que comprobar que la pestaña abre fuera de un web-view y que la redirección del servidor vuelve a la app con `code` y `state` en `page.route`.
