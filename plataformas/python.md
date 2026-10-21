# Python

Lo común a toda pieza en Python. Lo propio de cada una va en su página y se suma a esto.

## Proyecto

Estándares: [*pyproject.toml specification*](../fuentes/pypa/pyproject-toml.rst) y
[*Dependency Groups*](../fuentes/pypa/dependency-groups.rst) de PyPA.

- Python 3.13, el de Debian 13: `requires-python = "==3.13.*"`. Toda herramienta que elige la
  versión más alta permitida, como `flet build`, toma 3.13.
- uv maneja el entorno, las dependencias y la ejecución: un solo programa crea el venv, instala,
  bloquea y ejecuta.
- El bloqueo es `uv.lock`, en git, y se instala con `uv sync --locked`.
- El backend de construcción es `uv_build`.

Estándar del layout: la sección *Choosing a test layout* de las
[buenas prácticas de pytest](../fuentes/pytest/goodpractices.rst).

```text
<pieza>/
  .gitignore
  pyproject.toml
  uv.lock
  src/app/
    __init__.py
  tests/
    __init__.py
    test_<módulo>.py
```

- El paquete se llama `app` en toda pieza. Los archivos canónicos lo nombran y se copian sin
  editar.

Plantilla: el `pyproject.toml` de cada pieza, en [`plantilla/server/`](../plantilla/server/),
[`plantilla/qt/`](../plantilla/qt/) y [`plantilla/flet/`](../plantilla/flet/),
[`plantilla/python/.gitignore`](../plantilla/python/.gitignore) y los jobs de Python de
[`plantilla/.github/workflows/ci.yml`](../plantilla/.github/workflows/ci.yml). Cada uno lleva la
configuración de esta página más la de su plataforma.

## Dependencias

- Ninguna dependencia bloqueada tiene una vulnerabilidad conocida.
- Una vulnerabilidad se ignora solo por su identificador, con `--ignore-vuln`. Sacar el paquete
  del análisis también tapa sus vulnerabilidades futuras.
- Todo paquete que el código importa está declarado en `pyproject.toml`, aunque otro paquete ya
  lo traiga. Un import que funciona porque otro paquete lo trajo se rompe cuando ese paquete
  cambia.
- Toda dependencia declarada se usa.

## Estilo

Estándares: [PEP 8](../fuentes/python/pep-0008.rst), salvo la sección *Imports*, y
[PEP 257](../fuentes/python/pep-0257.rst).

- Líneas de 99 caracteres.
- Comillas dobles.
- El código se formatea con `ruff format`.
- El código cumple las reglas `F` de ruff: marcan nombres sin definir, e imports y variables sin
  usar.
- Los docstrings son prosa y nombran un argumento solo cuando la firma no basta. Contradice
  PEP 257, que prefiere una línea por argumento: la firma ya da el nombre, el tipo y el valor por
  defecto.

## Tipos

Estándares: las secciones *Ergonomic Practices* y *Types* de
[*Typing Best Practices*](../fuentes/typing/best_practices.rst) y
[*Modernizing Superseded Typing Features*](../fuentes/typing/modernizing.rst).

- Pyrefly en modo strict. Entiende sin plugin los alias que genera `to_camel` y los campos que
  pydantic-settings lee del entorno.
- Toda función va anotada: el verificador puede no revisar el cuerpo de una función sin anotar.
- Un error de tipos se ignora con `# pyrefly: ignore[<código>]`: Pyrefly aplica `# type: ignore` a
  toda la línea sin mirar el código.
- Todo ignore y todo `# noqa` llevan el código del error. Uno sin código también tapa los errores
  futuros de esa línea.

## Paquetes

Estándar: la sección *Imports* de [PEP 8](../fuentes/python/pep-0008.rst).

- Todo directorio de código lleva `__init__.py`: sin él, la carpeta se vuelve en silencio un
  paquete de espacio de nombres.
- Los imports son absolutos. Endurece PEP 8, que también acepta los relativos explícitos: una
  sola forma, y la que da mejores errores.
- En cada grupo de imports, los `import` van antes que los `from`, y unos y otros en orden
  alfabético del módulo.
- Los nombres de un `from` van en orden alfabético: primero las constantes, después las clases
  y al final lo demás.
- Los nombres de un mismo módulo se importan en un solo `from`.

## Archivos de texto

Estándar: la sección *Text Encoding* de [`io`](../fuentes/python/io.rst).

- Los archivos de texto se abren con `encoding="utf-8"`.

## Async

Estándar: las secciones *Concurrency and Multithreading*, *Running Blocking Code* y
*Asynchronous generators best practices* de la
[guía de desarrollo con asyncio](../fuentes/python/asyncio-dev.rst).

- Las tareas concurrentes se lanzan con `TaskGroup`, salvo una tarea que tiene que vivir más que
  la función que la lanza: no pierde tareas ni excepciones.
- Una tarea creada fuera de un `TaskGroup` guarda su referencia: el bucle de eventos solo guarda
  una referencia débil, y la tarea puede desaparecer antes de terminar.
- Las pruebas de CI corren en el modo de desarrollo de Python: activa el modo debug de asyncio y
  además muestra los `ResourceWarning`.

## Fechas

- Toda `datetime` es aware y en UTC, y la fecha de hoy sale de una de ellas; la hora local aparece
  solo al mostrarla: comparar una naive con una aware lanza `TypeError`, y una naive se toma como
  hora local.

## Logging

- Toda salida pasa por logging: ni un servidor ni una GUI tienen una consola que alguien lea.
- Los mensajes pasan sus valores como argumentos `%s`: el mensaje se arma solo si el nivel está
  activo.

## Seguridad

- Un archivo temporal se crea con `tempfile.mkstemp` o `NamedTemporaryFile`, nunca con `mktemp`:
  entre elegir el nombre y abrirlo, otro proceso puede crear el archivo.
- Una conexión TLS usa el contexto de `ssl.create_default_context()`, sin desactivar la
  verificación ni bajar la versión del protocolo: verifica el certificado y el nombre del
  servidor, y rechaza los protocolos inseguros.
- MD5 y SHA-1 se usan solo con `usedforsecurity=False`: están rotos como protección.
- Un token, una clave o cualquier valor que protege algo sale de `secrets`, nunca de `random`:
  la secuencia de `random` se puede predecir.
- No se usa `logging.config.listen`: ejecuta la configuración que recibe por la red.

## Pruebas

Estándar: la sección *Using pytest's strict mode* de las
[buenas prácticas de pytest](../fuentes/pytest/goodpractices.rst).

- Las pruebas se escriben con pytest: un `assert` simple muestra los valores que fallaron, y los
  fixtures reemplazan a `setUp`.
- Las pruebas cumplen las reglas `PT` de ruff: marcan el mal uso de fixtures, marcadores y
  `pytest.raises`.

## Cómo se hace cumplir

| Qué | Con qué |
|---|---|
| Python 3.13 de Debian 13 | `requires-python` y uv con `python-preference = "only-system"` |
| El bloqueo | `uv sync --locked` en CI |
| PEP 8 | `ruff format` y ruff `E`, `W`, `N`, `BLE` y `UP009`, con `max-doc-length = 72` |
| Reglas `F` | ruff `F` |
| Orden de los imports | ruff `I` |
| PEP 257 | ruff `D` con `convention = "pep257"` |
| *Modernizing Superseded Typing Features* | ruff `UP006`, `UP007`, `UP013`, `UP019`, `UP035`, `UP040`, `UP045` y `UP046` con `target-version = "py313"`, y `PYI050` y `PYI057` |
| Pyrefly en modo strict | `preset = "strict"` |
| Toda función anotada | Pyrefly con `preset = "strict"` y `unannotated-return = "error"` |
| `# pyrefly: ignore` | Pyrefly con `enabled-ignores = ["pyrefly"]` |
| `# noqa` con código | ruff `PGH004` |
| `__init__.py` | ruff `INP` |
| Imports absolutos | ruff `TID252` con `ban-relative-imports = "all"` |
| Toda salida por logging | ruff `T20` |
| Argumentos `%s` en los mensajes | ruff `G00` |
| Fechas aware | ruff `DTZ` |
| *Running Blocking Code*: llamadas que bloquean | ruff `ASYNC2` |
| Referencia de las tareas fuera de un `TaskGroup` | ruff `RUF006` |
| Pruebas en modo de desarrollo | `PYTHONDEVMODE=1` en el paso de pytest de CI |
| *Text Encoding*: codificación explícita | `PYTHONWARNDEFAULTENCODING=1` en el paso de pytest de CI y `error::EncodingWarning` en `filterwarnings` |
| Reglas `PT` | ruff `PT` |
| *Using pytest's strict mode* | `strict = true` |
| Sin `mktemp` | ruff `S306` |
| Contexto TLS por defecto | ruff `S323`, `S501`, `S502` y `S503` |
| MD5 y SHA-1 | ruff `S324` |
| Sin `logging.config.listen` | ruff `S612` |
| Vulnerabilidades | pip-audit |
| Imports declarados y dependencias usadas | deptry |
