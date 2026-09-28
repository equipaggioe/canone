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

- La red, la base y el sistema se tocan desde `core/`. `ui/` solo arma y muestra.

## PySide6

Estándares: [*Considerations*](../estandares/pyside6/considerations.rst) y
[*Porting from PySide2 to PySide6*](../estandares/pyside6/porting_from2.rst) de Qt for Python, y su
tutorial [*Signals and Slots*](../estandares/pyside6/signals_and_slots.rst).

- La API de Qt se usa en camelCase, como en su documentación.
- Una conexión se hace con `signal.connect(slot)`.
- Un `.ui` se compila con `pyside6-uic` a `ui/forms/ui_<nombre>.py`: así mypy ve cada widget con su
  tipo.
- El `ui_<nombre>.py` se commitea junto a su `.ui` y cambia solo al regenerarse.

## Widgets

Estándares: [*Object Trees & Ownership*](../estandares/qt/objecttrees.qdoc),
[*Layout Management*](../estandares/qt/layout.qdoc) y
[*Model/View Programming*](../estandares/qt/model-view-programming.qdoc) de Qt, y la documentación
de [`QSettings`](../estandares/qt/qsettings.qdoc).

- Todo widget que no es una ventana tiene padre: lo recibe al crearse o al entrar en un layout.
- Los widgets hijos se ubican con layouts.
- Datos en tabla, lista o árbol: un modelo con `QTableView`, `QListView` o `QTreeView`, siempre: las
  clases de ítems no aceptan otro modelo.
- Las preferencias del usuario, como el tamaño de la ventana, se guardan con `QSettings`.

## Tema

Estándar: [Qt Style Sheets](../estandares/qt/stylesheet.qdoc).

- Estilo `Fusion`.
- Los colores y la hoja de estilos viven en `ui/theme.py`, que aplica una sola hoja a la
  `QApplication`: un color se cambia en un solo lugar.
- Una variante de un widget es una propiedad dinámica con su selector en esa hoja, y se cambia con
  `set_variant` de `ui/theme.py`.

## Red e hilos

Estándares: [*Multithreading Technologies in Qt*](../estandares/qt/threads.qdoc) y la documentación
de [`QNetworkAccessManager`](../estandares/qt/qnetworkaccessmanager.qdoc).

- Todo corre sobre el lazo de eventos de Qt.
- HTTP con `QNetworkAccessManager`: su API es asíncrona sobre ese lazo.
- Una sola instancia de `QNetworkAccessManager` para toda la aplicación, creada con
  `setAutoDeleteReplies(True)`.
- Lo que tarda corre fuera del hilo principal.

## Tests

Estándar: [pytest-qt](../estandares/pytest-qt/intro.rst).

- Plataforma `offscreen`: los tests corren sin pantalla, también en CI.
- Una advertencia de Qt hace fallar el test, con la categoría `qt.pyside.libpyside` activa: así se
  ve cada método conectado sin `@Slot`.

## Empaquetado

Estándar: [*pyside6-deploy*](../estandares/pyside6/deployment-pyside6-deploy.rst) de Qt for Python.

- La aplicación se empaqueta con `pyside6-deploy`.
- El `pysidedeploy.spec` se commitea.

## Cómo se hace cumplir

| Convención | Con qué |
|---|---|
| [Qt for Python, enums de Python](../estandares/pyside6/considerations.rst) | mypy `strict` |
| [Porting, `exec_` obsoleto](../estandares/pyside6/porting_from2.rst) | `tests/test_conventions.py` |
| [Porting, API obsoleta](../estandares/pyside6/porting_from2.rst) | `filterwarnings` de pytest vuelve error el `DeprecationWarning` de PySide6, en lo que recorren los tests |
| [*Signals and Slots*, `@Slot`](../estandares/pyside6/signals_and_slots.rst) | `qt.pyside.libpyside` y `qt_log_level_fail`, en lo que recorren los tests |
| camelCase | `TID251` sobre `__feature__.snake_case` |
| `signal.connect(slot)` | `TID251` sobre `SIGNAL` y `SLOT` |
| `pyside6-uic` | `TID251` sobre `QtUiTools` |
| `ui_*.py` generados | Fuera de ruff con `extend-exclude`; en mypy, `ignore_errors` y `untyped_calls_exclude` para `ui.forms` |
| `ui_*.py` al día | CI lo regenera con `pyside6-uic` y falla si `ui/forms/` cambia |
| Modelo y vista | `TID251` sobre `QTableWidget`, `QListWidget` y `QTreeWidget` |
| Red, base y sistema en `core/` | `TID251` en `ui/ruff.toml` |
| Estilo `Fusion` | `tests/test_conventions.py` |
| Colores y hoja de estilos en `theme.py` | `tests/test_theme.py` |
| [`QWidget::setPalette` con hojas de estilo](../estandares/qt/qwidget.qdoc) | `tests/test_conventions.py` |
| Lazo de eventos de Qt y HTTP con `QNetworkAccessManager` | `TID251` sobre `asyncio`, `QtAsyncio`, `requests`, `httpx` y `urllib.request` |
| Una sola instancia de `QNetworkAccessManager`, con `setAutoDeleteReplies(True)` | `tests/test_conventions.py` |
| `ui/ruff.toml`, `tests/test_theme.py` y `tests/test_conventions.py` iguales a los de canone | `scripts/verificar.py` |

### Configuración

La base está en [`plantilla/qt/pyproject.toml`](../plantilla/qt/pyproject.toml). Sobre la de
[python.md](python.md) suma `pytest-qt`, el `banned-api` de la tabla, `qt_log_level_fail` y
`filterwarnings`. `tests/conftest.py` fija la plataforma y la categoría de log.

### CI

Los pasos de [python.md](python.md), con `mypy .`, y después `uv run pytest`. Antes de ruff, el paso
que regenera los formularios. Todo está en el job `desktop` de
[`plantilla/.github/workflows/ci.yml`](../plantilla/.github/workflows/ci.yml).
