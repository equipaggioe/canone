# ADR-0086 · Las pruebas corren con los permisos del servidor, y las migraciones con el dueño

- **Estado:** Aceptada
- **Fecha:** 2026-10-26
- **Alcance:** «Pruebas» de [`plataformas/fastapi.md`](../plataformas/fastapi.md),
  `plantilla/server/tests/` y el job `server` de `plantilla/.github/workflows/ci.yml`

## Contexto

fastapi.md dice que los permisos de una tabla los da la migración que la crea, y que el CI los
prueba. El CI migraba y corría las pruebas como `postgres`, superusuario: solo las pruebas de
`event_log` cambiaban de rol. Una tabla sin su `GRANT` pasaba el CI y fallaba en producción con
`permission denied`.

## Decisión

1. El CI crea los roles y la base como `install.py`: el rol del servidor, el dueño y la base del
   dueño, con sus extensiones.
2. `alembic upgrade head` entra como el dueño, con su propia carpeta de credenciales.
3. Las pruebas entran como superusuario, y cada conexión toma el rol del servidor con `SET ROLE`,
   desde un listener de `connect` en `tests/conftest.py`. El rol dura la conexión entera, también
   en el código que usa el engine fuera de la sesión.
4. Lo que corre el dueño, como la purga, se prueba con el fixture `owner`, que hace
   `SET LOCAL ROLE` al dueño dentro de la transacción de la prueba.

## Consecuencias

- Una prueba tiene los permisos que el servidor tiene en producción.
- Una prueba que crea una tabla pide `owner`, como haría una migración.
- Comprobado con PostgreSQL 17.11: las 37 pruebas de la plantilla pasan, y quitando el `INSERT`
  sobre `event_log` al rol del servidor fallan las tres que escriben un evento como el servidor.

## Descartado

- **Que las pruebas entren como el rol del servidor:** la purga necesitaría una segunda conexión
  como el dueño, con una credencial que `Settings` no tiene.
- **Una prueba que compruebe que cada tabla tiene algún `GRANT`:** no sabe qué permisos necesita el
  servidor, y no prueba los que sí usa.
