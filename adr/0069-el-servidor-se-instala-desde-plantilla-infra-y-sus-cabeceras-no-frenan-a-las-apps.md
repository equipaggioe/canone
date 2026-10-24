# ADR-0069 · El servidor se instala desde `plantilla/infra/`, y sus cabeceras no frenan a las apps

- **Estado:** Aceptada. El punto 2 lo reemplaza el [ADR-0070](0070-las-unidades-cargan-la-carpeta-de-credenciales-y-permissions-policy-sigue-a-owasp.md)
- **Fecha:** 2026-10-22
- **Alcance:** «Caddy», «Procesos» y «Respaldos» de [`plataformas/despliegue.md`](../plataformas/despliegue.md), e «Idiomas» de [`plataformas/fastapi.md`](../plataformas/fastapi.md)

## Contexto

Al escribir las unidades de systemd como archivos de canone aparecieron cuatro reglas que impedían
la mejor solución: las cabeceras de OWASP apagaban WebRTC, los mapas y el pago incrustado;
compilar los catálogos en `ExecStartPre=` obligaba al servidor a escribir en su propio código, y el
respaldo no decía cómo salía de la máquina.

## Decisión

1. Las unidades viven en `plantilla/infra/`, y se instalan con los datos de cada app sin copiarse
   al repositorio.
2. `Permissions-Policy` niega cada función que la app no usa, y la que usa va con `(self)`.
3. No se envía `Cross-Origin-Embedder-Policy`.
4. `release.yml` compila los catálogos y el `.mo` viaja en el artefacto. Sale `ExecStartPre=`.
5. El respaldo sale con `restic`, cifrado, a un repositorio S3 externo, en una unidad que solo lee.

## Consecuencias

- Un cambio en las unidades se hace una vez en canone y llega a cada app al reinstalar.
- El código de una versión es de solo lectura para el servidor y no cambia entre arranques.
- Una app que use la cámara, el micrófono o la ubicación lo declara al instalarse.
- Restaurar pide `restic restore` y `pg_restore`.

## Descartado

- **`Permissions-Policy` de OWASP tal cual:** rompe WebRTC y la ubicación en los mapas.
- **COEP `credentialless`:** deja pasar las teselas, pero sigue bloqueando el iframe de pago, y el
  aislamiento que da no lo usa ninguna pieza.
- **`ReadWritePaths=` sobre `locale/`:** deja al servidor escribir en su propio código.
