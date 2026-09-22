# Despliegue: VPS, Caddy y `consola`

Aplica a todo repositorio que se despliegue. Hoy: los seis.

Leído de `consola/core` y de `.consola/config.env` y `.consola/Caddyfile.generado` de los
repositorios.

## El contrato

Un repositorio no trae scripts de despliegue propios. Declara su configuración en
`.consola/config.env` y `consola` hace el resto: crea el usuario del VPS, clona, arma el entorno,
configura Postgres, escribe el servicio de systemd y genera el Caddyfile.

**`.consola/config.env` lo genera y lo edita `consola`, no se escribe a mano**, y nunca se
commitea: tiene tokens, contraseñas de base y secretos de TURN.

| Bloque | Qué declara |
|---|---|
| Server | `API_URL` |
| Cloudflare | `CF_API_TOKEN`, `CF_DOMAIN_NAME`, `CF_RECORD_NAME` |
| VPS | `VPS_IP`, `ROOT_USER`, `VPS_USER`, `VPS_KEY_NAME`, `VPS_PYTHON`, `VPS_DEPLOY_DIR`, `PUBLIC_HOST`, `SECRET_FILES` |
| Base | `DB_USER`, `DB_NAME`, `DB_PASSWORD`, `PG_SUPERUSER`, `PG_PASSWORD`, `DB_EXTENSIONS` |
| Web | `PUBLIC_ROUTES`, `CSP` |
| GitHub | `GIT_REPO_URL`, `GITHUB_TOKEN`, `GITHUB_KEY_TITLE` |
| systemd | `SERVER_DIR`, `BACKEND_HOST`, `BACKEND_PORT`, `CERT_FILE_PATH`, `KEY_FILE_PATH`, `UVICORN_APP`, `SERVICE_DIRS` |
| TURN | `TURN_SECRET`, `TURN_PORT`, `TURN_RELAY_RANGE`, solo si el producto tiene llamadas |

Un repositorio por usuario del VPS y una base por usuario: los valores por defecto son el nombre del
repositorio y `<VPS_USER>_db`.

## Caddy

**El Caddyfile se genera, no se escribe.** `.consola/Caddyfile.generado` es una copia de referencia
y su propio encabezado lo dice:

> Copia de referencia. El que usa Caddy es `/etc/caddy/Caddyfile` en el VPS. Lo genera Consola desde
> `CADDY_ROUTES`: editar esto no cambia nada.

Editarlo a mano crea una segunda fuente de verdad que la próxima generación pisa sin avisar.

Lo que produce, por host:

| Pieza | Regla |
|---|---|
| Compresión | `encode zstd gzip` |
| HSTS | `Strict-Transport-Security "max-age=31536000; includeSubDomains"` |
| Cabeceras | `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin` |
| CSP | Sale de `CSP`; **cada regla lleva su host**, una CSP sin host es la de todos los sitios |
| `frame-ancestors` | `'none'` salvo que el producto necesite incrustarse |
| API y WebSocket | `handle /api/*` y `handle /ws/*` → `reverse_proxy 127.0.0.1:8000` |
| Superficies web | El build estático, con `index.html` como respaldo para las rutas del cliente |

El backend escucha en `127.0.0.1`, nunca en `0.0.0.0`: lo único expuesto es Caddy.

## Lo que no va al repositorio

- `.consola/config.env`: secretos.
- El `.env` del servidor: se copia al VPS vía `SECRET_FILES`, no se commitea.
- Certificados y `*service-account*.json`.
- El Caddyfile real: vive en `/etc/caddy/` del VPS.

## Todas las piezas se despliegan juntas

No hay versionado entre piezas ni clientes viejos que sostener — ver
[principios.md](../principios.md). El repositorio que llegue a producción lo dirá en su
`docs/arquitectura/00_sistema.md`.
