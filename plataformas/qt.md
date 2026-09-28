# Qt

Una aplicación de escritorio con Qt Widgets y PySide6. Se suma a [python.md](python.md).

## Layout

```text
desktop/
  pyproject.toml
  uv.lock
  pysidedeploy.spec
  src/<paquete>/
    __init__.py
    main.py
    theme.py          la hoja de estilo global
    api/              el cliente y sus modelos
    windows/
    dialogs/
    models/           los modelos de Qt
  tests/
    __init__.py
    test_theme.py
```

Plantilla: [`plantilla/qt/`](../plantilla/qt/). `tests/test_theme.py` es canónico y se copia sin
editar; `theme.py` es un punto de partida y va en `src/<paquete>/`.

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

- La interfaz se construye en código. mypy revisa los widgets y los diffs se leen.

## Layouts

Estándar: [*Layout Management*](../estandares/qt/layout.qdoc) de Qt.

## Model/View

Estándar: [*Model/View Programming*](../estandares/qt/model-view-programming.qdoc) de Qt.

## Configuración

Estándar: [`QSettings`](../estandares/qt/qsettings.qdoc) de Qt.

- `QSettings` usa `IniFormat`: el mismo archivo legible en todos los sistemas.

## Estilo

Estándares: [*Qt Style Sheets*](../estandares/qt/stylesheet.qdoc), su
[sintaxis](../estandares/qt/stylesheet-syntax.qdoc), la
[personalización](../estandares/qt/stylesheet-customizing.qdoc) y la
[referencia](../estandares/qt/stylesheet-reference.qdoc).

- La app usa el estilo Fusion y una sola hoja de estilo, aplicada a la `QApplication` y armada
  desde `theme.py`. Lo que la hoja no define lo dibuja el estilo de cada sistema; Fusion lo iguala.

## Red e hilos

Estándares: [`QNetworkAccessManager`](../estandares/qt/qnetworkaccessmanager.qdoc) y
[*Threading Classes*](../estandares/qt/threads.qdoc) de Qt.

- HTTP va por `QNetworkAccessManager`, y las respuestas se leen con modelos de Pydantic en `api/`.
  Es asíncrono sin hilos, y las respuestas llegan como señales al hilo de la interfaz.

## Traducciones

Estándar: las [traducciones](../estandares/pyside6/translations.rst) de PySide6.

## Pruebas

Estándares: la [introducción](../estandares/pytest-qt/intro.rst), el
[tutorial](../estandares/pytest-qt/tutorial.rst), la
[`QApplication`](../estandares/pytest-qt/qapplication.rst), el
[logging](../estandares/pytest-qt/logging.rst) y las [señales](../estandares/pytest-qt/signals.rst)
de pytest-qt.

- En CI, las pruebas corren con `QT_QPA_PLATFORM=offscreen`, sin pantalla.

## Empaquetado

Estándar: [`pyside6-deploy`](../estandares/pyside6/deployment-pyside6-deploy.rst).

## Cómo se hace cumplir

| Qué | Con qué |
|---|---|
| `@override` | mypy `explicit-override` |
| Los nombres originales de Qt | ruff `TID251` sobre `__feature__` |
| La interfaz en código | ruff `TID251` sobre `PySide6.QtUiTools` |
| HTTP por `QNetworkAccessManager` | ruff `TID251` sobre httpx, requests y `urllib.request` |
| Fusion y una sola hoja de estilo en `theme.py` | `tests/test_theme.py` |
| Pruebas sin pantalla | `QT_QPA_PLATFORM=offscreen` en el job de CI |
