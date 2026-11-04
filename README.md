# canone

Convenciones, plantillas y herramientas compartidas para construir, organizar y mantener proyectos de software.

## Propósito

Los proyectos que usan Canone comparten sus convenciones y decisiones en un solo lugar para leerse, construirse, organizarse y mantenerse de la misma manera.

Canone es una guía, no un reglamento: sus convenciones se siguen por defecto.

Cada proyecto elige las tecnologías que utiliza y consulta únicamente las convenciones correspondientes. Canone responde a la pregunta «si se usa X, ¿cómo se usa?», sin convertir su catálogo en una lista de requisitos universales.

Al definir las convenciones de cada tecnología o ámbito, prioriza la adopción de fuentes normativas externas que ya establecen convenciones adecuadas, evitando volver a redactarlas y mantenerlas. Cuando esas fuentes no cubren una decisión, dejan opciones abiertas o requieren excepciones, Canone establece convenciones propias. Los criterios están en [plataformas/README.md](plataformas/README.md).

Además de documentar las convenciones, proporciona plantillas y herramientas para incorporarlas a los repositorios y comprobar su cumplimiento. Cuando una convención exige una configuración o un mecanismo en una máquina, Canone proporciona también el programa que lo implementa. Las convenciones, sus plantillas y sus programas se mantienen sincronizados; solo instalándolos se prueba su funcionamiento en conjunto.

## Aplicación

Canone distingue entre convenciones generales y convenciones específicas de cada tecnología o ámbito.

Las siguientes convenciones aplican a todos los repositorios:

- [principios.md](principios.md)
- [repositorio.md](repositorio.md)
- [documentacion.md](documentacion.md)

Las convenciones de `plataformas/` dependen de las tecnologías utilizadas por cada proyecto. Qué páginas se consultan para trabajar en una pieza y cómo se heredan entre ellas está en [plataformas/README.md](plataformas/README.md).

Un repositorio puede apartarse de una convención cuando exista un motivo justificado. La desviación se registra en un ADR propio, dentro de `docs/adr/`, que identifica la convención afectada y explica la decisión.

## Principios

**Una convención tiene una única definición.**

Cada convención es adoptada de una fuente normativa o establecida como convención propia en la página correspondiente. Los demás documentos la referencian en lugar de reproducirla. Si la desviación de un repositorio demuestra ser una mejor solución general, se incorpora a Canone y sustituye la convención anterior cuando corresponda.

**Toda convención que pueda verificarse automáticamente debe tener una herramienta que la verifique o la imponga.**

La sección «Cumplimiento» de cada página registra las herramientas que verifican o imponen sus convenciones. Las convenciones que no pueden verificarse automáticamente rigen igual.

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

## Documentación y recursos

El repositorio organiza sus convenciones, fuentes, decisiones, plantillas y herramientas en los siguientes archivos y directorios.

| Recurso | Contenido |
| :--- | :--- |
| [principios.md](principios.md) | Método de trabajo, independiente de las tecnologías utilizadas. |
| [repositorio.md](repositorio.md) | Convenciones de Git, estructura de carpetas, README y CI. |
| [documentacion.md](documentacion.md) | Estructura y mantenimiento de la documentación de cada repositorio. |
| [plataformas/](plataformas/) | Metodología y catálogo de convenciones específicas de cada tecnología o ámbito, con las fuentes que adoptan. |
| [fuentes/](fuentes/) | Copias de las fuentes normativas adoptadas por Canone y de las listas de las que sus programas toman valores. |
| [adr/](adr/) | Registro de las decisiones de Canone, con su alcance y estado. |
| [plantilla/](plantilla/) | Plantillas que se copian a los repositorios o se instalan desde Canone: qué es cada tipo y cómo se mantiene. |
| [scripts/verificar.py](scripts/verificar.py) | Comprueba que los repositorios cumplan las convenciones verificables y las citas de `plataformas/` contra `fuentes/`. |

## Verificación

`scripts/verificar.py` comprueba que los repositorios cumplan las convenciones verificables automáticamente y, con `--canone`, las citas de `plataformas/` contra `fuentes/`, y falla si encuentra un incumplimiento.

Para comprobar un repositorio:

```bash
python scripts/verificar.py --repo ../<repo>
```

Para comprobar todos los repositorios dentro de un directorio:

```bash
python scripts/verificar.py --todos ..
```

Para comprobar las citas de `plataformas/` contra `fuentes/`:

```bash
python scripts/verificar.py --canone
```

La verificación de cada repositorio considera únicamente las tecnologías que utiliza. Por ejemplo, si no tiene `server/`, no exige las convenciones de FastAPI.
