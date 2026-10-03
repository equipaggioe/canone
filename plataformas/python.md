# Python

Lo común a toda pieza en Python. Lo propio de cada una va en su página y se suma a esto.

## Proyecto

Estándares: [*pyproject.toml specification*](../estandares/pypa/pyproject-toml.rst),
[*Dependency Groups*](../estandares/pypa/dependency-groups.rst),
[*Tool recommendations*](../estandares/pypa/tool-recommendations.rst) y
[*pylock.toml specification*](../estandares/pypa/pylock-toml.rst) de PyPA.

- Python 3.13, el de Debian 13: `requires-python = "==3.13.*"`. Toda herramienta que elige la
  versión más alta permitida, como `flet build`, toma 3.13.
- uv maneja el entorno, las dependencias y la ejecución. Contradice *Tool recommendations*, que
  nombra a pip como la herramienta estándar para instalar: un solo programa crea el venv, instala,
  bloquea y ejecuta.
- El bloqueo es `uv.lock`, en git, y se instala con `uv sync --locked`. Contradice el formato
  estándar `pylock.toml`: `uv.lock` es el que uv lee, y el otro sería una copia exportada.
- El backend de construcción es `uv_build`.

Estándar del layout: las [buenas prácticas de pytest](../estandares/pytest/goodpractices.rst).

```text
pyproject.toml
uv.lock
src/app/
  __init__.py
tests/
  __init__.py
```

- El paquete se llama `app` en toda pieza. Los archivos canónicos lo nombran y se copian sin
  editar.

Plantilla: el `pyproject.toml` de cada pieza, en [`plantilla/server/`](../plantilla/server/),
[`plantilla/qt/`](../plantilla/qt/) y [`plantilla/flet/`](../plantilla/flet/),
[`plantilla/python/.gitignore`](../plantilla/python/.gitignore) y los jobs de Python de
[`plantilla/.github/workflows/ci.yml`](../plantilla/.github/workflows/ci.yml). Cada uno lleva la
configuración de esta página más la de su plataforma.

## Estilo

Estándares: [PEP 8](../estandares/python/pep-0008.rst) y
[PEP 257](../estandares/python/pep-0257.rst).

- Líneas de 99 caracteres.
- Comillas dobles.
- ruff formatea y revisa el código.
- Los docstrings son prosa y nombran un argumento solo cuando la firma no basta. Contradice
  PEP 257, que prefiere una línea por argumento: la firma ya da el nombre, el tipo y el valor por
  defecto.

## Tipos

Estándares: los capítulos [*Type annotations*](../estandares/typing/spec/annotations.rst) y
[*Type checker directives*](../estandares/typing/spec/directives.rst) de la especificación de
tipos, [*Typing Best Practices*](../estandares/typing/best_practices.rst) y
[*Modernizing Superseded Typing Features*](../estandares/typing/modernizing.rst).

- Pyrefly en modo strict. Entiende sin plugin los alias que genera `to_camel` y los campos que
  pydantic-settings lee del entorno.
- Toda función va anotada. Endurece la especificación: el verificador puede no revisar el cuerpo
  de una función sin anotar.
- Un error de tipos se ignora con `# pyrefly: ignore[<código>]`. Contradice el `# type: ignore` de
  la especificación: Pyrefly lo aplica a toda la línea sin mirar el código.
- Todo ignore y todo `# noqa` llevan el código del error. Uno sin código también tapa los errores
  futuros de esa línea.

## Paquetes

Estándares: [PEP 420](../estandares/python/pep-0420.rst) y
[PEP 8](../estandares/python/pep-0008.rst).

- Todo directorio de código lleva `__init__.py`. Los paquetes de espacio de nombres sirven para
  repartir un paquete entre distribuciones; en una app, una carpeta sin él es un olvido.
- Los imports son absolutos. Endurece PEP 8, que también acepta los relativos explícitos: una
  sola forma, y la que da mejores errores.

## Logging

Estándar: la [guía de logging](../estandares/python/logging-howto.rst).

- Toda salida pasa por logging. Contradice la guía, que reserva `print` para la salida normal de
  un programa de consola: ni un servidor ni una GUI la tienen.
- Los mensajes pasan sus valores como argumentos `%s`. Endurece la guía: el mensaje se arma solo
  si el nivel está activo.

## Fechas

Estándar: [`datetime`](../estandares/python/datetime.rst).

- Toda `datetime` es aware y en UTC; la hora local aparece solo al mostrarla. Endurece la
  preferencia de la documentación: comparar una naive con una aware lanza `TypeError`, y una
  naive se toma como hora local.

## Archivos de texto

Estándar: la sección *Text Encoding* de [`io`](../estandares/python/io.rst).

- Los archivos de texto son UTF-8.

## Async

Estándares: la [guía de desarrollo con asyncio](../estandares/python/asyncio-dev.rst) y la de
[tareas](../estandares/python/asyncio-task.rst).

- Las tareas concurrentes se lanzan con `TaskGroup`. Endurece la guía de tareas, que lo ofrece
  como alternativa: no pierde tareas ni excepciones.
- Las pruebas de CI corren en el modo de desarrollo de Python. De las cuatro formas de activar el
  modo debug, es la única que además muestra los `ResourceWarning`.

## Pruebas

Estándar: las [buenas prácticas de pytest](../estandares/pytest/goodpractices.rst).

- Las pruebas se escriben con pytest.

## Seguridad

Estándar: las [*Security Considerations*](../estandares/python/security_warnings.rst) de la
biblioteca estándar.

## Dependencias

- pip-audit revisa en CI las vulnerabilidades conocidas de lo bloqueado.
- deptry revisa que cada import esté declarado. Un import que funciona porque otro paquete lo
  trajo se rompe cuando ese paquete cambia.

## Cómo se hace cumplir

| Qué | Con qué |
|---|---|
| Python 3.13 de Debian 13 | `requires-python` y uv con `python-preference = "only-system"` |
| El bloqueo | `uv sync --locked` en CI |
| ruff revisa el código | ruff `F`, que ruff activa por defecto |
| PEP 8 | `ruff format` y ruff `E`, `W` y `N` |
| PEP 8: grupos de imports | ruff `I` |
| PEP 8: docstrings y comentarios a 72 | ruff `W505` con `max-doc-length = 72` |
| PEP 8: `except` sin tipo | ruff `E722` y `BLE` |
| PEP 257 | ruff `D` con `convention = "pep257"` |
| *Modernizing Superseded Typing Features* | ruff `UP` con `target-version = "py313"` |
| Toda función anotada | Pyrefly con `preset = "strict"` |
| `# pyrefly: ignore` | Pyrefly con `enabled-ignores = ["pyrefly"]` |
| `# noqa` con código | ruff `PGH004` |
| `__init__.py` | ruff `INP` |
| Imports absolutos | ruff `TID252` con `ban-relative-imports = "all"` |
| Toda salida por logging | ruff `T20` |
| Argumentos `%s` en los mensajes | ruff `G` |
| Fechas aware | ruff `DTZ` |
| Guía de asyncio: código que bloquea | ruff `ASYNC` |
| Guía de tareas: guardar la referencia | ruff `RUF006` |
| Pruebas en modo de desarrollo | `PYTHONDEVMODE=1` en el paso de pytest de CI |
| Archivos de texto UTF-8 | `PYTHONWARNDEFAULTENCODING=1` en el paso de pytest de CI y `error::EncodingWarning` en `filterwarnings` |
| Buenas prácticas de pytest | `--import-mode=importlib` en `addopts` |
| *Security Considerations*: `hashlib` | ruff `S324` |
| *Security Considerations*: `logging` | ruff `S612` |
| *Security Considerations*: `ssl` | ruff `S323`, `S502`, `S503` y `S504` |
| *Security Considerations*: `tempfile` | ruff `S306` |
| Vulnerabilidades | pip-audit |
| Imports declarados | deptry |
