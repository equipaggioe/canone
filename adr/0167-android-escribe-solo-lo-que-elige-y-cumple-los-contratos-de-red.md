# ADR-0167 · `android.md` escribe solo lo que elige, y cumple los contratos de red de `transversal.md`

- **Estado:** Aceptada. El usuario pidió aplicar la revisión (2026-11-16)
- **Fecha:** 2026-11-16
- **Alcance:** [`plataformas/android.md`](../plataformas/android.md), `fuentes/android/`,
  `fuentes/compose/`, [`stack.md`](../stack.md) y `scripts/contar_enunciados.py`

## Contexto

Revisión de `android.md` con los criterios del
[ADR-0162](0162-una-pagina-escribe-decisiones-y-no-como-funciona-su-tecnologia.md) y del
[ADR-0163](0163-una-revision-recorre-el-documento-entero-y-propone-tambien-lo-que-falta.md).

Comprobado con ktlint 1.8.0 y la `.editorconfig` de `plantilla/android/`:

- Marca dos líneas en blanco seguidas (`no-consecutive-blank-lines`), un bloque con solo un
  `return` (`function-expression-body`), un archivo de varias declaraciones en camelCase
  (`filename`) y un paquete con mayúsculas o con `_` (`package-name`).
- No marca un `for` ni un `while` sin llaves, un bloque vacío en una línea, dos miembros sin línea
  en blanco, un enum con líneas en blanco entre constantes sin cuerpo, un `import` partido, ni la
  falta de líneas en blanco entre `package`, los `import` y las declaraciones. Tampoco un escape
  Unicode de un carácter imprimible ni un tabulador dentro de un literal.

Comprobado en un proyecto con Gradle 9.9.1, AGP 9.5.1, Kotlin 2.4.21, dependency-analysis 3.20.3,
Hilt 2.60.1 y el BOM de Compose 2026.09.00, con el JDK 21:

- `espresso-core` 3.7.0 en `constraints` de `androidTestImplementation` reemplaza al 3.5.0 que
  trae `ui-test`, y `buildHealth`, con `severity("fail")`, pasa. Declarado como dependencia,
  `buildHealth` lo marca como no usado.
- AGP 9.5.1 no genera `BuildConfig` sin `buildConfig = true`.
- Un `Map<String, Any>` en una clase `@Serializable` no compila.
- Hilt no compila un módulo sin `@InstallIn` ni un `Context` sin calificador.
- Con OkHttp 5.5.1 y sus valores por defecto, una petición sin `User-Agent` lleva
  `okhttp/5.5.1`; el handshake de `newWebSocket` pasa por los interceptores del cliente, y un
  `POST` cuya conexión del pool se cierra después de enviarlo llega dos veces al servidor.

Leído: el `Serializer` que genera openapi-generator 7.27.0 activa `ignoreUnknownKeys` e
`isLenient`, y su `OffsetDateTimeAdapter` escribe con `ISO_OFFSET_DATE_TIME`, que incluye los
segundos `00`. *Auto Backup* dice que un dispositivo con la API 30 o menor usa
`android:fullBackupContent`, y la documentación de FCM, que el mensaje sin canal va al de
`default_notification_channel_id`. Google publica la imagen `aosp_atd` de la API 37 para
`x86_64`.

## Decisión

1. **Salen las convenciones que tienen una sola forma correcta:** `@HiltAndroidApp`,
   `@AndroidEntryPoint`, `@InstallIn`, los calificadores de `Context`, el alcance que coincide con
   su componente, `POST_NOTIFICATIONS`, el orden de `startSmsRetriever`, mandar el código al
   servidor, no fijar `origin` y la propiedad que apaga la atribución de MapLibre.
2. **Salen las repetidas:** Kotlin DSL y la única `Activity`, que muestra el árbol; el idioma base
   de `strings.xml`; el estilo del mapa según el modo y el color dinámico, que dice
   `transversal.md`; el JSON por el convertidor de Retrofit; la comunicación entre capas con
   corrutinas y flows; el repositorio como única entrada; los tipos inmutables que se exponen; los
   estados relacionados en un solo objeto, y la inyección por constructor del repositorio y del
   ViewModel.
3. **Cinco documentos salen de `fuentes/`:** `ui-layer`, `compose/architecture`, `datastore`,
   `notification-channels` y `sms-retriever-request` quedan con menos de tres convenciones, y
   `sms-retriever-request` depende de Play services. Lo que se aprovecha de ellos pasa a propio.
   *Events in Compose* sale entero: contradice que la lógica de UI quede en la UI.
4. **Las clases del SDK de Android quedan también en la capa de UI**, además de los componentes de
   la app y las fuentes de datos que envuelven una API del sistema.
5. **Una versión que sube la que trae otra dependencia va en `constraints`**, y no como dependencia
   declarada. `espresso-core` sale del `exclude` de dependency-analysis.
6. **Lo sensible del DataStore también se excluye en `backup_rules.xml`**, para la copia de un
   dispositivo con la API 30 o menor.
7. **Cada pantalla tiene una prueba de UI con `enableAccessibilityChecks()`.**
8. **Entra «Reintentos»:** el `OkHttpClient` lleva `retryOnConnectionFailure(false)`, y los
   reintentos de `transversal.md` los hace un interceptor de OkHttp.
9. **Entra «Versión mínima de cliente»:** un interceptor pone el `User-Agent` de pieza, y la
   versión vive solo en `versionName`, leída de `BuildConfig.VERSION_NAME`.
10. **Entra «WebSocket»:** va por `newWebSocket` del mismo `OkHttpClient`.
11. **«Push» nombra `firebase-messaging` y su `FirebaseMessagingService`**, y el manifiesto declara
    el canal por defecto de FCM.
12. ***Package Names* lo hace cumplir ktlint**, y `gradle-wrapper.properties` entra en
    «Cumplimiento».
13. **Salen razones que no corresponden:** las de las elecciones (`-bin`, el catálogo, el registro
    del receptor del SMS, `isShrinkResources`), la de Robolectric y `testedAbi`, y la versión de
    Kotlin que trae AGP. La de `jvmargs` pasa a lo comprobado en el
    [ADR-0119](0119-lo-que-corre-en-el-servidor-usa-la-version-de-debian-13-y-lo-demas-la-ultima-estable.md).

## Consecuencias

- `android.md` sigue en desarrollo: ningún repositorio la aplica.
- La razón de `-Xmx4g` queda sin comprobar: solo el Metaspace está comprobado.
- Que `espresso-core` 3.5.0 no corra en la API 37 queda sin comprobar en un dispositivo.

## Descartado

- **Conservar la 165 y recortar la propiedad `uiState` de las recomendaciones:** para el estado
  que expone un ViewModel, las recomendaciones resuelven más decisiones que `ui-layer`.
- **Sacar de «Proyecto» la frase de CI de `buildHealth`:** todas las páginas de cliente la
  escriben así, y `stack.md` la enlaza.
