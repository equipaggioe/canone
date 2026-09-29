# ADR-0023 · Un monto se guarda como `numeric` sin escala, y los decimales que admite los decide cada repositorio

- **Estado:** Aceptada
- **Fecha:** 2026-09-29
- **Alcance:** [plataformas/pagos.md](../plataformas/pagos.md); los repositorios que guardan montos

## Contexto

El [ADR-0020](0020-un-monto-se-guarda-como-numeric-sin-escala-junto-al-codigo-iso-4217-de-su-moneda.md)
fijó cómo se guarda un monto y, además, que el servidor rechaza uno con más decimales que la unidad
menor de su moneda. Esa regla chocaba con otra consecuencia del mismo ADR, la de guardar fracciones
de la unidad menor, como un precio unitario de USD 0.003. El
[ADR-0022](0022-donde-vive-el-tipo-money-que-valida-los-decimales-de-un-monto.md) preguntaba dónde
vive el tipo `Money` que haría esa validación.

Qué decimales admite un monto depende de lo que vende cada producto: una tienda cobra en centavos, y
un servicio que factura por llamada necesita fracciones de centavo. Es una regla de dominio, no de
plataforma.

## Decisión

1. Un monto es `numeric` sin precisión ni escala.
2. Va junto al código de su moneda de ISO 4217, en `text`.
3. La conversión a la unidad menor que pida un proveedor de pagos se hace en `payments/`.

## Consecuencias

- Sigue la recomendación de PostgreSQL: no hay contradicción que justificar.
- Guarda fracciones de la unidad menor, como un precio unitario o un tipo de cambio.
- Qué decimales admite un monto lo decide cada repositorio, según lo que vende.
- La plantilla no trae un tipo `Money` ni la tabla de unidades menores de ISO 4217.
- El valor se lee sin conocer la moneda: `10.50`, no `1050`.
- En Python un monto es `Decimal`, y mezclarlo con un `float` falla con `TypeError`.
- Pydantic serializa un `Decimal` como cadena JSON (`"10.50"`), y TypeScript y Dart no traen un
  tipo decimal nativo.
- `numeric` calcula más lento que un entero; a la escala de estos productos no se mide.

## Descartado

- **Que el servidor rechace un monto con más decimales que la unidad menor de su moneda** (punto 3
  del ADR-0020): es una regla de dominio, y prohíbe las fracciones de la unidad menor que `numeric`
  sin escala permite guardar.
- **Un tipo `Money` en la plantilla** (ADR-0022): sin esa regla no hay una validación común que
  ofrecer, y sería código que la plantilla no llama.
- **Que el primer repositorio con montos escriba el `Money` y de ahí pase a la plantilla:** la forma
  de un repositorio se volvería la convención de todos sin haberse decidido como tal.
- **`bigint` en la unidad menor:** es la unidad de Stripe, no un estándar, y contradice a
  PostgreSQL. No guarda fracciones de la unidad menor, `1050` no se entiende sin la tabla de
  decimales, y un error en esa tabla multiplica el monto por 100. Su ventaja, un entero exacto en
  todos los clientes, es del transporte y no del almacenamiento.
- **`numeric(19,4)`:** con escala declarada, `numeric` redondea sin avisar lo que la excede.
- **`money`:** su salida depende de `lc_monetary`, y guarda una sola moneda.
- **`real` o `double precision`:** la documentación de PostgreSQL los desaconseja para dinero por
  los errores de redondeo.
