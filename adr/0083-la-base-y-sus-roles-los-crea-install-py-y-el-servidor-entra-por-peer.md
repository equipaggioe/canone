# ADR-0083 · La base y sus roles los crea `install.py`, y el servidor entra por `peer`

- **Estado:** Aceptada. Los puntos 3 y 4 los reemplaza el
  [ADR-0085](0085-el-dueno-del-esquema-entra-por-peer-con-su-cuenta-y-corre-el-volcado.md)
- **Fecha:** 2026-10-25
- **Alcance:** «PostgreSQL» de [`plataformas/despliegue.md`](../plataformas/despliegue.md) y
  `plantilla/infra/install.py`

## Contexto

canone pedía dos roles, el del servidor sin DDL y el dueño del esquema
([ADR-0080](0080-la-purga-de-event-log-es-una-funcion-y-una-ruta-de-salud-dice-que-alertar.md),
[ADR-0081](0081-la-purga-de-event-log-la-corre-el-dueno-del-esquema.md)), pero ninguna plantilla
los creaba, y el
[ADR-0075](0075-canone-fija-el-repositorio-declara-y-consola-dispara.md) dejaba a consola bloqueada
hasta tenerla. consola creaba un solo rol, dueño de la base con `GRANT ALL`, con su contraseña en
`.consola/config.env`.

## Decisión

1. `install.py` crea la base `<app>`, el rol `<app>` del servidor y el rol `<app>_owner`, dueño de
   la base. Ninguno es superusuario.
2. El servidor entra por el socket con `peer`, sin contraseña, y `install.py` escribe su
   `database_url` en `<app>/`.
3. El dueño entra por `127.0.0.1` con una contraseña que genera `install.py` y que solo queda
   cifrada, en `<app>-migrate/database_url`.
4. *(propuesta)* Cada corrida de `install.py` cambia la contraseña del dueño.
5. *(propuesta)* `install.py` crea como `postgres` las extensiones que recibe con `--extension`.

## Consecuencias

- Nadie guarda una contraseña de la base: la del servidor no existe, y la del dueño solo la lee
  systemd.
- consola deja de crear en el servidor la base, los roles y las extensiones, y sus `DB_USER` y
  `DB_PASSWORD` remotos sobran.
- El explorador de base de consola, que entra como el rol de la app por un túnel TCP con
  contraseña, ya no puede entrar así.
- Comprobado en Debian 13 con PostgreSQL 17 y systemd 257, con las unidades de la plantilla y su
  aislamiento: el servidor entra como `<app>` y recibe `permission denied` al crear una tabla, la
  unidad de las migraciones entra como `<app>_owner` y la crea, ninguna de las dos entra como el
  dueño por `peer`, y una segunda corrida no falla y cambia la contraseña.

## Descartado

- **`postgres` como dueño de las tablas:** las migraciones y la purga corren código de la app, y
  como superusuario saltarían todo permiso y correrían comandos del sistema con
  `COPY … TO PROGRAM`.
- **`peer` para el dueño:** las migraciones corren con la cuenta `<app>`, así que haría falta otra
  cuenta del sistema, o un mapa de `pg_ident.conf` que dejaría al servidor entrar también como
  dueño.
- **Un solo rol dueño, como el de consola:** un error o una inyección en la app cambiarían el
  esquema y borrarían `event_log`.
- **Contraseña también para el servidor:** un secreto más, sin nada que ganar sobre la identidad
  que da el sistema.
