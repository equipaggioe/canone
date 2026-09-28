# Python

Lo común a toda pieza en Python. Lo propio de cada una va en su página y se suma a esto.

## Proyecto

Estándares: [*pyproject.toml specification*](../estandares/pypa/pyproject-toml.rst),
[*Dependency Groups*](../estandares/pypa/dependency-groups.rst),
[*Tool recommendations*](../estandares/pypa/tool-recommendations.rst) y
[*pylock.toml specification*](../estandares/pypa/pylock-toml.rst) de PyPA.

- Python 3.13, el de Debian 13: `requires-python = "==3.13.*"`. Toda herramienta que elige la
  versión más alta permitida, como `flet build`, toma 3.13.
- uv maneja el entorno, las dependencias y la ejecución. Un solo programa crea el venv, instala,
  bloquea y ejecuta.
- El bloqueo es `uv.lock`, en git, y se instala con `uv sync --locked`. Contradice el formato
  estándar `pylock.toml`: `uv.lock` es el que uv lee, y el otro sería una copia exportada.
- El backend de construcción es `uv_build`.

## Estilo

Estándares: [PEP 8](../estandares/python/pep-0008.rst) y
[PEP 257](../estandares/python/pep-0257.rst).

- Líneas de 99 caracteres.
- Comillas dobles.
- ruff formatea y revisa el código.
- Los docstrings describen los argumentos en prosa, porque los tipos ya van en las anotaciones.

## Tipos

Estándares: [PEP 484](../estandares/python/pep-0484.rst),
[*Typing Best Practices*](../estandares/typing/best_practices.rst) y
[*Modernizing Superseded Typing Features*](../estandares/typing/modernizing.rst).

- mypy en modo strict. Es el verificador de referencia de la documentación de typing, y Pydantic
  trae un plugin para él.
- Toda función va anotada. Endurece PEP 484: el verificador no revisa una función sin anotar.
- Todo `# type: ignore` y todo `# noqa` llevan el código del error. Uno sin código también tapa
  los errores futuros de esa línea.

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

## Async

Estándares: la [guía de desarrollo con asyncio](../estandares/python/asyncio-dev.rst) y la de
[tareas](../estandares/python/asyncio-task.rst).

- Las tareas concurrentes se lanzan con `TaskGroup`. Guarda la referencia de cada tarea y las
  espera y cancela juntas.
- En desarrollo, Python corre con `-X dev`. Avisa de corrutinas sin `await`, llamadas que
  bloquean más de 100 ms y recursos sin cerrar.

## Pruebas

Estándar: las [buenas prácticas de pytest](../estandares/pytest/goodpractices.rst).

- Las pruebas se escriben con pytest.

## Dependencias

- pip-audit revisa en CI las vulnerabilidades conocidas de lo bloqueado.
- deptry revisa que cada import esté declarado. Un import que funciona porque otro paquete lo
  trajo se rompe cuando ese paquete cambia.

## Cómo se hace cumplir

| Qué | Con qué |
|---|---|
| El bloqueo | `uv sync --locked` en CI |
| PEP 8 | `ruff format` y ruff `E`, `W` y `N` |
| PEP 8: docstrings y comentarios a 72 | ruff `W505` con `max-doc-length = 72` |
| PEP 8: `except` sin tipo | ruff `E722` y `BLE` |
| PEP 257 | ruff `D` con `convention = "pep257"` |
| *Modernizing Superseded Typing Features* | ruff `UP` con `target-version = "py313"` |
| Toda función anotada | `mypy --strict` |
| Ignores con código | ruff `PGH004` y mypy `ignore-without-code` |
| `__init__.py` | ruff `INP` |
| Imports absolutos | ruff `TID252` con `ban-relative-imports = "all"` |
| Toda salida por logging | ruff `T20` |
| Argumentos `%s` en los mensajes | ruff `G` |
| Fechas aware | ruff `DTZ` |
| Guía de asyncio: código que bloquea | ruff `ASYNC` |
| Guía de tareas: guardar la referencia | ruff `RUF006` |
| Buenas prácticas de pytest | `--import-mode=importlib` en `addopts` |
| Vulnerabilidades | pip-audit |
| Imports declarados | deptry |
