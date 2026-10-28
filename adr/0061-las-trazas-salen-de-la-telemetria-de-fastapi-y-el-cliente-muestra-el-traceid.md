# ADR-0061 · Las trazas salen de la telemetría de FastAPI, y el cliente muestra el `traceId`

- **Estado:** Aceptada. El punto 2 lo reemplaza
  [ADR-0099](0099-las-trazas-no-se-exportan-y-ninguna-variable-de-entorno-agrega-un-exportador.md)
- **Fecha:** 2026-10-16
- **Alcance:** «Trazas» de [plataformas/fastapi.md](../plataformas/fastapi.md#trazas), «Errores» de
  [plataformas/transversal.md](../plataformas/transversal.md#errores), y `tracing.py`, `errors.py` y
  `pyproject.toml` de `plantilla/server/`

## Contexto

Un middleware de `tracing.py` generaba el trace-id con `secrets.token_hex(16)`. Desde la 0.142,
FastAPI trae OpenTelemetry y lo documenta en *OpenTelemetry*: crea un span por petición y por
WebSocket si hay un `TracerProvider`, y por defecto continúa el `traceparent` que llega. «Trazas»
citaba solo Trace Context, y decía que el usuario ve el `traceId` sin que ningún cliente lo
mostrara.

## Decisión

1. «Trazas» cita las secciones *Customize telemetry* y *Choose what to record* de *OpenTelemetry* de
   FastAPI, y la regla `trace-id` de la sección 3.2.2.2 y la sección 3.2.2.3 de Trace Context. La
   sección 8 de Trace Context sale: el id lo genera el SDK de OpenTelemetry.
2. La app configura un `TracerProvider` del SDK, sin exportador. Exportar las trazas se decide en
   despliegue.
3. Un propagador propio ignora `traceparent`, como pedía el punto 7 del
   [ADR-0015](0015-el-sobre-de-error-sigue-el-rfc-9457.md).
4. Cada vuelta de una tarea periódica empieza su propia traza.
5. Que todo problem+json lleva `traceId` pasa a transversal, y el cliente lo muestra ante un 5xx o
   un `type` que su catálogo no conoce.
6. La plantilla pide `fastapi[standard]>=0.142` y declara `opentelemetry-api` y
   `opentelemetry-sdk`, que importa.

## Consecuencias

- El día que se agregue un exportador, el id de los logs y de los errores es el de la traza en el
  servicio de monitoreo.
- Las `BackgroundTasks` quedan en la traza de su petición, y un WebSocket tiene un trace-id por
  conexión.
- El handler de las excepciones sin atrapar ve el trace-id del span de la petición: la consecuencia
  del ADR-0015 sobre el middleware de `tracing.py` ya no aplica.

## Descartado

- **Conservar el middleware propio.** Repite lo que hace FastAPI, y su id no sería el de la traza
  de FastAPI.
- **`OTEL_PROPAGATORS=none`.** Con él, el propagador devuelve un contexto vacío como `None`, y
  FastAPI 0.142 falla en cada petición.
- **Continuar el `traceparent`.** El cliente elegiría el id con el que se buscan sus registros, y
  Trace Context advierte, en su sección 7.2, que así se falsifican ids repetidos.
- **Un trace-id por mensaje de WebSocket.** Sus errores no llegan al usuario como problem+json, y
  los mensajes de una llamada se leen mejor juntos.
