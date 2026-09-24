# ADR-0006 · Las dependencias de Python se declaran en `pyproject.toml` con `uv`

- **Estado:** Propuesta
- **Fecha:** 2026-09-22
- **Alcance:** `server/`, y toda pieza en Python

## Contexto

Los seis servidores tienen `requirements.txt`; dos tienen además `pyproject.toml`; las apps Flet de
banditore usan `pyproject.toml` + `uv.lock`. Los `requirements.txt` fijan versiones de forma
desigual: navetta con `==`, presenze y concordia con `>=` sin techo, vettore con rangos.

Un `>=` sin lock significa que dos instalaciones de la misma revisión traen árboles distintos.

## Decisión

1. `pyproject.toml` declara las dependencias directas, y `uv.lock` fija el árbol completo. Los dos
   se commitean.
2. `requirements.txt` se borra. No se mantiene en paralelo.
3. `pyproject.toml` también contiene la configuración de `ruff`, `mypy` y `pytest`. Se borran
   `pytest.ini` y cualquier otro archivo de configuración suelto.
4. CI instala con `uv sync --locked`: un lock desactualizado falla en vez de resolver otra cosa.
   `--frozen` no sirve para esto: instala el lock viejo sin comprobarlo y termina bien.

## Consecuencias

- Un solo archivo de configuración por proyecto y una instalación reproducible.
- Hay que reemplazar `pip install -r requirements.txt` en el CI, los scripts y la documentación de
  los seis repositorios, y en las tareas de `consola`.
- Las tres piezas que ya usan `uv` no cambian.

## Descartado

- **`requirements.txt` con `==` en todo:** fija las directas pero no las transitivas, y obliga a
  mantener a mano lo que un lock hace solo.
- **Poetry o PDM:** hacen lo mismo que `uv`, que ya está en uso en el repositorio.
