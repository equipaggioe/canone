# ADR-0138 · Un FID al que FCM responde `UNREGISTERED` se borra

- **Estado:** Aceptada
- **Fecha:** 2026-11-12
- **Alcance:** «Push» de [`plataformas/fastapi.md`](../plataformas/fastapi.md)

## Contexto

«Push» decía qué hacer con una suscripción web que el servicio de push da por vencida —se borra
con un 404 o un 410—, y nada de un FID que FCM rechaza. La guía de Firebase sobre los tokens de
registro dice que un envío que recibe `UNREGISTERED` apunta a un token que no va a volver a
servir. Sin borrarlo, cada aviso a esa persona vuelve a intentar un FID muerto.

## Decisión

1. Un FID al que FCM responde `UNREGISTERED` se borra. La convención es propia y enlaza la guía de
   Firebase.

## Consecuencias

- La regla queda igual que la de Web Push: lo que el servicio de push da por ausente se borra.
- La plantilla no envía push, así que ninguna prueba de Canone la hace cumplir.

## Descartado

- **Borrarlo también con `INVALID_ARGUMENT`.** FCM lo responde también a un mensaje mal armado, y
  borraría un FID que sirve.
- **Adoptar la guía de Firebase como fuente.** Sus demás reglas dan la vigencia del token por su
  edad, como borrar los que llevan un mes sin conectarse, y en Canone la da la sesión: «El FID y la
  suscripción web pertenecen a la sesión», en `transversal.md`.
