# Principios

Reglas de método. Valen en cualquier repositorio y no dependen del stack: lo que depende de una
tecnología está en [`plataformas/`](plataformas/), y solo aplica a los repositorios que la usan.

Este archivo es la fuente. `~/.claude/CLAUDE.md` no las repite: apunta aquí.

## Idioma

- **El código se escribe en inglés**: variables, funciones, clases, tablas, columnas, endpoints,
  enums y comentarios.
- **Los mensajes de commit se escriben en español.**
- **La documentación se escribe en español.** La UI se diseña multilingüe, con el español como
  idioma base ([transversal.md](plataformas/transversal.md#idiomas)).
- **Español neutro.** Ni rioplatense ni de España.
  - Sin voseo: `vos`, `sos`, `tenés`, `podés`, `querés`, `sabés`, `hacés`. Se usa `tú tienes`,
    `eres`, `puedes`, `quieres`, `sabes`, `haces`.
  - Sin imperativos voseantes: `mirá`, `probá`, `fijate`, `elegí`, `ingresá`, `revisá`, `dale`. Se
    usa `mira`, `prueba`, `fíjate`, `elige`, `ingresa`, `revisa`.
  - Sin `che`, `boludo`, `laburo`, `quilombo`, `plata` por dinero, `acá` (se usa `aquí`),
    `bárbaro`, `joya` ni `celu`.
  - Sin `vosotros` ni `vale`.

## Nombres

- Un nombre lleva las menos palabras posibles, y nunca más de cuatro. No repite lo que ya dicen su
  carpeta, su módulo o su clase: en `routers/stop_requests.py` es `list_mine`, no
  `list_my_stop_requests`.
- Sin abreviaturas, salvo las que son más comunes que la palabra entera, como `id`, `url` o `http`.
- Quedan fuera del límite:
  - Las pruebas: su nombre describe el caso.
  - Los nombres que no se eligen: los métodos que se sobrescriben del framework, como
    `didChangeDependencies`; los campos de una API externa, y los que genera una convención, como
    las restricciones que nombra Alembic.
  - El sufijo que distingue los esquemas de un mismo recurso, como `Create` o `Update`: no cuenta
    como palabra.
- [`scripts/verificar.py`](scripts/verificar.py) revisa las funciones, los métodos y las clases.

## Sin fallbacks

Nada de valores por defecto silenciosos, handlers vacíos ni degradados silenciosos, en ningún
repositorio. Ocultan errores: si un valor puede venir de dos sitios, no se sabe de cuál vino. **Que
falle ruidosamente y en el momento.**

## Compatibilidad

Depende del estado que el repositorio declara en su `README.md`
([repositorio.md](repositorio.md#archivos-del-raíz)). Si no lo declara, no se supone ninguno: se
pregunta.

Las migraciones normales de esquema van en los dos estados: no son compatibilidad, son la única
forma de abrir una base existente.

### En desarrollo

No hay usuarios reales ni datos que salvar. Nada de retrocompatibilidad, alias ni ramas
`if version <`, y **nunca se propone migrar datos ni conservar un formato "por lo que haya en
camino"**.

- Al mover, renombrar o cambiar de formato: cambio limpio, borrando la fuente vieja en vez de
  leerla. Si se pierden datos, se dice y se arreglan a mano una vez.
- **Cambio de formato = borrar los datos viejos.** Una pasada para reconvertir archivos ya
  guardados cuenta como sostener el formato viejo.
- **Ninguna pieza sostiene la versión anterior de otra.** El servidor no conserva rutas, campos ni
  formatos viejos para que un cliente sin actualizar siga funcionando, y un cliente no conserva
  código para un servidor viejo. Tampoco se justifica una decisión con "despliegue escalonado" ni
  "cliente viejo": si una operación es distinta de otra, se explica por qué lo es en sí misma.

### En producción

La compatibilidad y la migración de datos no se agregan por cuenta propia ni sin avisar: se
proponen con su costo, y decide el desarrollador.

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

1. **Un cambio va en todas las apps**, y se pasa a las demás cuando el usuario lo indica.
2. **Si el trabajo dice «aplico el patrón X», ¿está el patrón completo?** Se lee X entero y se
   enumeran sus piezas. Un campo declarado «por adelantado para la fase X» no está entregado hasta
   que tiene consumidores.
3. **¿Quedó código que no llama nadie?** Nada «por simetría».
4. **¿Se recorrieron todas las puertas de entrada?** Se prueban todos los caminos que llegan a la
   pantalla o la función, no solo el que se tocó.
5. **¿La prueba que falla ya fallaba antes?** Se corre sobre el commit anterior (`git worktree`)
   antes de culpar al cambio.

Si alguna falla, se arregla o se dice explícitamente que quedó fuera y por qué. **Nunca se reporta
«terminado» con parte del alcance faltante.**
