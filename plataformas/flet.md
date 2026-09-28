# Flet

Cliente en Flet. Se suma a [python.md](python.md).

## Layout

Estándar: [*Creating a new Flet app*](../estandares/flet/create-flet-app.md) de Flet.

```
app/
  pyproject.toml
  src/
    main.py
    assets/
    core/
      api_client.py
      session.py
      constants.py
      theme.py
      device.py
      native.py
      offline_queue.py
      i18n.py
    views/
      components/
      <dominio>/
    locales/
  tests/
```

- La red, el almacenamiento y el sistema se tocan desde `core/`. `views/` solo arma y muestra.
- Una vista por área, en `views/<dominio>/`. Lo que usan varias áreas va en `views/components/`.
- El código que comparten dos apps del mismo producto es un paquete de `packages/`.
- `src/.flet/storage/`, el estado local del SDK, va en el `.gitignore`.

## Cliente de la API

- HTTP con `httpx.AsyncClient`, en `core/api_client.py`, con la `base_url` y el timeout de
  `core/constants.py`.
- El sobre de error se traduce a `ApiError`, con `path`, `status_code`, `detail`, `type` y
  `trace_id`.

## Tema

Estándar: [*Theming*](../estandares/flet/theming.md) de Flet.

- Un solo tema para toda la app: `page.theme` y `page.dark_theme`, armados en `core/theme.py`.

## Sesión y almacenamiento

Estándares: [*Client Storage*](../estandares/flet/client-storage.md) y
[`SecureStorage`](../estandares/flet/securestorage.md) de Flet.

- Los tokens van en `SecureStorage`: usa el almacén seguro de cada plataforma.
- Las preferencias van en `SharedPreferences`.
- El estado de sesión vive en `core/session.py`, y el cliente de la API lo recibe al crearse.
- Lo que no se pudo enviar va a la cola de `core/offline_queue.py`.
