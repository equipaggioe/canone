# Qt

Una aplicación de escritorio con Qt Widgets y PySide6. Se suma a [python.md](python.md).

## Proyecto

Estándares: [`pyside6-deploy`](../estandares/pyside6/deployment-pyside6-deploy.rst) y las
[traducciones](../estandares/pyside6/translations.rst) de PySide6.

```text
desktop/
  pyproject.toml
  uv.lock
  pysidedeploy.spec
  src/app/
    __init__.py
    main.py             crea la QApplication y abre la ventana principal
    theme.py            los tokens de diseño y la hoja de estilo global
    icon.png
    resources.qrc       el icono y las traducciones compiladas
    translations/
      <locale>.ts
    api/
      __init__.py
      client.py         el cliente de la API
      base.py           el modelo base
      problem.py        el sobre de error RFC 9457
      <recurso>.py      los modelos de un recurso
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

Plantilla: [`plantilla/qt/`](../plantilla/qt/).

## PySide6

Estándares: las [consideraciones](../estandares/pyside6/considerations.rst), la
[migración desde PySide2](../estandares/pyside6/porting_from2.rst) y
[señales y slots](../estandares/pyside6/signals_and_slots.rst) de PySide6, y
[PEP 698](../estandares/python/pep-0698.rst).

- La API de Qt se usa con sus nombres originales. Los stubs de PySide6 y la documentación de Qt
  usan esos nombres.
- Todo método que sobrescribe otro lleva `@override`. Endurece PEP 698, que lo deja opcional: un
  `closeEvent` mal escrito nunca se llama y nada avisa.

## Árbol de objetos

Estándar: [*Object Trees & Ownership*](../estandares/qt/objecttrees.qdoc) de Qt.

## Widgets y diálogos

Estándares: [`QWidget`](../estandares/qt/qwidget.qdoc) y [`QDialog`](../estandares/qt/qdialog.qdoc)
de Qt.

- La interfaz se construye en código. Pyrefly revisa los widgets y los diffs se leen.

## Layouts

Estándar: [*Layout Management*](../estandares/qt/layout.qdoc) de Qt.

## Model/View

Estándar: [*Model/View Programming*](../estandares/qt/model-view-programming.qdoc) de Qt.

## Accesibilidad

Estándares: [*Accessibility*](../estandares/qt/accessible.qdoc) de Qt y la propiedad
`accessibleName` de [`QWidget`](../estandares/qt/qwidget.qdoc).

Contrato: [transversal.md](transversal.md#accesibilidad).

## Almacenamiento

Estándar: [`QSettings`](../estandares/qt/qsettings.qdoc) de Qt.

- `QSettings` usa `IniFormat`: el mismo archivo legible en todos los sistemas.
- El token de refresco que pide [transversal.md](transversal.md#sesión) va en keyring, que usa el
  almacén de credenciales del sistema.

## Idiomas

Estándar: las [traducciones](../estandares/pyside6/translations.rst) de PySide6.

Contrato: [transversal.md](transversal.md#idiomas).

- Los textos usan Qt Linguist. Un solo mecanismo traduce la app y los diálogos propios de Qt.
- Los textos se extraen con `pyside6-lupdate -extensions py src/app`, que recorre todo el paquete.
  `pyside6-project lupdate` solo lee los archivos que se listan a mano, y uno que falte se queda
  sin traducir.
- Los `.qm` y `rc_resources.py` se generan y no van en git. Salen de los `.ts` y del `.qrc`; en git
  quedarían desfasados.

## Red

Estándares: [`QNetworkAccessManager`](../estandares/qt/qnetworkaccessmanager.qdoc) y
[*Threading Classes*](../estandares/qt/threads.qdoc) de Qt.

- HTTP va por `QNetworkAccessManager`, y las respuestas se leen con modelos de Pydantic en `api/`.
  Es asíncrono sin hilos, y las respuestas llegan como señales al hilo de la interfaz.

## Tema

Estándares: [*Qt Style Sheets*](../estandares/qt/stylesheet.qdoc), su
[sintaxis](../estandares/qt/stylesheet-syntax.qdoc), la
[personalización](../estandares/qt/stylesheet-customizing.qdoc) y la
[referencia](../estandares/qt/stylesheet-reference.qdoc).

- La app usa el estilo Fusion y una sola hoja de estilo, aplicada a la `QApplication` y armada
  desde `theme.py`. Lo que la hoja no define lo dibuja el estilo de cada sistema; Fusion lo iguala.

Plantilla: `theme.py` es un punto de partida; `tests/test_theme.py` es canónico y se copia sin
editar.

## Pruebas

Estándares: la [introducción](../estandares/pytest-qt/intro.rst), el
[tutorial](../estandares/pytest-qt/tutorial.rst), la
[`QApplication`](../estandares/pytest-qt/qapplication.rst), el
[logging](../estandares/pytest-qt/logging.rst) y las [señales](../estandares/pytest-qt/signals.rst)
de pytest-qt.

- En CI, las pruebas corren con `QT_QPA_PLATFORM=offscreen`, sin pantalla.

## Empaquetado

Estándar: [`pyside6-deploy`](../estandares/pyside6/deployment-pyside6-deploy.rst).

- `pysidedeploy.spec` va en git, con rutas relativas a `desktop/`, y la app se empaqueta solo en
  CI. Cada corrida reescribe en el archivo las rutas absolutas de la máquina.
- `icon.png` mide 1024 × 1024 px, el mayor tamaño que usa macOS, y es el único icono: Nuitka lo
  convierte al formato de cada sistema. Contradice `pyside6-deploy`, que pide `.ico` en Windows y
  `.icns` en macOS: un archivo sirve a todos.
- Nuitka con el extra `onefile`, imageio y, en Linux, patchelf van en el grupo `deploy`, y el
  `packages` del `.spec` queda vacío. `pyside6-deploy` instala sus paquetes con pip, que un venv de
  uv no trae.

## Cómo se hace cumplir

| Qué | Con qué |
|---|---|
| `@override` | Pyrefly `missing-override-decorator` |
| Los nombres originales de Qt | ruff `TID251` sobre `__feature__` |
| La interfaz en código | ruff `TID251` sobre `PySide6.QtUiTools` |
| HTTP por `QNetworkAccessManager` | ruff `TID251` sobre httpx, requests y `urllib.request` |
| Fusion y una sola hoja de estilo en `theme.py` | `tests/test_theme.py` |
| Pruebas sin pantalla | `QT_QPA_PLATFORM=offscreen` en el job de CI |
