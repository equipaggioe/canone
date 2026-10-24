# ADR-0070 · Las unidades cargan entera la carpeta de credenciales, y `Permissions-Policy` sigue a OWASP

- **Estado:** Aceptada
- **Fecha:** 2026-10-23
- **Alcance:** «Configuración» y «Caddy» de [`plataformas/despliegue.md`](../plataformas/despliegue.md),
  «Configuración» de [`plataformas/fastapi.md`](../plataformas/fastapi.md), `plantilla/infra/` y
  `plantilla/server/src/app/config.py`

## Contexto

Las unidades de `plantilla/infra/` nombraban una por una las credenciales de `Settings`, pero
`Settings` es un punto de partida: una app con otro secreto, como el de coturn, no podía usar las
unidades sin editarlas, y el
[ADR-0069](0069-el-servidor-se-instala-desde-plantilla-infra-y-sus-cabeceras-no-frenan-a-las-apps.md)
las instala sin copiarlas.

El punto 2 del ADR-0069 se escribió como contradicción de OWASP, pero la recomendación del
*HTTP Security Response Headers Cheat Sheet* es «disable all the features that your site does not
need or allow them only to the authorized domains»; la cámara, el micrófono y la ubicación negados
son solo su ejemplo.

## Decisión

1. Las unidades cargan con `LoadCredentialEncrypted=app:/etc/credstore.encrypted/<app>` la carpeta
   entera, y cada archivo se cifra con `--name=app_<campo>`.
2. `Settings` usa `env_prefix="app_"` y lee solo los archivos de `CREDENTIALS_DIRECTORY`.
3. Las credenciales que el servidor no usa van en `<app>-migrate/`, `<app>-backup/` y
   `<app>-deploy/`. La unidad de migraciones carga además `app_database_url` desde
   `<app>-migrate/`, que gana sobre la de la carpeta.
4. `Permissions-Policy` sigue la recomendación de OWASP, y la función que la app usa va con
   `(self)`. Reemplaza el punto 2 del ADR-0069.

## Consecuencias

- Un campo nuevo de `Settings` es un archivo nuevo en la carpeta, sin tocar las unidades.
- En desarrollo y en el CI, las credenciales son archivos `app_<campo>` en una carpeta, no
  variables de entorno.
- Un archivo cifrado con otro `--name` no carga: systemd compara el nombre.

## Descartado

- **Una línea por credencial en cada unidad:** obliga a editar unidades que se instalan sin
  copiarse.
- **Leer también las variables de entorno:** un valor podría venir de dos lugares.
