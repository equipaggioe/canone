# ADR-0181 · «Cubre» y «Aporta» cuentan juntas las páginas de una misma documentación

- **Estado:** Aceptada. El usuario pidió aplicar lo recomendado en la revisión de `flutter.md`
  (2026-11-18)
- **Fecha:** 2026-11-18
- **Alcance:** [`plataformas/README.md`](../plataformas/README.md), «Requisitos»

## Contexto

Al revisar `flutter.md`, seis páginas de la documentación de Riverpod 3.5.0 eran el origen de 1 o
2 convenciones cada una, y no cumplían «Aporta». Sin ellas, *DO/DON'T* quedaba como origen de 5
de las 15 convenciones de «Estado», y tampoco cumplía «Cubre»: el asunto se quedaba sin fuente,
aunque todas sus convenciones salen de la misma guía, partida en páginas. «Elección entre fuentes»
ya contaba juntos los documentos de un mismo publicador.

## Decisión

1. Para «Cubre» y «Aporta», los documentos de una misma documentación, la que publica quien
   define una tecnología para una de sus versiones, cuentan juntos. Cada documento sigue siendo
   una fuente aparte.

## Consecuencias

- En `flutter.md` se quedan las páginas de Riverpod y *Common architecture concepts*. Sale el
  README de shared_preferences, que es la documentación de otra tecnología y le quedan 2
  convenciones.
- Antes salieron por «Aporta» documentos que con esta cuenta se quedarían: Keystore en
  `android.md`, `large-lists.md` en `flet.md` y `threads.qdoc` en `qt.md`. Se vuelven a evaluar al
  revisar su página; no se hace un barrido.

## Descartado

- **Contar cada documento por separado:** deja sin fuente un asunto cuya guía se publica partida
  en páginas.
- **Contar juntos todos los documentos de un publicador:** todos los RFC del IETF o todos los
  *cheat sheets* de OWASP valdrían como uno, y un documento que aporta una sola regla suelta, sin
  un enfoque que seguir, volvería a ser fuente.
- **Partir «Estado» en asuntos más chicos para que *DO/DON'T* cumpla «Cubre»:** acomoda los
  asuntos al conteo en vez de a las decisiones.
