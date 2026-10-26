# ADR-0085 · El dueño del esquema entra por `peer` con su cuenta, y corre el volcado

- **Estado:** Aceptada
- **Fecha:** 2026-10-26
- **Alcance:** «PostgreSQL», «Procesos» y «Respaldos» de
  [`plataformas/despliegue.md`](../plataformas/despliegue.md), `plantilla/infra/` y
  `.github/workflows/infra.yml`

## Contexto

El [ADR-0083](0083-la-base-y-sus-roles-los-crea-install-py-y-el-servidor-entra-por-peer.md) dejaba
al dueño del esquema entrar por `127.0.0.1` con una contraseña que `install.py` generaba en cada
corrida, porque las migraciones y la purga corrían con la cuenta `<app>`, la del servidor. Descartó
`peer` para el dueño porque hacía falta otra cuenta del sistema. Esa cuenta es una línea de
`sysusers.conf`.

El volcado corría como `postgres`, superusuario, con el mismo usuario que PostgreSQL, y por eso no
podía llevar `RemoveIPC=`.

## Decisión

1. `install.py` crea la cuenta `<app>_owner`, y el rol `<app>_owner` entra por `peer` desde ella,
   sin contraseña. Reemplaza los puntos 3 y 4 del ADR-0083.
2. Las migraciones, la purga y el volcado corren con la cuenta `<app>_owner`.
3. El volcado deja fuera las extensiones, y el respaldo ya no lleva `globals.sql`: los roles y las
   extensiones los crea `install.py`, y el dueño, que restaura, no puede crear una extensión que no
   es *trusted*.
4. El job `postgres` de `infra.yml` comprueba los roles y que el volcado del dueño se restaura.

## Consecuencias

- Ningún rol tiene contraseña: `<app>-migrate/database_url` solo nombra el rol y el socket.
- El respaldo diario corre sin superusuario, y el volcado lleva `RemoveIPC=yes`, como las demás
  unidades.
- Restaurar es correr `install.py` con las mismas `--extension` y `pg_restore` con la cuenta
  `<app>_owner`.
- La seguridad frente al servidor no cambia: con el aislamiento de la plantilla, el servidor ya no
  veía la credencial de la purga aunque corrían con la misma cuenta.
- Comprobado en Debian 13 con PostgreSQL 17.11, PostGIS 3.5.2 y systemd 257, con las unidades de
  la plantilla: la migración y la purga entran como `<app>_owner`, el servidor no entra como el
  dueño ni por `peer` ni por `127.0.0.1` y no crea tablas, dos volcados seguidos dejan la base
  viva, y `pg_restore --exit-on-error` restaura como el dueño los datos y los permisos. Sin dejar
  fuera las extensiones, el dueño falla en `COMMENT ON EXTENSION postgis` y en `spatial_ref_sys`.

## Descartado

- **Restaurar como `postgres`:** también funciona, pero deja un superusuario en el ciclo del
  respaldo cuando ninguno hace falta.
- **Mantener la contraseña del dueño:** un secreto que generar, rotar y cifrar, sin nada que ganar
  sobre la identidad que da el sistema.
