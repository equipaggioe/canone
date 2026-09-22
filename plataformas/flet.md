# Flet

Aplica a un repositorio con cliente en Flet. Hoy: `presenze` (`app`, `terminal`), `banditore`
(`customer`, `vendor`, `mobile_common`) y `cadenza` (`frontend`).

Leído de esas seis piezas. **`presenze/app` es la referencia de estructura** y `banditore` la de
empaquetado y código compartido. `cadenza/frontend` está plano y con datos mock; no es modelo.

Flet se elige cuando la pieza la operamos nosotros o vive en hardware propio, y no hay que salir del
lenguaje del servidor. Una app que se publica en tiendas y necesita segundo plano, push confiable o
hardware es un caso de [flutter.md](flutter.md). Ese criterio hoy no está escrito en ningún ADR:
`presenze/terminal` y `banditore/customer` no se compararon contra él.

## Layout

El de `presenze/app`:

```
app/
  pyproject.toml        dependencias con uv
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
      sync.py
    views/
      components/       widgets compartidos
      <dominio>/        una carpeta por área
    assets/
```

`core/` y `views/` separados. banditore usa `pages/` + `components/` con el resto plano en `src/`, y
`cadenza` tiene todo suelto con un `app_state.py`: las dos se alinean a esta forma.

El código compartido entre dos apps del mismo producto va en un paquete local instalable, como
`banditore/mobile_common` (`api.py`, `session.py`, `secure_store.py`, `models.py`, `i18n.py`), no
copiado.

## Cliente de la API

`httpx.AsyncClient` con `base_url` y timeout de `constants.py`. El de `presenze/app` es el modelo, y
su docstring ya fija la regla que importa:

> Adjunta el access token en cada llamada autenticada y, ante un 401, intenta refrescar la sesión
> **una sola vez** antes de reintentar — igual de una vez, sin bucles de reintento silenciosos.

El sobre de error del servidor se traduce a una excepción tipada, no a un `dict`:

```python
@dataclass(frozen=True)
class ApiError(Exception):
    path: str
    status_code: int | None
    detail: str
    error_code: str | None
    request_id: str | None
```

Los campos son los del sobre de [fastapi.md](fastapi.md). La interfaz ramifica sobre `error_code` y
muestra `detail`.

## Tema

Un módulo de constantes y **ningún color literal fuera de él**, igual que en Flutter. El
`core/theme.py` de presenze lo dice explícitamente y además declara de dónde sale la paleta:

> Espejo de `panel/src/app.css` y `terminal/src/core/constants.py`: los tres frontends comparten el
> mismo lenguaje visual.

Cuando el producto tiene panel web, la paleta de Flet es la misma que la de UnoCSS, y el archivo
dice de cuál es espejo.

## Sesión y almacenamiento

- Los tokens van al almacenamiento seguro de la plataforma (`secure_store.py` de
  `banditore/mobile_common`), nunca a un JSON al lado del código.
- El estado de sesión vive en un solo módulo (`core/session.py`), y el cliente de la API lo recibe
  inyectado, no lo importa global.
- Lo que no se pudo enviar va a una cola explícita (`offline_queue.py`), no se pierde en silencio.

## Dependencias y empaquetado

`pyproject.toml` + `uv.lock`, como ya hacen `banditore/customer`, `banditore/vendor` y
`mobile_common` — ver [ADR-0006](../adr/0006-dependencias-con-pyproject-y-uv.md). `presenze/app`,
`presenze/terminal` y `cadenza/frontend` todavía usan `requirements.txt`.

Un script de arranque por pieza en su raíz (`run_vendor.py`, `run_flet.py`), no un comando que haya
que recordar.

`src/.flet/storage/` es estado local del SDK: va al `.gitignore`.

## Lint y tipos

Es Python: valen `ruff` y `mypy` con la misma configuración que el servidor — ver
[fastapi.md](fastapi.md). Hoy ninguna pieza Flet los tiene configurados.
