# PySide6 (Qt)

Aplicación de escritorio con Qt Widgets. Se suma a [python.md](python.md). Archivos base en
[`plantilla/qt/`](../plantilla/qt/).

## Layout

```
desktop/
  pyproject.toml
  pysidedeploy.spec
  main.py
  core/
    api_client.py
    session.py
    constants.py
  ui/
    ruff.toml
    theme.py
    main_window.py
    <vista>_view.py
    <algo>_panel.py
    forms/
      <nombre>.ui
      ui_<nombre>.py
  tests/
    conftest.py
    test_conventions.py
    test_theme.py
```

- La red, la base y el sistema solo se tocan desde `core/`.

## PySide6

Estándares: *Considerations* y *Porting from PySide2 to PySide6* de Qt for Python, y su tutorial
*Signals and Slots*.

Sobre *Considerations* y *Porting*:

- Enums con su nombre completo.
- `exec()`, nunca `exec_()`.
- Nada de API que PySide6 marque como obsoleta, como `QMouseEvent.pos()` o los atributos de alta
  resolución.

Sobre *Signals and Slots*:

- Conexiones con `signal.connect(slot)`, nunca con `SIGNAL()` ni `SLOT()`.
- Todo método conectado a una señal lleva `@Slot`.

Donde la documentación admite dos caminos:

- La API de Qt se usa en `camelCase`, como en su documentación. Nada de
  `from __feature__ import snake_case`.
- Un `.ui` se compila con `pyside6-uic` a `ui/forms/ui_<nombre>.py`, nunca se carga con
  `QUiLoader`: así mypy ve cada widget con su tipo.
- El `ui_<nombre>.py` generado se commitea junto a su `.ui` y nunca se edita a mano.

## Widgets

Estándares: *Object Trees & Ownership*, *Layout Management* y *Model/View Programming* de Qt, y
la documentación de `QDialog` y `QSettings`.

- Todo widget que no es una ventana tiene padre: se crea con `parent` o lo adopta un layout. Sin
  padre ni referencia en Python, PySide6 lo destruye.
- Los widgets hijos se ubican con layouts, nunca con `setGeometry` ni `move`.
- Un diálogo se abre con `open()` y su resultado llega por `finished`. Nada de `QDialog.exec()`:
  levanta un segundo bucle de eventos.
- Datos en tabla, lista o árbol: un modelo con `QTableView`, `QListView` o `QTreeView`. Nada de
  `QTableWidget`, `QListWidget` ni `QTreeWidget`.
- Las preferencias del usuario, como el tamaño de la ventana, se guardan con `QSettings`.

## Tema

Estándar: Qt Style Sheets.

- Estilo `Fusion`.
- Colores solo en `ui/theme.py`.
- Los colores van en una sola hoja de estilos, aplicada a la `QApplication`. Ningún widget llama a
  `setStyleSheet`.
- Nada de `setPalette`: la documentación de Qt desaconseja combinarlo con una hoja de estilos.
- Una variante es una propiedad dinámica con su selector en la hoja global. Al cambiarla, `unpolish`
  y `polish` del widget.

## Red e hilos

Estándar: hilos de Qt y `QNetworkAccessManager`.

- Los widgets solo se usan desde el hilo principal.
- Nada que tarde corre en el hilo principal.
- HTTP solo por `QNetworkAccessManager`: una instancia para toda la aplicación, usada desde el hilo
  que la creó.
- La instancia se crea con `setAutoDeleteReplies(True)`: cada `QNetworkReply` se libera sola al
  terminar.
- Nada de `asyncio` ni `QtAsyncio`.
- Un trabajo con comandos es un `QObject` movido con `moveToThread`. Una tarea suelta, un
  `QRunnable` en el `QThreadPool`. Un bucle permanente sin eventos, un `QThread` con `run()`.
- El resultado vuelve por una señal. Un worker no toca widgets.
- La conexión a la base se abre en el hilo que la usa.

## Tests

- `pytest-qt`.
- Una advertencia de Qt hace fallar el test.
- Plataforma `offscreen` y la categoría `qt.pyside.libpyside` activa.

## Empaquetado

Estándar: *pyside6-deploy* de Qt for Python.

- La aplicación se empaqueta con `pyside6-deploy`.
- El `pysidedeploy.spec` se commitea.

## Cómo se hace cumplir

| Convención | Con qué |
|---|---|
| Enums con nombre completo | mypy `strict` |
| `exec()`, no `exec_()` | `tests/test_conventions.py` |
| Sin API obsoleta | `filterwarnings` de pytest vuelve error el `DeprecationWarning` de PySide6, en lo que recorren los tests |
| Estilo `Fusion` | `tests/test_conventions.py` |
| `@Slot` | `qt.pyside.libpyside` y `qt_log_level_fail`, en lo que recorren los tests |
| Sin `SIGNAL()` ni `SLOT()` | `TID251` en `pyproject.toml` |
| Solo `QNetworkAccessManager`, sin `asyncio` | `TID251` en `pyproject.toml` |
| Una sola instancia de `QNetworkAccessManager`, con `setAutoDeleteReplies(True)` | `tests/test_conventions.py` |
| Sin `snake_case` ni `QUiLoader` | `TID251` en `pyproject.toml` |
| Sin `QTableWidget`, `QListWidget` ni `QTreeWidget` | `TID251` en `pyproject.toml` |
| `ui_*.py` generados | Fuera de ruff con `extend-exclude`; en mypy, `ignore_errors` y `untyped_calls_exclude` para `ui.forms` |
| `ui_*.py` commiteado y sin editar | CI lo regenera con `pyside6-uic` y falla si `ui/forms/` cambia |
| Sin `setPalette` | `tests/test_conventions.py` |
| Red, base y sistema solo en `core/` | `TID251` en `ui/ruff.toml` |
| Colores y `setStyleSheet` solo en `theme.py` | `tests/test_theme.py` |
| `ui/ruff.toml`, `tests/test_theme.py` y `tests/test_conventions.py` iguales a los de canone | `scripts/verificar.py` |

### CI

Los pasos de [python.md](python.md), con `mypy .`, y después `uv run pytest`. Antes de ruff, el paso
que regenera los formularios. Todo está en el job `desktop` de
[`plantilla/.github/workflows/ci.yml`](../plantilla/.github/workflows/ci.yml).
