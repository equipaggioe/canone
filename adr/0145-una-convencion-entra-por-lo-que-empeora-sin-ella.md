# ADR-0145 · Una convención entra por lo que empeora sin ella, y una revisión la rehace desde la causa

- **Estado:** Aceptada. El [ADR-0162](0162-una-pagina-escribe-decisiones-y-no-como-funciona-su-tecnologia.md) agrega una condición al punto 1
- **Fecha:** 2026-11-14
- **Alcance:** [`plataformas/README.md`](../plataformas/README.md), «Función de las páginas»,
  «Qué no se escribe», «Revisión» y «Cumplimiento»

## Contexto

Una convención entraba si contribuía a la uniformidad, a las decisiones comunes o a los contratos
entre piezas. Casi cualquier regla pasaba ese filtro, y una revisión proponía fuentes y reglas para
completar el catálogo. La revisión evaluaba elemento por elemento, y eso llevaba a parchar lo que
estaba mal en vez de corregir su causa. Pedir una herramienta para toda convención verificable
llevaba a escribir chequeos que repetían lo que ya hace el build.

Un caso: que `@sveltejs/kit`, `svelte` y `vite` vayan en `devDependencies` no cambia el programa
con `adapter-static`. Comprobado con SvelteKit 3.1.1, `adapter-static` 4.0.1 y Vite 8.3.6: con esos
paquetes en `dependencies`, el build sale idéntico (`diff -r build`, con `version.name` fijo), y el
release copia solo `build/`.

## Decisión

1. **Una convención entra solo si se puede nombrar qué empeora sin ella**, aunque no haya pasado
   todavía: en la eficacia, la eficiencia, el uso o la estructura. En una regla de estilo se pregunta
   qué empeora si no hubiera regla. No la justifica que una fuente la establezca, que una
   herramienta pueda comprobarla ni que complete una lista.
2. «Qué no se escribe» remite a ese criterio.
3. **Una revisión llega a la página que se escribiría de cero**: lo que está mal se corrige en su
   causa, aunque cambie otras partes. Si la causa es un criterio del README, se propone cambiarlo.
   Una fuente o una convención nueva se propone solo con su efecto comprobado.
4. **Si romper una convención ya hace fallar un paso de CI, ese paso es su herramienta**, y no se
   agrega un chequeo aparte.

## Consecuencias

- Las convenciones adoptadas también pasan por el criterio. La de `devDependencies` de
  `sveltekit.md` queda para revisar con él.
- Una revisión puede cambiar varias partes de una página para corregir una sola causa.
- Una fila de «Cumplimiento» puede nombrar un paso de CI, como `svelte-check`, y hay que comprobar
  con un experimento que ese paso falla siempre que se rompe la convención.

## Descartado

- **Agregar «lo que no cambia el programa» como un caso más de «Qué no se escribe»:** repetía el
  criterio, que ya cubren dos casos de esa lista.
