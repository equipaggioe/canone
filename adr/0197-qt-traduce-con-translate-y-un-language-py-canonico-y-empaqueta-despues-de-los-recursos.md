# ADR-0197 · Qt traduce con `translate` y un `language.py` canónico, y empaqueta después de compilar los recursos

- **Estado:** Aceptada. El usuario pidió desarrollar los cambios recomendados si eran los más
  convenientes para cualquier repositorio (2026-11-19)
- **Fecha:** 2026-11-19
- **Alcance:** [`plataformas/qt.md`](../plataformas/qt.md), «Proyecto», «Idiomas» y «Entrega»;
  `plantilla/qt/src/app/services/language.py`; el job `desktop` de
  `plantilla/.github/workflows/release.yml`; `scripts/verificar.py`

## Contexto

Consola es la primera app de Qt que implementó «Idiomas» y «Entrega» enteras. Se comprobó con
PySide6 6.12.0, Nuitka 4.3.5 y uv 0.13.9, en Windows y en Debian 13:

- **El orden del job `desktop`.** Instalaba la app con `--no-editable` y después compilaba las
  traducciones y `resources.qrc`. La instalación copia `src/app/` como está, y Nuitka compila esa
  copia: el binario de Linux se armó y al abrirse falló con
  `ModuleNotFoundError: No module named 'app.rc_resources'`.
- **El icono en Linux.** Con el `mode` en `onefile`, Nuitka avisa: «Using Linux app specific
  option '--linux-app-icon' has no effect unless building with '--mode=app' or
  '--mode=app-dist' on Linux».
- **La extracción.** En Windows, `pyside6-lupdate -extensions py src/app` termina con un fallo de
  acceso a memoria (3221225477) si lee el `rc_resources.py` de Consola, de 250 KB, con
  `qtbase_es.qm` dentro. Con un `rc_resources.py` que solo lleva el icono no falla, y en Debian no
  falla con ninguno de los dos.
- **`self.tr()`.** Busca con la clase del objeto: un método heredado, llamado desde una subclase,
  busca con el nombre de la subclase y no encuentra el texto que `pyside6-lupdate` guardó con la
  clase donde está escrito.
- **`QT_TRANSLATE_NOOP`.** En los stubs de PySide6 devuelve `object`, y Pyrefly strict rechaza
  usarlo como `str`. `pyside6-lupdate` reconoce `translate(...)` y `QT_TRANSLATE_NOOP(...)` por el
  nombre de la función, venga de donde venga.
- `qt.md` no decía en qué idioma va el texto fuente, ni qué idioma rige si el del sistema no tiene
  traducción. `flet.md` cae en el primero de `supported_locales`, y en Flutter la plantilla de las
  traducciones es la del idioma base.

## Decisión

1. **El job `desktop` de `release.yml` instala las dependencias con `--no-install-project`,
   compila las traducciones y `resources.qrc` con `uv run --no-sync`, y al final instala la app
   con `--no-editable`.**
2. **La ventana principal pone `icon.png` con `setWindowIcon`**: es el único icono que tiene la app
   en Linux.
3. **Los textos se extraen de los `.py` que git no ignora**:
   `pyside6-lupdate $(git ls-files --cached --others --exclude-standard 'src/app/*.py') -ts
   src/app/translations/<locale>.ts`. Así no lee el `rc_resources.py` generado, que está en
   `.gitignore`.
4. **El texto fuente es el del idioma base.**
5. **Un texto se traduce con `QCoreApplication.translate("<contexto>", ...)`**, con la clase o el
   módulo donde está como contexto, y no con `self.tr()`. Un valor entra con `.format()` después
   de traducir, nunca en un f-string.
6. **`src/app/services/language.py` es canónico y se copia sin editar.** Trae un
   `QT_TRANSLATE_NOOP` que devuelve `str`, para lo que se arma al importar, y `install()`, que
   `main.py` llama antes de crear un widget: aplica el idioma guardado bajo `language.KEY`, o si
   no hay ninguno, el primero de `QLocale.system().uiLanguages()` que tiene traducción, o el base,
   con `QLocale.setDefault()` y los traductores de la app y de Qt.

## Consecuencias

- Una app de Qt nueva no escribe su propia elección de idioma: copia `language.py`, y su selector
  escribe `language.KEY`.
- `verificar.py` compara `language.py` con el de la plantilla, como los `ruff.toml` de `src/`.
- Un texto armado al importar se traduce donde se muestra; si además es una clave, como el grupo
  de un menú, se guarda sin traducir.

## Descartado

- **Extraer con `-extensions py src/app` después de borrar `rc_resources.py`:** obliga a
  regenerarlo antes de correr la app, y un paso olvidado tumba `pyside6-lupdate` solo en Windows.
- **Guardar `rc_resources.py` fuera de `src/app/`:** `qt.md` lo deja junto a `resources.qrc`, y
  `main.py` lo importa como parte del paquete.
- **Un `QT_TRANSLATE_NOOP` envuelto en `cast(str, ...)` en cada llamada:** repite el arreglo en
  cientos de líneas.
- **Que cada app escriba su `language.py`:** la elección del idioma y la marca de los textos son
  las mismas en toda app de Qt.
