# Canone

Convenciones, plantillas y herramientas compartidas para construir, organizar y mantener proyectos de software.

**Canone no es una aplicación.** Es una serie de documentos que definen aplicaciones, y las convenciones que escribe para ellas no se aplican a Canone.

## Propósito

Los proyectos que usan Canone comparten sus convenciones y decisiones en un solo lugar para leerse, construirse, organizarse y mantenerse de la misma manera.

Canone está escrito para un asistente de IA: le dice con qué y cómo se construye cada proyecto, para no explicárselo en cada sesión. El desarrollador revisa aquí lo que el asistente va a leer.

Canone escribe decisiones: lo que tiene más de una forma que funciona. No escribe cómo funciona una tecnología, que el asistente ya sabe.

Lo que Canone escribe rige, y una herramienta lo comprueba cuando puede. Un repositorio se aparta de una convención solo con un ADR propio, en `docs/adr/`, que identifica la convención y explica el motivo, y su `docs/arquitectura/` describe lo que hace en su lugar. Si `scripts/verificar.py` comprueba esa convención, el ADR nombra el incumplimiento en «Se aparta de» ([documentacion.md](documentacion.md#formato)), y `verificar.py` y `copiar.py` lo respetan.

Cada proyecto elige las tecnologías que utiliza y consulta únicamente las convenciones correspondientes. Canone responde a la pregunta «si se usa X, ¿cómo se usa?», sin convertir su catálogo en una lista de requisitos universales.

Qué entra en una página, cómo se eligen sus fuentes y cómo se revisa está en [plataformas/README.md](plataformas/README.md).

Además de documentar las convenciones, proporciona plantillas y herramientas para incorporarlas a los repositorios y comprobar su cumplimiento. Cuando una convención exige una configuración o un mecanismo en una máquina, Canone proporciona también el programa que lo implementa. Las convenciones, sus plantillas y sus programas se mantienen sincronizados; solo instalándolos se prueba su funcionamiento en conjunto.

## Aplicación

Canone distingue entre convenciones generales y convenciones específicas de cada tecnología o ámbito.

Las siguientes convenciones aplican a todas las aplicaciones:

- [principios.md](principios.md)
- [repositorio.md](repositorio.md)
- [documentacion.md](documentacion.md)

Las convenciones de `plataformas/` dependen de las tecnologías utilizadas por cada proyecto. Qué páginas se leen para trabajar en una pieza está en [plataformas/README.md](plataformas/README.md), y qué se usa en cada plataforma y en qué versión, en [stack.md](stack.md).

## Principios

**Una convención tiene una única definición.**

Cada convención es adoptada de una fuente normativa o establecida como convención propia en la página correspondiente. Los demás documentos la referencian en lugar de reproducirla. Si la desviación de un repositorio demuestra ser una mejor solución general, se incorpora a Canone y sustituye la convención anterior cuando corresponda.

**Toda convención que pueda verificarse automáticamente debe tener una herramienta que la verifique o la imponga.**

La sección «Cumplimiento» de cada página registra las herramientas que verifican o imponen sus convenciones.

## Responsabilidades

Canone, cada repositorio y quien despliega tienen responsabilidades distintas y complementarias.

| Quién | Responsabilidades | Límites |
| :--- | :--- | :--- |
| **Canone** | Define las convenciones, proporciona las plantillas y establece la interfaz de sus programas mediante argumentos y `stdin`. | No guarda datos de las aplicaciones, no decide cuándo se ejecutan sus programas ni impone qué herramienta debe ejecutarlos. |
| **El repositorio** | Sigue las convenciones aplicables, incorpora las plantillas que se copian y declara sus propios datos: nombre, superficies y campos de `Settings`. | No reimplementa las plantillas canónicas ni define cómo se instalan las plantillas proporcionadas por Canone. |
| **Quien despliega** | Ejecuta los programas de Canone, manualmente o mediante la herramienta que elija, respetando sus interfaces. | No escribe lo que instalan esos programas, ni con unidades, configuración o scripts propios. |

### Configuración de cada despliegue

Los valores que cambian entre despliegues, sean secretos o no, no se incorporan al control de versiones. Cada repositorio declara los campos que necesita y quien despliega proporciona sus valores al servidor mediante la interfaz del programa correspondiente.

Por ejemplo, `install.py` recibe valores como el dominio y la memoria mediante argumentos, mientras que las credenciales se suministran mediante `credentials.py`.

Canone define cómo se reciben esos valores, pero no dónde los almacena quien despliega.

## Instrumentos

Canone tiene instrumentos propios: se construyen para servir a sus convenciones, y una página los nombra como nombra a Canone, sin una condición.

| Instrumento | Qué hace |
| :--- | :--- |
| **Equipaggio** | El servicio que usan las máquinas: el correo y el SMS de cada producto, el registro central del journal y el monitor de salud. Su API es la misma para todo despliegue, y cada uno entra con la clave de su cliente. |
| **Consola** | Una herramienta que corre los programas de Canone. No es obligatoria: quien despliega elige con qué los corre. |

## Documentación y recursos

El repositorio organiza sus convenciones, fuentes, decisiones, plantillas y herramientas en los siguientes archivos y directorios.

| Recurso | Contenido |
| :--- | :--- |
| [principios.md](principios.md) | Método de trabajo, independiente de las tecnologías utilizadas. |
| [repositorio.md](repositorio.md) | Convenciones de Git, estructura de carpetas, README y CI. |
| [documentacion.md](documentacion.md) | Estructura y mantenimiento de la documentación de cada repositorio. |
| [stack.md](stack.md) | Qué se usa en cada plataforma y en qué versión. Lo decide el desarrollador. |
| [plataformas/](plataformas/) | Metodología y catálogo de convenciones específicas de cada tecnología o ámbito, con las fuentes que adoptan. |
| [fuentes/](fuentes/) | Copias de las fuentes normativas adoptadas por Canone y de las listas de las que sus programas toman valores. |
| [adr/](adr/) | Registro de las decisiones de Canone, con su alcance y estado. |
| [pendientes/](pendientes/) | Temas de Canone documentados para retomarlos después, con su estado verificado; cada uno se borra cuando se cierra. |
| [plantilla/](plantilla/) | Plantillas que se copian a los repositorios o se instalan desde Canone: qué es cada tipo y cómo se mantiene. |
| [scripts/bloqueo.py](scripts/bloqueo.py) | Escribe la lista de bloqueo de contraseñas de la plantilla del servidor desde la lista del NCSC de `fuentes/`. |
| [scripts/copiar.py](scripts/copiar.py) | Copia a un repositorio los archivos de la plantilla que se copian sin editar y que le faltan o se separaron. |
| [scripts/infra/](scripts/infra/) | Las pruebas de los programas de `plantilla/infra/`, de `plantilla/receiver/` y de `plantilla/scripts/java.py`. |
| [scripts/verificar.py](scripts/verificar.py) | Comprueba que los repositorios cumplan las convenciones verificables, y las páginas, la plantilla y los workflows de Canone. |
| [.github/workflows/](.github/workflows/) | El CI de Canone: `fuentes.yml` corre `verificar.py --canone`, e `infra.yml`, las pruebas de `scripts/infra/` y las del servidor de la plantilla. |

## Verificación

`scripts/verificar.py` comprueba que los repositorios cumplan las convenciones verificables automáticamente, y falla si encuentra un incumplimiento. Un incumplimiento que un ADR aceptado del repositorio nombra en «Se aparta de» lo informa aparte y no cuenta, y un «Se aparta de» que no es un incumplimiento falla.

Para comprobar un repositorio:

```bash
python scripts/verificar.py --repo ../<repo>
```

Para comprobar todos los repositorios dentro de un directorio:

```bash
python scripts/verificar.py --todos ..
```

Con `--canone` comprueba Canone:

- Los orígenes de `plataformas/` contra `fuentes/`.
- Las versiones de la plantilla contra `stack.md`, y que una tecnología que está en dos bloques de `stack.md` lleve la misma versión.
- Que la lista de bloqueo de la plantilla salga de la del NCSC, y sus colores, de `plantilla/brand/tokens/`.
- Que cada archivo de `plantilla/server/` esté en una lista de `verificar.py`, y que cada archivo de sus listas exista.
- Que los workflows de Canone usen las acciones, los contenedores y las versiones de `stack.md`, y que sus scripts de `sh` no nieguen con `!` bajo `set -e`.

```bash
python scripts/verificar.py --canone
```

Para copiar a un repositorio los archivos que se copian sin editar, los mismos que compara `verificar.py`:

```bash
python scripts/copiar.py ../<repo>             # solo los nombra
python scripts/copiar.py ../<repo> --aplicar
```

Con `--cuentas` copia también los de un servidor con cuentas a uno que todavía no las tiene. No toca los archivos que cada repositorio completa ni uno del que un ADR aceptado del repositorio se aparta, y si reemplazaría uno cuyo contenido no está en un commit, no copia nada.

La verificación de cada repositorio considera únicamente las tecnologías que utiliza. Por ejemplo, si no tiene `server/`, no exige las convenciones de FastAPI.
