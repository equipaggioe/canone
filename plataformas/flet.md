# Flet

Una aplicación en Flet. Se suma a [python.md](python.md).

## Proyecto

Estándar: [*Publishing a Flet app*](../fuentes/flet/publish.md) de Flet.

- CI pone en el `PATH` el Flutter de [stack.md](../stack.md#flet), con la versión mayor y menor que pide Flet: `flet build` usa el del `PATH` si coinciden, y si no, descarga el suyo. [Flet 1.1.2](https://raw.githubusercontent.com/flet-dev/flet/v1.1.2/sdk/python/packages/flet-cli/src/flet_cli/commands/flutter_base.py)
- Pydantic es la que fija [stack.md](../stack.md#flet), y no la del bloque de Python: `flet build apk` instala desde el índice de Flet para Android, y esa es la última Pydantic cuyo `pydantic-core` está en él. [Índice de Flet](https://pypi.flet.dev/pydantic-core/)
- `[tool.flet.flutter.pubspec.dependency_overrides]` fija `jni` y `jni_flutter` en las versiones de [stack.md](../stack.md#flet): con `jni` 1.2.0 y `jni_flutter` 1.1.0, que `path_provider_android` 2.3.1 resuelve, la app de Android no arranca y muestra `ClassNotFoundException: Landroid/content/Context;`.
- Las dependencias de `[project]` van exactas, con `==`, en lugar del `>=` de [python.md](python.md): `flet build` no lee `uv.lock` y le pasa a pip las dependencias tal como están escritas. [Flet 1.1.2](https://raw.githubusercontent.com/flet-dev/flet/v1.1.2/sdk/python/packages/flet-cli/src/flet_cli/commands/build_base.py)
- `flet build` y `flet test` corren con `PIP_CONSTRAINT` en el `uv.lock` exportado con `uv export --locked --no-dev --no-emit-project --no-emit-local --no-hashes`: así las dependencias transitivas que resuelve pip llevan las versiones de `uv.lock`. Una ruta local en las restricciones hace fallar a pip.
- Un paquete local del repositorio entra a `flet build` por `[tool.flet].dev_packages`, con la ruta a su wheel, construido antes con `uv build --wheel`: `flet build` no lee `[tool.uv.sources]`, y para Android pip no puede construir una carpeta.
- El grupo `dev` lleva también `flet` con el extra `cli`, que trae `flet build`. [Flet 1.1.2](https://raw.githubusercontent.com/flet-dev/flet/v1.1.2/website/docs/getting-started/installation.md)
- El proyecto no lleva `[build-system]`, en lugar del `uv_build` de [python.md](python.md): sin `src/app/`, no hay paquete que construir.
- `src/` no lleva `__init__.py`, en lugar de lo que pide [Paquetes](python.md#paquetes): `flet build` empaqueta `src/` como la raíz de la app, y sus módulos de primer nivel no son de ningún paquete.
- El código va directo en `src/`, sin paquete, en lugar del `src/app/` de [python.md](python.md), y `[tool.flet.app]` lleva `path = "src"`: es la estructura que supone `flet build`, que empaqueta `src/` por su cuenta ([Publishing, *Project structure*](../fuentes/flet/publish.md) y [*How it works*](../fuentes/flet/publish.md)):

```text
<pieza>/
  .gitignore
  pyproject.toml
  uv.lock
  installer.iss         el instalador de Windows
  build-appimage.sh     el AppImage de Linux
  src/
    main.py
    colors.py
    theme.py
    assets/
      icon.png
    api/                lo que habla HTTP
      __init__.py
      client.py         las llamadas al servidor propio, escritas a mano
      models.py         los modelos del cable, generados
      <servicio>.py     un servicio externo: sus llamadas y sus modelos
      ruff.toml         permite httpx
    services/           lo que no es interfaz ni HTTP
      __init__.py
      <módulo>.py
      <dominio>/
        __init__.py
        <módulo>.py
    locales/
      <idioma>/LC_MESSAGES/<pieza>.po
    views/              una vista por ruta
      __init__.py
      <ruta>.py
  tests/
    __init__.py
    test_theme.py
    test_<módulo>.py
```

Plantilla: [plantilla/flet/](../plantilla/flet/), el job `flet` de [plantilla/.github/workflows/ci.yml](../plantilla/.github/workflows/ci.yml) y los jobs `flet-mobile` y `flet-desktop` de [plantilla/.github/workflows/release.yml](../plantilla/.github/workflows/release.yml). `src/api/ruff.toml` se copia sin editar; `pyproject.toml`, `installer.iss` y `build-appimage.sh` son un punto de partida.

## Componentes

Estándar: [*Declarative vs Imperative*](../fuentes/flet/declarative-vs-imperative.md) de Flet.

- Una pieza de interfaz reutilizable es un `@ft.component`, y no una subclase de un control con `@ft.control`.
- Un diálogo se muestra con `ft.use_dialog()`, desde el estado del componente, y no con `page.show_dialog()`. [Flet 1.1.2](https://raw.githubusercontent.com/flet-dev/flet/v1.1.2/website/docs/cookbook/declarative-dialogs.md)
- Una lista de cientos de elementos usa `ListView` o `GridView`, que dibujan solo lo visible, y no `Column` ni `Row`, que dibujan todo. [Flet 1.1.2](https://raw.githubusercontent.com/flet-dev/flet/v1.1.2/website/docs/cookbook/large-lists.md)
- Un `ListView` cuyos elementos miden lo mismo lleva `item_extent` o `first_item_prototype`. [Flet 1.1.2](https://raw.githubusercontent.com/flet-dev/flet/v1.1.2/website/docs/cookbook/large-lists.md)
- La interfaz es declarativa: cada pantalla es un `@ft.component` que devuelve sus controles a partir del estado, y ningún handler cambia las propiedades de un control ni `page.controls` ([Declarative vs Imperative, *Declarative*](../fuentes/flet/declarative-vs-imperative.md)).
- El estado que comparten varios componentes vive en clases `@ft.observable`, y sus cambios son métodos de esas clases ([Declarative vs Imperative, *Observables*](../fuentes/flet/declarative-vs-imperative.md) y [*Example*](../fuentes/flet/declarative-vs-imperative.md)).
- El estado que es solo de una vista, como si una fila está en edición, vive en un hook como `ft.use_state`, y no en el observable ([Declarative vs Imperative, *Hooks*](../fuentes/flet/declarative-vs-imperative.md) y [*Example*](../fuentes/flet/declarative-vs-imperative.md)).

## Async

Estándar: [*Async apps*](../fuentes/flet/async-apps.md) de Flet.

- Un componente que trabaja en segundo plano al montarse, como cargar datos, lo hace en `ft.use_effect` con un setup `async` y dependencias vacías: Flet cancela el setup al desmontar el componente. [Flet 1.1.2](https://raw.githubusercontent.com/flet-dev/flet/v1.1.2/sdk/python/packages/flet/src/flet/components/hooks/use_effect.py)
- Ningún handler bloquea, sea síncrono o async: los dos corren en el único bucle de eventos de la app, y mientras uno corre no se despacha otro evento ni se actualiza la pantalla ([Async apps, *Never block the event loop*](../fuentes/flet/async-apps.md) y [*Control event handlers*](../fuentes/flet/async-apps.md)).
- Un handler que espera algo es `async def` ([Async apps, *Control event handlers*](../fuentes/flet/async-apps.md)).
- Una tarea que sigue después del handler que la lanza se crea con `page.run_task()`, que recibe la función y sus argumentos, guarda la referencia de la tarea y reporta sus excepciones ([Async apps, *Async lambdas*](../fuentes/flet/async-apps.md) y [*Background tasks*](../fuentes/flet/async-apps.md)).
- Una llamada que bloquea corre con `await asyncio.to_thread()` o, si no hace falta su resultado, con `page.run_thread()` ([Async apps, *Threading*](../fuentes/flet/async-apps.md)).

## Navegación

Estándares: [*Router*](../fuentes/flet/router.md) y [*Navigation and Routing*](../fuentes/flet/navigation-and-routing.md) de Flet.

- Con `manage_views=True`, el componente `not_found` devuelve un control, y no una `View`: el `Router` ya lo pone en una, y una `View` dentro de otra falla al dibujarse.
- La navegación usa `ft.Router` con `manage_views=True`, y la app arranca con `page.render_views()`: cada nivel de la ruta es una `View`, con la vuelta atrás del sistema y de la `AppBar` ([Router, *Multi-view navigation*](../fuentes/flet/router.md)).
- Un parámetro de la ruta se lee con `ft.use_route_params()` ([Router, *Dynamic segments, optional segments, and splats*](../fuentes/flet/router.md)).
- Las pantallas que piden sesión cuelgan de una ruta de layout que, sin sesión, navega al inicio de sesión ([Router, *Authentication*](../fuentes/flet/router.md)).
- Una ruta que no existe muestra el componente `not_found` del `Router` ([Router, *404 handling*](../fuentes/flet/router.md)).
- Toda ruta a la que se navega empieza con `/` ([Navigation and Routing, *Route basics*](../fuentes/flet/navigation-and-routing.md)).
- Se navega con `page.navigate()` desde un callback síncrono, y con `await page.push_route()` desde uno async ([Navigation and Routing, *Programmatic navigation*](../fuentes/flet/navigation-and-routing.md)).
- Un parámetro opcional de la query se lee con `page.query.to_dict.get()`: `page.query.get()` lanza `KeyError` si falta ([Navigation and Routing, *Query strings*](../fuentes/flet/navigation-and-routing.md)).
- Una vista que pide confirmar la vuelta atrás, como una con cambios sin guardar, lleva `can_pop` en `False` y confirma en `on_confirm_pop` ([Navigation and Routing, *Back navigation and pop confirmation*](../fuentes/flet/navigation-and-routing.md)).

## Ciclo de vida

Estándar: [*Publishing a Flet app*](../fuentes/flet/publish.md) de Flet.

- Lo que no puede perderse se guarda antes de salir, sin depender de la limpieza al terminar: una app construida termina en el acto, sin correr los `atexit`, los finalizadores ni las escrituras pendientes ([Publishing, *How a built app terminates*](../fuentes/flet/publish.md)).
- El handler del evento `CLOSE` de la ventana es corto: retiene la salida de la app ([Publishing, *How a built app terminates*](../fuentes/flet/publish.md)).

## Accesibilidad

Estándar: [*Accessibility*](../fuentes/flet/accessibility.md) de Flet.

Contrato: [transversal.md](transversal.md#accesibilidad).

- Un `Text` cuyo texto no sirve como nombre lleva `semantics_label` ([Accessibility, *Text*](../fuentes/flet/accessibility.md)).
- Un `IconButton`, un `FloatingActionButton` y un `PopupMenuButton` llevan `tooltip`, que es su nombre para el lector de pantalla ([Accessibility, *Buttons*](../fuentes/flet/accessibility.md)).
- Un `TextField` y un `Dropdown` llevan `label` ([Accessibility, *`TextField` and `Dropdown`*](../fuentes/flet/accessibility.md)).
- Un control que no tiene por otra vía su nombre, su rol o su estado va dentro de un `Semantics` ([Accessibility, *Custom semantics*](../fuentes/flet/accessibility.md)).

## Almacenamiento

Estándar: [*Packaging app for Windows*](../fuentes/flet/publish-windows.md) de Flet.

- Lo sensible, como el token de refresco que pide [autenticacion.md](autenticacion.md#sesión), va en `SecureStorage`, de flet-secure-storage, que usa el almacén de credenciales del sistema: cifrarlo a mano obliga a guardar la clave en algún lado. [Flet 1.1.2](https://raw.githubusercontent.com/flet-dev/flet/v1.1.2/website/docs/services/securestorage/index.md)
- En Android, `[tool.flet.android.manifest_application]` lleva `allowBackup = false`: `SecureStorage` usa flutter_secure_storage, y una copia restaurada en otro dispositivo trae datos cuya clave no se puede recuperar. [flutter_secure_storage 10.3.1](https://raw.githubusercontent.com/juliansteenbakker/flutter_secure_storage/v10.3.1/flutter_secure_storage/README.md)
- `SharedPreferences` guarda solo preferencias, y ningún dato de la app que no pueda perderse. [Flet 1.1.2](https://raw.githubusercontent.com/flet-dev/flet/v1.1.2/website/docs/cookbook/client-storage.md)
- Un servicio, como `SharedPreferences` o `SecureStorage`, se crea una vez, y la app guarda su referencia mientras lo usa: Flet lo da de baja cuando no queda ninguna. [Flet 1.1.2](https://raw.githubusercontent.com/flet-dev/flet/v1.1.2/website/docs/cookbook/client-storage.md)
- La app guarda sus archivos en `FLET_APP_STORAGE_DATA`, nunca junto a `__file__`: la carpeta donde se instala la app puede no admitir escritura ([Packaging app for Windows, *Distributing*](../fuentes/flet/publish-windows.md)).

## Código de autorización

Contrato: [autenticacion.md](autenticacion.md#código-de-autorización).

- La app abre la petición de autorización con `UrlLauncher().launch_url()` en `LaunchMode.IN_APP_BROWSER_VIEW`: es una pestaña del navegador en Android y `SFSafariViewController` en iOS, donde la passkey funciona. [Flet 1.1.2](https://raw.githubusercontent.com/flet-dev/flet/v1.1.2/sdk/python/packages/flet/src/flet/controls/services/url_launcher.py), [url_launcher_ios 6.4.2](https://raw.githubusercontent.com/flutter/packages/url_launcher_ios-v6.4.2/packages/url_launcher/url_launcher_ios/ios/url_launcher_ios/Sources/url_launcher_ios/URLLaunchSession.swift), [WebKit](https://webkit.org/blog/11312/meet-face-id-and-touch-id-for-the-web/)
- En Android, la URI `https` de retorno se declara en `[[tool.flet.android.activity.intent_filter]]`, con `autoVerify = true`, y no en `[tool.flet.deep_linking]`, cuyo filtro no lleva `android:autoVerify`. [Flet 1.1.2](https://raw.githubusercontent.com/flet-dev/flet/v1.1.2/website/docs/publish/index.md)
- En iOS, el retorno llega a un esquema propio con el dominio al revés, declarado en `[tool.flet.ios.deep_linking]`: iOS abre en Safari un Universal Link del mismo dominio que la página. [Apple](https://developer.apple.com/documentation/xcode/allowing-apps-and-websites-to-link-to-your-content)
- En iOS, la app cierra la pestaña con `UrlLauncher().close_in_app_web_view()` cuando recibe el retorno: `SFSafariViewController` se abre sobre la app y no se cierra solo. [url_launcher_ios 6.4.2](https://raw.githubusercontent.com/flutter/packages/url_launcher_ios-v6.4.2/packages/url_launcher/url_launcher_ios/lib/url_launcher_ios.dart)

## Contraseñas

Contrato: [autenticacion.md](autenticacion.md#contraseñas).

- Los campos para entrar y para elegir una contraseña van en un `AutofillGroup`, y los gestores de contraseñas los completan por sus `autofill_hints`: al entrar, `AutofillHint.USERNAME` en el del correo o el teléfono y `AutofillHint.PASSWORD` en el de la contraseña, y al elegir una, `AutofillHint.NEW_PASSWORD`.
- El campo de la contraseña lleva `password` y `can_reveal_password`.

## Idiomas

Contrato: [transversal.md](transversal.md#idiomas).

- Los textos usan `gettext` de la biblioteca estándar de Python, con catálogos `.po`. Flet no trae un sistema de traducción.
- Babel compila el `.mo` de cada catálogo, con `pybabel compile -d src/locales -D <pieza>`, y va en el grupo `dev`: `gettext` lee solo el `.mo`. [Python 3.13](https://raw.githubusercontent.com/python/cpython/3.13/Doc/library/gettext.rst)
- Los catálogos van en `src/locales/<idioma>/LC_MESSAGES/<pieza>.po`. El `.mo` se genera antes de `flet build` y de `flet test`, y no va en git: sale del `.po`, y en git quedaría desfasado.
- `page.locale_configuration` declara en `supported_locales` los idiomas de la app, con el base primero, y en `current_locale`, el que eligió el usuario: sin ella, los controles de Flutter quedan en `en-US`, y un idioma que no está en la lista cae en el primero. [Flet 1.1.2](https://raw.githubusercontent.com/flet-dev/flet/v1.1.2/sdk/python/packages/flet/src/flet/controls/types.py)

## OpenAPI y clientes

Contrato: [transversal.md](transversal.md#openapi-y-clientes).

- datamodel-code-generator genera desde `../server/openapi.json` los modelos del cable en `src/api/models.py`, con la configuración de `[tool.datamodel-codegen]`: modelos de Pydantic v2, campos en snake_case con su alias en camelCase y `extra="forbid"` en cada esquema que declara `additionalProperties: false`. Un modelo generado rechaza un campo y un valor de enum que no conoce.
- `src/api/models.py` se versiona, y CI lo vuelve a generar y falla si cambia: `flet build` empaqueta `src/` tal como está.
- `src/api/models.py` no lleva docstrings propios: los suyos son las descripciones de los esquemas del servidor, y ruff no le exige las reglas `D1`.
- Las llamadas a la API se escriben a mano en `api/client.py`, con el `httpx.AsyncClient` de [Red](#red): datamodel-code-generator genera solo los modelos.

## Red

- HTTP va por un solo `httpx.AsyncClient`, con `await` desde handlers async, y las respuestas se leen con los modelos de `api/`: no bloquea el bucle de eventos y reutiliza las conexiones.
- Los reintentos de [transversal.md](transversal.md#reintentos) se escriben a mano en `api/`: el `retries` del transporte de httpx solo reintenta una conexión que falla, y no un 502, un 503 ni un 504. [httpx 0.28.1](https://raw.githubusercontent.com/encode/httpx/0.28.1/httpx/_transports/default.py)

## Tema

> **En desarrollo; no se implementa:** [transversal.md](transversal.md#tema).

Contrato: [transversal.md](transversal.md#tema).

- `page.theme` y `page.dark_theme` se arman en `theme.py` con `LIGHT` y `DARK`, generados en `colors.py`, y `page.theme_mode` sale de la elección del usuario, guardada en `SharedPreferences`: `ThemeMode.SYSTEM` mientras no elija otro.
- Los tamaños van en `theme.py`, sin tamaños literales fuera de él.

Plantilla: `theme.py` y `tests/test_theme.py` de [plantilla/flet/](../plantilla/flet/), en desarrollo como esta sección: no se copian.

## Versión mínima de cliente

Estándar: [*Publishing a Flet app*](../fuentes/flet/publish.md) de Flet.

Contrato: [transversal.md](transversal.md#versión-mínima-de-cliente).

- La versión del `User-Agent` sale de `page.get_package_info()`, sin otra copia en el código ([Publishing, *Reading the version at runtime*](../fuentes/flet/publish.md)).

## WebSocket

Contrato: [transversal.md](transversal.md#websocket) y [autenticacion.md](autenticacion.md#websocket).

- El WebSocket va por httpx-ws, con `aconnect_ws` sobre el mismo `httpx.AsyncClient` de [Red](#red): lleva sus cabeceras, como el `User-Agent` y `Authorization`.

## Pruebas

Estándar: [*Integration testing*](../fuentes/flet/integration-testing.md) de Flet.

- CI corre las pruebas en Linux con `flet test`, bajo `xvfb-run`, con el Flutter de [Proyecto](#proyecto) y los paquetes que lista `flet --version --json`: `flet test` construye la app de escritorio de las pruebas de integración antes de que arranque pytest, y esa app necesita una pantalla. Construida dentro de pytest, `flet-cli` escribe archivos sin `encoding` y el `error::EncodingWarning` de [python.md](python.md#cumplimiento) detiene la prueba.
- `flet test` corre sin el `LD_LIBRARY_PATH` que deja `setup-python`: con él, el Python que embebe la app no arranca.
- pytest ignora el `EncodingWarning` de `lazy_loader`, que scikit-image importa desde `flet.testing`: es código de terceros, y el aviso detiene la recolección de las pruebas.
- pytest lleva `asyncio_default_fixture_loop_scope = "function"`: sin él, pytest-asyncio avisa en cada corrida.
- El grupo `dev` lleva `flet` con el extra `test` ([Integration testing, *Enabling tests in an existing app*](../fuentes/flet/integration-testing.md)).
- Un control que busca una prueba lleva un `key` estable, y la prueba lo encuentra con `find_by_key()`: un texto cambia con el idioma ([Integration testing, *Writing a test*](../fuentes/flet/integration-testing.md)).
- Después de cada interacción, la prueba llama a `pump_and_settle()` antes de comprobar el resultado ([Integration testing, *Pumping*](../fuentes/flet/integration-testing.md)).

## Entrega

Estándares: [*Publishing a Flet app*](../fuentes/flet/publish.md), [*Packaging app for Android*](../fuentes/flet/publish-android.md), [*Packaging app for Windows*](../fuentes/flet/publish-windows.md), [*Packaging app for Linux*](../fuentes/flet/publish-linux.md), [*Packaging app for iOS*](../fuentes/flet/publish-ios.md) y [*Packaging app for macOS*](../fuentes/flet/publish-macos.md) de Flet.

Contrato: [transversal.md](transversal.md#distribución).

- CI instala el certificado Apple Distribution y el perfil de App Store desde sus secretos, con `scripts/apple.py`, sin otra acción de GitHub.
- El release corre `uv run flet build` después de `uv sync --locked`, sin flet-build-action: la acción corre `uv run` sin `--locked`, y un `uv.lock` desfasado no detiene el build. [flet-build-action v1](https://raw.githubusercontent.com/flet-dev/flet-build-action/v1/action.yml)
- `[tool.flet]` declara `bundle_id`, `<dominio al revés>.<pieza>`: sin él, sale de `org`, que vale `com.flet` si falta ([Publishing, *Bundle ID*](../fuentes/flet/publish.md) y [*Organization name*](../fuentes/flet/publish.md)).
- `[tool.flet]` declara `product`, el nombre que ve el usuario: sin él, es `[project].name` ([Publishing, *Product name*](../fuentes/flet/publish.md)).
- `[tool.flet]` declara `company` antes de la primera versión, y ni `company` ni `product` cambian después: Windows guarda los datos de la app en `%APPDATA%\<company>\<product>`, y sin `company`, en *Your Company* ([Packaging app for Windows, *Distributing*](../fuentes/flet/publish-windows.md)).
- `[tool.flet]` declara `artifact`, el nombre del ejecutable, que nombran `installer.iss` y `build-appimage.sh` ([Packaging app for Windows, *Distributing*](../fuentes/flet/publish-windows.md)).
- `src/assets/icon.png` es un PNG cuadrado de 1024 × 1024 px, con fondo transparente y el dibujo hasta el borde: Flet genera con él los iconos de cada sistema ([Publishing, *Icons*](../fuentes/flet/publish.md)).
- La versión es `[project].version`, y sube en cada versión que se publica ([Publishing, *Build Version*](../fuentes/flet/publish.md)).
- El número de build es `build_number`, de `[tool.flet]` ([Publishing, *Build Number*](../fuentes/flet/publish.md)).
- `flet build` no recibe argumentos de `flutter build` ([Publishing, *Additional `flutter build` Arguments*](../fuentes/flet/publish.md)).
- `pyproject.toml` no agrega ni reemplaza dependencias de Flutter ([Publishing, *Flutter dependencies*](../fuentes/flet/publish.md)).
- `flet build aab` recibe el keystore de subida y sus contraseñas por `FLET_ANDROID_SIGNING_KEY_STORE`, `FLET_ANDROID_SIGNING_KEY_STORE_PASSWORD`, `FLET_ANDROID_SIGNING_KEY_ALIAS` y `FLET_ANDROID_SIGNING_KEY_PASSWORD`, desde los secretos de CI ([Packaging app for Android, *Key store password*](../fuentes/flet/publish-android.md)).
- La versión de Windows es el `setup.exe` que compila Inno Setup desde `installer.iss`, el script de Flet, después de `flet build windows` ([Packaging app for Windows, *Distributing*](../fuentes/flet/publish-windows.md)).
- El `AppId` de `installer.iss` es el `bundle_id`, y no cambia entre versiones: con otro, el instalador registra una app aparte en vez de actualizarla ([Packaging app for Windows, *Distributing*](../fuentes/flet/publish-windows.md)).
- CI compila el instalador con el `iscc` del runner de Windows ([Packaging app for Windows, *Building the installer in CI*](../fuentes/flet/publish-windows.md)).
- La versión de Linux es el AppImage que arma `build-appimage.sh`, el script de Flet, después de `flet build linux` ([Packaging app for Linux, *Distributing*](../fuentes/flet/publish-linux.md)).
- En CI, `build-appimage.sh` corre con `APPIMAGE_EXTRACT_AND_RUN=1`, sin FUSE ([Packaging app for Linux, *Distributing*](../fuentes/flet/publish-linux.md)).
- La versión de Android que va a Google Play es un AAB, de `flet build aab` ([Packaging app for Android, *`flet build aab`*](../fuentes/flet/publish-android.md)).
- El AAB guarda las librerías nativas con el empaquetado moderno, el predeterminado ([Packaging app for Android, *When to use which*](../fuentes/flet/publish-android.md)).
- Un permiso que trae un paquete multiplataforma de `permissions` se declara con él, y no como permiso de Android ([Packaging app for Android, *Permissions*](../fuentes/flet/publish-android.md)).
- La app declara solo los permisos que usa. `READ_MEDIA_*` y `*_EXTERNAL_STORAGE` van solo si necesita acceso a toda la biblioteca, y `*_EXTERNAL_STORAGE`, con `maxSdkVersion = "32"`: `FilePicker` no pide permisos ([Packaging app for Android, *Permissions*](../fuentes/flet/publish-android.md)).
- El keystore de subida no va en git ([Packaging app for Android, *Create an upload keystore*](../fuentes/flet/publish-android.md)).
- El build de Linux instala antes los paquetes que lista `flet --version --json` ([Packaging app for Linux, *Prerequisites*](../fuentes/flet/publish-linux.md)).
- El AppImage lleva el bundle entero, y su `AppRun` solo hace `exec` del ejecutable, sin `LD_LIBRARY_PATH` ([Packaging app for Linux, *Distributing*](../fuentes/flet/publish-linux.md) y [*Do not set `LD_LIBRARY_PATH` in `AppRun`*](../fuentes/flet/publish-linux.md)).
- El `Exec=` del desktop entry se reescribe con el nombre del ejecutable ([Packaging app for Linux, *Distributing*](../fuentes/flet/publish-linux.md)).
- `build-appimage.sh` descarga appimagetool de un release fijo, no del tag `continuous` ([Packaging app for Linux, *Distributing*](../fuentes/flet/publish-linux.md)).
- La versión de iOS es el `.ipa` de `flet build ipa`, con `export_method = "app-store-connect"` en `[tool.flet.ios]`, y CI la sube a App Store Connect con `xcrun altool --upload-package` y una llave de la API de App Store Connect ([Packaging app for iOS, *Export method*](../fuentes/flet/publish-ios.md) y [*Building and signing in CI*](../fuentes/flet/publish-ios.md)).
- `[tool.flet.ios]` declara `team_id`, `signing_certificate = "Apple Distribution"` y, en `provisioning_profile`, el perfil de App Store de la app ([Packaging app for iOS, *Team ID*](../fuentes/flet/publish-ios.md), [*Signing Certificate*](../fuentes/flet/publish-ios.md) y [*Provisioning Profile*](../fuentes/flet/publish-ios.md)).
- La versión de macOS sale de `flet build macos --macos-distribution developer-id`, que firma la app con el runtime endurecido, la notariza y le grapa el ticket ([Packaging app for macOS, *Distribution lanes*](../fuentes/flet/publish-macos.md)).
- La app va en un DMG de `hdiutil create`, que se firma con el mismo certificado, se notariza y lleva grapado el ticket ([Packaging app for macOS, *Distributing*](../fuentes/flet/publish-macos.md)).
- La notarización usa una llave de la API de App Store Connect, por `APPLE_API_KEY`, `APPLE_API_KEY_ID` y `APPLE_API_ISSUER`, y `flet build` encuentra solo el certificado Developer ID, el único del llavero del runner ([Packaging app for macOS, *Creating a credential*](../fuentes/flet/publish-macos.md), [*Providing it to Flet*](../fuentes/flet/publish-macos.md) y [*Identity auto-discovery*](../fuentes/flet/publish-macos.md)).

## Cumplimiento

| Convención | Herramienta |
| :--- | :--- |
| Las versiones de [stack.md](../stack.md), exactas en `[project]` | [scripts/verificar.py](../scripts/verificar.py) |
| `src/api/models.py` al día con `../server/openapi.json` | `uv run datamodel-codegen` y `git diff --exit-code src/api/models.py` en CI |
| El árbol de «Proyecto» en `src/` | [scripts/verificar.py](../scripts/verificar.py), que falla con un archivo o una carpeta que el árbol no tiene |
| HTTP solo en `api/` | ruff `TID251` sobre httpx y httpx-ws, que `src/api/ruff.toml` permite |
