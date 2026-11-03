# canone

Convenciones, plantillas y herramientas compartidas para construir, organizar y mantener mis proyectos de software.

## Propósito

Mis proyectos comparten sus convenciones y decisiones en un solo lugar para construirse, organizarse y mantenerse de manera coherente.

Canone es una guía, no un reglamento: sus convenciones se siguen por defecto.

Cada proyecto elige las tecnologías que utiliza y consulta únicamente las convenciones correspondientes. Canone responde a la pregunta «si uso X, ¿cómo lo uso?», sin convertir su catálogo en una lista de requisitos universales.

Al definir las convenciones de cada tecnología o ámbito, prioriza la adopción de fuentes normativas externas que ya establecen convenciones adecuadas, evitando volver a redactarlas y mantenerlas. Cuando esas fuentes no cubren una decisión, dejan opciones abiertas o requieren excepciones, Canone establece convenciones propias.

Además de documentar las convenciones, proporciona plantillas y herramientas para incorporarlas a los repositorios y comprobar su cumplimiento. Cuando una convención exige una configuración o un mecanismo en una máquina, Canone proporciona también el programa que lo implementa. Las convenciones, sus plantillas y sus programas se mantienen sincronizados; instalarlos permite comprobar su funcionamiento en conjunto.

## Aplicación

Canone distingue entre convenciones generales y convenciones específicas de cada tecnología o ámbito.

Las siguientes convenciones aplican a todos los repositorios:

- [principios.md](principios.md)
- [repositorio.md](repositorio.md)
- [documentacion.md](documentacion.md)

Las convenciones de `plataformas/` dependen de las tecnologías utilizadas por cada proyecto. Para trabajar en una pieza se consulta su página y las secciones de `transversal.md` que esta enlaza.

Cada página hereda las convenciones de su página madre, sin repetirlas. La relación de herencia se declara en la propia página.

Un repositorio puede apartarse de una convención cuando exista un motivo justificado. La desviación se registra en un ADR propio, dentro de `docs/adr/`, que identifica la convención afectada y explica la decisión.

## Principios

**Una convención tiene una única definición.**

Cada convención es adoptada de una fuente normativa o establecida como convención propia en la página correspondiente. Los demás documentos la referencian en lugar de reproducirla. Si la desviación de un repositorio demuestra ser una mejor solución general, se incorpora a Canone y sustituye la convención anterior cuando corresponda.

**Toda convención que pueda verificarse automáticamente debe tener una herramienta que la verifique o la imponga.**

La sección «Cumplimiento» de cada página registra las herramientas que verifican o imponen sus convenciones. Cuando una convención puede materializarse en una configuración, herramienta o programa, Canone proporciona ese mecanismo. Las convenciones que no pueden verificarse automáticamente siguen siendo válidas y deben cumplirse igualmente.

## Responsabilidades

Canone, cada repositorio y quien despliega tienen responsabilidades distintas y complementarias.

| Quién | Responsabilidades | Límites |
|---|---|---|
| **Canone** | Define las convenciones, proporciona las plantillas y establece la interfaz de sus programas mediante argumentos y `stdin`. | No guarda datos de las aplicaciones, no decide cuándo se ejecutan sus programas ni impone qué herramienta debe ejecutarlos. |
| **El repositorio** | Sigue las convenciones aplicables, incorpora las plantillas que se copian y declara sus propios datos: nombre, superficies y campos de `Settings`. | No reimplementa las plantillas ni define cómo se instalan las plantillas proporcionadas por Canone. |
| **Quien despliega** | Ejecuta los programas de Canone, manualmente o mediante la herramienta que elija, respetando sus interfaces. | No modifica ni sustituye los archivos que instalan esos programas, como unidades, configuraciones y scripts propios. |

El reparto de responsabilidades se fundamenta en [ADR-0075](adr/0075-canone-fija-el-repositorio-declara-y-consola-dispara.md) y [ADR-0107](adr/0107-canone-fija-la-interfaz-de-sus-programas-y-no-la-herramienta-que-los-corre.md).

## Integración

Canone proporciona dos tipos de plantillas, según cómo se incorporan al proyecto o al servidor.

### Plantillas que se copian

Se incorporan al repositorio que las utiliza y se mantienen allí. Por ejemplo, `release.yml`.

### Plantillas que se instalan

Se obtienen directamente de Canone y sus programas las instalan en el servidor. Por ejemplo, `infra/` y su `deploy.py`.

### Configuración de cada despliegue

Los valores que cambian entre despliegues, sean secretos o no, no se incorporan al control de versiones. Cada repositorio declara los campos que necesita y quien despliega proporciona sus valores al servidor mediante la interfaz del programa correspondiente.

Por ejemplo, `install.py` recibe valores como el dominio y la memoria mediante argumentos, mientras que las credenciales se suministran mediante `credentials.py`.

Canone define cómo se reciben esos valores, pero no dónde los almacena quien despliega.

## Documentación y recursos

El repositorio organiza sus convenciones, fuentes, decisiones, plantillas y herramientas en los siguientes archivos y directorios.

| Recurso | Contenido y aplicación |
|---|---|
| [principios.md](principios.md) | Método de trabajo, independiente de las tecnologías utilizadas. |
| [repositorio.md](repositorio.md) | Convenciones de Git, estructura de carpetas, README y CI. |
| [documentacion.md](documentacion.md) | Estructura y mantenimiento de la documentación de cada repositorio. |
| [plataformas/](plataformas/) | Metodología y catálogo de convenciones específicas de cada tecnología o ámbito, con las fuentes que adoptan. |
| [fuentes/](fuentes/) | Versiones concretas de las fuentes normativas adoptadas por Canone. |
| [adr/](adr/) | Registro de las decisiones de Canone, con su alcance y estado. |
| [plantilla/](plantilla/) | Archivos canónicos que se copian a los repositorios o se instalan desde Canone. |
| [scripts/verificar.py](scripts/verificar.py) | Comprueba el cumplimiento de las convenciones de Canone y de los repositorios que las utilizan. |

## Conservación de fuentes

`fuentes/` conserva exclusivamente las versiones de las fuentes normativas que Canone adopta. Cada copia corresponde a una versión concreta y fija el texto que se adopta.

Las páginas de `plataformas/` identifican las convenciones que adoptan de cada fuente, sin reproducir innecesariamente su contenido.

La publicación de una nueva versión no implica su adopción automática. Decidir si se incorpora corresponde al mantenimiento de Canone: requiere revisar sus cambios y determinar si justifican modificar las convenciones existentes.

## Verificación

`scripts/verificar.py` comprueba que Canone y los repositorios que lo utilizan cumplan las convenciones verificables automáticamente.

Para comprobar un repositorio:

```bash
python scripts/verificar.py --repo ../&lt;repo&gt;
```

Para comprobar todos los repositorios dentro de un directorio:

```bash
python scripts/verificar.py --todos ..
```

Para comprobar las convenciones internas de Canone:

```bash
python scripts/verificar.py --canone
```

La verificación de cada repositorio considera únicamente las tecnologías que utiliza. Por ejemplo, si no tiene `server/`, no exige las convenciones de FastAPI.

## Mantenimiento

Las plantillas que se copian a los repositorios tienen una única versión canónica en `plantilla/`.

Toda modificación se realiza primero en esa ubicación y después se propaga a los repositorios que utilizan la plantilla. No se utiliza una copia de un repositorio como origen para actualizar las demás.

Las plantillas que se instalan directamente desde Canone se mantienen en el propio repositorio y se actualizan desde allí, sin crear implementaciones paralelas en los repositorios consumidores.