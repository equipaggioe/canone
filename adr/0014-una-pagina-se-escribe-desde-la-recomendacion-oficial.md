# ADR-0014 · Una página de plataforma se escribe desde la recomendación oficial, no desde el código

- **Estado:** Reemplazada por [ADR-0016](0016-una-pagina-es-un-catalogo-de-convenciones-que-sale-de-la-recomendacion-oficial.md)
- **Fecha:** 2026-09-24
- **Alcance:** `plataformas/`

## Contexto

Reemplaza la última frase del punto 2 del [ADR-0001](0001-el-estandar-vive-en-un-repositorio.md):
«se escribe leyendo ese código».

Escrita así, `qt.md` tomó como norma lo que hacían `consola`, `presenze` y `spazio`, errores
incluidos. No pedía el estilo `Fusion`, y con el estilo nativo de Windows (`windowsvista`) un botón
ignora el color que le da la paleta: comprobado con PySide6 6.11. Además permitía `setStyleSheet` en
cada widget, que el tutorial de estilos de Qt for Python desaconseja frente a una hoja global.

## Decisión

1. Una página de plataforma se escribe desde la documentación oficial más reciente de la
   tecnología.
2. Donde no hay recomendación oficial, se escribe desde la mejor práctica establecida.
3. El código de los repositorios no es fuente. Si un repositorio hace algo distinto, la diferencia
   va a [homologacion.md](../homologacion.md), no a la página.
4. *(propuesta)* Cada sección de una página nombra el estándar del que sale, como `python.md` con
   sus PEP.

## Consecuencias

- Las páginas escritas leyendo código hay que revisarlas contra la documentación oficial de su
  tecnología. `qt.md` ya está revisada.
- Una página puede exigir algo que ningún repositorio cumple hoy. Eso no es un defecto de la página.

## Descartado

- **Escribir la página leyendo el código que estrenó la tecnología (ADR-0001):** convierte en norma
  los errores de ese código.
