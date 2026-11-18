# Java

Una pieza en Java que acompaña al servidor en la máquina: un servicio que solo llama el servidor, por loopback. No es un servidor aparte: no tiene base, ni archivos, ni host propio.

## Proyecto

- La pieza es una carpeta en la raíz del repositorio. Su nombre es el de su jar y la instancia de su unidad, `<app>-java@<pieza>.service`.
- `dependencies.txt` lleva cada dependencia de ejecución, también las transitivas, en una línea: `grupo:artefacto:versión` y el SHA-256 de su jar de Maven Central. La pieza no tiene Gradle ni Maven.
- `scripts/java.py` compila la pieza con `--release` de la versión de Java de [stack.md](../stack.md#java).
- La unidad que corre la pieza está en [despliegue.md](despliegue.md#procesos).

```text
<pieza>/
  .gitignore            build/
  dependencies.txt
  src/
    <Clase>.java
  build/<pieza>/        lo que escribe java.py fuera del release
    <pieza>.jar         con Main-Class y el Class-Path de lib/
    lib/                cada jar de dependencies.txt
```

Plantilla: [plantilla/scripts/java.py](../plantilla/scripts/java.py), los pasos de Java del job `server` de `ci.yml` y del job `artifact` de `release.yml`, en [plantilla/.github/workflows/](../plantilla/.github/workflows/), y la unidad `PRODUCTO-java@.service` de [plantilla/infra/](../plantilla/infra/).

## Código

- `javac` compila con `-Xlint:all,-serial -Werror`.
- El código lleva el formato de google-java-format, en la versión de [stack.md](../stack.md#java).

## Red

- La pieza escucha solo en loopback, en un puerto fijo de su código, y el servidor la llama en esa dirección, una constante suya.

## Pruebas

- Cada llamada del servidor a la pieza tiene una prueba del servidor que la hace contra la pieza corriendo, que el job `server` del CI compila y arranca antes de pytest. Las demás pruebas pueden reemplazarla.

## Entrega

- El `release.yml` compila cada pieza con `scripts/java.py <pieza> <Clase> dist`, con el JDK de [stack.md](../stack.md#java).

## Cumplimiento

| Convención | Herramienta |
| :--- | :--- |
| `scripts/java.py` igual al de la plantilla | [scripts/verificar.py](../scripts/verificar.py) |
| Que el `release.yml` compila cada carpeta de la raíz con `dependencies.txt`, y que el `ci.yml` la compila y la arranca | [scripts/verificar.py](../scripts/verificar.py) |
| Que el jar que compila `java.py` con el JDK de stack.md corre en el JRE de Debian 13 con sus dependencias de `lib/`; que una advertencia, salvo `serial`, o un `.java` sin el formato de google-java-format hacen fallar la compilación, y que `java.py` no escribe una dependencia cuyo SHA-256 no es el de `dependencies.txt` | [scripts/infra/java-build.sh](../scripts/infra/java-build.sh), en [.github/workflows/infra.yml](../.github/workflows/infra.yml) de Canone |
| El código de cada pieza, sin advertencias y con el formato de google-java-format | El paso de `java.py` del job `server` del `ci.yml` de cada repositorio |
