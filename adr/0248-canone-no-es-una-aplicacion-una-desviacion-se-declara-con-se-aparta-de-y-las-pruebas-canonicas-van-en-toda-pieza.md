# ADR-0248 · Canone no es una aplicación, una desviación se declara con «Se aparta de», y las pruebas canónicas de Qt y de Flet van en toda pieza

- **Estado:** Aceptada. El usuario pidió aplicar lo recomendado en la revisión de coherencia del
  README y que se note que Canone no es una aplicación (2026-11-25). Los puntos 2 y 6 son
  *(propuesta)*: su forma se eligió al implementar.
- **Fecha:** 2026-11-25
- **Alcance:** [`README.md`](../README.md), [`principios.md`](../principios.md),
  [`repositorio.md`](../repositorio.md), [`documentacion.md`](../documentacion.md),
  [`plantilla/README.md`](../plantilla/README.md), [`fuentes/README.md`](../fuentes/README.md),
  `scripts/verificar.py` y `scripts/copiar.py`

## Contexto

Una revisión de la coherencia del README y de lo que enlaza encontró, comprobado con repositorios de
prueba y `scripts/verificar.py` del 2026-11-25:

- El README dejaba apartarse de una convención con un ADR, pero `verificar.py` no leía `docs/adr/`:
  un repositorio con un ADR aceptado que se aparta del `.gitattributes` fallaba igual, y
  `copiar.py` lo reemplazaba.
- Una pieza `desktop/` sin `tests/` daba 0 incumplimientos; con `tests/` vacía faltaban
  `test_theme.py` y `test_accessibility.py`.
- `verificar.py` decía que cada comprobación cita su ADR y que «una regla que no rompe CI es una
  sugerencia», y diez mensajes citaban un ADR en vez del documento que escribe la regla.

En la misma revisión se comprobó también, en Debian 13 con Node 26.13.1 y pnpm 12.23.0, con los
paquetes del bloque de SvelteKit de [`stack.md`](../stack.md): esbuild ya no llega, porque Vite 8.3.8
usa Rolldown, ningún paquete tiene script de instalación, y `CI=true pnpm install` termina bien sin
`pnpm-workspace.yaml`. `pnpm peers check` avisa que openapi-typescript 7.13.0 pide TypeScript `^5.x`,
y con TypeScript 6.0.3 genera igual los tipos del `openapi.json` de la plantilla.

## Decisión

1. **Canone no es una aplicación:** es una serie de documentos que definen aplicaciones, y las
   convenciones que escribe para ellas no se le aplican. El README lo dice al principio.
2. *(propuesta)* **Una desviación se declara en su ADR:** un ADR aceptado del repositorio nombra
   cada incumplimiento del que se aparta en una línea `- **Se aparta de:**` de su encabezado, con el
   texto exacto que reporta `verificar.py`. `verificar.py` lo informa aparte y no lo cuenta, falla
   con un «Se aparta de» que ya no es un incumplimiento, y `copiar.py` no reemplaza ese archivo. El
   `docs/arquitectura/` del repositorio describe lo que hace en lugar de la convención.
3. **Cada incumplimiento nombra el documento que escribe su regla**, nunca un ADR.
4. **Una pieza de Qt o de Flet lleva siempre las pruebas canónicas de `tests/`.** Un archivo
   canónico de `api/` o de `services/` va solo en la pieza que tiene esa carpeta.
5. **`principios.md`, `repositorio.md` y `documentacion.md` tienen su «Cumplimiento»**, con lo que
   comprueba `verificar.py`, como `stack.md`.
6. *(propuesta)* **`plantilla/README.md` suma dos tipos:** un archivo de la receptora, que la
   receptora de los respaldos corre desde Canone, y uno generado, que escribe un script canónico del
   repositorio.
7. **Una página web de `fuentes/` sin versiones ni commit lleva en «Nota» la fecha de su copia.**
8. **El estado de un ADR puede decir quién lo confirmó y cuándo.**

## Consecuencias

- Los comentarios de cinco canónicos del servidor nombran el ADR de Canone que citan: cada
  repositorio con servidor falla en `verificar.py` hasta copiarlos con `copiar.py --aplicar`.
- Con el punto 4, una pieza de Qt o de Flet sin `tests/` falla hasta tener sus pruebas.
- Las propuestas sin confirmar de los ADR quedan en `pendientes/propuestas-sin-confirmar.md`.
- `scripts/recuperar.py` sale de Canone: no sirve a ninguna convención.

## Descartado

- **Una lista de desviaciones en un archivo del repositorio:** separaría la desviación de su
  motivo, que ya está en el ADR.
- **Que una convención comprobada no admita desviación:** contradice que un repositorio se aparta
  con un ADR propio.
