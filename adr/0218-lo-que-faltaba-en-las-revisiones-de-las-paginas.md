# ADR-0218 · Lo que faltaba en las revisiones de las páginas

- **Estado:** Aceptada. El 2026-11-22 el usuario pidió aplicar las recomendaciones de la revisión de lo que faltaba en cada página. Lo que es preferencia suya queda en «Abierto»
- **Fecha:** 2026-11-22
- **Alcance:** `plataformas/README.md`, `despliegue.md`, `postgres.md`, `fastapi.md`, `autenticacion.md`, `java.md`, `sveltekit.md`, `flet.md`, `qt.md`, `python.md`, `transversal.md`, `stack.md`, con `plantilla/infra/`, `plantilla/receiver/`, `plantilla/server/`, `plantilla/qt/tests/`, `plantilla/flet/tests/`, `scripts/verificar.py`, `scripts/infra/` y `fuentes/README.md`

## Contexto

Ninguna de las revisiones posteriores al README de Fable aplicó todos los pasos de «Revisión».
Faltaban, sobre todo, el paso 1, la comparación de algunas adoptadas con su origen y los
experimentos de varias filas de «Cumplimiento». Al completarlos aparecieron estos hallazgos:

- `CREATE DATABASE` heredaba el locale de la máquina. En PostgreSQL 17.12 de Debian 13, `en_US`
  ordena «Ábaco abeja Ñandú nube», con la Ñ antes de la n, y `C.UTF-8` ordena por bytes
  («Oso abeja nube zeta Ábaco»). `es-x-icu` da el orden del español.
- *Backup and Restore* dice que, con `ON_ERROR_STOP` o sin él, una restauración que falla deja la
  base a medias, y ofrece `--single-transaction` para que quede entera o no quede.
- El Authorization Cheat Sheet pide que el permiso se compruebe con una configuración global de la
  app, no aplicada ruta por ruta (*Validate the Permissions on Every Request*). `fastapi.md` pedía
  declarar el permiso en cada ruta, y nada negaba una ruta que no lo declaraba.
- `test_colors_only_generated`, canónico en Qt y en Flet, no tenía fila en «Cumplimiento», y su
  expresión dejaba pasar `Qt.GlobalColor.red`, `QColorConstants.Red`, `QColor.fromRgb(…)` y
  `ft.CupertinoColors.X`.
- Faltaban secciones de cliente para cumplir contratos de `transversal.md`: en SvelteKit, los
  errores, los reintentos, `Accept-Language`, el WebSocket y las llamadas; en Flet, los errores y
  `Accept-Language`; en Qt, los errores y los reintentos.
- Catorce versiones de `stack.md` no eran la última estable.

## Decisión

1. La base se crea desde `template0`, en UTF-8, con la colación ICU `es` y `C.UTF-8` como locale de
   libc. Comprobado en la distro Testing: la base queda con proveedor `i` y `es`, ordena
   «Ábaco nube Ñandú zeta», PostGIS se crea en ella y el dump se restaura.
2. `<app>_owner` restaura con `pg_restore --single-transaction`.
3. Una fecha sin hora es `date`.
4. El router de `/api` lleva `deny_by_default`, que responde 404 a una ruta que no declara quién la
   llama, y cada ruta lo declara con `public` o con la dependencia de su permiso, marcada con
   `@access`. Lo comprueban `test_routes_declare_access`, que recorre las rutas de
   `app.routers`, y `test_undeclared_route_is_not_found`. FastAPI 0.163.1 guarda un router incluido
   como `_IncludedRouter`, y `app.routes` no lista sus rutas: la prueba lee el `router` de cada
   módulo. Sin `public` en `GET /api/health`, las dos pruebas y las de salud fallan.
5. `test_colors_only_generated` detecta también `QColor.from…` con un literal, `QColorConstants`,
   `Qt.GlobalColor` salvo `transparent`, y `ft.CupertinoColors`. `Qt.GlobalColor.transparent` y
   `QColor.fromString(SCHEME[...])`, que usa Consola, siguen pasando. Las dos páginas tienen su fila,
   y Flet, la de sus archivos copiados sin editar.
6. Los clientes escriben cómo cumplen sus contratos. En SvelteKit, comprobado con openapi-fetch
   0.17.0: una función que envuelve el `fetch` reintenta, también el `fetch` que se pasa en una
   petición, y un middleware `onRequest` pone `Accept-Language` en cada petición.
7. La pieza en Java sirve HTTP con `com.sun.net.httpserver`. El módulo `jdk.httpserver` está en
   `openjdk-21-jre-headless` 21.0.13 de Debian 13 (listado con `jimage`).
8. En `autenticacion.md`, «Ningún token llega al navegador» sale de L10 porque lo dice la sesión,
   el límite de SMS queda solo en «Código por SMS», y sale la razón del código 4401.
9. `stack.md` sube a la última versión estable. Las
   ocho copias de SvelteKit y de Svelte en `fuentes/` son iguales en la versión nueva. Cada enlace
   que prueba un hecho se comparó entre las dos versiones, y pasa a la nueva si el hecho sigue ahí.
   Playwright queda en la 1.65.1, la de npm: la 1.65.2 es solo de PyPI, y el servidor usa la de
   SvelteKit.
10. TypeScript sigue en la 6, la excepción que ya escribía `sveltekit.md`. Comprobado:
    `svelte-check` 4.7.8 con TypeScript 7.0.2 sale con un error que pide tener la 6 y la 7 y usar
    `--tsgo`, y SvelteKit 3.4.0, `svelte-check` y typescript-eslint 8.73.0 piden la 6 en sus
    `peerDependencies`.
11. Una cuenta de administración entra solo con una passkey que verificó al usuario, la
    autenticación de varios factores que NIST §2.2.1 pide para AAL2, y no se recupera con el
    código. Lo confirmó el usuario el 2026-11-22.
12. Flutter hace las llamadas con flutter_webrtc 1.6.3, la que usa vettore. Lo confirmó el usuario
    el 2026-11-22.
13. Una respuesta lleva todos los campos de su esquema, y uno sin valor va como `null`, salvo en
    un problem+json, que omite el miembro sin valor. El esquema base lleva
    `json_schema_serialization_defaults_required=True`, y `Problem` y `FieldError`, `False`: sin
    eso, FastAPI 0.165.0 escribe `null` pero el OpenAPI no declara requerido el campo, y un cliente
    generado lo tipa como opcional. Lo confirmó el usuario el 2026-11-22.
14. El servidor sigue solo agregando, y la receptora guarda la contraseña del repositorio. Después
    de cada respaldo bueno olvida lo que pasó la retención, con `--keep-within-daily 7d
    --keep-within-weekly 1m --keep-within-monthly 1y` y `--group-by=`, y corre `restic check
    --read-data-subset 5%`. Es lo que recomiendan la guía #StopRansomware de CISA (respaldos
    cifrados, fuera del alcance de quien ataca, y probados) y la comunidad de restic (un servidor
    que solo agrega, y la poda desde otra máquina de confianza). Ningún respaldo pasa de un año,
    como pide *Disposal of logs*, y `event_log` sigue en 365 días. Con `--group-by=` se agrupan
    todos los respaldos, y uno de otro host también se olvida. En Windows PowerShell 5.1 un
    argumento `""` no llega al programa, así que los dos scripts usan `--group-by=`. Antes de
    olvidar, la receptora corre `restic unlock --remove-all`: un respaldo cortado deja su lock, y
    `forget --prune`, que pide uno exclusivo, falla con él. Cuando corre, el servidor ya terminó.
    Comprobado con `scripts/infra/backup.sh` en el Debian 13 de la distro Testing: pasan todos sus
    pasos, entre ellos que la receptora olvida un respaldo de 2020 y que su revisión falla si a su
    copia le falta un pack. Lo confirmó el usuario el 2026-11-22.
15. Un «Se queda» de una convención propia nombra lo que empeora sin ella, y uno de una adoptada
    lleva «Leído» con su origen (`plataformas/README.md`, «Evidencia»). Lo pidió el usuario el
    2026-11-22.
16. A los 100 fallos consecutivos de la recuperación, la cuenta deja de recuperarse con el código y
    la recupera un administrador, y un inicio de sesión exitoso la vuelve a habilitar. Un
    administrador recupera una cuenta que no es de administración cambiando su correo o su
    teléfono por uno que tiene el titular.
17. El servidor sigue con `httpx`. firebase-admin 7.8.0 exige `httpx` 0.28.1, y stripe 17.1.0 lo
    usa si no está `httpx2`. Comprobado que los dos conviven: con los dos instalados, stripe usa
    `httpx2` y firebase-admin, `httpx`. Cuando stripe deje `httpx`, entra `httpx2` solo para él.
18. Un cliente muestra una fecha con hora en la zona del dispositivo, salvo la de un dato que viaja
    con su zona horaria.
19. Una lista acepta un orden solo si un caso de uso lo pide, y lo recibe en `orderBy`, como dice la
    AIP-132 de Google, *Ordering*. Se copió en `fuentes/` del mismo commit que la AIP-158, y cuenta
    junto con ella para «Aporta».

Los puntos 16 a 19 los confirmó el usuario el 2026-11-22.

## Razones que salen de `fastapi.md`

Salen por «Redacción»: no se apartan de ninguna fuente.

- Un solo `httpx.AsyncClient`: reutiliza las conexiones, y es el cliente de las pruebas.
- El `.mo` no se versiona: uno versionado puede quedar desfasado de su `.po`, y el código de una
  versión no cambia en el servidor.
- En producción no se sirve el OpenAPI: el contrato está en el repositorio, y nadie de afuera
  necesita el mapa de la API.
- Cada operación declara sus errores: un cliente generado tipa el error que de verdad recibe.
- `GET /api/health` responde 503 con una dependencia caída: un servidor así no está vivo aunque el
  proceso responda.
- `lastEventAt`: si `event_log` deja de recibir eventos, `lastCriticalAt` sigue en `null`, como
  cuando no pasó nada grave.
- `diskFreeBytes`: con el disco lleno PostgreSQL deja de escribir, y `SELECT 1` sigue respondiendo.
- Un token equivocado es `warn`: un escaneo no mueve `lastCriticalAt`.
- `GET /api/health/event-log` en orden de transacción: quien vigila copia las filas fuera de la
  máquina y nota si una se cambió o se borró.
- El corte en `pg_snapshot_xmin`: una transacción que confirma tarde deja filas con un `xid` menor
  que el de las ya leídas, y un cursor por `id` o por hora se las saltaría.
- 10 conexiones de WebSocket por usuario alcanzan para varias pestañas y dispositivos.

## Abierto

- **«Cumplimiento» de `autenticacion.md`**, que necesita escribir la autenticación del servidor en
  la plantilla (`pendientes/autenticacion-sin-cumplimiento.md`).

## Consecuencias

- Un repositorio con servidor copia `deny_by_default` y declara el acceso de cada ruta, y cada
  repositorio de Qt o de Flet copia el `tests/test_theme.py` nuevo.
- Una base que ya existe conserva su colación. Cambiarla es crear la base otra vez y restaurar el
  respaldo.
