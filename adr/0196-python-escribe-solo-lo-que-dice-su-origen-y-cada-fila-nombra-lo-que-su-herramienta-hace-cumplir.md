# ADR-0196 · `python.md` escribe solo lo que dice su origen, y cada fila de Cumplimiento nombra lo que su herramienta hace cumplir

- **Estado:** Aceptada
- **Fecha:** 2026-11-19
- **Alcance:** [plataformas/python.md](../plataformas/python.md), «Estilo» y «Cumplimiento» de [plataformas/fastapi.md](../plataformas/fastapi.md), «Pruebas» de [plataformas/flet.md](../plataformas/flet.md), el `pyproject.toml` de `plantilla/server/`, `plantilla/qt/` y `plantilla/flet/`, y `scripts/verificar.py`

## Contexto

Se revisó `python.md` con los cinco pasos de [plataformas/README.md](../plataformas/README.md#revisión). Cada fila de «Cumplimiento» se probó con un caso que rompe su convención, con ruff 0.17.5, Pyrefly 1.4.1, pytest 9.2.0, deptry 0.25.1, pip-audit 2.10.1, uv 0.13.9 y Python 3.13, en Windows y en Debian 13. Los dos dieron lo mismo.

- `E501` y `W505` no marcan una línea que termina en una URL, y `W505` no marca un comentario en línea.
- `UP009` no marca `# -*- coding: latin-1 -*-`; un archivo que no es UTF-8 da `E902`.
- `E721` acepta `type(x) is int`. `D403` solo mira funciones. `UP006` y `UP035` no marcan `typing.Mapping` usado como atributo. `UP040` no marca `Bare = list[int]`. `N999` no marca una carpeta de paquete en CapWords. `DTZ` no marca `replace(tzinfo=None)`.
- `RET501` marca `return None` en una función que solo devuelve `None`: es la otra mitad de la misma frase de PEP 8, y la página no la escribía.
- `D` con `convention = "pep257"` activa `D412` y `D414`, reglas de secciones que PEP 257 no tiene.
- `ruff format --check` ya falla con un tabulador, una sentencia compuesta y un punto y coma: `W191`, `E101` y `E701` a `E703` no marcan nada más. `W291` y `W293` sí: marcan espacios dentro de una cadena, que el formateador no toca.
- `pytest.toml`, `.pytest.toml`, `pytest.ini` y `.pytest.ini`, aunque solo tengan `[pytest]`, le ganan a `pyproject.toml` y apagan `strict = true`. `tox.ini` y `setup.cfg`, no.
- `models/ruff.toml` del servidor deja pasar cualquier línea de hasta 320 caracteres, no solo las columnas.
- 10 repositorios llaman a `subprocess` desde una pieza, y tres piezas usan `shell=True`. `S602` y `S605` marcan `subprocess` con `shell=True`, `os.system` y `os.popen`; no marcan `asyncio.create_subprocess_shell`.
- En los repositorios hay `os.path` 231 veces, en 8 de ellos, y `pathlib` en 15; 6199 f-strings, 10 cadenas con `%` y 7 con `format()`.
- Pyrefly oculta los avisos y sale con 0: una llamada a algo `@deprecated` pasa el CI. La plantilla del servidor no tiene ninguna, y la de Flet tampoco. Con `filterwarnings = ["error"]`, las 95 pruebas de la plantilla del servidor pasan, en Debian 13 con PostgreSQL y Valkey. Las pruebas de Qt y de Flet no se pudieron correr fuera de un repositorio.
- `UP031` y `UP032` no marcan el `%s` de logging, ni un `format()` con `**` o con un argumento entre corchetes. `PTH201` y `PTH210` son reglas de `pathlib` que no tratan de elegirlo.
- `requires-python` con `==` es lo que fija la serie en una app de Flet: con `flet build apk` de Flet 1.1.2, `==3.13.*` empaqueta `libpython3.13.so` y `>=3.13` empaqueta `libpython3.14.so`. La razón salió de `python.md` porque no se aparta de nada.
- Las razones que son un hecho se comprobaron: una carpeta sin `__init__.py` se importa como paquete de espacio de nombres, una tarea sin referencia se borra con `gc`, comparar una naive con una aware lanza `TypeError`, `mktemp` no crea el archivo, `logging.config.listen` ejecutó un `os.makedirs` que recibió, y 624 salidas de `random` predicen las siguientes.

## Decisión

1. Ninguna pieza tiene `requirements.txt`, `pytest.ini`, `.pytest.ini`, `pytest.toml` ni `.pytest.toml`. `verificar.py` lo comprueba junto a cada `pyproject.toml`, no solo en `server/`.
2. Un proceso se lanza con una lista de argumentos, sin shell. Lo comprueban ruff `S602` y `S605`.
3. El `select` de ruff de las plantillas nombra cada regla de pycodestyle y de pep8-naming que nombra «Cumplimiento», en lugar de `E`, `W` y `N` enteras. No lleva `E101`, `E701` a `E703`, `W191` ni `W292`, que ya hace fallar `ruff format --check`, y lleva `E902`. Ignora `D412` y `D414`.
4. Una fila de «Cumplimiento» dice solo lo que su herramienta hace cumplir: las del largo de línea, la codificación, los tipos comparados, la mayúscula del docstring, los genéricos, los alias, los nombres de módulo y las fechas se acotan a lo comprobado.
5. Si ningún `return` de una función devuelve un valor, ninguno dice `return None`.
6. Lo que endurece su origen se escribe como endurecimiento, con su razón y antes de las convenciones adoptadas: el docstring de todo módulo, `TypeIs`, `import *`, CapWords, las reglas `PT` y terminar la conexión con un certificado que no vale. Lo que el origen no dice pasa a convención propia: uv, la E/S síncrona en una corrutina, `create_default_context()`, `secrets` y `test_<módulo>.py`. «Seguridad» deja de citar NIST SP 800-63B-4.
7. Una razón que no se aparta de una fuente ni de otra regla sale. Una que afirma un hecho que no es evidente lleva el enlace a la documentación de la versión en uso.
8. El código de `models/` del servidor no tiene el límite de 99 caracteres, que es lo que hace `models/ruff.toml`.
9. Una ruta se maneja con `pathlib`. Lo comprueba ruff `PTH`, sin `PTH201` ni `PTH210`.
10. Una cadena literal con valores se arma con una f-string. Lo comprueban ruff `UP031` y `UP032`.
11. Lo obsoleto rompe CI: Pyrefly lleva `deprecated = "error"`, y pytest, `filterwarnings = ["error"]`. Un aviso de un tercero se ignora por su clase y su módulo, y lo escribe la página de la pieza.
12. Un módulo importa cada submódulo que usa, y un `except` no repite lo que ya atrapa otro: Pyrefly lleva `implicit-import = "error"` y `unreachable-except-clause = "error"`. La plantilla del servidor tenía 3 y 1, ocultos como avisos, y se corrigieron.

## Consecuencias

- Una versión nueva de ruff no agrega reglas de pycodestyle ni de pep8-naming sin que la página las nombre.
- Un repositorio con el `select` anterior copia el nuevo.
- Quedan sin herramienta `type(x) is int`, un alias sin `TypeAlias`, el nombre de un paquete, una fecha que se vuelve naive y `asyncio.create_subprocess_shell`: las convenciones rigen igual.
- Un archivo de pytest que le gana a `pyproject.toml` rompe CI en cualquier pieza.
- Los repositorios que usan `os.path`, `%`, `format()` o algo obsoleto dejan de pasar el CI hasta cambiarlo, y uno con un aviso de un tercero lo ignora en su configuración.

## Descartado

- **Mantener `E`, `W` y `N` enteras:** activan reglas que ninguna fila nombra, hoy `W292` y `E902`, y las que ruff estabilice después.
- **Eximir del límite solo las columnas de `models/`:** ruff no tiene una opción por sentencia, y el formateador partiría la columna; habría que poner `# fmt: skip` y `noqa` en cada línea.
- **Una regla de ruff para lo que las filas acotadas no cubren:** ruff 0.17.5 no tiene una que lo marque.
