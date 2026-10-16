# ADR-0051 · Un tutorial no se cita, y lo que se toma de él es regla propia

- **Estado:** Aceptada
- **Fecha:** 2026-10-15
- **Alcance:** `plataformas/` y `fuentes/`

## Contexto

El [ADR-0030](0030-una-pagina-cita-lo-que-adopta-en-su-mayoria-y-lo-demas-es-regla-propia.md)
fija que citar una fuente adopta todas sus convenciones. Un tutorial casi no las escribe: da pasos
y ejemplos, con «you could» en vez de MUST o SHOULD. *Generating SDKs* de FastAPI propone el
`operationId` de tag y función como «For example, you could…».

## Decisión

1. Un tutorial no se cita, como un blog, un curso o un foro. Lo que una página toma de él entra
   como regla propia.

## Consecuencias

- Una página que cita un tutorial deja de cumplir `plataformas/README.md` hasta que se revisa.
  `fastapi.md` cita todavía *Bigger Applications* y el tutorial de Alembic.
- *Generating SDKs* deja de citarse, y su copia sale de `fuentes/`.

## Descartado

- **Citar de un tutorial solo lo que escribe como recomendación:** con pasos y recomendaciones
  mezclados, no se puede saber qué convenciones adopta la cita.
