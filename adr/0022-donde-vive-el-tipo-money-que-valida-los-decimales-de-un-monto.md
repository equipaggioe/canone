# ADR-0022 · Dónde vive el tipo `Money` que valida los decimales de un monto

- **Estado:** Reemplazada por [ADR-0023](0023-un-monto-se-guarda-como-numeric-sin-escala-y-sus-decimales-los-decide-cada-repositorio.md)
- **Fecha:** 2026-09-29
- **Alcance:** `plantilla/server/src/app/schemas/base.py`; los servidores que manejan montos

## Contexto

El servidor rechaza un monto con más decimales que la unidad menor de su moneda
([ADR-0020](0020-un-monto-se-guarda-como-numeric-sin-escala-junto-al-codigo-iso-4217-de-su-moneda.md)),
y un monto viaja como `{"amount": "10.50", "currency": "USD"}`
([ADR-0021](0021-un-monto-viaja-como-objeto-con-el-monto-en-cadena-y-los-clientes-no-calculan-con-el.md)).
El lugar natural de esa validación es un esquema `Money` de Pydantic con la tabla de unidades menores
de ISO 4217. La plantilla no tiene montos, y hoy ningún código lo llamaría.

## Opciones

- **Un `Money` canónico en `schemas/base.py`, con la tabla de ISO 4217:** todos los servidores
  validan igual y se verifica como el resto de los archivos canónicos. Es código que la plantilla no
  llama, y la tabla hay que mantenerla al día con la lista de ISO 4217.
- **Que lo escriba el primer repositorio que maneje montos, y de ahí pase a la plantilla:** no hay
  código sin uso, y el tipo sale de un caso real. Hasta que pase a la plantilla, un segundo
  repositorio puede escribir el suyo distinto.

## Decisión

Sin resolver.
