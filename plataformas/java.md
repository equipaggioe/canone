# Java

Una pieza en Java que acompaña al servidor en la máquina: un servicio que solo llama el servidor, por loopback, como el comparador de huellas de un producto que usa una biblioteca de la JVM. No es un servidor aparte: no tiene base, ni archivos, ni host propio.

## Proyecto

- Java 21: la pieza corre con `openjdk-21-jre-headless`, el JRE de Debian 13 que instala `packages.py --java`, y se compila con `javac --release 21`.

```text
<pieza>/
  .gitignore            build/
  dependencies.txt
  src/
    <Clase>.java
```

Plantilla: [plantilla/scripts/java.py](../plantilla/scripts/java.py) y la unidad `PRODUCTO-java@.service` de [plantilla/infra/](../plantilla/infra/).

- La pieza es una carpeta en la raíz del repositorio, y su nombre es el de su unidad, `<app>-java@<pieza>.service`, y el de su jar.
- `dependencies.txt` lleva cada dependencia de ejecución en una línea, `grupo:artefacto:versión` y el SHA-256 de su jar de Maven Central: la pieza no tiene Gradle ni Maven, y la lista no se resuelve sola.
- `scripts/java.py <pieza> <clase> <salida>` baja cada dependencia a `<salida>/<pieza>/lib/` y falla, sin escribirla, si su SHA-256 es otro; compila `src/` y escribe `<salida>/<pieza>/<pieza>.jar`, con `Main-Class` y el `Class-Path` de `lib/`. Lo corren el `release.yml` del repositorio y quien desarrolla, con el mismo resultado.
- El `release.yml` compila la pieza en `debian:trixie`, con `openjdk-21-jdk-headless`, y el artefacto la lleva en `<pieza>/`. Consola reconoce la pieza por la línea de `scripts/java.py` del `release.yml` y la pasa a `install.py --java`.

## Proceso

- La pieza escucha solo en loopback, en un puerto fijo del código, y el servidor la llama a esa dirección, una constante suya.
- La unidad corre `java -jar /srv/<app>/current/<pieza>/<pieza>.jar` con `DynamicUser=`: la pieza no guarda estado ni tiene credenciales.
- La unidad solo alcanza loopback: `IPAddressDeny=any` y `IPAddressAllow=localhost`. La pieza no llama a nadie.
- La unidad no lleva `MemoryDenyWriteExecute=`, la única opción del aislamiento de las demás unidades que le falta: el JIT de la JVM escribe el código que corre.
- `SuccessExitStatus=143`: la JVM termina con 128 más SIGTERM cuando systemd la detiene, y sin eso la unidad queda `failed` en cada despliegue.
- `deploy.py` reinicia cada pieza antes que el servidor, en cada versión y al volver a la anterior: corren siempre la misma versión.

## Cumplimiento

| Convención | Herramienta |
| :--- | :--- |
| Que la pieza arranca con su jar, responde en loopback, no sale a otra dirección y queda con una exposición de 2.0 o menos | Una pieza de prueba en el systemd de Debian 13, con [scripts/infra/java.sh](../scripts/infra/java.sh), en [.github/workflows/infra.yml](../.github/workflows/infra.yml) de Canone, y `systemd-analyze security` del job `exposure` |
| Que `install.py --java` instala y habilita la unidad, que sin `--java` no la instala, y que `deploy.py` la reinicia | [scripts/infra/java.sh](../scripts/infra/java.sh) |
| Que `java.py` no escribe un jar cuyo SHA-256 no es el de `dependencies.txt` | [scripts/infra/java.sh](../scripts/infra/java.sh) |
