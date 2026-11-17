# ADR-0162 · Una página escribe decisiones, y no cómo funciona su tecnología

- **Estado:** Aceptada en los puntos 1 a 4, que el usuario pidió aplicar (2026-11-16). Los puntos 5
  y 6 son *(propuesta)*: se eligieron al implementar
- **Fecha:** 2026-11-16
- **Alcance:** [`plataformas/README.md`](../plataformas/README.md), «Función de las páginas»,
  «Selección de fuentes», «Adopción de fuentes» y «Revisión», y [`README.md`](../README.md)

## Contexto

Las páginas las escriben asistentes de IA, y transcriben como convenciones las instrucciones de uso
de una tecnología. Un caso: de las nueve convenciones que `qt.md` toma de *Model/View Programming*,
seis dicen cómo se usa la API, como llamar a `beginInsertRows()` antes de insertar filas, y tres
eligen entre formas que funcionan, como usar una vista con modelo y no `QListWidget`.

Leído en `plataformas/README.md`, sin experimento que lo confirme como causa:

- El criterio de entrada preguntaba solo qué empeora sin la convención. Un uso incorrecto de una API
  hace fallar el programa, así que pasaba.
- «Revisión» pedía que lo que la página no escribe de una fuente cayera en un caso de «Qué no se
  escribe». Escribir era lo normal, y dejar fuera, lo que había que justificar.
- El requisito «Normativa» se cumplía con que el documento dijera «se debe».

## Decisión

1. **Una convención entra solo si hay elección**: existe otra forma que también funciona. Lo que
   tiene una sola forma correcta es conocimiento de la tecnología y no se escribe.
2. **No escribir es lo normal.** De una fuente se escriben solo las posiciones que cumplen el
   criterio de entrada, y una revisión no evalúa lo que la página no escribe de ella.
3. **Un documento que explica cómo funciona o cómo se usa una tecnología no es fuente**, aunque sea
   oficial y diga «se debe».
4. **Lo que tiene una sola forma correcta se escribe solo si ya se hizo mal y está comprobado**,
   como convención propia.
5. *(propuesta)* Se queda la condición de poder nombrar qué empeora, como segunda condición. Una
   preferencia la cumple por la estructura: sin la convención, cada sesión o cada repositorio
   elegiría distinto.
6. *(propuesta)* `README.md` dice que Canone escribe decisiones y no cómo funciona una tecnología.

Agrega una condición al punto 1 del
[ADR-0145](0145-una-convencion-entra-por-lo-que-empeora-sin-ella.md), y quita de «Revisión» la
comprobación de lo que la página no escribe, que venía del
[ADR-0129](0129-la-pagina-escribe-cada-convencion-que-rige-y-la-adoptada-lleva-su-origen.md).

## Consecuencias

- Las páginas no se revisaron con el criterio nuevo: siguen teniendo convenciones que no lo cumplen.
  Al revisarlas, salen esas convenciones y las copias de `fuentes/` que queden sin ninguna.
- No está comprobado que un asistente acierte siempre en lo que deja de escribirse. El punto 4 lo
  cubre después del primer fallo, no antes.
- En seguridad casi toda regla elige entre formas que funcionan, así que casi todo se queda.

## Descartado

- **Quitar la condición de qué empeora:** filtra otra cosa, la elección que da lo mismo, como la del
  caso de `devDependencies` del ADR-0145.
