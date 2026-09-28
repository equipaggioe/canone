# Flet

Una aplicación en Flet. Se suma a [python.md](python.md).

## Proyecto

Estándar: [*Creating a new Flet app*](../estandares/flet/create-flet-app.md).

- En `src/`, al lado de `main.py` y `assets/`, van `api/` con el cliente y sus modelos, `views/`
  con una vista por ruta, y `theme.py`.

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

- Lo sensible va en `SecureStorage`, y `SharedPreferences` guarda solo preferencias.
  `SecureStorage` usa el almacén cifrado del sistema; cifrar a mano obliga a guardar la clave en
  algún lado.

## Publicación

Estándar: [*Publishing a Flet app*](../estandares/flet/publish.md).
