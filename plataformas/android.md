# Android

Una app de Android en Kotlin y Jetpack Compose.

## Proyecto

- `compileSdk`, `targetSdk` y `minSdk` son los de [stack.md](../stack.md#android). `compileSdk` se declara con `release(<API>) { minorApiLevel = <menor> }`.
- Kotlin es el que integra AGP, sin el plugin `org.jetbrains.kotlin.android`. Su versión la fijan `org.jetbrains.kotlin.plugin.compose` y `org.jetbrains.kotlin.plugin.serialization`, declarados con `apply false` en el `build.gradle.kts` raíz: Gradle usa la versión más alta de las que ve el build raíz, y la que trae AGP es anterior. [Built-in Kotlin](https://developer.android.com/build/migrate-to-built-in-kotlin)
- Gradle corre con el wrapper y su distribución `-bin`.
- `gradle.properties` lleva `org.gradle.jvmargs=-Xmx4g -XX:MaxMetaspaceSize=2g`: con los valores por defecto de Gradle, 512 MiB de heap y 384 MiB de Metaspace, el build de release se queda sin heap y Gradle descarta el daemon al agotarse el Metaspace. [Gradle 9.9.1](https://docs.gradle.org/9.9.1/userguide/build_environment.html#sec:configuring_jvm_memory)
- Las dependencias y los plugins se declaran en el catálogo `gradle/libs.versions.toml`, con nombres en kebab-case, como `androidx-ktx`.
- La versión de ktlint la fija el bloque `ktlint` de `app/build.gradle.kts`.
- La versión que sube la que trae otra dependencia se fija en un bloque `constraints`, y no con una dependencia declarada.
- El plugin `com.autonomousapps.dependency-analysis` va en el `build.gradle.kts` raíz y en el de `app`: aplicado solo en la raíz, no analiza `app`. Su bloque `dependencyAnalysis` del raíz hace fallar cada aviso con `onAny { severity("fail") }`, y con `onUsedTransitiveDependencies { exclude(...) }` saca lo que solo usa el código que genera Hilt: `androidx.annotation:annotation`, `androidx.fragment:fragment`, `androidx.lifecycle:lifecycle-viewmodel-savedstate` y `org.jspecify:jspecify`: el import y el paquete los pone la misma versión de Hilt. CI corre `./gradlew buildHealth`, que falla con una dependencia que no se usa o un paquete importado sin declarar ([stack.md](../stack.md#qué-entra)).
- `espresso-core` se fija con `constraints` en `androidTestImplementation`: el 3.5.0 que trae `ui-test-junit4` no corre en la API 37.
- `core-ktx` se fija con `constraints` en la versión de `core`: la 1.18.0 que llega con otras dependencias repite clases de `core`.
- Todo va en un solo módulo `app`, sin módulo de benchmark: sin un arranque lento medido, Macrobenchmark y los Baseline Profiles no tienen un síntoma que corregir.

```text
mobile/
  settings.gradle.kts
  build.gradle.kts
  gradle.properties
  .editorconfig
  .gitignore
  gradle/
    libs.versions.toml
    wrapper/
      gradle-wrapper.properties
  app/
    build.gradle.kts
    src/
      main/
        AndroidManifest.xml
        java/<paquete>/
          App.kt              la Application con @HiltAndroidApp
          MainActivity.kt     la única Activity
          data/
            repository/
            network/          Retrofit y OkHttp
            local/            DataStore
          di/                 los módulos de Hilt
          ui/
            theme/
            <función>/        la pantalla y su ViewModel
        res/
          resources.properties
          values/
            strings.xml       los textos en el idioma base
          xml/
            backup_rules.xml
            data_extraction_rules.xml
      test/java/<paquete>/
      androidTest/java/<paquete>/
```

Plantilla: [plantilla/android/](../plantilla/android/): `.editorconfig` y `gradle/wrapper/gradle-wrapper.properties`, que se copian sin editar, y `.gitignore`.

## Estilo

Estándar: la [guía de estilo de Kotlin](../fuentes/android/kotlin-style-guide.md) de Android.

- ktlint formatea y revisa el código con `ktlint_code_style = android_studio` en `.editorconfig`, el estilo de la guía de Android, y CI corre `./gradlew ktlintCheck`.
- Android Lint trata las advertencias como errores, con `warningsAsErrors = true` en el bloque `lint` de `app/build.gradle.kts`.
- El mismo bloque apaga `AndroidGradlePluginVersion`, `GradleDependency` y `NewerVersionAvailable`, que avisan cuando sale una versión más nueva: [stack.md](../stack.md#android) fija las versiones, y con esos avisos el CI fallaría cada vez que se publica una, sin que cambie el repositorio.
- Un archivo con una sola clase de nivel superior se llama como ella, con `.kt`, y uno con varias declaraciones, con un nombre en PascalCase que describe su contenido, también en plural: ktlint no admite camelCase ([Kotlin style guide, *Source files*](../fuentes/android/kotlin-style-guide.md)).
- Nunca van dos líneas en blanco seguidas: ktlint no las admite ([Kotlin style guide, *Vertical*](../fuentes/android/kotlin-style-guide.md)).
- Una función con una sola expresión usa un cuerpo de expresión: ktlint no admite un bloque con solo un `return` ([Kotlin style guide, *Expression functions*](../fuentes/android/kotlin-style-guide.md)).
- Un carácter imprimible que no es ASCII se escribe tal cual, y un escape Unicode solo va para uno que no se imprime ([Kotlin style guide, *Non-ASCII characters*](../fuentes/android/kotlin-style-guide.md)).
- El código cumple *Non-empty blocks*, *Indentation*, *One statement per line*, *Functions* y *Horizontal*, que hace cumplir ktlint ([Kotlin style guide, *Non-empty blocks*](../fuentes/android/kotlin-style-guide.md), [*Indentation*](../fuentes/android/kotlin-style-guide.md), [*One statement per line*](../fuentes/android/kotlin-style-guide.md), [*Functions*](../fuentes/android/kotlin-style-guide.md) y [*Horizontal*](../fuentes/android/kotlin-style-guide.md)).
- Los archivos fuente van en UTF-8 ([Kotlin style guide, *Source files*](../fuentes/android/kotlin-style-guide.md)).
- Fuera del fin de línea, el único espacio en blanco es el espacio ASCII: los demás van como escape en los literales, y la sangría no usa tabuladores ([Kotlin style guide, *Whitespace characters*](../fuentes/android/kotlin-style-guide.md)).
- Un carácter con secuencia de escape propia, como `\n`, `\t`, `\"` o `\$`, se escribe con ella, y no con su escape Unicode ([Kotlin style guide, *Special escape sequences*](../fuentes/android/kotlin-style-guide.md)).
- Un archivo `.kt` lleva, en este orden y con una línea en blanco entre cada parte, las anotaciones de archivo, el `package`, los `import` y las declaraciones de nivel superior ([Kotlin style guide, *Structure*](../fuentes/android/kotlin-style-guide.md) y [*File-level annotations*](../fuentes/android/kotlin-style-guide.md)).
- El `package` y los `import` no se parten ni cuentan para el límite de columnas ([Kotlin style guide, *Package statement*](../fuentes/android/kotlin-style-guide.md) e [*Import statements*](../fuentes/android/kotlin-style-guide.md)).
- Los `import` van en una sola lista en orden ASCII, y ninguno lleva comodín ([Kotlin style guide, *Import statements*](../fuentes/android/kotlin-style-guide.md)).
- Un archivo trata un solo tema: una declaración sin relación con el resto va en su propio archivo, y las públicas de un archivo son las menos posibles ([Kotlin style guide, *Top-level declarations*](../fuentes/android/kotlin-style-guide.md)).
- Las declaraciones de un archivo y los miembros de una clase siguen un orden lógico que quien los mantiene puede explicar, y no el orden en que se agregaron ([Kotlin style guide, *Top-level declarations*](../fuentes/android/kotlin-style-guide.md) y [*Class member ordering*](../fuentes/android/kotlin-style-guide.md)).
- Un `if`, un `for`, una rama de `when`, un `do` y un `while` llevan llaves, aunque su cuerpo esté vacío o tenga una sola sentencia, salvo una rama de `when` o un `if` con a lo sumo un `else` que caben enteros en una línea ([Kotlin style guide, *Braces*](../fuentes/android/kotlin-style-guide.md) y [*Expressions*](../fuentes/android/kotlin-style-guide.md)).
- Un bloque vacío también sigue el estilo K&R: su `{` y su `}` van en líneas distintas ([Kotlin style guide, *Empty blocks*](../fuentes/android/kotlin-style-guide.md)).
- Una línea tiene hasta 100 columnas, salvo la que no puede cumplirlo, como una URL larga en un KDoc, y una línea de comandos en un comentario ([Kotlin style guide, *Line wrapping*](../fuentes/android/kotlin-style-guide.md)).
- Una línea se parte en el nivel sintáctico más alto posible: después de un operador o de una función infija, antes de `.`, `?.` y `::`, y nunca entre el nombre de una función y su `(`, entre una coma y lo que la precede ni entre `->` y la lista de argumentos que lo precede ([Kotlin style guide, *Where to break*](../fuentes/android/kotlin-style-guide.md)).
- El inicializador de una propiedad que no cabe en una línea va después de `=`, en la línea siguiente y con sangría, y cada `get` y `set` va en su línea, con cuatro espacios de sangría ([Kotlin style guide, *Properties*](../fuentes/android/kotlin-style-guide.md)).
- Una línea en blanco separa los miembros seguidos de una clase, salvo dos propiedades seguidas, donde es opcional ([Kotlin style guide, *Vertical*](../fuentes/android/kotlin-style-guide.md)).
- En un enum con una constante por línea, solo la constante que define un cuerpo va separada por una línea en blanco ([Kotlin style guide, *Enum classes*](../fuentes/android/kotlin-style-guide.md)).
- Una anotación de miembro o de tipo va en su línea, justo antes de lo que anota, salvo las que no llevan argumentos, que pueden compartir línea entre ellas o, si es una sola, con la declaración. `@[...]` va solo con un destino de uso explícito y para dos o más anotaciones sin argumentos ([Kotlin style guide, *Annotations*](../fuentes/android/kotlin-style-guide.md)).

## Nombres

Estándar: la [guía de estilo de Kotlin](../fuentes/android/kotlin-style-guide.md) de Android.

- Un identificador lleva solo letras y dígitos ASCII, y `_` solo donde lo permite esta sección. No lleva prefijos ni sufijos como `mName`, `name_` o `kName` ([Kotlin style guide, *Naming*](../fuentes/android/kotlin-style-guide.md)).
- El código cumple *Package Names*, que hace cumplir ktlint ([Kotlin style guide, *Package Names*](../fuentes/android/kotlin-style-guide.md)).
- Una clase va en PascalCase y se nombra con un sustantivo, y una interfaz, con un sustantivo o un adjetivo. Una clase de prueba lleva el nombre de la clase que prueba y termina en `Test` ([Kotlin style guide, *Type names*](../fuentes/android/kotlin-style-guide.md)).
- Una función va en camelCase y se nombra con un verbo, salvo un `@Composable` que devuelve `Unit`, que va en PascalCase y con un sustantivo. Una función de prueba separa con `_` las partes de su nombre, y ningún nombre de función lleva espacios entre acentos graves ([Kotlin style guide, *Function names*](../fuentes/android/kotlin-style-guide.md)).
- Una constante es un `val` sin `get` propio, de contenido profundamente inmutable y sin efectos visibles, declarada en un `object` o en el nivel superior. Va en UPPER_SNAKE_CASE, y lleva `const` si es un escalar ([Kotlin style guide, *Constant names*](../fuentes/android/kotlin-style-guide.md)).
- Lo que no es constante, como una propiedad, una variable local o un parámetro, va en camelCase ([Kotlin style guide, *Non-constant names*](../fuentes/android/kotlin-style-guide.md)).
- Una propiedad de respaldo lleva el nombre de la propiedad real con `_` delante ([Kotlin style guide, *Backing properties*](../fuentes/android/kotlin-style-guide.md)).
- Un parámetro de tipo es una mayúscula, seguida a lo sumo de un dígito, como `T` o `T2`, o un nombre de clase seguido de `T`, como `RequestT` ([Kotlin style guide, *Type variable names*](../fuentes/android/kotlin-style-guide.md)).
- Una sigla se escribe como una palabra, como `XmlHttpRequest` o `newCustomerId` ([Kotlin style guide, *Camel case*](../fuentes/android/kotlin-style-guide.md)).

## Comentarios

Estándar: la [guía de estilo de Kotlin](../fuentes/android/kotlin-style-guide.md) de Android.

- Un KDoc va en varias líneas, cada una con `*`, o en una sola si cabe entero en ella y no lleva etiquetas de bloque ([Kotlin style guide, *Documentation*](../fuentes/android/kotlin-style-guide.md)).
- Una línea con solo el `*` separa los párrafos de un KDoc, y los párrafos de las etiquetas de bloque ([Kotlin style guide, *Paragraphs*](../fuentes/android/kotlin-style-guide.md)).
- Las etiquetas de bloque van en el orden `@constructor`, `@receiver`, `@param`, `@property`, `@return`, `@throws`, `@see`, nunca sin descripción, y la línea que continúa una lleva cuatro espacios de sangría desde su `@` ([Kotlin style guide, *Block tags*](../fuentes/android/kotlin-style-guide.md)).
- Un KDoc empieza con un fragmento breve, un sintagma nominal o verbal, con mayúscula y punto como una oración, y no con «A `Foo` is a…» ni «This method returns…» ([Kotlin style guide, *Summary fragment*](../fuentes/android/kotlin-style-guide.md)).
- Todo tipo público, y todo miembro público o protegido de uno, lleva KDoc, salvo una función o una propiedad que no tiene nada que decir más que su nombre y lo que sobrescribe un supertipo ([Kotlin style guide, *Usage*](../fuentes/android/kotlin-style-guide.md), [*Exception: Self-explanatory functions*](../fuentes/android/kotlin-style-guide.md) y [*Exception: overrides*](../fuentes/android/kotlin-style-guide.md)).

## Uso del lenguaje

Estándar: las [*Coding conventions*](../fuentes/kotlin/coding-conventions.md) de Kotlin.

- Una construcción opcional que el IDE marca como redundante se omite ([Coding conventions, *Avoid redundant constructs*](../fuentes/kotlin/coding-conventions.md)).
- El código cumple *Unit return type*, que hace cumplir ktlint ([Coding conventions, *Unit return type*](../fuentes/kotlin/coding-conventions.md)).
- Una variable simple va en una plantilla de cadena sin llaves, y las llaves quedan para una expresión. Un `$` literal se escribe con la interpolación de varios dólares ([Coding conventions, *String templates*](../fuentes/kotlin/coding-conventions.md)).
- Una variable local o una propiedad que no se modifica después de inicializarse es `val`. Una colección que no se modifica se declara con su interfaz inmutable, como `List` o `Set`, y se crea con una función que la devuelve, como `listOf()` ([Coding conventions, *Immutability*](../fuentes/kotlin/coding-conventions.md)).
- Una función con valores por defecto en sus parámetros reemplaza a sus sobrecargas ([Coding conventions, *Default parameter values*](../fuentes/kotlin/coding-conventions.md)).
- Un tipo funcional o un tipo con parámetros de tipo que se repite lleva un `typealias`. Un choque de nombres se resuelve con `import … as …`, y no con un `typealias` privado ([Coding conventions, *Type aliases*](../fuentes/kotlin/coding-conventions.md)).
- Una lambda corta y no anidada usa `it`, y una anidada declara sus parámetros ([Coding conventions, *Lambda parameters*](../fuentes/kotlin/coding-conventions.md)).
- Una lambda no tiene varios `return` con etiqueta, y su última sentencia no es un `return` con etiqueta ([Coding conventions, *Returns in a lambda*](../fuentes/kotlin/coding-conventions.md)).
- Una llamada nombra sus argumentos si la función recibe varios parámetros del mismo tipo primitivo o uno `Boolean`, salvo que el contexto deje claro el sentido de todos ([Coding conventions, *Named arguments*](../fuentes/kotlin/coding-conventions.md)).
- `try`, `if` y `when` se usan como expresiones, como en `return if (x) foo() else bar()` ([Coding conventions, *Conditional statements*](../fuentes/kotlin/coding-conventions.md)).
- Una condición de dos casos es un `if`, y una de tres o más, un `when` ([Coding conventions, *if versus when*](../fuentes/kotlin/coding-conventions.md)).
- Una guarda de `when` que combina varias expresiones booleanas las encierra entre paréntesis ([Coding conventions, *Guard conditions in when expression*](../fuentes/kotlin/coding-conventions.md)).
- Un `Boolean?` se evalúa con `== true` o `== false` ([Coding conventions, *Nullable Boolean values in conditions*](../fuentes/kotlin/coding-conventions.md)).
- Un recorrido usa funciones de orden superior, como `filter` o `map`, y no un bucle, salvo `forEach`: va un `for`, a menos que el receptor admita `null` o que `forEach` siga una cadena de llamadas ([Coding conventions, *Loops*](../fuentes/kotlin/coding-conventions.md)).
- Un rango abierto por la derecha se escribe con `..<` ([Coding conventions, *Loops on ranges*](../fuentes/kotlin/coding-conventions.md)).
- Las cadenas se componen con plantillas, y no concatenando. Un texto de varias líneas es una cadena multilínea, y no una con `\n`. Una cadena multilínea lleva `trimIndent` o, si conserva una sangría interna, `trimMargin` ([Coding conventions, *Strings*](../fuentes/kotlin/coding-conventions.md)).
- Un cálculo sin argumentos que no lanza excepciones, es barato o se guarda en caché y devuelve lo mismo mientras el objeto no cambie es una propiedad, y no una función ([Coding conventions, *Functions vs properties*](../fuentes/kotlin/coding-conventions.md)).
- Una función de extensión tiene la menor visibilidad posible ([Coding conventions, *Extension functions*](../fuentes/kotlin/coding-conventions.md)).
- Una función es `infix` solo si opera sobre dos objetos con un papel parecido y no modifica el receptor ([Coding conventions, *Infix functions*](../fuentes/kotlin/coding-conventions.md)).
- Una función de fábrica lleva un nombre distinto del de su clase, que dice qué tiene de especial, y reemplaza a los constructores sobrecargados que no llaman a constructores distintos de la superclase ni se reducen a uno con valores por defecto ([Coding conventions, *Factory functions*](../fuentes/kotlin/coding-conventions.md)).
- Una función pública que devuelve una expresión de un tipo de plataforma, y una propiedad que se inicializa con una, declaran su tipo de Kotlin ([Coding conventions, *Platform types*](../fuentes/kotlin/coding-conventions.md)).

## Arquitectura

Estándares: la [guía de arquitectura](../fuentes/android/architecture.md), sus [recomendaciones](../fuentes/android/architecture-recommendations.md) y la [capa de datos](../fuentes/android/data-layer.md) de Android.

- HTTP va por Retrofit con OkHttp. El `Authenticator` de OkHttp hace el único reintento tras refrescar la sesión que pide [autenticacion.md](autenticacion.md#sesión).
- La app no guarda en el dispositivo los datos de la API: su fuente de verdad es el servidor, que también los cambia por push y por el WebSocket, y la app los vuelve a pedir al abrir una pantalla y al reconectar.
- Las clases del SDK de Android, como `Context` o `Toast`, quedan en los componentes de la app, en la capa de UI y en las fuentes de datos que envuelven una API del sistema, como el Keystore.
- El estado de la UI es inmutable, y la UI no lo modifica, salvo el que solo ella produce.
- La lógica de negocio nunca va en la capa de UI. La lógica de UI, como elegir un texto de los recursos, navegar o mostrar un snackbar, queda en la UI, y no en el ViewModel; si crece, va en una clase de estado simple de la UI.
- Ningún componente de la app, como una `Activity`, un `Service` o un `BroadcastReceiver`, guarda datos ni estado de la app, y ninguno depende de otro ([Guide to app architecture, *Variable launch conditions*](../fuentes/android/architecture.md) y [*General best practices*](../fuentes/android/architecture.md)).
- Cada tipo de dato tiene un solo dueño, el único que lo modifica: lo expone con un tipo inmutable y ofrece funciones para cambiarlo ([Guide to app architecture, *Single source of truth*](../fuentes/android/architecture.md)).
- El estado baja desde los tipos de mayor alcance hasta la UI, y los eventos suben hasta el dueño del dato, en todas las capas ([Guide to app architecture, *Unidirectional data flow*](../fuentes/android/architecture.md)).
- La UI no supone una orientación fija, conserva su estado ante un cambio de configuración, como girar o plegar el dispositivo, y una pantalla que cambia de disposición según el tamaño de la ventana usa un layout canónico ([Guide to app architecture, *Adaptive layouts*](../fuentes/android/architecture.md) y [*General best practices*](../fuentes/android/architecture.md)).
- El código que habla con la red está en las fuentes de datos de `data/network/`, y no repartido por otras clases ([Guide to app architecture, *General best practices*](../fuentes/android/architecture.md)).
- La capa de datos tiene casi toda la lógica de negocio y expone los datos al resto de la app, y la de UI los muestra con Compose. Hay un repositorio aunque tenga una sola fuente de datos ([Recommendations, *Layered architecture*](../fuentes/android/architecture-recommendations.md)).
- Ni un composable ni un ViewModel usan directamente una fuente de datos, como DataStore, una API de Firebase o la ubicación: pasan por un repositorio ([Recommendations, *Layered architecture*](../fuentes/android/architecture-recommendations.md)).
- Un ViewModel expone el estado de la UI para que la UI lo observe, y recibe las acciones de la UI como llamadas a sus métodos ([Recommendations, *UI layer*](../fuentes/android/architecture-recommendations.md)).
- La UI recoge el estado con `collectAsStateWithLifecycle` ([Recommendations, *UI layer*](../fuentes/android/architecture-recommendations.md)).
- Un ViewModel no le manda eventos a la UI: procesa el evento en el momento y lo refleja en el estado ([Recommendations, *UI layer*](../fuentes/android/architecture-recommendations.md)).
- La app navega entre pantallas y atiende los deep links con Navigation 3 ([Recommendations, *UI layer*](../fuentes/android/architecture-recommendations.md)).
- Un ViewModel extiende `ViewModel`, y no `AndroidViewModel`, y no guarda referencias a tipos del ciclo de vida ([Recommendations, *ViewModel*](../fuentes/android/architecture-recommendations.md)).
- Un ViewModel recibe los datos con flows de Kotlin y hace sus acciones con funciones suspendidas, en `viewModelScope` ([Recommendations, *ViewModel*](../fuentes/android/architecture-recommendations.md)).
- Solo una pantalla tiene ViewModel. Un componente de UI reutilizable maneja su complejidad con una clase de estado simple, que su llamador puede elevar ([Recommendations, *ViewModel*](../fuentes/android/architecture-recommendations.md)).
- Un ViewModel expone su estado en una sola propiedad `uiState`, un `StateFlow`, o en una por cada dato sin relación con los demás. Si el estado sale de un flow de otra capa, se crea con `stateIn` y `SharingStarted.WhileSubscribed(5_000)` ([Recommendations, *ViewModel*](../fuentes/android/architecture-recommendations.md)).
- Ninguna `Activity` sobrescribe un método de su ciclo de vida, como `onResume`, para una tarea de UI: un composable usa `LifecycleStartEffect` o `LifecycleResumeEffect` para el trabajo síncrono, y `repeatOnLifecycle` para el asíncrono ([Recommendations, *Lifecycle*](../fuentes/android/architecture-recommendations.md)).
- Hay un repositorio por tipo de dato. Cada fuente de datos trabaja con una sola fuente, como un archivo, la red o una base local ([Data layer, *Data layer architecture*](../fuentes/android/data-layer.md)).
- La capa de datos expone una función suspendida para cada operación puntual y un flow para cada dato que cambia con el tiempo ([Data layer, *Expose APIs*](../fuentes/android/data-layer.md)).
- El nombre de una fuente de datos no dice cómo guarda el dato, como `UserSharedPreferencesDataSource` ([Data layer, *Naming conventions in this guide*](../fuentes/android/data-layer.md)).
- Una fuente de datos que recibe datos que no coinciden con lo que espera el resto de la app los pasa a un modelo propio ([Data layer, *Represent business models*](../fuentes/android/data-layer.md)).
- Una operación que tiene que sobrevivir a la muerte del proceso, como terminar una subida, va con WorkManager ([Data layer, *Business-oriented operations*](../fuentes/android/data-layer.md)).
- La capa de datos señala un fallo con una excepción, propia si es un error conocido, y no con un `Result` ([Data layer, *Expose errors*](../fuentes/android/data-layer.md)).

## Corrutinas

Estándar: las [buenas prácticas de corrutinas](../fuentes/android/coroutines-best-practices.md) de Android.

- Una clase recibe por inyección los `Dispatchers` que usa, y no los escribe en el código ([Best practices for coroutines, *Inject Dispatchers*](../fuentes/android/coroutines-best-practices.md)).
- Una función suspendida se puede llamar desde el hilo principal: la clase que hace un trabajo bloqueante lo saca de él con `withContext` ([Best practices for coroutines, *Suspend functions should be safe to call from the main thread*](../fuentes/android/coroutines-best-practices.md)).
- Un ViewModel lanza las corrutinas de la lógica de negocio, en vez de exponer funciones suspendidas, y la UI lanza solo las de la lógica de UI ([Best practices for coroutines, *The ViewModel should create coroutines*](../fuentes/android/coroutines-best-practices.md)).
- Un trabajo de la capa de datos que solo vale mientras el usuario está en la pantalla sigue al llamador, con `coroutineScope` o `supervisorScope`. Uno que vale mientras la app está abierta usa un `CoroutineScope` externo, que recibe por inyección y que maneja una clase que vive más que la pantalla ([Best practices for coroutines, *Creating coroutines in the business and data layer*](../fuentes/android/coroutines-best-practices.md)).
- Ninguna clase usa `GlobalScope` ([Best practices for coroutines, *Avoid GlobalScope*](../fuentes/android/coroutines-best-practices.md)).
- Una corrutina que hace trabajo bloqueante en un bucle comprueba la cancelación en cada vuelta, como con `ensureActive()` ([Best practices for coroutines, *Make your coroutine cancellable*](../fuentes/android/coroutines-best-practices.md)).
- Una corrutina de `viewModelScope` atrapa las excepciones que pueden ocurrir, de los tipos concretos, como `IOException`, y no `Exception` ni `Throwable`. Un `CancellationException` no se atrapa, o se relanza ([Best practices for coroutines, *Watch out for exceptions*](../fuentes/android/coroutines-best-practices.md)).

## Inyección de dependencias

Estándares: las [recomendaciones de arquitectura](../fuentes/android/architecture-recommendations.md) y [Hilt](../fuentes/android/hilt.md), de Android.

- Una clase recibe sus dependencias en el constructor, con `@Inject` ([Recommendations, *Handle dependencies*](../fuentes/android/architecture-recommendations.md)).
- Hilt genera su código con KSP, y Java y Kotlin compilan para Java 17, el que piden Compose y Hilt ([Hilt, *Adding dependencies*](../fuentes/android/hilt.md)).
- Una interfaz se provee con `@Binds`, en un módulo `abstract`, y un tipo que no es propio o que se arma con un builder, con `@Provides`, en un módulo `object` ([Hilt, *Hilt modules*](../fuentes/android/hilt.md), [*Inject interface instances with @Binds*](../fuentes/android/hilt.md) e [*Inject instances with @Provides*](../fuentes/android/hilt.md)).
- Si un tipo tiene un binding con calificador, todos sus bindings lo llevan ([Hilt, *Provide multiple bindings for the same type*](../fuentes/android/hilt.md)).
- Un binding no tiene alcance, salvo el que guarda un estado que se comparte, necesita sincronización o es caro de crear según una medición ([Hilt, *Component scopes*](../fuentes/android/hilt.md)).
- Un ViewModel lleva `@HiltViewModel`, y la pantalla lo obtiene con `hiltViewModel()` ([Hilt, *Inject dependencies in classes not supported by Hilt*](../fuentes/android/hilt.md)).
- Dagger se usa solo a través de Hilt ([Hilt, *Hilt and Dagger*](../fuentes/android/hilt.md)).

## Compose

Estándar: el [estado](../fuentes/compose/state.md) de Compose.

- Un composable recibe solo los datos que muestra, y no el objeto entero que los contiene. Si son demasiados parámetros, van agrupados en una clase.
- Un estado que tiene que sobrevivir a un cambio de configuración se guarda con `rememberSaveable`, y `remember` solo para el que basta que sobreviva a la recomposición ([State and Jetpack Compose, *State in composables*](../fuentes/compose/state.md)).
- Un objeto mutable que Compose no observa, como un `ArrayList` o una data class mutable, no es estado: el estado es un `State` con un valor inmutable, como el de `listOf()` ([State and Jetpack Compose, *State in composables*](../fuentes/compose/state.md)).
- Un tipo observable que no es `State` se convierte en `State` dentro de un composable antes de leerlo ([State and Jetpack Compose, *Other supported types of state*](../fuentes/compose/state.md)).
- Un composable sin estado recibe el valor y un evento para cambiarlo, como `value` y `onValueChange`, o un evento más concreto. El estado sube al menos hasta el ancestro común de quienes lo leen y hasta el nivel más alto donde cambia, y dos estados que cambian con los mismos eventos suben juntos ([State and Jetpack Compose, *State hoisting*](../fuentes/compose/state.md)).
- Un valor de `rememberSaveable` que no cabe en un `Bundle` se vuelve `Parcelable` con `@Parcelize`, o, si no sirve, se guarda con `mapSaver` o `listSaver` ([State and Jetpack Compose, *Ways to store state*](../fuentes/compose/state.md)).

## Accesibilidad

Contrato: [transversal.md](transversal.md#accesibilidad).

- Cada pantalla tiene una prueba de UI que llama a `enableAccessibilityChecks()`.

## Almacenamiento

Estándar: la [capa de datos](../fuentes/android/data-layer.md) de Android.

- Lo sensible, como el token de refresco que pide [autenticacion.md](autenticacion.md#sesión), va en DataStore, cifrado con una clave AES-GCM del proveedor `AndroidKeyStore`. [Android Keystore](https://developer.android.com/privacy-and-security/keystore)
- Lo sensible va en su propio DataStore, que `data_extraction_rules.xml` excluye de la copia en la nube y de la transferencia entre dispositivos, y `backup_rules.xml`, de la copia de un dispositivo con la API 30 o menor, que no lee `data_extraction_rules.xml`: sin la clave, otro dispositivo no lo descifra. [Auto Backup](https://developer.android.com/identity/data/autobackup)
- Cada archivo de DataStore tiene una sola instancia por proceso, creada una vez en el nivel superior de su archivo de Kotlin con el delegado `preferencesDataStore`.
- Las preferencias, un conjunto pequeño de datos que solo se lee y se reemplaza, van en Preferences DataStore ([Data layer, *Save and retrieve data from disk*](../fuentes/android/data-layer.md)).
- Las preferencias relacionadas van en el mismo DataStore, y cada parte de la app tiene el suyo ([Data layer, *DataStore as a data source*](../fuentes/android/data-layer.md)).

## Código por SMS

Contrato: [autenticacion.md](autenticacion.md#código-por-sms).

- El `BroadcastReceiver` se registra en tiempo de ejecución, mientras la pantalla del código está abierta.
- El `BroadcastReceiver` se registra con el permiso `SmsRetriever.SEND_PERMISSION`, y la app no declara ese permiso.

## Contraseñas

Contrato: [autenticacion.md](autenticacion.md#contraseñas).

- Los gestores de contraseñas completan los campos por el `contentType` de su semántica: al entrar, `ContentType.Username` en el del correo o el teléfono y `ContentType.Password` en el de la contraseña, y al elegir una contraseña, `ContentType.NewPassword`. [Autofill in Compose](https://developer.android.com/develop/ui/compose/text/autofill)

## Errores

Contrato: [transversal.md](transversal.md#errores).

- La fuente de datos de red traduce una `HttpException` a la excepción tipada del sobre que pide [transversal.md](transversal.md#errores).

## Idiomas

Estándar: [*Localize your app*](../fuentes/android/localization.md) de Android.

Contrato: [transversal.md](transversal.md#idiomas).

- `androidResources` lleva `generateLocaleConfig = true`, y `res/resources.properties`, `unqualifiedResLocale=es`: el usuario elige el idioma de la app en los ajustes del sistema. [Per-app language preferences](https://developer.android.com/guide/topics/resources/app-languages)
- Un interceptor de OkHttp manda en `Accept-Language` el primer idioma de `LocaleManagerCompat.getApplicationLocales()` o, si el usuario no eligió uno para la app, el primero de `LocaleManagerCompat.getSystemLocales()`.
- Los recursos por defecto, sin calificadores, como `res/values/` y `res/drawable/`, tienen todo lo que usa la app, y uno de un idioma puede tener solo una parte ([Localize your app, *Why default resources are important*](../fuentes/android/localization.md) y [*Design your app to work in any locale*](../fuentes/android/localization.md)).
- Ningún texto va escrito en el código: todos son recursos de `strings.xml`, también el de una imagen con texto, y Compose los lee con `stringResource` ([Localize your app, *Move all strings into strings.xml*](../fuentes/android/localization.md)).
- Los textos usan la terminología estándar de Android, como la barra de la app o las notificaciones ([Localize your app, *Follow Android guidelines for UI strings*](../fuentes/android/localization.md)).
- Cada texto de `strings.xml` lleva un comentario con su contexto: para qué es, dónde aparece y cuánto espacio tiene ([Localize your app, *Provide sufficient context for declared strings*](../fuentes/android/localization.md)).
- Lo que no se traduce dentro de un texto, como un marcador, un símbolo o un nombre, va en `<xliff:g>` con `id` y, si la app lo reemplaza, `example` ([Localize your app, *Mark message parts that aren't to be translated*](../fuentes/android/localization.md)).

## Mapas

Contrato: [transversal.md](transversal.md#mapas).

- El mapa de MapLibre Android va dentro de Compose con `AndroidView`.

## OpenAPI y clientes

Contrato: [transversal.md](transversal.md#openapi-y-clientes).

- openapi-generator genera desde `../server/openapi.json` los modelos del cable y las interfaces de Retrofit, con el generador `kotlin`, `library = "jvm-retrofit2"` y `serializationLibrary = "kotlinx_serialization"`, en `app/build/generated/openapi/`, que no se versiona. `preBuild` depende de `openApiGenerate`.
- Un esquema libre, como el de un objeto con `additionalProperties`, se genera como `JsonElement`, con `typeMappings` y su `importMappings`: con `Any`, el plugin de kotlinx.serialization hace fallar al compilador.
- El `Json` del convertidor de Retrofit suma los serializadores de `Serializer.kotlinxSerializationAdapters`, de lo generado, y deja `ignoreUnknownKeys` e `isLenient` en `false`, sus valores por defecto: el `Json` que genera openapi-generator los activa, y un campo desconocido tiene que fallar.

## Paginación

Contrato: [transversal.md](transversal.md#paginación).

- Una lista que se recorre con `nextPageToken` usa Paging 3, con un `PagingSource` que toma el `pageToken` como clave.
- El ViewModel expone el `PagingData` en su propio flow, fuera de `uiState`: no es inmutable.

## Pagos

Contrato: [transversal.md](transversal.md#pagos).

- Con Stripe, la hoja de pago es `PaymentSheet` del SDK de Stripe para Android.

## Passkeys

Estándares: [*Create a passkey*](../fuentes/android/create-passkeys.md), [*Sign in with a passkey*](../fuentes/android/sign-in-with-passkeys.md) y los [requisitos de Credential Manager](../fuentes/android/credential-manager-prerequisites.md) de Android.

Contrato: [autenticacion.md](autenticacion.md#passkeys).

- El manifiesto declara el `meta-data` `asset_statements`, y el recurso `asset_statements`, con `translatable="false"`, incluye `https://<dominio>/.well-known/assetlinks.json` ([Prerequisites, *Update the app's manifest*](../fuentes/android/credential-manager-prerequisites.md) y [*Configure Digital Asset Links for passwords*](../fuentes/android/credential-manager-prerequisites.md)).
- `minSdk` no baja de la API 28 ([Create a passkey, *Prerequisites*](../fuentes/android/create-passkeys.md)).
- La app crea la passkey con un `CreatePublicKeyCredentialRequest` cuyo `requestJson` son las opciones del servidor, y `preferImmediatelyAvailableCredentials` en `false`: la app la crea cuando lo pide el usuario ([Create a passkey, *Create a passkey*](../fuentes/android/create-passkeys.md)).
- Cada subclase de `CreateCredentialException` se maneja aparte ([Create a passkey, *Handle the response*](../fuentes/android/create-passkeys.md)).
- El login pide en un solo `GetCredentialRequest` la passkey, con un `GetPublicKeyCredentialOption`, y la contraseña guardada, con un `GetPasswordOption` ([Sign in with a passkey, *Create the object required to get the public key credential*](../fuentes/android/sign-in-with-passkeys.md)).
- `getCredential` recibe un `MutableContextWrapper` de la `Activity` en primer plano ([Sign in with a passkey, *Launch the sign-in flow*](../fuentes/android/sign-in-with-passkeys.md)).
- Cada subclase de `GetCredentialException` se maneja aparte ([Sign in with a passkey, *Handle exceptions*](../fuentes/android/sign-in-with-passkeys.md)).

## Push

Estándar: [*Notification runtime permission*](../fuentes/android/notification-permission.md) de Android.

Contrato: [transversal.md](transversal.md#push).

- La app recibe push con `firebase-messaging`, en un `FirebaseMessagingService`.
- Toda notificación va en un canal, y hay un canal por cada tipo de notificación.
- El manifiesto declara `com.google.firebase.messaging.default_notification_channel_id`: FCM manda a ese canal el mensaje que no nombra uno. [Firebase Cloud Messaging](https://firebase.google.com/docs/cloud-messaging/android/client)
- Los ajustes de la app tienen una entrada que abre los ajustes del sistema de cada canal, con `Settings.ACTION_CHANNEL_NOTIFICATION_SETTINGS`.
- La app pide el permiso de notificaciones tras una acción del usuario que deja claro para qué sirven, y no al arrancar. Explica antes por qué lo pide solo si `shouldShowRequestPermissionRationale()` devuelve `true` ([Notification runtime permission, *Wait to show notification permission prompt*](../fuentes/android/notification-permission.md) y [*Request the permission in context*](../fuentes/android/notification-permission.md)).
- El permiso se pide con `rememberLauncherForActivityResult` y el contrato `ActivityResultContracts.RequestPermission()` ([Notification runtime permission, *Request the permission*](../fuentes/android/notification-permission.md)).
- Antes de mostrar una notificación, la app comprueba `areNotificationsEnabled()` ([Notification runtime permission, *Check whether your app can send notifications*](../fuentes/android/notification-permission.md)).

## Reintentos

Contrato: [transversal.md](transversal.md#reintentos).

- El `OkHttpClient` lleva `retryOnConnectionFailure(false)`: por defecto, OkHttp vuelve a mandar un `POST` ya enviado si se cae la conexión que tomó del pool. [OkHttp 5.5.1](https://raw.githubusercontent.com/square/okhttp/parent-5.5.1/okhttp/src/commonJvmAndroid/kotlin/okhttp3/internal/http/RetryAndFollowUpInterceptor.kt)
- Los reintentos que pide [transversal.md](transversal.md#reintentos) los hace un interceptor de OkHttp.

## Tema

> **En desarrollo; no se implementa:** [transversal.md](transversal.md#tema).

Contrato: [transversal.md](transversal.md#tema).

- El `ColorScheme` claro y el oscuro son `LightColorScheme` y `DarkColorScheme`, generados en `ui/theme/Colors.kt`. El modo sale de la elección del usuario, guardada en Preferences DataStore, y con «sistema», de `isSystemInDarkTheme()`.
- Los tamaños van en `ui/theme/`, sin tamaños literales fuera de él.

## Versión mínima de cliente

Contrato: [transversal.md](transversal.md#versión-mínima-de-cliente).

- Un interceptor de OkHttp pone el `User-Agent` de pieza en cada petición: sin él, OkHttp manda `okhttp/<versión>`. [OkHttp 5.5.1](https://raw.githubusercontent.com/square/okhttp/parent-5.5.1/okhttp/src/commonJvmAndroid/kotlin/okhttp3/internal/http/BridgeInterceptor.kt)
- La versión vive solo en `versionName`, y el interceptor la lee de `BuildConfig.VERSION_NAME`, con `buildConfig = true` en `buildFeatures`.

## WebSocket

Contrato: [transversal.md](transversal.md#websocket) y [autenticacion.md](autenticacion.md#websocket).

- El WebSocket va por `newWebSocket` del mismo `OkHttpClient` de las peticiones: el handshake lleva el `User-Agent` y `Authorization` de sus interceptores.

## Pruebas

Estándares: las [recomendaciones de arquitectura](../fuentes/android/architecture-recommendations.md), las [buenas prácticas de corrutinas](../fuentes/android/coroutines-best-practices.md) y la [capa de datos](../fuentes/android/data-layer.md) de Android.

- Las pruebas de UI son instrumentadas, y CI las corre en el dispositivo administrado por Gradle `pixel6`, con `device = "Pixel 6"`, `apiLevel` en la API de `targetSdk` de [stack.md](../stack.md#android), `systemImageSource = "aosp-atd"` y `testedAbi = "x86_64"`: AGP avisa que su valor por defecto pasa a `arm64-v8a`, que esa imagen no corre.
- Las llamadas HTTP se prueban contra MockWebServer ([Data layer, *Integration tests*](../fuentes/android/data-layer.md)).
- Cada ViewModel, con sus flows, cada repositorio y cada fuente de datos tienen pruebas unitarias, y CI corre pruebas de la navegación de la UI ([Recommendations, *Testing*](../fuentes/android/architecture-recommendations.md)).
- Las pruebas usan fakes, y no mocks ([Recommendations, *Testing*](../fuentes/android/architecture-recommendations.md)).
- Una prueba de un `StateFlow` comprueba su `value` ([Recommendations, *Testing*](../fuentes/android/architecture-recommendations.md)).
- Una prueba inyecta un `TestDispatcher` que comparte el planificador de `runTest`, y reemplaza `Dispatchers.Main` con `Dispatchers.setMain` para `viewModelScope` ([Best practices for coroutines, *Inject TestDispatchers in tests*](../fuentes/android/coroutines-best-practices.md) e [*Inject Dispatchers*](../fuentes/android/coroutines-best-practices.md)).

## Entrega

Estándar: las [recomendaciones de arquitectura](../fuentes/android/architecture-recommendations.md) de Android.

Contrato: [transversal.md](transversal.md#distribución).

- La versión se compila con `./gradlew bundleRelease` y se firma con la llave de subida que nombra `key.properties`, que git ignora. [Sign your app](https://developer.android.com/studio/publish/app-signing)
- El número de build es el `versionCode` de `defaultConfig`, en `app/build.gradle.kts`.
- La versión de release lleva `isShrinkResources = true`.
- La versión de release activa R8 en su modo completo, con `isMinifyEnabled = true` ([Recommendations, *Performance*](../fuentes/android/architecture-recommendations.md)).

## Cumplimiento

| Convención | Herramienta |
| :--- | :--- |
| `MaxMetaspaceSize=2g` | [scripts/verificar.py](../scripts/verificar.py) |
| `.editorconfig` igual al de la plantilla | [scripts/verificar.py](../scripts/verificar.py) |
| `gradle-wrapper.properties` igual al de la plantilla | [scripts/verificar.py](../scripts/verificar.py) |
| Todo paquete que importa el código está declarado, y toda dependencia declarada se usa | `./gradlew buildHealth` en CI |
| El formato de ktlint con `android_studio` | `./gradlew ktlintCheck` en CI |
| *Non-empty blocks*, *Indentation*, *One statement per line*, *Functions* y *Horizontal* | `curly-spacing`, `keyword-spacing`, `indent`, `no-semi`, `statement-wrapping`, `function-signature`, `parameter-list-wrapping`, `op-spacing`, `comma-spacing`, `colon-spacing`, `double-colon-spacing`, `range-spacing`, `comment-spacing`, `paren-spacing` y `unary-op-spacing` de ktlint |
| *Package Names* | `package-name` de ktlint |
| *Unit return type* | `no-unit-return` de ktlint |
