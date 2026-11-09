# ADR-0130 · `Estándar:` solo nombra los documentos de origen, y una elección lleva el origen de su regla

- **Estado:** Aceptada
- **Fecha:** 2026-11-09
- **Alcance:** `plataformas/`, `principios.md` y `scripts/verificar.py`

## Contexto

El [ADR-0129](0129-la-pagina-escribe-cada-convencion-que-rige-y-la-adoptada-lleva-su-origen.md)
sacó el párrafo `Estándar:`, porque repetía los orígenes. Ya no tiene que acotar lo que se adopta,
pero sigue sirviendo para ver de entrada de qué documentos sale una sección.

## Decisión

1. Una sección con convenciones adoptadas empieza por un párrafo `Estándar:` o `Estándares:` que
   nombra, con su enlace, los documentos que son su origen. Es informativo: no adopta nada, no
   nombra secciones y no lleva «salvo».
2. `verificar.py --canone` falla si el párrafo no nombra los mismos documentos que son origen de
   las convenciones de su sección. Un origen es un enlace a `fuentes/` que nombra su sección.
3. `principios.md` dice solo que al escribir código basta la página.
4. La convención que nombra una parte que hace cumplir una herramienta dice qué reglas de esa parte
   no sigue, con su razón: esas reglas no están escritas, y sin decirlo no se sabría que no rigen.
   Precisa el punto 4 del ADR-0129.
5. De una regla que da opciones se escribe solo la opción elegida, y de una que se endurece, solo
   su forma endurecida, con el origen de la regla. Cuentan para «Aporta»: la fuente decidió las
   opciones, y sin contarlas una referencia de opciones como `systemd.exec` nunca llegaría a tres.
   Precisa los puntos 2 y 6 del ADR-0129.

Reemplaza el punto 3 del ADR-0129 en lo que saca el párrafo `Estándar:`, y su descarte de
mantenerlo. Descarta el punto 9 del ADR-0129, que era propuesta: no hay régimen de transición.

## Consecuencias

- El párrafo repite los documentos de los orígenes, y `verificar.py` impide que se desfasen.
- Sin transición, lo que una página todavía no escribe no rige, aunque su párrafo `Estándar:`
  nombre partes. Hay que reescribir las páginas.
- `verificar.py` no compara las secciones sin orígenes, para no fallar en las páginas sin
  reescribir.

## Descartado

- **El párrafo con las secciones de cada documento:** repetiría cada origen, y volvería a parecer
  una cita que adopta.
