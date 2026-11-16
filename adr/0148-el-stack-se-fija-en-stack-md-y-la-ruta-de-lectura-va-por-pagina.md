# ADR-0148 · El stack se fija en `stack.md`, la ruta de lectura va por página, y una fuente es la guía de un asunto

- **Estado:** Aceptada. Los puntos 1 a 9 los confirmó el usuario al pedirlos, y los puntos 10 a 13,
  que se eligieron al implementar, al pedir que se aplicara la recomendación de confirmarlos
  (2026-11-14)
- **Fecha:** 2026-11-14
- **Alcance:** [`stack.md`](../stack.md), [`README.md`](../README.md),
  [`plataformas/README.md`](../plataformas/README.md), «Proyecto» y «Cumplimiento» de las páginas de
  `plataformas/`, [`principios.md`](../principios.md), [`repositorio.md`](../repositorio.md) y
  `scripts/verificar.py`

## Contexto

Canone se escribe para que un asistente de IA sepa con qué y cómo se construye cada producto sin
que el desarrollador se lo explique en cada sesión. Una revisión de los README contra ese fin
encontró esto:

- **El stack no tenía un lugar.** Unas 150 versiones estaban repartidas en diez secciones
  «Proyecto» y en `repositorio.md`. La elección de un paquete aparecía de cinco formas: una lista
  con versión, una convención propia, una convención adoptada, un descarte escrito solo en
  `verificar.py` y un ADR en propuesta.
- **La ruta de lectura dependía de enlaces sección por sección.** `sveltekit.md` enlazaba 7 de las
  17 secciones de `transversal.md` y 1 de las 9 de `autenticacion.md`, y no «Sesión», que fija la
  cookie de la web. Otras 45 secciones de las páginas contenían solo el enlace a su contrato.
- **La fuerza de una convención estaba dicha de cuatro formas**, entre «guía, no reglamento» y «una
  regla que no rompe CI es una sugerencia».
- **El objetivo de las fuentes no estaba escrito.** La misma revisión leyó «Cubre», «Aporta» y la
  fuente única por asunto como reglas sobre cada convención, y propuso quitarlas.

Comprobado: `scripts/verificar.py --canone` da 0 incumplimientos antes y después del cambio.
Después del cambio, los 2178 enlaces relativos de `README.md`, `stack.md`, `principios.md`,
`repositorio.md`, `documentacion.md`, `plataformas/`, `pendientes/` y los README de `plantilla/`,
`fuentes/` y `adr/` resuelven, con su ancla.

## Decisión

1. **`stack.md` fija qué se usa en cada plataforma y en qué versión, y es el único lugar.** Las
   páginas escriben cómo se usa: «Proyecto» conserva cómo se declara cada cosa y la estructura, sin
   lista de versiones.
2. **El stack lo decide el desarrollador.** Lo que una pieza necesita y no está en `stack.md` no se
   elige por cuenta propia: se presentan las opciones con una recomendación.
3. **`stack.md` no lleva razones**: la razón de una elección va en su ADR. La plataforma de cada
   pieza la sigue eligiendo cada repositorio.
4. **El bloque de una página en desarrollo lleva su misma nota**, y no se aplica mientras la tenga.
5. **Para trabajar en una pieza se leen enteras su página y las que nombra «Se lee con»** en la
   tabla «Páginas» de `plataformas/README.md`. Salen las secciones que solo enlazaban un contrato,
   y una sección de `transversal.md` o de `autenticacion.md` que no obliga a todas las piezas dice a
   cuáles.
6. **Una fuente es la guía de un asunto, para que siga un mismo enfoque.** Se prefieren pocas
   fuentes que cubran muchos asuntos, no se busca una para cada convención, y una convención no
   necesita una fuente que la justifique: el origen registra de dónde salió. «Cubre», «Aporta» y la
   fuente única por asunto se quedan, porque son las reglas que lo cumplen.
7. **Una página se escribe desde las decisiones que hay que tomar**, con sus fuentes como guía.
8. **La fuerza se dice una sola vez, en `README.md`:** lo que Canone escribe rige, una herramienta
   lo comprueba cuando puede, y apartarse requiere un ADR del repositorio.
9. **`README.md` declara que el lector es un asistente de IA**, y que el desarrollador revisa ahí
   lo que el asistente va a leer.
10. «Se lee con» nombra las páginas cuyas convenciones cumple el código de la pieza:
    la página madre, `postgres.md` en el servidor, `transversal.md` y `autenticacion.md`. No nombra
    `despliegue.md`, que rige la máquina y no el código de una pieza.
11. `stack.md` lleva su tabla «Cumplimiento», con las filas de versiones que estaban
    en las páginas, y los mensajes de `verificar.py` sobre una versión nombran `stack.md`.
12. El bloque «CI» de `stack.md` nombra también el contenedor `valkey/valkey`, que la
    plantilla usa y `verificar.py` ya comprobaba.
13. Sale también «Autenticación» de `fastapi.md`, que solo decía «Rige
    `autenticacion.md`».

Reemplaza los puntos 1 y 5 del [ADR-0118](0118-cada-pagina-fija-la-version-de-sus-tecnologias-y-la-plantilla-y-las-fuentes-la-siguen.md),
y su punto 6 en «la versión que fija la página»; y el punto 2 del
[ADR-0114](0114-lo-que-cumplen-juntas-varias-piezas-va-en-transversal-y-lo-demas-en-la-pagina-de-su-tecnologia.md),
en que la sección de cada pieza enlaza su contrato.

## Consecuencias

- El desarrollador ve todo su stack en un archivo, y un asistente sabe qué usar antes de abrir una
  página.
- Subir una versión toca `stack.md`, el diccionario de `verificar.py` y la plantilla: `verificar.py`
  sigue repitiendo las versiones.
- Una excepción de versión conserva su línea, con su razón, en «Proyecto» de su página, como la
  Pydantic de Flet, y esa línea repite el número de `stack.md`.
- Una sección de `transversal.md` o de `autenticacion.md` rige por lo que dice, y no por quién la
  enlaza. «Archivos» y «Llamadas de voz y video», que ninguna página de cliente enlazaba, rigen en el
  cliente que sube un archivo o hace una llamada.
- Los ADR [0048](0048-una-app-flutter-usa-riverpod-go-router-dio-y-freezed.md) y
  [0049](0049-la-ubicacion-en-segundo-plano-de-una-app-flutter-usa-geolocator-y-native-geofence.md)
  siguen en propuesta: `stack.md` se escribió con lo que decían las páginas.
- Queda sin hacer la revisión de las convenciones con origen contra el criterio de entrada del
  [ADR-0145](0145-una-convencion-entra-por-lo-que-empeora-sin-ella.md).

## Descartado

- **Una columna con la razón de cada elección en `stack.md`:** la razón va en el ADR, y la página
  tiene que leerse fácil.
- **Escribir en `stack.md` cuándo elegir una plataforma sobre otra:** la elige cada repositorio.
- **Quitar «Cubre», «Aporta» y la fuente única por asunto:** no filtran qué convención se escribe,
  pero mantienen pocas fuentes y un solo enfoque, que es para lo que están.
- **Enlazar como origen la URL de un documento del que salen una o dos convenciones:** invita a
  buscarle una fuente a cada convención.
- **Seguir con la ruta por enlaces de sección:** un enlace que falta deja sin efecto una sección
  entera, y nada lo avisa.
- **Separar `plataformas/README.md` en dos documentos, uno para escribir código y otro para escribir
  páginas:** el lector es el mismo, y la ruta ya está al principio.
