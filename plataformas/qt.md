# Qt

Una aplicación de escritorio con Qt Widgets y PySide6. Se suma a [python.md](python.md).

## Proyecto

```text
desktop/
  .gitignore
  pyproject.toml
  uv.lock
  pysidedeploy.spec
  src/app/
    __init__.py
    main.py             crea la QApplication y abre la ventana principal
    colors.py
    theme.py            el estilo y la paleta
    icon.png
    resources.qrc       el icono, las imágenes de assets/ y las traducciones compiladas
    assets/             lo que no es código: las imágenes y los archivos que se leen del disco
    translations/
      <locale>.ts
    api/                lo que habla HTTP
      __init__.py
      client.py         las llamadas al servidor propio
      models.py         los modelos del cable, generados
      <servicio>.py     un servicio externo: sus llamadas y sus modelos
      ruff.toml         permite QtNetwork
    services/           lo que no es interfaz ni HTTP
      __init__.py
      ruff.toml         prohíbe QtWidgets
      language.py       el idioma de la interfaz
      <módulo>.py
      <dominio>/
        __init__.py
        <módulo>.py
    windows/
      __init__.py
      main_window.py
    dialogs/
      __init__.py
      <clase>.py
    widgets/            los demás widgets y los delegates
      __init__.py
      <clase>.py
    models/
      __init__.py
      <clase>.py
  tests/
    __init__.py
    conftest.py         el fixture screen que mide test_accessibility.py
    test_accessibility.py
    test_theme.py
```

Plantilla: [plantilla/qt/](../plantilla/qt/), el job `desktop` de [plantilla/.github/workflows/ci.yml](../plantilla/.github/workflows/ci.yml) y el job `desktop` de [plantilla/.github/workflows/release.yml](../plantilla/.github/workflows/release.yml). `tests/test_theme.py` y `tests/test_accessibility.py` son canónicos y se copian sin editar, y `tests/conftest.py` es un punto de partida; `theme.py` es un punto de partida para los dos modos, y con uno se le quita la elección del modo. `src/app/api/ruff.toml`, `src/app/services/ruff.toml` y `src/app/services/language.py` se copian sin editar.

## PySide6

- La API de Qt se usa con sus nombres originales, sin `__feature__`.
- Un enum o un flag de Qt se nombra con su clase, como `Qt.AlignmentFlag.AlignLeft`, y un flag vacío es `Qt.AlignmentFlag(0)`: los stubs solo traen esa forma. [PySide6 6.12.0](https://raw.githubusercontent.com/qtproject/pyside-pyside-setup/v6.12.0/sources/pyside6/doc/considerations.rst)
- Todo método que sobrescribe otro lleva `@override`, en lugar de lo que fija [python.md](python.md#tipos): un `closeEvent` mal escrito nunca se llama y nada avisa.
- Todo método conectado a una señal lleva `@Slot`: sin él, cada conexión agrega el método al `QMetaObject` en tiempo de ejecución. [PySide6 6.12.0](https://raw.githubusercontent.com/qtproject/pyside-pyside-setup/v6.12.0/sources/pyside6/doc/tutorials/basictutorial/signals_and_slots.rst)
- Un slot no es privado, con prefijo `__`: obliga a búsquedas en tiempo de ejecución. [PySide6 6.12.0](https://raw.githubusercontent.com/qtproject/pyside-pyside-setup/v6.12.0/sources/pyside6/doc/tutorials/basictutorial/signals_and_slots.rst)
- Las señales con tipos distintos llevan nombres distintos.

## Widgets

Estándar: [QWidget](../fuentes/qt/qwidget.qdoc) de Qt.

- La interfaz se construye en código.
- Un widget formatea las fechas y los números con su `locale()`.
- Un evento se maneja en su handler específico, como `mousePressEvent()`, y no reimplementando `event()` ([QWidget, *event()*](../fuentes/qt/qwidget.qdoc)).
- Un atajo de teclado es un `QAction` o un `QShortcut`, nunca `grabShortcut()` ([QWidget, *grabShortcut*](../fuentes/qt/qwidget.qdoc)).
- Un campo cuyos `inputMethodHints` restringen lo que se escribe lleva también un `QValidator` ([QWidget, *inputMethodHints*](../fuentes/qt/qwidget.qdoc)).

## Diálogos

- Un diálogo modal se abre con `open()`, nunca con `exec()`.
- El cierre de un diálogo cambia en `accept()`, `reject()` o `done()`, y `closeEvent()` se reimplementa solo para guardar su posición o reemplazar el cierre estándar.

## Layouts

Contrato: [transversal.md](transversal.md#accesibilidad).

- Los widgets se ubican con layouts, salvo el que flota encima de otros, como una búsqueda sobre un texto o una lista desplegada bajo un campo: va con `setGeometry()`, y su tamaño sale de su `sizeHint()`, acotado por el lugar que hay. Un layout no lo puede superponer sin quitarle los clics al de abajo.

## Model/View

Estándar: [*Model/View Programming*](../fuentes/qt/model-view-programming.qdoc) de Qt.

Contrato: [transversal.md](transversal.md#paginación).

- Un modelo de una lista paginada pide la página siguiente en `fetchMore()`, y su `canFetchMore()` devuelve si la última respuesta trajo un `nextPageToken`.
- Una lista, una tabla o un árbol de datos usa una vista con un modelo, no `QListWidget`, `QTableWidget` ni `QTreeWidget` ([Model/View Programming, *Convenience classes*](../fuentes/qt/model-view-programming.qdoc)).
- Un delegate propio hereda de `QStyledItemDelegate` ([Model/View Programming, *Delegates*](../fuentes/qt/model-view-programming.qdoc)).
- Un modelo implementa `headerData()` ([Model/View Programming, *Read-Only access*](../fuentes/qt/model-view-programming.qdoc)).

## Hilos

- Un trabajo largo corre en otro hilo, que le entrega su resultado.
- Una señal entre hilos no usa `Qt.ConnectionType.DirectConnection`.

## Accesibilidad

Estándares: [*Accessibility*](../fuentes/qt/accessible.qdoc) y [QWidget](../fuentes/qt/qwidget.qdoc) de Qt.

Contrato: [transversal.md](transversal.md#accesibilidad).

- El `data()` de un modelo responde también `ToolTipRole`, `AccessibleTextRole` y `AccessibleDescriptionRole`.
- La interfaz usa los widgets de Qt donde puede: ya implementan su accesibilidad ([Accessibility, *Implementing Accessibility*](../fuentes/qt/accessible.qdoc)).
- Un widget propio que dibuja su contenido implementa su `QAccessibleInterface` y envía sus eventos de accesibilidad ([Accessibility, *Implementing Accessibility*](../fuentes/qt/accessible.qdoc)).
- Un separador de `QSplitter` es una línea de 1 px que no recibe el puntero ni el foco, y se agarra en una franja transparente de 24 px puesta encima de ella, que recibe el arrastre, Tab y las flechas y solo dibuja el foco: así mide lo que pide [transversal.md](transversal.md#accesibilidad) sin abrir un hueco de 24 px entre los paneles. Lo que queda debajo de la franja le deja ese lugar libre; una barra de desplazamiento, por ejemplo, no va bajo ella.
- Una función de uso frecuente tiene un atajo de teclado ([Accessibility, *Keyboard Navigation*](../fuentes/qt/accessible.qdoc)).
- `accessibleName` es corto, y `accessibleDescription` dice qué hace el widget ([QWidget, *accessibleName*](../fuentes/qt/qwidget.qdoc) y [*accessibleDescription*](../fuentes/qt/qwidget.qdoc)).
- `tests/test_accessibility.py` mide en la ventana principal lo que una herramienta puede medir de [transversal.md](transversal.md#accesibilidad): el contraste del texto y de los glifos, los objetivos de 24 × 24 o con su círculo de 24 libre, que todo lo que responde al ratón reciba el foco de Tab, que Tab salga de cada control, se vea y siga el orden de lectura, que lo que se mueve se detenga, que los cambios de estado se anuncien y que la ventana quepa al 200 % en una pantalla de 1920 × 1080. Lo demás se comprueba a mano.
- `tests/conftest.py` da el fixture `screen`, con lo que solo el repositorio sabe (`Screen`, de `test_accessibility.py`): la ventana abierta con el contenido que se usa, sus bandas en orden de lectura, lo que detiene lo que se mueve y lo que cambia un estado.

## Almacenamiento

Estándar: [QSettings](../fuentes/qt/qsettings.qdoc) de Qt.

- `QSettings` usa `IniFormat`.
- El token de refresco que pide [autenticacion.md](autenticacion.md#sesión) va en keyring.
- `main.py` declara el nombre de la organización y el de la app en la `QApplication` antes de crear un `QSettings` ([QSettings, *Basic Usage*](../fuentes/qt/qsettings.qdoc)).
- Una clave se escribe siempre con las mismas mayúsculas, dos claves no difieren solo en ellas, y ninguna lleva `/` ni `\` ([QSettings, *Section and Key Syntax*](../fuentes/qt/qsettings.qdoc)).
- La ventana principal lee su geometría y su estado al crearse, y los guarda en `closeEvent()` ([QSettings, *Restoring the State of a GUI Application*](../fuentes/qt/qsettings.qdoc)).

## Código de autorización

Contrato: [autenticacion.md](autenticacion.md#código-de-autorización).

- La app hace el flujo con `QOAuth2AuthorizationCodeFlow`, de Qt Network Authorization, que manda el `code_challenge` con `S256`. [Qt 6.12.0](https://raw.githubusercontent.com/qt/qtnetworkauth/v6.12.0/src/oauth/qoauth2authorizationcodeflow_p.h)
- La app recibe el retorno en un `QOAuthHttpServerReplyHandler` creado sin dirección ni puerto: escucha en `127.0.0.1` con un puerto libre, y la URI de retorno lleva esa IP y no `localhost`. Lo cierra con `close()` al recibir el token. [Qt 6.12.0](https://raw.githubusercontent.com/qt/qtnetworkauth/v6.12.0/src/oauth/qoauthhttpserverreplyhandler.cpp)
- `authorizeWithBrowser` va conectado a `QDesktopServices.openUrl`, que abre la petición en el navegador del sistema.

## Contraseñas

Contrato: [autenticacion.md](autenticacion.md#contraseñas).

- El campo de la contraseña es un `QLineEdit` en `EchoMode.Password`, con una acción al final que lo pasa a `EchoMode.Normal` mientras está marcada.

## Errores

Contrato: [transversal.md](transversal.md#errores).

- `api/client.py` lanza una respuesta de error como `ApiError`, con el `Problem` de `api/models.py`, y una sin problem+json, con un `Problem` de tipo `about:blank` y su `status`.

## Idiomas

Contrato: [transversal.md](transversal.md#idiomas).

- El idioma que elige el usuario se guarda en `QSettings`, bajo la clave `language.KEY`, y `main.py` lo aplica con `language.install()` antes de crear un widget: fija `QLocale.setDefault()` e instala el `QTranslator` de la app y el de Qt. Hasta que elige, es el primero de `QLocale.system().uiLanguages()` que tiene traducción, o el base. `Accept-Language` lo toma de `QLocale()`.
- Los textos usan Qt Linguist, y el texto fuente es el del idioma base.
- Un texto se traduce con `QCoreApplication.translate("<contexto>", ...)`, con la clase o el módulo donde está como contexto, y no con `self.tr()`: en PySide6, `tr()` busca con la clase del objeto, y un método heredado no encuentra el texto que `pyside6-lupdate` guardó con la clase donde está escrito.
- Un valor entra en el texto con `.format()` después de traducirlo, nunca en un f-string: el f-string arma el texto antes de buscarlo, y la búsqueda falla.
- Un texto que se arma al importar, antes de instalar el traductor, se marca con `QT_TRANSLATE_NOOP` de `services/language.py` y se traduce donde se muestra. El de PySide6 devuelve `object` en sus stubs.
- Los `.qm` van en `resources.qrc`.
- Los textos se extraen de los `.py` que git no ignora, sin el `rc_resources.py` generado: `pyside6-lupdate $(git ls-files --cached --others --exclude-standard 'src/app/*.py') -ts src/app/translations/<locale>.ts`. En Windows, `pyside6-lupdate` 6.12.0 termina con un fallo de acceso a memoria si lee el `rc_resources.py` de una app con traducciones.
- Los `.qm` y `rc_resources.py` se generan y no van en git.

## OpenAPI y clientes

Contrato: [transversal.md](transversal.md#openapi-y-clientes).

- datamodel-code-generator genera desde `../server/openapi.json` los modelos del cable en `src/app/api/models.py`, con la configuración de `[tool.datamodel-codegen]`: modelos de Pydantic v2, campos en snake_case con su alias en camelCase, que el código llena por su nombre en snake_case, y `extra="forbid"` en cada esquema que declara `additionalProperties: false`.
- `src/app/api/models.py` se versiona, y CI lo vuelve a generar y falla si cambia.
- `src/app/api/models.py` no lleva docstrings propios, y ruff no le exige las reglas `D1`.
- Las llamadas a la API se escriben a mano en `api/client.py`, con el `QNetworkAccessManager` de [Red](#red).

## Red

- HTTP va por `QNetworkAccessManager`, y las respuestas se leen con los modelos de `api/`.
- La app no llama a `ignoreSslErrors()`: un certificado que no vale termina la conexión, como fija [python.md](python.md#seguridad).
- La app tiene un solo `QNetworkAccessManager`.
- El `QNetworkAccessManager` libera cada respuesta al terminar, con `setAutoDeleteReplies(True)`.
- Los reintentos de [transversal.md](transversal.md#reintentos) se escriben a mano en `api/client.py`.

## Tema

Estándar: [QWidget](../fuentes/qt/qwidget.qdoc) de Qt.

Contrato: [transversal.md](transversal.md#tema).

- La app usa Fusion a través de `Style`, el `QProxyStyle` de `theme.py`, y ninguna hoja de estilo: Qt recomienda un `QProxyStyle` para ajustar el estilo en producción, deja las hojas de estilo para prototipos y ajustes locales, y pide no cambiar de tema con ellas. [QProxyStyle, Qt 6.12.0](https://raw.githubusercontent.com/qt/qtbase/v6.12.0/src/widgets/styles/qproxystyle.cpp) y [Qt Style Sheets, Qt 6.12.0](https://raw.githubusercontent.com/qt/qtbase/v6.12.0/src/widgets/doc/src/widgets-and-layouts/stylesheet.qdoc)
- La paleta de la `QApplication` sale de `palette()` con el esquema del modo del `ColorTheme` elegido, generado en `colors.py`, según la elección del usuario, guardada en `QSettings`: `INITIAL` mientras no elija otro tema. Con los dos modos y «sistema», sigue `QStyleHints.colorScheme()` y se vuelve a aplicar con `colorSchemeChanged`.
- `Style` dibuja el marco de los campos, los spin boxes, los combo boxes y los paneles en `Dark`, que es `outline`, y en 2 px de `Highlight` con el foco, y la grilla de las tablas en `Mid`, que es `outlineVariant`: Fusion los saca del color de la ventana oscurecido, y en el modo oscuro no se ven. [Fusion, Qt 6.12.0](https://raw.githubusercontent.com/qt/qtbase/v6.12.0/src/widgets/styles/qfusionstyle_p_p.h)
- Un botón con la propiedad `variant` en `primary` o `danger` toma sus colores en `Style`, y no en una hoja de estilo.
- Los tamaños van en `theme.py`, sin tamaños literales fuera de él.
- Ningún widget cambia su estilo con `setStyle()`: la app usa uno solo ([QWidget, *setStyle*](../fuentes/qt/qwidget.qdoc)).

## Versión mínima de cliente

Contrato: [transversal.md](transversal.md#versión-mínima-de-cliente).

- `main.py` lee la versión de la app con `importlib.metadata.version()` y la pasa a `QApplication.setApplicationVersion()`, y el `User-Agent` la toma de `applicationVersion()`: la versión vive solo en `pyproject.toml`.

## WebSocket

Contrato: [transversal.md](transversal.md#websocket) y [autenticacion.md](autenticacion.md#websocket).

- El WebSocket va por `QWebSocket`, de QtWebSockets.

## Pruebas

- En CI, las pruebas corren con `QT_QPA_PLATFORM=offscreen`, sin pantalla.
- Una prueba registra cada widget con `qtbot.addWidget` y lo maneja con sus propios métodos, como `setText` o `setCurrentIndex`, y no con los clics de `qtbot`.

## Entrega

Estándar: [pyside6-deploy](../fuentes/pyside6/deployment-pyside6-deploy.rst) de PySide6.

- La versión de macOS es el `.app` de `pyside6-deploy` dentro del DMG que pide [transversal.md](transversal.md#distribución), que `scripts/apple.py` firma y notariza junto con la app.
- Las rutas de `pysidedeploy.spec` son relativas a `desktop/`, y la app se empaqueta solo en CI: cada corrida reescribe en el archivo las rutas absolutas de la máquina.
- `icon.png` mide 1024 × 1024 px, el mayor tamaño que usa macOS, y es el único icono, en lugar del `.ico` de Windows y el `.icns` de macOS que pide `pyside6-deploy`: Nuitka lo convierte al formato de cada sistema, y un archivo sirve a todos.
- La ventana principal pone `icon.png` con `setWindowIcon`: en Linux, con el `mode` en `onefile`, Nuitka no lo pone en el binario y avisa que `--linux-app-icon` solo rige con `--mode=app`.
- El job que empaqueta instala las dependencias, compila las traducciones y `resources.qrc`, y al final instala la app: Nuitka compila la copia instalada, y una instalada antes no tiene `rc_resources.py`.
- La carpeta `dist/`, el `exec_directory` del `.spec`, existe antes de ejecutar `pyside6-deploy`: no la crea, y al copiar el binario falla con `FileNotFoundError`.
- Nuitka con el extra `onefile`, imageio y, en Linux, patchelf van en el grupo `deploy`.
- En CI de Windows, el job agrega al `PATH` la carpeta del `dumpbin` de MSVC que encuentra `vswhere`, y falla si no lo encuentra: sin él, `pyside6-deploy` solo avisa y no busca los módulos de Qt de los que dependen los que usa la app. [PySide6 6.12.0](https://raw.githubusercontent.com/qtproject/pyside-pyside-setup/v6.12.0/sources/pyside-tools/deploy_lib/config.py)
- El job que empaqueta instala la app sin modo editable, con `--no-editable` en `uv sync` y en `uv run`: Nuitka busca en el `RECORD` de la distribución el paquete al que pertenecen sus metadatos, y una instalación editable no lo lista. [Nuitka 4.3.5](https://raw.githubusercontent.com/Nuitka/Nuitka/4.3.5/nuitka/utils/Distributions.py)
- El `mode` del `.spec` es `onefile`: cada sistema recibe un solo archivo, que [despliegue.md](despliegue.md#versiones) publica, salvo macOS, donde `pyside6-deploy` siempre arma un `.app` ([pyside6-deploy, *pysidedeploy.spec parameters*](../fuentes/pyside6/deployment-pyside6-deploy.rst)).
- El `extra_args` del `.spec` lleva `--windows-console-mode=disable`: sin eso, Nuitka abre en Windows una consola junto a la ventana, y en Linux y macOS no hace nada. [Nuitka 4.3.5](https://raw.githubusercontent.com/Nuitka/Nuitka/4.3.5/nuitka/options/Options.py)
- `pyside6-deploy` corre con `--no-install`, y el `packages` del `.spec` lista `Nuitka` e `imageio`: comprueba que el grupo `deploy` los trajo, y no instala nada con pip, que un venv de uv no tiene ([pyside6-deploy, *Command Line Options*](../fuentes/pyside6/deployment-pyside6-deploy.rst) y [*What pyside6-deploy runs*](../fuentes/pyside6/deployment-pyside6-deploy.rst)).
- `pysidedeploy.spec` va en git: elige los paquetes y los argumentos de Nuitka ([pyside6-deploy, *What pyside6-deploy runs*](../fuentes/pyside6/deployment-pyside6-deploy.rst)).

## Cumplimiento

| Convención | Herramienta |
| :--- | :--- |
| `@override` | Pyrefly `missing-override-decorator` |
| Los nombres originales de Qt | ruff `TID251` sobre `__feature__` |
| Un enum con su clase | Pyrefly `missing-attribute` |
| La interfaz en código | ruff `TID251` sobre `PySide6.QtUiTools`, y [scripts/verificar.py](../scripts/verificar.py), que falla con un `.ui` en `desktop/` |
| HTTP por `QNetworkAccessManager`: sin httpx, requests, `urllib.request` ni `http.client` | ruff `TID251` sobre httpx, requests, `urllib.request` y `http.client` |
| El árbol de «Proyecto» en `src/` | [scripts/verificar.py](../scripts/verificar.py), que falla con un archivo o una carpeta que el árbol no tiene, y con un módulo de `dialogs/`, `widgets/` o `models/` que no declara una sola clase pública con su nombre |
| HTTP solo en `api/` | ruff `TID251` sobre `PySide6.QtNetwork`, que `src/app/api/ruff.toml` permite |
| `services/` sin interfaz | ruff `TID251` sobre `PySide6.QtWidgets`, que prohíbe `src/app/services/ruff.toml` |
| Los `ruff.toml` de `src/` y `services/language.py`, sin editar | [scripts/verificar.py](../scripts/verificar.py), que los compara con los de la plantilla |
| Fusion, a través del `QProxyStyle` de `theme.py` | `test_style_is_fusion`, de `tests/test_theme.py` |
| Ninguna hoja de estilo | `test_no_style_sheet`, de `tests/test_theme.py` |
| Los colores, solo los de `colors.py`, que genera [transversal.md](transversal.md#tema): fuera de él, ni un color hexadecimal, ni `rgb()`, ni un `QColor` de un literal, ni `QColorConstants`, ni `Qt.GlobalColor` salvo `transparent` | `test_colors_only_generated`, de `tests/test_theme.py` |
| Pruebas sin pantalla | `QT_QPA_PLATFORM=offscreen` en el job de CI |
| Lo que una herramienta mide de «Accesibilidad» de `transversal.md` | `tests/test_accessibility.py`, que [scripts/verificar.py](../scripts/verificar.py) compara con el de la plantilla |
| `src/app/api/models.py` al día con `../server/openapi.json` | `uv run datamodel-codegen` y `git diff --exit-code src/app/api/models.py` en CI |
