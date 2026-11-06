# Flet

> **En desarrollo; no se implementa:** [README.md](README.md#en-desarrollo).

Una aplicación en Flet. Se suma a [python.md](python.md).

## Proyecto

- Flet 1.1.0, que construye con un Flutter 3.47 del `PATH` y, si no lo encuentra, instala el 3.47.9, el de [flutter.md](flutter.md).
- Las dependencias de `[project]` van exactas, con `==`: `flet build` no lee `uv.lock` y le pasa a pip las dependencias tal como están escritas. Contradice el `>=` de [python.md](python.md).
- Pydantic es la 2.13.4, y no la de [python.md](python.md): `flet build apk` instala desde el índice de Flet para Android, que trae `pydantic-core` hasta la 2.47.0. Pydantic 2.13.5 pide la 2.46.5 y la 2.14 pide la 2.50, que no están, y la compilación falla al resolver.

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

- Lo sensible, como el token de refresco que pide [transversal.md](transversal.md#sesión), va en `SecureStorage`, y `SharedPreferences` guarda solo preferencias. `SecureStorage` usa el almacén cifrado del sistema; cifrar a mano obliga a guardar la clave en algún lado. [Flet 1.1.0](https://raw.githubusercontent.com/flet-dev/flet/v1.1.0/website/docs/services/securestorage/index.md)
- Un secreto no va en el código fuente. [Flet 1.1.0](https://raw.githubusercontent.com/flet-dev/flet/v1.1.0/website/docs/cookbook/encrypting-sensitive-data.md)

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
| Flet 1.1.0, Pydantic 2.13.4 y dependencias exactas | [scripts/verificar.py](../scripts/verificar.py) |
