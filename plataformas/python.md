# Python

Lo común a toda pieza en Python: `server/`, Flet y Qt. Lo propio de cada una va en su página y se
suma a esto.

## Proyecto

Estándares: [*pyproject.toml specification*](../estandares/pypa/pyproject-toml.rst) y
[*Dependency Groups*](../estandares/pypa/dependency-groups.rst) de PyPA.

- Python 3.13, el del sistema (Debian 13).
- Las dependencias se instalan con `uv` y se bloquean en `uv.lock`, que siempre corresponde al
  `pyproject.toml`.
- Las herramientas de desarrollo van en el grupo `dev`.
- Una dependencia que nada usa se borra.
- Ninguna dependencia, directa o transitiva, con una vulnerabilidad publicada.

## Estilo

Estándares: [PEP 8](../estandares/python/pep-0008.rst),
[PEP 257](../estandares/python/pep-0257.rst) y [PEP 498](../estandares/python/pep-0498.rst).

- El formato de Black.
- Líneas de 99 caracteres.
- Imports absolutos, en el orden de isort dentro de cada grupo.
- El texto se arma con f-strings.
- `except Exception` solo para registrar el traceback, o para limpiar y relanzar: en cualquier otro
  caso esconde el error.
- Un `except` registra, traduce o relanza el error.
- Un `# noqa` lleva el código de la regla que calla.

## Tipos

Estándares: [PEP 484](../estandares/python/pep-0484.rst),
[PEP 604](../estandares/python/pep-0604.rst), [PEP 695](../estandares/python/pep-0695.rst),
[PEP 698](../estandares/python/pep-0698.rst) y [`enum`](../estandares/python/enum.rst).

- Toda función y todo genérico con sus tipos completos: un parámetro sin anotar es `Any`, y mypy
  no revisa lo que pasa por él.
- Uniones con `X | Y`. Genéricos y alias con la sintaxis de PEP 695: `class Box[T]`,
  `type Pair = ...`.
- `@override` en todo método que sobrescribe otro: si la clase base lo renombra o lo borra, mypy lo
  marca.
- Un import que solo lee mypy y crearía un ciclo va bajo `if TYPE_CHECKING:`.
- Un `# type: ignore` lleva el código del error que calla.
- Un enum de texto hereda de `StrEnum`.

## Paquetes y tests

Estándares: [PEP 420](../estandares/python/pep-0420.rst) y
[*Good Integration Practices*](../estandares/pytest/goodpractices.rst) de pytest.

- Toda carpeta con código es un paquete regular, con su `__init__.py` vacío. Solo dos llevan código:
  el de un registro que se importa por su efecto, y el de un paquete de `packages/`, que reexporta
  su API pública.
- Los tests van en `tests/`, fuera del código y sin `__init__.py`.

## Logging

Estándar: la [guía de logging](../estandares/python/logging-howto.rst).

- Todo mensaje sale por `logging`.
- Cada módulo registra en `logging.getLogger(__name__)`: así cada mensaje dice de qué módulo sale.
- El nivel, el formato y los handlers se configuran una sola vez, en el punto de entrada.
- Los argumentos del mensaje van como parámetros del logger: se formatean solo si el mensaje se
  emite.
- Dentro de un `except`, `logger.exception(...)`.

## Fechas

Estándar: [`datetime`](../estandares/python/datetime.rst).

- Siempre con zona horaria: una fecha sin zona no dice a qué instante corresponde.

## Async

Estándares: la [guía de desarrollo con asyncio](../estandares/python/asyncio-dev.rst) y la de
[tareas](../estandares/python/asyncio-task.rst).

- El código bloqueante va en `asyncio.to_thread`.

## Cómo se hace cumplir

| Convención | Con qué |
|---|---|
| Python 3.13 | `requires-python`, que lee ruff (sin `target-version`), y `python_version` en `[tool.mypy]` |
| Python del sistema | `python-preference = "only-system"` |
| `uv.lock` al día | `uv sync --locked` en CI |
| Dependencias sin usar | `deptry` en CI |
| Vulnerabilidades | `pip-audit` sobre el lock, en CI |
| [PEP 8](../estandares/python/pep-0008.rst) | `E`, `W` (con `max-doc-length = 72`), `N` |
| Formato de Black | `ruff format --check` |
| Imports absolutos | `TID252` |
| Orden de isort | `I` |
| f-strings | `UP031`, `UP032` |
| `except Exception` y `except` sin tratar el error | `BLE`, `S110` |
| `# noqa` con código | `PGH004` |
| [PEP 257](../estandares/python/pep-0257.rst) | `D` con `convention = "pep257"`, sin `D1` |
| Funciones anotadas | mypy `strict` |
| [PEP 585](../estandares/python/pep-0585.rst) | `UP006`, `UP035` |
| Uniones, genéricos y alias | `UP007`, `UP040`, `UP045`, `UP046`, `UP047` |
| `@override` | mypy `explicit-override` |
| `# type: ignore` con código | mypy `ignore-without-code` |
| `StrEnum` | `UP` |
| Paquetes regulares | `INP001`, apagada en `tests/` |
| [pytest, modo `importlib`](../estandares/pytest/goodpractices.rst) | `--import-mode=importlib` |
| Logging | `G`, `LOG`, `T20` |
| Fechas con zona | `DTZ` |
| [asyncio, *Running Blocking Code*](../estandares/python/asyncio-dev.rst) | `ASYNC` |
| [asyncio, referencia a las tareas de `create_task`](../estandares/python/asyncio-task.rst) | `RUF006` |
| Sin convención propia | `F`, `B`, `SIM`, `RUF` |

### Configuración

La base está en [`plantilla/python/pyproject.toml`](../plantilla/python/pyproject.toml).

- Un paquete sin tipos va en su propio `[[tool.mypy.overrides]]`.
- Una dependencia que se usa sin importarse va en `[tool.deptry.per_rule_ignores]`, con el motivo
  en un comentario.

### CI

Los pasos están en el job de cada pieza de
[`plantilla/.github/workflows/ci.yml`](../plantilla/.github/workflows/ci.yml).
