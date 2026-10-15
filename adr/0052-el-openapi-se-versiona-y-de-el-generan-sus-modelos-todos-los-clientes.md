# ADR-0052 · El OpenAPI se versiona, y de él generan sus modelos todos los clientes

- **Estado:** Aceptada
- **Fecha:** 2026-10-15
- **Alcance:** la sección «OpenAPI y clientes» de [plataformas/fastapi.md](../plataformas/fastapi.md#openapi-y-clientes)
  y de [plataformas/transversal.md](../plataformas/transversal.md#openapi-y-clientes); el servidor
  y sus clientes

## Contexto

La sección citaba *Generating SDKs* de FastAPI, que el
[ADR-0051](0051-un-tutorial-no-se-cita-y-lo-que-se-toma-de-el-es-regla-propia.md) deja sin citar,
y tenía una sola regla: el `operationId` era `<tag>-<función>`. Solo la web generaba su cliente
del OpenAPI; las apps y los clientes de escritorio escribían los modelos a mano.

## Decisión

1. La fuente es la especificación OpenAPI 3.1, la versión que genera FastAPI.
2. Cada router lleva un solo tag, y el `operationId` es el tag seguido del nombre de la función,
   en camelCase.
3. El OpenAPI se exporta a `server/openapi.json`, versionado, y una prueba falla si no coincide con
   la app.
4. Cada operación declara sus errores como `application/problem+json`, y el 422 con el esquema del
   problema `validation`.
5. En producción no se sirven el OpenAPI ni su documentación.
6. Cada cliente genera del `openapi.json` los modelos del cable, y ninguno los escribe a mano.

## Consecuencias

- Un cambio de contrato se ve en el diff, y los clientes generan sin levantar el servidor.
- Un cliente generado tipa el error que de verdad recibe.
- `flutter.md`, `android.md`, `flet.md` y `qt.md` escriben los modelos a mano, y «Nombres en el
  cable» pone la conversión en el cliente de la API: hay que revisarlos.
- La plantilla no declara todavía los errores en el OpenAPI ni lo apaga en producción.

## Descartado

- **`<tag>-<función>`:** un guion no forma un identificador, y OpenAPI recomienda seguir las
  convenciones de nombres de los lenguajes.
- **`<tag>_<función>` en snake_case:** el resto del documento está en camelCase.
- **Servir `/docs` en producción:** el contrato ya está en el repositorio, y nadie de afuera
  necesita el mapa de la API.
