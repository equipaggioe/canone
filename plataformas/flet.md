# Flet

> **En desarrollo; no se implementa:** [README.md](README.md#en-desarrollo).

Una aplicación en Flet. Se suma a [python.md](python.md).

## Proyecto

Estándar: [*Publishing a Flet app*](../fuentes/flet/publish.md) de Flet.

- Flet 1.1.2, flet-secure-storage 1.1.2, httpx-ws 0.9.0, la de [fastapi.md](fastapi.md), y datamodel-code-generator 0.95.0, con el extra `ruff`.
- Flutter 3.47.9, el de [flutter.md](flutter.md) y el que pide Flet 1.1.2: `flet build` usa el del `PATH` si tiene la misma versión mayor y menor, y si no, instala ese. [Flet 1.1.2](https://raw.githubusercontent.com/flet-dev/flet/v1.1.2/sdk/python/packages/flet-cli/src/flet_cli/commands/flutter_base.py)
- Pydantic es la 2.13.4, y no la de [python.md](python.md): `flet build apk` instala desde el índice de Flet para Android, que tiene `pydantic-core` 2.46.4 y 2.47.0, y la 2.13.4 es la última Pydantic que pide una de ellas. [Índice de Flet](https://pypi.flet.dev/pydantic-core/)
- Las dependencias de `[project]` van exactas, con `==`, en lugar del `>=` de [python.md](python.md): `flet build` no lee `uv.lock` y le pasa a pip las dependencias tal como están escritas. [Flet 1.1.2](https://raw.githubusercontent.com/flet-dev/flet/v1.1.2/sdk/python/packages/flet-cli/src/flet_cli/commands/build_base.py)
- El grupo `dev` lleva también `flet`, con el extra `cli`, que trae `flet build`, y el extra `test` de [Pruebas](#pruebas). [Flet 1.1.2](https://raw.githubusercontent.com/flet-dev/flet/v1.1.2/website/docs/getting-started/installation.md)
- El proyecto no lleva `[build-system]`, en lugar del `uv_build` de [python.md](python.md): sin `src/app/`, no hay paquete que construir.
- `[project].dependencies` declara `flet` y cada extensión de Flet que usa la app, como `flet-secure-storage` ([Publishing, *App dependencies*](../fuentes/flet/publish.md)).
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
    api/                el cliente de la API
      __init__.py
      models.py         los modelos del cable, generados
    views/              una vista por ruta
      __init__.py
      <ruta>.py
  tests/
    __init__.py
    test_theme.py
    test_<módulo>.py
```

Plantilla: [plantilla/flet/](../plantilla/flet/), el job `flet` de [plantilla/.github/workflows/ci.yml](../plantilla/.github/workflows/ci.yml) y los jobs `flet-mobile` y `flet-desktop` de [plantilla/.github/workflows/release.yml](../plantilla/.github/workflows/release.yml). `tests/test_theme.py` es canónico y se copia sin editar; `theme.py`, `installer.iss` y `build-appimage.sh` son un punto de partida.

## Async

Estándar: [*Async apps*](../fuentes/flet/async-apps.md) de Flet.

- Un control que lanza una tarea en `did_mount()` la cancela en `will_unmount()` ([Async apps, *Background tasks*](../fuentes/flet/async-apps.md)).
- Ningún handler bloquea, sea síncrono o async: los dos corren en el único bucle de eventos de la app, y mientras uno corre no se despacha otro evento ni se actualiza la pantalla ([Async apps, *Never block the event loop*](../fuentes/flet/async-apps.md) y [*Control event handlers*](../fuentes/flet/async-apps.md)).
- Un handler que espera algo es `async def` ([Async apps, *Control event handlers*](../fuentes/flet/async-apps.md)).
- Una tarea que sigue después del handler que la lanza se crea con `page.run_task()`, que recibe la función y sus argumentos, guarda la referencia de la tarea y reporta sus excepciones ([Async apps, *Async lambdas*](../fuentes/flet/async-apps.md) y [*Background tasks*](../fuentes/flet/async-apps.md)).
- Una tarea lanzada con `page.run_task()` llama a `update()` después de cambiar la interfaz: la actualización automática del handler ya ocurrió ([Async apps, *Async lambdas*](../fuentes/flet/async-apps.md)).
- Un handler que muestra su avance es un generador que hace `yield` entre partes cortas ([Async apps, *Yielding for intermediate updates*](../fuentes/flet/async-apps.md)).
- Una llamada que bloquea corre con `await asyncio.to_thread()` o, si no hace falta su resultado, con `page.run_thread()` ([Async apps, *Threading*](../fuentes/flet/async-apps.md)).

## Controles

Estándares: [*Custom Controls*](../fuentes/flet/custom-controls.md) y [*Large Lists*](../fuentes/flet/large-lists.md) de Flet.

- Un control propio se declara con `@ft.control` ([Custom Controls, *Styled controls*](../fuentes/flet/custom-controls.md)).
- Un control propio que llama a `self.update()` en sus métodos es aislado: su `is_isolated` devuelve `True` ([Custom Controls, *Isolated controls*](../fuentes/flet/custom-controls.md)).
- Un `ListView` cuyos elementos miden lo mismo lleva `item_extent` o `first_item_prototype` ([Large Lists, *ListView*](../fuentes/flet/large-lists.md)).
- Cada campo de un control propio lleva su anotación de tipo: sin ella no es un campo, y no reemplaza la propiedad heredada ([Custom Controls, *Styled controls*](../fuentes/flet/custom-controls.md)).
- Un campo de tipo simple lleva un valor literal por defecto, y uno que es una lista, un diccionario o un objeto, `field(default_factory=...)` ([Custom Controls, *Styled controls*](../fuentes/flet/custom-controls.md)).
- La lógica que necesita `self.page` va en `build()`, no en el constructor ([Custom Controls, *`build()`*](../fuentes/flet/custom-controls.md)).
- La limpieza de un control va en `will_unmount()` ([Custom Controls, *`will_unmount()`*](../fuentes/flet/custom-controls.md)).
- `before_update()` no llama a `update()` ([Custom Controls, *`before_update()`*](../fuentes/flet/custom-controls.md)).
- Una lista de cientos de elementos usa `ListView` o `GridView`, que dibujan solo lo visible, y no `Column` ni `Row`, que dibujan todo ([Large Lists, *Large Lists*](../fuentes/flet/large-lists.md)).
- Un `ListView` tiene un alto, propio o con `expand` ([Large Lists, *ListView*](../fuentes/flet/large-lists.md)).

## Navegación

Estándar: [*Navigation and Routing*](../fuentes/flet/navigation-and-routing.md) de Flet.

- Toda ruta empieza con `/` ([Navigation and Routing, *Route basics*](../fuentes/flet/navigation-and-routing.md)).
- `page.views` se arma desde `page.route`, la única fuente de verdad, y siempre tiene la vista de `/` ([Navigation and Routing, *Routing model in Flet*](../fuentes/flet/navigation-and-routing.md) y [*Practical recommendations*](../fuentes/flet/navigation-and-routing.md)).
- Solo `page.on_route_change` cambia `page.views`: vacía la pila, agrega la vista de `/` y después las de la ruta ([Navigation and Routing, *Building views from route*](../fuentes/flet/navigation-and-routing.md) y [*Practical recommendations*](../fuentes/flet/navigation-and-routing.md)).
- `page.on_view_pop` maneja la vuelta atrás y navega a la vista que queda arriba ([Navigation and Routing, *Building views from route*](../fuentes/flet/navigation-and-routing.md)).
- Se navega con `page.navigate()` desde un callback síncrono, y con `await page.push_route()` desde uno async ([Navigation and Routing, *Programmatic navigation*](../fuentes/flet/navigation-and-routing.md)).
- Un parámetro opcional de la query se lee con `page.query.to_dict.get()`: `page.query.get()` lanza `KeyError` si falta ([Navigation and Routing, *Query strings*](../fuentes/flet/navigation-and-routing.md)).
- Una vista que pide confirmar la vuelta atrás, como una con cambios sin guardar, lleva `can_pop` en `False` y confirma en `on_confirm_pop` ([Navigation and Routing, *Back navigation and pop confirmation*](../fuentes/flet/navigation-and-routing.md)).
- Un flujo de varios pasos que termina vuelve a su destino con `page.pop_views_until()`, y el resultado le llega por `page.on_views_pop_until` ([Navigation and Routing, *Pop multiple views with a result*](../fuentes/flet/navigation-and-routing.md)).
- Una ruta con parámetros se lee con `TemplateRoute`, no partiendo la cadena ([Navigation and Routing, *Route templates (parameterized routes)*](../fuentes/flet/navigation-and-routing.md) y [*Practical recommendations*](../fuentes/flet/navigation-and-routing.md)).
- Cada ruta nueva se prueba con el botón Atrás de la app ([Navigation and Routing, *Practical recommendations*](../fuentes/flet/navigation-and-routing.md)).

## Ciclo de vida

Estándar: [*Publishing a Flet app*](../fuentes/flet/publish.md) de Flet.

- Lo que no puede perderse se guarda antes de salir, sin depender de la limpieza al terminar: una app construida termina en el acto, sin correr los `atexit`, los finalizadores ni las escrituras pendientes ([Publishing, *How a built app terminates*](../fuentes/flet/publish.md)).
- Una app de escritorio que guarda algo al cerrar la ventana lleva `page.window.prevent_close`, y su handler del evento `CLOSE` guarda y después llama a `page.window.destroy()` ([Publishing, *How a built app terminates*](../fuentes/flet/publish.md)).
- El handler del cierre es corto: retiene la salida de la app ([Publishing, *How a built app terminates*](../fuentes/flet/publish.md)).

## Accesibilidad

Estándar: [*Accessibility*](../fuentes/flet/accessibility.md) de Flet.

Contrato: [transversal.md](transversal.md#accesibilidad).

- Un `Text` cuyo texto no sirve como nombre lleva `semantics_label` ([Accessibility, *Text*](../fuentes/flet/accessibility.md)).
- Un `IconButton`, un `FloatingActionButton` y un `PopupMenuButton` llevan `tooltip`, que es su nombre para el lector de pantalla ([Accessibility, *Buttons*](../fuentes/flet/accessibility.md)).
- Un `TextField` y un `Dropdown` llevan `label` ([Accessibility, *`TextField` and `Dropdown`*](../fuentes/flet/accessibility.md)).
- Un control que no tiene por otra vía su nombre, su rol o su estado va dentro de un `Semantics` ([Accessibility, *Custom semantics*](../fuentes/flet/accessibility.md)).

## Almacenamiento

Estándares: [*Client Storage*](../fuentes/flet/client-storage.md) y [*Packaging app for Windows*](../fuentes/flet/publish-windows.md) de Flet.

- Lo sensible, como el token de refresco que pide [autenticacion.md](autenticacion.md#sesión), va en `SecureStorage`, de flet-secure-storage, que usa el almacén de credenciales del sistema: cifrarlo a mano obliga a guardar la clave en algún lado. [Flet 1.1.2](https://raw.githubusercontent.com/flet-dev/flet/v1.1.2/website/docs/services/securestorage/index.md)
- Cada clave de `SharedPreferences` empieza con `<producto>.<pieza>.` ([Client Storage, *Client Storage*](../fuentes/flet/client-storage.md)).
- La app no llama a `clear()` de `SharedPreferences`: borra las preferencias de todas las apps de Flet del usuario ([Client Storage, *Client Storage*](../fuentes/flet/client-storage.md)).
- `SharedPreferences` guarda solo preferencias, y ningún dato de la app que no pueda perderse ([Client Storage, *Client Storage*](../fuentes/flet/client-storage.md)).
- Un servicio, como `SharedPreferences` o `SecureStorage`, se crea una vez, y la app guarda su referencia mientras lo usa: Flet lo da de baja cuando no queda ninguna ([Client Storage, *Client Storage*](../fuentes/flet/client-storage.md)).
- La app guarda sus archivos en `FLET_APP_STORAGE_DATA`, nunca junto a `__file__`: la carpeta donde se instala la app puede no admitir escritura ([Packaging app for Windows, *Distributing*](../fuentes/flet/publish-windows.md)).

## Autenticación

Contrato: [autenticacion.md](autenticacion.md#código-de-autorización).

## Código por SMS

Contrato: [autenticacion.md](autenticacion.md#código-por-sms).

## Contraseñas

Contrato: [autenticacion.md](autenticacion.md#contraseñas).

## Cuentas

Contrato: [autenticacion.md](autenticacion.md#cuentas).

## Errores

Contrato: [transversal.md](transversal.md#errores).

## Fechas

Contrato: [transversal.md](transversal.md#fechas).

## Idiomas

Contrato: [transversal.md](transversal.md#idiomas).

- Los textos usan `gettext` de la biblioteca estándar de Python, con catálogos `.po`. Flet no trae un sistema de traducción.
- `page.locale_configuration` declara en `supported_locales` los idiomas de la app, con el base primero, y en `current_locale`, el que eligió el usuario: sin ella, los controles de Flutter quedan en `en-US`, y un idioma que no está en la lista cae en el primero. [Flet 1.1.2](https://raw.githubusercontent.com/flet-dev/flet/v1.1.2/sdk/python/packages/flet/src/flet/controls/types.py)

## Mapas

Contrato: [transversal.md](transversal.md#mapas).

## Montos

Contrato: [transversal.md](transversal.md#montos).

## OpenAPI y clientes

Contrato: [transversal.md](transversal.md#openapi-y-clientes).

- datamodel-code-generator genera desde `../server/openapi.json` los modelos del cable en `src/api/models.py`, con la configuración de `[tool.datamodel-codegen]`: modelos de Pydantic v2, campos en snake_case con su alias en camelCase y `extra="forbid"` en cada esquema que declara `additionalProperties: false`. Un modelo generado rechaza un campo y un valor de enum que no conoce.
- `src/api/models.py` se versiona, y CI lo vuelve a generar y falla si cambia: `flet build` empaqueta `src/` tal como está.
- `src/api/models.py` no lleva docstrings propios: los suyos son las descripciones de los esquemas del servidor, y ruff no le exige las reglas `D1`.
- Las llamadas a la API se escriben a mano en `api/`, con el `httpx.AsyncClient` de [Red](#red): datamodel-code-generator genera solo los modelos.

## Paginación

Contrato: [transversal.md](transversal.md#paginación).

## Pagos

Contrato: [transversal.md](transversal.md#pagos).

## Recuperación

Contrato: [autenticacion.md](autenticacion.md#recuperación).

## Red

- HTTP va por un solo `httpx.AsyncClient`, con `await` desde handlers async, y las respuestas se leen con los modelos de `api/models.py`: no bloquea el bucle de eventos y reutiliza las conexiones.

## Reintentos

Contrato: [transversal.md](transversal.md#reintentos).

## Sesión

Contrato: [autenticacion.md](autenticacion.md#sesión).

## Tema

> **En desarrollo; no se implementa:** [transversal.md](transversal.md#tema).

Contrato: [transversal.md](transversal.md#tema).

- `page.theme` y `page.dark_theme` se arman en `theme.py` con `LIGHT` y `DARK`, generados en `colors.py`, y `page.theme_mode` es `ThemeMode.SYSTEM`.
- Los tamaños van en `theme.py`, sin tamaños literales fuera de él.

## Versión mínima de cliente

Estándar: [*Publishing a Flet app*](../fuentes/flet/publish.md) de Flet.

Contrato: [transversal.md](transversal.md#versión-mínima-de-cliente).

- La versión del `User-Agent` sale de `page.get_package_info()`, sin otra copia en el código ([Publishing, *Reading the version at runtime*](../fuentes/flet/publish.md)).

## WebSocket

Contrato: [transversal.md](transversal.md#websocket) y [autenticacion.md](autenticacion.md#websocket).

- El WebSocket va por httpx-ws, con `aconnect_ws` sobre el mismo `httpx.AsyncClient` de [Red](#red): lleva sus cabeceras, como el `User-Agent` y `Authorization`.

## Pruebas

Estándar: [*Integration testing*](../fuentes/flet/integration-testing.md) de Flet.

- CI corre las pruebas en Linux con `xvfb-run uv run pytest`, con el Flutter de [Proyecto](#proyecto) y los paquetes que lista `flet --version --json`: el plugin de Flet construye la app de escritorio de las pruebas de integración, que necesita una pantalla.
- pytest lleva `asyncio_default_fixture_loop_scope = "function"`: sin él, pytest-asyncio avisa en cada corrida.
- El grupo `dev` lleva `flet` con el extra `test` ([Integration testing, *Enabling tests in an existing app*](../fuentes/flet/integration-testing.md)).
- pytest lleva `asyncio_mode = "auto"` ([Integration testing, *Enabling tests in an existing app*](../fuentes/flet/integration-testing.md)).
- Una prueba de integración es async y recibe el fixture `flet_app`, que arranca una app nueva para cada prueba ([Integration testing, *Writing a test*](../fuentes/flet/integration-testing.md)).
- Un control que busca una prueba lleva un `key` estable, y la prueba lo encuentra con `find_by_key()`: un texto cambia con el idioma ([Integration testing, *Writing a test*](../fuentes/flet/integration-testing.md)).
- Después de cada interacción, la prueba llama a `pump_and_settle()` antes de comprobar el resultado ([Integration testing, *Pumping*](../fuentes/flet/integration-testing.md)).

## Entrega

Estándares: [*Publishing a Flet app*](../fuentes/flet/publish.md), [*Packaging app for Android*](../fuentes/flet/publish-android.md), [*Packaging app for Windows*](../fuentes/flet/publish-windows.md) y [*Packaging app for Linux*](../fuentes/flet/publish-linux.md) de Flet.

Contrato: [transversal.md](transversal.md#distribución).

- `[tool.flet]` declara `bundle_id`, `<dominio al revés>.<pieza>`: sin él, sale de `org`, que vale `com.flet` si falta ([Publishing, *Bundle ID*](../fuentes/flet/publish.md) y [*Organization name*](../fuentes/flet/publish.md)).
- `[tool.flet]` declara `product`, el nombre que ve el usuario: sin él, es `[project].name` ([Publishing, *Product name*](../fuentes/flet/publish.md)).
- `src/assets/icon.png` es un PNG cuadrado de 1024 × 1024 px, con fondo transparente y el dibujo hasta el borde: Flet genera con él los iconos de cada sistema ([Publishing, *Icons*](../fuentes/flet/publish.md)).
- Cada versión que se publica lleva como número de build el `github.run_number` de su release, mayor que el de la anterior ([Publishing, *Build Number*](../fuentes/flet/publish.md)).
- `flet build` no recibe argumentos de `flutter build` ([Publishing, *Additional `flutter build` Arguments*](../fuentes/flet/publish.md)).
- `pyproject.toml` no agrega ni reemplaza dependencias de Flutter ([Publishing, *Flutter dependencies*](../fuentes/flet/publish.md)).
- La versión de Android que va a Google Play es un AAB, de `flet build aab` ([Packaging app for Android, *`flet build aab`*](../fuentes/flet/publish-android.md)).
- `flet build aab` recibe el keystore de subida y sus contraseñas por `FLET_ANDROID_SIGNING_KEY_STORE`, `FLET_ANDROID_SIGNING_KEY_STORE_PASSWORD`, `FLET_ANDROID_SIGNING_KEY_ALIAS` y `FLET_ANDROID_SIGNING_KEY_PASSWORD`, desde los secretos de CI ([Packaging app for Android, *Key store password*](../fuentes/flet/publish-android.md)).
- Un permiso que trae un paquete multiplataforma de `permissions` se declara con él, y no como permiso de Android ([Packaging app for Android, *Permissions*](../fuentes/flet/publish-android.md)).
- La versión de Windows es el `setup.exe` que compila Inno Setup desde `installer.iss`, el script de Flet, después de `flet build windows` ([Packaging app for Windows, *Distributing*](../fuentes/flet/publish-windows.md)).
- La versión de Linux es el AppImage que arma `build-appimage.sh`, el script de Flet, después de `flet build linux` ([Packaging app for Linux, *Distributing*](../fuentes/flet/publish-linux.md)).
- En CI, `build-appimage.sh` corre con `APPIMAGE_EXTRACT_AND_RUN=1`, sin FUSE ([Packaging app for Linux, *Distributing*](../fuentes/flet/publish-linux.md)).
- La versión es `[project].version`, en `x.y.z`, y sube en cada versión que se publica ([Publishing, *Build Version*](../fuentes/flet/publish.md)).
- El AAB guarda las librerías nativas con el empaquetado moderno, el predeterminado ([Packaging app for Android, *When to use which*](../fuentes/flet/publish-android.md)).
- La app declara solo los permisos que usa. `READ_MEDIA_*` y `*_EXTERNAL_STORAGE` van solo si necesita acceso a toda la biblioteca, y `*_EXTERNAL_STORAGE`, con `maxSdkVersion = "32"`: `FilePicker` no pide permisos ([Packaging app for Android, *Permissions*](../fuentes/flet/publish-android.md)).
- El keystore de subida no va en git ([Packaging app for Android, *Create an upload keystore*](../fuentes/flet/publish-android.md)).
- `[tool.flet]` declara `company` antes de la primera versión, y ni `company` ni `product` cambian después: Windows guarda los datos de la app en `%APPDATA%\<company>\<product>`, y sin `company`, en *Your Company* ([Packaging app for Windows, *Distributing*](../fuentes/flet/publish-windows.md)).
- `[tool.flet]` declara `artifact`, el nombre del ejecutable, que nombran `installer.iss` y `build-appimage.sh` ([Packaging app for Windows, *Distributing*](../fuentes/flet/publish-windows.md)).
- El `AppId` de `installer.iss` es el `bundle_id`, y no cambia entre versiones: con otro, el instalador registra una app aparte en vez de actualizarla ([Packaging app for Windows, *Distributing*](../fuentes/flet/publish-windows.md)).
- CI compila el instalador con el `iscc` del runner de Windows ([Packaging app for Windows, *Building the installer in CI*](../fuentes/flet/publish-windows.md)).
- El build de Linux instala antes los paquetes que lista `flet --version --json` ([Packaging app for Linux, *Prerequisites*](../fuentes/flet/publish-linux.md)).
- El AppImage lleva el bundle entero, y su `AppRun` solo hace `exec` del ejecutable, sin `LD_LIBRARY_PATH` ([Packaging app for Linux, *Distributing*](../fuentes/flet/publish-linux.md) y [*Do not set `LD_LIBRARY_PATH` in `AppRun`*](../fuentes/flet/publish-linux.md)).
- El `Exec=` del desktop entry se reescribe con el nombre del ejecutable ([Packaging app for Linux, *Distributing*](../fuentes/flet/publish-linux.md)).
- `build-appimage.sh` descarga appimagetool de un release fijo, no del tag `continuous` ([Packaging app for Linux, *Distributing*](../fuentes/flet/publish-linux.md)).

## Cumplimiento

| Convención | Herramienta |
| :--- | :--- |
| Las versiones de «Proyecto» y de [python.md](python.md), exactas en `[project]` | [scripts/verificar.py](../scripts/verificar.py) |
| `src/api/models.py` al día con `../server/openapi.json` | `uv run datamodel-codegen` y `git diff --exit-code src/api/models.py` en CI |
