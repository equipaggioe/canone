> **Apuntes personales sin revisar. No es una convención ni una fuente: no se toma en cuenta para
> nada.**

# Estándar API Backend


## Guia de Implementación
- Las reglas sin etiqueta aplican a **todos los proyectos**.
- Las reglas con `[multi-tenant]` aplican **solo** a proyectos SaaS donde cada tenant opera como sistema independiente.
- Las reglas con `[single-system]` aplican **solo** a proyectos donde todos los usuarios coexisten en un mismo sistema compartido.
- Ambas etiquetas son mutuamente excluyentes: en cada proyecto solo aplica una.


## Reglas Obligatorias
- No usar contratos dobles ni compatibilidad temporal.
- Si una regla no aplica, dejar excepción explícita en código y prueba.
- Los endpoints DELETE en routers deben ser hard delete. No deben implementar soft delete.

## 1. Convención de nombres
- El código Python usa `snake_case` (PEP 8).
- El JSON de la API usa `snake_case`: cuerpos de entrada, respuestas, errores y query params.
- Los schemas no declaran alias de otra convención (`camelCase` u otra). El nombre del campo en Python es el nombre en el JSON.

## 2. Schemas
- Cada entidad expone:
  - `XxxCreate` para altas.
  - `XxxUpdate` para modificaciones parciales.
  - `XxxRead` para lectura.
- Los inputs heredan de `SchemaInputBase` (`extra="forbid"`).
- `[multi-tenant]` `tenant_id` no viaja en `Create/Update` de recursos tenant-scoped.

## 3. Capa de Router y Servicio
- Router: dependencias, llamada a servicio, respuesta.
- Servicio: reglas de negocio, ownership y persistencia.

## 4. Respuestas
- Endpoint no paginado devuelve schema directo.
- Listado paginado devuelve `PageResponse[T]` con `items` y `meta`.
- Paginación usa `PaginationParams.offset` y `PaginationParams.limit`.

## 5. Errores
- Errores controlados usan `HTTPException` (o subclases propias de ella) y handlers globales.
- Todo error sale con el contrato único, incluidos los que genera el framework (ruta inexistente, método no permitido) y las excepciones no controladas.
- Contrato único: `ErrorResponse { status, detail, error_code, errors?, request_id? }`.
- `error_code` debe ser suficientemente específico para que el cliente actúe sin parsear `detail`.
- Preferir `404` sobre `403` para no confirmar existencia de recursos ajenos.
- Reservar `403` para casos donde la existencia es pública pero el acceso está denegado.
- Mapeo mínimo:
  - `400 -> bad_request`
  - `401 -> unauthorized`
  - `403 -> forbidden | insufficient_permissions`
  - `404 -> not_found | resource_deleted`
  - `409 -> conflict`
  - `422 -> validation_error`
  - `429 -> rate_limit_exceeded`
  - `500 -> internal_error`
  - `503 -> service_unavailable`
- `[multi-tenant]` Errores adicionales:
  - `403 -> wrong_tenant`
  - `409 -> tenant_limit_reached`
