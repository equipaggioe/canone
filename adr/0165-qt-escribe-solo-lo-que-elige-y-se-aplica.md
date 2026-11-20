# ADR-0165 · `qt.md` escribe solo lo que elige, y se aplica a los repositorios

- **Estado:** Aceptada. El usuario pidió aplicar la revisión con sus correcciones (2026-11-16). El punto 6 lo reemplaza el [ADR-0175](0175-qt-y-flet-entran-con-pantallas-propias-sin-salir-al-navegador.md), y la hoja única del punto 8, el [ADR-0201](0201-un-producto-elige-sus-temas-y-sus-modos-y-el-modo-es-otro-modificador.md)
- **Fecha:** 2026-11-16
- **Alcance:** [`plataformas/qt.md`](../plataformas/qt.md),
  [`plataformas/transversal.md`](../plataformas/transversal.md), «Distribución»,
  [`plataformas/autenticacion.md`](../plataformas/autenticacion.md), «Código de autorización»,
  [`plataformas/flet.md`](../plataformas/flet.md), «Entrega», y `fuentes/qt/`

## Contexto

Primera revisión de una página con los criterios del
[ADR-0162](0162-una-pagina-escribe-decisiones-y-no-como-funciona-su-tecnologia.md) y del
[ADR-0163](0163-una-revision-recorre-el-documento-entero-y-propone-tambien-lo-que-falta.md).
Comprobado en la distro WSL `Testing`, con el `pyproject.toml` de `plantilla/qt/`, PySide6 6.12.0,
ruff 0.17.3 y Pyrefly 1.4:

- ruff `TID251` marca `__feature__`, `PySide6.QtUiTools`, httpx, requests, `urllib.request` y
  `from urllib import request`, pero no `http.client`.
- Pyrefly marca `Qt.AlignLeft` y `Qt.DirectConnection` con `missing-attribute`, y un `closeEvent`
  sin `@override` con `missing-override-decorator`.
- `pyside6-lupdate -extensions py src/app` encuentra un `tr()` dentro de un subpaquete.

## Decisión

1. **Salen de `qt.md` las convenciones que tienen una sola forma correcta**: las de `paintEvent()`,
   los handlers de teclado y de rueda, la referencia que mantiene vivo un diálogo, el resultado en
   `finished()`, el widget sin padre en un layout, `sizeHint()`, el layout antes de `setWidget()`,
   `QPersistentModelIndex`, los métodos abstractos de un modelo, `beginInsertRows()` y su familia,
   el orden de vida de los `QObject` entre hilos, el `QIODevice` de una subida, la regla de
   todo o nada de un widget complejo y `--include-distribution-metadata`, que no consta que haya
   fallado.
2. **Salen las que regulan una función que no se ofrece**: leer un archivo de `QSettings` ajeno y
   armar la hoja de estilo con datos externos. También la de Aceptar y Cancelar, porque la fuente
   da `done()` como equivalente.
3. **Salen de `fuentes/qt/` las copias que quedan con menos de tres convenciones**: `qdialog.qdoc`,
   `layout.qdoc`, `qnetworkaccessmanager.qdoc` y `threads.qdoc`. Lo que queda de ellas va como
   convención propia.
4. **Las convenciones que se quedan pierden la razón** cuando no se apartan de una fuente ni de otra
   regla de Canone.
5. **El `data()` de un modelo con los roles de accesibilidad pasa a «Accesibilidad»** como
   convención propia: *Read-Only access* no nombra `AccessibleTextRole` ni
   `AccessibleDescriptionRole`.
6. **La app de escritorio entra solo por el navegador del sistema**, y eso va en
   `autenticacion.md`. `qt.md` nombra las clases de QtNetworkAuth.
7. **Los ejecutables y los instaladores de Windows van sin firmar**, y eso se escribe una vez en
   `transversal.md`, «Distribución». Sale de `qt.md` y de `flet.md`.
8. **`http.client` entra en el `banned-api` de `plantilla/qt/`**, y «Cumplimiento» nombra lo que
   prohíbe. `tests/test_theme.py` entra como herramienta de Fusion y de la hoja única.
9. **`qt.md` deja de estar en desarrollo**, y su bloque de `stack.md` también. «Tema» conserva su
   nota mientras la tenga la sección de `transversal.md`.

## Consecuencias

- `verificar.py --repo` exige `qt.md` a los repositorios con `desktop/`.
- `@Slot`, el slot sin `__` y los nombres distintos de las señales quedan como convenciones propias.
  `signals_and_slots.rst` es un tutorial y no cumple «Autoridad».
- Firmar el instalador cuesta un certificado de una autoridad certificadora, y uno autofirmado no
  quita el aviso de SmartScreen
  ([Flet 1.1.2](https://raw.githubusercontent.com/flet-dev/flet/v1.1.2/website/docs/publish/windows.md)).

## Descartado

- **Adoptar `signals_and_slots.rst` como fuente:** se buscaba una fuente para convenciones que ya
  estaban escritas.
- **Serializar las peticiones con `by_alias=True` como convención:** tiene una sola forma correcta,
  y no consta que haya fallado.
- **Elegir entre `QThreadPool` y un worker en un `QThread`:** una convención que se propone no
  cuenta para «Aporta», y la decisión no se tomó.
