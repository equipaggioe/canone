# ADR-0027 · El prefijo `/api` va sin versión, en un `APIRouter` de `main.py`

- **Estado:** Aceptada
- **Fecha:** 2026-10-01
- **Alcance:** [`plataformas/fastapi.md`](../plataformas/fastapi.md),
  `plantilla/server/src/app/main.py` y `routers/`, y todo cliente que llame a la API

## Contexto

El [ADR-0012](0012-el-prefijo-api-v1-se-aplica-al-montar.md) proponía `/api/v1` porque «`/api` sin
versión no es lo que se recomienda para una API con clientes instalables». Ningún estándar de
`fuentes/` lo recomienda: *Bigger Applications* y *Behind a Proxy* de FastAPI usan `/api/v1`
solo como ejemplo, y las guías de empresas se contradicen (Google pone la versión en la ruta,
Microsoft en el query, Zalando pide no versionar).

Una app instalada con una versión vieja ya tiene salida: la versión mínima de cliente de
`fastapi.md` le pide actualizar.

*Behind a Proxy* describe dos montajes: el proxy quita el prefijo y la app usa `root_path`, o la app
declara las rutas completas.

## Decisión

1. La API va bajo `/api`, sin versión.
2. Los routers se incluyen en un `APIRouter(prefix="/api")` de `main.py`, y cada uno declara solo su
   recurso.

## Consecuencias

- Las rutas de las pruebas, los logs y el OpenAPI son las que ve el cliente, también en desarrollo
  sin proxy.
- Si un cambio incompatible tiene que convivir con apps instaladas, `/api/v2` se agrega junto a
  `/api` sin tocar ninguna ruta existente.

## Descartado

- **`/api/v1` desde ahora:** no elimina ningún síntoma hoy, y la versión se puede agregar después.
- **El proxy quita el prefijo y la app usa `root_path`:** las rutas de la app dejan de ser las del
  cliente, y cada arranque tiene que pasar el `root_path`.
- **Cada router declara `/api` en su `prefix`:** el prefijo se repite y es fácil olvidarlo.
