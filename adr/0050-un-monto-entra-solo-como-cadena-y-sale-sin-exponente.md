# ADR-0050 · Un monto entra solo como cadena y sale sin exponente

- **Estado:** Aceptada
- **Fecha:** 2026-10-12
- **Alcance:** la sección «Montos» de [plataformas/fastapi.md](../plataformas/fastapi.md#montos) y
  de [plataformas/transversal.md](../plataformas/transversal.md#montos); los servidores con montos

## Contexto

El [ADR-0021](0021-un-monto-viaja-como-objeto-con-el-monto-en-cadena-y-los-clientes-no-calculan-con-el.md)
fijó que un monto viaja en cadena y se apoyó en lo que Pydantic hace con un `Decimal` al
responder. No decidió cómo entra ni cómo se escribe la cadena. La sección 2.2 de I-JSON pide la
cadena a quien envía, y no dice nada de su sintaxis ni de lo que hace quien recibe.

Comprobado con Pydantic 2.13.5:

- Al recibir, acepta un número JSON y en el OpenAPI declara el monto como `number` o `string`. Un
  número que excede un `double` entra recortado sin error: `12345678901234567890.123` queda en
  `12345678901234567000`.
- Al responder, escribe el `Decimal` con `str`: `Decimal("0.0000001")` sale como `"1E-7"`. Su
  OpenAPI declara la cadena con el patrón `^(?!^[-+.]*$)[+-]?0*\d*\.?\d*$`, que no admite exponente.
- `Strict()` no rechaza un número JSON en un `Decimal`.

## Decisión

1. Un monto entra solo como cadena: el servidor rechaza un número JSON.
2. Un monto se serializa sin exponente.

## Consecuencias

- El OpenAPI de las peticiones declara el monto como `string`, y los clientes generados no aceptan
  un número.
- Un monto mal enviado falla con un error de validación en vez de entrar recortado.
- El servidor cumple el patrón que su propio OpenAPI publica.
- Pydantic no lo hace por defecto: cada servidor con montos declara el tipo con su validador y su
  serializador.

## Descartado

- **Aceptar número o cadena, como Pydantic por defecto:** el OpenAPI invita a los clientes a enviar
  un `double`, y lo que excede su precisión entra recortado sin aviso.
- **Dejar el exponente:** `Intl.NumberFormat` formatea `"1E-7"` bien, pero la respuesta no cumple
  el OpenAPI que publica el mismo servidor.
