# Homologación: qué tiene hoy cada repositorio

Inventario verificado el 2026-09-22 leyendo el código de `navetta`, `presenze`, `vettore`,
`banditore`, `concordia`, `cadenza` y `consola`. Cada fila dice qué variantes existen, cuál se
adopta y por qué. Las que aún no fueron confirmadas están como **propuesta**.

## Lo que ya es uniforme

No hay nada que decidir aquí; solo hay que impedir que se separe.

| Pieza | Valor |
|---|---|
| Backend | FastAPI + SQLAlchemy 2 async + asyncpg + Alembic + PostgreSQL |
| `server/app/schemas/base.py` | Idéntico byte a byte en los 6 repositorios |
| `server/alembic.ini` | Idéntico en los 6 |
| Serialización | Pydantic v2, `alias_generator=to_camel`, entrada y salida en camelCase |
| Web | SvelteKit 2 + Svelte 5 + UnoCSS + TypeScript + Vite |
| Convención de docs | `arquitectura/` + `adr/` + `planes/` en los 6 |
| Marcador de repo | `.consola/params.json` en los 6 |

## Divergencias del servidor

| # | Tema | Qué hay hoy | Se adopta | Por qué |
|---|---|---|---|---|
| 1 | `StringEnumType`, CHECK | `create_constraint=True` en banditore y concordia; ausente en navetta, presenze, vettore, cadenza | **concordia** | Sin el CHECK, `native_enum=False` deja un TEXT pelado: `validate_strings` solo valida del lado de Python y la base acepta cualquier cadena escrita por SQL directo o una carga masiva |
| 2 | Columnas geográficas | `Annotated[..., mapped_column(Geography(...))]` en 5 repositorios; funciones `geo_point()` / `geo_line()` en concordia | **concordia** | geoalchemy2 guarda `nullable` en la instancia del tipo y la muta por columna; un `Annotated` comparte una sola instancia, así que la última columna procesada le impone su `nullable` a todas las demás, en silencio |
| 3 | `expire_on_commit` | `False` en presenze, vettore, banditore, concordia; default `True` en navetta | **`False`** | Una `AsyncSession` no puede hacer lazy-load: leer un modelo después del commit revienta |
| 4 | `rollback` en `get_db` | Solo concordia | **concordia** | Sin él, un servicio que falla a mitad de una escritura devuelve la conexión al pool con la transacción abierta |
| 5 | `pool_pre_ping` | navetta, vettore, banditore sí; presenze y concordia no | **sí** | Las bases se alcanzan por túnel; una conexión muerta en el pool falla el primer request que la tome |
| 6 | `UpdatedAt` | `datetime \| None` en 5; `datetime` en banditore | **banditore** *(propuesta)* | Lleva `server_default=now()`, así que la columna nunca es nula: el tipo opcional describe algo que no ocurre y obliga a comprobaciones que nunca se cumplen |
| 7 | Carpeta de routers | `routers/` en navetta, presenze, vettore, concordia; `api/routers/` en banditore; `api/` vacío en cadenza | **`routers/`** *(propuesta)* | Mayoría, y un nivel menos. Las dependencias van en `core/deps.py` |
| 8 | Prefijo de la API | Sin prefijo (navetta, vettore); `/api` en cada router (presenze); `/api` en `include_router` (concordia); `/api/v1` (banditore) | **`/api` en `include_router`** *(propuesta)* | Un solo lugar que cambiar. Sin `v1`: ningún repositorio está en producción y no hay cliente viejo que sostener |
| 9 | Dependencias de Python | `requirements.txt` en los 6; `pyproject.toml` además en banditore y concordia; `uv.lock` en las apps Flet de banditore | **`pyproject.toml` + `uv`** *(propuesta)* | Ya está en uso y es lo único que fija versiones de forma reproducible. `requirements.txt` no tiene lock |
| 10 | Lint y tipos | Solo concordia tiene `ruff` + `mypy` configurados | **concordia** | Es la única configuración que existe |
| 11 | Configuración de pytest | `pyproject.toml` en banditore y concordia; `pytest.ini` en vettore; ninguna en navetta, presenze, cadenza | **`pyproject.toml`** | Un archivo de configuración por proyecto |
| 12 | CI | Solo concordia (`ci.yml`: ruff, mypy, pytest, svelte-check, build) | **concordia** | Es la única regla que hoy se hace cumplir sola |
| 13 | Cobertura de tests | vettore 39 archivos, presenze 20, concordia 16, banditore 7, navetta 4, cadenza 0 | — | No es una convención; es deuda. Va al documento 30 de cada repositorio |

### Defectos encontrados de paso (sin confirmar)

| Repositorio | Hallazgo |
|---|---|
| cadenza | Hay dos clases `Base` declaradas, `app/db/base.py` y `app/models/base.py`, con mapas de tipos distintos. `app/db/__init__.py` exporta la primera |
| cadenza | `server/app/main.py` está vacío (0 líneas) y `app/api/` no tiene routers |
| cadenza | No existe `app/core/settings.py` ni `app/core/database.py` |

## Divergencias del cliente

| # | Tema | Qué hay hoy | Se adopta | Por qué |
|---|---|---|---|---|
| 14 | Adaptador de SvelteKit | `adapter-static` en todas las landings, en el panel y el backoffice de vettore, y en el backoffice y la pwa de concordia; `adapter-auto` en el panel de navetta y presenze y en el backoffice de banditore y cadenza | **`adapter-static`** *(propuesta)* | Todo se sirve con Caddy desde el VPS. `adapter-auto` elige un adaptador de plataforma (Vercel, Netlify) que no se usa |
| 15 | Línea de versiones | vettore en Vite 8 / TypeScript 6 / plugin-svelte 7; los otros cinco en Vite 7 / TypeScript 5 / plugin-svelte 6 | **la de vettore** *(propuesta)* | Ningún repositorio está en producción; sostener dos líneas mayores es costo sin beneficio |
| 16 | Nombre de la superficie | `panel` en navetta, presenze, vettore; `backoffice` en banditore, concordia, cadenza; vettore tiene las dos | **`panel` = cliente; `backoffice` = operación** | En vettore ya significan cosas distintas y funciona: `panel/` es el cliente web del usuario final y `backoffice/` la operación interna del producto. Falta verificar qué es hoy el `backoffice/` de banditore, concordia y cadenza, y renombrarlo si en realidad es el panel del cliente |
| 17 | `vitest` | Configurado en navetta/panel, vettore/panel, vettore/backoffice, concordia/pwa; ausente en el resto | **presente en toda superficie con lógica propia** | |
| 18 | Cliente nativo | Flutter en navetta (3 apps) y vettore; Flet en presenze (`app/`, `terminal/`), banditore (`customer/`, `vendor/`) y cadenza (`frontend/`); SvelteKit PWA en concordia | **sin decidir — hay que elegir** | Tres tecnologías de cliente para el mismo problema es el punto más caro del inventario. Ver [adr/0008](adr/0008-un-solo-cliente-nativo.md) |

## Divergencias del repositorio

| # | Tema | Qué hay hoy | Se adopta | Por qué |
|---|---|---|---|---|
| 19 | `.gitattributes` | No existe en ninguno | **se agrega** | `navetta/.gitignore` ya mezcla CRLF y LF dentro del mismo archivo. Sin `.gitattributes`, un diff puede aparecer como el archivo entero cambiado |
| 20 | `node_modules` en el `.gitignore` raíz | Ausente en los 6; cubierto por el `.gitignore` de cada superficie web | **se sube al raíz** | Hoy depende de que toda superficie nueva traiga el suyo; `banditore/customer` y `cadenza/frontend` no lo tienen |
| 21 | `docs/` con archivos sueltos | banditore (`api_response_standard.md`, `descripcion.md`, `implementaciones_futuras.md`), cadenza (`memoria_tecnica.md`), presenze (`4500/`, `mockups/`) | **se reubica** | La convención ya dice dónde va cada cosa: el estándar de respuesta pasa a `canone/convenciones/api.md`, las implementaciones futuras al documento 30, y el resto a `arquitectura/` o se borra |
| 22 | `README.md` raíz | Solo vettore | **se agrega en todos** | Qué es el repositorio, cómo se levanta, y un enlace a `docs/` y a `canone` |

## Ya existía un intento: `.commons`

`E:\Git\.commons` es un repositorio con `general_style.md`, `estandar_archivos_maestros.md`,
`estandares/api_response.md` y `estandares/api_response_multitenant.md`, más scripts de VPS y de
base. Su último commit es del **2026-06-16**; los seis repositorios se tocaron en septiembre.

No es una crítica al documento: es la demostración de por qué una guía necesita algo que la haga
fallar. Lo que dice ya no coincide con el código:

| `.commons` dice | El código hace |
|---|---|
| `backend/`, `dashboard/`, `mobile/` | `server/`, `panel/` o `backoffice/`, `app/` |
| `VARCHAR(100)` por defecto para texto | `str` mapea a `TEXT` en `models/base.py` |
| `SMALLINT` con CHECK para los enums | `VARCHAR` con CHECK vía `StringEnumType` |
| «SQLAlchemy gestiona el CheckConstraint automáticamente» | Falso desde SQLAlchemy 1.4; es la fila 1 de este inventario |
| Índices con prefijo `idx_` | `ix_` |

Además, `estandares/api_response.md` ya tiene una copia divergente y más nueva en
`banditore/docs/api_response_standard.md` y otra en `spazio/docs/`.

**Qué hacer con él:** lo que sigue siendo cierto ya está absorbido en `convenciones/`. Los scripts
(`setup scripts/`, `vps/`) son código, no convención: van a `canone/scripts/` o a `consola`, donde
se ejecuten. Después `.commons` se borra, porque una segunda guía es el problema que `canone` viene
a resolver. Queda en el historial de git si hace falta recuperar algo.

## Hay más repositorios que los seis

`scripts/verificar.py --todos ..` encuentra también `posta`, `spazio`, `parametri`, `forziere`,
`fugace` y `bot`. `posta` y `spazio` ya tienen `server/` y superficies web, y `spazio` tiene su
propia copia de `api_response_standard.md`. La homologación los incluye; este inventario no los
midió a fondo.

## Orden de aplicación

Cada paso es un commit por repositorio, y se puede detener en cualquier punto.

1. **Los defectos de base** (filas 1 a 5): tocan `models/base.py` y `core/database.py`, no tienen consecuencias de diseño y eliminan fallas reales. Una migración regenera los CHECK de los enums.
2. **`.gitattributes`, `.gitignore`, `README.md` raíz** (19 a 22): mecánico.
3. **`ruff` + `mypy` + `pytest` en `pyproject.toml`, y CI** (9 a 12): la primera corrida va a fallar; ese ruido es el inventario real de la deuda.
4. **Layout y prefijo de la API** (6 a 8): renombres amplios, mejor solos.
5. **Adaptador y versiones del cliente** (14, 15): se verifica levantando cada superficie.
6. **El cliente nativo** (18): decisión abierta, no un renombre.

**cadenza no se homologa: se termina primero.** No tiene `main.py`, ni settings, ni conexión a la
base; aplicarle convenciones a un esqueleto es escribir reglas contra código que no existe.
