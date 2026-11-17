# Qt y Flet en el primer repositorio que los use

Tema pendiente: lo que solo se comprueba en un repositorio real, y la nota «En desarrollo» de `flet.md`.

## Estado (verificado 2026-11-13)

Un repositorio temporal corrió en GitHub Actions la CI de Flet y de Qt, el AAB firmado, el AppImage, el `setup.exe` y `pyside6-deploy` en Linux y Windows, con el ejecutable leyendo su versión. Lo que falló se corrigió en la plantilla (commit `d862fad`).

| Pieza | Estado |
| :--- | :--- |
| `gh release upload` de los jobs `desktop`, `flet-mobile` y `flet-desktop` | **Nunca corrió**: necesita un tag de un repositorio real |
| La subida del AAB de Flet a Play | Pendiente en [play-y-apk-universal.md](play-y-apk-universal.md) |
| keyring y `QWebSocket` en Qt, y httpx-ws y `SecureStorage` en Flet | Escritos y declarados; ninguna prueba los usa en ejecución |
| La nota «En desarrollo; no se implementa» de `flet.md` | Sigue; **sin decidir** cuándo se quita. La de `qt.md` se quitó el 2026-11-16 |

## Cuándo se retoma

Con el primer repositorio que tenga una pieza en Qt o en Flet: su primer tag prueba la subida al release, y su código, keyring, el WebSocket y el almacenamiento seguro.

## La nota «En desarrollo»

| Opción | Qué implica |
| :--- | :--- |
| Quitarla ahora | Los repositorios con Flet tendrían que cumplir la página ya, con la subida al release sin probar |
| Quitarla cuando ese primer repositorio corra su CI y un release completo | La página se aplica cuando todo lo que pide ya corrió una vez |
| Mantenerla hasta que «Tema» salga de desarrollo | Ata la página entera a una sección que ya tiene su propia nota |

Recomendación: la segunda. La nota de «Tema» ya cubre esa sección por separado.
