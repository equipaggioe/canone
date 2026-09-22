# Flet

Cómo se construye un cliente en Flet.

## Layout

```
app/
  pyproject.toml        dependencias con uv
  run_app.py            arranque; no un comando que haya que recordar
  src/
    main.py
    core/
      api_client.py     httpx async, sobre de error tipado
      session.py        tokens y estado de sesión
      constants.py      URL del servidor, timeouts
      theme.py          tokens de diseño
      device.py         identidad del dispositivo
      native.py         lo que toca el sistema
      offline_queue.py  lo que no se pudo enviar
      i18n.py
    views/
      components/       widgets compartidos
      <dominio>/        una carpeta por área
    locales/
    assets/
```

`core/` y `views/` separados: ninguna vista habla con la red ni con el sistema directamente.

El código compartido entre dos apps del mismo producto va en un paquete local instalable
(`api.py`, `session.py`, `secure_store.py`, `models.py`, `i18n.py`), no copiado.

`src/.flet/storage/` es estado local del SDK: va al `.gitignore`.

## Cliente de la API

`httpx.AsyncClient` con `base_url` y timeout de `constants.py`. Adjunta el access token en cada
llamada autenticada y, ante un 401, **refresca la sesión una sola vez** antes de reintentar — igual
de una vez, sin bucles de reintento silenciosos.

El sobre de error se traduce a una excepción tipada, no a un `dict`:

```python
@dataclass(frozen=True)
class ApiError(Exception):
    path: str
    status_code: int | None
    detail: str
    error_code: str | None
    request_id: str | None
```

La interfaz ramifica sobre `error_code` y muestra `detail` — ver [fastapi.md](fastapi.md).

## Tema

Un módulo de constantes y **ningún color literal fuera de él**. Si el producto tiene superficie web,
la paleta es la misma y el archivo declara de cuál es espejo.

## Sesión y almacenamiento

- Los tokens van al almacenamiento seguro de la plataforma, nunca a un JSON al lado del código.
- El estado de sesión vive en un solo módulo, y el cliente de la API lo recibe inyectado, no lo
  importa global.
- Lo que no se pudo enviar va a una cola explícita, no se pierde en silencio.

## Textos

Un módulo `i18n.py` y un catálogo por idioma en `locales/`. Ningún texto visible se escribe dentro
de un widget — ver [i18n.md](i18n.md).

## Dependencias, lint y tipos

`pyproject.toml` + `uv.lock`. Es Python: `ruff` y `mypy` con la misma configuración que el servidor
— ver [fastapi.md](fastapi.md).
