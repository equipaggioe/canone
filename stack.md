# Stack

Qué se usa en cada plataforma y en qué versión. Es el único lugar donde se fija: las páginas de [plataformas/](plataformas/) escriben cómo se usa, y no repiten las versiones.

## Quién decide

- El stack lo decide el desarrollador. Lo que una pieza necesita y no está aquí no se elige por cuenta propia: se presentan las opciones con una recomendación, y decide el desarrollador. Cambiar lo que ya está aquí se decide igual.
- La plataforma de cada pieza la elige cada repositorio. Aquí está lo que se usa dentro de cada plataforma, y a un repositorio solo le aplican los bloques de las plataformas que usa.
- El bloque de una página en desarrollo lleva su misma nota, y no se aplica mientras la tenga ([plataformas/README.md](plataformas/README.md#en-desarrollo)).

## Qué entra

- Entra lo que una pieza declara en su manifiesto, con sus extras, o instala, con su versión.
- Lo que una pieza usa, pero cuya versión fija otra tecnología, entra con una nota que dice cuál, como «3.14.0, el de Flutter 3.50.1» o «0.28.1, la que fija firebase-admin»: su versión no se elige, se sigue.
- Todo paquete que importa el código de una pieza está declarado en su manifiesto, aunque otro paquete ya lo traiga: un import que funciona porque otro paquete lo trajo se rompe cuando ese paquete cambia.
- Toda dependencia declarada se usa. Lo que llega dentro de otro paquete y el código no importa no entra ni se nombra en ningún lado.

## Versiones

- La versión se fija por tecnología, no por pieza: una tecnología lleva la misma versión en todas las piezas que la usan.
- Lo que el servidor instala desde los paquetes de su sistema, como Python, PostgreSQL o Valkey, usa la versión de esos paquetes en todas las piezas, también en las que no corren en el servidor, en la máquina de desarrollo y en CI: así se desarrolla y se prueba con la misma versión que corre en producción.
- Lo demás usa la última versión estable, o la última LTS si la tecnología las publica.
- Una versión nueva se adopta a mano, en una [revisión de este archivo](plataformas/README.md#revisión-de-stackmd): que se publique no la adopta.
- Una excepción lleva su razón en la página de su plataforma, y la razón es sobre la última versión.
- La plantilla y las fuentes dependen de este archivo: la plantilla no declara una versión que este archivo no estipule, y las fuentes se descargan de esa versión.

En cada bloque, «Para» enlaza la sección de la página que escribe cómo se usa.

## Python

Página: [python.md](plataformas/python.md). Vale para toda pieza en Python.

| Se usa | Versión | Para |
| :--- | :--- | :--- |
| Python | 3.13, el de Debian 13 | [Proyecto](plataformas/python.md#proyecto) |
| uv | 0.13.10 | [Proyecto](plataformas/python.md#proyecto) |
| `uv_build` | 0.13.10 | [Proyecto](plataformas/python.md#proyecto) |
| pytest | 9.2.0 | [Pruebas](plataformas/python.md#pruebas) |
| ruff | 0.17.6 | [Estilo](plataformas/python.md#estilo) |
| Pyrefly | 1.5.0 | [Tipos](plataformas/python.md#tipos) |
| deptry | 0.25.1 | [Proyecto](plataformas/python.md#proyecto) |
| pip-audit | 2.10.1 | [Cumplimiento](plataformas/python.md#cumplimiento) |
| Pydantic | 2.14.4 | [Esquemas](plataformas/fastapi.md#esquemas) |
| httpx | 0.28.1, la que fija firebase-admin | [Envíos al exterior](plataformas/fastapi.md#envíos-al-exterior) y [Pruebas](plataformas/fastapi.md#pruebas) del servidor, y [Red](plataformas/flet.md#red) de Flet |

## FastAPI

Página: [fastapi.md](plataformas/fastapi.md).

| Se usa | Versión | Para |
| :--- | :--- | :--- |
| FastAPI | 0.165.0 | — |
| Starlette | 1.10.0 | — |
| pydantic-settings | 2.16.3 | [Configuración](plataformas/fastapi.md#configuración) |
| SQLAlchemy, con el extra `asyncio` | 2.1.9 | [Base de datos](plataformas/fastapi.md#base-de-datos) |
| asyncpg | 0.32.0 | [Base de datos](plataformas/fastapi.md#base-de-datos) |
| Alembic | 1.20.1 | [Migraciones](plataformas/fastapi.md#migraciones) |
| valkey-py | 6.2.0 | [Valkey](plataformas/fastapi.md#valkey) |
| Uvicorn, con el extra `standard` | 0.54.0 | [WebSocket](plataformas/fastapi.md#websocket) y [Procesos](plataformas/despliegue.md#procesos) |
| Pillow | 13.0.0 | [Archivos](plataformas/fastapi.md#archivos) |
| python-multipart | 0.0.34 | [Archivos](plataformas/fastapi.md#archivos) |
| Babel | 2.19.0 | [Idiomas](plataformas/fastapi.md#idiomas) |
| cryptography | 50.0.2 | [Paginación](plataformas/fastapi.md#paginación) y [Push](plataformas/fastapi.md#push) |
| pywebpush | 2.5.0 | [Push](plataformas/fastapi.md#push) |
| aiohttp | 3.14.5 | [Push](plataformas/fastapi.md#push) |
| firebase-admin | 7.8.0 | [Push](plataformas/fastapi.md#push) |
| google-auth | 2.63.1 | [Push](plataformas/fastapi.md#push) |
| py-vapid | 1.9.6 | [Push](plataformas/fastapi.md#push) |
| stripe, con el extra `async`, con Stripe | 17.1.0 | [Pagos](plataformas/fastapi.md#pagos) |
| OpenTelemetry | 1.45.2 | [Trazas](plataformas/fastapi.md#trazas) |
| AnyIO | 4.16.0 | [Pruebas](plataformas/fastapi.md#pruebas) |
| httpx-ws | 0.10.0 | [Pruebas](plataformas/fastapi.md#pruebas) |
| Playwright, en el servidor que maneja un navegador | 1.65.1, la de [SvelteKit](#sveltekit) | [Tareas](plataformas/fastapi.md#tareas) |

## Autenticación

Página: [autenticacion.md](plataformas/autenticacion.md). Son paquetes del servidor.

| Se usa | Versión | Para |
| :--- | :--- | :--- |
| pwdlib, con el extra `argon2` | 0.4.2 | [Contraseñas](plataformas/autenticacion.md#contraseñas) |
| phonenumbers | 9.0.44 | [Código por SMS](plataformas/autenticacion.md#código-por-sms) |
| webauthn | 3.0.1 | [Passkeys](plataformas/autenticacion.md#passkeys) |

## PostgreSQL

Página: [postgres.md](plataformas/postgres.md). PostgreSQL y PostGIS son los de los paquetes del servidor.

| Se usa | Versión | Para |
| :--- | :--- | :--- |
| PostgreSQL | 17 | — |
| PostGIS | 3.5 | [Geografía](plataformas/postgres.md#geografía) |
| GeoAlchemy2, en el servidor que guarda geografía | 0.21.0 | [Geografía](plataformas/postgres.md#geografía) |

## Despliegue

Página: [despliegue.md](plataformas/despliegue.md). Cada programa es el de los paquetes de Debian 13, salvo Caddy, que sale de su repositorio APT, y rest-server, que sale de su release de GitHub y corre en la receptora y en el CI.

| Se usa | Versión | Para |
| :--- | :--- | :--- |
| Debian | 13 | [Máquina](plataformas/despliegue.md#máquina) |
| Caddy | 2.11 | [Caddy](plataformas/despliegue.md#caddy) y [Máquina](plataformas/despliegue.md#máquina) |
| Valkey | 8.1 | [Valkey](plataformas/despliegue.md#valkey) |
| coturn | 4.6.1 | [Coturn](plataformas/despliegue.md#coturn) |
| nftables | 1.1.3 | [Firewall](plataformas/despliegue.md#firewall) |
| systemd, con systemd-timesyncd y systemd-journal-remote | 257 | [Procesos](plataformas/despliegue.md#procesos), [Máquina](plataformas/despliegue.md#máquina) y [Registros](plataformas/despliegue.md#registros) |
| sudo | 1.9.16 | [SSH](plataformas/despliegue.md#ssh) |
| unattended-upgrades | 2.12 | [Máquina](plataformas/despliegue.md#máquina) |
| ca-certificates | 20250419 | [Máquina](plataformas/despliegue.md#máquina) |
| OpenSSH | 10.0 | [SSH](plataformas/despliegue.md#ssh) |
| WireGuard | 1.0.20210914 | [Registros](plataformas/despliegue.md#registros) |
| restic | 0.18.0 | [Respaldos](plataformas/despliegue.md#respaldos) |
| rest-server | 0.15.0 | [Respaldos](plataformas/despliegue.md#respaldos) |
| Chromium, en la máquina con una tarea que maneja un navegador | 156 | [Procesos](plataformas/despliegue.md#procesos) |

## Java

Página: [java.md](plataformas/java.md).

| Se usa | Versión | Para |
| :--- | :--- | :--- |
| Java | 21, el JRE de Debian 13 | [Proyecto](plataformas/java.md#proyecto) |
| JDK, con el que compila `java.py` | 25.0.5 | [Entrega](plataformas/java.md#entrega) |
| google-java-format | 2.0.0 | [Código](plataformas/java.md#código) |

## SvelteKit

Página: [sveltekit.md](plataformas/sveltekit.md).

| Se usa | Versión | Para |
| :--- | :--- | :--- |
| Node | 26.13.1 | [Proyecto](plataformas/sveltekit.md#proyecto) |
| pnpm | 12.23.0 | [Proyecto](plataformas/sveltekit.md#proyecto) |
| SvelteKit | 3.4.0 | — |
| Svelte | 5.59.1 | — |
| Vite | 8.3.8 | — |
| `@sveltejs/vite-plugin-svelte` | 7.3.2 | — |
| `@sveltejs/adapter-static` | 4.0.1 | [Entrega](plataformas/sveltekit.md#entrega) |
| TypeScript | 6.0.3 | [Tipos](plataformas/sveltekit.md#tipos) |
| `svelte-check` | 4.7.8 | [Tipos](plataformas/sveltekit.md#tipos) |
| `@types/node` | 26.6.6 | [Proyecto](plataformas/sveltekit.md#proyecto) |
| knip | 6.48.0 | [Proyecto](plataformas/sveltekit.md#proyecto) |
| Prettier | 3.10.1 | [Estilo](plataformas/sveltekit.md#estilo) |
| `prettier-plugin-svelte` | 4.2.0 | [Estilo](plataformas/sveltekit.md#estilo) |
| ESLint | 10.15.0 | [Estilo](plataformas/sveltekit.md#estilo) |
| `eslint-plugin-svelte` | 3.24.1 | [Estilo](plataformas/sveltekit.md#estilo) |
| `typescript-eslint` | 8.74.0 | [Estilo](plataformas/sveltekit.md#estilo) |
| `@eslint/js` | 10.0.1 | [Estilo](plataformas/sveltekit.md#estilo) |
| `globals` | 17.14.0 | [Estilo](plataformas/sveltekit.md#estilo) |
| `eslint-config-prettier` | 10.1.8 | [Estilo](plataformas/sveltekit.md#estilo) |
| UnoCSS | 66.13.0 | [Estilos](plataformas/sveltekit.md#estilos) |
| Paraglide | 3.2.2 | [Idiomas](plataformas/sveltekit.md#idiomas) |
| `openapi-typescript` | 7.13.0 | [Carga de datos](plataformas/sveltekit.md#carga-de-datos) |
| `openapi-fetch` | 0.17.0 | [Carga de datos](plataformas/sveltekit.md#carga-de-datos) |
| MapLibre GL JS, `maplibre-gl` | 6.19.0 | [Mapas](plataformas/sveltekit.md#mapas) |
| `@stripe/stripe-js`, con Stripe | 10.3.0 | [Pagos](plataformas/sveltekit.md#pagos) |
| Vitest | 5.1.1 | [Pruebas](plataformas/sveltekit.md#pruebas) |
| Playwright | 1.65.1 | [Pruebas](plataformas/sveltekit.md#pruebas) |
| `@axe-core/playwright` | 4.14.0 | [Accesibilidad](plataformas/sveltekit.md#accesibilidad) |

## Flutter

Página: [flutter.md](plataformas/flutter.md). El JDK, Gradle, AGP, Kotlin y, en `packages/passkey/`, `androidx.credentials` son los de [Android](#android).

| Se usa | Versión | Para |
| :--- | :--- | :--- |
| Flutter | 3.50.1 | — |
| Dart | 3.14.0, el de Flutter 3.50.1 | [Proyecto](plataformas/flutter.md#proyecto) |
| flutter_riverpod | 3.5.0 | [Estado](plataformas/flutter.md#estado) |
| riverpod_annotation | 4.0.8 | [Estado](plataformas/flutter.md#estado) |
| riverpod_generator | 4.0.10 | [Estado](plataformas/flutter.md#estado) |
| riverpod_lint | 3.2.0 | [Estado](plataformas/flutter.md#estado) |
| go_router | 18.1.4 | [Arquitectura](plataformas/flutter.md#arquitectura) |
| http | 1.6.0 | [Red](plataformas/flutter.md#red) |
| maplibre_gl | 0.28.1 | [Mapas](plataformas/flutter.md#mapas) |
| freezed_annotation | 3.1.0 | [Arquitectura](plataformas/flutter.md#arquitectura) |
| freezed | 4.0.3 | [Arquitectura](plataformas/flutter.md#arquitectura) |
| json_annotation | 4.12.0 | [Arquitectura](plataformas/flutter.md#arquitectura) |
| json_serializable | 6.15.2 | — |
| build_runner | 2.17.1 | [Proyecto](plataformas/flutter.md#proyecto) |
| dependency_validator | 5.1.0 | [Proyecto](plataformas/flutter.md#proyecto) |
| swagger_parser | 2.4.0 | [OpenAPI y clientes](plataformas/flutter.md#openapi-y-clientes) |
| shared_preferences | 2.5.6 | [Almacenamiento](plataformas/flutter.md#almacenamiento) |
| flutter_secure_storage | 11.2.0 | [Almacenamiento](plataformas/flutter.md#almacenamiento) |
| oauth2 | 2.0.5 | [Código de autorización](plataformas/flutter.md#código-de-autorización) |
| url_launcher | 6.3.3 | [Código de autorización](plataformas/flutter.md#código-de-autorización) |
| web | 1.1.2 | [Código de autorización](plataformas/flutter.md#código-de-autorización) |
| sms_autofill | 2.6.1 | [Código por SMS](plataformas/flutter.md#código-por-sms) |
| flutter_stripe, con Stripe | 15.0.0 | [Pagos](plataformas/flutter.md#pagos) |
| flutter_webrtc | 1.6.3 | [Llamadas de voz y video](plataformas/flutter.md#llamadas-de-voz-y-video) |
| firebase_core | 5.2.0 | — |
| firebase_messaging | 17.1.0 | [Push](plataformas/flutter.md#push) |
| material_ui | 1.11.1 | [Tema](plataformas/flutter.md#tema) e [Idiomas](plataformas/flutter.md#idiomas) |
| flutter_localizations | el de Flutter 3.50.1 | — |
| intl | 0.20.3 | — |
| uuid | 4.6.0 | — |
| package_info_plus | 10.2.2 | [Versión mínima de cliente](plataformas/flutter.md#versión-mínima-de-cliente) |
| flutter_lints | 6.0.0 | [Estilo](plataformas/flutter.md#estilo) |
| flutter_test | el de Flutter 3.50.1 | [Pruebas](plataformas/flutter.md#pruebas) y [Accesibilidad](plataformas/flutter.md#accesibilidad) |

## Android

Página: [android.md](plataformas/android.md).

| Se usa | Versión | Para |
| :--- | :--- | :--- |
| JDK, con el que corre Gradle | 25.0.5 | [Proyecto](plataformas/android.md#proyecto) |
| Gradle | 9.9.2 | [Proyecto](plataformas/android.md#proyecto) |
| AGP | 9.5.2 | [Proyecto](plataformas/android.md#proyecto) |
| Kotlin | 2.4.21 | [Proyecto](plataformas/android.md#proyecto) |
| La API de Android, en `compileSdk` | 37.2 | [Proyecto](plataformas/android.md#proyecto) |
| La API de Android, en `targetSdk` | 37 | [Proyecto](plataformas/android.md#proyecto) |
| La API de Android, en `minSdk` | 28 | [Passkeys](plataformas/android.md#passkeys) |
| El plugin `org.jlleitschuh.gradle.ktlint` | 14.2.0 | [Estilo](plataformas/android.md#estilo) |
| ktlint | 1.8.0 | [Estilo](plataformas/android.md#estilo) |
| El plugin `com.autonomousapps.dependency-analysis` | 3.20.4 | [Proyecto](plataformas/android.md#proyecto) |
| KSP | 2.3.14 | [Inyección de dependencias](plataformas/android.md#inyección-de-dependencias) |
| Hilt | 2.60.1 | [Inyección de dependencias](plataformas/android.md#inyección-de-dependencias) |
| `javax.inject` | 1, la que trae Hilt | [Inyección de dependencias](plataformas/android.md#inyección-de-dependencias) |
| `androidx.hilt:hilt-lifecycle-viewmodel-compose` | 1.4.0 | [Inyección de dependencias](plataformas/android.md#inyección-de-dependencias) |
| El BOM de Compose | 2026.11.01 | [Compose](plataformas/android.md#compose) |
| `activity-compose` | 1.13.0 | [Compose](plataformas/android.md#compose) |
| `androidx.core:core` | 1.19.1 | [Idiomas](plataformas/android.md#idiomas) |
| Lifecycle | 2.11.1 | [Arquitectura](plataformas/android.md#arquitectura) |
| `kotlinx-coroutines-core` | 1.11.0 | [Corrutinas](plataformas/android.md#corrutinas) |
| Navigation 3 | 1.2.2 | [Arquitectura](plataformas/android.md#arquitectura) |
| Paging, con `paging-common` y `paging-compose` | 3.5.3 | [Paginación](plataformas/android.md#paginación) |
| WorkManager | 2.12.0 | [Arquitectura](plataformas/android.md#arquitectura) |
| Retrofit | 3.0.0 | [Arquitectura](plataformas/android.md#arquitectura) |
| OkHttp | 5.5.1 | [Arquitectura](plataformas/android.md#arquitectura) |
| `converter-kotlinx-serialization` | 3.0.0 | [OpenAPI y clientes](plataformas/android.md#openapi-y-clientes) |
| `kotlinx-serialization-json` | 1.13.0 | [OpenAPI y clientes](plataformas/android.md#openapi-y-clientes) |
| El plugin `org.openapi.generator` | 7.27.0 | [OpenAPI y clientes](plataformas/android.md#openapi-y-clientes) |
| `logging-interceptor`, para lo que genera openapi-generator | 5.5.1 | [OpenAPI y clientes](plataformas/android.md#openapi-y-clientes) |
| `converter-scalars`, para lo que genera openapi-generator | 3.0.0 | [OpenAPI y clientes](plataformas/android.md#openapi-y-clientes) |
| DataStore | 1.3.0 | [Almacenamiento](plataformas/android.md#almacenamiento) |
| `androidx.credentials`, con `credentials-play-services-auth` | 1.6.0 | [Passkeys](plataformas/android.md#passkeys) |
| `play-services-auth-api-phone` | 18.3.1 | [Código por SMS](plataformas/android.md#código-por-sms) |
| El BOM de Firebase | 35.2.0 | [Push](plataformas/android.md#push) |
| El plugin `com.google.gms.google-services` | 4.6.0 | [Push](plataformas/android.md#push) |
| MapLibre Android | 13.7.1 | [Mapas](plataformas/android.md#mapas) |
| `stripe-android`, con Stripe | 23.26.0 | [Pagos](plataformas/android.md#pagos) |
| JUnit | 4.13.2 | [Pruebas](plataformas/android.md#pruebas) |
| `kotlinx-coroutines-test` | 1.11.0 | [Pruebas](plataformas/android.md#pruebas) |
| `mockwebserver3` | 5.5.1 | [Pruebas](plataformas/android.md#pruebas) |
| `androidx.test:runner` | 1.7.0 | [Pruebas](plataformas/android.md#pruebas) |
| `androidx.test.ext:junit` | 1.3.0 | [Pruebas](plataformas/android.md#pruebas) |

## Flet

Página: [flet.md](plataformas/flet.md). Se suma a [Python](#python), y en `packages/passkey/`, `androidx.credentials` es el de [Android](#android).

| Se usa | Versión | Para |
| :--- | :--- | :--- |
| Flet, con los extras `cli` y `test` en `dev` | 1.1.3 | — |
| Flutter, en lugar de la de [Flutter](#flutter) | 3.47.9, la que pide Flet 1.1.3 | [Proyecto](plataformas/flet.md#proyecto) |
| AGP, en lugar del de [Android](#android) | 8.13.2, el de Flet 1.1.3 | [Código por SMS](plataformas/flet.md#código-por-sms) y [Passkeys](plataformas/flet.md#passkeys) |
| La API de Android, en `compileSdk` de `packages/passkey/` | 36, la que encuentra AGP 8.13.2 | [Passkeys](plataformas/flet.md#passkeys) |
| flet-secure-storage | 1.1.3 | [Almacenamiento](plataformas/flet.md#almacenamiento) |
| smart_auth, en `packages/sms/` | 4.0.0 | [Código por SMS](plataformas/flet.md#código-por-sms) |
| httpx-ws | 0.10.0 | [WebSocket](plataformas/flet.md#websocket) |
| Babel | 2.19.0 | [Idiomas](plataformas/flet.md#idiomas) |
| datamodel-code-generator, con el extra `ruff` | 0.102.0 | [OpenAPI y clientes](plataformas/flet.md#openapi-y-clientes) |
| Pydantic, en lugar de la de [Python](#python) | 2.14.3 | [Proyecto](plataformas/flet.md#proyecto) |
| appimagetool, en `build-appimage.sh` | 1.9.1, la del script de Flet 1.1.3 | [Entrega](plataformas/flet.md#entrega) |
| Inno Setup, en el runner de Windows | 6, la que trae el runner | [Entrega](plataformas/flet.md#entrega) |

## Qt

Página: [qt.md](plataformas/qt.md). Se suma a [Python](#python).

| Se usa | Versión | Para |
| :--- | :--- | :--- |
| PySide6 y Qt | 6.12.0 | [Proyecto](plataformas/qt.md#proyecto) |
| keyring | 25.7.0 | [Almacenamiento](plataformas/qt.md#almacenamiento) |
| datamodel-code-generator, con el extra `ruff` | 0.102.0 | [OpenAPI y clientes](plataformas/qt.md#openapi-y-clientes) |
| pytest-qt | 4.5.0 | [Pruebas](plataformas/qt.md#pruebas) |
| Nuitka, con el extra `onefile` | 4.3.5 | [Entrega](plataformas/qt.md#entrega) |
| imageio | 2.38.2 | [Entrega](plataformas/qt.md#entrega) |
| patchelf | 0.19.3.0 | [Entrega](plataformas/qt.md#entrega) |

## CI

Página: [repositorio.md](repositorio.md#ci). Los contenedores corresponden a Debian 13.

| Se usa | Versión |
| :--- | :--- |
| `actions/checkout` | v7 |
| `actions/setup-python` | v7 |
| `actions/setup-node` | v7 |
| `actions/setup-java` | v6 |
| `astral-sh/setup-uv` | v10.4.0 |
| `pnpm/action-setup` | v6 |
| `gradle/actions/setup-gradle` | v6 |
| `subosito/flutter-action` | v2 |
| El contenedor `postgis/postgis` | 17-3.5 |
| El contenedor `valkey/valkey` | 8.1 |
| El contenedor `debian` | trixie |

## Cumplimiento

| Convención | Herramienta |
| :--- | :--- |
| Python, Node, Flutter y el JDK, en los workflows de cada repositorio | [scripts/verificar.py](scripts/verificar.py) |
| Las versiones de los paquetes de Python, FastAPI, Autenticación, PostgreSQL, Flet y Qt, en cada `pyproject.toml`, y sus extras, en el de cada pieza | [scripts/verificar.py](scripts/verificar.py) |
| Las versiones de los paquetes de SvelteKit y la de pnpm, en cada `package.json` | [scripts/verificar.py](scripts/verificar.py) |
| Las versiones de los paquetes de Flutter, en cada `pubspec.yaml`, y la de Dart, en el de cada pieza | [scripts/verificar.py](scripts/verificar.py) |
| Gradle, AGP y Kotlin, en Android y en Flutter | [scripts/verificar.py](scripts/verificar.py) |
| Las versiones de los plugins y las bibliotecas de Android, en `libs.versions.toml`, y las API de Android y ktlint, en `app/build.gradle.kts` | [scripts/verificar.py](scripts/verificar.py) |
| La versión de uv, en cada `pyproject.toml` | [scripts/verificar.py](scripts/verificar.py) |
| Las acciones y los contenedores de CI | [scripts/verificar.py](scripts/verificar.py) |
| Que la plantilla y los scripts de Canone no declaran otra versión | `scripts/verificar.py --canone` en CI |
| Una tecnología que está en dos bloques lleva la misma versión, salvo la fila que dice «en lugar de» | `scripts/verificar.py --canone` en CI |
