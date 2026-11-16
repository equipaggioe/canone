# ADR-0161 · Cada regla queda en una sola página, y `plugins/` deja de ser una carpeta de primer nivel

- **Estado:** Aceptada. El usuario confirmó los puntos al pedir que se aplicaran (2026-11-16); el
  punto 8 es *(propuesta)* en lo que quita `plugins` de `verificar.py`, que no estaba en la lista
- **Fecha:** 2026-11-16
- **Alcance:** [`stack.md`](../stack.md), [`repositorio.md`](../repositorio.md),
  [`documentacion.md`](../documentacion.md), [`plataformas/README.md`](../plataformas/README.md),
  [`plantilla/README.md`](../plantilla/README.md), las páginas de Python, Android, Flutter,
  SvelteKit, Qt y despliegue, y `scripts/verificar.py`

## Contexto

Una revisión de coherencia entre las páginas (2026-11-16) encontró reglas escritas en más de un
lugar, contra el principio del [README](../README.md#principios): una convención tiene una única
definición, y los demás documentos la referencian.

- «Todo paquete que se importa está declarado, y toda dependencia declarada se usa» estaba en
  `python.md`, `flutter.md`, `android.md` y `sveltekit.md`.
- `python.md` escribía `==3.13.*`, `==0.13.7` y `<0.14`, y `android.md`, `compileSdk`, `targetSdk`
  y `minSdk`, aunque `stack.md` dice que es el único lugar donde se fija una versión.
- «Git» de `repositorio.md` repetía el idioma del mensaje, de `principios.md`, y la arquitectura en
  el mismo commit, de `documentacion.md`.
- `qt.md` repetía «la última LTS», de «Versiones» de `stack.md`.
- La fila de `infra/` de `plantilla/README.md` reproducía `despliegue.md` y ya no coincidía: no
  nombraba `--task`, `--mobile` ni `--development`.

Y encontró reglas en uso sin escribir, o escritas sin uso:

- `Contrato:` abría 56 secciones de seis páginas, y `plataformas/README.md` no lo definía.
- 22 ADR llevaban el estado «Aceptada. El punto N lo reemplaza el ADR-X», que `documentacion.md`
  no describía.
- `plugins/` era una frase de `repositorio.md`, fuera de su tabla, y ninguna página la usaba.
  `verificar.py` aceptaba además `infra/`, que ninguna página define.

Comprobado el 2026-11-16 listando las carpetas de primer nivel de los 19 repositorios de `E:\Git`:
ninguno tiene `plugins/` ni `infra/`.

## Decisión

1. **La regla de las dependencias se define una vez, en «Qué entra» de `stack.md`.** Cada página
   escribe solo la herramienta con que su CI la comprueba, y lo que su plataforma cambia de ella.
2. **`python.md` remite a `stack.md` por la serie de Python, la versión de uv y el tope de
   `uv_build`.**
3. **`compileSdk`, `targetSdk` y `minSdk` se fijan en `stack.md`.** `android.md` conserva, con su
   origen, que `minSdk` no baja de la API 28.
4. **`repositorio.md` no repite el idioma del mensaje ni la arquitectura en el mismo commit**, y
   `qt.md` no repite la regla de la LTS.
5. **La fila de `infra/` de `plantilla/README.md` dice el tipo y remite a `despliegue.md`.** La
   firma de `install.py` y `--without`, que solo estaban en esa fila, pasan a «Procesos» de
   `despliegue.md`.
6. **`plataformas/README.md` define el párrafo `Contrato:`** en «Alcance».
7. **`documentacion.md` describe el reemplazo de solo algunos puntos de un ADR.**
8. **`plugins/` e `infra/` no son carpetas de primer nivel:** la frase sale de `repositorio.md`, y
   las dos, de `FIJAS` en `verificar.py`.

## Consecuencias

- Subir una versión de Python, de uv o de la API de Android toca `stack.md` y los manifiestos, no
  la página.
- `android.md` todavía nombra la API 37 en «Pruebas», en `pixel6Api37` y `apiLevel = 37`, y al
  explicar `espresso-core`: cambiar de API sigue tocando la página.
- Un repositorio con `plugins/` o `infra/` en la raíz falla `verificar.py`.
- Lo que una app de Flutter necesita de un canal nativo queda sin regla.

## Descartado

- **Dejar la regla de las dependencias en `python.md` y que los clientes la enlacen:** `python.md`
  es de las piezas en Python, y los clientes no la leen.
- **Mover `minSdk` a `stack.md` sin dejar nada en `android.md`:** el piso de la API 28 lo pone la
  fuente de las passkeys, y `stack.md` no lleva orígenes.
