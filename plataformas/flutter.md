# Flutter

> **En desarrollo; no se implementa:** [README.md](README.md#en-desarrollo).

Una app en Flutter.

## Proyecto

- La app sale en Android y en iOS.
- Flutter 3.47.9, con Dart 3.13.7.
- `pubspec.yaml` declara exactos flutter_riverpod 3.5.0, riverpod 3.5.0 y riverpod_annotation 4.0.8, y en `dev_dependencies`, riverpod_generator 4.0.10: las mutations de Riverpod son experimentales y pueden cambiar sin una versión mayor. [Riverpod 3.5.0](https://raw.githubusercontent.com/rrousselGit/riverpod/flutter_riverpod-v3.5.0/website/docs/concepts2/mutations.mdx)
- `pubspec.yaml` declara exactos o con `^` shared_preferences 2.5.6, flutter_secure_storage 11.2.0, flutter_appauth 13.0.0, go_router 18.1.4, http 1.6.0, freezed_annotation 3.1.0, json_annotation 4.12.0, sms_autofill 2.6.1 y, con Stripe, flutter_stripe 14.2.0, y en `dev_dependencies`, flutter_lints 6.0.0, freezed 4.0.3, json_serializable 6.15.2, build_runner 2.17.1 y swagger_parser 2.1.1.
- Gradle, AGP y Kotlin son los de [android.md](android.md#proyecto), con su `gradle-wrapper.properties` en `android/gradle/wrapper/`. AGP y Kotlin se declaran en `android/settings.gradle.kts`.
- `analysis_options.yaml` declara el plugin riverpod_lint 3.2.0.
- Lo que genera build_runner, `*.g.dart` y `*.freezed.dart`, y lo que genera swagger_parser, en `lib/data/services/api/`, no se versiona, y CI revisa el formato antes de generarlo: riverpod_generator no escribe con líneas de 99.
- `analysis_options.yaml` excluye del análisis `lib/data/services/api/`: lo que genera swagger_parser no pasa las reglas de «Nombres» ni de «Estilo».
- `analysis_options.yaml` excluye del análisis `build/`, `android/` e `ios/`: si falta la exclusión, `flutter pub get` y `flutter analyze` la agregan, y la copia deja de ser la canónica. [Flutter 3.47.9](https://raw.githubusercontent.com/flutter/flutter/3.47.9/packages/flutter_tools/lib/src/migrations/analysis_options_migration.dart)

```text
<pieza>/
  pubspec.yaml
  pubspec.lock
  analysis_options.yaml
  swagger_parser.yaml
  lib/
    main.dart
    config/
    routing/          el GoRouter y sus rutas
    data/
      repositories/
      services/       el cliente de la API
        api/          lo que genera swagger_parser
    domain/
      models/         los modelos con freezed
    ui/
      core/
        themes/       el tema claro y el oscuro
      <función>/
        view_models/
        widgets/
  test/
```

Plantilla: [plantilla/flutter/](../plantilla/flutter/): `analysis_options.yaml`, con el analizador, sus reglas y el ancho de `dart format`, que se copia sin editar, y `.gitignore`.

## Estilo

Estándares: de Effective Dart, [*Style*](../fuentes/dart/effective-dart-style.md) y [*Usage*](../fuentes/dart/effective-dart-usage.md).

- El analizador incluye la [lista de flutter_lints](https://raw.githubusercontent.com/flutter/packages/flutter_lints-v6.0.0/packages/flutter_lints/lib/flutter.yaml), y CI corre `dart analyze --fatal-infos`: un aviso de nivel info también rompe CI, y `flutter analyze` no corre los plugins del analizador, como riverpod_lint.
- Las líneas tienen hasta 99 caracteres, el `page_width` de `dart format`, salvo una URI o una ruta dentro de un comentario o de una cadena, y una cadena de varias líneas: es el ancho de las demás páginas.
- El código cumple *DO follow a consistent rule for `var` and `final` on local variables* con `final` en toda variable local que no se reasigna, también la de un `for`-`in` y la de un patrón, y `var` en la que se reasigna ([Usage, *DO follow a consistent rule for `var` and `final` on local variables*](../fuentes/dart/effective-dart-usage.md)).
- El código cumple *PREFER using interpolation to compose strings and values*, *AVOID using curly braces in interpolation when not needed* y *AVOID using `Iterable.forEach()` with a function literal* ([Usage, *PREFER using interpolation to compose strings and values*](../fuentes/dart/effective-dart-usage.md), [*AVOID using curly braces in interpolation when not needed*](../fuentes/dart/effective-dart-usage.md) y [*AVOID using `Iterable.forEach()` with a function literal*](../fuentes/dart/effective-dart-usage.md)).
- Una variable que necesita saber si ya se inicializó no es `late`: es nullable y se compara con `null` o, si `null` es un valor válido, lleva un booleano aparte ([Usage, *AVOID `late` variables if you need to check whether they are initialized*](../fuentes/dart/effective-dart-usage.md)).
- `cast()` se usa solo si la colección no puede crearse con su tipo, castear cada elemento al recorrerla ni copiarse con `List<T>.from()`: es perezoso y revisa el tipo en cada operación ([Usage, *AVOID using `cast()`*](../fuentes/dart/effective-dart-usage.md)).
- Una clase no guarda lo que puede calcular de sus otros campos, salvo la caché de un cálculo lento, con un comentario que la explica ([Usage, *AVOID storing what you can calculate*](../fuentes/dart/effective-dart-usage.md)).
- Una propiedad que el código de fuera lee y no asigna es un campo `final`, salvo que la clase la reasigne fuera del constructor ([Usage, *PREFER using a `final` field to make a read-only property*](../fuentes/dart/effective-dart-usage.md)).
- El código cumple *DO format your code using `dart format`* y *DO use curly braces for all flow control statements* ([Style, *DO format your code using `dart format`*](../fuentes/dart/effective-dart-style.md) y [*DO use curly braces for all flow control statements*](../fuentes/dart/effective-dart-style.md)).
- El código cumple *DON'T explicitly initialize variables to `null`*, *DON'T use an explicit default value of `null`*, *DO use adjacent strings to concatenate string literals*, *DON'T use `.length` to see if a collection is empty*, *DO use `whereType()` to filter a collection by type*, *DO use a function declaration to bind a function to a name*, *DON'T create a lambda when a tear-off will do*, *DON'T wrap a field in a getter and setter unnecessarily*, *DON'T use `this.` except to redirect to a named constructor or to avoid shadowing*, *DO use initializing formals when possible*, *DO use `;` instead of `{}` for empty constructor bodies*, *DON'T use `new`* y *DON'T use `const` redundantly* ([Usage, *DON'T explicitly initialize variables to `null`*](../fuentes/dart/effective-dart-usage.md), [*DON'T use an explicit default value of `null`*](../fuentes/dart/effective-dart-usage.md), [*DO use adjacent strings to concatenate string literals*](../fuentes/dart/effective-dart-usage.md), [*DON'T use `.length` to see if a collection is empty*](../fuentes/dart/effective-dart-usage.md), [*DO use `whereType()` to filter a collection by type*](../fuentes/dart/effective-dart-usage.md), [*DO use a function declaration to bind a function to a name*](../fuentes/dart/effective-dart-usage.md), [*DON'T create a lambda when a tear-off will do*](../fuentes/dart/effective-dart-usage.md), [*DON'T wrap a field in a getter and setter unnecessarily*](../fuentes/dart/effective-dart-usage.md), [*DON'T use `this.` except to redirect to a named constructor or to avoid shadowing*](../fuentes/dart/effective-dart-usage.md), [*DO use initializing formals when possible*](../fuentes/dart/effective-dart-usage.md), [*DO use `;` instead of `{}` for empty constructor bodies*](../fuentes/dart/effective-dart-usage.md), [*DON'T use `new`*](../fuentes/dart/effective-dart-usage.md) y [*DON'T use `const` redundantly*](../fuentes/dart/effective-dart-usage.md)).
- Una expresión booleana que no admite `null` no se compara con `true` ni con `false`, y una que lo admite se evalúa con `??` o con `!= null` ([Usage, *DON'T use `true` or `false` in equality operations*](../fuentes/dart/effective-dart-usage.md)).
- Una lista, un mapa o un conjunto se crea con un literal, con `...`, `if` y `for` dentro si hace falta, y no con su constructor sin nombre ni agregando los elementos uno por uno ([Usage, *DO use collection literals when possible*](../fuentes/dart/effective-dart-usage.md)).
- Un iterable se copia con `toList()`, y `List.from()` se usa solo para cambiar el tipo de sus elementos ([Usage, *DON'T use `List.from()` unless you intend to change the type of the result*](../fuentes/dart/effective-dart-usage.md)).
- El tipo de una colección se fija en la operación que ya la transforma, como `List<T>.from()` o `map<T>()`, y no con un `cast()` al final ([Usage, *DON'T use `cast()` when a nearby operation will do*](../fuentes/dart/effective-dart-usage.md)).
- Un campo que no depende de los parámetros del constructor se inicializa en su declaración ([Usage, *DO initialize fields at their declaration when possible*](../fuentes/dart/effective-dart-usage.md)).
- Un campo no es `late` si puede inicializarse en la lista de inicialización del constructor ([Usage, *DON'T use `late` when a constructor initializer list will do*](../fuentes/dart/effective-dart-usage.md)).

## Comentarios

Estándar: [*Documentation*](../fuentes/dart/effective-dart-documentation.md) de Effective Dart.

- Un doc comment no repite lo que dicen la firma ni la clase que lo contiene: dice lo que el lector no sabe ([Documentation, *AVOID redundancy with the surrounding context*](../fuentes/dart/effective-dart-documentation.md)).
- El doc comment de una función o un método cuyo propósito es un efecto empieza con un verbo en tercera persona, como `Connects to the server` ([Documentation, *PREFER starting comments of a function or method with third-person verbs if its main purpose is a side effect*](../fuentes/dart/effective-dart-documentation.md)).
- El de una variable o una propiedad que no es booleana empieza con un sintagma nominal, y el de una booleana, con `Whether`. El de una función que sobre todo devuelve un valor se escribe como el de una propiedad ([Documentation, *PREFER starting a non-boolean variable or property comment with a noun phrase*](../fuentes/dart/effective-dart-documentation.md), [*PREFER starting a boolean variable or property comment with "Whether" followed by a noun or gerund phrase*](../fuentes/dart/effective-dart-documentation.md) y [*PREFER a noun phrase or non-imperative verb phrase for a function or method if returning a value is its primary purpose*](../fuentes/dart/effective-dart-documentation.md)).
- El de una biblioteca o un tipo empieza con un sintagma nominal, que describe una instancia ([Documentation, *PREFER starting library or type comments with noun phrases*](../fuentes/dart/effective-dart-documentation.md)).
- Un doc comment usa poco Markdown y nada de HTML, y sus bloques de código van entre tres acentos graves ([Documentation, *AVOID using markdown excessively*](../fuentes/dart/effective-dart-documentation.md), [*AVOID using HTML for formatting*](../fuentes/dart/effective-dart-documentation.md) y [*PREFER backtick fences for code blocks*](../fuentes/dart/effective-dart-documentation.md)).
- Un comentario es breve, no usa abreviaturas ni siglas que no sean obvias, como `e.g.`, y llama `this` a la instancia del miembro que documenta ([Documentation, *PREFER brevity*](../fuentes/dart/effective-dart-documentation.md), [*AVOID abbreviations and acronyms unless they are obvious*](../fuentes/dart/effective-dart-documentation.md) y [*PREFER using "this" instead of "the" to refer to a member's instance*](../fuentes/dart/effective-dart-documentation.md)).
- Un comentario se escribe como una oración: empieza con mayúscula, salvo que su primera palabra sea un identificador, y termina con punto, también un TODO ([Documentation, *DO format comments like sentences*](../fuentes/dart/effective-dart-documentation.md)).
- Un comentario usa `//`, y `/* */` solo comenta código por un tiempo ([Documentation, *DON'T use block comments for documentation*](../fuentes/dart/effective-dart-documentation.md)).
- Un miembro o un tipo se documenta con `///`, y no con `//` ni con `/** */` ([Documentation, *DO use `///` doc comments to document members and types*](../fuentes/dart/effective-dart-documentation.md)).
- Un doc comment empieza con una oración que lo resume, en su propio párrafo ([Documentation, *DO start doc comments with a single-sentence summary*](../fuentes/dart/effective-dart-documentation.md) y [*DO separate the first sentence of a doc comment into its own paragraph*](../fuentes/dart/effective-dart-documentation.md)).
- De una propiedad con getter y setter se documenta solo uno ([Documentation, *DON'T write documentation for both the getter and setter of a property*](../fuentes/dart/effective-dart-documentation.md)).
- Un doc comment nombra entre corchetes los identificadores que están al alcance, como `[StateError]` o `[Duration.inDays]` ([Documentation, *DO use square brackets in doc comments to refer to in-scope identifiers*](../fuentes/dart/effective-dart-documentation.md)).
- Los parámetros, el retorno y las excepciones se explican en prosa, sin etiquetas como `@param` ([Documentation, *DO use prose to explain parameters, return values, and exceptions*](../fuentes/dart/effective-dart-documentation.md)).
- El doc comment va antes de las anotaciones ([Documentation, *DO put doc comments before metadata annotations*](../fuentes/dart/effective-dart-documentation.md)).

## Tipos

Estándar: [*Design*](../fuentes/dart/effective-dart-design.md) de Effective Dart.

- El analizador activa `strict-casts`, `strict-inference` y `strict-raw-types`: los tipos se revisan como con Pyrefly en modo strict.
- El código cumple *AVOID writing incomplete generic types* y *PREFER using function type syntax for parameters* ([Design, *AVOID writing incomplete generic types*](../fuentes/dart/effective-dart-design.md) y [*PREFER using function type syntax for parameters*](../fuentes/dart/effective-dart-design.md)).
- Un tipo de función se anota con su firma, y no con `Function`, salvo el que acepta funciones de firmas distintas ([Design, *PREFER signatures in function type annotations*](../fuentes/dart/effective-dart-design.md)).
- Un tipo de función se escribe en línea, y un `typedef` se define solo para uno largo o que se repite ([Design, *PREFER inline function types over typedefs*](../fuentes/dart/effective-dart-design.md)).
- Lo que acepta cualquier valor es `Object?`, u `Object` si no admite `null`. `dynamic` va solo para desactivar la revisión de tipos, o con una API que ya lo usa, como el JSON ([Design, *AVOID using `dynamic` unless you want to disable static checking*](../fuentes/dart/effective-dart-design.md)).
- El código cumple *DO type annotate variables without initializers*, *DON'T type annotate initializing formals*, *DO annotate with `dynamic` instead of letting inference fail*, *DON'T specify a return type for a setter*, *DON'T use the legacy typedef syntax*, *DON'T redundantly type annotate initialized local variables* y *DON'T annotate inferred parameter types on function expressions* ([Design, *DO type annotate variables without initializers*](../fuentes/dart/effective-dart-design.md), [*DON'T type annotate initializing formals*](../fuentes/dart/effective-dart-design.md), [*DO annotate with `dynamic` instead of letting inference fail*](../fuentes/dart/effective-dart-design.md), [*DON'T specify a return type for a setter*](../fuentes/dart/effective-dart-design.md), [*DON'T use the legacy typedef syntax*](../fuentes/dart/effective-dart-design.md), [*DON'T redundantly type annotate initialized local variables*](../fuentes/dart/effective-dart-design.md) y [*DON'T annotate inferred parameter types on function expressions*](../fuentes/dart/effective-dart-design.md)).
- Un campo o una variable de nivel superior anota su tipo, salvo que su inicializador lo haga obvio, como un literal o la llamada a un constructor ([Design, *DO type annotate fields and top-level variables if the type isn't obvious*](../fuentes/dart/effective-dart-design.md)).
- Una función, un método o un getter que no es local anota su tipo de retorno y los de sus parámetros, también si sobrescribe a otro ([Design, *DO annotate return types on function declarations*](../fuentes/dart/effective-dart-design.md) y [*DO annotate parameter types on function declarations*](../fuentes/dart/effective-dart-design.md)).
- Una invocación genérica escribe sus argumentos de tipo solo si no se infieren ([Design, *DO write type arguments on generic invocations that aren't inferred*](../fuentes/dart/effective-dart-design.md) y [*DON'T write type arguments on generic invocations that are inferred*](../fuentes/dart/effective-dart-design.md)).

## Paquetes

Estándares: de Effective Dart, [*Style*](../fuentes/dart/effective-dart-style.md), [*Usage*](../fuentes/dart/effective-dart-usage.md) y [*Design*](../fuentes/dart/effective-dart-design.md).

- El código cumple *PREFER relative import paths* ([Usage, *PREFER relative import paths*](../fuentes/dart/effective-dart-usage.md)).
- Una declaración que no usa otra biblioteca es privada ([Design, *PREFER making declarations private*](../fuentes/dart/effective-dart-design.md)).
- El código cumple *DO use strings in `part of` directives*, *DON'T import libraries that are inside the `src` directory of another package* y *DON'T allow an import path to reach into or out of `lib`* ([Usage, *DO use strings in `part of` directives*](../fuentes/dart/effective-dart-usage.md), [*DON'T import libraries that are inside the `src` directory of another package*](../fuentes/dart/effective-dart-usage.md) y [*DON'T allow an import path to reach into or out of `lib`*](../fuentes/dart/effective-dart-usage.md)).
- El código cumple *DON'T explicitly name libraries* ([Style, *DON'T explicitly name libraries*](../fuentes/dart/effective-dart-style.md)).
- El código cumple *DO place `dart:` imports before other imports*, *DO place `package:` imports before relative imports*, *DO specify exports in a separate section after all imports* y *DO sort sections alphabetically* ([Style, *DO place `dart:` imports before other imports*](../fuentes/dart/effective-dart-style.md), [*DO place `package:` imports before relative imports*](../fuentes/dart/effective-dart-style.md), [*DO specify exports in a separate section after all imports*](../fuentes/dart/effective-dart-style.md) y [*DO sort sections alphabetically*](../fuentes/dart/effective-dart-style.md)).
- Una línea en blanco separa cada sección de imports y la de los `export` ([Style, *Ordering*](../fuentes/dart/effective-dart-style.md)).

## Nombres

Estándares: de Effective Dart, [*Style*](../fuentes/dart/effective-dart-style.md) y [*Design*](../fuentes/dart/effective-dart-design.md).

- El código cumple *PREFER using `lowerCamelCase` for constant names* ([Style, *PREFER using `lowerCamelCase` for constant names*](../fuentes/dart/effective-dart-style.md)).
- El parámetro que no usa una función anónima y local se llama `_` ([Style, *PREFER using wildcards for unused callback parameters*](../fuentes/dart/effective-dart-style.md)).
- La última palabra de un nombre es el sustantivo que mejor describe la cosa ([Design, *PREFER putting the most descriptive noun last*](../fuentes/dart/effective-dart-design.md)).
- Una propiedad o una variable que no es booleana se nombra con un sintagma nominal, y una booleana, con un verbo que no es imperativo, como `isEnabled`, `hasElements` o `canClose` ([Design, *PREFER a noun phrase for a non-boolean property or variable*](../fuentes/dart/effective-dart-design.md) y [*PREFER a non-imperative verb phrase for a boolean property or variable*](../fuentes/dart/effective-dart-design.md)).
- Una booleana lleva el nombre positivo, como `isEnabled` y no `isDisabled`, salvo que casi todo uso la niegue ([Design, *PREFER the "positive" name for a boolean property or variable*](../fuentes/dart/effective-dart-design.md)).
- Una función o un método cuyo propósito es un efecto se nombra con un verbo imperativo, y uno que sobre todo devuelve un valor, con un sintagma nominal o un verbo que no es imperativo, como `elementAt()` ([Design, *PREFER an imperative verb phrase for a function or method whose main purpose is a side effect*](../fuentes/dart/effective-dart-design.md) y [*PREFER a noun phrase or non-imperative verb phrase for a function or method if returning a value is its primary purpose*](../fuentes/dart/effective-dart-design.md)).
- Ninguna función ni método empieza por `get`: es un getter, o lleva un verbo más preciso, como `fetch` o `calculate` ([Design, *AVOID starting a function or method name with `get`*](../fuentes/dart/effective-dart-design.md)).
- Un método que copia el estado del objeto en uno nuevo se llama `to…()`, y uno que devuelve otra representación del mismo objeto, `as…()` ([Design, *PREFER naming a method `to___()` if it copies the object's state to a new object*](../fuentes/dart/effective-dart-design.md) y [*PREFER naming a method `as___()` if it returns a different representation backed by the original object*](../fuentes/dart/effective-dart-design.md)).
- El nombre de una función no describe sus parámetros, salvo para distinguirla de otra parecida que recibe otros tipos ([Design, *AVOID describing the parameters in the function's or method's name*](../fuentes/dart/effective-dart-design.md)).
- El código cumple *DO name extensions using `UpperCamelCase`*, *DO name import prefixes using `lowercase_with_underscores`*, *DO name other identifiers using `lowerCamelCase`* y *DON'T use a leading underscore for identifiers that aren't private* ([Style, *DO name extensions using `UpperCamelCase`*](../fuentes/dart/effective-dart-style.md), [*DO name import prefixes using `lowercase_with_underscores`*](../fuentes/dart/effective-dart-style.md), [*DO name other identifiers using `lowerCamelCase`*](../fuentes/dart/effective-dart-style.md) y [*DON'T use a leading underscore for identifiers that aren't private*](../fuentes/dart/effective-dart-style.md)).
- Las clases, los enums, los typedefs y los parámetros de tipo se nombran en `UpperCamelCase`, también una clase que se usa como anotación ([Style, *DO name types using `UpperCamelCase`*](../fuentes/dart/effective-dart-style.md)).
- Los paquetes, los directorios y los archivos se nombran en `lowercase_with_underscores` ([Style, *DO name packages, directories, and source files using `lowercase_with_underscores`*](../fuentes/dart/effective-dart-style.md)).
- Una sigla o una abreviatura de más de dos letras se escribe como una palabra, como `Http` o `Uri`. Una de dos letras que en inglés va en mayúsculas queda en mayúsculas, como `ID` o `UI`, y al principio de un nombre en `lowerCamelCase` toda sigla va en minúsculas, como `httpConnection` ([Style, *DO capitalize acronyms and abbreviations longer than two letters like words*](../fuentes/dart/effective-dart-style.md)).
- Un nombre no lleva letras de prefijo, como la `k` de `kDefaultTimeout` ([Style, *DON'T use prefix letters*](../fuentes/dart/effective-dart-style.md)).
- Una misma cosa lleva el mismo nombre en todo el código, y el que ya usan el dominio o las bibliotecas, si existe ([Design, *DO use terms consistently*](../fuentes/dart/effective-dart-design.md)).
- Un parámetro de tipo se llama `E` si es el elemento de una colección, `K` y `V` si son la clave y el valor, `R` si es un tipo de retorno, y `T`, `S` o `U` si su sentido es obvio ([Design, *DO follow existing mnemonic conventions when naming type parameters*](../fuentes/dart/effective-dart-design.md)).

## Clases y funciones

Estándar: [*Design*](../fuentes/dart/effective-dart-design.md) de Effective Dart.

- Un callback es una función, y no una clase abstracta con un solo miembro ([Design, *AVOID defining a one-member abstract class when a simple function will do*](../fuentes/dart/effective-dart-design.md)).
- Una clase no tiene solo miembros estáticos, salvo la que agrupa constantes: lo que no pertenece a una clase va en el nivel superior ([Design, *AVOID defining a class that contains only static members*](../fuentes/dart/effective-dart-design.md)).
- Una clase no extiende otra que no está pensada para extenderse, ni implementa otra que no está pensada como interfaz ([Design, *AVOID extending a class that isn't intended to be subclassed*](../fuentes/dart/effective-dart-design.md) y [*AVOID implementing a class that isn't intended to be an interface*](../fuentes/dart/effective-dart-design.md)).
- Un tipo es un `mixin` o una `class`, y no una `mixin class` ([Design, *PREFER defining a pure `mixin` or pure `class` to a `mixin class`*](../fuentes/dart/effective-dart-design.md)).
- Un campo o una variable de nivel superior que no cambia es `final` ([Design, *PREFER making fields and top-level variables `final`*](../fuentes/dart/effective-dart-design.md)).
- Un método no simula una sobrecarga con pruebas de tipo en ejecución: cada operación tiene su método, salvo que quien llama no sepa qué tipo tiene ([Design, *AVOID using runtime type tests to fake overloading*](../fuentes/dart/effective-dart-design.md)).
- Un campo `late final` sin inicializador no es público ([Design, *AVOID public `late final` fields without initializers*](../fuentes/dart/effective-dart-design.md)).
- Un `Future`, un `Stream` o una colección que se devuelven no son nullables: la falta de datos es una colección vacía, un futuro de un tipo nullable o un stream sin eventos, salvo que `null` signifique otra cosa ([Design, *AVOID returning nullable `Future`, `Stream`, and collection types*](../fuentes/dart/effective-dart-design.md)).
- El código cumple *AVOID returning `this` from methods just to enable a fluent interface* y *AVOID positional boolean parameters* ([Design, *AVOID returning `this` from methods just to enable a fluent interface*](../fuentes/dart/effective-dart-design.md) y [*AVOID positional boolean parameters*](../fuentes/dart/effective-dart-design.md)).
- Si quien llama puede querer omitir un parámetro opcional y pasar uno posterior, los parámetros son nombrados, y no posicionales ([Design, *AVOID optional positional parameters if the user may want to omit earlier parameters*](../fuentes/dart/effective-dart-design.md)).
- Un parámetro que quien llama puede omitir es opcional, y no uno obligatorio que recibe un valor especial, como `null` o una cadena vacía ([Design, *AVOID mandatory parameters that accept a special "no argument" value*](../fuentes/dart/effective-dart-design.md)).
- Una clase mutable no define `==` ni `hashCode` ([Design, *AVOID defining custom equality for mutable classes*](../fuentes/dart/effective-dart-design.md)).
- El código cumple *DO override `hashCode` if you override `==`*, *DON'T define a setter without a corresponding getter* y *DON'T make the parameter to `==` nullable* ([Design, *DO override `hashCode` if you override `==`*](../fuentes/dart/effective-dart-design.md), [*DON'T define a setter without a corresponding getter*](../fuentes/dart/effective-dart-design.md) y [*DON'T make the parameter to `==` nullable*](../fuentes/dart/effective-dart-design.md)).
- Una clase que no está pensada para extenderse fuera de su biblioteca lo declara con `final`, `interface` o `sealed`, y una que no está pensada para implementarse, con `final`, `base` o `sealed` ([Design, *DO use class modifiers to control if your class can be extended*](../fuentes/dart/effective-dart-design.md) y [*DO use class modifiers to control if your class can be an interface*](../fuentes/dart/effective-dart-design.md)).
- Una operación sin argumentos ni efectos visibles, idempotente, cuyo resultado importa más que el trabajo y que no expone todo el estado del objeto es un getter ([Design, *DO use getters for operations that conceptually access properties*](../fuentes/dart/effective-dart-design.md)).
- Una operación que recibe un solo argumento, no devuelve nada, cambia el estado del objeto y es idempotente es un setter ([Design, *DO use setters for operations that conceptually change properties*](../fuentes/dart/effective-dart-design.md)).
- Un rango se recibe con un inicio inclusivo y un final exclusivo ([Design, *DO use inclusive start and exclusive end parameters to accept a range*](../fuentes/dart/effective-dart-design.md)).
- `==` es reflexivo, simétrico y transitivo ([Design, *DO make your `==` operator obey the mathematical rules of equality*](../fuentes/dart/effective-dart-design.md)).
## Async

Estándares: de Effective Dart, [*Usage*](../fuentes/dart/effective-dart-usage.md) y [*Design*](../fuentes/dart/effective-dart-design.md).

- Lo asíncrono se escribe con `async` y `await`, y no encadenando futuros ([Usage, *PREFER async/await over using raw futures*](../fuentes/dart/effective-dart-usage.md)).
- `Completer` se usa solo en una primitiva asíncrona nueva o para adaptar código asíncrono que no usa futuros ([Usage, *AVOID using Completer directly*](../fuentes/dart/effective-dart-usage.md)).
- `FutureOr<T>` no es el tipo de retorno de una función: va solo en una posición contravariante, como un parámetro o el retorno de un callback que se recibe ([Design, *AVOID using `FutureOr<T>` as a return type*](../fuentes/dart/effective-dart-design.md)).
- Una función es `async` solo si usa `await`, si devuelve un error con `throw` o si devuelve un valor que hay que envolver en un futuro ([Usage, *DON'T use `async` when it has no useful effect*](../fuentes/dart/effective-dart-usage.md)).
- Un `FutureOr<T>` cuyo `T` puede ser `Object` se distingue con `is Future<T>`, y no con `is T` ([Usage, *DO test for `Future<T>` when disambiguating a `FutureOr<T>` whose type argument could be `Object`*](../fuentes/dart/effective-dart-usage.md)).
- Un miembro asíncrono que no produce un valor devuelve `Future<void>`, o `void` si nadie necesita esperarlo ni manejar su fallo ([Design, *DO use `Future<void>` as the return type of asynchronous members that do not produce values*](../fuentes/dart/effective-dart-design.md)).

## Excepciones

Estándar: [*Usage*](../fuentes/dart/effective-dart-usage.md) de Effective Dart.

- Todo `catch` lleva `on`, salvo uno que pasa lo que atrapa con `rethrow`, `Completer.completeError`, `Future.error` o `FlutterError.reportError`: así no se traga nada. El `on` nombra los tipos de los fallos que maneja o, en el código que aísla a la app de cualquier fallo de ejecución, `Exception` ([Usage, *AVOID catches without `on` clauses*](../fuentes/dart/effective-dart-usage.md)).
- El código cumple *DO use `rethrow` to rethrow a caught exception* y *DON'T explicitly catch `Error` or types that implement it* ([Usage, *DO use `rethrow` to rethrow a caught exception*](../fuentes/dart/effective-dart-usage.md) y [*DON'T explicitly catch `Error` or types that implement it*](../fuentes/dart/effective-dart-usage.md)).
- Un `catch` que atrapa cualquier `Exception` hace algo con lo que atrapa: lo registra, lo muestra o lo relanza ([Usage, *DON'T discard errors from catches without `on` clauses*](../fuentes/dart/effective-dart-usage.md)).
- Un `Error` se lanza solo ante un error de programación, y un fallo de ejecución lanza una `Exception` u otro tipo ([Usage, *DO throw objects that implement `Error` only for programmatic errors*](../fuentes/dart/effective-dart-usage.md)).
## Arquitectura

Estándares: de Flutter, [*Common architecture concepts*](../fuentes/flutter/app-architecture-concepts.md), [*Guide to app architecture*](../fuentes/flutter/app-architecture-guide.md) y las [recomendaciones de arquitectura](../fuentes/flutter/architecture-recommendations.yml).

- HTTP va por `package:http`, en el servicio del cliente de la API.
- Los ViewModels son `AsyncNotifier` o `Notifier` de Riverpod: un provider que falta no compila, asignar `state` ya avisa a la vista, y `AsyncValue` obliga a tratar la carga y el error.
- Las dependencias llegan por inyección, con los providers de Riverpod, y ningún objeto es accesible de forma global. Un repositorio es un provider con `keepAlive: true`: guarda el estado de la sesión.
- Un Command es una `Mutation` de Riverpod, `static final` en su ViewModel: la vista la corre con `run`, que llama a un método del ViewModel, y muestra su estado con `ref.watch`.
- Un modelo de freezed es una `sealed class`: así no se extiende ni se implementa fuera de su biblioteca.
- freezed genera el JSON con json_serializable.
- Los modelos inmutables se generan con freezed: da igualdad, `copyWith` y JSON con menos código que built_value ([recomendaciones, *Use freezed or built_value to generate immutable data models.*](../fuentes/flutter/architecture-recommendations.yml)).
- Las acciones del usuario llegan al ViewModel por Commands: estandarizan cómo la UI le manda los eventos a la capa de datos ([recomendaciones, *Use `Commands` to handle events from user interaction.*](../fuentes/flutter/architecture-recommendations.yml)).
- La navegación usa go_router, con sus rutas en `routing/` ([recomendaciones, *app-structure*](../fuentes/flutter/architecture-recommendations.yml)).
- Cada clase lleva en su nombre el componente que representa, como `HomeViewModel`, `HomeScreen`, `UserRepository` o `ClientApiService`, y cada carpeta, el de los componentes que guarda. Los widgets compartidos van en `ui/core/` ([recomendaciones, *Use standardized naming conventions for classes, files and directories.*](../fuentes/flutter/architecture-recommendations.yml)).
- La app tiene una capa de datos, que expone los datos y tiene casi toda la lógica de negocio, y una de UI, que los muestra y recibe las acciones del usuario, con la lógica de UI y los widgets en clases separadas ([recomendaciones, *Use clearly defined data and UI layers.*](../fuentes/flutter/architecture-recommendations.yml)).
- La capa de datos se divide en repositorios y servicios ([recomendaciones, *Use the repository pattern in the data layer.*](../fuentes/flutter/architecture-recommendations.yml)).
- La capa de UI se divide en vistas, que son widgets, y ViewModels ([recomendaciones, *Use ViewModels and Views in the UI layer. (MVVM)*](../fuentes/flutter/architecture-recommendations.yml)).
- La única lógica de un widget son los `if` que muestran u ocultan algo según un flag o un campo nullable del ViewModel, la animación, el layout según el dispositivo y la navegación simple: lo demás es un método del ViewModel ([recomendaciones, *Do not put logic in widgets.*](../fuentes/flutter/architecture-recommendations.yml)).
- Los datos van solo de la capa de datos a la de UI, y las interacciones, de la UI a la capa de datos, que las procesa ([recomendaciones, *Use unidirectional data flow.*](../fuentes/flutter/architecture-recommendations.yml)).
- Los modelos de datos son inmutables ([recomendaciones, *Use immutable data models.*](../fuentes/flutter/architecture-recommendations.yml)).
- Cada repositorio es una clase abstracta, con una implementación por entorno ([recomendaciones, *Use abstract repository classes*](../fuentes/flutter/architecture-recommendations.yml)).
- Hay un repositorio por tipo de dato, y es la única clase que lo modifica ([Common architecture concepts, *Single source of truth*](../fuentes/flutter/app-architecture-concepts.md)).
- Un ViewModel recibe solo fuentes de datos, como repositorios, y expone solo datos listos para la vista y los Commands que la vista ejecuta ante una acción del usuario ([Common architecture concepts, *Extensibility*](../fuentes/flutter/app-architecture-concepts.md)).
- Cada vista tiene un ViewModel, y cada ViewModel, una vista ([Guide to app architecture, *UI layer*](../fuentes/flutter/app-architecture-guide.md)).
- Una vista recibe del ViewModel todos los datos que muestra ([Guide to app architecture, *Views*](../fuentes/flutter/app-architecture-guide.md)).
- Un repositorio no conoce a otro: los datos de dos repositorios se combinan en el ViewModel ([Guide to app architecture, *Repositories*](../fuentes/flutter/app-architecture-guide.md)).
- El estado que comparten varios ViewModels durante la sesión, como la sesión del usuario, vive en un repositorio ([Guide to app architecture, *Managing app-wide session state*](../fuentes/flutter/app-architecture-guide.md)).
- Un servicio envuelve una fuente de datos externa, como la API o una API de la plataforma, devuelve un `Future` o un `Stream` y no guarda estado. Hay un servicio por fuente de datos ([Guide to app architecture, *Services*](../fuentes/flutter/app-architecture-guide.md)).

## Estado

Estándares: de Riverpod, [*DO/DON'T*](../fuentes/riverpod/do_dont.mdx), [*Providers*](../fuentes/riverpod/providers.mdx), [*Refs*](../fuentes/riverpod/refs.mdx), [*Consumers*](../fuentes/riverpod/consumers.mdx), [*Automatic disposal*](../fuentes/riverpod/auto_dispose.mdx), [*ProviderContainers/ProviderScopes*](../fuentes/riverpod/containers.mdx) y [*About code generation*](../fuentes/riverpod/about_code_generation.mdx).

- El analizador corre riverpod_lint.
- El `ProviderScope` de la app y el de cada prueba llevan `retry: (_, _) => null`: Riverpod reintenta por defecto toda excepción de un provider, hasta 10 veces, y [transversal.md](transversal.md#reintentos) solo deja reintentar una petición idempotente ante un fallo de red, un 502, un 503 o un 504. [Riverpod 3.5.0](https://raw.githubusercontent.com/rrousselGit/riverpod/flutter_riverpod-v3.5.0/website/docs/concepts2/retry.mdx)
- Los providers se declaran con `@riverpod`, de riverpod_generator: la app ya genera código con freezed y json_serializable ([About code generation, *Should I use code generation?*](../fuentes/riverpod/about_code_generation.mdx)).
- Un widget que lee providers es un `ConsumerWidget`, o un `ConsumerStatefulWidget` si necesita un `State` ([Consumers, *Which one to use?*](../fuentes/riverpod/consumers.mdx)).
- Un provider se inicializa solo: ningún widget lo inicializa ([DO/DON'T, *AVOID initializing providers in a widget*](../fuentes/riverpod/do_dont.mdx)).
- El estado efímero, como el elemento seleccionado, un formulario, una animación o un controlador como `TextEditingController`, no va en un provider ([DO/DON'T, *AVOID using providers for Ephemeral state.*](../fuentes/riverpod/do_dont.mdx)).
- `ref.watch`, `ref.read` y `ref.listen` reciben un provider que se conoce al compilar, nunca uno que llega por parámetro ([DO/DON'T, *PREFER ref.watch/read/listen (and similar APIs) with statically known providers*](../fuentes/riverpod/do_dont.mdx)).
- Un provider es una variable final de nivel superior, nunca un campo de una clase ([DO/DON'T, *AVOID dynamically creating providers*](../fuentes/riverpod/do_dont.mdx)).
- Un provider con parámetros no lleva `keepAlive: true`: crearía un estado por cada combinación de parámetros ([Automatic disposal, *Enabling/disabling automatic disposal*](../fuentes/riverpod/auto_dispose.mdx)).
- Un provider representa una lectura: una escritura, como enviar un formulario, no va en la inicialización de un provider ([DO/DON'T, *DON'T perform side effects during the initialization of a provider*](../fuentes/riverpod/do_dont.mdx)).
- Un Notifier no tiene constructor: su lógica va en `build`, que nadie llama directamente ([Providers, *Creating a provider*](../fuentes/riverpod/providers.mdx)).
- `ref.read` se usa en respuesta a una acción del usuario, y nunca en lugar de `ref.watch` para reconstruir menos: para eso está `select` ([Refs, *Interacting with the provider's state inside user interactions*](../fuentes/riverpod/refs.mdx)).
- Fuera de `build`, un widget escucha un provider con `listenManual`, y no con `listen` ([Refs, *Ref.listen*](../fuentes/riverpod/refs.mdx)).
- El callback de `ref.onDispose` no causa efectos ni modifica providers ([Automatic disposal, *Reacting to state disposal*](../fuentes/riverpod/auto_dispose.mdx)).
- La app arranca con un `ProviderScope` en la raíz, y no usa `ProviderContainer` directamente ([ProviderContainers/ProviderScopes, *Using a ProviderScope for Flutter applications*](../fuentes/riverpod/containers.mdx)).

## Accesibilidad

Contrato: [transversal.md](transversal.md#accesibilidad).

- Cada pantalla tiene una prueba de widget con `androidTapTargetGuideline`, `labeledTapTargetGuideline` y una subclase de `MinimumTextContrastGuideline` cuyo `targetContrastRatio` devuelve 4.5: `textContrastGuideline` acepta 3:1 en el texto grande, y la subclase conserva su exención del texto de un componente inactivo. La guía de iOS pide 44 × 44, menos que la de Android. [Flutter 3.47.9](https://raw.githubusercontent.com/flutter/flutter/3.47.9/packages/flutter_test/lib/src/accessibility.dart)

## Almacenamiento

Estándares: el README de [shared_preferences](../fuentes/pub/shared_preferences/README.md) y el de [flutter_secure_storage](../fuentes/pub/flutter_secure_storage/README.md).

- El token de refresco que pide [autenticacion.md](autenticacion.md#sesión) va en flutter_secure_storage.
- Las preferencias usan `SharedPreferencesAsync`: sin caché, cada lectura trae el valor actual ([shared_preferences, *SharedPreferences vs SharedPreferencesAsync vs SharedPreferencesWithCache*](../fuentes/pub/shared_preferences/README.md) y [*Cache and async or sync getters*](../fuentes/pub/shared_preferences/README.md)).
- flutter_secure_storage usa `AndroidOptions()`, sin biometría: la app refresca la sesión sin pedirle nada al usuario ([flutter_secure_storage, *Encryption Options (Version 10.0.0+)*](../fuentes/pub/flutter_secure_storage/README.md)).
- En Android, `SharedPreferencesAsync` usa su backend por defecto, DataStore Preferences ([shared_preferences, *Android platform storage*](../fuentes/pub/shared_preferences/README.md)).
- shared_preferences no guarda datos críticos: no garantiza que una escritura llegue al disco ([shared_preferences, *Shared preferences plugin*](../fuentes/pub/shared_preferences/README.md)).
- Si `main` usa flutter_secure_storage antes de `runApp`, llama antes a `WidgetsFlutterBinding.ensureInitialized()` ([flutter_secure_storage, *Installation*](../fuentes/pub/flutter_secure_storage/README.md)).
- La copia de seguridad de Android no incluye los datos de flutter_secure_storage: restaurados en otro dispositivo, su clave no se puede recuperar ([flutter_secure_storage, *Disabling Auto Backup*](../fuentes/pub/flutter_secure_storage/README.md)).
- En iOS, los entitlements de debug y de release declaran `keychain-access-groups` ([flutter_secure_storage, *macOS & iOS*](../fuentes/pub/flutter_secure_storage/README.md)).

## Autenticación

Contrato: [autenticacion.md](autenticacion.md#código-de-autorización).

- La app hace el flujo del código de autorización con flutter_appauth, que usa AppAuth.

## Código por SMS

Contrato: [autenticacion.md](autenticacion.md#código-por-sms).

- El campo del código es `TextFieldPinAutoFill`: lleva una `InputDecoration`, y se ve como los demás campos del tema.

## Errores

Contrato: [transversal.md](transversal.md#errores).

## Fechas

Contrato: [transversal.md](transversal.md#fechas).

## Idiomas

Estándar: [*Internationalizing Flutter apps*](../fuentes/flutter/internationalization.md).

Contrato: [transversal.md](transversal.md#idiomas).

- Un `Locale` se crea con `Locale.fromSubtags`, que admite el script ([Internationalizing Flutter apps, *Set up an internationalized app with `flutter_localizations`*](../fuentes/flutter/internationalization.md)).
- `MaterialApp` declara los `localizationsDelegates` de `flutter_localizations` y sus `supportedLocales` ([Internationalizing Flutter apps, *Set up an internationalized app with `flutter_localizations`*](../fuentes/flutter/internationalization.md)).
- El proyecto de Xcode declara en *Localizations* los idiomas de la app: la App Store los muestra desde ahí ([Internationalizing Flutter apps, *Localizing for iOS: Updating the iOS app bundle*](../fuentes/flutter/internationalization.md)).

## Mapas

Contrato: [transversal.md](transversal.md#mapas).

## Montos

Contrato: [transversal.md](transversal.md#montos).

## OpenAPI y clientes

Contrato: [transversal.md](transversal.md#openapi-y-clientes).

- swagger_parser genera los modelos del cable y el cliente de la API desde `../server/openapi.json`, en `lib/data/services/api/`. `swagger_parser.yaml` lleva `serializer: freezed`, `http_client: http` y `page_width: 99`.
- Un modelo generado rechaza un campo y un valor de enum que no conoce: el OpenAPI del servidor declara `additionalProperties: false` en cada esquema ([fastapi.md](fastapi.md#esquemas)).

## Paginación

Contrato: [transversal.md](transversal.md#paginación).

## Pagos

Contrato: [transversal.md](transversal.md#pagos).

- Con Stripe, la hoja de pago es `PaymentSheet` de `flutter_stripe`.

## Push

Contrato: [transversal.md](transversal.md#push).

## Reintentos

Contrato: [transversal.md](transversal.md#reintentos).

## Sesión

Contrato: [autenticacion.md](autenticacion.md#sesión).

## Tema

> **En desarrollo; no se implementa:** [transversal.md](transversal.md#tema).

Contrato: [transversal.md](transversal.md#tema).

- El tema claro y el oscuro usan `lightColorScheme` y `darkColorScheme`, generados en `ui/core/themes/colors.dart`, y `themeMode` es `ThemeMode.system`.
- Los tamaños van en `ui/core/themes/`, sin tamaños literales fuera de él.

## Versión mínima de cliente

Contrato: [transversal.md](transversal.md#versión-mínima-de-cliente).

## WebSocket

Contrato: [transversal.md](transversal.md#websocket) y [autenticacion.md](autenticacion.md#websocket).

## Pruebas

Estándares: las [recomendaciones de arquitectura](../fuentes/flutter/architecture-recommendations.yml) de Flutter y [*ProviderContainers/ProviderScopes*](../fuentes/riverpod/containers.mdx) de Riverpod.

- Una prueba reemplaza cada repositorio por su fake con `overrideWithValue`, en el `ProviderScope` de una prueba de widget o en el `ProviderContainer.test` de una sin widgets.
- Cada servicio, repositorio y ViewModel tiene pruebas unitarias de cada uno de sus métodos, y cada vista, pruebas de widget, que prueban también la navegación y la inyección de dependencias ([recomendaciones, *Test architectural components separately, and together.*](../fuentes/flutter/architecture-recommendations.yml)).
- Las pruebas usan fakes, y el código recibe sus dependencias para poder reemplazarlas por ellos ([recomendaciones, *Make fakes for testing (and write code that takes advantage of fakes.)*](../fuentes/flutter/architecture-recommendations.yml)).
- Una prueba sin widgets usa `ProviderContainer.test`, que se libera al terminar, y no `ProviderContainer` ([ProviderContainers/ProviderScopes, *Using a ProviderContainer for pure Dart applications*](../fuentes/riverpod/containers.mdx)).

## Entrega

Contrato: [transversal.md](transversal.md#distribución).

- CI construye la app de iOS en macOS con `flutter build ios --no-codesign`: sin una Mac, es la única revisión del proyecto de Xcode.
- La versión de Android se compila con `flutter build appbundle --release` y se firma con la llave de subida que nombra `android/key.properties`, que git ignora. [Build and release an Android app](https://docs.flutter.dev/deployment/android)

## Cumplimiento

| Convención | Herramienta |
| :--- | :--- |
| Gradle, AGP y Kotlin | [scripts/verificar.py](../scripts/verificar.py) |
| Flutter en CI y los paquetes de «Proyecto» | [scripts/verificar.py](../scripts/verificar.py) |
| `analysis_options.yaml` igual al de la plantilla | [scripts/verificar.py](../scripts/verificar.py) |
| La lista de flutter_lints, riverpod_lint y los tipos estrictos | `dart analyze --fatal-infos` en CI |
| Las versiones exactas de Riverpod | [scripts/verificar.py](../scripts/verificar.py) |
| Un `ProviderScope` en la raíz del `runApp` | `missing_provider_scope` de riverpod_lint |
| *DO format your code using `dart format`* | `dart format --output=none --set-exit-if-changed` en CI |
| *DO use curly braces for all flow control statements* | `curly_braces_in_flow_control_structures` |
| *PREFER using interpolation to compose strings and values*, *AVOID using curly braces in interpolation when not needed* y *AVOID using `Iterable.forEach()` with a function literal* | `prefer_interpolation_to_compose_strings`, `unnecessary_brace_in_string_interps` y `avoid_function_literals_in_foreach_calls` |
| *DO follow a consistent rule for `var` and `final` on local variables*, con `final` | `prefer_final_locals` y `prefer_final_in_for_each` |
| Las partes de *Usage* que nombra «Estilo» | `avoid_init_to_null`, `prefer_adjacent_string_concatenation`, `prefer_is_empty`, `prefer_is_not_empty`, `prefer_iterable_whereType`, `prefer_function_declarations_over_variables`, `unnecessary_lambdas`, `unnecessary_getters_setters`, `unnecessary_this`, `prefer_initializing_formals`, `empty_constructor_bodies`, `unnecessary_new` y `unnecessary_const` |
| Ni `Map()` ni `Set()` sin nombre | `prefer_collection_literals` |
| *AVOID writing incomplete generic types* | `strict-raw-types` |
| *PREFER using function type syntax for parameters* | `use_function_type_syntax_for_parameters` |
| *DO type annotate variables without initializers* | `prefer_typing_uninitialized_variables` |
| *DON'T type annotate initializing formals*, *DON'T specify a return type for a setter* y *DON'T use the legacy typedef syntax* | `type_init_formals`, `avoid_return_types_on_setters` y `prefer_generic_function_type_aliases` |
| *DON'T redundantly type annotate initialized local variables* y *DON'T annotate inferred parameter types on function expressions* | `omit_local_variable_types` y `avoid_types_on_closure_parameters` |
| *DO annotate with `dynamic` instead of letting inference fail* | `strict-inference` y `strict_top_level_inference` |
| Los tipos de retorno y de parámetro de una función que no es local y no sobrescribe a otra | `strict_top_level_inference` |
| *DO use strings in `part of` directives*, *DON'T import libraries that are inside the `src` directory of another package* y *DON'T allow an import path to reach into or out of `lib`* | `use_string_in_part_of_directives`, `implementation_imports`, `avoid_relative_lib_imports` y el analizador, que no resuelve un import relativo que sale de `lib` |
| *PREFER relative import paths* | `prefer_relative_imports` |
| *DO place `dart:` imports before other imports*, *DO place `package:` imports before relative imports*, *DO specify exports in a separate section after all imports* y *DO sort sections alphabetically* | `directives_ordering` |
| *DON'T explicitly name libraries* | `unnecessary_library_name` |
| *PREFER using `lowerCamelCase` for constant names* | `constant_identifier_names` y `non_constant_identifier_names` |
| *DO name extensions using `UpperCamelCase`*, *DO name import prefixes using `lowercase_with_underscores`*, *DO name other identifiers using `lowerCamelCase`* y *DON'T use a leading underscore for identifiers that aren't private* | `camel_case_extensions`, `library_prefixes`, `non_constant_identifier_names`, `no_leading_underscores_for_local_identifiers` y `no_leading_underscores_for_library_prefixes` |
| Las clases, los enums y los typedefs en `UpperCamelCase` | `camel_case_types` |
| Los archivos `.dart` y el paquete en `lowercase_with_underscores` | `file_names` y `package_names` |
| *AVOID returning `this` from methods just to enable a fluent interface* y *AVOID positional boolean parameters* | `avoid_returning_this` y `avoid_positional_boolean_parameters` |
| *DO override `hashCode` if you override `==`*, *DON'T define a setter without a corresponding getter* y *DON'T make the parameter to `==` nullable* | `hash_and_equals`, `avoid_setters_without_getters` y el aviso `non_nullable_equals_parameter` del analizador |
| Un `catch` sin `on` que no pasa lo que atrapa con `rethrow`, `Completer.completeError`, `Future.error` o `FlutterError.reportError` | `avoid_catches_without_on_clauses` |
| *DO use `rethrow` to rethrow a caught exception* y *DON'T explicitly catch `Error` or types that implement it* | `use_rethrow_when_possible` y `avoid_catching_errors` |
