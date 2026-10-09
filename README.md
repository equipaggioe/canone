# canone

Cómo escribo el código. **No es una lista de lo que todo repositorio debe tener**: cada producto
elige sus piezas. Es la respuesta a «si uso X, ¿cómo lo uso?», escrita una sola vez.

Un repositorio que no tiene aplicación móvil no lee `plataformas/flutter.md`. Uno que no tiene web
no lee `plataformas/sveltekit.md`. Lo que sí aplica siempre son los principios de método, la
convención de `docs/` y lo mínimo del repositorio.

## Objetivo

canone fija las convenciones con las que se escriben todos mis proyectos, para que cualquiera de
ellos se lea, se construya y se mantenga igual que los demás. Esas convenciones tienen que ser las
más convenientes, y por eso salen primero de los estándares oficiales de cada tecnología:

- **Los escribe quien mejor conoce la tecnología** y una comunidad amplia los revisa antes de
  publicarlos. Recogen errores que un solo proyecto tardaría años en encontrar.
- **Las herramientas se construyen sobre ellos.** El formateador, el analizador y el framework dan
  por hecho que se sigue el estándar. Seguirlo exige menos configuración y da menos sorpresas.
- **Se actualizan con la tecnología.** Una regla propia envejece sin que nadie lo note.
- **Quien llega ya los conoce.** Una persona o un asistente nuevo no tiene que aprender
  convenciones privadas, y una elección que se cita no se vuelve a discutir.

Si la tecnología no dice nada sobre un asunto, se busca, en este orden, un estándar del campo, una
especificación de facto o una guía de una organización de referencia.

**Se cita lo que se adopta en su mayoría. Todo lo demás, venga de donde venga, es una regla
propia.** Citar una fuente es seguir todas sus convenciones. Las que una página contradice, deja
sin efecto o endurece se escriben como reglas, con su razón: la fuente es la base, no el techo.

El criterio completo está en [plataformas/README.md](plataformas/README.md).

## Índice

| Archivo | Cuándo aplica |
|---|---|
| [principios.md](principios.md) | Siempre. Método de trabajo, sin stack |
| [repositorio.md](repositorio.md) | Siempre. Git, estructura de carpetas, README, CI |
| [documentacion.md](documentacion.md) | Siempre. La convención `docs/` |
| [plataformas/](plataformas/) | **Solo la página de cada tecnología que el repositorio use** |
| [estandares/](estandares/) | Al escribir o revisar una página. Los textos de las fuentes que citan las páginas |
| [adr/](adr/) | Por qué cada regla es como es |
| [plantilla/](plantilla/) | Los archivos que se copian a un repositorio, por plataforma: canónicos o puntos de partida |
| [scripts/verificar.py](scripts/verificar.py) | Comprueba lo que aplica a cada repositorio, y falla si no se cumple |

## Plataformas documentadas

Qué es una página y de dónde sale: [plataformas/README.md](plataformas/README.md).

| Servidor y datos | Cliente | Transversal |
|---|---|---|
| [fastapi.md](plataformas/fastapi.md) | [sveltekit.md](plataformas/sveltekit.md) | [transversal.md](plataformas/transversal.md) |
| [postgres.md](plataformas/postgres.md) | [flutter.md](plataformas/flutter.md) | |
| [despliegue.md](plataformas/despliegue.md) | [flet.md](plataformas/flet.md) | |
| | [qt.md](plataformas/qt.md) | |

## Las dos reglas que sostienen esto

**Una regla se escribe una sola vez.** Un repositorio que necesita apartarse abre un ADR propio que
diga de qué se aparta y por qué, y lo enlaza desde su `docs/arquitectura/`. Si la desviación resulta
mejor, se promueve aquí.

**Una regla que se puede ejecutar, se ejecuta.** Cada página apunta al archivo de configuración, la
regla de lint o el script que la hace fallar sola. Una regla que solo vive en prosa se incumple sin
que nadie se entere: `models/base.py` existe en seis copias con cinco contenidos distintos, y nadie
lo notó.

## Verificar

```
python scripts/verificar.py --repo ../<repo>
python scripts/verificar.py --todos ..
```

Solo comprueba las plataformas que el repositorio realmente tiene: si no hay `server/`, no exige
nada de FastAPI.

Una mejora a un archivo canónico se hace primero en `plantilla/`, y desde ahí se copia a cada
repositorio.
