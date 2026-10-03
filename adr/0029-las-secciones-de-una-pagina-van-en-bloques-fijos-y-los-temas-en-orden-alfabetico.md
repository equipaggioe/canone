# ADR-0029 · Las secciones de una página van en bloques fijos, y los temas en orden alfabético

- **Estado:** Aceptada
- **Fecha:** 2026-10-03
- **Alcance:** `plataformas/`

## Contexto

Cada página ordenaba sus secciones a su manera. Quien leía dos páginas a la vez, como `python.md`
y `qt.md`, no encontraba el mismo tema en el mismo lugar:

- La sección del proyecto se llamaba `Proyecto`, `Layout` o `Estructura`.
- Un mismo título nombraba cosas distintas: `Estilo` era el estilo de código en `python.md` y la
  hoja de estilo en `qt.md`; `Dependencias` eran los paquetes en `python.md` y `Depends` en
  `fastapi.md`, que hereda de ella.
- `Red` iba después de `Tema` en `flet.md` y después de `Accesibilidad` en `qt.md`.
- La columna «Cubre» del README repetía las secciones de cada página y ya no coincidía con ellas.

## Decisión

1. Las secciones van en siete bloques, en este orden: Proyecto, Código, Arquitectura, Temas,
   Pruebas, Entrega y Cómo se hace cumplir.
2. Los temas van en orden alfabético del título.
3. Un título nombra lo mismo en todas las páginas.
4. La tabla del README describe cada página en una frase y no lista sus secciones.

## Consecuencias

- Dos temas que comparten dos páginas quedan en el mismo orden en ambas, sin una lista que
  mantener.
- Un tema nuevo tiene su lugar por su título.
- Renombrar un tema lo mueve de lugar.
- Los temas afines quedan separados: en `fastapi.md`, `Autenticación`, `Contraseñas`,
  `Segundo factor` y `Tokens`; en los clientes, `Tema`, `Idiomas` y `Accesibilidad`.
- En Código y Arquitectura el orden no es alfabético: una sección va después de las que necesita
  para leerse.

## Descartado

- **Los temas en el orden de `transversal.md`, y los propios al final:** son dos reglas, y la
  primera es ambigua, porque `fastapi.md` no tiene una sección `Sesión`, sino `Autenticación`,
  `Tokens` y `Segundo factor`. Tampoco mantiene juntos los afines de `fastapi.md`.
- **Lo mismo, con los propios en orden alfabético:** la misma ambigüedad, y los afines igual de
  separados.
- **Una lista en el README con todos los temas en orden:** unos 50 nombres que hay que actualizar
  con cada tema nuevo.
- **Que cada página elija su orden:** es lo que había.
