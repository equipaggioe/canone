# ADR-0147 · Una pieza en Java corre en su unidad, con el JRE de Debian 13, y se compila con sus dependencias fijadas por SHA-256

- **Estado:** Aceptada en los puntos 1 a 4, que pidió el usuario (2026-11-13). Los puntos 5 a 8 son *(propuesta)*: se eligieron al construir. El punto 7 lo reemplaza el [ADR-0173](0173-una-pieza-en-java-se-compila-con-el-jdk-del-ci-sin-advertencias-y-el-servidor-la-prueba-corriendo.md)
- **Fecha:** 2026-11-13
- **Alcance:** [`plataformas/java.md`](../plataformas/java.md); [`plataformas/despliegue.md`](../plataformas/despliegue.md), «Máquina», «Procesos» y «Versiones»; `packages.py`, `install.py`, `deploy.py` y `PRODUCTO-java@.service` de `plantilla/infra/`; `plantilla/scripts/java.py` y el `release.yml` de la plantilla

## Contexto

presenze compara huellas con SourceAFIS, una biblioteca de la JVM, en un servicio de Java que
solo llama su servidor por loopback. canone solo sabía correr el servidor de Python: el servicio
no tenía unidad, paquete ni lugar en el artefacto, y en la máquina el enrolamiento y el login con
imagen de huella respondían 503.

Comprobado el 2026-11-13 y el 2026-11-14, con systemd 257, `openjdk-21-jre-headless` y
`openjdk-21-jdk-headless` 21.0.13+9-1~deb13u2 de Debian 13:

- La unidad de la pieza queda con una exposición de 0.9 en `systemd-analyze security`. Con
  `MemoryDenyWriteExecute=yes`, la JVM no arranca: termina con 1.
- Con `IPAddressDeny=any` e `IPAddressAllow=localhost`, la pieza responde en loopback y una conexión
  suya a 1.1.1.1:80 no sale.
- Sin `SuccessExitStatus=143`, detener la unidad la deja `failed`, porque la JVM termina con 143.
- `scripts/infra/java.sh` pasa entero en una Debian 13 arrancada con `systemd-nspawn`, y
  `scripts/infra/java-build.sh` en Debian 13.
- presenze `v0.0.4` corre su comparador en `presenze-java@server-fingerprint.service` en un VPS
  con Debian 13: responde en `127.0.0.1:8091` y SourceAFIS 3.18.1 saca la plantilla de una
  captura real.

## Decisión

1. **Una pieza en Java es una carpeta en la raíz del repositorio, y corre en la unidad
   `<app>-java@<pieza>.service`**, que `install.py --java <pieza>` instala y habilita. Sin
   `--java`, la unidad no se instala.
2. **Corre con `openjdk-21-jre-headless`, el JRE de Debian 13**, que instala `packages.py --java`.
3. **El artefacto lleva el jar de la pieza, compilado por el CI**, y `deploy.py` la reinicia antes
   que el servidor, en cada versión y al volver a la anterior.
4. **La unidad solo alcanza loopback** (`IPAddressDeny=any`, `IPAddressAllow=localhost`) y lleva
   el aislamiento de las demás, salvo `MemoryDenyWriteExecute=`: el JIT escribe el código que
   corre.
5. *(propuesta)* **La unidad usa `DynamicUser=`**: la pieza no guarda estado ni tiene
   credenciales.
6. *(propuesta)* **Las dependencias van en `<pieza>/dependencies.txt`, cada una con el SHA-256 de
   su jar de Maven Central**, y `scripts/java.py` falla sin escribirla si el SHA-256 es otro. La
   pieza no tiene Gradle ni Maven.
7. *(propuesta)* **El `release.yml` compila la pieza en `debian:trixie`, con
   `openjdk-21-jdk-headless`**, y Consola la reconoce por su línea de `scripts/java.py`.
8. *(propuesta)* **`SuccessExitStatus=143`**: la JVM termina así cuando systemd la detiene.

## Consecuencias

- El puerto de la pieza es una constante de su código y del servidor que la llama: canone no lo
  asigna.
- Agregar una dependencia es escribir su línea con su SHA-256, y sus dependencias transitivas a
  mano.
- La exposición de la unidad queda en 0.9 en `systemd-analyze security`, debajo del 2.0 que pide
  «Procesos».
- El eje de servicios de Consola todavía no ofrece la unidad (30 de Consola).

## Descartado

- **Correr el código fuente con `java Archivo.java`**, como en desarrollo: compila en cada
  arranque y no se comprueba en el CI.
- **Gradle o Maven en la pieza**: resolverían las dependencias transitivas, pero agregan una
  herramienta y su caché para un servicio de pocas clases.
- **Un mecanismo para servicios auxiliares de cualquier lenguaje**: Java es el único que lo pide,
  y cada runtime trae lo suyo, como el JIT.
- **Instalar el servicio a mano en la máquina**: lo que deja un cambio permanente en la máquina lo
  hace un programa de canone.
