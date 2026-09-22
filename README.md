# canone

Cómo escribo el código. **No es una lista de lo que todo repositorio debe tener**: cada producto
elige sus piezas. Es la respuesta a «si uso X, ¿cómo lo uso?», escrita una sola vez.

Un repositorio que no tiene aplicación móvil no lee `plataformas/flutter.md`. Uno que no tiene web
no lee `plataformas/sveltekit.md`. Lo que sí aplica siempre son los principios de método, la
convención de `docs/` y lo mínimo del repositorio.

## Índice

| Archivo | Cuándo aplica |
|---|---|
| [principios.md](principios.md) | Siempre. Método de trabajo, sin stack |
| [repositorio.md](repositorio.md) | Siempre. Git, estructura de carpetas, README, CI |
| [documentacion.md](documentacion.md) | Siempre. La convención `docs/` |
| [plataformas/](plataformas/) | **Solo la página de cada tecnología que el repositorio use** |
| [homologacion.md](homologacion.md) | Qué divergencias hay hoy, agrupadas por plataforma |
| [adr/](adr/) | Por qué cada regla es como es |
| [plantilla/](plantilla/) | Los archivos que se copian tal cual, por plataforma |
| [scripts/verificar.py](scripts/verificar.py) | Comprueba lo que aplica a cada repositorio, y falla si no se cumple |

## Plataformas documentadas

Una página existe porque la tecnología ya está en uso en algún repositorio. No se documenta lo que
no se usa, y usar una tecnología nueva empieza por escribir su página leyendo el código que la
estrenó.

| Plataforma | Página | Dónde está en uso hoy |
|---|---|---|
| FastAPI + SQLAlchemy async | [fastapi.md](plataformas/fastapi.md) | Los 6 servidores |
| PostgreSQL y PostGIS | [postgres.md](plataformas/postgres.md) | Los 6 |
| SvelteKit + UnoCSS | [sveltekit.md](plataformas/sveltekit.md) | 15 superficies web |
| Flutter | [flutter.md](plataformas/flutter.md) | navetta (3 apps), vettore |
| Flet | [flet.md](plataformas/flet.md) | presenze (2), banditore (2), cadenza |

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
python scripts/verificar.py --repo ../navetta
python scripts/verificar.py --todos ..
```

Solo comprueba las plataformas que el repositorio realmente tiene: si no hay `server/`, no exige
nada de FastAPI.
