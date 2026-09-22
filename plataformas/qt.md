# PySide6 (Qt)

Aplica a un repositorio con aplicación de escritorio. Hoy: `consola`, `presenze/terminal` y
`spazio/app`.

Leído de esas tres. **`consola/ui` es la referencia**: es la única con tokens tipados, hoja de
estilos generada desde ellos y ayudantes de contraste.

## Layout

```
app/
  main.py               crea QApplication, aplica el tema, abre la ventana
  core/                 lo que no es interfaz
    api_client.py       QNetworkAccessManager + señales
    session.py          tokens y estado de sesión
    constants.py        URL del servidor, timeouts, tamaños
  ui/  (o views/)
    theme.py            tokens + hoja de estilos global
    main_window.py
    <vista>_view.py     una por pantalla
    <algo>_panel.py     paneles reutilizables
```

`consola` separa `core/` (catálogo, tareas, SSH, base) de `ui/` (vistas y paneles) y ninguna vista
habla con el sistema directamente. `presenze/terminal` usa `core/` + `views/`, que es lo mismo con
otro nombre. `spazio/app` tiene todo plano en la raíz (`api.py`, `theme.py`, `widgets.py`,
`pages/`), y se alinea a esta forma.

## Tema

**Todos los tokens en un módulo, y la hoja de estilos generada desde ellos.** Es lo que hace
`consola/ui/theme.py` y es lo que se adopta:

```python
class Colors:
    BG      = '#0d1117'
    SURFACE = '#1c212b'
    ACCENT  = '#58a6ff'
    ERROR   = '#f85149'

class Fonts:
    FAMILY = '"Inter", "Segoe UI", sans-serif'
    MONO   = '"Cascadia Code", "Consolas", monospace'
    SIZE_BASE = 15

class Spacing:  XS, SM, MD, LG, XL, XXL = 4, 8, 12, 16, 24, 32
class Radius:   SM, MD, LG, XL = 4, 8, 12, 16
```

```python
def apply_theme(app: QApplication) -> None:
    app.setFont(...)
    app.setStyleSheet(global_stylesheet())   # f-string que interpola los tokens
    app.setPalette(...)                      # la QPalette también sale de Colors
```

Las tres formas que hay hoy, y por qué gana esta:

| Forma | Dónde | Problema |
|---|---|---|
| Tokens + QSS generada desde ellos | `consola` | — |
| Archivo `.qss` estático | `presenze/terminal` (`theme_dark_glass.qss`) | Los colores viven dos veces: en el `.qss` y en el código que los necesita en Python |
| `STYLESHEET` global + `setStyleSheet` por widget | `spazio/app` | Tiene literales sueltos (`"font-size:18px; font-weight:bold;"`) que ningún token controla |

**Ningún color ni tamaño literal fuera del módulo de tema**, igual que en Flutter, Flet y UnoCSS. Si
el producto también tiene panel web, la paleta es la misma y el archivo dice de cuál es espejo
(`spazio/app/theme.py` ya lo declara: «replica los colores de `uno.config.js`»).

Dos ayudantes que valen la pena copiar de `consola/ui/theme.py`:

| Función | Qué resuelve |
|---|---|
| `tint(hex, alpha)` | `rgba(...)` desde un hex, para halos y fondos teñidos, sin inventar un token nuevo |
| `on_color(hex)` | Texto legible sobre ese fondo, por luminancia relativa (WCAG), en vez de elegir a ojo |

Además, `QPalette` se llena con los mismos tokens: sin eso, los diálogos nativos y los menús
contextuales quedan con los colores del sistema y no con los de la aplicación.

## Red

`QNetworkAccessManager` con señales, no `requests` en el hilo de la interfaz: una petición síncrona
congela la ventana. `spazio/app` depende de `requests`, y ahí hay que revisar desde qué hilo se
llama.

El sobre de error del servidor se traduce a una excepción tipada con los mismos campos que en las
otras plataformas — ver [fastapi.md](fastapi.md):

```python
@dataclass(frozen=True)
class ApiError:
    path: str
    status_code: int | None
    detail: str
    error_code: str | None
    request_id: str | None
```

`presenze/terminal` ya lo tiene así, y es idéntico en forma al de `presenze/app`, que es Flet. Esa
es la convención que importa: **la plataforma cambia el transporte, no el contrato**.

## Trabajo pesado

Nada que tarde corre en el hilo de la interfaz. `consola` tiene un worker dedicado para la base
(`ui/db_worker.py`) y ejecuta las tareas largas fuera del hilo principal; una consulta síncrona en
el hilo de la ventana la congela sin aviso.

## Dependencias y lint

`pyproject.toml` + `uv.lock` como cualquier pieza de Python — ver
[ADR-0006](../adr/0006-dependencias-con-pyproject-y-uv.md). Hoy las tres usan `requirements.txt`, y
`presenze/requirements.txt` además arrastra `psycopg2-binary`, `python-jose` y `passlib[bcrypt]`,
que están reemplazados — ver [fastapi.md](fastapi.md).

`ruff` y `mypy` con la misma configuración que el servidor. Hoy ninguna de las tres los tiene.
