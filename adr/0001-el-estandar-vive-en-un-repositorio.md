# ADR-0001 · El estándar vive en un repositorio y los demás lo enlazan

- **Estado:** Propuesta
- **Fecha:** 2026-09-22
- **Alcance:** todos los repositorios

## Contexto

Cada repositorio tiene su `docs/`, y el `docs/README.md` de `consola` dice explícitamente que «este
archivo se puede copiar tal cual a otro repositorio». Se copió: hay seis copias de la convención de
documentación y seis de `models/base.py`. Estas últimas ya tienen cinco contenidos distintos, y dos
de las diferencias son defectos reales (ADR-0003 y ADR-0004).

Una regla copiada en dos sitios son dos fuentes de verdad, y la copia se queda vieja. Es la misma
regla que el propio `docs/README.md` enuncia y que la práctica de copiarlo incumple.

## Decisión

1. `canone` contiene los principios, el stack, las convenciones y los ADR transversales. Es la
   única copia.
2. El `docs/README.md` de un repositorio no repite la convención: la enlaza.
3. `~/.claude/CLAUDE.md` queda reducido a un puntero a `canone/principios.md`. Las reglas de método
   no se mantienen en dos lugares.
4. Un repositorio que necesita apartarse de una regla abre un ADR propio que declare la desviación
   y el motivo, y lo enlaza desde su `docs/arquitectura/`.
5. Si una desviación resulta mejor que la regla, se promueve a `canone` y el ADR del repositorio
   pasa a «Reemplazada».

## Consecuencias

- Hay un lugar donde mirar antes de decidir, y un lugar donde escribir después de decidir.
- `canone` se vuelve una dependencia de lectura de todos los repositorios. Si se queda viejo, se
  queda viejo para todos a la vez, que es preferible a seis versiones que nadie compara.
- Obliga a tocar dos repositorios cuando una decisión de uno generaliza.

## Descartado

- **Una carpeta compartida sin repositorio propio:** no tiene historia ni permite un ADR que
  explique por qué una regla cambió.
- **Dejar cada repositorio con su copia y sincronizar a mano:** es exactamente lo que produjo las
  seis copias divergentes de `models/base.py`.
