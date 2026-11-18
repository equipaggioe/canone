# Qué tecnología usa una app según quién la usa

Tema pendiente: **sin decidir**.

## Estado (verificado 2026-11-18)

[flutter.md](../plataformas/flutter.md) dice que la app sale en Android y en iOS, y [despliegue.md](../plataformas/despliegue.md#versiones) que la PWA es `web/`, en SvelteKit. Caddy sirve solo `landing` en el dominio, `web` en `app.` y `panel` en `panel.`. Nada decide la tecnología por el público de la app, ni dónde vive una segunda PWA.

posta tiene dos apps en Flutter, cada una pensada para Android y como PWA: MobileCustomer, la del cliente que manda paquetes, y MobileOperations, la del empleado de sucursal. Sus PWA no se publican.

## Qué hay que decidir

La dirección que dio el desarrollador el 2026-11-18, sin cerrar todavía:

| Público | Propuesta | Qué falta decidir |
| :--- | :--- | :--- |
| Clientes | Solo PWA, en SvelteKit | Si es `web/` u otra pieza, y en qué host |
| Operadores | Android, y por ahora también PWA | En qué host va esa PWA, y si sale de Flutter o de SvelteKit |

Con eso cambian `flutter.md`, «Caddy» y «Versiones» de `despliegue.md`, los hosts de Consola (`canone.hosts`) y `install.py --without`.

## Cuándo se retoma

Antes de publicar las apps de posta, y antes de que otro producto agregue una app para sus clientes.
