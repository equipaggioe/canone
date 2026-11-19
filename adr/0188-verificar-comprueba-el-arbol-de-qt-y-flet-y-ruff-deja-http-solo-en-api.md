# ADR-0188 · `verificar.py` comprueba el árbol de Qt y de Flet, y ruff deja HTTP solo en `api/`

- **Estado:** Aceptada. El usuario pidió implementar lo recomendado para comprobar el árbol: los
  nombres con `verificar.py` y el contenido de las carpetas con ruff (2026-11-18). El punto 3 lo
  confirmó aparte, con las clases que ayudan a la pública como privadas (2026-11-18)
- **Fecha:** 2026-11-18
- **Alcance:** [`plataformas/qt.md`](../plataformas/qt.md) y [`plataformas/flet.md`](../plataformas/flet.md),
  «Proyecto» y «Cumplimiento»; `scripts/verificar.py`; `plantilla/qt/` y `plantilla/flet/`

## Contexto

El [ADR-0186](0186-lo-que-no-es-interfaz-va-en-services-y-un-servicio-externo-tiene-su-modulo-en-api.md)
agregó `services/` y los servicios externos de `api/`, y ninguna herramienta comprobaba el árbol.

Comprobado con ruff 0.17.5, en un proyecto con el `pyproject.toml` de `plantilla/qt/` y los
`ruff.toml` de esta decisión:

- Un `ruff.toml` anidado con `extend` reemplaza entero el `banned-api` de `pyproject.toml`, no le
  agrega: el de `services/` que solo nombraba `PySide6.QtWidgets` dejaba pasar httpx.
- Hereda lo demás: `ban-relative-imports` y el `per-file-ignores` de `src/app/api/models.py`.

## Decisión

1. **`verificar.py` falla con un archivo o una carpeta de `src/` que el árbol de la pieza no
   tiene**, en `desktop/` con Qt y en cada pieza de Flet, y nombra una sola vez la carpeta que
   sobra.
2. **`services/` admite un nivel de subpaquetes por dominio**, `services/<dominio>/`.
3. **Un módulo de `dialogs/`, `widgets/` o `models/` declara una sola clase pública, con su
   nombre en snake_case.** Una clase privada que la ayuda puede ir con ella.
4. **En Qt, ruff prohíbe `PySide6.QtNetwork` fuera de `api/` y `PySide6.QtWidgets` en
   `services/`**, con `src/app/api/ruff.toml` y `src/app/services/ruff.toml`.
5. **En Flet, ruff prohíbe httpx y httpx-ws fuera de `api/`**, con `src/api/ruff.toml`.
6. Los `ruff.toml` de `src/` son canónicos, y `verificar.py` los compara con la plantilla.

## Consecuencias

- Cada `ruff.toml` anidado repite el `banned-api` de su `pyproject.toml`: un cambio en uno se hace
  también en los otros.
- Un repositorio que no sigue el árbol falla desde su próximo CI. Con canone en `0abd8b6`,
  `verificar.py --todos` marca el árbol en bot, comande, consola, posta y presenze.
- En Flet, nada prohíbe importar `flet` en `services/`: el estado que comparten varios componentes
  es una clase `@ft.observable`, y no está escrito dónde va.

## Descartado

- **import-linter:** suma una herramienta al stack para lo que ruff ya hace.
- **Un `ruff.toml` que solo agrega lo prohibido:** ruff reemplaza el `banned-api` en vez de
  sumarlo.
- **Comprobar la raíz de la pieza y `tests/`:** el árbol de `tests/` depende de «Tema», que sigue en
  desarrollo.
