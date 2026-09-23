# Homologación

Qué divergencias hay hoy, **agrupadas por plataforma**. Una fila solo le toca a los repositorios que
usan esa plataforma: nada de esto obliga a un repositorio a adoptar una pieza que no necesita.

Inventario verificado el 2026-09-22 leyendo el código de `navetta`, `presenze`, `vettore`,
`banditore`, `concordia`, `cadenza` y `consola`. Lo marcado **(propuesta)** no está confirmado.

## Qué usa cada repositorio

| Repositorio | Servidor | Base | Web | Cliente instalable |
|---|---|---|---|---|
| navetta | FastAPI | PostGIS | panel, landing | Flutter ×3 (`mobile-driver`, `mobile-passenger`, `mobile-shared`) |
| consola | — | — | — | Qt (`ui/`) |
| presenze | FastAPI | PostGIS | panel, landing | Flet (`app`) + Qt (`terminal`) |
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

## Autenticación y bitácoras

Verificado el 2026-09-23 leyendo `services/auth*`, `models/**/*log*` y `core/enums.py` de los cinco
servidores con autenticación. Se adopta lo del [ADR-0008](adr/0008-un-sobre-unico-de-evento-y-el-catalogo-es-del-repositorio.md)
y el [ADR-0009](adr/0009-el-login-no-delata-cuentas-y-el-bloqueo-vive-en-la-base.md).

| # | Tema | Qué hay hoy | Se adopta | Por qué |
|---|---|---|---|---|
| 45 | Forma de la bitácora | 3 tablas por categoría (navetta, presenze); 1 sobre único (vettore); solo `audit_log` (banditore); `audit_log` + `login_attempt` (concordia) | **el sobre único de vettore** | Con una tabla por categoría, «todo lo que pasó alrededor de las 3:14» es la unión de cuatro consultas con esquemas distintos |
| 46 | Quién escribe la bitácora | presenze expone `POST` y `PATCH` sobre `audit_log` y `auth_log` con permiso `*:manage` | **solo el servicio que ejecuta la acción** | Una bitácora que se puede editar por HTTP no es una bitácora |
| 47 | `login` dentro de `AuditAction` | navetta y banditore lo mezclan con `insert`/`update`/`delete`; presenze y concordia ya lo separaron | **presenze** | «Una fila cambió» y «una persona entró» son dos preguntas sin nada en común |
| 48 | Tablas de bitácora sin escritores | navetta tiene las tres y **ningún código escribe en ninguna** | — | No es convención, es esquema muerto: va a su documento 30 |
| 49 | Bloqueo por fuerza bruta | Ninguno (navetta, presenze, banditore); en memoria del proceso (vettore); sobre `login_attempt` (concordia) | **concordia** | El de memoria se pierde al reiniciar y con N workers el límite real es N veces el declarado, como documenta el propio `rate_limit.py` de vettore |
| 50 | El tiempo del login delata la cuenta | presenze sale antes de verificar si el usuario no existe; banditore corta por la izquierda en `user is None or not verify_password(...)` | **el hash señuelo de concordia** | argon2 cuesta ~100 ms: sin verificar siempre, el mensaje de error uniforme no sirve de nada |
| 51 | Lista blanca en `old`/`new` | Solo concordia | **concordia** | Serializar la fila entera convierte la bitácora en un almacén de datos personales que sobrevive al derecho de supresión |
| 52 | Ventanas de retención | 8 con interruptor (vettore); 3 (banditore); 2 (concordia); **ninguna** en navetta y presenze | **una por tabla, `0` = indefinida** | Cero es una decisión escrita; la ausencia de la variable es un olvido |
| 53 | Disparador de la limpieza | 7 lazos en `main.py` con `@app.on_event` y sin candado (vettore); `lifespan` + script de cron sobre la misma función (concordia); proceso aparte a mano (banditore) | **concordia** *(propuesta)* | La pasada es una función; el disparador es aparte y puede ser los dos. Sin candado, cada worker corre las 7 |
| 54 | Nombre de tabla | `postgres.md` pide plural; solo vettore lo cumple (`auth_sessions`, `security_logs`). navetta, presenze, banditore y concordia usan singular | **falta decidir** | Cuatro de cinco incumplen la página. O se cambia la página o se renombra: hoy la regla no describe nada |

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
| 29 | Código compartido | Paquete instalable `mobile_common` en banditore; nada en presenze ni cadenza | **paquete local** | Ya funciona en banditore |
| 30 | Dependencias | `pyproject.toml` + `uv.lock` en banditore; `requirements.txt` en presenze y cadenza | **`pyproject.toml` + `uv`** *(propuesta)* | Un `>=` sin lock no es reproducible |
| 31 | Lint y tipos | Ninguna pieza Flet tiene `ruff` ni `mypy` | **la misma config que el servidor** | Es Python |

## PySide6 (Qt)

| # | Tema | Qué hay hoy | Se adopta | Por qué |
|---|---|---|---|---|
| 32 | Hoja de estilos | Tokens + QSS generada desde ellos (consola); `.qss` estático (presenze/terminal); `STYLESHEET` global con literales inline (spazio/app) | **la de consola** | En el `.qss` estático los colores viven dos veces; spazio tiene `"font-size:18px"` suelto que ningún token controla |
| 33 | Layout | `core/` + `ui/` (consola); `core/` + `views/` (presenze/terminal); todo plano (spazio/app) | **`core/` + `ui/`** *(propuesta)* | Los dos primeros son lo mismo con otro nombre; el plano no separa red de interfaz |
| 34 | Cliente HTTP | `QNetworkAccessManager` con señales (presenze/terminal); `requests` (spazio/app) | **`QNetworkAccessManager`** | Una petición síncrona en el hilo de la interfaz congela la ventana |
| 35 | `QPalette` | Solo consola la llena desde los tokens | **consola** | Sin eso, los diálogos nativos y los menús contextuales quedan con los colores del sistema |
| 36 | Contraste | Solo consola tiene `on_color()` por luminancia WCAG | **consola** | El resto elige el color del texto a ojo |

## Transversal a los clientes

| # | Tema | Qué hay hoy | Se adopta | Por qué |
|---|---|---|---|---|
| 37 | Sobre de error | `ApiError` con los mismos campos en presenze/app (Flet, httpx) y presenze/terminal (Qt, QNetwork) | **esa forma en los cuatro clientes** | La plataforma cambia el transporte, no el contrato. Flutter y SvelteKit leen `errorCode` igual |
| 38 | Textos | Paraglide en concordia/pwa y banditore/landing; `i18n.py` + `locales/` en banditore Flet; nada en el resto | **Paraglide en web, `i18n.py` en Flet** | Los dos ya tienen ADR propio en su repositorio |
| 39 | Push | FCM en vettore, Web Push en concordia | **lo decide el destino** | App nativa → FCM; navegador y PWA → Web Push. No son dos formas de hacer lo mismo |

## Cualquier repositorio

| # | Tema | Qué hay hoy | Se adopta | Por qué |
|---|---|---|---|---|
| 40 | `.gitattributes` | No existe en ninguno | **se agrega** | `navetta/.gitignore` ya mezcla CRLF y LF dentro del mismo archivo |
| 41 | `.gitignore` por pieza | Ausente en `banditore/customer` y `cadenza/frontend`; el resto tiene el suyo | **uno por pieza, y el raíz sin nada de tecnología** | Subir `node_modules/` al raíz tapa el olvido en silencio; `verificar.py` falla si una carpeta con `package.json` no ignora `node_modules/` |
| 42 | `docs/` con archivos sueltos | banditore (`api_response_standard.md`, `descripcion.md`, `implementaciones_futuras.md`), cadenza (`memoria_tecnica.md`), presenze (`4500/`, `mockups/`), concordia (`postman/`) | **se reubica** | El estándar de respuesta pasa a `plataformas/fastapi.md`, las implementaciones futuras al documento 30, y el resto a `arquitectura/` o se borra |
| 44 | Nombre de las piezas | Tres criterios a la vez: la tecnología (`frontend`, `pwa`, `flet_app`), el usuario (`customer`, `clientes`, `vendor`) y lo que hace (`backoffice`, `terminal`, `app`) | **`<dónde corre>[-<a quién sirve>]`** | Un solo criterio y dos preguntas con respuesta objetiva; `panel` y `landing` quedan porque es como las nombra la industria |
| 43 | `README.md` raíz | Solo vettore | **se agrega en todos** | Qué es, qué piezas tiene, cómo se levanta cada una |

## Piezas en un solo repositorio

Tienen página igual que las demás: la guía dice cómo se usan, no cuántos repositorios las usan.

| Pieza | Página |
|---|---|
| Stripe y el contrato de proveedor de pago | [pagos.md](plataformas/pagos.md) |
| Resend y el correo transaccional | [notificaciones.md](plataformas/notificaciones.md) |
| WebRTC, STUN y TURN | [tiempo-real.md](plataformas/tiempo-real.md) |
| TOTP y los tipos de token | [seguridad.md](plataformas/seguridad.md) |
| Paraglide | [i18n.md](plataformas/i18n.md) |

Lo que sí es una divergencia: **`slowapi` en concordia contra `core/rate_limit.py` propio en
vettore** son dos implementaciones del mismo problema, y el propio `rate_limit.py` documenta que su
conteo en memoria no sirve con varias instancias.

Y una dependencia muerta: **`celery` está en el `requirements.txt` de navetta y ningún archivo de
`server/app` lo importa.** Se borra.

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
3. **`.gitattributes`, `.gitignore`, `README.md`** (40 a 43): mecánico.
4. **`ruff`, `mypy`, `pytest` y CI** (9 a 11, 31): la primera corrida va a fallar; ese ruido es el
   inventario real de la deuda.
5. **Layout y prefijo** (4, 5, 23, 28): renombres amplios, mejor solos.
6. **Cliente web** (17 a 22): se verifica levantando cada superficie.
7. **Qt** (32 a 36): `consola` ya es el modelo; `spazio/app` es el que más cambia.
8. **Autenticación y bitácoras** (45 a 53): es rediseño, no homologación mecánica. Empieza por
   50 y 49, que son defectos de seguridad reales y cortos; 45 y 47 arrastran migración.

**cadenza no se homologa: se termina primero.** No tiene `main.py`, ni settings, ni conexión a la
base; aplicarle convenciones a un esqueleto es escribir reglas contra código que no existe.
