# Flet

Una aplicación en Flet. Se suma a [python.md](python.md).

## Proyecto

- Flet 1.0.5, que construye con Flutter 3.44.8.
- Pydantic va exacto, `pydantic==2.13.4`, y no con `>=`: `flet build apk` ignora `uv.lock` e instala con pip desde el índice de Flet para Android, que solo trae `pydantic-core` 2.46.x. Pydantic 2.14 pide la 2.50 y la compilación falla al resolver. Contradice [python.md](python.md), que fija 2.13.4 con `>=`.

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

- Lo sensible, como el token de refresco que pide [transversal.md](transversal.md#sesión), va en `SecureStorage`, y `SharedPreferences` guarda solo preferencias. `SecureStorage` usa el almacén cifrado del sistema; cifrar a mano obliga a guardar la clave en algún lado. [Flet 1.0.5](https://raw.githubusercontent.com/flet-dev/flet/v1.0.5/website/docs/services/securestorage/index.md)
- Un secreto no va en el código fuente. [Flet 1.0.5](https://raw.githubusercontent.com/flet-dev/flet/v1.0.5/website/docs/cookbook/encrypting-sensitive-data.md)

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
