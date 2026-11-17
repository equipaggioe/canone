# Python

Lo común a toda pieza en Python. Lo propio de cada una va en su página y se suma a esto.

## Proyecto

Estándar: las [*Good Integration Practices*](../fuentes/pytest/goodpractices.rst) de pytest.

- `requires-python` fija con `==` la serie de Python de [stack.md](../stack.md#python), y uv usa solo el Python del sistema, con `python-preference = "only-system"`. Toda herramienta que elige la versión más alta permitida, como `flet build`, toma esa serie.
- uv es la misma versión en toda pieza, en el CI, en la máquina de quien desarrolla y en el servidor: `required-version` en `[tool.uv]`, con `==` y la versión de [stack.md](../stack.md#python). El CI la instala con `setup-uv` y `version-file`, y el servidor, con `uv.py` de [despliegue.md](despliegue.md#máquina).
- El bloqueo es `uv.lock`, en git, y se instala con `uv sync --locked`.
- El backend de construcción es `uv_build`, con la siguiente versión menor como tope.
- `pyproject.toml` declara con `>=` la versión que fija [stack.md](../stack.md), y `uv.lock` fija la exacta.
- Las herramientas de desarrollo van en el grupo `dev` de `[dependency-groups]`.
- Las dependencias y la configuración de pytest van en el `pyproject.toml` de la pieza: no hay `requirements.txt` ni `pytest.ini`.
- El paquete se llama `app` en toda pieza, con `module-name = "app"` en `[tool.uv.build-backend]`. Los archivos canónicos lo nombran y se copian sin editar.
- uv maneja el entorno, las dependencias y la ejecución: crea el entorno virtual `.venv` de la pieza, instala en él la pieza, sus dependencias y pytest, bloquea y ejecuta ([Good Integration Practices, *Install package in a virtual environment*](../fuentes/pytest/goodpractices.rst)).
- Ninguna dependencia bloqueada tiene una vulnerabilidad conocida.
- Una vulnerabilidad se ignora solo por su identificador, con `--ignore-vuln`. Sacar el paquete del análisis también tapa sus vulnerabilidades futuras.
- CI corre `deptry`, que falla con un paquete que el código de `src/` importa sin declararlo en `dependencies`, o con una dependencia que no se usa ([stack.md](../stack.md#qué-entra)).
- Las pruebas van fuera del código, y el código, en el layout `src` ([Good Integration Practices, *Choosing a test layout*](../fuentes/pytest/goodpractices.rst)):

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

Plantilla: el `pyproject.toml` de cada pieza, en [plantilla/server/](../plantilla/server/), [plantilla/qt/](../plantilla/qt/) y [plantilla/flet/](../plantilla/flet/), [plantilla/python/.gitignore](../plantilla/python/.gitignore) y los jobs de Python de [plantilla/.github/workflows/ci.yml](../plantilla/.github/workflows/ci.yml). Cada uno lleva la configuración de esta página más la de su plataforma.

## Estilo

Estándar: [PEP 8](../fuentes/python/pep-0008.rst).

- El código se formatea con `ruff format`.
- El código cumple las reglas `F` de ruff: marcan nombres sin definir, e imports y variables sin usar.
- La pertenencia se niega con `x not in y`, no con `not x in y`, y ninguna cadena lleva una secuencia de escape inválida.
- Un archivo de código es UTF-8 y no declara su codificación.
- El código cumple *Maximum Line Length*, con líneas de hasta 99 caracteres, y comentarios y docstrings de hasta 72 ([PEP 8, *Maximum Line Length*](../fuentes/python/pep-0008.rst)).
- El código cumple *String Quotes*, con comillas dobles ([PEP 8, *String Quotes*](../fuentes/python/pep-0008.rst)).
- El código cumple *Should a Line Break Before or After a Binary Operator?*: la línea se parte antes del operador ([PEP 8, *Should a Line Break Before or After a Binary Operator?*](../fuentes/python/pep-0008.rst)).
- El código cumple *Indentation* ([PEP 8, *Indentation*](../fuentes/python/pep-0008.rst)).
- El código cumple *Tabs or Spaces?* ([PEP 8, *Tabs or Spaces?*](../fuentes/python/pep-0008.rst)).
- El código cumple *Blank Lines* ([PEP 8, *Blank Lines*](../fuentes/python/pep-0008.rst)).
- El código cumple *Whitespace in Expressions and Statements*, salvo los espacios según la prioridad de los operadores: `ruff format` pone uno a cada lado de todo operador binario, y el código queda como lo deja el formateador ([PEP 8, *Whitespace in Expressions and Statements*](../fuentes/python/pep-0008.rst)).
- El código cumple *When to Use Trailing Commas* ([PEP 8, *When to Use Trailing Commas*](../fuentes/python/pep-0008.rst)).
- El código cumple *Variable Annotations* ([PEP 8, *Variable Annotations*](../fuentes/python/pep-0008.rst)).
- Una comparación con `None` usa `is` o `is not`, y un valor que puede ser `None` se compara así, no por su valor de verdad ([PEP 8, *Programming Recommendations*](../fuentes/python/pep-0008.rst)).
- La identidad se niega con `x is not y`, no con `not x is y` ([PEP 8, *Programming Recommendations*](../fuentes/python/pep-0008.rst)).
- Un booleano no se compara con `True` ni con `False`, ni con `==` ni con `is` ([PEP 8, *Programming Recommendations*](../fuentes/python/pep-0008.rst)).
- Un tipo se comprueba con `isinstance()`, no comparando tipos ([PEP 8, *Programming Recommendations*](../fuentes/python/pep-0008.rst)).
- Una secuencia vacía se reconoce por su valor de verdad, no con `len()` ([PEP 8, *Programming Recommendations*](../fuentes/python/pep-0008.rst)).
- Un prefijo o un sufijo se comprueba con `startswith()` o `endswith()`, no cortando la cadena ([PEP 8, *Programming Recommendations*](../fuentes/python/pep-0008.rst)).
- Ningún literal de cadena depende de espacios al final ([PEP 8, *Programming Recommendations*](../fuentes/python/pep-0008.rst)).
- Una clase que define un orden implementa las seis comparaciones, o las completa con `functools.total_ordering` ([PEP 8, *Programming Recommendations*](../fuentes/python/pep-0008.rst)).
- Una función se define con `def`, nunca asignando una `lambda` a un nombre ([PEP 8, *Programming Recommendations*](../fuentes/python/pep-0008.rst)).
- Si un `return` de una función devuelve un valor, todos lo hacen: el que no devuelve nada dice `return None`, y la función termina con un `return` si su final se alcanza ([PEP 8, *Programming Recommendations*](../fuentes/python/pep-0008.rst)).
- Un recurso que usa una sola sección del código se libera con `with`, o con `try` y `finally` ([PEP 8, *Programming Recommendations*](../fuentes/python/pep-0008.rst)).
- Un administrador de contexto que hace algo más que tomar y liberar un recurso se obtiene de una función o un método que lo dice, como `conn.begin_transaction()` ([PEP 8, *Programming Recommendations*](../fuentes/python/pep-0008.rst)).

## Comentarios

Estándares: [PEP 8](../fuentes/python/pep-0008.rst) y [PEP 257](../fuentes/python/pep-0257.rst).

- Un docstring es prosa que resume qué hace o qué es su objeto: no lista lo que exporta un módulo ni lo que tiene una clase, y nombra un argumento solo cuando la firma no basta. La firma ya da el nombre, el tipo y el valor por defecto.
- Un docstring no está vacío y empieza con mayúscula, y una función con `@overload` no lleva docstring.
- Los docstrings cumplen *What is a Docstring?*, y el `__init__.py` de cada paquete también lleva el suyo ([PEP 257, *What is a Docstring?*](../fuentes/python/pep-0257.rst)).
- Los docstrings cumplen *One-line Docstrings*, salvo decir la naturaleza del valor de retorno: la anotación ya la da ([PEP 257, *One-line Docstrings*](../fuentes/python/pep-0257.rst)).
- Los docstrings cumplen la forma de *Multi-line Docstrings*: la línea de resumen, la línea en blanco, la sangría y las comillas de cierre ([PEP 257, *Multi-line Docstrings*](../fuentes/python/pep-0257.rst)).
- Un método no público sin docstring lleva, después de la línea `def`, un comentario que dice qué hace ([PEP 8, *Documentation Strings*](../fuentes/python/pep-0008.rst)).
- Ningún comentario contradice el código: cambia en el mismo commit que el código que describe ([PEP 8, *Comments*](../fuentes/python/pep-0008.rst)).
- Un comentario es claro y se escribe en oraciones completas, cada una terminada en punto. Empieza con mayúscula, salvo que su primera palabra sea un identificador en minúscula ([PEP 8, *Comments*](../fuentes/python/pep-0008.rst)).
- Un comentario de bloque tiene la sangría del código que sigue, cada una de sus líneas empieza con `# `, y sus párrafos se separan con una línea que solo tiene `#` ([PEP 8, *Block Comments*](../fuentes/python/pep-0008.rst)).
- Los comentarios en línea son pocos y no dicen lo obvio. Van a dos espacios de la sentencia y empiezan con `# ` ([PEP 8, *Inline Comments*](../fuentes/python/pep-0008.rst)).

## Tipos

Estándares: [*Typing Best Practices*](../fuentes/typing/best_practices.rst), [*Modernizing Superseded Typing Features*](../fuentes/typing/modernizing.rst) y [PEP 8](../fuentes/python/pep-0008.rst).

- Pyrefly en modo strict, salvo `missing-override-decorator`. Entiende sin plugin los alias que genera `to_camel` y los campos que pydantic-settings lee del entorno.
- Toda función va anotada: un argumento sin anotar es `Any`, y Pyrefly no revisa lo que recibe.
- Un error de tipos se ignora con `# pyrefly: ignore[<código>]`: Pyrefly aplica `# type: ignore` a toda la línea sin mirar el código.
- Todo ignore y todo `# noqa` llevan el código del error. Uno sin código también tapa los errores futuros de esa línea.
- Lo que el `typing` de Python 3.13 trae no se importa de `typing_extensions`.
- Las uniones cumplen *Shorthand Syntax* ([Typing Best Practices, *Shorthand Syntax*](../fuentes/typing/best_practices.rst)).
- Los genéricos cumplen *Generics in the ``typing`` Module* ([Modernizing, *Generics in the ``typing`` Module*](../fuentes/typing/modernizing.rst)).
- Las anotaciones cumplen *``typing.Text``* ([Modernizing, *``typing.Text``*](../fuentes/typing/modernizing.rst)).
- Las anotaciones cumplen *``typing.TypedDict`` Legacy Forms* ([Modernizing, *``typing.TypedDict`` Legacy Forms*](../fuentes/typing/modernizing.rst)).
- Las anotaciones cumplen *Type Aliases*: un alias de tipo se declara con `type` ([Modernizing, *Type Aliases*](../fuentes/typing/modernizing.rst)).
- Las anotaciones cumplen *User Defined Generics* ([Modernizing, *User Defined Generics*](../fuentes/typing/modernizing.rst)).
- Las anotaciones cumplen *``typing.ByteString``* ([Modernizing, *``typing.ByteString``*](../fuentes/typing/modernizing.rst)).
- Las anotaciones cumplen *``typing.Hashable`` and ``typing.Sized``* ([Modernizing, *``typing.Hashable`` and ``typing.Sized``*](../fuentes/typing/modernizing.rst)).
- Una anotación usa la sintaxis de anotaciones, nunca un comentario `# type:` ([Modernizing, *Type Comments*](../fuentes/typing/modernizing.rst)).
- `Never` reemplaza a `NoReturn`, también como retorno ([Modernizing, *``typing.NoReturn``*](../fuentes/typing/modernizing.rst)).
- Una función que estrecha un tipo devuelve `TypeIs`, y `TypeGuard` solo cuando las restricciones de `TypeIs` lo impiden ([Modernizing, *``typing.TypeGuard``*](../fuentes/typing/modernizing.rst)).
- Un argumento que acepta cualquier valor, y el retorno de un callback que se ignora, se anotan con `object`. `Any` queda para el tipo que el sistema de tipos no expresa o que es incómodo escribir ([Typing Best Practices, *Using ``Any`` and ``object``*](../fuentes/typing/best_practices.rst)).
- Un argumento se anota con un tipo abstracto o un protocolo, como `Mapping`, `Sequence` o `Iterable`, y el retorno de una implementación concreta, con un tipo concreto, como `list` o `dict` ([Typing Best Practices, *Arguments and Return Types*](../fuentes/typing/best_practices.rst)).
- Un retorno no es una unión que obliga a distinguir sus tipos con `isinstance()`: si hace falta, es `Any` o `X | Any` ([Typing Best Practices, *Arguments and Return Types*](../fuentes/typing/best_practices.rst)).
- Se anota `float`, no `int | float`, y `None`, no `Literal[None]` ([Typing Best Practices, *Types*](../fuentes/typing/best_practices.rst)).
- Las anotaciones de una función siguen la sintaxis de PEP 484 ([PEP 8, *Function Annotations*](../fuentes/python/pep-0008.rst)).

## Paquetes

Estándar: [PEP 8](../fuentes/python/pep-0008.rst).

- Todo directorio de código lleva `__init__.py`: sin él, la carpeta se vuelve en silencio un paquete de espacio de nombres.
- En cada grupo de imports, los `import` van antes que los `from`, y unos y otros en orden alfabético del módulo.
- Los nombres de un `from` van en orden alfabético: primero las constantes, después las clases y al final lo demás.
- Los nombres de un mismo módulo se importan en un solo `from`.
- Los imports son absolutos: una sola forma, y la que da mejores errores ([PEP 8, *Imports*](../fuentes/python/pep-0008.rst)).
- No se importa con `from <módulo> import *`: deja sin saber qué nombres hay ([PEP 8, *Imports*](../fuentes/python/pep-0008.rst)).
- Cada import va en su propia línea, al principio del archivo, después de los comentarios y el docstring del módulo y antes de sus variables y constantes ([PEP 8, *Imports*](../fuentes/python/pep-0008.rst)).
- Los imports van en tres grupos separados por una línea en blanco: la biblioteca estándar, los de terceros y los de la pieza ([PEP 8, *Imports*](../fuentes/python/pep-0008.rst)).
- Si el nombre de una clase importada choca con un nombre local, se importa su módulo y se usa `módulo.Clase` ([PEP 8, *Imports*](../fuentes/python/pep-0008.rst)).
- `__all__` y los demás dunders de módulo van después del docstring y antes de los imports, salvo los `from __future__` ([PEP 8, *Module Level Dunder Names*](../fuentes/python/pep-0008.rst)).
- Un módulo no toma de otro un nombre que ese otro solo importó, salvo que lo exponga a propósito, como el `__init__.py` de un paquete con los de sus submódulos ([PEP 8, *Public and Internal Interfaces*](../fuentes/python/pep-0008.rst)).

## Nombres

Estándar: [PEP 8](../fuentes/python/pep-0008.rst).

- Toda clase se nombra en CapWords, también la que se usa como una función ([PEP 8, *Class Names*](../fuentes/python/pep-0008.rst)).
- Las funciones, los métodos, los argumentos y las variables se nombran en minúsculas, con guiones bajos entre palabras, sin mixedCase. Solo un método que sobrescribe otro conserva el nombre del original ([PEP 8, *Function and Variable Names*](../fuentes/python/pep-0008.rst), [PEP 8, *Method Names and Instance Variables*](../fuentes/python/pep-0008.rst) y [PEP 8, *Global Variable Names*](../fuentes/python/pep-0008.rst)).
- Los nombres cumplen *Names to Avoid* ([PEP 8, *Names to Avoid*](../fuentes/python/pep-0008.rst)).
- Un paquete tiene un nombre corto, en minúsculas y sin guiones bajos. Un módulo tiene un nombre corto, en minúsculas, con guiones bajos solo si se lee mejor ([PEP 8, *Package and Module Names*](../fuentes/python/pep-0008.rst)).
- Una constante se nombra en mayúsculas, con guiones bajos entre palabras ([PEP 8, *Constants*](../fuentes/python/pep-0008.rst)).
- Una excepción que es un error lleva el sufijo `Error` ([PEP 8, *Exception Names*](../fuentes/python/pep-0008.rst); [PEP 8, *Programming Recommendations*](../fuentes/python/pep-0008.rst)).
- Una variable de tipo se nombra en CapWords, con un nombre corto como `T`, y con el sufijo `_co` o `_contra` si se declara covariante o contravariante ([PEP 8, *Type Variable Names*](../fuentes/python/pep-0008.rst)).
- En CapWords, un acrónimo va entero en mayúsculas, como `HTTPServerError` ([PEP 8, *Descriptive: Naming Styles*](../fuentes/python/pep-0008.rst)).
- No se inventan nombres con dos guiones bajos al principio y al final ([PEP 8, *Descriptive: Naming Styles*](../fuentes/python/pep-0008.rst)).
- El primer argumento de un método es `self`, y el de un método de clase, `cls` ([PEP 8, *Function and Method Arguments*](../fuentes/python/pep-0008.rst)).
- Un nombre que choca con una palabra reservada lleva un guion bajo al final, como `class_`, y no una abreviatura ([PEP 8, *Function and Method Arguments*](../fuentes/python/pep-0008.rst); [PEP 8, *Designing for Inheritance*](../fuentes/python/pep-0008.rst)).
- Un dato de una clase se expone como atributo, sin métodos para leerlo y escribirlo. Si necesita lógica, pasa a ser una `property`, sin efectos secundarios ni cálculos caros ([PEP 8, *Designing for Inheritance*](../fuentes/python/pep-0008.rst)).

## Archivos de texto

- Los archivos de texto se abren con `encoding="utf-8"`: la codificación por defecto es la del sistema, que en Windows no suele ser UTF-8. [Python 3.13](https://raw.githubusercontent.com/python/cpython/3.13/Doc/library/io.rst)

## Async

Estándares: [*Developing with asyncio*](../fuentes/python/asyncio-dev.rst) y [*Coroutines and tasks*](../fuentes/python/asyncio-task.rst).

- Las tareas concurrentes se lanzan con `TaskGroup`, y no con `create_task` ni `gather`, salvo una tarea que tiene que vivir más que la función que la lanza: no pierde tareas ni excepciones, y si una falla, cancela las demás ([Coroutines and tasks, *Creating tasks*](../fuentes/python/asyncio-task.rst); [Coroutines and tasks, *Running tasks concurrently*](../fuentes/python/asyncio-task.rst)).
- Una corrutina que atrapa `CancelledError` lo relanza cuando termina de limpiar, y no llama a `uncancel()`: `TaskGroup` y `asyncio.timeout()` se basan en la cancelación ([Coroutines and tasks, *Task cancellation*](../fuentes/python/asyncio-task.rst); [Coroutines and tasks, *Shielding from cancellation*](../fuentes/python/asyncio-task.rst)).
- Las pruebas de CI corren en el modo de desarrollo de Python: activa el modo debug de asyncio y además muestra los `ResourceWarning` ([Developing with asyncio, *Debug Mode*](../fuentes/python/asyncio-dev.rst)).
- Una corrutina hace su limpieza en un `finally` ([Coroutines and tasks, *Task cancellation*](../fuentes/python/asyncio-task.rst)).
- Una tarea creada fuera de un `TaskGroup` guarda su referencia: el bucle de eventos solo guarda una referencia débil, y la tarea puede desaparecer antes de terminar ([Coroutines and tasks, *Creating tasks*](../fuentes/python/asyncio-task.rst); [Coroutines and tasks, *Shielding from cancellation*](../fuentes/python/asyncio-task.rst)).
- `add_done_callback()` se usa solo en código de bajo nivel basado en callbacks, y para que una tarea quite su referencia de la colección que la guarda ([Coroutines and tasks, *Task object*](../fuentes/python/asyncio-task.rst); [Coroutines and tasks, *Creating tasks*](../fuentes/python/asyncio-task.rst)).
- Un plazo se pone con `asyncio.timeout()` o `asyncio.timeout_at()`, no creando un `Timeout` ([Coroutines and tasks, *Timeouts*](../fuentes/python/asyncio-task.rst)).
- Desde otro hilo, el código llega al bucle de eventos solo con `loop.call_soon_threadsafe` o `asyncio.run_coroutine_threadsafe` ([Developing with asyncio, *Concurrency and Multithreading*](../fuentes/python/asyncio-dev.rst)).
- Una corrutina no llama directamente código que bloquea, como una E/S síncrona o un cálculo largo: lo corre en un executor ([Developing with asyncio, *Running Blocking Code*](../fuentes/python/asyncio-dev.rst)).
- Toda corrutina que se llama se espera con `await` o se lanza como tarea ([Developing with asyncio, *Detect never-awaited coroutines*](../fuentes/python/asyncio-dev.rst)).
- Un generador asíncrono se recorre dentro de `contextlib.aclosing`, o se cierra con `aclose()` ([Developing with asyncio, *Close asynchronous generators explicitly*](../fuentes/python/asyncio-dev.rst)).
- Un generador asíncrono se crea con el bucle de eventos ya en marcha ([Developing with asyncio, *Create asynchronous generators only when the event loop is running*](../fuentes/python/asyncio-dev.rst)).
- Un generador asíncrono no se recorre ni se cierra desde varias tareas a la vez, ni desde varios bucles de eventos ([Developing with asyncio, *Avoid concurrent iteration and closure of the same generator*](../fuentes/python/asyncio-dev.rst)).

## Excepciones

Estándar: [PEP 8](../fuentes/python/pep-0008.rst).

- Una excepción deriva de `Exception`, no de `BaseException`. La jerarquía distingue lo que necesita saber quien la atrapa, no dónde se lanza ([PEP 8, *Programming Recommendations*](../fuentes/python/pep-0008.rst)).
- Una excepción que reemplaza a otra se lanza con `raise X from Y`. Con `raise X from None`, la nueva lleva los datos de la original, como su mensaje ([PEP 8, *Programming Recommendations*](../fuentes/python/pep-0008.rst)).
- Un `except` nombra las excepciones que atrapa. `except Exception:` atrapa todos los errores del programa, y `except:` solo registra el traceback, o limpia y relanza con `raise` ([PEP 8, *Programming Recommendations*](../fuentes/python/pep-0008.rst)).
- Un error del sistema operativo se atrapa por su clase, como `FileNotFoundError`, y no mirando `errno` ([PEP 8, *Programming Recommendations*](../fuentes/python/pep-0008.rst)).
- El `try` envuelve solo el código que puede lanzar la excepción que se atrapa ([PEP 8, *Programming Recommendations*](../fuentes/python/pep-0008.rst)).
- Un `finally` no tiene un `return`, `break` ni `continue` que salga de él: cancela la excepción que está en curso ([PEP 8, *Programming Recommendations*](../fuentes/python/pep-0008.rst)).

## Fechas

- Toda `datetime` es aware y en UTC, y la fecha de hoy sale de una de ellas; la hora local aparece solo al mostrarla: comparar una naive con una aware lanza `TypeError`, y una naive se toma como hora local.

## Logging

- Toda salida pasa por logging: ni un servidor ni una GUI tienen una consola que alguien lea.
- Los mensajes pasan sus valores como argumentos `%s`: el mensaje se arma solo si el nivel está activo.

## Seguridad

Estándares: [NIST SP 800-63B-4](../fuentes/nist/sp800-63b-4.txt) y [RFC 9110](../fuentes/rfc/rfc9110.txt).

- Un archivo temporal se crea con `tempfile.mkstemp` o `NamedTemporaryFile`, nunca con `mktemp`: entre elegir el nombre y abrirlo, otro proceso puede crear el archivo.
- MD5 y SHA-1 se usan solo con `usedforsecurity=False`: están rotos como protección.
- No se usa `logging.config.listen`: ejecuta la configuración que recibe por la red.
- Un código, un challenge, un token, una clave o cualquier otro valor que protege algo sale de `secrets`, el generador criptográfico de Python, nunca de `random`: la secuencia de `random` se puede predecir ([NIST SP 800-63B-4 §3.2.12](../fuentes/nist/sp800-63b-4.txt)).
- Una conexión TLS usa el contexto de `ssl.create_default_context()`, sin desactivar la verificación ni bajar la versión del protocolo: verifica que el certificado valga para el host de la URI y rechaza los protocolos inseguros. Un certificado que no vale termina la conexión con un error, que va al log ([RFC 9110 §4.3.4](../fuentes/rfc/rfc9110.txt)).

## Pruebas

Estándar: las [*Good Integration Practices*](../fuentes/pytest/goodpractices.rst) de pytest.

- Las pruebas se escriben con pytest: un `assert` simple muestra los valores que fallaron, y los fixtures reemplazan a `setUp`.
- Las pruebas cumplen las reglas `PT` de ruff, la versión de flake8-pytest-style que trae ruff ([Good Integration Practices, *Checking with flake8-pytest-style*](../fuentes/pytest/goodpractices.rst)).
- Cada módulo de pruebas se llama `test_<módulo>.py` ([Good Integration Practices, *Conventions for Python test discovery*](../fuentes/pytest/goodpractices.rst)).
- pytest importa las pruebas con `--import-mode=importlib` ([Good Integration Practices, *Choosing a test layout*](../fuentes/pytest/goodpractices.rst)).
- pytest corre en modo estricto, con `strict = true`, y su versión queda bloqueada en `uv.lock` ([Good Integration Practices, *Using pytest's strict mode*](../fuentes/pytest/goodpractices.rst)).

## Cumplimiento

| Convención | Herramienta |
| :--- | :--- |
| El Python de [stack.md](../stack.md#python), y solo el del sistema | `requires-python` y uv con `python-preference = "only-system"` |
| La misma versión de uv en toda pieza | uv con `required-version`, y [scripts/verificar.py](../scripts/verificar.py), que comprueba que cada `pyproject.toml` la declare |
| Las versiones de [stack.md](../stack.md), declaradas con `>=` | [scripts/verificar.py](../scripts/verificar.py) |
| El bloqueo | `uv sync --locked` en CI |
| Sin `requirements.txt` ni `pytest.ini`, en `server/` | [scripts/verificar.py](../scripts/verificar.py) |
| Vulnerabilidades | pip-audit |
| Imports declarados y dependencias usadas | deptry |
| El formato, *Should a Line Break Before or After a Binary Operator?*, *Indentation*, *Blank Lines* y *When to Use Trailing Commas* | `ruff format --check` |
| *Maximum Line Length* | `ruff format`, y ruff `E501` y `W505` con `line-length = 99` y `max-doc-length = 72` |
| *String Quotes* | `ruff format` y ruff `D300` |
| *Tabs or Spaces?* | `ruff format`, y ruff `W191` y `E101` |
| *Whitespace in Expressions and Statements* | `ruff format`, y ruff `E701` a `E703`, `W291` y `W293` |
| *Variable Annotations* | `ruff format` |
| Reglas `F` | ruff `F` |
| `not in` y las secuencias de escape | ruff `E713` y `W605` |
| Sin declaración de codificación | ruff `UP009` |
| Comparaciones con `None` | ruff `E711` |
| `is not` | ruff `E714` |
| Booleanos comparados con `==` | ruff `E712` |
| `isinstance()` | ruff `E721` |
| `def` en vez de `lambda` | ruff `E731` |
| Los `return` de una función | ruff `RET501`, `RET502` y `RET503` |
| *What is a Docstring?*, *One-line Docstrings* y la forma de *Multi-line Docstrings* | ruff `D` con `convention = "pep257"` |
| Docstring no vacío, con mayúscula, y ninguno en `@overload` | ruff `D419`, `D403` y `D418` |
| El `# ` y los dos espacios de los comentarios | `ruff format` |
| Pyrefly en modo strict | `preset = "strict"` y `missing-override-decorator = false` |
| Toda función anotada | Pyrefly con `preset = "strict"` y `unannotated-return = "error"` |
| `# pyrefly: ignore` | Pyrefly con `enabled-ignores = ["pyrefly"]` |
| `# noqa` con código | ruff `PGH004` |
| Sin `typing_extensions` para lo que trae `typing` | ruff `UP035` con `target-version = "py313"` |
| Las uniones | ruff `UP007`, `UP045` y `RUF036` |
| Los genéricos | ruff `UP006` y `UP035` |
| *``typing.Text``* | ruff `UP019` |
| *``typing.TypedDict`` Legacy Forms* | ruff `UP013` |
| *Type Aliases* | ruff `UP040` |
| *User Defined Generics* | ruff `UP046` |
| *``typing.ByteString``* | ruff `PYI057` |
| *``typing.Hashable`` and ``typing.Sized``* | ruff `UP035` |
| `Never` en los argumentos | ruff `PYI050` |
| `None` y no `Literal[None]` | ruff `PYI061` |
| `__init__.py` | ruff `INP` |
| Imports absolutos | ruff `TID252` con `ban-relative-imports = "all"` |
| Sin `import *` | ruff `F403` |
| Un import por línea y al principio del archivo | ruff `E401` y `E402` |
| Los grupos y el orden de los imports | ruff `I` |
| Clases en CapWords | ruff `N801` |
| Funciones, métodos, argumentos y variables en minúsculas | ruff `N802`, `N803`, `N806`, `N815` y `N816` |
| *Names to Avoid* | ruff `E741`, `E742` y `E743` |
| Módulos y paquetes en minúsculas | ruff `N999` |
| Sin nombres inventados con dos guiones bajos en una función | ruff `N807` |
| `self` y `cls` | ruff `N804` y `N805` |
| Toda salida por logging: sin `print` ni `pprint` | ruff `T20` |
| Argumentos `%s` en los mensajes | ruff `G00` |
| Fechas aware | ruff `DTZ` |
| Las llamadas de E/S que bloquean de la biblioteca estándar y de los clientes HTTP síncronos, dentro de una corrutina | ruff `ASYNC2` |
| Referencia de las tareas fuera de un `TaskGroup` | ruff `RUF006` |
| Corrutinas sin `await` | Pyrefly `unused-coroutine` |
| Pruebas en modo de desarrollo | `PYTHONDEVMODE=1` en el paso de pytest de CI |
| Codificación explícita en el código que corren las pruebas | `PYTHONWARNDEFAULTENCODING=1` en el paso de pytest de CI y `error::EncodingWarning` en `filterwarnings` |
| `raise ... from` dentro de un `except` | ruff `B904` |
| Sin `return`, `break` ni `continue` que salgan de un `finally` | ruff `B012` |
| Sin `mktemp` | ruff `S306` |
| MD5 y SHA-1 | ruff `S324` |
| Sin `logging.config.listen` | ruff `S612` |
| TLS: sin `_create_unverified_context`, sin `verify=False` y sin un protocolo inseguro como valor por defecto | ruff `S323`, `S501` y `S503` |
| Reglas `PT` | ruff `PT` |
| Modo estricto | `strict = true` |
