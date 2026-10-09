# ADR-0040 · `~/.claude/CLAUDE.md` guarda solo lo que es para Claude, y enlaza canone para el método

- **Estado:** Aceptada
- **Fecha:** 2026-10-08
- **Alcance:** `~/.claude/CLAUDE.md` y [`principios.md`](../principios.md)

## Contexto

El punto 4 del [ADR-0001](0001-el-estandar-vive-en-un-repositorio.md) reducía `~/.claude/CLAUDE.md`
a un puntero a `principios.md`. Hoy además guarda el idioma de las respuestas, cómo reportar y las
trampas verificadas de las herramientas.

## Decisión

Reemplaza el punto 4 del ADR-0001.

1. `~/.claude/CLAUDE.md` enlaza `principios.md` y `documentacion.md`, y no repite sus reglas.
2. Guarda solo lo que es para Claude: el idioma de las respuestas, cómo reportar y las trampas
   verificadas.

## Consecuencias

- Las reglas de método siguen en un solo lugar, `canone`.

## Descartado

- **Solo un puntero** (el punto 4 del ADR-0001): el idioma y cómo reportar son para Claude, no para
  quien lee `canone`.
