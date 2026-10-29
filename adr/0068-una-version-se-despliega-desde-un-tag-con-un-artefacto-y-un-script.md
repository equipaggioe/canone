# ADR-0068 · Una versión se despliega desde un tag, con un artefacto y un script

- **Estado:** Aceptada. El punto 3 lo reemplaza el [ADR-0106](0106-deploy-py-se-instala-desde-plantilla-infra-con-los-datos-de-la-app.md)
- **Fecha:** 2026-10-22
- **Alcance:** la sección «Versiones» de [`plataformas/despliegue.md`](../plataformas/despliegue.md)

## Contexto

`despliegue.md` decía cómo queda el servidor, pero no cómo llega una versión a él. Tampoco había
dónde viviera una versión nueva de la web, de la landing o de un instalable, y
[`repositorio.md`](../repositorio.md) decía que el repositorio no traía scripts de despliegue.

## Decisión

1. Se despliega un tag. El CI corre en él los jobs de `ci.yml`, y solo si pasan construye un
   artefacto con el servidor y el build de cada superficie web, y lo publica en un release de GitHub
   con su SHA-256.
2. Cada versión queda en `releases/<versión>/` y el enlace `current` apunta a la activa. Los datos
   quedan fuera, en `/var/lib/<app>/`.
3. Un script, `scripts/deploy.py`, instala la versión en el servidor, y una persona lo lanza por
   `ssh`.
4. Si `GET /api/health` falla y la versión no aplicó migraciones, `current` vuelve a la versión
   anterior. Si las aplicó, `current` queda en la nueva y el script termina con error.
5. Caddy sirve cada superficie web desde `current/<pieza>/`. La PWA es `web/`.
6. Los instalables de `desktop/` se adjuntan al mismo release y `deploy` los copia a `downloads/`
   con un nombre fijo por sistema.
7. En un repositorio privado, `deploy` baja el release con un token de solo lectura cifrado con
   `systemd-creds`.
8. Quien despliega firma el `.sha256` con su llave SSH, fuera de GitHub, y el servidor verifica la
   firma contra `allowed_signers`.

## Consecuencias

- La web, el servidor y los instalables de una versión salen de un solo tag que pasó el CI.
- Una versión con migraciones que no pasa el health check deja el servicio caído hasta que la
  persona lo arregla: se prefiere a correr código que no conoce el esquema.
- Los instalables de `mobile/` quedan fuera: dependen de las tiendas y de la firma.

## Descartado

- **Desplegar desde Actions por `ssh`:** GitHub guardaría una llave con acceso al servidor.
- **Un timer en el servidor que consulta los releases:** agrega una pieza y retrasa el despliegue.
- **Atestaciones de GitHub:** en un repositorio privado piden el plan Enterprise Cloud, y quien
  controla la cuenta controla también el workflow que atesta.
- **cosign sin llave:** publica en un registro público el repositorio, el workflow y el commit.
- **Volver a la versión anterior también tras migrar:** el código viejo correría sobre un esquema
  que no conoce, sin error visible.
