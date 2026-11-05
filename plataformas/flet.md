# Flet

Una aplicación en Flet. Se suma a [python.md](python.md).

## Proyecto

- Flet 1.0.5, que construye con Flutter 3.44.8.

```text
<pieza>/
  pyproject.toml
  uv.lock
  src/
    main.py
    colors.py
    theme.py
    assets/
      icon.png
    api/              el cliente y sus modelos
    views/            una vista por ruta
  tests/
    __init__.py
    test_theme.py
```

- El código va directo en `src/`, y el proyecto no lleva `[build-system]`. Contradice el `src/app/` y el `uv_build` de [python.md](python.md): es la estructura que supone `flet build`, que empaqueta `src/` por su cuenta.
- `[tool.flet.app]` lleva `path = "src"`.

Plantilla: [plantilla/flet/](../plantilla/flet/). `tests/test_theme.py` es canónico y se copia sin editar; `theme.py` es un punto de partida.

## Accesibilidad

Contrato: [transversal.md](transversal.md#accesibilidad).

## Almacenamiento

Estándares: [*Encrypting sensitive data*](../fuentes/flet/encrypting-sensitive-data.md), entero, y la referencia de [SecureStorage](../fuentes/flet/securestorage.md), por las entradas que se usan, de Flet.

- Lo sensible, como el token de refresco que pide [transversal.md](transversal.md#sesión), va en `SecureStorage`, y `SharedPreferences` guarda solo preferencias. `SecureStorage` usa el almacén cifrado del sistema; cifrar a mano obliga a guardar la clave en algún lado.

## Idiomas

Contrato: [transversal.md](transversal.md#idiomas).

- Los textos usan `gettext` de la biblioteca estándar de Python, con catálogos `.po`. Flet no trae un sistema de traducción.

## Mapas

Contrato: [transversal.md](transversal.md#mapas).

## Red

- HTTP va por un solo `httpx.AsyncClient` desde handlers async, y las respuestas se leen con modelos de Pydantic en `api/`. No bloquea la interfaz y reutiliza las conexiones.

## Tema

> **En desarrollo; no se implementa:** [transversal.md](transversal.md#tema).

Contrato: [transversal.md](transversal.md#tema).

- `page.theme` y `page.dark_theme` se arman en `theme.py` con `LIGHT` y `DARK`, generados en `colors.py`, y `page.theme_mode` es `ThemeMode.SYSTEM`.
- Los tamaños van en `theme.py`, sin tamaños literales fuera de él.

## Publicación

Estándar: las entradas de [*Publishing a Flet app*](../fuentes/flet/publish.md) que usa el `pyproject.toml` de la plantilla.

## Cumplimiento

| Convención | Herramienta |
| :--- | :--- |
| Flet 1.0.5 | [scripts/verificar.py](../scripts/verificar.py) |
