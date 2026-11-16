# ADR-0160 · El usuario elige el modo claro u oscuro en cada dispositivo, y «sistema» es el inicial

- **Estado:** Aceptada
- **Fecha:** 2026-11-16
- **Alcance:** [`plataformas/transversal.md`](../plataformas/transversal.md), «Tema» y «Mapas»; «Tema» y «Mapas» de cada cliente

## Contexto

«Tema» decía que cada cliente sigue el modo claro u oscuro del sistema, sin dar una razón para no
dejar elegir. El [ADR-0062](0062-los-colores-de-un-producto-salen-de-brand-tokens-en-dtcg-y-un-generador-arma-el-esquema-de-cada-cliente.md),
punto 8, en propuesta, hacía que Qt siguiera el modo del sistema.

## Decisión

1. El usuario elige el modo en la app: sistema, claro u oscuro.
2. Con «sistema», con el que empieza, el cliente sigue el modo del sistema y cambia con él.
3. La elección es una preferencia del dispositivo, en el almacén de preferencias de cada cliente:
   `SharedPreferencesAsync` en Flutter, Preferences DataStore en Android, `localStorage` en la
   web, `SharedPreferences` en Flet y `QSettings` en Qt.
4. El mapa sigue el modo de la app.

## Consecuencias

- Quien quiere la app en otro modo que el del sistema no tiene que cambiar el del sistema.
- El servidor no guarda la elección: un dispositivo nuevo empieza en «sistema».
- En la web, el modo oscuro entra con `prefers-color-scheme` solo si `<html>` no lleva
  `data-theme`.

## Descartado

- **Seguir siempre el modo del sistema:** no tenía una razón escrita, y obliga a cambiar el modo
  de todo el dispositivo.
- **Guardar la elección en la cuenta:** el modo que conviene depende del dispositivo.
