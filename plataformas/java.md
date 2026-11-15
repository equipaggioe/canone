# Java

Una pieza en Java que acompaña al servidor en la máquina: un servicio que solo llama el servidor, por loopback, como el comparador de huellas de un producto que usa una biblioteca de la JVM. No es un servidor aparte: no tiene base, ni archivos, ni host propio.

## Proyecto

- La pieza corre con `openjdk-21-jre-headless`, el JRE de Debian 13 que instala `packages.py --java`, y se compila con `javac --release 21`. Compilada para otra versión, la pieza no arranca o usa una API que el JRE de la máquina no tiene.
- La pieza es una carpeta en la raíz del repositorio, y su nombre es el de su unidad, `<app>-java@<pieza>.service`, y el de su jar: `install.py`, `deploy.py` y Consola la encuentran por ese nombre, sin otra configuración.
- `dependencies.txt` lleva cada dependencia de ejecución en una línea, `grupo:artefacto:versión` y el SHA-256 de su jar de Maven Central: un jar cambiado en el camino entraría a la máquina sin que nadie lo note. La pieza no tiene Gradle ni Maven, y las dependencias transitivas se escriben a mano.
- `scripts/java.py <pieza> <clase> <salida>` baja cada dependencia a `<salida>/<pieza>/lib/` y falla, sin escribirla, si su SHA-256 es otro; compila `src/` y escribe `<salida>/<pieza>/<pieza>.jar`, con `Main-Class` y el `Class-Path` de `lib/`. Lo corren el `release.yml` del repositorio y quien desarrolla, con el mismo resultado.
- El `release.yml` compila la pieza en `debian:trixie`, con `openjdk-21-jdk-headless`, el mismo JDK del JRE que la corre, y el artefacto la lleva en `<pieza>/`. Consola reconoce la pieza por la línea de `scripts/java.py` del `release.yml` y la pasa a `install.py --java`.

```text
<pieza>/
  .gitignore            build/
  dependencies.txt
  src/
    <Clase>.java
```

Plantilla: [plantilla/scripts/java.py](../plantilla/scripts/java.py), el paso de Java del `release.yml` de [plantilla/.github/workflows/](../plantilla/.github/workflows/) y la unidad `PRODUCTO-java@.service` de [plantilla/infra/](../plantilla/infra/).

## Proceso

- La pieza escucha solo en loopback, en un puerto fijo del código, y el servidor la llama a esa dirección, una constante suya: abierta a la red, cualquiera usaría un servicio que no autentica.
- La unidad corre `java -jar /srv/<app>/current/<pieza>/<pieza>.jar` con `DynamicUser=`: la pieza no guarda estado ni tiene credenciales, y una cuenta fija sería una cuenta más que mantener.
- La unidad solo alcanza loopback, con `IPAddressDeny=any` e `IPAddressAllow=localhost`: una pieza comprometida no llama a otra máquina.
- La unidad lleva el aislamiento de las demás salvo `MemoryDenyWriteExecute=`: con él, la JVM no arranca, porque su JIT escribe el código que corre ([ADR-0147](../adr/0147-una-pieza-en-java-corre-en-su-unidad-con-el-jre-de-debian.md)).
- `SuccessExitStatus=143`: la JVM termina con 128 más SIGTERM cuando systemd la detiene, y sin eso la unidad queda `failed` en cada despliegue.
- `deploy.py` reinicia cada pieza antes que el servidor, en cada versión y al volver a la anterior: el servidor nunca llama a una pieza de otra versión.

## Cumplimiento

| Convención | Herramienta |
| :--- | :--- |
| Que la pieza arranca con su jar, responde en loopback, solo alcanza localhost, se detiene sin fallar y queda con una exposición de 2.0 o menos | Una pieza de prueba en el systemd de Debian 13, con [scripts/infra/java.sh](../scripts/infra/java.sh), en [.github/workflows/infra.yml](../.github/workflows/infra.yml) de Canone |
| Que `install.py --java` instala y habilita la unidad, que sin `--java` no la instala, que `deploy.py` la reinicia y que `uninstall.py` la borra | [scripts/infra/java.sh](../scripts/infra/java.sh) |
| Que el jar corre con sus dependencias de `lib/`, y que `java.py` no escribe una dependencia cuyo SHA-256 no es el de `dependencies.txt` | [scripts/infra/java-build.sh](../scripts/infra/java-build.sh), en [.github/workflows/infra.yml](../.github/workflows/infra.yml) de Canone |
