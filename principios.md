# Principios

Reglas de método. Valen en cualquier repositorio y no dependen del stack: lo que depende de una
tecnología está en [`plataformas/`](plataformas/), y solo aplica a los repositorios que la usan.

Este archivo es la fuente. `~/.claude/CLAUDE.md` no las repite: apunta aquí.

## Idioma

- **El código se escribe en inglés**: variables, funciones, clases, tablas, columnas, endpoints,
  enums, comentarios y mensajes de commit.
- **La UI y la documentación se escriben en español**, salvo que el proyecto sea explícitamente
  multilingüe.
- **Español neutro.** Ni rioplatense ni de España. Nada de voseo (`vos`, `tenés`, `mirá`), nada de
  `vosotros` ni `vale`, nada de `acá`, `plata`, `laburo`, `che`.

## Ningún repositorio está en producción

No hay usuarios reales, ni datos que salvar, ni clientes con versiones viejas: todas las piezas se
despliegan juntas. El repositorio que sí llegue a producción lo dirá en su
`docs/arquitectura/00_sistema.md`; mientras no lo diga, no lo está.

Consecuencia directa: **nunca se propone migrar datos ni conservar un formato "por lo que haya en
camino"**.

## Sin fallbacks ni capas de compatibilidad

Nada de retrocompatibilidad, valores por defecto silenciosos, alias, handlers vacíos, ramas
`if version <` ni degradados silenciosos. Ocultan errores: si un valor puede venir de dos sitios,
no se sabe de cuál vino. **Que falle ruidosamente y en el momento.**

- Al mover, renombrar o cambiar de formato: cambio limpio, borrando la fuente vieja en vez de
  leerla. Si se pierden datos, se dice y se arreglan a mano una vez.
- **Cambio de formato = borrar los datos viejos.** Una pasada para reconvertir archivos ya
  guardados cuenta como sostener el formato viejo.
- Las migraciones normales de esquema sí van: no son un fallback, son la única forma de abrir una
  base existente.
- No se justifica una decisión con "despliegue escalonado" ni "cliente viejo". Si una operación es
  distinta de otra, se explica por qué lo es en sí misma.

## Reestructurar, no parchar

Ante una pregunta de diseño («¿no sería mejor…?», «¿qué mecanismo usamos para casos así?») se mide
primero el alcance real en todo el repositorio —contando los casos con un script, distinguiendo
causas de síntomas— y recién entonces se propone la reestructuración que cubre todos los casos, no
el arreglo del caso que disparó la conversación.

Deshacer trabajo ya hecho es aceptable si el rediseño lo pide. Se presentan opciones con sus costos
y una recomendación, no una sola salida.

## No endurecer de más

En un arreglo de bug se cambia **solo** lo que el bug exige. Nada de flags, endurecimientos ni
optimizaciones defensivas «de paso»: una opción agregada por cuenta propia puede romper justo el
camino que funcionaba. Si algo no es estrictamente el arreglo, se pregunta o se deja fuera.

## Elegir la mejor mejora, no la más barata

El tamaño del diff no decide la ingeniería. Se evalúa por corrección y por si elimina la clase de
problema. «El tráfico es chico» o «no hay síntoma reportado» deciden la urgencia, nunca si hay que
arreglarlo.

Matiz: no se empaqueta una migración de gran radio junto a un arreglo que hay que verificar en
campo. Eso es separar lo verificable, no elegir lo barato.

## Poder nombrar el síntoma

Si al implementar no se puede nombrar el síntoma concreto que el cambio elimina, el cambio no va
todavía. Optimizar una escala que no existe es sobre-ingeniería aunque el código sea correcto.

## Antes de cerrar un paso

1. **¿Se entregó en todos los clientes?** Si el proyecto tiene varios (app, panel, backoffice),
   se porta a todos.
2. **Si el trabajo dice «aplico el patrón X», ¿está el patrón completo?** Se lee X entero y se
   enumeran sus piezas. Un campo declarado «por adelantado para la fase X» no está entregado hasta
   que tiene consumidores.
3. **¿El tipo de fila o entidad nueva se comporta como su hermana ante el borrado?** Se prueban
   los caminos de purgado y borrado.
4. **¿Quedó código que no llama nadie?** Nada «por simetría».
5. **¿Se recorrieron todas las puertas de entrada?** Se prueban todos los caminos que llegan a la
   pantalla o la función, no solo el que se tocó.

Si alguna falla, se arregla o se dice explícitamente que quedó fuera y por qué. **Nunca se reporta
«terminado» con parte del alcance faltante.**

## Trampas verificadas

Comprobadas contra el código o reproducidas. Cada una vive en la página de su plataforma, junto al
código que la sufre:

| Plataforma | Trampas |
|---|---|
| [mapas.md](plataformas/mapas.md) | `flutter_map`: la rueda del mouse, el arrastre de una capa encima, las teselas que relanzan fallos de red |
| [sveltekit.md](plataformas/sveltekit.md) | UnoCSS: los atajos con prefijo de variante y los archivos `.ts` sin escanear |
| [postgres.md](plataformas/postgres.md) | `Geography` compartido en un `Annotated`; `native_enum=False` sin `create_constraint` |
