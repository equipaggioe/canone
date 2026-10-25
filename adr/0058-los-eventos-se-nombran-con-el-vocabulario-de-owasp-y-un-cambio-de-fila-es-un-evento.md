# ADR-0058 · Los eventos se nombran con el vocabulario de OWASP, y un cambio de fila es un evento

- **Estado:** Aceptada. La purga del punto 11 la reemplaza el [ADR-0080](0080-la-purga-de-event-log-es-una-funcion-y-una-ruta-de-salud-dice-que-alertar.md)
- **Fecha:** 2026-10-16
- **Alcance:** la sección «Registro de eventos» de
  [plataformas/fastapi.md](../plataformas/fastapi.md#registro-de-eventos); el servidor

## Contexto

El [ADR-0008](0008-un-sobre-unico-de-evento-y-el-catalogo-es-del-repositorio.md) fijó un sobre
propio para `event_log`: una categoría de cuatro valores, una acción de cada repositorio,
`outcome`, una severidad de cuatro niveles y una tabla aparte, `audit_log`, para los cambios de
fila. La página citaba entero el *Logging Cheat Sheet* de OWASP, y ninguna fuente nombraba los
eventos.

## Decisión

1. Del *Logging Cheat Sheet* se citan las secciones que rigen al servidor. *Network architecture*,
   *Release*, *Operation* y *Monitoring of events* quedan fuera.
2. Los eventos se nombran con la sección *The Vocabulary* del *Application Logging Vocabulary
   Cheat Sheet* de OWASP, citada en `fastapi.md`.
3. `action` es el nombre del vocabulario sin sus parámetros. Los parámetros van en sus columnas.
4. Sin `category` ni `outcome`: el prefijo y el nombre ya los dicen.
5. `level` es `info`, `warn` o `critical`, el nivel del vocabulario, en lugar de `severity`.
6. Una sola columna de tiempo, `occurred_at`.
7. Sin `audit_log`: un cambio de fila es un evento de `event_log`, con los campos cambiados en
   `details` y la misma lista blanca.
8. La retención es obligatoria y mayor que cero.
9. Renovar un token no lleva regla: ninguna fuente citada pide registrarlo.
10. Un evento se escribe en su propia transacción, salvo el de un cambio de fila, que va en la del
    cambio.
11. El rol de la app solo tiene `INSERT` y `SELECT` sobre `event_log`, y la purga usa otro rol. Es
    la forma de cumplir *Protection* y la cuenta aparte que prefiere *Where to record event data*.

## Consecuencias

- Reemplaza los puntos 1, 2, 4, 7 y 8 del ADR-0008, y la mitad del punto 6 que escribía todo en la
  transacción de la acción: un evento de fallo se perdía cuando la petición se deshacía.
- El servidor necesita una segunda credencial de base para la purga.
- Los repositorios renombran sus acciones al vocabulario y mudan `audit_log` a `event_log`.
- Lo que pasó alrededor de una hora, cambios de fila incluidos, se lee en una consulta.

## Descartado

- **El vocabulario como contrato en `transversal.md`:** solo el servidor escribe los eventos. El
  cliente recibe los nombres como valores de un enum del `openapi.json` y los traduce con su
  catálogo, y eso ya lo cubren «OpenAPI y clientes» e «Idiomas».
- **ASVS 5.0, capítulo V16:** regula lo mismo que los dos *cheat sheets* con requisitos más
  generales, y su sección 16.5 regula lo mismo que «Errores».
- **Las convenciones semánticas de OpenTelemetry:** ninguna pieza usa OpenTelemetry.
- **NIST SP 800-92:** trata de la infraestructura de logs, no de los eventos de una aplicación.
- **`category` y `outcome` junto al nombre del vocabulario:** dos campos con el mismo dato pueden
  contradecirse.
- **`audit_log` aparte:** el vocabulario ya tiene los eventos de cambio (`user_updated`,
  `sensitive_update`, `privilege_permissions_changed`), y con dos tablas lo que pasó a una hora
  deja de leerse en una consulta.
- **`created_at` además de `occurred_at`:** solo difieren si un cliente reporta eventos tarde, y
  ninguno lo hace.
- **`0` como retención indefinida:** *Disposal of logs* pide un período, y la IP y el user agent son
  datos personales.
