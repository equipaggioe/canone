# ADR-0166 · `flet.md` escribe solo lo que elige

- **Estado:** Aceptada. El usuario pidió aplicar la revisión (2026-11-16). El punto 10 lo reemplaza el [ADR-0170](0170-cada-app-guarda-su-numero-de-build-en-su-manifiesto.md)
- **Fecha:** 2026-11-16
- **Alcance:** [`plataformas/flet.md`](../plataformas/flet.md), `fuentes/flet/`,
  `plantilla/flet/` y `scripts/verificar.py`

## Contexto

Revisión de `flet.md` con los criterios del
[ADR-0162](0162-una-pagina-escribe-decisiones-y-no-como-funciona-su-tecnologia.md) y del
[ADR-0163](0163-una-revision-recorre-el-documento-entero-y-propone-tambien-lo-que-falta.md).
Leído en los wheels de PyPI de Flet 1.1.2, flet-secure-storage 1.1.2 y httpx 0.28.1:

- `TextField` tiene `autofill_hints` y `can_reveal_password`, y `AutofillHint` tiene `USERNAME`,
  `PASSWORD`, `NEW_PASSWORD` y `ONE_TIME_CODE`.
- flet-secure-storage 1.1.2 depende de flutter_secure_storage 10.3.1, cuyo README pide
  `allowBackup="false"` en Android.
- El `retries` del transporte de httpx se pasa a httpcore como reintentos de conexión.

Comprobado: con `paginas = {"flet.md", "python.md"}`, el `verificar.py` anterior no marcaba un
`flutter-version` distinto del de stack.md, y el nuevo lo marca. `plantilla/flet/theme.py` pasa
ruff 0.17.3 y Pyrefly 1.4.0 con el `pyproject.toml` de la plantilla, y con un `SharedPreferences`
falso empieza en `SYSTEM`, guarda `dark` y lo vuelve a leer.

## Decisión

1. **Salen las convenciones que tienen una sola forma correcta:** `update()` en una tarea de
   `run_task()`, la anotación y el `default_factory` de los campos, `before_update()` sin
   `update()`, el alto de un `ListView`, `prevent_close`, `asyncio_mode = "auto"` y el fixture
   `flet_app`. También salen la prueba manual con el botón Atrás, que es un procedimiento, y la
   declaración de las extensiones, que ya pide stack.md.
2. **`large-lists.md` sale de `fuentes/flet/`:** le quedan dos convenciones. Las dos pasan a propias.
3. **Un control propio fija sus valores por defecto como campos anotados, no en `init()`.**
4. **`src/` no lleva `__init__.py`**, y la página lo dice frente a «Paquetes» de `python.md`.
5. **Entra «Contraseñas»:** `AutofillGroup` con sus `autofill_hints`, y `password` con
   `can_reveal_password`.
6. **En Android, la app lleva `allowBackup = false`.**
7. **Los catálogos van en `src/locales/`, y el `.mo` se genera y no va en git.**
8. **Las llamadas y los reintentos se escriben a mano en `api/client.py`.**
9. **Las versiones salen de la página:** el Flutter y la Pydantic los fija stack.md, y la página
   conserva solo la razón de la excepción.
10. **El número de build es el `github.run_number` del release**, como convención propia.
11. **`verificar.py` exige el `flutter-version` de stack.md también con `flet.md`.**

## Consecuencias

- `plantilla/flet/theme.py` lee y guarda la elección del modo en `SharedPreferences`.
- La herramienta que compila el `.mo` queda sin elegir, y el CI de la plantilla todavía no lo
  compila.

## Descartado

- **Fijar las dependencias transitivas con `==` en `[project]`:** choca con «Toda dependencia
  declarada se usa» de stack.md y con deptry.
- **Elegir entre `flet build` a mano y flet-build-action:** la razón para construir a mano no se
  confirmó. La acción también corre con `uv run`.
