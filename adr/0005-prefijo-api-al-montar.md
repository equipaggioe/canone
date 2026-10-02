# ADR-0005 · El prefijo `/api` se aplica al montar, y la ruta no lleva versión

- **Estado:** Reemplazada por [ADR-0027](0027-el-prefijo-api-va-sin-version-en-un-apirouter-de-main.md)
- **Fecha:** 2026-09-22
- **Alcance:** `server/app/main.py`, `server/app/routers/`

## Contexto

Hay cuatro formas en cinco repositorios: sin prefijo (navetta, vettore), `/api` dentro de cada
`APIRouter` (presenze), `/api` en `include_router` (concordia), y `/api/v1` en `include_router`
(banditore).

## Decisión

1. `API_PREFIX = "/api"` en `main.py`, aplicado en cada `include_router`.
2. El `APIRouter` declara solo su recurso: `prefix="/vehicles"`.
3. La ruta **no lleva versión**.
4. Las rutas de operación interna van bajo `/api/backoffice/...`.

## Consecuencias

- Cambiar el prefijo es una línea.
- Un router se puede leer sin saber dónde está montado.
- Cuando algún producto llegue a producción con clientes instalados, habrá que decidir el
  versionado. Ese es un ADR de ese repositorio, ese día.

## Descartado

- **`/api/v1` desde ahora:** ningún repositorio está en producción y todas las piezas se despliegan
  juntas. Un `v1` que nunca tendrá un `v2` es un prefijo decorativo que hay que escribir en cada
  cliente.
- **Sin prefijo:** el servidor también sirve los builds estáticos del panel y el backoffice; sin
  `/api`, las rutas de la API compiten con las del cliente.
