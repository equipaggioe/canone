# Qt

Una aplicación de escritorio con Qt Widgets y PySide6. Se suma a [python.md](python.md).

## Proyecto

- PySide6 y Qt 6.12.0, pytest-qt 4.5.0, Nuitka 4.3.4, imageio 2.38.1 y patchelf 0.19.3.0.

```text
desktop/
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

Plantilla: [plantilla/qt/](../plantilla/qt/).

## PySide6

Estándar: las [consideraciones](../fuentes/pyside6/considerations.rst) de PySide6.

- La API de Qt se usa con sus nombres originales. Los stubs de PySide6 y la documentación de Qt usan esos nombres.
- Todo método que sobrescribe otro lleva `@override`: un `closeEvent` mal escrito nunca se llama y nada avisa.
- Todo método conectado a una señal lleva `@Slot`: sin él, cada conexión agrega el método al `QMetaObject` en tiempo de ejecución. [PySide6 6.12.0](https://raw.githubusercontent.com/qtproject/pyside-pyside-setup/v6.12.0/sources/pyside6/doc/tutorials/basictutorial/signals_and_slots.rst)
- Un slot no es privado, con prefijo `__`: obliga a búsquedas en tiempo de ejecución. [PySide6 6.12.0](https://raw.githubusercontent.com/qtproject/pyside-pyside-setup/v6.12.0/sources/pyside6/doc/tutorials/basictutorial/signals_and_slots.rst)
- Las señales con tipos distintos llevan nombres distintos. [PySide6 6.12.0](https://raw.githubusercontent.com/qtproject/pyside-pyside-setup/v6.12.0/sources/pyside6/doc/tutorials/basictutorial/signals_and_slots.rst)

## Widgets y diálogos

Estándar: de Qt, las entradas que se usan de [QWidget](../fuentes/qt/qwidget.qdoc) y de [QDialog](../fuentes/qt/qdialog.qdoc).

- La interfaz se construye en código. Pyrefly revisa los widgets y los diffs se leen.

## Layouts

Estándar: [*Layout Management*](../fuentes/qt/layout.qdoc) de Qt.

## Model/View

Estándar: [*Model/View Programming*](../fuentes/qt/model-view-programming.qdoc) de Qt.

## Accesibilidad

Estándares: [*Accessibility*](../fuentes/qt/accessible.qdoc) de Qt, salvo *Accessibility for Qt Quick Applications*; y la propiedad `accessibleName` de [QWidget](../fuentes/qt/qwidget.qdoc).

Contrato: [transversal.md](transversal.md#accesibilidad).

## Almacenamiento

Estándar: las entradas que se usan de [QSettings](../fuentes/qt/qsettings.qdoc) de Qt.

- `QSettings` usa `IniFormat`: el mismo archivo legible en todos los sistemas.
- El token de refresco que pide [transversal.md](transversal.md#sesión) va en keyring, que usa el almacén de credenciales del sistema.

## Idiomas

Contrato: [transversal.md](transversal.md#idiomas).

- Los textos usan Qt Linguist. Un solo mecanismo traduce la app y los diálogos propios de Qt.
- Los `.qm` van en `resources.qrc`: no se distribuyen aparte. [PySide6 6.12.0](https://raw.githubusercontent.com/qtproject/pyside-pyside-setup/v6.12.0/sources/pyside6/doc/tutorials/basictutorial/translations.rst)
- Los textos se extraen con `pyside6-lupdate -extensions py src/app`, que recorre todo el paquete. `pyside6-project lupdate` solo lee los archivos que se listan a mano, y uno que falte se queda sin traducir.
- Los `.qm` y `rc_resources.py` se generan y no van en git. Salen de los `.ts` y del `.qrc`; en git quedarían desfasados.

## Red

Estándares: de Qt, las entradas que se usan de [QNetworkAccessManager](../fuentes/qt/qnetworkaccessmanager.qdoc), y [*Threading Classes*](../fuentes/qt/threads.qdoc), entero.

- HTTP va por `QNetworkAccessManager`, y las respuestas se leen con modelos de Pydantic en `api/`. Es asíncrono sin hilos, y las respuestas llegan como señales al hilo de la interfaz.

## Tema

> **En desarrollo; no se implementa:** [transversal.md](transversal.md#tema).

Estándar: las entradas que se usan de la [referencia de *Qt Style Sheets*](../fuentes/qt/stylesheet-reference.qdoc).

Contrato: [transversal.md](transversal.md#tema).

- La app usa el estilo Fusion y una sola hoja de estilo, aplicada a la `QApplication` y armada desde `theme.py`. Lo que la hoja no define lo dibuja el estilo de cada sistema; Fusion lo iguala.
- La paleta de la `QApplication` sale de `palette()` con `LIGHT` o `DARK`, generados en `colors.py`, según `QStyleHints.colorScheme()`, y se vuelve a aplicar con `colorSchemeChanged`. El evento `ApplicationPaletteChange` no sirve: la app lo provoca al aplicar su paleta.
- Los tamaños van en `theme.py`, sin tamaños literales fuera de él.
- Una hoja de estilo que incluye datos que la app no controla se trata como una ruta no confiable: `url()` puede leer cualquier archivo local. [Qt 6.12.0](https://raw.githubusercontent.com/qt/qtbase/v6.12.0/src/widgets/doc/src/widgets-and-layouts/stylesheet.qdoc)
- En un widget complejo, como `QComboBox` o `QScrollBar`, personalizar una propiedad o un sub-control obliga a personalizar todos. [Qt 6.12.0](https://raw.githubusercontent.com/qt/qtbase/v6.12.0/src/widgets/doc/src/widgets-and-layouts/stylesheet-customizing.qdoc)

Plantilla: `theme.py` es un punto de partida; `tests/test_theme.py` es canónico y se copia sin editar.

## Pruebas

- En CI, las pruebas corren con `QT_QPA_PLATFORM=offscreen`, sin pantalla.
- Una prueba registra cada widget con `qtbot.addWidget` y lo maneja con sus propios métodos, como `setText` o `setCurrentIndex`, y no con los clics de `qtbot`: `qtbot` cierra lo que se registra, y el método del widget no depende de dónde cae un clic.

## Empaquetado

Estándar: las entradas de [pyside6-deploy](../fuentes/pyside6/deployment-pyside6-deploy.rst) que usa `pysidedeploy.spec`.

- `pysidedeploy.spec` va en git, con rutas relativas a `desktop/`, y la app se empaqueta solo en CI. Cada corrida reescribe en el archivo las rutas absolutas de la máquina.
- `icon.png` mide 1024 × 1024 px, el mayor tamaño que usa macOS, y es el único icono: Nuitka lo convierte al formato de cada sistema. Contradice `pyside6-deploy`, que pide `.ico` en Windows y `.icns` en macOS: un archivo sirve a todos.
- Nuitka con el extra `onefile`, imageio y, en Linux, patchelf van en el grupo `deploy`, y el `packages` del `.spec` queda vacío. `pyside6-deploy` instala sus paquetes con pip, que un venv de uv no trae.

## Cumplimiento

| Convención | Herramienta |
| :--- | :--- |
| PySide6, pytest-qt, Nuitka, imageio y patchelf | [scripts/verificar.py](../scripts/verificar.py) |
| `@override` | Pyrefly `missing-override-decorator` |
| Los nombres originales de Qt | ruff `TID251` sobre `__feature__` |
| La interfaz en código | ruff `TID251` sobre `PySide6.QtUiTools` |
| HTTP por `QNetworkAccessManager` | ruff `TID251` sobre httpx, requests y `urllib.request` |
| Pruebas sin pantalla | `QT_QPA_PLATFORM=offscreen` en el job de CI |
