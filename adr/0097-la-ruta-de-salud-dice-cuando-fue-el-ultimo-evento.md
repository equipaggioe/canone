# ADR-0097 · La ruta de salud dice cuándo fue el último evento

- **Estado:** Aceptada
- **Fecha:** 2026-10-27
- **Alcance:** «Salud» de [`plataformas/fastapi.md`](../plataformas/fastapi.md) y `plantilla/server/`

## Contexto

Si `event_log` deja de recibir eventos, nadie se entera. Comprobado en Debian 13.5 con
PostgreSQL 17.11: sin `INSERT` sobre `event_log`, escribir un evento `critical` falla con
`permission denied`, `GET /api/health` responde 204 y `GET /api/health/events` responde
`lastCriticalAt: null`, lo mismo que cuando no pasó nada grave.

## Decisión

1. `GET /api/health/events` responde también `lastEventAt`, la hora del último evento de
   cualquier nivel, o `null`. Quien la consulta decide cuándo avisar, como con las fechas del
   [ADR-0080](0080-la-purga-de-event-log-es-una-funcion-y-una-ruta-de-salud-dice-que-alertar.md).
2. Es una regla propia: *Operation* del *Logging Cheat Sheet* sigue fuera de la cita, como fijó el
   punto 1 del
   [ADR-0058](0058-los-eventos-se-nombran-con-el-vocabulario-de-owasp-y-un-cambio-de-fila-es-un-evento.md).

## Consecuencias

- Una app sin tráfico pasa horas sin eventos: el umbral de quien vigila depende de la app.
- Leer la hora no escribe nada: la ruta responde aunque `event_log` no acepte escrituras.

## Descartado

- **Citar *Operation*:** adopta también detectar la manipulación de los registros, que remite a
  *Protection*, ya citada en «Registro de eventos», y dos partes citadas regularían lo mismo.
- **Que la ruta escriba un evento de prueba:** cada consulta de quien vigila llenaría `event_log`.
- **Que la ruta compruebe el permiso `INSERT` del rol:** no ve un servidor que deja de llamar a
  `record`.
