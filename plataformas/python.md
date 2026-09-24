# Python

Lo común a toda pieza en Python: `server/`, Flet y Qt. Lo propio de cada una va en su página y se
suma a esto.

## Versión y dependencias

- Python 3.13: `requires-python = ">=3.13"` y `target-version = "py313"`.
- `pyproject.toml` + `uv.lock`, sin `requirements.txt` en paralelo ([ADR-0006](../adr/0006-dependencias-con-pyproject-y-uv.md)).
  CI instala con `uv sync --frozen`.
- Una dependencia que ningún archivo importa se borra del `pyproject.toml`.

## Estilo: PEP 8, hecho cumplir por herramienta

- **`ruff format` da el formato.** Nadie lo ajusta a mano ni lo discute en una revisión; CI corre
  `ruff format --check`.
- **Nombres de PEP 8** (`N`): funciones, variables y módulos en `snake_case`; clases en
  `PascalCase`; constantes en `UPPER_CASE`; una excepción que es un error termina en `Error`.
- Un método que sobrescribe uno de una biblioteca lleva `@override` (`typing`). Es lo que exime de
  `N802` a los nombres en camelCase que impone Qt (`paintEvent`, `rowCount`), y mypy comprueba que
  de verdad sobrescriba algo.
- Un enum de texto hereda de `StrEnum` ([ADR-0013](../adr/0013-un-enum-hereda-de-strenum-y-se-guarda-como-varchar-con-check.md)).

## Imports

- **Siempre absolutos**: `from app.core.enums import Status`, nunca `from ..core.enums import
  Status`. Un import relativo falla al correr el archivo directo y cambia de destino cuando el
  archivo se mueve. `TID252` lo hace cumplir.
- El orden lo pone `ruff` (`I`), no la mano.
- Un import que solo sirve para anotar un tipo y crearía un ciclo va bajo `if TYPE_CHECKING:`.

## `__init__.py`

- **Toda carpeta con código lleva el suyo** (`INP001`). Sin él es un paquete de espacio de nombres
  implícito: mypy y pytest pueden resolver el mismo módulo por dos rutas y quejarse de un duplicado,
  o no encontrarlo.
- **Vacío.** Dos excepciones, y ninguna lleva lógica:
  - Un registro que hay que importar por su efecto: `models/__init__.py` del servidor — ver
    [fastapi.md](fastapi.md).
  - La API pública de un paquete de `packages/`, que reexporta lo que otras piezas usan.

## Tipos

mypy en modo `strict`. Un paquete sin tipos se declara en un `[[tool.mypy.overrides]]` propio con
`ignore_missing_imports = true`, nunca en el bloque global: el global apaga la revisión de cada
import mal escrito.

## Configuración base

```toml
[tool.ruff]
line-length = 120
target-version = "py313"

[tool.ruff.lint]
select = ["E", "W", "F", "I", "N", "UP", "B", "SIM", "ASYNC", "TID", "INP"]

[tool.ruff.lint.flake8-tidy-imports]
ban-relative-imports = "all"

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["INP001"]

[tool.mypy]
python_version = "3.13"
strict = true
```

| Regla | Qué atrapa |
|---|---|
| `E`, `W` | PEP 8: espacios, líneas, sangría |
| `F` | Nombres sin definir, imports sin usar |
| `I` | Orden de los imports |
| `N` | Nombres que no siguen PEP 8 |
| `UP` | Sintaxis vieja de Python. Incluye `UP042`: `StrEnum` en vez de `(str, Enum)` |
| `B` (bugbear) | Argumentos por defecto mutables, `return` dentro de `finally`, variables de lazo capturadas tarde |
| `SIM` | Código que se puede escribir más simple |
| `ASYNC` | Llamadas bloqueantes dentro de una corrutina (`time.sleep`, `open`, `requests`): congelan el event loop |
| `TID252` | Imports relativos |
| `INP001` | Carpetas de código sin `__init__.py` |
| mypy `strict` | Funciones sin tipos, `Any` implícito, `type: ignore` que ya no hace falta |

## CI

```yaml
- run: uv sync --frozen
- run: uv run ruff format --check .
- run: uv run ruff check .
- run: uv run mypy <paquete>
```
