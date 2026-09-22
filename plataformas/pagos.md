# Cobro

Cómo se cobra. El proveedor concreto es un detalle de implementación; esta página fija lo que no
cambia al cambiarlo.

## El SDK del proveedor vive en un solo directorio

```
services/billing/
  providers/
    base.py             el contrato: vocabulario interno
    registry.py         qué adaptador atiende a qué proveedor
    stripe_provider.py  el único que importa el SDK de Stripe
  checkout_service.py
  subscription_service.py
  credit_service.py
  webhook_service.py
```

**Nada fuera de `providers/` conoce el vocabulario de un proveedor concreto.** Ni un
`if event_type == "checkout.session.completed"`, ni un objeto de su SDK, ni una de sus excepciones.
El adaptador traduce el dialecto de la pasarela al vocabulario interno (`BillingEventType`,
`NormalizedEvent`), y el resto del sistema —motor de créditos, suscripciones, routers— habla solo
ese vocabulario.

Sin esa traducción, los nombres de los eventos del proveedor se filtran por todo el motor de cobro y
agregar un segundo rail vuelve a ser una reescritura. Eso es lo que esta capa existe para evitar.

Siendo honestos sobre lo que cuesta: agregar un proveedor siempre exige escribir su adaptador. Lo
que la capa garantiza es que ese trabajo quede confinado a un archivo, sin tocar el esquema, el
motor de créditos ni los endpoints.

## Agregar un proveedor

1. Escribir su adaptador cumpliendo el `Protocol` de `base.py`.
2. Agregar su valor a `PaymentProvider` en `core/enums.py`. **Requiere migración**, porque los enums
   llevan CHECK en la base; esa fricción es deseable: obliga a que el adaptador exista antes de que
   la base acepte el valor.
3. Registrarlo en el `registry.py`.
4. Cargar sus identificadores de precio en la tabla de referencias.

## Lo que no se puede uniformar va como capacidad

No toda pasarela hace todo. Lo que unas soportan y otras no se declara como **capacidad** que el
llamador consulta, no como método obligatorio del contrato que la mitad de los adaptadores tenga que
implementar vacío.

## Webhooks: idempotencia

Las pasarelas reenvían. Ante cualquier duda de entrega, repiten: es el comportamiento **normal y
documentado** de cualquier pasarela, no un caso raro. Sin idempotencia, un reenvío acredita el mismo
paquete dos veces.

**El mecanismo es insertar primero, no comprobar primero.** Se intenta insertar la fila del evento
—con `UNIQUE (provider, provider_event_id)`— dentro de la misma transacción que aplica el efecto; si
el `UNIQUE` la rechaza, el evento ya se procesó y se descarta sin tocar nada.

Comprobar y luego insertar en dos pasos **no sirve**: dos reenvíos concurrentes pasarían ambos la
comprobación —ninguno ve la fila del otro, que todavía no existe— y ambos aplicarían el efecto. La
única forma de resolver esa carrera es que el árbitro sea la base, no el código.

**Un evento que no se entiende igual se registra.** Un tipo desconocido, o uno cuyo usuario no se
puede resolver, se guarda con su estado y se descarta sin efecto. Devolver error haría que la
pasarela lo reintentara para siempre; perderlo sin registro dejaría un cobro real sin rastro.

La firma del webhook se verifica antes de mirar el cuerpo. Una firma inválida es un rechazo, no un
evento con estado.

## Dinero

`NUMERIC`, nunca `float`, y con los decimales que el dominio exige — ver
[postgres.md](postgres.md). Un importe opcional no lleva `server_default="0.00"`: «no aplica» y
«cero» no son lo mismo.
