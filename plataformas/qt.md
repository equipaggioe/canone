# Qt

> **En desarrollo; no se implementa:** [README.md](README.md#en-desarrollo).

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
    theme.py            la paleta y la hoja de estilo global
    icon.png
    resources.qrc       el icono y las traducciones compiladas
    translations/
      <locale>.ts
    api/
      __init__.py
      client.py         el cliente de la API
      models.py         los modelos del cable, generados
    windows/            las ventanas
      __init__.py
      main_window.py
    dialogs/            los QDialog
      __init__.py
      <clase>.py
    widgets/            los demás widgets y los delegates
      __init__.py
      <clase>.py
    models/             los QAbstractItemModel
      __init__.py
      <clase>.py
  tests/
    __init__.py
    test_theme.py
```

Plantilla: [plantilla/qt/](../plantilla/qt/), el job `desktop` de [plantilla/.github/workflows/ci.yml](../plantilla/.github/workflows/ci.yml) y el job `desktop` de [plantilla/.github/workflows/release.yml](../plantilla/.github/workflows/release.yml). `tests/test_theme.py` es canónico y se copia sin editar; `theme.py` es un punto de partida.

## PySide6

- La API de Qt se usa con sus nombres originales, sin `__feature__`: los stubs de PySide6 y la documentación de Qt usan esos nombres.
- Un enum o un flag de Qt se nombra con su clase, como `Qt.AlignmentFlag.AlignLeft`, y un flag vacío es `Qt.AlignmentFlag(0)`: los stubs solo traen esa forma. [PySide6 6.12.0](https://raw.githubusercontent.com/qtproject/pyside-pyside-setup/v6.12.0/sources/pyside6/doc/considerations.rst)
- Todo método que sobrescribe otro lleva `@override`, en lugar de lo que fija [python.md](python.md#tipos): un `closeEvent` mal escrito nunca se llama y nada avisa.
- Todo método conectado a una señal lleva `@Slot`: sin él, cada conexión agrega el método al `QMetaObject` en tiempo de ejecución. [PySide6 6.12.0](https://raw.githubusercontent.com/qtproject/pyside-pyside-setup/v6.12.0/sources/pyside6/doc/tutorials/basictutorial/signals_and_slots.rst)
- Un slot no es privado, con prefijo `__`: obliga a búsquedas en tiempo de ejecución. [PySide6 6.12.0](https://raw.githubusercontent.com/qtproject/pyside-pyside-setup/v6.12.0/sources/pyside6/doc/tutorials/basictutorial/signals_and_slots.rst)
- Las señales con tipos distintos llevan nombres distintos. [PySide6 6.12.0](https://raw.githubusercontent.com/qtproject/pyside-pyside-setup/v6.12.0/sources/pyside6/doc/tutorials/basictutorial/signals_and_slots.rst)

## Widgets

Estándar: [QWidget](../fuentes/qt/qwidget.qdoc) de Qt.

- La interfaz se construye en código: Pyrefly revisa los widgets, y los diffs se leen.
- Un evento se maneja en su handler específico, como `mousePressEvent()`, y no reimplementando `event()` ([QWidget, *event()*](../fuentes/qt/qwidget.qdoc)).
- Un atajo de teclado es un `QAction` o un `QShortcut`, nunca `grabShortcut()` ([QWidget, *grabShortcut*](../fuentes/qt/qwidget.qdoc)).
- `paintEvent()` no llama a `update()` ni a `repaint()` ([QWidget, *paintEvent*](../fuentes/qt/qwidget.qdoc)).
- Un handler de teclado que no actúa sobre la tecla llama a la implementación de la clase base, y uno de rueda que no maneja el evento lo ignora: así lo recibe el padre ([QWidget, *keyPressEvent*](../fuentes/qt/qwidget.qdoc) y [*wheelEvent*](../fuentes/qt/qwidget.qdoc)).
- Un campo cuyos `inputMethodHints` restringen lo que se escribe lleva también un `QValidator` ([QWidget, *inputMethodHints*](../fuentes/qt/qwidget.qdoc)).
- Un widget formatea las fechas y los números con su `locale()` ([QWidget, *locale*](../fuentes/qt/qwidget.qdoc)).

## Diálogos

Estándar: [QDialog](../fuentes/qt/qdialog.qdoc) de Qt.

- Un diálogo modal se abre con `open()`, nunca con `exec()`, que abre un bucle de eventos anidado ([QDialog, *Modal Dialogs*](../fuentes/qt/qdialog.qdoc)).
- Un diálogo abierto con `open()` o `show()` tiene un padre o una referencia que lo mantiene vivo mientras está abierto ([QDialog, *Modal Dialogs*](../fuentes/qt/qdialog.qdoc)).
- El resultado de un diálogo se lee en `finished()`, o en `accepted()` y `rejected()` ([QDialog, *Modal Dialogs*](../fuentes/qt/qdialog.qdoc)).
- El botón por defecto, como Aceptar, se conecta a `accept()`, y Cancelar, a `reject()` ([QDialog, *Modal Dialogs*](../fuentes/qt/qdialog.qdoc)).
- El cierre de un diálogo cambia en `accept()`, `reject()` o `done()`, y `closeEvent()` se reimplementa solo para guardar su posición o reemplazar el cierre estándar ([QDialog, *Return Value (Modal Dialogs)*](../fuentes/qt/qdialog.qdoc)).

## Layouts

Estándar: [*Layout Management*](../fuentes/qt/layout.qdoc) de Qt.

- Los widgets se ubican con layouts, que los reacomodan cuando cambian el tamaño, la letra o el texto: el texto tiene que crecer al 200 % sin perder contenido, como fija [transversal.md](transversal.md#accesibilidad).
- Un widget que va en un layout se crea sin padre: el layout se lo asigna ([Layout Management, *Tips for Using Layouts*](../fuentes/qt/layout.qdoc)).
- Un widget propio sin hijos en un layout declara su `sizeHint()`, su `minimumSizeHint()` y su `sizePolicy()` ([Layout Management, *Custom Widgets in Layouts*](../fuentes/qt/layout.qdoc)).
- El layout de un widget se asigna antes de pasarlo a `QScrollArea.setWidget()` o a `QDockWidget.setWidget()` ([Layout Management, *Layout Issues*](../fuentes/qt/layout.qdoc)).

## Model/View

Estándar: [*Model/View Programming*](../fuentes/qt/model-view-programming.qdoc) de Qt.

- Un modelo de una lista paginada pide la página siguiente en `fetchMore()`, y su `canFetchMore()` devuelve si la última respuesta trajo un `nextPageToken`, como fija [transversal.md](transversal.md#paginación).
- Una lista, una tabla o un árbol de datos usa una vista con un modelo, no `QListWidget`, `QTableWidget` ni `QTreeWidget` ([Model/View Programming, *Convenience classes*](../fuentes/qt/model-view-programming.qdoc)).
- Un delegate propio hereda de `QStyledItemDelegate` ([Model/View Programming, *Delegates*](../fuentes/qt/model-view-programming.qdoc)).
- `data()` responde también `ToolTipRole`, `AccessibleTextRole` y `AccessibleDescriptionRole` ([Model/View Programming, *Read-Only access*](../fuentes/qt/model-view-programming.qdoc)).
- Un `QModelIndex` no se guarda: una referencia duradera es un `QPersistentModelIndex` ([Model/View Programming, *Model indexes*](../fuentes/qt/model-view-programming.qdoc)).
- Un modelo implementa `flags()`, `data()`, `headerData()` y `rowCount()`, y uno que hereda de `QAbstractTableModel` o de `QAbstractItemModel`, también `columnCount()` ([Model/View Programming, *Read-Only access*](../fuentes/qt/model-view-programming.qdoc)).
- Un modelo editable incluye `ItemIsEditable` en `flags()`, acepta `EditRole` en `setData()` y emite `dataChanged()` después de cambiar un dato ([Model/View Programming, *Editable items*](../fuentes/qt/model-view-programming.qdoc)).
- Un modelo que agrega o quita filas llama a `beginInsertRows()` o a `beginRemoveRows()` antes de cambiar sus datos, y al `end` que le corresponde justo después ([Model/View Programming, *Resizable models*](../fuentes/qt/model-view-programming.qdoc)).
- Un cambio de estructura que no es agregar ni quitar filas, como ordenar, emite `layoutAboutToBeChanged()`, actualiza los índices persistentes con `changePersistentIndexList()` y emite `layoutChanged()` ([Model/View Programming, *Resizable models*](../fuentes/qt/model-view-programming.qdoc)).
- `fetchMore()` agrega sus filas entre `beginInsertRows()` y `endInsertRows()` ([Model/View Programming, *Performance optimization for large amounts of data*](../fuentes/qt/model-view-programming.qdoc)).

## Hilos

Estándar: [*Threading Classes*](../fuentes/qt/threads.qdoc) de Qt.

- Los widgets se usan solo desde el hilo principal, y un trabajo largo corre en otro hilo, que le entrega su resultado ([Threading Classes, *QObject Reentrancy*](../fuentes/qt/threads.qdoc)).
- La `QApplication` es el primer `QObject` que se crea y el último que se destruye, y ningún `QObject` vive en una variable de módulo ([Threading Classes, *QObject Reentrancy*](../fuentes/qt/threads.qdoc)).
- El hijo de un `QObject` se crea en el hilo de su padre, y un `QThread` nunca es el padre de lo que se crea en su hilo ([Threading Classes, *QObject Reentrancy*](../fuentes/qt/threads.qdoc)).
- Un temporizador o un objeto de red se usa solo en el hilo al que pertenece ([Threading Classes, *QObject Reentrancy*](../fuentes/qt/threads.qdoc)).
- Lo que se crea en un hilo se borra antes que su `QThread` ([Threading Classes, *QObject Reentrancy*](../fuentes/qt/threads.qdoc)).
- Una señal entre hilos no usa `Qt.ConnectionType.DirectConnection`: el slot correría en el hilo que emite ([Threading Classes, *Signals and Slots Across Threads*](../fuentes/qt/threads.qdoc)).

## Accesibilidad

Estándares: [*Accessibility*](../fuentes/qt/accessible.qdoc) y [QWidget](../fuentes/qt/qwidget.qdoc) de Qt.

Contrato: [transversal.md](transversal.md#accesibilidad).

- La interfaz usa los widgets de Qt donde puede: ya implementan su accesibilidad ([Accessibility, *Implementing Accessibility*](../fuentes/qt/accessible.qdoc)).
- Un widget propio que dibuja su contenido implementa su `QAccessibleInterface` y envía sus eventos de accesibilidad ([Accessibility, *Implementing Accessibility*](../fuentes/qt/accessible.qdoc)).
- Una función de uso frecuente tiene un atajo de teclado ([Accessibility, *Keyboard Navigation*](../fuentes/qt/accessible.qdoc)).
- `accessibleName` es corto y dice lo mismo que lo que se ve, y `accessibleDescription` dice qué hace el widget ([QWidget, *accessibleName*](../fuentes/qt/qwidget.qdoc) y [*accessibleDescription*](../fuentes/qt/qwidget.qdoc)).

## Almacenamiento

Estándar: [QSettings](../fuentes/qt/qsettings.qdoc) de Qt.

- `QSettings` usa `IniFormat`: el mismo archivo legible en todos los sistemas.
- El token de refresco que pide [autenticacion.md](autenticacion.md#sesión) va en keyring, que usa el almacén de credenciales del sistema.
- `main.py` declara el nombre de la organización, su dominio y el nombre de la app en la `QApplication` antes de crear un `QSettings` ([QSettings, *Basic Usage*](../fuentes/qt/qsettings.qdoc)).
- Una clave se escribe siempre con las mismas mayúsculas, dos claves no difieren solo en ellas, y ninguna lleva `/` ni `\` ([QSettings, *Section and Key Syntax*](../fuentes/qt/qsettings.qdoc)).
- La ventana principal lee su geometría y su estado al crearse, y los guarda en `closeEvent()` ([QSettings, *Restoring the State of a GUI Application*](../fuentes/qt/qsettings.qdoc)).
- `QSettings` lee solo el archivo que escribió la app ([QSettings, *Security Considerations*](../fuentes/qt/qsettings.qdoc)).

## Código de autorización

Contrato: [autenticacion.md](autenticacion.md#código-de-autorización).

- La app entra solo por el navegador del sistema, sin pantallas propias de contraseña ni de código por SMS: el login es el de la web, que cumple [Contraseñas](autenticacion.md#contraseñas), [Código por SMS](autenticacion.md#código-por-sms) y [Recuperación](autenticacion.md#recuperación), ofrece la passkey y lo completa el gestor de contraseñas del navegador.
- La app hace el flujo del código de autorización con `QOAuth2AuthorizationCodeFlow` de QtNetworkAuth, con PKCE S256, y abre la autorización con `QDesktopServices.openUrl` desde `authorizeWithBrowser`.
- La vuelta la recibe `QOAuthHttpServerReplyHandler`, que escucha en `127.0.0.1` con el puerto que le da el sistema.

## Idiomas

Contrato: [transversal.md](transversal.md#idiomas).

- Los textos usan Qt Linguist. Un solo mecanismo traduce la app y los diálogos propios de Qt.
- Los `.qm` van en `resources.qrc`: no se distribuyen aparte. [PySide6 6.12.0](https://raw.githubusercontent.com/qtproject/pyside-pyside-setup/v6.12.0/sources/pyside6/doc/tutorials/basictutorial/translations.rst)
- Los textos se extraen con `pyside6-lupdate -extensions py src/app`, que recorre todo el paquete. `pyside6-project lupdate` solo lee los archivos que se listan a mano, y uno que falte se queda sin traducir.
- Los `.qm` y `rc_resources.py` se generan y no van en git. Salen de los `.ts` y del `.qrc`; en git quedarían desfasados.

## OpenAPI y clientes

Contrato: [transversal.md](transversal.md#openapi-y-clientes).

- datamodel-code-generator genera desde `../server/openapi.json` los modelos del cable en `src/app/api/models.py`, con la configuración de `[tool.datamodel-codegen]`: modelos de Pydantic v2, campos en snake_case con su alias en camelCase y `extra="forbid"` en cada esquema que declara `additionalProperties: false`. Un modelo generado rechaza un campo y un valor de enum que no conoce.
- `src/app/api/models.py` se versiona, y CI lo vuelve a generar y falla si cambia: Nuitka compila `src/app/` tal como está.
- `src/app/api/models.py` no lleva docstrings propios: los suyos son las descripciones de los esquemas del servidor, y ruff no le exige las reglas `D1`.
- Las llamadas a la API se escriben a mano en `api/client.py`, con el `QNetworkAccessManager` de [Red](#red): datamodel-code-generator genera solo los modelos.

## Red

Estándar: [QNetworkAccessManager](../fuentes/qt/qnetworkaccessmanager.qdoc) de Qt.

- HTTP va por `QNetworkAccessManager`, y las respuestas se leen con los modelos de `api/models.py`. Es asíncrono sin hilos, y las respuestas llegan como señales al hilo de la interfaz.
- La app no llama a `ignoreSslErrors()`: un certificado que no vale termina la conexión, como fija [python.md](python.md#seguridad).
- La app tiene un solo `QNetworkAccessManager`, que usa desde el hilo principal ([QNetworkAccessManager, *QNetworkAccessManager*](../fuentes/qt/qnetworkaccessmanager.qdoc)).
- Un `QNetworkReply` terminado se libera con `deleteLater()`, nunca borrándolo en el slot de `finished()` ([QNetworkAccessManager, *QNetworkAccessManager*](../fuentes/qt/qnetworkaccessmanager.qdoc)).
- El `QIODevice` que sube un `post()` o un `put()` queda abierto y vivo hasta `finished()` ([QNetworkAccessManager, *post()*](../fuentes/qt/qnetworkaccessmanager.qdoc)).

## Tema

> **En desarrollo; no se implementa:** [transversal.md](transversal.md#tema).

Estándar: [QWidget](../fuentes/qt/qwidget.qdoc) de Qt.

Contrato: [transversal.md](transversal.md#tema).

- La app usa el estilo Fusion y una sola hoja de estilo, aplicada a la `QApplication` y armada desde `theme.py`. Lo que la hoja no define lo dibuja el estilo de cada sistema; Fusion lo iguala.
- La paleta de la `QApplication` sale de `palette()` con `LIGHT` o `DARK`, generados en `colors.py`, según la elección del usuario, guardada en `QSettings`. Con «sistema», sigue `QStyleHints.colorScheme()` y se vuelve a aplicar con `colorSchemeChanged`. El evento `ApplicationPaletteChange` no sirve: la app lo provoca al aplicar su paleta.
- Los tamaños van en `theme.py`, sin tamaños literales fuera de él.
- Una hoja de estilo que incluye datos que la app no controla se trata como una ruta no confiable: `url()` puede leer cualquier archivo local. [Qt 6.12.0](https://raw.githubusercontent.com/qt/qtbase/v6.12.0/src/widgets/doc/src/widgets-and-layouts/stylesheet.qdoc)
- En un widget complejo, como `QComboBox` o `QScrollBar`, personalizar una propiedad o un sub-control obliga a personalizar todos. [Qt 6.12.0](https://raw.githubusercontent.com/qt/qtbase/v6.12.0/src/widgets/doc/src/widgets-and-layouts/stylesheet-customizing.qdoc)
- Ningún widget cambia su estilo con `setStyle()`: la app usa uno solo ([QWidget, *setStyle*](../fuentes/qt/qwidget.qdoc)).

## Versión mínima de cliente

Contrato: [transversal.md](transversal.md#versión-mínima-de-cliente).

- `main.py` lee la versión de la app con `importlib.metadata.version()` y la pasa a `QApplication.setApplicationVersion()`, y el `User-Agent` la toma de `applicationVersion()`: la versión vive solo en `pyproject.toml`.
- El `extra_args` del `.spec` lleva `--include-distribution-metadata` con el nombre del proyecto: el ejecutable que arma Nuitka trae así los metadatos que lee `importlib.metadata`.

## WebSocket

Contrato: [transversal.md](transversal.md#websocket) y [autenticacion.md](autenticacion.md#websocket).

- El WebSocket va por `QWebSocket`, de QtWebSockets, abierto con un `QNetworkRequest` que lleva el `User-Agent` y `Authorization` de las peticiones: corre en el mismo bucle de eventos y entrega sus mensajes como señales.

## Pruebas

- En CI, las pruebas corren con `QT_QPA_PLATFORM=offscreen`, sin pantalla.
- Una prueba registra cada widget con `qtbot.addWidget` y lo maneja con sus propios métodos, como `setText` o `setCurrentIndex`, y no con los clics de `qtbot`: `qtbot` cierra lo que se registra, y el método del widget no depende de dónde cae un clic.

## Entrega

Estándar: [pyside6-deploy](../fuentes/pyside6/deployment-pyside6-deploy.rst) de PySide6.

- Las rutas de `pysidedeploy.spec` son relativas a `desktop/`, y la app se empaqueta solo en CI: cada corrida reescribe en el archivo las rutas absolutas de la máquina.
- `icon.png` mide 1024 × 1024 px, el mayor tamaño que usa macOS, y es el único icono, en lugar del `.ico` de Windows y el `.icns` de macOS que pide `pyside6-deploy`: Nuitka lo convierte al formato de cada sistema, y un archivo sirve a todos.
- La carpeta `dist/`, el `exec_directory` del `.spec`, existe antes de ejecutar `pyside6-deploy`: no la crea, y al copiar el binario falla con `FileNotFoundError`. En CI, `mkdir -p dist`.
- Nuitka con el extra `onefile`, imageio y, en Linux, patchelf van en el grupo `deploy`.
- En CI de Windows, el job agrega al `PATH` la carpeta del `dumpbin` de MSVC que encuentra `vswhere`, y falla si no lo encuentra: sin él, `pyside6-deploy` solo avisa y no busca los módulos de Qt de los que dependen los que usa la app. [PySide6 6.12.0](https://raw.githubusercontent.com/qtproject/pyside-pyside-setup/v6.12.0/sources/pyside-tools/deploy_lib/config.py)
- El job que empaqueta instala la app sin modo editable, con `--no-editable` en `uv sync` y en `uv run`: Nuitka busca en el `RECORD` de la distribución el paquete al que pertenecen sus metadatos, y una instalación editable no lo lista. [Nuitka 4.3.5](https://raw.githubusercontent.com/Nuitka/Nuitka/4.3.5/nuitka/utils/Distributions.py)
- El `.exe` de Windows va sin firmar: firmarlo exige un certificado de una autoridad certificadora, que se paga, y uno autofirmado no quita el aviso de SmartScreen. [Flet 1.1.2](https://raw.githubusercontent.com/flet-dev/flet/v1.1.2/website/docs/publish/windows.md)
- macOS no se construye hasta que haya cuenta de Apple Developer: sin firma ni notarización, macOS 15 no abre la app.
- El `mode` del `.spec` es `onefile`: cada sistema recibe un solo archivo, que [despliegue.md](despliegue.md#versiones) publica ([pyside6-deploy, *pysidedeploy.spec parameters*](../fuentes/pyside6/deployment-pyside6-deploy.rst)).
- `pyside6-deploy` corre con `--no-install`, y el `packages` del `.spec` lista `Nuitka` e `imageio`: comprueba que el grupo `deploy` los trajo, y no instala nada con pip, que un venv de uv no tiene ([pyside6-deploy, *Command Line Options*](../fuentes/pyside6/deployment-pyside6-deploy.rst) y [*What pyside6-deploy runs*](../fuentes/pyside6/deployment-pyside6-deploy.rst)).
- `pysidedeploy.spec` va en git: elige los paquetes y los argumentos de Nuitka ([pyside6-deploy, *What pyside6-deploy runs*](../fuentes/pyside6/deployment-pyside6-deploy.rst)).
- En Windows, `dumpbin` está en el `PATH` al empaquetar: con él, `pyside6-deploy` incluye solo los plugins que hacen falta ([pyside6-deploy, *Considerations*](../fuentes/pyside6/deployment-pyside6-deploy.rst)).

## Cumplimiento

| Convención | Herramienta |
| :--- | :--- |
| `@override` | Pyrefly `missing-override-decorator` |
| Los nombres originales de Qt | ruff `TID251` sobre `__feature__` |
| Un enum con su clase | Pyrefly `missing-attribute` |
| La interfaz en código | ruff `TID251` sobre `PySide6.QtUiTools` |
| HTTP por `QNetworkAccessManager` | ruff `TID251` sobre httpx, requests y `urllib.request` |
| Pruebas sin pantalla | `QT_QPA_PLATFORM=offscreen` en el job de CI |
| `src/app/api/models.py` al día con `../server/openapi.json` | `uv run datamodel-codegen` y `git diff --exit-code src/app/api/models.py` en CI |
