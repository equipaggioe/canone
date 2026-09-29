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

## Montos

Estándares: el `numeric` de [*Data Types*](../estandares/postgresql/datatype.sgml) de PostgreSQL y
la [lista de monedas](../estandares/iso/iso-4217-list-one.xml) de ISO 4217.

- Un monto es `numeric` sin precisión ni escala, junto al código de su moneda en `text`. Con escala
  declarada, `numeric` redondea sin avisar lo que la excede.
- La conversión a la unidad menor que pide el proveedor se hace en `payments/`. El resto del servidor
  no conoce la unidad de Stripe.

## Idempotencia

Estándar: [*Idempotent requests*](../estandares/stripe/idempotent-requests.md) de Stripe.

## Webhooks

Estándar: los [webhooks](../estandares/stripe/webhooks.md) de Stripe.

- El ID de cada evento procesado se guarda con una restricción única. Un evento repetido choca con
  ella y no se procesa dos veces.
