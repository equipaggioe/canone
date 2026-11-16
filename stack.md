# Stack

Qué se usa en cada plataforma y en qué versión. Es el único lugar donde se fija: las páginas de [plataformas/](plataformas/) escriben cómo se usa, y no repiten las versiones.

## Quién decide

- El stack lo decide el desarrollador. Lo que una pieza necesita y no está aquí no se elige por cuenta propia: se presentan las opciones con una recomendación, y decide el desarrollador. Cambiar lo que ya está aquí se decide igual.
- La plataforma de cada pieza la elige cada repositorio. Aquí está lo que se usa dentro de cada plataforma, y a un repositorio solo le aplican los bloques de las plataformas que usa.
- El bloque de una página en desarrollo lleva su misma nota, y no se aplica mientras la tenga ([plataformas/README.md](plataformas/README.md#en-desarrollo)).

## Qué entra

- Entra lo que una pieza declara en su manifiesto o instala, con su versión.
- Lo que una pieza usa, pero cuya versión fija otra tecnología, entra con una nota que dice cuál, como «3.13.7, el de Flutter 3.47.9» o «0.28.1, la que fija firebase-admin»: su versión no se elige, se sigue.
- Todo paquete que importa el código de una pieza está declarado en su manifiesto, aunque otro paquete ya lo traiga: un import que funciona porque otro paquete lo trajo se rompe cuando ese paquete cambia.
- Toda dependencia declarada se usa. Lo que llega dentro de otro paquete y el código no importa no entra ni se nombra en ningún lado.
- La página de cada plataforma dice con qué herramienta lo comprueba su CI: [python.md](plataformas/python.md#dependencias), [flutter.md](plataformas/flutter.md#proyecto), [sveltekit.md](plataformas/sveltekit.md#proyecto) y [android.md](plataformas/android.md#proyecto).

## Versiones

- La versión se fija por tecnología, no por pieza: una tecnología lleva la misma versión en todas las piezas que la usan.
- Lo que el servidor instala desde los paquetes de su sistema, como Python, PostgreSQL o Valkey, usa la versión de esos paquetes en todas las piezas, también en las que no corren en el servidor, en la máquina de desarrollo y en CI: así se desarrolla y se prueba con la misma versión que corre en producción.
- Lo demás usa la última versión estable, o la última LTS si la tecnología las publica.
- Una excepción lleva su razón en la página de su plataforma.
- La plantilla y las fuentes dependen de este archivo: la plantilla no declara una versión que este archivo no estipule, y las fuentes se descargan de esa versión.

En cada bloque, «Para» enlaza la sección de la página que escribe cómo se usa.

## Python

Página: [python.md](plataformas/python.md). Vale para toda pieza en Python.

| Se usa | Versión | Para |
| :--- | :--- | :--- |
| Python | 3.13, el de Debian 13 | [Proyecto](plataformas/python.md#proyecto) |
| uv | 0.13.7 | [Proyecto](plataformas/python.md#proyecto) |
| `uv_build` | 0.13.7 | [Proyecto](plataformas/python.md#proyecto) |
| pytest | 9.2.0 | [Pruebas](plataformas/python.md#pruebas) |
| ruff | 0.17.3 | [Estilo](plataformas/python.md#estilo) |
| Pyrefly | 1.4.0 | [Tipos](plataformas/python.md#tipos) |
| deptry | 0.25.1 | [Dependencias](plataformas/python.md#dependencias) |
| pip-audit | 2.10.1 | [Cumplimiento](plataformas/python.md#cumplimiento) |
| Pydantic | 2.14.3 | [Esquemas](plataformas/fastapi.md#esquemas) |
| httpx | 0.28.1, la que fija firebase-admin | [Pruebas](plataformas/fastapi.md#pruebas) del servidor y [Red](plataformas/flet.md#red) de Flet |

## FastAPI

Página: [fastapi.md](plataformas/fastapi.md).

| Se usa | Versión | Para |
| :--- | :--- | :--- |
| FastAPI | 0.162.0 | — |
| Starlette | 1.10.0 | — |
| pydantic-settings | 2.16.2 | [Configuración](plataformas/fastapi.md#configuración) |
| SQLAlchemy | 2.1.8 | [Base de datos](plataformas/fastapi.md#base-de-datos) |
| asyncpg | 0.32.0 | [Base de datos](plataformas/fastapi.md#base-de-datos) |
| Alembic | 1.20.1 | [Migraciones](plataformas/fastapi.md#migraciones) |
| valkey-py | 6.2.0 | [Valkey](plataformas/fastapi.md#valkey) |
| Uvicorn | 0.54.0 | [WebSocket](plataformas/fastapi.md#websocket) y [Procesos](plataformas/despliegue.md#procesos) |
| Pillow | 13.0.0 | [Archivos](plataformas/fastapi.md#archivos) |
| Babel | 2.18.0 | [Idiomas](plataformas/fastapi.md#idiomas) |
| cryptography | 50.0.2 | [Paginación](plataformas/fastapi.md#paginación) |
| pywebpush | 2.5.0 | [Push](plataformas/fastapi.md#push) |
| aiohttp | 3.14.5 | [Push](plataformas/fastapi.md#push) |
| firebase-admin | 7.7.0 | [Push](plataformas/fastapi.md#push) |
| OpenTelemetry | 1.45.2 | [Trazas](plataformas/fastapi.md#trazas) |
| AnyIO | 4.16.0 | [Pruebas](plataformas/fastapi.md#pruebas) |
| httpx-ws | 0.9.0 | [Pruebas](plataformas/fastapi.md#pruebas) |

## Autenticación

Página: [autenticacion.md](plataformas/autenticacion.md). Son paquetes del servidor.

| Se usa | Versión | Para |
| :--- | :--- | :--- |
| pwdlib | 0.3.1 | [Contraseñas](plataformas/autenticacion.md#contraseñas) |
| phonenumbers | 9.0.43 | [Código por SMS](plataformas/autenticacion.md#código-por-sms) |
| webauthn | 3.0.1 | [Passkeys](plataformas/autenticacion.md#passkeys) |
| PyJWT | 2.15.1 | [Token de acceso](plataformas/autenticacion.md#token-de-acceso) |

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
| systemd | 257 | [Procesos](plataformas/despliegue.md#procesos) |
| OpenSSH | 10.0 | [SSH](plataformas/despliegue.md#ssh) |
| WireGuard | 1.0.20210914 | [Registros](plataformas/despliegue.md#registros) |
| restic | 0.18.0 | [Respaldos](plataformas/despliegue.md#respaldos) |
| rest-server | 0.14.0 | [Respaldos](plataformas/despliegue.md#respaldos) |

## Java

Página: [java.md](plataformas/java.md).

| Se usa | Versión | Para |
| :--- | :--- | :--- |
| Java | 21, el JRE de Debian 13 | [Proyecto](plataformas/java.md#proyecto) |

## SvelteKit

> **En desarrollo; no se implementa:** [README.md](plataformas/README.md#en-desarrollo).

Página: [sveltekit.md](plataformas/sveltekit.md).

| Se usa | Versión | Para |
| :--- | :--- | :--- |
| Node | 26.13.1 | [Proyecto](plataformas/sveltekit.md#proyecto) |
| pnpm | 12.18.0 | [Proyecto](plataformas/sveltekit.md#proyecto) |
| SvelteKit | 3.2.0 | — |
| Svelte | 5.57.3 | — |
| Vite | 8.3.8 | — |
| `@sveltejs/vite-plugin-svelte` | 7.3.1 | — |
| `@sveltejs/adapter-static` | 4.0.1 | [Adaptador](plataformas/sveltekit.md#adaptador) |
| TypeScript | 6.0.3 | [Tipos](plataformas/sveltekit.md#tipos) |
| `svelte-check` | 4.7.8 | [Tipos](plataformas/sveltekit.md#tipos) |
| `@types/node` | 26.6.6 | [Proyecto](plataformas/sveltekit.md#proyecto) |
| knip | 6.45.1 | [Proyecto](plataformas/sveltekit.md#proyecto) |
| Prettier | 3.10.1 | [Estilo](plataformas/sveltekit.md#estilo) |
| `prettier-plugin-svelte` | 4.1.1 | [Estilo](plataformas/sveltekit.md#estilo) |
| ESLint | 10.15.0 | [Estilo](plataformas/sveltekit.md#estilo) |
| `eslint-plugin-svelte` | 3.24.1 | [Estilo](plataformas/sveltekit.md#estilo) |
| `typescript-eslint` | 8.72.2 | [Estilo](plataformas/sveltekit.md#estilo) |
| `@eslint/js` | 10.0.1 | [Estilo](plataformas/sveltekit.md#estilo) |
| `globals` | 17.14.0 | [Estilo](plataformas/sveltekit.md#estilo) |
| `eslint-config-prettier` | 10.1.8 | [Estilo](plataformas/sveltekit.md#estilo) |
| UnoCSS | 66.13.0 | [Estilos](plataformas/sveltekit.md#estilos) |
| Paraglide | 3.2.2 | [Idiomas](plataformas/sveltekit.md#idiomas) |
| `openapi-typescript` | 7.13.0 | [Carga de datos](plataformas/sveltekit.md#carga-de-datos) |
| `openapi-fetch` | 0.17.0 | [Carga de datos](plataformas/sveltekit.md#carga-de-datos) |
| MapLibre GL JS, `maplibre-gl` | 6.18.0 | [Mapas](plataformas/sveltekit.md#mapas) |
| Vitest | 5.1.0 | [Pruebas](plataformas/sveltekit.md#pruebas) |
| Playwright | 1.65.1 | [Pruebas](plataformas/sveltekit.md#pruebas) |
| `@axe-core/playwright` | 4.14.0 | [Accesibilidad](plataformas/sveltekit.md#accesibilidad) |

## Flutter

> **En desarrollo; no se implementa:** [README.md](plataformas/README.md#en-desarrollo).

Página: [flutter.md](plataformas/flutter.md). Gradle, AGP y Kotlin son los de [Android](#android).

| Se usa | Versión | Para |
| :--- | :--- | :--- |
| Flutter | 3.47.9 | — |
| Dart | 3.13.7, el de Flutter 3.47.9 | [Proyecto](plataformas/flutter.md#proyecto) |
| flutter_riverpod | 3.5.0 | [Estado](plataformas/flutter.md#estado) |
| riverpod_annotation | 4.0.8 | [Estado](plataformas/flutter.md#estado) |
| riverpod_generator | 4.0.10 | [Estado](plataformas/flutter.md#estado) |
| riverpod_lint | 3.2.0 | [Estado](plataformas/flutter.md#estado) |
| go_router | 18.1.4 | [Arquitectura](plataformas/flutter.md#arquitectura) |
| http | 1.6.0 | [Arquitectura](plataformas/flutter.md#arquitectura) |
| maplibre_gl | 0.28.0 | [Mapas](plataformas/flutter.md#mapas) |
| freezed_annotation | 3.1.0 | [Arquitectura](plataformas/flutter.md#arquitectura) |
| freezed | 4.0.3 | [Arquitectura](plataformas/flutter.md#arquitectura) |
| json_annotation | 4.12.0 | [Arquitectura](plataformas/flutter.md#arquitectura) |
| json_serializable | 6.15.2 | [Arquitectura](plataformas/flutter.md#arquitectura) |
| build_runner | 2.17.1 | [Proyecto](plataformas/flutter.md#proyecto) |
| dependency_validator | 5.1.0 | [Proyecto](plataformas/flutter.md#proyecto) |
| swagger_parser | 2.1.1 | [OpenAPI y clientes](plataformas/flutter.md#openapi-y-clientes) |
| shared_preferences | 2.5.6 | [Almacenamiento](plataformas/flutter.md#almacenamiento) |
| flutter_secure_storage | 11.2.0 | [Almacenamiento](plataformas/flutter.md#almacenamiento) |
| flutter_appauth | 13.0.0 | [Autenticación](plataformas/flutter.md#autenticación) |
| sms_autofill | 2.6.1 | [Código por SMS](plataformas/flutter.md#código-por-sms) |
| flutter_stripe, con Stripe | 14.2.0 | [Pagos](plataformas/flutter.md#pagos) |
| firebase_core | 5.1.0 | [Push](plataformas/flutter.md#push) |
| firebase_messaging | 17.0.1 | [Push](plataformas/flutter.md#push) |
| flutter_lints | 6.0.0 | [Estilo](plataformas/flutter.md#estilo) |

## Android

> **En desarrollo; no se implementa:** [README.md](plataformas/README.md#en-desarrollo).

Página: [android.md](plataformas/android.md).

| Se usa | Versión | Para |
| :--- | :--- | :--- |
| JDK, con el que corre Gradle | 25.0.5 | [Proyecto](plataformas/android.md#proyecto) |
| Gradle | 9.9.1 | [Proyecto](plataformas/android.md#proyecto) |
| AGP | 9.5.1 | [Proyecto](plataformas/android.md#proyecto) |
| Kotlin | 2.4.21 | [Proyecto](plataformas/android.md#proyecto) |
| La API de Android, en `compileSdk` | 37.2 | [Proyecto](plataformas/android.md#proyecto) |
| La API de Android, en `targetSdk` | 37 | [Proyecto](plataformas/android.md#proyecto) |
| La API de Android, en `minSdk` | 28 | [Passkeys](plataformas/android.md#passkeys) |
| El plugin `org.jlleitschuh.gradle.ktlint` | 14.2.0 | [Estilo](plataformas/android.md#estilo) |
| ktlint | 1.8.0 | [Estilo](plataformas/android.md#estilo) |
| El plugin `com.autonomousapps.dependency-analysis` | 3.20.3 | [Proyecto](plataformas/android.md#proyecto) |
| KSP | 2.3.13 | [Inyección de dependencias](plataformas/android.md#inyección-de-dependencias) |
| Hilt | 2.60.1 | [Inyección de dependencias](plataformas/android.md#inyección-de-dependencias) |
| `androidx.hilt:hilt-lifecycle-viewmodel-compose` | 1.4.0 | [Inyección de dependencias](plataformas/android.md#inyección-de-dependencias) |
| El BOM de Compose | 2026.09.00 | [Compose](plataformas/android.md#compose) |
| `activity-compose` | 1.13.0 | [Compose](plataformas/android.md#compose) |
| Lifecycle | 2.11.0 | [Arquitectura](plataformas/android.md#arquitectura) |
| Navigation 3 | 1.2.1 | [Arquitectura](plataformas/android.md#arquitectura) |
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
| El BOM de Firebase | 35.2.0 | [Push](plataformas/transversal.md#push) |
| El plugin `com.google.gms.google-services` | 4.6.0 | [Push](plataformas/transversal.md#push) |
| MapLibre Android | 13.7.1 | [Mapas](plataformas/android.md#mapas) |
| `stripe-android`, con Stripe | 23.26.0 | [Pagos](plataformas/android.md#pagos) |
| JUnit | 4.13.2 | [Pruebas](plataformas/android.md#pruebas) |
| `kotlinx-coroutines-test` | 1.11.0 | [Pruebas](plataformas/android.md#pruebas) |
| `mockwebserver3` | 5.5.1 | [Pruebas](plataformas/android.md#pruebas) |
| `androidx.test:runner` | 1.7.0 | [Pruebas](plataformas/android.md#pruebas) |
| `androidx.test.ext:junit` | 1.3.0 | [Pruebas](plataformas/android.md#pruebas) |
| `espresso-core` | 3.7.0 | [Proyecto](plataformas/android.md#proyecto) |

## Flet

> **En desarrollo; no se implementa:** [README.md](plataformas/README.md#en-desarrollo).

Página: [flet.md](plataformas/flet.md). Se suma a [Python](#python), y Flutter es el de [Flutter](#flutter).

| Se usa | Versión | Para |
| :--- | :--- | :--- |
| Flet | 1.1.2 | — |
| flet-secure-storage | 1.1.2 | [Almacenamiento](plataformas/flet.md#almacenamiento) |
| httpx-ws | 0.9.0 | [WebSocket](plataformas/flet.md#websocket) |
| datamodel-code-generator, con el extra `ruff` | 0.95.0 | [OpenAPI y clientes](plataformas/flet.md#openapi-y-clientes) |
| Pydantic, en lugar de la de [Python](#python) | 2.13.4 | [Proyecto](plataformas/flet.md#proyecto) |

## Qt

> **En desarrollo; no se implementa:** [README.md](plataformas/README.md#en-desarrollo).

Página: [qt.md](plataformas/qt.md). Se suma a [Python](#python).

| Se usa | Versión | Para |
| :--- | :--- | :--- |
| PySide6 y Qt | 6.12.0 | [Proyecto](plataformas/qt.md#proyecto) |
| keyring | 25.7.0 | [Almacenamiento](plataformas/qt.md#almacenamiento) |
| datamodel-code-generator, con el extra `ruff` | 0.95.0 | [OpenAPI y clientes](plataformas/qt.md#openapi-y-clientes) |
| pytest-qt | 4.5.0 | [Pruebas](plataformas/qt.md#pruebas) |
| Nuitka | 4.3.5 | [Entrega](plataformas/qt.md#entrega) |
| imageio | 2.38.1 | [Entrega](plataformas/qt.md#entrega) |
| patchelf | 0.19.3.0 | [Entrega](plataformas/qt.md#entrega) |

## CI

Página: [repositorio.md](repositorio.md#ci). Los contenedores corresponden a Debian 13.

| Se usa | Versión |
| :--- | :--- |
| `actions/checkout` | v7 |
| `actions/setup-python` | v7 |
| `actions/setup-node` | v7 |
| `actions/setup-java` | v6 |
| `astral-sh/setup-uv` | v10.3.3 |
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
| Las versiones de los paquetes de Python, FastAPI, Autenticación, PostgreSQL, Flet y Qt, en cada `pyproject.toml` | [scripts/verificar.py](scripts/verificar.py) |
| Las versiones de los paquetes de SvelteKit y la de pnpm, en cada `package.json` | [scripts/verificar.py](scripts/verificar.py) |
| Las versiones de los paquetes de Flutter, en cada `pubspec.yaml` | [scripts/verificar.py](scripts/verificar.py) |
| Gradle, AGP y Kotlin, en Android y en Flutter, y los plugins de ktlint y de dependency-analysis | [scripts/verificar.py](scripts/verificar.py) |
| La versión de uv, en cada `pyproject.toml` | [scripts/verificar.py](scripts/verificar.py) |
| Las acciones de CI y los contenedores `postgis/postgis` y `valkey/valkey` | [scripts/verificar.py](scripts/verificar.py) |
