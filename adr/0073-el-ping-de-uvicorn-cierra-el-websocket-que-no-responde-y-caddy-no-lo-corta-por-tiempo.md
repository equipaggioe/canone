# ADR-0073 · El ping de Uvicorn cierra el WebSocket que no responde, y Caddy no lo corta por tiempo

- **Estado:** Aceptada
- **Fecha:** 2026-10-23
- **Alcance:** «Caddy» de [`plataformas/despliegue.md`](../plataformas/despliegue.md)

## Contexto

«Caddy» cita *Infrastructure Configuration* del *WebSocket Security Cheat Sheet* de OWASP, que pide
timeouts de lectura apropiados para las conexiones largas, y la página no fijaba ninguno.

## Decisión

1. Caddy no tiene timeout para una conexión WebSocket.
2. Uvicorn manda un ping cada 20 s y cierra la conexión que no responde en 20 s, con
   `--ws-ping-interval` y `--ws-ping-timeout` en sus valores por defecto.

## Consecuencias

- Comprobado con Caddy 2.6.2 de Debian 13, el Caddyfile de `plantilla/infra/`, Uvicorn 0.54.0 y
  websockets 17.1: un cliente que no responde los pings recibe el ping a los 20 s y el cierre a los
  40 s, y Caddy cierra su TCP en ese momento; un cliente que responde sigue abierto a los 330 s,
  más que el `idle_timeout` de 5 minutos de Caddy.
- Una conexión viva y en silencio no se corta, y una caída no queda abierta más de 40 s.

## Descartado

- **`read_timeout` en el transporte de `reverse_proxy`:** no detecta nada que el ping no detecte, y
  suma un segundo tiempo que mantener junto al de Uvicorn.
- **`stream_timeout` de `reverse_proxy`:** no existe en Caddy 2.6.2, y corta también una conexión
  viva.
