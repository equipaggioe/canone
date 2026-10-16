# ADR-0001 · El estándar vive en un repositorio y los demás lo enlazan

- **Estado:** Aceptada. La última frase del punto 2 la reemplazan el
  [ADR-0014](0014-una-pagina-se-escribe-desde-la-recomendacion-oficial.md), en «se escribe leyendo
  ese código», y el [ADR-0057](0057-una-pagina-no-espera-a-que-un-repositorio-use-la-tecnologia.md),
  en «Una página existe porque la tecnología ya está en uso»; el punto 4, el
  [ADR-0040](0040-el-claude-md-global-guarda-solo-lo-que-es-para-claude.md)
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

1. `canone` contiene los principios de método, la convención de `docs/`, lo mínimo del repositorio
   y **una página por plataforma**. Es la única copia.
2. **`canone` no obliga a ningún repositorio a adoptar una tecnología.** Cada producto elige sus
   piezas; la página de una plataforma solo aplica a quien la usa. Una página existe porque la
   tecnología ya está en uso, y se escribe leyendo ese código.
3. El `docs/README.md` de un repositorio no repite la convención: la enlaza.
4. `~/.claude/CLAUDE.md` queda reducido a un puntero a `canone/principios.md`. Las reglas de método
   no se mantienen en dos lugares.
5. Un repositorio que necesita apartarse de una regla abre un ADR propio que declare la desviación
   y el motivo, y lo enlaza desde su `docs/arquitectura/`.
6. Si una desviación resulta mejor que la regla, se promueve a `canone` y el ADR del repositorio
   pasa a «Reemplazada».

## Consecuencias

- Hay un lugar donde mirar antes de decidir, y un lugar donde escribir después de decidir.
- La pregunta que responde `canone` es «si uso X, ¿cómo lo uso?», no «qué debe tener todo repositorio».
- `canone` se vuelve una dependencia de lectura de todos los repositorios. Si se queda viejo, se
  queda viejo para todos a la vez, que es preferible a seis versiones que nadie compara.
- Obliga a tocar dos repositorios cuando una decisión de uno generaliza.

## Descartado

- **Una carpeta compartida sin repositorio propio:** no tiene historia ni permite un ADR que
  explique por qué una regla cambió.
- **Dejar cada repositorio con su copia y sincronizar a mano:** es exactamente lo que produjo las
  seis copias divergentes de `models/base.py`.
- **Fijar un stack único obligatorio para todos los repositorios:** haría que un producto sin web
  tuviera que justificar por qué no tiene web, y que la página de una tecnología se escribiera antes
  de que existiera el código que la usa.
