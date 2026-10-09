# ADR-0042 · Una sesión vencida se borra sin gracia

- **Estado:** Aceptada
- **Fecha:** 2026-10-09
- **Alcance:** la sección «Tokens» de [`plataformas/fastapi.md`](../plataformas/fastapi.md)

## Contexto

El punto 6 del [ADR-0010](0010-la-sesion-es-estado-vivo-y-la-historia-esta-en-los-eventos.md)
purgaba las sesiones vencidas pasada una gracia sobre `expires_at`.

## Decisión

Reemplaza la gracia del punto 6 del ADR-0010.

1. La tarea periódica borra toda sesión vencida.

## Consecuencias

- La purga es una sola condición sobre `expires_at`.

## Descartado

- **Una gracia sobre `expires_at`:** una sesión vencida se rechaza igual, así que la gracia no evita
  ningún síntoma.
