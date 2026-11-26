# Las versiones de Java en CI

Tema pendiente: **sin decidir**. El JDK 25.0.5 construye y no corre en el servidor, y por eso sigue
la última LTS; la pieza en Java corre en el servidor con el JRE 21 de Debian 13.

## Estado (verificado 2026-11-26)

| Pieza | Estado |
| :--- | :--- |
| Fila «JDK» de [stack.md](../stack.md#java) y de Android | 25.0.5. Que es la última LTS porque no corre en el servidor solo lo dicen los ADR 0119 y 0169 |
| Job `server` de `plantilla/.github/workflows/ci.yml` | Compila la pieza con el JDK 25 de `setup-java`, y pytest la arranca con ese mismo `java`: se prueba en el 25 lo que en producción corre en el 21 |
| `scripts/infra/java-build.sh`, en `infra.yml` de Canone | Comprueba que el jar corre en `openjdk-21-jre-headless` |
| Job `flet-mobile` de `plantilla/.github/workflows/release.yml` | No usa `setup-java`: `flet build aab` construye con el JDK que trae el runner, y `stack.md` no lo fija |

## Qué hay que decidir

- Escribir en la fila del JDK de `stack.md` que es la última LTS porque no corre en el servidor.
- Que el job `server` arranque la pieza con el Java 21: `verificar.py` pide hoy un solo `java-version`
  por workflow y busca `java -jar` en `ci.yml`.
- Qué JDK usa `flet-mobile`: el Gradle que genera Flet 1.1.3, con AGP 8.13.2, no se probó con el 25.
