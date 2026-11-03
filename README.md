# canone

Convenciones, plantillas y herramientas compartidas para construir, organizar y mantener mis proyectos de software.

## Propósito

Canone centraliza las convenciones y decisiones compartidas por mis proyectos para que puedan construirse, organizarse y mantenerse de manera coherente.

Al definir las convenciones de cada tecnología, prioriza la adopción de fuentes normativas externas que ya establecen criterios adecuados, evitando volver a redactar y mantener reglas existentes. Cuando esas fuentes no cubren una decisión, dejan alternativas abiertas o requieren excepciones, canone establece los criterios correspondientes.

Además de documentar las convenciones, proporciona plantillas y herramientas para incorporarlas a los repositorios y comprobar su cumplimiento.

## Aplicación

Canone distingue entre convenciones generales y convenciones específicas de cada tecnología.

Las siguientes convenciones aplican a todos los repositorios:

- `principios.md`: método de trabajo.
- `repositorio.md`: organización, Git, README y CI.
- `documentacion.md`: estructura y mantenimiento de la documentación de cada repositorio.

Las convenciones de `plataformas/` dependen de las tecnologías utilizadas por cada proyecto. Cada repositorio consulta únicamente las páginas correspondientes a sus tecnologías y las convenciones transversales que le sean aplicables.

Una página que hereda de otra incorpora también sus convenciones, sin necesidad de repetirlas. La relación de herencia se declara en la propia página.

Un repositorio puede apartarse de una convención cuando exista un motivo justificado. La desviación se registra en un ADR propio, dentro de `docs/adr/`, que identifica la convención afectada y explica la decisión.

## Principios

**Una convención tiene una única definición.**

Cada convención se adopta de una fuente normativa o se establece como una regla propia en la página correspondiente. Los demás documentos la referencian en lugar de reproducirla. Si un repositorio necesita apartarse de ella, documenta la excepción mediante un ADR propio. Si la excepción demuestra ser una mejor solución general, se incorpora a canone y sustituye la convención anterior cuando corresponda.

**Toda convención que pueda verificarse automáticamente debe tener un mecanismo de cumplimiento.**

Cada página identifica el archivo de configuración, la regla de análisis o la prueba que comprueba las convenciones aplicables. Las convenciones que no pueden verificarse automáticamente siguen siendo válidas y deben cumplirse igualmente.

## Responsabilidades

Canone, cada repositorio y quien despliega tienen responsabilidades distintas y complementarias.

| Quién | Responsabilidades | Límites |
|---|---|---|
| **Canone** | Define las convenciones, proporciona las plantillas y establece la interfaz de sus programas mediante argumentos y `stdin`. | No guarda datos de las aplicaciones, no decide cuándo se ejecutan sus programas ni impone qué herramienta debe ejecutarlos. |
| **El repositorio** | Adopta las convenciones aplicables, incorpora las plantillas que se copian y declara sus propios datos: nombre, superficies y campos de `Settings`. | No reimplementa las plantillas ni define cómo se instalan los componentes proporcionados por canone. |
| **Quien despliega** | Ejecuta los programas de canone, manualmente o mediante la herramienta que elija, respetando sus interfaces. | No modifica ni sustituye los archivos que instalan esos programas, como unidades, configuraciones y scripts propios. |

El reparto de responsabilidades se fundamenta en [ADR-0075](adr/0075-canone-fija-el-repositorio-declara-y-consola-dispara.md) y [ADR-0107](adr/0107-canone-fija-la-interfaz-de-sus-programas-y-no-la-herramienta-que-los-corre.md).

## Integración

Canone proporciona dos tipos de plantillas, según cómo se incorporan al proyecto o al servidor.

### Plantillas que se copian

Se incorporan al repositorio que las utiliza y se mantienen allí. Por ejemplo, `release.yml`.

### Plantillas que se instalan

Se obtienen directamente de canone y sus programas las instalan en el servidor. Por ejemplo, `infra/` y su `deploy.py`.

No se copian al repositorio ni se mantienen mediante implementaciones propias.

### Configuración de cada despliegue

Los valores que cambian entre despliegues, sean secretos o no, no se incorporan al control de versiones. Cada repositorio declara los campos que necesita y quien despliega proporciona sus valores al servidor mediante la interfaz del programa correspondiente.

Por ejemplo, `install.py` recibe valores como el dominio y la memoria mediante argumentos, mientras que las credenciales se suministran mediante `credentials.py`.

Canone define cómo se reciben esos valores, pero no dónde los almacena quien despliega.

## Documentación y recursos

El repositorio organiza sus convenciones, referencias, decisiones, plantillas y herramientas en los siguientes archivos y directorios.

| Recurso | Contenido y aplicación |
|---|---|
| [principios.md](principios.md) | Método de trabajo, independiente de las tecnologías utilizadas. |
| [repositorio.md](repositorio.md) | Convenciones de Git, estructura de carpetas, README y CI. |
| [documentacion.md](documentacion.md) | Estructura y mantenimiento de la documentación de cada repositorio. |
| [plataformas/](plataformas/) | Metodología y catálogo de convenciones específicas de cada tecnología, incluidas sus referencias normativas. |
| [fuentes/](fuentes/) | Versiones concretas de las fuentes normativas adoptadas por canone. |
| [adr/](adr/) | Registro de las decisiones de canone, con su alcance y estado. |
| [plantilla/](plantilla/) | Archivos y componentes canónicos que se copian a los repositorios o se instalan desde canone. |
| [scripts/verificar.py](scripts/verificar.py) | Comprueba el cumplimiento de las convenciones de canone y de los repositorios que las utilizan. |

## Conservación de fuentes

`fuentes/` conserva exclusivamente las versiones de las fuentes normativas que canone adopta. Cada copia corresponde a una versión concreta y sirve como referencia estable para las páginas que la utilizan.

Las páginas de `plataformas/` identifican las convenciones que adoptan de cada fuente, sin reproducir innecesariamente su contenido.

La publicación de una nueva versión no implica su adopción automática. Decidir si se incorpora corresponde al mantenimiento de canone: requiere revisar sus cambios y determinar si justifican modificar las convenciones existentes.

## Verificación

`scripts/verificar.py` comprueba que canone y los repositorios que lo utilizan cumplan las convenciones verificables automáticamente.

Para comprobar un repositorio:

```bash
python scripts/verificar.py --repo ../<repo>
```

Para comprobar todos los repositorios dentro de un directorio:

```bash
python scripts/verificar.py --todos ..
```

Para comprobar las convenciones internas de canone:

```bash
python scripts/verificar.py --canone
```

La verificación de cada repositorio considera únicamente las plataformas que utiliza. Por ejemplo, si no tiene `server/`, no exige las convenciones de FastAPI.

El verificador detecta incumplimientos de las reglas que tienen mecanismos automatizados. Las convenciones que no pueden comprobarse mediante herramientas siguen siendo obligatorias.

## Mantenimiento

Las plantillas que se copian a los repositorios tienen una única versión canónica en `plantilla/`.

Toda modificación se realiza primero en esa ubicación y después se propaga a los repositorios que utilizan la plantilla. No se utiliza una copia de un repositorio como origen para actualizar las demás.

Los componentes que se instalan directamente desde canone se mantienen en el propio repositorio y se actualizan desde allí, sin crear implementaciones paralelas en los repositorios consumidores.