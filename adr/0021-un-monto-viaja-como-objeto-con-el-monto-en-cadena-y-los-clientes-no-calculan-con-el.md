# ADR-0021 · Un monto viaja como objeto con el monto en cadena, y los clientes no calculan con él

- **Estado:** Aceptada
- **Fecha:** 2026-09-29
- **Alcance:** [plataformas/fastapi.md](../plataformas/fastapi.md) y la tabla de lo que cruza
  plataformas en [plataformas/README.md](../plataformas/README.md); el servidor y todos sus clientes

## Contexto

Un monto se guarda como `numeric` ([ADR-0020](0020-un-monto-se-guarda-como-numeric-sin-escala-junto-al-codigo-iso-4217-de-su-moneda.md)),
y en Python es un `Decimal`. Pydantic lo serializa como cadena JSON (`"10.50"`) y lo declara en el
OpenAPI como `type: string`. TypeScript y Dart leen un número JSON como `double`, y ninguno de los dos
trae un tipo decimal.

## Decisión

1. Un monto viaja como `{"amount": "10.50", "currency": "USD"}`: el monto en cadena decimal y el
   código ISO 4217 de su moneda.
2. Cada cliente conserva el monto como cadena o como el decimal de su lenguaje, nunca como `double`.
3. Los clientes no calculan con montos: los totales, impuestos y descuentos llegan calculados del
   servidor.

## Consecuencias

- Sigue la recomendación de I-JSON (RFC 7493 §2.2) para un número que debe llegar exacto, y es lo
  que Pydantic ya hace con un `Decimal`.
- El monto y su moneda no se separan: la función que formatea recibe un solo valor.
- Ningún cliente necesita una biblioteca decimal. `Intl.NumberFormat` formatea la cadena sin pasar
  por `double`.
- El servidor arma el objeto a partir de dos columnas.
- Un recurso con varios montos en la misma moneda la repite en cada uno.
- Si un cliente llega a necesitar calcular sin conexión, necesita una biblioteca decimal y esta
  decisión se revisa.

## Descartado

- **Un número JSON (`10.50`):** llega como `double` a TypeScript y Dart, y va contra I-JSON.
- **Un entero en la unidad menor (`1050`):** obliga a convertir en cada respuesta, no lleva
  fracciones de la unidad menor, y cada cliente necesita la tabla de decimales de ISO 4217 para
  mostrarlo.
- **El monto y la moneda como dos campos hermanos:** nada impide que un recurso mande el monto sin
  la moneda, y formatear pide dos valores.
- **Una biblioteca decimal en cada cliente:** trae un cálculo que el servidor ya hace, y el monto
  que se cobra es el que calcula el servidor.
