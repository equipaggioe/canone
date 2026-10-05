# ADR-0028 · Una página está completa cuando sus estándares cubren lo que hay que decidir

- **Estado:** Aceptada. El punto 1 lo reemplaza el [ADR-0031](0031-una-revision-empieza-por-lo-que-la-tecnologia-obliga-a-decidir.md)
- **Fecha:** 2026-10-03
- **Alcance:** `plataformas/` y la configuración de herramientas de `plantilla/` que hace cumplir
  cada página

## Contexto

El [ADR-0018](0018-una-pagina-se-revisa-contra-la-copia-de-sus-estandares-y-solo-dice-lo-que-elige-endurece-o-no-cubren.md)
dice qué escribe una página sobre sus estándares, pero no cuándo le faltan estándares ni qué pasa
con uno que la página contradice en parte. Al revisar `python.md` aparecieron tres errores que
salieron de ahí:

- Se propuso quitar *Tool recommendations* porque la página lo contradice al elegir uv en vez de
  pip. Quitarlo también descartaba lo que sí se sigue, como no invocar `setup.py`.
- La revisión buscó qué estándar «usaba» cada punto, en vez de preguntar si los estándares
  cubrían lo que un proyecto Python tiene que decidir. Así quedaron fuera la codificación de los
  archivos de texto y las advertencias de seguridad de la biblioteca estándar.
- Para hacer cumplir *Security Considerations* se activaron reglas de ruff como `S311`, que marca
  todo uso de `random` aunque el estándar solo lo desaconseja para seguridad. Un reintento con
  *jitter* tendría que pedir un `# noqa`.

## Decisión

1. Una página está completa cuando sus estándares cubren todo lo que la tecnología obliga a
   decidir. Lo que ninguno cubre es una regla propia.
2. Contradecir una parte de un estándar no lo quita: el resto sigue rigiendo.
3. Una herramienta que marca más de lo que la regla dice impone una regla no escrita, y no va.

## Consecuencias

- Una revisión empieza por la lista de lo que hay que decidir, no por los puntos que ya tiene la
  página.
- Una parte de un estándar puede quedar sin herramienta que la revise, como la de `random` en
  *Security Considerations*. Sigue vigente igual.

## Descartado

- **Escribir como regla lo que la herramienta marca de más:** «no se usa `random`» no elimina
  ningún síntoma.
- **Quitar el estándar que se contradice y escribir lo que se sigue de él:** el estándar y su
  resumen serían dos fuentes de verdad.
