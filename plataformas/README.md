# Plataformas

Una página por tecnología, y [transversal.md](transversal.md) con lo que cumplen juntas varias
piezas. **Se lee la de lo que el repositorio use**, junto con transversal.md; las demás no aplican.

| Página | Cubre |
|---|---|
| [transversal.md](transversal.md) | Errores, nombres en el cable, montos, versión mínima, sesión, tema, idiomas, accesibilidad, WebSocket, llamadas, push, pagos, archivos, mapas |
| [python.md](python.md) | Versión, uv, estilo, tipos, paquetes, logging, fechas, archivos de texto, async, pruebas, seguridad, auditoría de dependencias |
| [fastapi.md](fastapi.md) | Layout, configuración, SQLAlchemy async, migraciones, errores RFC 9457, trazas, fechas, montos, paginación, contraseñas, tokens, segundo factor, límite de tasa, permisos, WebSocket, push, correo, pagos, archivos, direcciones, OpenAPI, pruebas |
| [postgres.md](postgres.md) | Clave primaria, tipos, montos, borrado, nombres, índices, geografía |
| [sveltekit.md](sveltekit.md) | Proyecto, carga de datos, cliente generado, adaptador estático, CSP, estado, UnoCSS, idiomas, accesibilidad, mapas, pruebas |
| [flutter.md](flutter.md) | Estilo, analizador, arquitectura, modelos, estado, tema, almacenamiento, idiomas, accesibilidad, mapas |
| [android.md](android.md) | Gradle, estilo, arquitectura, red, Compose, tema, almacenamiento, idiomas, accesibilidad, mapas, pruebas |
| [flet.md](flet.md) | Layout, tema, red, almacenamiento, idiomas, accesibilidad, mapas, publicación |
| [qt.md](qt.md) | Layout, API de PySide6, `@override`, interfaz en código, `QSettings`, Fusion y hoja de estilo, idiomas, accesibilidad, red, pruebas, empaquetado |
| [despliegue.md](despliegue.md) | Caddy, cabeceras, límite del cuerpo, servicios de systemd, configuración, datos, registros, respaldos, coturn |

## Qué es una página

Un catálogo de convenciones de una tecnología. Una convención sirve para una de tres cosas:

- **Que todos los repositorios se lean igual:** el mismo layout y los mismos nombres.
- **Que cada elección se tome una sola vez:** la tecnología, la biblioteca, la versión y la
  configuración.
- **Que las piezas de un sistema se entiendan:** el servidor y sus clientes cumplen el mismo
  contrato, como el sobre de error, los nombres en el cable o la sesión.

Una regla que no sirve para ninguna de las tres no va. Una convención vale aunque ninguna
herramienta la haga cumplir.

### Los estándares son las convenciones

- Cada sección nombra los estándares que sigue y enlaza su texto en [estandares/](../estandares/).
  Esos estándares son las convenciones de la sección: lo que recomiendan se hace como si fuera
  obligatorio, y no se escribe.
- Es oficial el texto normativo de un estándar (MUST, SHOULD o RECOMMENDED) y la recomendación
  escrita en la documentación de la tecnología, en su versión más reciente. Nada más: ni el código
  de sus ejemplos, ni sus proyectos de muestra, ni lo que hace la comunidad. Una regla que sale de
  ahí es propia.
- El comportamiento por defecto de una herramienta no es una recomendación. Si la página no dice
  nada, rige; cambiarlo es oficial solo si la documentación lo pide.
- Contradecir una parte de un estándar no lo quita: el resto sigue rigiendo.
- Una página está completa cuando sus estándares cubren todo lo que la tecnología obliga a decidir.

### Qué escribe la página

Sobre sus estándares, solo tres cosas. Una sección sin puntos sigue su estándar entero.

- La opción que elige donde el estándar deja varias.
- Lo que contradice o endurece del estándar. Endurecer es volver obligatorio lo que el estándar
  recomienda «cuando sea posible» o deja como preferencia.
- Lo que ningún estándar cubre.

Cómo se escribe:

- Cada regla dice qué se usa y cómo queda. No es un procedimiento ni un tutorial.
- Sin comentarios ni explicaciones, salvo dos, cada una en una frase corta: por qué la página
  contradice o endurece el estándar, y cómo ayuda una elección que no es trivial. Una regla trivial,
  como un color o el largo de línea, no lleva frase: su razón es una preferencia. Vale también para
  los comentarios de `plantilla/`.
- El layout se dibuja completo, como árbol, aunque repita partes del estándar. El árbol es la
  convención misma, y a pedazos no se lee.

### Cómo se hace cumplir

- La tabla «Cómo se hace cumplir» nombra en su primera columna el estándar o su sección, o una
  regla que la página ya escribió. Nunca redacta una regla nueva para llenar la fila.
- Una herramienta que marca más de lo que la regla dice impone una regla no escrita, y no va.

### Alcance

- Hereda de su página madre y no repite nada de ella: `fastapi.md`, `flet.md` y `qt.md` heredan de
  `python.md`.
- Dice solo lo que hace su pieza. Lo que tienen que cumplir juntas varias piezas va en
  [transversal.md](transversal.md), y la sección de cada pieza que lo implementa enlaza ahí: quien
  trabaja en una pieza encuentra sus reglas en su página.
- Nombra los archivos de `plantilla/` que salen de ella.
- No dice qué repositorio la usa ni cuándo elegir una plataforma sobre otra.

### Fuentes

Ni el código de los repositorios, ni lo que la página ya dice, ni los ADR son fuente. Una página se
escribe de cero desde sus estándares, nunca corrigiendo la versión anterior.

Se agrega una página cuando la tecnología se estrena en algún repositorio.

El porqué, en el [ADR-0018](../adr/0018-una-pagina-se-revisa-contra-la-copia-de-sus-estandares-y-solo-dice-lo-que-elige-endurece-o-no-cubren.md)
y el [ADR-0028](../adr/0028-una-pagina-esta-completa-cuando-sus-estandares-cubren-lo-que-hay-que-decidir.md).
