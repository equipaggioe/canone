# ADR-0012 · El prefijo `/api/v1` se aplica al montar

- **Estado:** Propuesta
- **Fecha:** 2026-09-23
- **Alcance:** `server/app/main.py`, `server/app/routers/`, y todo cliente que llame a la API

## Contexto

Reemplaza al [ADR-0005](0005-prefijo-api-al-montar.md), que fijaba `/api` al montar y sin versión,
porque todas las piezas se desplegaban juntas. Los puntos sobre dónde se aplica el prefijo se
mantienen; cambia solo la versión.

## Decisión

1. `API_PREFIX = "/api/v1"` en `main.py`, aplicado en cada `include_router`.
2. El `APIRouter` declara solo su recurso: `prefix="/vehicles"`.
3. Las rutas de operación interna van bajo `/api/v1/backoffice/...`.

## Consecuencias

- Es la forma que espera quien consume una API HTTP, y deja un lugar para un cambio incompatible
  sin renombrar rutas: una app instalada desde una tienda no se actualiza en el mismo despliegue que
  el servidor.
- Cambiar el prefijo sigue siendo una línea, y un router se lee sin saber dónde está montado.
- Hay que cambiar la URL base en cada cliente de los repositorios que hoy montan `/api`.
- Cuándo nace un `v2` y cuánto convive con el `v1` no se decide aquí: es un ADR del repositorio que
  lo necesite, y empieza por nombrar el cambio incompatible que lo obliga.

## Descartado

- **`/api` sin versión (ADR-0005):** no es lo que se recomienda para una API con clientes
  instalables, y agregar la versión después obliga a tocar todas las rutas de todos los clientes a
  la vez.
- **Versión en un encabezado (`Accept-Version`) o en la query:** no se ve en la URL, no se puede
  probar desde el navegador y el proxy no puede enrutar por ella sin configuración extra.
- **Sin prefijo:** el servidor también sirve los builds estáticos del panel y el backoffice; sin
  `/api`, las rutas de la API compiten con las del cliente.
