# Flet

Una aplicación en Flet. Se suma a [python.md](python.md).

## Proyecto

Estándares: [*Creating a new Flet app*](../estandares/flet/create-flet-app.md) y la
[estructura del proyecto](../estandares/flet/publish.md) que supone `flet build`.

```text
<pieza>/
  pyproject.toml
  uv.lock
  src/
    main.py
    theme.py
    assets/
      icon.png
    api/              el cliente y sus modelos
    views/            una vista por ruta
  tests/
    __init__.py
    test_theme.py
```

- El código va directo en `src/`, y el proyecto no lleva `[build-system]`. Contradice el
  `src/app/` y el `uv_build` de [python.md](python.md): es la estructura que supone
  `flet build`, que empaqueta `src/` por su cuenta.
- `[tool.flet.app]` lleva `path = "src"`.

Plantilla: [`plantilla/flet/`](../plantilla/flet/). `tests/test_theme.py` es canónico y se copia
sin editar; `theme.py` es un punto de partida.

## Tema

Estándar: [*Theming*](../estandares/flet/theming.md) de Flet.

- `page.theme` y `page.dark_theme` salen de `theme.py`, y `page.theme_mode` es
  `ThemeMode.SYSTEM`. La app sigue el modo oscuro del sistema, con los colores en un solo módulo.

## Red

- HTTP va por un solo `httpx.AsyncClient` desde handlers async, y las respuestas se leen con modelos
  de Pydantic en `api/`. No bloquea la interfaz y reutiliza las conexiones.

## Almacenamiento

Estándares: [*Client Storage*](../estandares/flet/client-storage.md),
[*Session Storage*](../estandares/flet/session-storage.md),
[`SecureStorage`](../estandares/flet/securestorage.md) y
[*Encrypting sensitive data*](../estandares/flet/encrypting-sensitive-data.md) de Flet.

- Lo sensible, como el token de refresco que pide [transversal.md](transversal.md#sesión), va en
  `SecureStorage`, y `SharedPreferences` guarda solo preferencias. `SecureStorage` usa el almacén
  cifrado del sistema; cifrar a mano obliga a guardar la clave en algún lado.

## Idiomas

Contrato: [transversal.md](transversal.md#idiomas).

- Los textos usan `gettext` de la biblioteca estándar de Python, con catálogos `.po`. Flet no trae
  un sistema de traducción.

## Accesibilidad

Estándar: [*Accessibility*](../estandares/flet/accessibility.md) de Flet.

Contrato: [transversal.md](transversal.md#accesibilidad).

## Mapas

Estándar: [flet-map](../estandares/flet/map.md).

Contrato: [transversal.md](transversal.md#mapas).

## Publicación

Estándar: [*Publishing a Flet app*](../estandares/flet/publish.md).

## Cómo se hace cumplir

| Qué | Con qué |
|---|---|
| Los colores, solo en `theme.py` | `tests/test_theme.py` |
