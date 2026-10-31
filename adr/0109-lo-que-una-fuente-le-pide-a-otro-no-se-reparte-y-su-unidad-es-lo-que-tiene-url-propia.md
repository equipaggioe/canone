# ADR-0109 · Lo que una fuente le pide a otro no se reparte, y su unidad es lo que tiene URL propia

- **Estado:** Aceptada
- **Fecha:** 2026-10-30
- **Alcance:** `plataformas/` y `fuentes/`

## Contexto

El [ADR-0108](0108-una-fuente-se-cita-entera-o-por-entradas-y-cada-parte-rige-en-una-sola-seccion.md)
pide que cada parte de una fuente entera rija en una sola sección o se deje sin efecto. En una
especificación de protocolo, casi todo lo que se pide lo cumple quien programa la herramienta: el
RFC 9110 tiene 238 títulos y 329 frases normativas, el RFC 6455, 88 y 165, y el RFC 8656, 95 y 116.
Repartirlos obligaba a anotar cientos de partes que ninguna regla del producto puede cumplir.

La unidad era «el documento que se publica por separado», y en un manual dividido en capítulos no
se sabía cuál era. ASVS 5.0 se publica como un solo estándar y en un archivo por capítulo:
`fastapi.md` cita V3.3 y V3.5 de V3, y V3.4, que choca con el *HTTP Security Response Headers
Cheat Sheet* de `despliegue.md`, no lo cita nadie.

## Decisión

1. La unidad es lo que se publica en una URL propia, sin contar el fragmento: lo que guarda un
   archivo de `fuentes/`, como una cheat sheet, un capítulo de ASVS o un capítulo del manual de
   PostgreSQL. El manual entero no es una unidad. Reemplaza el punto 2 del ADR-0108.
2. Lo que una fuente le pide a otro no se reparte: a quien programa una herramienta que el producto
   usa, como coturn, Uvicorn o el navegador, o a la otra parte de un protocolo, como el servicio de
   push de Web Push. Tampoco cuenta como cubierto en «Cubre». Precisa los puntos 4, 5 y 7 del
   ADR-0108.
3. Sí se reparte cuando la herramienta deja elegirlo a quien la configura, como los destinos a los
   que coturn niega relevar.

## Consecuencias

- Un protocolo se cita entero, y se reparte solo lo que le pide al producto: al servidor de la app,
  a sus clientes y a quien despliega.
- Citar *WebAuthn Relying Party Operations* y no las operaciones del autenticador, como hace hoy
  `transversal.md`, deja de ser una cita por partes: es la regla.
- Saber a quién le habla cada parte pide leerla. La fuente suele nombrarlo, como «the server» o
  «the user agent».
- Cada capítulo de ASVS se reparte entero: V3.4 pasa a regir en una sección o a dejarse sin efecto.

## Descartado

- **Citar los protocolos por entradas:** un protocolo trae un enfoque, y citarlo por entradas
  dejaría callar lo que molesta de lo que le pide al producto.
- **Dejar fuera también lo que una fuente le pide a la organización**, como políticas,
  planificación o respuesta a incidentes: quien despliega es una parte del producto en canone, y
  dejarlo fuera volvería a callar lo que molesta.
- **Que la unidad sea lo que el organismo llama documento**, como ASVS entero o el manual de
  PostgreSQL: habría que repartir cientos de requisitos que ninguna página usa.
- **Que la unidad sea una sección con anclaje propio:** vuelve a citar partes sueltas.
