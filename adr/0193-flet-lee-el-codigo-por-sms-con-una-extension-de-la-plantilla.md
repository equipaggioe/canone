# ADR-0193 · Flet lee el código por SMS con una extensión que copia la plantilla

- **Estado:** Aceptada. El usuario eligió leer el código del SMS con una extensión, por la experiencia
  del usuario, y copiarla desde la plantilla en vez de darle un repositorio propio (2026-11-18)
- **Fecha:** 2026-11-19
- **Alcance:** [`plataformas/flet.md`](../plataformas/flet.md), «Código por SMS»;
  [`stack.md`](../stack.md), «Flet»; `plantilla/packages/sms/`, `plantilla/README.md` y
  `scripts/verificar.py`

## Contexto

- Comprobado el 2026-11-18 en un Galaxy S10e con Android 12: con el teclado y el autocompletado de
  Samsung, un `TextField` de Flet con `AutofillHint.ONE_TIME_CODE` no ofrece el código del SMS.
- Ningún paquete de PyPI da a Flet el SMS Retriever.
- Comprobado el 2026-11-19 con Flet 1.1.2: una extensión sobre sms_autofill 2.6.1 no construye,
  porque sms_autofill compila con `compileSdk 37` y AGP 8.13.2 busca `android-37`, que el SDK
  publica como `android-37.0`. Sobre smart_auth 4.0.0, con `compileSdk 35`, construye.
- Comprobado el 2026-11-19 en el mismo teléfono: con la extensión sobre smart_auth, la app mostró el
  hash que da `apksigner` para su certificado y, al llegar un SMS con ese hash y la última línea
  `@<host> #<código>`, recibió el código en `on_code` sin que el usuario tocara nada.

## Decisión

1. **La extensión `flet_sms` vive en `plantilla/packages/sms/` y se copia sin editar** al
   `packages/sms/` del repositorio cuya app de Flet lee el código por SMS. `verificar.py` compara la
   copia.
2. **`flet_sms` usa smart_auth 4.0.0** y lee los 6 dígitos que siguen al `#` de la última línea.

## Consecuencias

- Una corrección de la extensión se hace en la plantilla y se propaga a cada repositorio.
- Flutter sigue con sms_autofill: su versión de AGP la elige el proyecto.

## Descartado

- **Un repositorio propio para la extensión:** un repositorio entero para una sola función.
- **Que el usuario escriba el código:** peor experiencia en cada registro y cada recuperación.
- **sms_autofill:** no construye con Flet 1.1.2.
