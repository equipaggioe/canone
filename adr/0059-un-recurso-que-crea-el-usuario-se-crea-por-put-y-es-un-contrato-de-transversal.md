# ADR-0059 · Un recurso que crea el usuario se crea por `PUT`, y es un contrato de transversal

- **Estado:** Aceptada, salvo el punto 2, que sigue en propuesta
- **Fecha:** 2026-10-16
- **Alcance:** la sección «Reintentos» de
  [plataformas/transversal.md](../plataformas/transversal.md#reintentos) y de
  [plataformas/fastapi.md](../plataformas/fastapi.md#reintentos); el servidor y sus clientes

## Contexto

`fastapi.md` pedía `PUT` con un uuid del cliente para «una creación que el cliente puede
reintentar». La regla la cumple sobre todo el cliente, que genera el id y elige el método, y la
condición no separaba nada: cualquier creación puede perder su respuesta.

## Decisión

1. La regla va en `transversal.md`, y `fastapi.md` la enlaza como contrato.
2. Un recurso que el usuario crea desde un cliente se crea por `PUT /<recurso>/{id}`, con un uuid v4
   que genera el cliente.
3. El cliente reintenta solo una petición idempotente ante un fallo de red, un 502, un 503 o un
   504, hasta 3 veces, con espera exponencial y jitter.

## Consecuencias

- Una lista propia del equipo sigue creándose por `POST`, con el id de la base, como fija el
  [ADR-0024](0024-la-clave-primaria-se-elige-por-lo-que-guarda-la-tabla.md).
- Un reinicio del servidor de pocos segundos no llega al usuario como error.
- El registro de una cuenta entra en la regla: un reintento cae sobre la misma cuenta en vez de
  responder 409.

## Descartado

- **Toda creación desde un cliente:** abarca el login y las listas del equipo, que no la necesitan.
- **`POST` con el encabezado `Idempotency-Key`:** es un borrador de IETF, y obliga a guardar cada
  clave con su respuesta. Con `PUT`, la clave primaria rechaza el duplicado.
- **uuid v7 generado en el cliente:** expone la hora de su reloj, y PostgreSQL 17 genera v4.
