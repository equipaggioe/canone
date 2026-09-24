# Python

Lo común a toda pieza en Python: `server/`, Flet y Qt. Lo propio de cada una va en su página y se
suma a esto.

## Versión y dependencias

- Python 3.13, la que trae Debian 13: `requires-python = ">=3.13"`. `ruff` la lee de ahí, así que
  no se repite en `target-version`. mypy no la lee: sin `python_version` revisa contra el intérprete
  que lo corre, que puede ser más nuevo. Por eso se repite en `[tool.mypy]`.
- `uv` usa solo el Python del sistema (`python-preference = "only-system"`). Si en la máquina hay un
  Python descargado por `uv`, lo preferiría, y ese no recibe los parches de seguridad de `apt`.
- `pyproject.toml` + `uv.lock`, sin `requirements.txt` en paralelo ([ADR-0006](../adr/0006-dependencias-con-pyproject-y-uv.md)).
  CI instala con `uv sync --locked`, que falla si el lock no corresponde al `pyproject.toml`.
  `--frozen` no lo comprueba: instala el lock viejo y termina bien.
- Una dependencia que nada usa se borra del `pyproject.toml`. `deptry` lo comprueba en CI. La que se
  usa sin importarse (el servidor que arranca la unidad, el driver que nombra la URL de la base) va
  en `[tool.deptry.per_rule_ignores]`, con el motivo en un comentario.
- Ninguna dependencia, directa o transitiva, con una vulnerabilidad publicada. `pip-audit` revisa el
  lock en CI contra la base de vulnerabilidades de PyPI.

## Estilo: PEP 8, hecho cumplir por herramienta

- **`ruff format` da el formato.** Nadie lo ajusta a mano ni lo discute en una revisión; CI corre
  `ruff format --check`.
- **Líneas de 99 caracteres; comentarios y docstrings de 72** (`E501`, `W505`). Es el máximo que
  PEP 8 admite cuando un equipo lo acuerda, y lo condiciona a esos 72. `ruff format` corta el
  código, pero no los comentarios: esos se parten a mano.
- **Nombres de PEP 8** (`N`): funciones, variables y módulos en `snake_case`; clases en
  `PascalCase`; constantes en `UPPER_CASE`; una excepción que es un error termina en `Error`.
- Un método que sobrescribe uno de una biblioteca lleva `@override` (`typing`). Es lo que exime de
  `N802` a los nombres en camelCase que impone Qt (`paintEvent`, `rowCount`). mypy exige que esté
  (`explicit-override`) y que de verdad sobrescriba algo.
- Un enum de texto hereda de `StrEnum` ([ADR-0013](../adr/0013-un-enum-hereda-de-strenum-y-se-guarda-como-varchar-con-check.md)).

## Imports

- **Siempre absolutos**: `from app.core.enums import Status`, nunca `from ..core.enums import
  Status`. Un import relativo falla al correr el archivo directo y cambia de destino cuando el
  archivo se mueve. `TID252` lo hace cumplir.
- El orden lo pone `ruff` (`I`), no la mano.
- Un import que solo sirve para anotar un tipo y crearía un ciclo va bajo `if TYPE_CHECKING:`.
  **Nunca en un schema de Pydantic ni en los parámetros de un endpoint o una dependencia de
  FastAPI:** leen las anotaciones al correr, y el tipo que no se importó hace fallar el modelo.

## Logging

- Cada módulo que registra algo declara `logger = logging.getLogger(__name__)`. Ninguna regla lo
  exige, así que se revisa a mano: `LOG002` solo atrapa `getLogger(__file__)`. Nada va al logger
  raíz con `logging.info(...)` (`LOG015`): la línea pierde el módulo que la emitió.
- El nivel, el formato y el destino se configuran una sola vez, en el punto de entrada. Un módulo no
  agrega handlers: cada handler de más imprime la misma línea otra vez.
- Los argumentos van aparte, nunca en un f-string: `logger.info("usuario %s entró", user_id)`
  (`G004`). El f-string se arma aunque ese nivel esté apagado.
- Dentro de un `except`, `logger.exception(...)`, que adjunta la traza (`G201`).

## `__init__.py`

- **Toda carpeta con código lleva el suyo** (`INP001`). Sin él es un paquete de espacio de nombres
  implícito: mypy y pytest pueden resolver el mismo módulo por dos rutas y quejarse de un duplicado,
  o no encontrarlo.
- `tests/` es la excepción: no lleva `__init__.py`, y pytest corre con `--import-mode=importlib`.
  Con el modo por defecto, dos tests con el mismo nombre en carpetas distintas
  (`tests/a/test_x.py`, `tests/b/test_x.py`) detienen la colección con "import file mismatch".
  El costo: con `importlib`, un módulo auxiliar suelto en `tests/` no se puede importar. Lo que
  comparten varios tests va en `conftest.py`, como fixture.
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
line-length = 99

[tool.ruff.lint]
select = ["E", "W", "F", "I", "N", "UP", "B", "SIM", "ASYNC", "TID", "INP", "RUF", "DTZ", "BLE", "S110",
          "PGH004", "T20", "G", "LOG"]
# La raya corta es puntuación del español, no un guion confundido.
allowed-confusables = ["–"]

[tool.ruff.lint.pycodestyle]
max-doc-length = 72

[tool.ruff.lint.flake8-tidy-imports]
ban-relative-imports = "all"

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["INP001"]

[tool.mypy]
python_version = "3.13"
strict = true
enable_error_code = ["explicit-override", "ignore-without-code"]

[tool.pytest.ini_options]
addopts = ["--import-mode=importlib"]

[tool.uv]
python-preference = "only-system"
```

| Regla | Qué atrapa |
|---|---|
| `E`, `W` | Lo de PEP 8 que el formateador no arregla: `== None`, `except:` pelado, un `lambda` asignado a un nombre, nombres ambiguos (`l`, `O`, `I`), escapes inválidos en un string, líneas y comentarios largos. Los espacios y la sangría los pone `ruff format`: las reglas `E1`, `E2` y `E3` de ruff están en preview y `E` no las activa |
| `F` | Nombres sin definir, imports sin usar |
| `I` | Orden de los imports |
| `N` | Nombres que no siguen PEP 8 |
| `UP` | Sintaxis vieja de Python. Incluye `UP042`: `StrEnum` en vez de `(str, Enum)` |
| `B` (bugbear) | Argumentos por defecto mutables, `return` dentro de `finally`, variables de lazo capturadas tarde |
| `SIM` | Código que se puede escribir más simple |
| `ASYNC` | Llamadas bloqueantes dentro de una corrutina (`time.sleep`, `open`, `requests`): congelan el event loop |
| `TID252` | Imports relativos |
| `INP001` | Carpetas de código sin `__init__.py` |
| `RUF` | Las reglas propias de ruff. Entre ellas `RUF006`: `asyncio.create_task` sin guardar la tarea, que el recolector de basura puede cortar a medias |
| `DTZ` | Fechas sin zona horaria: `datetime.now()`, `datetime.utcnow()` |
| `BLE` | `except Exception` genérico, que se traga errores que nadie esperaba |
| `S110` | `try`-`except`-`pass`: un error que desaparece sin dejar rastro |
| `PGH004` | Un `# noqa` sin código de regla, que calla todas las reglas de la línea |
| `T20` | Un `print` que quedó en el código. Lo que el programa tiene que contar va por `logging` |
| `G`, `LOG` | Un log mal escrito: f-string, logger raíz, `getLogger(__file__)`, `error(..., exc_info=True)` en vez de `exception` |
| mypy `strict` | Funciones sin tipos, `Any` implícito, `type: ignore` que ya no hace falta |
| mypy `explicit-override` | Un método que sobrescribe sin `@override` |
| mypy `ignore-without-code` | Un `type: ignore` sin el código del error que calla |

## CI

```yaml
- run: uv sync --locked
- run: uv run ruff format --check .
- run: uv run ruff check .
- run: uv run mypy <paquete>
- run: uv run deptry .
- run: uv export --format requirements-txt --locked -o "$RUNNER_TEMP/audit.txt"
- run: uv run pip-audit -r "$RUNNER_TEMP/audit.txt" --require-hashes --disable-pip
```

`deptry` y `pip-audit` van en el grupo `dev` de `[dependency-groups]`, con `ruff`, `mypy` y
`pytest`. El archivo que exporta `uv` vive solo durante el job, fuera del repositorio.
