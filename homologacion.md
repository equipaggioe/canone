# Homologación

Qué divergencias hay hoy, **agrupadas por plataforma**. Una fila solo le toca a los repositorios que
usan esa plataforma: nada de esto obliga a un repositorio a adoptar una pieza que no necesita.

Inventario verificado el 2026-09-22 leyendo el código de `navetta`, `presenze`, `vettore`,
`banditore`, `concordia`, `cadenza` y `consola`. Lo marcado **(propuesta)** no está confirmado.

## Qué usa cada repositorio

| Repositorio | Servidor | Base | Web | Cliente instalable |
|---|---|---|---|---|
| navetta | FastAPI | PostGIS | panel, landing | Flutter ×3 (`mobile-driver`, `mobile-passenger`, `mobile-shared`) |
| presenze | FastAPI | PostGIS | panel, landing | Flet ×2 (`app`, `terminal`) |
| vettore | FastAPI | PostGIS | panel, backoffice, landing, demo | Flutter (`app`) + plugins propios |
| banditore | FastAPI | PostGIS | backoffice, landing | Flet ×2 (`customer`, `vendor`) + `mobile_common` |
| concordia | FastAPI | PostGIS | backoffice, landing, pwa | PWA |
| cadenza | FastAPI (esqueleto) | — | backoffice, landing | Flet (`frontend`) |

## Lo que ya es uniforme

No hay nada que decidir; solo hay que impedir que se separe.

| Pieza | Estado |
|---|---|
| Backend | FastAPI + SQLAlchemy 2 async + asyncpg + Alembic + PostgreSQL en los 6 |
| `server/app/schemas/base.py` | Idéntico byte a byte en los 6 |
| `server/alembic.ini` | Idéntico en los 6 |
| Serialización | Pydantic v2 con `alias_generator=to_camel` en los 6 |
| Web | SvelteKit 2 + Svelte 5 + UnoCSS + TypeScript en las 15 superficies |
| Tokens de color | Una clase o módulo de constantes, sin colores literales, en Flutter y en Flet |
| Convención de `docs/` | `arquitectura/` + `adr/` + `planes/` en los 6 |

## FastAPI

| # | Tema | Qué hay hoy | Se adopta | Por qué |
|---|---|---|---|---|
| 1 | `expire_on_commit` | `False` en presenze, vettore, banditore, concordia; default `True` en navetta | **`False`** | Una `AsyncSession` no hace lazy-load: leer un modelo después del commit revienta |
| 2 | `rollback` en `get_db` | Solo concordia | **concordia** | Sin él, un servicio que falla a mitad de una escritura devuelve la conexión al pool con la transacción abierta |
| 3 | `pool_pre_ping` | navetta, vettore, banditore sí; presenze y concordia no | **sí** | Las bases se alcanzan por túnel; una conexión muerta en el pool falla el primer request que la tome |
| 4 | Carpeta de routers | `routers/` en navetta, presenze, vettore, concordia; `api/routers/` en banditore; `api/` vacío en cadenza | **`routers/`** *(propuesta)* | Mayoría, y un nivel menos |
| 5 | Prefijo de la API | Sin prefijo (navetta, vettore); `/api` en cada router (presenze); `/api` al montar (concordia); `/api/v1` (banditore) | **`/api` al montar** *(propuesta)* | Un solo lugar que cambiar. Sin `v1`: nada está en producción |
| 6 | Biblioteca de JWT | `python-jose` (presenze); `PyJWT` (navetta, banditore, concordia) | **PyJWT** | `python-jose` está sin mantenimiento desde 2021 y con vulnerabilidades publicadas |
| 7 | Hash de contraseña | `passlib[argon2]` (navetta); `argon2-cffi` directo (presenze, vettore, banditore, concordia) | **`argon2-cffi`** | `passlib` está sin mantenimiento desde 2020 |
| 8 | Driver sync | `psycopg2-binary` (navetta); `psycopg[binary]` v3 (el resto) | **psycopg 3** | psycopg2 está en mantenimiento pasivo |
| 9 | Lint y tipos | Solo concordia tiene `ruff` + `mypy` | **concordia** | Es la única configuración que existe |
| 10 | Configuración de pytest | `pyproject.toml` (banditore, concordia); `pytest.ini` (vettore); ninguna (navetta, presenze, cadenza) | **`pyproject.toml`** | Un archivo de configuración por proyecto |
| 11 | CI | Solo concordia | **concordia** | Es la única regla que hoy se hace cumplir sola |
| 12 | Cobertura de tests | vettore 39 archivos, presenze 20, concordia 16, banditore 7, navetta 4, cadenza 0 | — | No es convención, es deuda: va al documento 30 de cada repositorio |
| 13 | Redis opcional | concordia lo importa solo si `REDIS_URL` está definida | **obligatorio con varios workers** | Con dos workers y sin Redis los WebSocket se parten sin que nada falle: es el degradado silencioso que `principios.md` prohíbe |

## PostgreSQL y PostGIS

| # | Tema | Qué hay hoy | Se adopta | Por qué |
|---|---|---|---|---|
| 14 | `StringEnumType`, CHECK | `create_constraint=True` en banditore y concordia; ausente en navetta, presenze, vettore, cadenza | **concordia** | Sin el CHECK, `native_enum=False` deja un TEXT pelado y la base acepta cualquier cadena escrita por SQL directo o una carga masiva |
| 15 | Columnas geográficas | `Annotated[..., mapped_column(Geography(...))]` en 5; funciones `geo_point()` / `geo_line()` en concordia | **concordia** | geoalchemy2 guarda `nullable` en la instancia del tipo y la muta por columna; un `Annotated` comparte una sola instancia y la última procesada se lo impone a todas |
| 16 | `UpdatedAt` | `datetime \| None` en 5; `datetime` en banditore | **banditore** *(propuesta)* | Lleva `server_default=now()`, así que la columna nunca es nula: el tipo opcional describe algo que no ocurre |

### Defectos encontrados de paso (sin confirmar)

| Repositorio | Hallazgo |
|---|---|
| cadenza | Dos clases `Base` declaradas, `app/db/base.py` y `app/models/base.py`, con mapas de tipos distintos. `app/db/__init__.py` exporta la primera |
| cadenza | `server/app/main.py` está vacío (0 líneas) y `app/api/` no tiene routers |
| cadenza | No existe `app/core/settings.py` ni `app/core/database.py` |

## SvelteKit

| # | Tema | Qué hay hoy | Se adopta | Por qué |
|---|---|---|---|---|
| 17 | Adaptador | `adapter-static` en las landings, en panel y backoffice de vettore y en backoffice y pwa de concordia; `adapter-auto` en el panel de navetta y presenze y en el backoffice de banditore y cadenza | **`adapter-static`** *(propuesta)* | Todo se sirve con Caddy; `adapter-auto` elige un adaptador de Vercel o Netlify que no se usa |
| 18 | Dónde vive la config de UnoCSS | `uno.config.ts` en 7 superficies; dentro de `vite.config.ts` en banditore/backoffice y cadenza/backoffice | **`uno.config.ts`** | Inline, la extensión del editor no la lee y `content.pipeline.include` no tiene dónde declararse |
| 19 | Preset de UnoCSS | `presetWind4` (concordia); `presetWind3` (navetta, vettore/backoffice); `presetUno` (presenze, vettore/panel, banditore, cadenza) | **`presetWind4`** *(propuesta)* | Es el actual; `presetUno` es el alias viejo de Wind3 |
| 20 | Estado | Runes `$state`/`$derived` en las superficies nuevas; `lib/stores` de Svelte 4 en navetta (11), concordia (5+1), presenze (1) | **runes en `.svelte.ts`** *(propuesta)* | Es Svelte 5. Lo escrito con stores se deja; no se agregan nuevos |
| 21 | `vitest` | navetta/panel, vettore/panel, vettore/backoffice, concordia/pwa | **en toda superficie con lógica propia** | Una landing sin lógica no lo necesita |
| 22 | Línea de versiones | vettore en Vite 8 / TS 6 / plugin-svelte 7; las otras cinco en Vite 7 / TS 5 | **la de vettore** *(propuesta)* | Nada está en producción; sostener dos líneas mayores es costo sin beneficio |

## Flutter

| # | Tema | Qué hay hoy | Se adopta | Por qué |
|---|---|---|---|---|
| 23 | Layout de `lib/` | `core/` + `features/` en vettore; `screens/` plano en las dos apps de navetta | **`core/` + `features/`** *(propuesta)* | Una carpeta por funcionalidad. El plano se sostiene con pocas pantallas y no escala |
| 24 | Analizador | vettore sube `unawaited_futures`, `dead_code` y las comprobaciones de tipo a error y agrega 18 reglas; navetta **apaga** `prefer_const_constructors` | **el de vettore** | Un future sin await es un bug de concurrencia, no un detalle de estilo |
| 25 | Gestión de estado | `ChangeNotifier`/`ValueNotifier` sin paquete en vettore (25 archivos); `provider` en navetta | **sin paquete** *(propuesta)* | vettore resuelve una app mucho más compleja sin él. Lo escrito con `provider` se deja donde está |
| 26 | Datos | vettore habla con el servidor real; navetta corre con `mock_data.dart` y un `AuthService` que acepta cualquier credencial | — | No es convención: navetta está sin terminar. Va a su documento 30 |
| 27 | CI | Ninguna app corre `flutter analyze` ni `flutter test` | **las dos** | |

## Flet

| # | Tema | Qué hay hoy | Se adopta | Por qué |
|---|---|---|---|---|
| 28 | Layout | `core/` + `views/` en presenze/app; `pages/` + `components/` con el resto plano en banditore; todo suelto con `app_state.py` en cadenza | **`core/` + `views/`** *(propuesta)* | Es el único que separa red, sesión y tema de la interfaz |
| 29 | Código compartido | Paquete instalable `mobile_common` en banditore; copiado entre `app/` y `terminal/` en presenze | **paquete local** | Ya funciona en banditore |
| 30 | Dependencias | `pyproject.toml` + `uv.lock` en banditore; `requirements.txt` en presenze y cadenza | **`pyproject.toml` + `uv`** *(propuesta)* | Un `>=` sin lock no es reproducible |
| 31 | Lint y tipos | Ninguna pieza Flet tiene `ruff` ni `mypy` | **la misma config que el servidor** | Es Python |
| 32 | Cuándo Flet y cuándo Flutter | No está escrito en ningún lado | **falta decidir** | Ver abajo |

## Cualquier repositorio

| # | Tema | Qué hay hoy | Se adopta | Por qué |
|---|---|---|---|---|
| 33 | `.gitattributes` | No existe en ninguno | **se agrega** | `navetta/.gitignore` ya mezcla CRLF y LF dentro del mismo archivo |
| 34 | `node_modules` en el `.gitignore` raíz | Ausente en los 6; cubierto por el de cada superficie web | **se sube al raíz** | `banditore/customer` y `cadenza/frontend` no tienen el suyo |
| 35 | `docs/` con archivos sueltos | banditore (`api_response_standard.md`, `descripcion.md`, `implementaciones_futuras.md`), cadenza (`memoria_tecnica.md`), presenze (`4500/`, `mockups/`), concordia (`postman/`) | **se reubica** | El estándar de respuesta pasa a `plataformas/fastapi.md`, las implementaciones futuras al documento 30, y el resto a `arquitectura/` o se borra |
| 36 | `README.md` raíz | Solo vettore | **se agrega en todos** | Qué es, qué piezas tiene, cómo se levanta cada una |

## La decisión que falta

**Cuándo un cliente instalable es Flet y cuándo es Flutter.** Hoy hay tres respuestas distintas sin
criterio escrito: Flutter en navetta y vettore, Flet en presenze, banditore y cadenza, y una PWA en
concordia.

No hace falta unificar la tecnología —cada producto puede elegir— pero sí hace falta el criterio,
porque hoy la elección parece histórica y no razonada. Lo que el código sugiere:

| Si la pieza… | Va en |
|---|---|
| Se publica en tienda y necesita push confiable, segundo plano o hardware | Flutter. Es lo que hacen vettore y navetta |
| La operamos nosotros o vive en hardware propio, y no conviene salir de Python | Flet. Es el caso de `presenze/terminal` |
| Se puede resolver en el navegador | PWA con SvelteKit, que reutiliza el stack que ya está en los seis |

Para escribirlo como ADR falta verificar dos cosas que no se comprobaron: qué hace exactamente
`presenze/terminal` con el hardware, y si `banditore/customer` y `banditore/vendor` se publican en
tiendas o son internas.

## Hay más repositorios que los seis

`scripts/verificar.py --todos ..` encuentra también `posta`, `spazio`, `parametri`, `forziere`,
`fugace` y `bot`. `posta` y `spazio` ya tienen `server/` y superficies web, y `spazio` tiene su
propia copia de `api_response_standard.md`. La homologación los incluye; este inventario no los
midió a fondo.

## Orden de aplicación

Cada paso es un commit por repositorio, y se puede detener en cualquier punto.

1. **Los defectos de base** (14, 15, 1, 2, 3): eliminan fallas reales y no tienen consecuencias de
   diseño. Una migración regenera los CHECK de los enums.
2. **Las bibliotecas sin mantenimiento** (6, 7, 8): tocan solo a navetta y presenze.
3. **`.gitattributes`, `.gitignore`, `README.md`** (33 a 36): mecánico.
4. **`ruff`, `mypy`, `pytest` y CI** (9 a 11, 31): la primera corrida va a fallar; ese ruido es el
   inventario real de la deuda.
5. **Layout y prefijo** (4, 5, 23, 28): renombres amplios, mejor solos.
6. **Cliente web** (17 a 22): se verifica levantando cada superficie.
7. **El criterio Flet/Flutter**: decisión abierta, no un renombre.

**cadenza no se homologa: se termina primero.** No tiene `main.py`, ni settings, ni conexión a la
base; aplicarle convenciones a un esqueleto es escribir reglas contra código que no existe.
