# Qt y Flet en el primer repositorio que los use

Tema pendiente: lo que solo se comprueba en un repositorio real.

## Estado (verificado 2026-11-13)

Un repositorio temporal corrió en GitHub Actions la CI de Flet y de Qt, el AAB firmado, el AppImage, el `setup.exe` y `pyside6-deploy` en Linux y Windows, con el ejecutable leyendo su versión. Lo que falló se corrigió en la plantilla (commit `d862fad`).

| Pieza | Estado |
| :--- | :--- |
| `gh release upload` de los jobs `desktop`, `flet-mobile` y `flet-desktop` | **Nunca corrió**: necesita un tag de un repositorio real |
| La subida del AAB de Flet a Play | Pendiente en [play-y-apk-universal.md](play-y-apk-universal.md) |
| keyring y `QWebSocket` en Qt, y httpx-ws y `SecureStorage` en Flet | Escritos y declarados; ninguna prueba los usa en ejecución |

## Cuándo se retoma

Con el primer repositorio que tenga una pieza en Qt o en Flet: su primer tag prueba la subida al release, y su código, keyring, el WebSocket y el almacenamiento seguro.

