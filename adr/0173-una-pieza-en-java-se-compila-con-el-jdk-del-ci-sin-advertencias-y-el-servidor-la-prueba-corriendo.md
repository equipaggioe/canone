# ADR-0173 · Una pieza en Java se compila con el JDK del CI, sin advertencias y con google-java-format, y el servidor la prueba corriendo

- **Estado:** Aceptada. Los puntos 1 a 5 los pidió el usuario al revisar `java.md`, y el 6 y el 7 los confirmó al arreglar los defectos de esa revisión (2026-11-17)
- **Fecha:** 2026-11-17
- **Alcance:** [`plataformas/java.md`](../plataformas/java.md); [`stack.md`](../stack.md), «Java»; `plantilla/scripts/java.py`, el `ci.yml` y el `release.yml` de la plantilla; `scripts/infra/java-build.sh`, `java.sh` e `infra.yml`; `scripts/verificar.py`

## Contexto

La revisión de `java.md` encontró que el `ci.yml` de la plantilla no compilaba la pieza, así que un
error recién aparecía al publicar; que `java.py` fallaba al correr dos veces sobre la misma
salida, y que las pruebas de presenze reemplazaban `afis.template` y `afis.score`: ninguna llamaba
al comparador.

Comprobado el 2026-11-17 en Debian 13.5, con Temurin 25.0.5+8 y `openjdk-21-jre-headless`
21.0.13:

- `javac` 25.0.5 con `--release 21` escribe clases de la versión 65, la de Java 21. El comparador
  de presenze, compilado así, corre en el JRE de Debian y responde `/health`, `/template` y
  `/score`.
- Con `-Xlint:all -Werror`, el comparador solo falla por `serial`: una excepción suya no declara
  `serialVersionUID`.
- google-java-format 2.0.0 corre en el JDK 25 y en el JRE 21, y `Afis.java` no tenía su formato.
- `scripts/infra/java-build.sh` pasa entero con ese JDK y ese JRE.

## Decisión

1. **El CI y el release compilan con el JDK de `actions/setup-java` de stack.md**, no en
   `debian:trixie` con `openjdk-21-jdk-headless`: `--release` ya fija la API del JRE que corre la
   pieza. Reemplaza el punto 7 del [ADR-0147](0147-una-pieza-en-java-corre-en-su-unidad-con-el-jre-de-debian.md).
2. **`javac` compila con `-Xlint:all,-serial -Werror`.** `serial` queda fuera porque la pieza no
   serializa objetos con `java.io`.
3. **El código lleva el formato de google-java-format**: `java.py` falla si un `.java` no lo
   tiene, y `java.py --format <pieza>` se lo da.
4. **Cada llamada del servidor a la pieza tiene una prueba contra la pieza corriendo**, que el job
   `server` del CI compila y arranca antes de pytest.
5. **La salida de `java.py` fuera del release es `<pieza>/build/`**, la que ignora su
   `.gitignore`.
6. **`java.py` borra `<salida>/<pieza>/` antes de compilar**: otra corrida sobre la misma salida
   no falla, y en `lib/` no queda una dependencia que `dependencies.txt` ya no nombra.
7. **`java.py` falla si `<salida>/<pieza>/` es la pieza o la contiene**: borrarla borraría su
   código.

## Consecuencias

- El release ya no instala paquetes de Debian en un contenedor, y la pieza compila con el mismo
  JDK en el CI, en el release y con Android.
- Cada compilación baja google-java-format de Maven Central, con su SHA-256 fijo en `java.py`.
- `java.sh` compila su pieza fuera de la máquina, como el release, y la máquina recibe el JRE de
  `packages.py --java`.
- Quien despliega sigue encontrando la pieza por la línea `scripts/java.py <pieza>` del
  `release.yml`.

## Descartado

- **Compilar con el JDK 21 de Debian**, en un contenedor: hace lo mismo que `--release` e instala
  paquetes en cada release.
- **`-Xlint:all` con `serial`**: pide un `serialVersionUID` en cada excepción, y nadie las
  serializa.
- **Error Prone**: agrega una herramienta, con sus dependencias transitivas a mano, para un
  servicio de pocas clases.
- **La Google Java Style como fuente**: el formateador la hace cumplir entera, así que daría una
  sola convención, y no cumple «Aporta» de `plataformas/README.md`.
- **JUnit en la pieza**: pide el console launcher y compilar las pruebas aparte, y no prueba que el
  servidor y la pieza se entiendan.
- **Que `java.py` falle si la salida ya existe**: obliga a borrarla a mano antes de cada
  compilación.
- **Compilar en una carpeta temporal y moverla al terminar**, para que una compilación que falla
  deje la anterior: el CI y el release se detienen igual ante el fallo, así que esa garantía no
  evita ningún síntoma.
