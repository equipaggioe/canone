# Java

Una pieza en Java que acompaña al servidor en la máquina: un servicio que solo llama el servidor, por loopback, como el comparador de huellas de un producto que usa una biblioteca de la JVM. No es un servidor aparte: no tiene base, ni archivos, ni host propio.

## Proyecto

- La pieza corre con `openjdk-21-jre-headless`, el JRE de Debian 13 que instala `packages.py --java`, y se compila con `javac --release 21`. Compilada para otra versión, la pieza no arranca o usa una API que el JRE de la máquina no tiene.
- La pieza es una carpeta en la raíz del repositorio, y su nombre es el de su unidad, `<app>-java@<pieza>.service`, y el de su jar: `install.py`, `deploy.py` y quien despliega la encuentran por ese nombre, sin otra configuración.
- `dependencies.txt` lleva cada dependencia de ejecución en una línea, `grupo:artefacto:versión` y el SHA-256 de su jar de Maven Central: un jar cambiado en el camino entraría a la máquina sin que nadie lo note. La pieza no tiene Gradle ni Maven, y las dependencias transitivas se escriben a mano.
- `scripts/java.py <pieza> <clase> <salida>` baja cada dependencia a `<salida>/<pieza>/lib/` y falla, sin escribirla, si su SHA-256 es otro; compila `src/` y escribe `<salida>/<pieza>/<pieza>.jar`, con `Main-Class` y el `Class-Path` de `lib/`. Lo corren el `release.yml` del repositorio y quien desarrolla, con el mismo resultado.
- El `release.yml` compila la pieza en `debian:trixie`, con `openjdk-21-jdk-headless`, el mismo JDK del JRE que la corre, y el artefacto la lleva en `<pieza>/`. Quien despliega reconoce la pieza por la línea de `scripts/java.py` del `release.yml` y la pasa a `install.py --java`.
- La pieza escucha solo en loopback, en un puerto fijo del código, y el servidor la llama a esa dirección, una constante suya: abierta a la red, cualquiera usaría un servicio que no autentica.
- La unidad que corre la pieza está en [despliegue.md](despliegue.md#procesos).

```text
<pieza>/
  .gitignore            build/
  dependencies.txt
  src/
    <Clase>.java
```

Plantilla: [plantilla/scripts/java.py](../plantilla/scripts/java.py), el paso de Java del `release.yml` de [plantilla/.github/workflows/](../plantilla/.github/workflows/) y la unidad `PRODUCTO-java@.service` de [plantilla/infra/](../plantilla/infra/).

## Cumplimiento

| Convención | Herramienta |
| :--- | :--- |
| Que el jar corre con sus dependencias de `lib/`, y que `java.py` no escribe una dependencia cuyo SHA-256 no es el de `dependencies.txt` | [scripts/infra/java-build.sh](../scripts/infra/java-build.sh), en [.github/workflows/infra.yml](../.github/workflows/infra.yml) de Canone |
