# ADR-0099 · Las trazas no se exportan, y ninguna variable de entorno agrega un exportador

- **Estado:** Aceptada
- **Fecha:** 2026-10-27
- **Alcance:** «Trazas» de [`plataformas/fastapi.md`](../plataformas/fastapi.md) y `main.py` y
  `test_conventions.py` de `plantilla/server/`

## Contexto

El punto 2 del
[ADR-0061](0061-las-trazas-salen-de-la-telemetria-de-fastapi-y-el-cliente-muestra-el-traceid.md)
dejó el `TracerProvider` sin exportador y mandó a despliegue la decisión de exportar.

Comprobado con FastAPI 0.162, la versión del `uv.lock` de la plantilla:

- Con `FASTAPI_OTEL_AUTO_CONFIGURE=true` y `OTEL_EXPORTER_OTLP_ENDPOINT`, FastAPI agrega al
  arrancar un `BatchSpanProcessor` con `OTLPSpanExporter` al `TracerProvider` de la app, y exporta
  también las métricas, sin cambiar el código. En la 0.142, el mínimo que pide la plantilla,
  `auto_configure` vale `True` por defecto y basta la segunda variable, leído en su código.
- Una petición produce cuatro spans: `fastapi.dependencies`, `fastapi.endpoint`,
  `fastapi.serialization` y el de la ruta. La app no instrumenta SQLAlchemy ni httpx, y el
  propagador no envía `traceparent`: ningún span ve la base ni sigue a otro servicio.

## Decisión

1. La app no exporta trazas ni métricas ni logs de OpenTelemetry: el `TracerProvider` no tiene
   exportador. Reemplaza el punto 2 del ADR-0061.
2. La app crea FastAPI con `telemetry={"auto_configure": False}`: ninguna variable de entorno le
   agrega un exportador.
3. `test_otlp_variables_export_nothing` arranca la app con las dos variables y comprueba que no
   agrega ningún procesador de spans.

## Consecuencias

- El trace-id une el log, el problem+json y `event_log` de una petición, en la máquina de la app.
- No hay duración por paso de una petición fuera de lo que diga el log.
- Se vuelve a evaluar cuando una petición siga a otro servicio con su contexto, o la app
  instrumente la base o el cliente HTTP: entonces una traza muestra algo que el log no.
- Exportar pediría además elegir el servicio OTLP y el muestreo, dejar fuera `/api/health` con
  `exclude` y filtrar los logs de excepciones que FastAPI emite con su mensaje y su stack trace.

## Descartado

- **Exportar por OTLP a un colector:** con solo los spans de FastAPI repite lo que dicen el log y
  el trace-id, y suma un servicio que mantener y otra copia de cada petición.
- **Confiar en que el entorno no tenga las variables:** el exportador dependería de dos sitios, la
  plantilla y la unidad, y en la 0.142 basta una variable estándar de OpenTelemetry.
