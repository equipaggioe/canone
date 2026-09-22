# canone

Lo que comparten todos los repositorios: principios, stack, convenciones y decisiones
transversales. **Es la única fuente de estas reglas.** Ningún repositorio las copia.

## Cómo se usa

| Quién | Qué hace |
|---|---|
| Una persona | Lee `principios.md` y la convención del área que va a tocar |
| Un asistente de IA | `~/.claude/CLAUDE.md` lo apunta aquí; lee `principios.md` y la convención del área |
| Un repositorio nuevo | Se crea desde `plantilla/`, que ya materializa estas reglas |
| Un repositorio existente | Se homologa siguiendo `homologacion.md` |

## Índice

| Archivo | Responde |
|---|---|
| [principios.md](principios.md) | Cómo se trabaja y por qué. Reglas de método, válidas en cualquier proyecto |
| [stack.md](stack.md) | Qué tecnología se usa, cuál está a prueba y cuál está prohibida |
| [convenciones/repo.md](convenciones/repo.md) | Estructura de carpetas, nombres de superficies, git, CI |
| [convenciones/servidor-python.md](convenciones/servidor-python.md) | Layout de `server/`, modelos, schemas, servicios, routers |
| [convenciones/datos.md](convenciones/datos.md) | PostgreSQL, PostGIS, tipos, nombres, migraciones |
| [convenciones/api.md](convenciones/api.md) | Prefijo, envoltorios de respuesta, errores, paginación |
| [convenciones/web.md](convenciones/web.md) | SvelteKit, UnoCSS, adaptadores, build |
| [convenciones/documentacion.md](convenciones/documentacion.md) | La convención `docs/` de cada repositorio |
| [homologacion.md](homologacion.md) | Qué divergencia tiene hoy cada repositorio y qué le falta |
| [adr/](adr/) | Por qué cada regla es como es |
| [plantilla/](plantilla/) | Los archivos que un repositorio copia tal cual |
| [scripts/verificar.py](scripts/verificar.py) | Comprueba que un repositorio cumpla, y falla si no |

## Verificar

```
python scripts/verificar.py --repo ../navetta
python scripts/verificar.py --todos ..
```

Cada incumplimiento cita el ADR o la convención que lo fija. Corre en el CI de cada repositorio.

## La regla que sostiene todo esto

**Una regla se escribe una sola vez.** Un repositorio que necesita apartarse de una regla no la
reescribe: abre un ADR propio que diga de qué se aparta y por qué, y lo enlaza desde su
`docs/arquitectura/`. Si la desviación resulta mejor que la regla, se promueve aquí y el ADR del
repositorio se marca como reemplazado.

**Una regla que se puede ejecutar, se ejecuta.** Cada convención de este repositorio apunta al
archivo de configuración, la regla de lint o el script que la hace fallar sola. Una regla que solo
vive en prosa se incumple sin que nadie se entere: `models/base.py` ya existe en seis copias con
cinco contenidos distintos, y nadie lo notó.
