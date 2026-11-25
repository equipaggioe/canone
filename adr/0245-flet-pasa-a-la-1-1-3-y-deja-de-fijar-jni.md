# ADR-0245 · Flet pasa a la 1.1.3 con Pydantic 2.14.3, y deja de fijar `jni`

- **Estado:** Aceptada. El usuario pidió reevaluar las razones de estas versiones y actualizar lo que
  no tenga una válida, y la confirmó el 2026-11-25
- **Fecha:** 2026-11-25
- **Alcance:** [`stack.md`](../stack.md), [`flet.md`](../plataformas/flet.md), `fuentes/flet/`,
  `plantilla/flet/`, `plantilla/packages/` y `scripts/verificar.py`

## Contexto

- **Flet 1.1.2:** el 2026-11-06 se anotó que subir Flet pide probar `flet build apk`, y
  `fuentes/README.md` pide descargar otra vez sus fuentes. Es lo que cuesta subir, y no una razón
  para quedarse.
- **Pydantic 2.13.4:** el [ADR-0118](0118-cada-pagina-fija-la-version-de-sus-tecnologias-y-la-plantilla-y-las-fuentes-la-siguen.md)
  la fijó porque el índice de Flet llegaba a `pydantic-core` 2.47.0. Hoy trae el 2.50.4, el de
  Pydantic 2.14.3, para Android y iOS con Python 3.13, y no el 2.50.5, el de la 2.14.4.
- **`jni` 1.1.2 y `jni_flutter` 1.0.4+1:** el
  [ADR-0187](0187-flet-fija-jni-y-jni-flutter-en-el-pubspec-que-genera.md) las fijó porque con `jni`
  1.2.0 la app no arrancaba. El 2026-11-19 salió la 1.2.1.

Comprobado el 2026-11-25 con Flutter 3.47.5, el JDK 25.0.5 y un emulador x86_64 de la API 36, con una
app que muestra las versiones de Pydantic y de httpx y que lleva `flet_sms`:

| Build de `flet build apk`, Flet 1.1.3 y Pydantic 2.14.3 | En el emulador |
| :--- | :--- |
| `jni` 1.2.0 y `jni_flutter` 1.1.0 | No arranca: `ClassNotFoundException: Didn't find class "Landroid/content/Context;"` |
| `jni` 1.2.1 y `jni_flutter` 1.1.0, lo último que admite `path_provider_android` 2.3.1 | Arranca y muestra `2.14.3 0.28.1` |

De las 12 fuentes de Flet cambian 4: `publish`, `publish-macos`, `async-apps` y
`declarative-vs-imperative`. De sus convenciones cambia una: `page.run_task()` registra la excepción
de la tarea que nadie espera.

## Decisión

1. **Flet y flet-secure-storage pasan a la 1.1.3**, con sus fuentes y los enlaces de `flet.md`.
2. **Pydantic de Flet pasa a la 2.14.3**, la última cuyo `pydantic-core` está en el índice de Flet.
   Reemplaza esa parte del punto 4 del ADR-0118.
3. **`jni` y `jni_flutter` salen** del stack, de la plantilla, de `flet.md` y de `verificar.py`.
   Reemplaza el ADR-0187.

## Consecuencias

- `flet build` resuelve `jni` sin una versión fija: una nueva con la misma falla llegaría sin que
  cambie el repositorio.
- Sin confirmar: un teléfono, iOS y el escritorio con Flet 1.1.3.
- Una app de Flet con `packages/passkey/` no construye: Flet registra como extensión cada paquete de
  `flutter/`, y `passkey` no tiene `Extension()`. La 1.1.2 registra igual (leído).

## Descartado

- **Fijar `jni` 1.2.1:** es la que se resuelve sola, y `flet.md` pide no reemplazar dependencias de
  Flutter.
