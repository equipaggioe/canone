# ADR-0211 · `transversal.md` escribe entero cada criterio de WCAG que adopta, la API lleva la fecha sin hora y la zona horaria, y `brand/tokens/` dice lo que no sigue de DTCG

- **Estado:** Aceptada. El usuario pidió aplicar los veredictos de la revisión (2026-11-21). Que el valor de `type` de un mensaje de WebSocket vaya en snake_case no lo confirmó: queda como propuesta abierta
- **Fecha:** 2026-11-21
- **Alcance:** [plataformas/transversal.md](../plataformas/transversal.md), `flet.md`, `despliegue.md`, `plantilla/scripts/tokens.py` y `plantilla/server/tests/test_conventions.py`

## Contexto

Se revisó `transversal.md` con los cinco pasos de [plataformas/README.md](../plataformas/README.md#revisión). Cada fila de «Cumplimiento» se probó rompiendo a propósito su convención, con Python 3.13.5, PostgreSQL 17.12 y Valkey 8.1.1 de Debian 13. Lo comprobado:

- Las pruebas del servidor no fallaban sin el chequeo de los no-caracteres U+FDD0 a U+FDEF, ni con la página de un tipo de problema sin su código de estado. `tokens.py` aceptaba un `$description` y un `name` del resolver que no eran cadenas, y rechazaba un alias sin `$type`, que DTCG Format §5.2.2 tipa con el token al que apunta. También rechaza referencias encadenadas, el valor `none` de un componente, tokens en línea en el resolver, claves junto a un `$ref` y un `$ref` a una parte de un archivo, que las partes que la página decía seguir permiten. DTCG Resolver §4.1.5.1 pide al menos dos contextos por modificador, y `tokens.py` acepta uno.
- `verificar.py --variables` falla con una variable `RELEASE_` que falta, que no vale `true` ni `false` o que no es de ninguna pieza. `tokens.py --check` falla con un rol sin asignar y con un custom color mal nombrado, incompleto o ausente en algún tema o modo, y con lo generado de Flutter, Compose, Flet, Qt y SvelteKit editado o borrado.
- Varias convenciones de «Accesibilidad» quitaban excepciones o requisitos de su criterio: 1.4.5, 1.4.11, 2.1.2, 2.2.1, 2.2.2, 2.4.5, 2.5.2, 2.5.4, 2.5.7, 3.2.3, 3.2.6 y 3.3.8. La de nivel AA repetía las demás, salvo los medios pregrabados, que ningún producto ofrece.
- «Un cliente falla ante un campo que no conoce» contradecía la convención de RFC 9457 §3.2 de ignorar una extensión desconocida de un problem+json.
- La API de `concordia` lleva una fecha sin hora (`birth_date`), y la de `cadenza`, una zona horaria por su nombre IANA. Los mensajes de WebSocket de `concordia` usan un `type` con punto, `message.send`, y los de `equipaggio` y `presenze`, palabras sueltas.
- coturn 4.6.1 de Debian 13 no abre una asignación con una credencial de `use-auth-secret` vencida, y sí con una vigente. Leído en `get_user_key` de `userdb.c`. El README que enlazaba la página no lo dice.
- Leído: MapLibre GL JS 6.18.0 pliega la atribución en un mapa de hasta 640 px; maplibre_gl 0.28.0 y MapLibre Android 13.7.1 la muestran tras un botón. Apple anunció que en macOS Sequoia una app sin notarizar no abre con Control-clic. Flutter 3.47.9 tiene 46 colores no obsoletos en `ColorScheme`. OData 4.01 no dice qué hacer con un tamaño de página negativo, ni que el enlace a la página siguiente no da permisos, ni que los demás parámetros se repitan: no le gana a AIP-158.

## Decisión

1. Cada criterio de WCAG que adopta «Accesibilidad» se escribe con sus excepciones y requisitos, como su origen. Sale «Todos los clientes cumplen el nivel AA». El objetivo de 48 × 48 lleva su origen, §2.5.8, como elección.
2. Un cliente falla ante un campo desconocido de una respuesta del servidor, salvo en un problem+json, que sigue «Errores». En el punto 3 del [ADR-0186](0186-lo-que-no-es-interfaz-va-en-services-y-un-servicio-externo-tiene-su-modulo-en-api.md), el problem+json del servidor propio queda fuera.
3. Una fecha sin hora viaja como `full-date` de RFC 3339, y una zona horaria, con su nombre IANA.
4. De DTCG, `brand/tokens/` sigue *Name and value*, *Description*, *Type*, *Group Structure* y *Curly Brace Syntax* del formato; *Format* y *sRGB* del módulo de color, salvo un `alpha` menor que 1 y `none`; y *Root level properties* y *Reference objects* del resolver, salvo que un modificador puede tener un solo contexto, que los tokens no van en línea y que un `$ref` solo apunta a un set, a un modificador desde `resolutionOrder` o a un `.tokens.json` entero, sin otras claves. *Chained References* y *Circular References* salen: un rol apunta directo a un color de `palette`. *Input validation*, *Ordering* y *Aliases* salen: son el algoritmo del resolvedor. Que un tema cambie la paleta y un modo asigne los roles pasa a ser propia: su origen, Resolver §2.1, no es normativo.
5. `tokens.py` falla con un `$description`, un `name`, un `description` o un `default` que no es una cadena, y acepta un alias sin `$type`.
6. Las pruebas del servidor prueban U+FDD0 y el código de estado de la página de cada tipo de problema. «Cumplimiento» agrega las variables `RELEASE_` y los roles y custom colors que hace cumplir `tokens.py`.
7. Un tipo `about:blank` lleva su origen, RFC 9457 §4 y §4.2.1, y la página de un tipo propio explica cómo resolverlo. El servidor rechaza un mensaje que no es I-JSON.
8. Una app de iOS se publica en la App Store, sin más: el certificado y el perfil son la única forma de llegar a App Store Connect. `use-auth-secret` pasa a `despliegue.md`; «cada cliente las dibuja con MapLibre» sale, porque lo fija `stack.md`, y que Flet no muestra mapas pasa a `flet.md`. La atribución de MapLibre, la credencial vencida de coturn, macOS 15 y el APK universal enlazan el documento que lo prueba.

## Consecuencias

- Cada repositorio con `brand/tokens/` copia el `tokens.py` nuevo: `verificar.py` compara la copia.
- El modelo de problem+json que genera cada cliente tiene que ignorar una extensión desconocida, y `openapi.json` declara `additionalProperties: false` en `Problem`: queda en [pendientes/problem-json-en-los-modelos-generados.md](../pendientes/problem-json-en-los-modelos-generados.md). El valor de `type` de WebSocket queda en [pendientes/tipo-de-los-mensajes-de-websocket.md](../pendientes/tipo-de-los-mensajes-de-websocket.md).

## Descartado

- **Declarar como endurecimientos los criterios de WCAG recortados:** ninguno tenía una razón; el recorte salió de resumir el criterio.
- **Que el cliente falle también ante una extensión desconocida de un problem+json:** se apartaría de RFC 9457 §3.2 sin un síntoma que lo pida.
- **Rechazar en `tokens.py` un alias sin `$type`:** DTCG lo tipa con el token al que apunta, y un rol solo apunta a un color.
