# ADR-0008 · Un solo cliente nativo

- **Estado:** Propuesta — **decisión abierta, sin opción elegida**
- **Fecha:** 2026-09-22
- **Alcance:** navetta, presenze, vettore, banditore, concordia, cadenza

## Contexto

Hay tres tecnologías distintas resolviendo «una aplicación que no es el navegador»:

| Tecnología | Dónde | Qué es |
|---|---|---|
| Flutter | navetta (`mobile-driver`, `mobile-passenger`, `mobile-shared`), vettore (`app`) | App móvil publicable, con mapas, cámara, push y ejecución en segundo plano |
| Flet | presenze (`app`, `terminal`), banditore (`customer`, `vendor`), cadenza (`frontend`) | UI en Python sobre Flutter, sin salir del lenguaje del servidor |
| PWA con SvelteKit | concordia (`pwa`) | El mismo stack que las otras superficies web, instalable |

Cada una arrastra su propio modelo de estado, su propia forma de hablar con la API, su propio
empaquetado y su propio conjunto de trampas. Las tres trampas de `flutter_map` que ya están
verificadas valen para dos de las tres.

`presenze/terminal` puede ser un caso distinto del resto: es una pieza de hardware fija, no un
teléfono.

## Decisión

Sin decidir. Las opciones, con su costo:

| Opción | A favor | En contra |
|---|---|---|
| **Flutter para todo lo nativo** | Es lo que está en las apps que se publican; mapas, push y segundo plano ya están resueltos; Flet corre encima de Flutter igual | Dart es un segundo lenguaje; hay que reescribir las tres piezas Flet |
| **Flet para todo lo nativo** | Un solo lenguaje con el servidor; las piezas internas se escriben rápido | Ecosistema mucho más chico; lo que Flet no expone hay que resolverlo en Dart igual; publicar en tiendas es menos transitado |
| **PWA donde se pueda, Flutter donde no** | Reutiliza el stack web que ya está en los seis repositorios y una sola forma de hablar con la API | Push limitado en iOS; sin segundo plano ni acceso pleno al hardware. No sirve para navetta ni vettore |

**Recomendación:** la tercera. **PWA con SvelteKit como forma por defecto, y Flutter solo cuando el
producto necesite algo que el navegador no da** —push confiable en iOS, segundo plano, hardware—,
que hoy es navetta y vettore. Flet se retira: no aporta nada que Flutter o la PWA no cubran, y es
una tercera forma de hacer lo mismo.

Antes de decidir hay que verificar dos cosas que no se comprobaron: qué hace exactamente
`presenze/terminal` con el hardware, y si `banditore/customer` y `banditore/vendor` se publican en
tiendas o son internas.

## Consecuencias

Las de la opción que se elija se escriben aquí cuando se elija.
