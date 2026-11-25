# ADR-0171 · dependency-analysis no cuenta lo que solo usa el código que genera Hilt

- **Estado:** Aceptada. Salió al actualizar `equipaggio/mobile` a `android.md`, y el usuario la
  aceptó si cumple `plataformas/README.md` (2026-11-17)
- **Fecha:** 2026-11-17
- **Alcance:** [`plataformas/android.md`](../plataformas/android.md), «Proyecto», y
  [`stack.md`](../stack.md)

## Contexto

El [ADR-0159](0159-cada-cliente-comprueba-en-ci-que-declara-lo-que-importa-y-usa-lo-que-declara.md)
comprobó `buildHealth` sobre un proyecto mínimo. Sobre `equipaggio/mobile`, con Hilt 2.60.1,
dependency-analysis 3.20.3, AGP 9.5.1 y el JDK 25.0.5, `buildHealth` pide además declarar:

- Lo que el código de la app importa: `activity`, `core`, `lifecycle-common`,
  `lifecycle-viewmodel`, `datastore-core`, `datastore-preferences-core`, siete artefactos de
  Compose, `dagger`, `hilt-core`, `javax.inject`, `kotlinx-coroutines-core` y
  `kotlinx-serialization-core`.
- Lo que solo usa el código que genera Hilt: `androidx.annotation:annotation`,
  `androidx.fragment:fragment` (1.5.1), `androidx.lifecycle:lifecycle-viewmodel-savedstate` y
  `org.jspecify:jspecify`. El código de la app no importa ninguno.
- `core-ktx`: llega en la 1.18.0 y repite clases de `core` 1.19.1, cuyo `core-ktx` está vacío.

Comprobado: con esos cambios, `buildHealth` pasa, y también las pruebas, Android Lint, ktlint y
`assembleRelease`.

Comprobado después, con `javap` sobre el código compilado: `jspecify` no lo usa el código que
genera Hilt, sino `GatewayService`, porque Kotlin copia en el tipo que infiere de
`NotificationCompat` su anotación `@NonNull` de jspecify. El código fuente tampoco lo importa, y
la página lo dice así.

Comprobado el 2026-11-25 con dependency-analysis 3.20.4, AGP 9.5.2, el BOM de Compose 2026.11.01 y una
prueba instrumentada que llama a `enableAccessibilityChecks()`:

- Con `createAndroidComposeRule`, `buildHealth` pide declarar `androidx.test.ext:junit`: está en el tipo
  de la regla. La prueba corre en el emulador sin declararla y sin `@RunWith`. Con `createComposeRule`
  no la pide.
- Con las dos reglas, pide declarar `accessibility-test-framework` 4.1.1, que el código no importa:
  es el tipo del parámetro que `enableAccessibilityChecks()` llena por defecto. Con él en el `exclude`,
  pasa, y la página lo dice así.
- `androidx.test:runner` y `ui-test-manifest` van con `androidTestRuntimeOnly` y `debugRuntimeOnly`.

## Decisión

1. **dependency-analysis saca de las transitivas usadas lo que solo usa el código
   que genera Hilt**, con `onUsedTransitiveDependencies { exclude(...) }`. La regla de declarar lo
   que se importa evita que un import se rompa cuando cambia el paquete que lo trae, y aquí el
   import y el paquete los pone la misma versión de Hilt.
2. **`core-ktx` se fija con `constraints` en la versión de `core`.**
3. **`stack.md` suma `javax.inject`, «1, la que trae Hilt».** El resto de lo que pide
   `buildHealth` ya está en una fila de su familia: Hilt, Lifecycle, DataStore, el BOM de Compose y
   las de kotlinx.

## Consecuencias

- Al subir Hilt, la lista puede cambiar: `buildHealth` lo muestra como un aviso nuevo.
- Sin confirmar: de dónde sale el uso de `jspecify`, que no aparece en el código generado.

## Descartado

- **Declarar también lo que usa el código generado:** suma a `stack.md` versiones que fija Hilt,
  como `fragment` 1.5.1, y cada subida de Hilt las vuelve a mover.
