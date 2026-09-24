# PySide6 (Qt)

Cómo se construye una aplicación de escritorio.

## Layout

```
app/
  main.py               crea QApplication, aplica el tema, abre la ventana
  core/                 lo que no es interfaz
    api_client.py       QNetworkAccessManager + señales
    session.py          tokens y estado de sesión
    constants.py        URL del servidor, timeouts, tamaños
  ui/
    theme.py            tokens + hoja de estilos global
    main_window.py
    <vista>_view.py     una por pantalla
    <algo>_panel.py     paneles reutilizables
```

Ninguna vista habla con la red, la base ni el sistema directamente.

## Tema

**Todos los tokens en un módulo, y la hoja de estilos generada desde ellos.** Nunca un `.qss`
estático con los colores escritos aparte, ni `setStyleSheet` con literales dentro de un widget: en
los dos casos los colores viven dos veces y uno de los dos se queda viejo.

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
    app.setPalette(palette_from(Colors))
```

**La `QPalette` se llena con los mismos tokens.** Sin eso, los diálogos nativos y los menús
contextuales salen con los colores del sistema y no con los de la aplicación.

Dos ayudantes que evitan inventar tokens y elegir colores a ojo:

| Función | Qué resuelve |
|---|---|
| `tint(hex, alpha)` | `rgba(...)` desde un hex, para halos y fondos teñidos |
| `on_color(hex)` | Color de texto legible sobre ese fondo, por luminancia relativa (WCAG) |

Si el producto también tiene superficie web, la paleta es la misma y el archivo dice de cuál es
espejo.

## Red

`QNetworkAccessManager` con señales. **Nada de `requests` en el hilo de la interfaz**: una petición
síncrona congela la ventana.

El sobre de error se traduce a un error tipado con los mismos campos que en las demás plataformas:
la plataforma cambia el transporte, no el contrato — ver [fastapi.md](fastapi.md).

## Hilos

Nada que tarde corre en el hilo de la interfaz. Las consultas a la base van en un worker dedicado y
las tareas largas, fuera del hilo principal. Una consulta síncrona en el hilo de la ventana la
congela sin aviso y sin error.

## Dependencias, lint y tipos

Los de [python.md](python.md). Los métodos que Qt obliga a sobrescribir (`paintEvent`, `rowCount`,
`eventFilter`) llevan `@override`: así conservan su nombre en camelCase sin apagar `N802`.
