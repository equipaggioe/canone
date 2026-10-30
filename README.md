# canone

Cómo escribo el código. **No es una lista de lo que todo repositorio debe tener**: cada producto
elige sus piezas. Es la respuesta a «si uso X, ¿cómo lo uso?», escrita una sola vez.

Un repositorio que no tiene aplicación móvil no lee `plataformas/flutter.md`. Uno que no tiene web
no lee `plataformas/sveltekit.md`. Lo que sí aplica siempre son los principios de método, la
convención de `docs/` y lo mínimo del repositorio.

## Objetivo

canone fija las convenciones con las que se escriben todos mis proyectos, para que cualquiera de
ellos se lea, se construya y se mantenga igual que los demás. Esas convenciones tienen que ser las
más convenientes, y por eso salen primero de los estándares y la documentación oficial de cada
tecnología:

- **Los escribe quien mejor conoce la tecnología** y una comunidad amplia los revisa antes de
  publicarlos. Recogen errores que un solo proyecto tardaría años en encontrar.
- **Las herramientas se construyen sobre ellos.** El formateador, el analizador y el framework dan
  por hecho que se siguen. Seguirlos exige menos configuración y da menos sorpresas.
- **Se actualizan con la tecnología.** Una regla propia envejece sin que nadie lo note.
- **Quien llega ya los conoce.** Una persona o un asistente nuevo no tiene que aprender
  convenciones privadas, y una elección que se cita no se vuelve a discutir.

El criterio completo está en [plataformas/README.md](plataformas/README.md).

Lo que una convención exige en una máquina, canone lo da también como el programa que la deja así:
cambia junto con sus plantillas, y solo instalándola se prueba entera.

## Quién hace qué

Por qué se reparte así: [ADR-0075](adr/0075-canone-fija-el-repositorio-declara-y-consola-dispara.md)
y [ADR-0107](adr/0107-canone-fija-la-interfaz-de-sus-programas-y-no-la-herramienta-que-los-corre.md).

| Quién | Qué hace | Qué no hace |
|---|---|---|
| **canone** | Fija las reglas, da las plantillas y fija cada programa por su interfaz: sus argumentos y su stdin | No guarda datos de ninguna app, no decide cuándo se corre nada ni nombra con qué se corre |
| **El repositorio** | Sigue las reglas, copia las plantillas que se copian y declara sus datos: nombre, superficies y campos de `Settings` | No reimplementa una plantilla ni decide cómo se instala |
| **Quien despliega** | Corre los programas de canone por su interfaz, a mano o con la herramienta que elija | No escribe encima de lo que instalan: ni unidades, ni configuración, ni scripts propios |

- Una plantilla **que se copia**, como `release.yml`, vive en el repositorio.
- Una plantilla **que se instala**, como `infra/` con su `deploy.py`, se toma de canone.
- Lo que cambia entre despliegues, secreto o no, no se commitea: el repositorio declara el campo, y
  el valor llega al servidor como argumento de `install.py`, como el dominio y la memoria, o por
  `credentials.py`. canone no fija dónde lo guarda quien despliega.

## Índice

| Archivo | Cuándo aplica |
|---|---|
| [principios.md](principios.md) | Siempre. Método de trabajo, sin stack |
| [repositorio.md](repositorio.md) | Siempre. Git, estructura de carpetas, README, CI |
| [documentacion.md](documentacion.md) | Siempre. La convención `docs/` |
| [plataformas/](plataformas/) | **Solo la página de cada tecnología que el repositorio use** |
| [fuentes/](fuentes/) | Al escribir o revisar una página. Los textos de las fuentes que citan las páginas |
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
