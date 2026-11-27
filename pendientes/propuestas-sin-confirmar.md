# Las propuestas sin confirmar de los ADR

Tema pendiente: lo que un ADR deja en propuesta, sin que el desarrollador lo haya confirmado.

## Estado (verificado 2026-11-25)

| ADR | Lo que sigue en propuesta |
| :--- | :--- |
| [0008](../adr/0008-un-sobre-unico-de-evento-y-el-catalogo-es-del-repositorio.md) | La mitad del punto 6: que ninguna API escribe en una bitácora |
| [0037](../adr/0037-la-uri-de-cada-tipo-de-problema-sirve-su-documentacion-bajo-api.md) | Punto 4: la ruta que documenta cada tipo de problema vive en `routers/problems.py`, fuera del esquema de OpenAPI |
| [0048](../adr/0048-una-app-flutter-usa-riverpod-go-router-dio-y-freezed.md) | Entero, en estado «Propuesta»: Riverpod, go_router, Dio y Freezed. `stack.md` ya fija Riverpod, go_router y Freezed, y `http` en lugar de Dio |
| [0049](../adr/0049-la-ubicacion-en-segundo-plano-de-una-app-flutter-usa-geolocator-y-native-geofence.md) | Entero, en estado «Propuesta»: la ubicación en segundo plano con geolocator y native_geofence, que `stack.md` no tiene |
| [0059](../adr/0059-un-recurso-que-crea-el-usuario-se-crea-por-put-y-es-un-contrato-de-transversal.md) | Punto 2: un recurso que crea el usuario se crea por `PUT /<recurso>/{id}`, con un uuid v4 del cliente |
| [0088](../adr/0088-gradle-agp-y-kotlin-tienen-una-sola-version-en-android-y-flutter.md) | Puntos 3 y 4: el `gradle-wrapper.properties` canónico, y que `verificar.py` lo compare y compruebe AGP y Kotlin |
| [0089](../adr/0089-playwright-tiene-una-sola-version-exacta-en-todos-los-repositorios.md) | Puntos 2 a 4: Playwright exacto en todo `package.json`, la regla en «Pruebas» de `sveltekit.md`, y que `verificar.py` lo compruebe |
| [0131](../adr/0131-los-paquetes-de-la-maquina-los-instala-packages-py.md) | Puntos 2 a 5: `packages.py` instala los paquetes de la máquina, sus opciones, `--list` y su prueba en CI |
| [0133](../adr/0133-la-autenticacion-tiene-su-pagina-y-el-servidor-comprueba-aparte-lo-que-sus-bibliotecas-no-miran.md) | Punto 6: el servidor no pide extensiones de WebAuthn |
| [0147](../adr/0147-una-pieza-en-java-corre-en-su-unidad-con-el-jre-de-debian.md) | Puntos 5, 6 y 8: `DynamicUser=`, `dependencies.txt` con el SHA-256 de cada jar, y `SuccessExitStatus=143` |
| [0161](../adr/0161-cada-regla-queda-en-una-sola-pagina-y-plugins-deja-de-ser-una-carpeta-de-primer-nivel.md) | Punto 8, en lo que quita `plugins` de las carpetas que acepta `verificar.py` |
| [0162](../adr/0162-una-pagina-escribe-decisiones-y-no-como-funciona-su-tecnologia.md) | Puntos 5 y 6: la segunda condición de «Qué entra en una página», y que el README diga que Canone escribe decisiones |
| [0169](../adr/0169-el-stack-suma-los-paquetes-que-sus-paginas-ya-pedian-y-el-servidor-declara-uvicorn.md) | Puntos 4, 6 y 10: `loadStripe` de `@stripe/stripe-js/pure`, los textos de Flutter en ARB, y el `.mo` de Flet compilado en CI |
| [0172](../adr/0172-una-tarea-que-maneja-chromium-corre-en-su-instancia-de-browser.md) | Puntos 4 y 5: una vuelta de una tarea con navegador termina a la hora, y la tarea se declara en `BROWSER_TIMERS` |
| [0180](../adr/0180-cada-plataforma-se-escribe-como-si-hubiera-cuenta-y-cada-repositorio-elige-donde-publica.md) | Puntos 6 y 7: `apple.py` instala en el runner el certificado y el perfil, y Flutter firma Release a mano |
| [0199](../adr/0199-fastapi-cada-fila-detecta-lo-que-promete-y-el-servidor-reconecta-compara-los-server-default-y-limita-cada-subida.md) | Punto 4: `migrate`, `mock` y los seeders pasan de `tasks.py` a `database.py` |
| [0209](../adr/0209-un-estado-que-el-colorscheme-no-tiene-lleva-un-custom-color-de-material.md) | Punto 7: `brand/tokens/` de la plantilla trae `success` y `warning` |
| [0251](../adr/0251-lo-que-corre-mas-seguido-que-cada-minuto-es-un-worker-en-su-unidad.md) | Puntos 6 a 8: `install.py --worker` arranca el worker si hay una versión activa, los workers se detienen con el servidor antes de migrar y en `database.py empty`, y la unidad lleva `Restart=on-failure` |

## Qué hay que decidir

Cada fila, por separado: si se confirma, su ADR dice en el estado quién la confirmó y cuándo; si no,
un ADR nuevo la reemplaza o la descarta.
