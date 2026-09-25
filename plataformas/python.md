# Python

Lo común a toda pieza en Python: `server/`, Flet y Qt. Lo propio de cada una va en su página y se
suma a esto.

## Versión y dependencias

- Python 3.13, el del sistema (Debian 13). Nunca uno descargado por `uv`.
- `pyproject.toml` (PEP 621) + `uv.lock`, sin `requirements.txt`. El lock siempre corresponde al
  `pyproject.toml`.
- Una dependencia que nada usa se borra.
- Ninguna dependencia, directa o transitiva, con una vulnerabilidad publicada.

## Estilo

Estándares: PEP 8, PEP 257 y PEP 498.

Sobre PEP 8:

- El formato de Black.
- Líneas de 99 caracteres.
- Imports siempre absolutos y, dentro de cada bloque, en el orden de isort.
- Las constantes de módulo en `UPPER_CASE`.
- Un método que sobrescribe uno de una biblioteca conserva el nombre que esta le impone, aunque no
  sea `snake_case`.
- Se atrapa la excepción que se espera, nunca `except Exception`. Un `except` no termina en `pass`.

Sobre PEP 498:

- Siempre f-strings, nunca `%` ni `.format()`.

Un `# noqa` lleva el código de la regla que calla.

## Tipos

Estándares: PEP 484, PEP 585, PEP 604, PEP 695 y PEP 698.

Sobre PEP 484:

- Toda función anotada y nada de `Any` implícito.
- Un import que solo anota un tipo y crearía un ciclo va bajo `if TYPE_CHECKING:`. Nunca en un
  schema de Pydantic ni en los parámetros de un endpoint o una dependencia de FastAPI.
- Un `# type: ignore` lleva el código del error que calla.

Sobre PEP 585, PEP 604 y PEP 695:

- Siempre su sintaxis: `list[int]`, `X | None`, `class Box[T]`. Nunca `typing.List`, `Optional`,
  `Union`, `TypeVar` ni `Generic`.

Sobre PEP 698:

- Un método que sobrescribe uno de una biblioteca lleva `@override`.

Un enum de texto hereda de `StrEnum`.

## Paquetes

- Toda carpeta con código lleva su `__init__.py`, vacío. Dos excepciones:
  - El de un registro que hay que importar por su efecto.
  - El de un paquete de `packages/`, que reexporta su API pública.
- `tests/` no lleva `__init__.py`. Lo que comparten varios tests va en `conftest.py`.

## Logging

- Cada módulo que registra algo declara `logger = logging.getLogger(__name__)`. Nada va al logger
  raíz.
- El nivel, el formato y el destino se configuran una sola vez, en el punto de entrada. Un módulo no
  agrega handlers.
- Los argumentos van aparte, nunca en un f-string.
- Dentro de un `except`, `logger.exception(...)`.
- Nada de `print`.

## Fechas

Siempre con zona horaria.

## Async

- Nada bloqueante dentro de una corrutina: va en `asyncio.to_thread`.
- La tarea de `asyncio.create_task` se guarda en una referencia que vive mientras corre, o se
  lanza desde un `asyncio.TaskGroup`.

## Cómo se hace cumplir

| Convención | Con qué |
|---|---|
| Versión | `requires-python`, que lee ruff (sin `target-version`), y `python_version` en `[tool.mypy]` |
| Python del sistema | `python-preference = "only-system"` |
| Lock | `uv sync --locked` en CI |
| Dependencias sin usar | `deptry` en CI |
| Vulnerabilidades | `pip-audit` sobre el lock, en CI |
| PEP 8 | `E`, `W` (con `max-doc-length = 72`), `N` |
| Formato de Black | `ruff format --check` |
| PEP 257 | `D` con `convention = "pep257"`, sin `D1` |
| PEP 498 | `UP031`, `UP032` |
| Imports absolutos | `TID252` |
| Orden de los imports | `I` |
| Errores | `BLE`, `S110` |
| `# noqa` con código | `PGH004` |
| Tipos | mypy `strict` |
| PEP 585, PEP 604 y PEP 695 | `UP006`, `UP007`, `UP035`, `UP040`, `UP045`, `UP046`, `UP047` |
| `@override` | mypy `explicit-override` |
| `# type: ignore` con código | mypy `ignore-without-code` |
| `StrEnum` | `UP` |
| Logging | `G`, `LOG`, `T20` |
| Fechas | `DTZ` |
| Async | `ASYNC`, `RUF006` |
| `__init__.py` | `INP001`, apagada en `tests/`, y pytest con `--import-mode=importlib` |
| Sin convención propia | `F`, `B`, `SIM`, `RUF` |

### Configuración

La base está en [`plantilla/python/pyproject.toml`](../plantilla/python/pyproject.toml).

- Un paquete sin tipos va en su propio `[[tool.mypy.overrides]]`, nunca en el bloque global.
- Una dependencia que se usa sin importarse va en `[tool.deptry.per_rule_ignores]`, con el motivo
  en un comentario.
- `ruff`, `mypy`, `pytest`, `deptry` y `pip-audit` van en el grupo `dev` de
  `[dependency-groups]`.

### CI

Los pasos están en el job de cada pieza de
[`plantilla/.github/workflows/ci.yml`](../plantilla/.github/workflows/ci.yml).
