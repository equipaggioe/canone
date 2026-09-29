# ADR-0020 · Un monto se guarda como `numeric` sin escala, junto al código ISO 4217 de su moneda

- **Estado:** Aceptada
- **Fecha:** 2026-09-29
- **Alcance:** [plataformas/pagos.md](../plataformas/pagos.md); los repositorios que guardan montos

## Contexto

[pagos.md](../plataformas/pagos.md) guardaba los montos en `bigint`, en la unidad menor de la
moneda, porque es la unidad de Stripe. Contradecía la recomendación de PostgreSQL, que da `numeric`
para montos (`datatype.sgml`), y el único motivo era un proveedor que solo importa el módulo
`payments/`.

## Decisión

1. Un monto es `numeric` sin precisión ni escala.
2. Va junto al código de su moneda de ISO 4217, en `text`.
3. El servidor rechaza un monto con más decimales que la unidad menor de su moneda, que da la lista
   de ISO 4217.
4. La conversión a la unidad menor que pida un proveedor de pagos se hace en `payments/`.

## Consecuencias

- Sigue la recomendación de PostgreSQL: no hay contradicción que justificar.
- Guarda fracciones de la unidad menor, como un precio unitario o un tipo de cambio.
- El valor se lee sin conocer la moneda: `10.50`, no `1050`.
- En Python un monto es `Decimal`, y mezclarlo con un `float` falla con `TypeError`.
- Validar los decimales exige que el servidor tenga la tabla de unidades menores de ISO 4217.
- Pydantic serializa un `Decimal` como cadena JSON (`"10.50"`), y TypeScript y Dart no traen un
  tipo decimal nativo.
- `numeric` calcula más lento que un entero; a la escala de estos productos no se mide.

## Descartado

- **`bigint` en la unidad menor:** es la unidad de Stripe, no un estándar, y contradice a
  PostgreSQL. No guarda fracciones de la unidad menor, `1050` no se entiende sin la tabla de
  decimales, y un error en esa tabla multiplica el monto por 100. Su ventaja, un entero exacto en
  todos los clientes, es del transporte y no del almacenamiento.
- **`numeric(19,4)`:** con escala declarada, `numeric` redondea sin avisar lo que la excede.
- **`money`:** su salida depende de `lc_monetary`, y guarda una sola moneda.
- **`real` o `double precision`:** la documentación de PostgreSQL los desaconseja para dinero por
  los errores de redondeo.
