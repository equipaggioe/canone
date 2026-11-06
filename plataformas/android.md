# Android

> **En desarrollo; no se implementa:** [README.md](README.md#en-desarrollo).

Una app de Android en Kotlin y Jetpack Compose.

## Proyecto

- Gradle usa Kotlin DSL y corre con el JDK 25.0.5, la última LTS.
- `gradle.properties` lleva `org.gradle.jvmargs=-Xmx4g -XX:MaxMetaspaceSize=2g`: con el JDK 25, Android Lint agota 512 MB de Metaspace.
- Las dependencias y los plugins se declaran en el catálogo `gradle/libs.versions.toml`, con nombres en kebab-case, como `androidx-ktx`: una sola lista de versiones, y el autocompletado del IDE los encuentra.
- Gradle 9.8.2, AGP 9.5.0 y Kotlin 2.4.21, también en las apps Flutter. Con una sola versión, un proyecto no se queda con la que traía la plantilla el día en que se creó.
- Gradle corre con el wrapper y su distribución `-bin`: `-all` solo agrega las fuentes y la documentación de Gradle.

Plantilla: [plantilla/android/gradle/wrapper/gradle-wrapper.properties](../plantilla/android/gradle/wrapper/gradle-wrapper.properties), que se copia sin editar.

## Estilo

Estándares: la [guía de estilo de Kotlin para Android](../fuentes/android/kotlin-style-guide.md) y las secciones *Avoid redundant constructs* e *Idiomatic use of language features* de las [*Coding conventions*](../fuentes/kotlin/coding-conventions.md) de Kotlin.

- ktlint formatea y revisa con el estilo `android_studio`, el de la guía de Android. Corre con el plugin de Gradle `org.jlleitschuh.gradle.ktlint`, y el estilo va en `.editorconfig`.
- Android Lint trata las advertencias como errores, con `warningsAsErrors = true` en el bloque `lint` de `app/build.gradle.kts`. Endurece Android Lint: una advertencia no pasa CI.
- El mismo bloque apaga `AndroidGradlePluginVersion`, `GradleDependency` y `NewerVersionAvailable`, que avisan cuando sale una versión más nueva: Gradle, AGP y Kotlin los fija «Proyecto», y con esos avisos el CI fallaría cada vez que se publica una versión, sin que cambie el repositorio.

Plantilla: [plantilla/android/](../plantilla/android/): `.editorconfig`, que se copia sin editar, y `.gitignore`.

## Arquitectura

Estándares: la [guía de arquitectura](../fuentes/android/architecture.md), sus [recomendaciones](../fuentes/android/architecture-recommendations.md), la [capa de UI](../fuentes/android/ui-layer.md) y la [capa de datos](../fuentes/android/data-layer.md), las [buenas prácticas de corrutinas](../fuentes/android/coroutines-best-practices.md) y [Hilt](../fuentes/android/hilt.md).

```text
mobile/
  settings.gradle.kts
  build.gradle.kts
  gradle/
    libs.versions.toml
  app/
    build.gradle.kts
    src/
      main/java/<paquete>/
        App.kt              la Application con @HiltAndroidApp
        MainActivity.kt
        data/
          repository/
          network/          Retrofit y OkHttp
          local/            DataStore
        di/                 los módulos de Hilt
        ui/
          theme/
          <función>/        la pantalla y su ViewModel
      test/java/<paquete>/
      androidTest/java/<paquete>/
```

- Todo va en un solo módulo `app`.
- HTTP va por Retrofit con OkHttp. El `Authenticator` de OkHttp hace el único reintento tras refrescar la sesión que pide [transversal.md](transversal.md#sesión).
- El JSON se lee con kotlinx.serialization. Las propiedades de Kotlin ya están en camelCase, como el cable.

## Compose

Estándares: el [estado](../fuentes/compose/state.md) y la [arquitectura](../fuentes/compose/architecture.md) de Compose.

## Accesibilidad

Estándares: de Android, [*Make apps more accessible*](../fuentes/android/accessibility-apps.md) y [*Principles for improving app accessibility*](../fuentes/android/accessibility-principles.md).

Contrato: [transversal.md](transversal.md#accesibilidad).

- Las pruebas de UI de Compose llaman a `enableAccessibilityChecks()`. [Compose](https://developer.android.com/develop/ui/compose/accessibility/testing)

## Almacenamiento

Estándares: [DataStore](../fuentes/android/datastore.md) y el [Keystore de Android](../fuentes/android/keystore.md).

- Las preferencias van en Preferences DataStore.
- Lo sensible, como el token de refresco que pide [transversal.md](transversal.md#sesión), va en DataStore, cifrado con una clave AES-GCM del Keystore. La clave no sale del dispositivo, así que lo cifrado no sirve fuera de él.

## Código por SMS

Estándar: las secciones *Start the SMS retriever*, *Receive verification messages* y *Send the one-time code from the verification message to your server* de [*Request SMS Verification in an Android App*](../fuentes/android/sms-retriever-request.md) de Google.

Contrato: [transversal.md](transversal.md#código-por-sms).

- El `BroadcastReceiver` se registra en tiempo de ejecución, mientras la pantalla del código está abierta: solo esa pantalla espera el SMS.

## Idiomas

Estándar: la [localización](../fuentes/android/localization.md) de Android.

Contrato: [transversal.md](transversal.md#idiomas).

## Mapas

Contrato: [transversal.md](transversal.md#mapas).

- El mapa usa MapLibre Android, con un estilo de una sola capa raster que arma la app con la configuración del servidor. Va dentro de Compose con `AndroidView`.

## Pagos

Contrato: [transversal.md](transversal.md#pagos).

- Con Stripe, la hoja de pago es `PaymentSheet` del SDK de Stripe para Android.

## Passkeys

Estándares: los [requisitos de Credential Manager](../fuentes/android/credential-manager-prerequisites.md), [*Create a passkey*](../fuentes/android/create-passkeys.md) y [*Sign in with a passkey*](../fuentes/android/sign-in-with-passkeys.md) de Android.

Contrato: [transversal.md](transversal.md#passkeys).

## Push

Estándares: [*Notification runtime permission*](../fuentes/android/notification-permission.md) y [*Create and manage notification channels*](../fuentes/android/notification-channels.md) de Android.

Contrato: [transversal.md](transversal.md#push).

## Tema

> **En desarrollo; no se implementa:** [transversal.md](transversal.md#tema).

Contrato: [transversal.md](transversal.md#tema).

- El `ColorScheme` claro y el oscuro son `LightColorScheme` y `DarkColorScheme`, generados en `ui/theme/Colors.kt`, sin color dinámico, y el modo sigue al sistema. El color dinámico reemplazaría la paleta del producto, que es la misma en todas las superficies.
- Los tamaños van en `ui/theme/`, sin tamaños literales fuera de él.

## Pruebas

Estándar: los [fundamentos de pruebas](../fuentes/android/testing-fundamentals.md).

- Las llamadas HTTP se prueban contra MockWebServer.

## Cumplimiento

| Convención | Herramienta |
| :--- | :--- |
| Gradle, AGP, Kotlin y el JDK | [scripts/verificar.py](../scripts/verificar.py) |
| `MaxMetaspaceSize=2g` | [scripts/verificar.py](../scripts/verificar.py) |
| Objetivos, etiquetas y contraste | `enableAccessibilityChecks()` en las pruebas de UI |
