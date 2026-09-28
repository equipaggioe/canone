# Pagos

Cómo se cobra.

## Proveedor

Estándar: [*Secure Integration of Third-Party Payment Gateways Cheat Sheet*](../estandares/owasp/Third_Party_Payment_Gateway_Integration.md)
de OWASP.

- El proveedor es Stripe, y solo el módulo `payments/` del servidor lo importa. Cambiar de proveedor
  toca un módulo.
- El cobro se hace en Stripe Checkout, la página alojada por Stripe. Los datos de la tarjeta nunca
  pasan por nuestras páginas.
- Un pago cuenta como hecho solo cuando llega su webhook. El regreso del navegador no prueba nada.
- Los montos se guardan en `bigint`, en la unidad menor de la moneda, junto al código ISO 4217 en
  `text`. Contradice el `numeric` que [postgres.md](postgres.md) cita para montos: es la unidad de
  Stripe, y no hay conversión que redondear.

## Idempotencia

Estándar: [*Idempotent requests*](../estandares/stripe/idempotent-requests.md) de Stripe.

## Webhooks

Estándar: los [webhooks](../estandares/stripe/webhooks.md) de Stripe.

- El ID de cada evento procesado se guarda con una restricción única. Un evento repetido choca con
  ella y no se procesa dos veces.
