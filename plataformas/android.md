# Android

Una app de Android en Kotlin y Jetpack Compose.

## Proyecto

Estándar: [*Migrate your build to version catalogs*](../estandares/android/version-catalogs.md).

- Gradle usa Kotlin DSL y corre con el JDK 21 de Debian 13.

## Estilo

Estándares: la [guía de estilo de Kotlin para Android](../estandares/android/kotlin-style-guide.md)
y las [*Coding conventions*](../estandares/kotlin/coding-conventions.md) de Kotlin.

- ktlint formatea y revisa con el estilo `android_studio`, el de la guía de Android. Corre con el
  plugin de Gradle `org.jlleitschuh.gradle.ktlint`, y el estilo va en `.editorconfig`.
- Android Lint trata las advertencias como errores, con `warningsAsErrors = true` en el bloque
  `lint` de `app/build.gradle.kts`. Endurece Android Lint: una advertencia no pasa CI.

Plantilla: [`plantilla/android/`](../plantilla/android/): `.editorconfig`, que se copia sin
editar, y `.gitignore`.

## Arquitectura

Estándares: la [guía de arquitectura](../estandares/android/architecture.md), sus
[recomendaciones](../estandares/android/architecture-recommendations.md), la
[capa de UI](../estandares/android/ui-layer.md) y la [capa de datos](../estandares/android/data-layer.md),
las [buenas prácticas de corrutinas](../estandares/android/coroutines-best-practices.md) y
[Hilt](../estandares/android/hilt.md).

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
- HTTP va por Retrofit con OkHttp. El `Authenticator` de OkHttp hace el único reintento tras
  refrescar la sesión que pide [transversal.md](transversal.md#sesión).
- El JSON se lee con kotlinx.serialization. Las propiedades de Kotlin ya están en camelCase, como el
  cable.

## Compose

Estándares: el [estado](../estandares/compose/state.md) y la
[arquitectura](../estandares/compose/architecture.md) de Compose, y
[Navigation 3](../estandares/android/navigation-3.md).

## Accesibilidad

Estándares: de Android, [*Make apps more accessible*](../estandares/android/accessibility-apps.md)
y [*Principles for improving app accessibility*](../estandares/android/accessibility-principles.md),
y de Compose, [*Accessibility testing*](../estandares/compose/accessibility-testing.md).

Contrato: [transversal.md](transversal.md#accesibilidad).

- Las pruebas de UI de Compose llaman a `enableAccessibilityChecks()`.

## Almacenamiento

Estándares: [DataStore](../estandares/android/datastore.md) y el
[Keystore de Android](../estandares/android/keystore.md).

- Las preferencias van en Preferences DataStore.
- Lo sensible, como el token de refresco que pide [transversal.md](transversal.md#sesión), va en
  DataStore, cifrado con una clave AES-GCM del Keystore. La clave no sale del dispositivo, así que
  lo cifrado no sirve fuera de él.

## Código por SMS

Estándar: las secciones *Start the SMS retriever*, *Receive verification messages* y *Send the
one-time code from the verification message to your server* de
[*Request SMS Verification in an Android App*](../estandares/android/sms-retriever-request.md) de
Google.

Contrato: [transversal.md](transversal.md#código-por-sms).

- El `BroadcastReceiver` se registra en tiempo de ejecución, mientras la pantalla del código está
  abierta: solo esa pantalla espera el SMS.

## Idiomas

Estándar: la [localización](../estandares/android/localization.md) de Android.

Contrato: [transversal.md](transversal.md#idiomas).

## Mapas

Estándar: [*Quickstart*](../estandares/maplibre/android-getting-started.md) de MapLibre Android.

Contrato: [transversal.md](transversal.md#mapas).

- El mapa usa MapLibre Android, con un estilo de una sola capa raster que arma la app con la
  configuración del servidor. Va dentro de Compose con `AndroidView`.

## Tema

Estándar: [Material 3 en Compose](../estandares/compose/material3.md).

- El `ColorScheme` claro y el oscuro salen de los tokens de `ui/theme/`, sin color dinámico, y el
  modo sigue al sistema. El color dinámico reemplazaría la paleta del producto, que es la misma en
  todas las superficies.

## Pruebas

Estándares: los [fundamentos de pruebas](../estandares/android/testing-fundamentals.md) y las
[pruebas de Compose](../estandares/compose/testing.md).

- Las llamadas HTTP se prueban contra MockWebServer.

## Cómo se hace cumplir

| Qué | Con qué |
|---|---|
| Objetivos, etiquetas y contraste | `enableAccessibilityChecks()` en las pruebas de UI |
