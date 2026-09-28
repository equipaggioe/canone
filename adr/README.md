# ADR de `canone`

Decisiones transversales. **Cada una dice a qué aplica**: la mayoría vale solo para los
repositorios que usan esa plataforma. Un repositorio que se aparta de una abre un ADR propio que
diga de qué se aparta y por qué.

Formato y reglas: [`documentacion.md`](../documentacion.md).

| # | Título | Aplica a | Estado |
|---|---|---|---|
| [0001](0001-el-estandar-vive-en-un-repositorio.md) | El estándar vive en un repositorio y los demás lo enlazan | Todos | Propuesta |
| [0002](0002-los-archivos-base-se-copian-y-se-verifican.md) | Los archivos base se copian y un script verifica la copia | Con `server/` | Propuesta |
| [0003](0003-enum-como-varchar-con-check.md) | Un enum se guarda como VARCHAR con CHECK | Con base de datos | Reemplazada por ADR-0013 |
| [0004](0004-geografia-con-funciones.md) | Una columna geográfica se declara con una función, no con un Annotated | Con PostGIS | Propuesta |
| [0005](0005-prefijo-api-al-montar.md) | El prefijo `/api` se aplica al montar, y la ruta no lleva versión | Con FastAPI | Reemplazada por ADR-0012 |
| [0006](0006-dependencias-con-pyproject-y-uv.md) | Las dependencias de Python se declaran en `pyproject.toml` con `uv` | Con Python | Propuesta |
| [0007](0007-adapter-static.md) | Toda superficie web usa `adapter-static` | Con SvelteKit | Propuesta |
| [0008](0008-un-sobre-unico-de-evento-y-el-catalogo-es-del-repositorio.md) | Lo que pasa se registra en un sobre único, y el catálogo es de cada repositorio | Con `server/` | Propuesta |
| [0009](0009-el-login-no-delata-cuentas-y-el-bloqueo-vive-en-la-base.md) | El login no delata cuentas por tiempo y el bloqueo vive en una tabla | Con autenticación | Propuesta |
| [0010](0010-la-sesion-es-estado-vivo-y-la-historia-esta-en-los-eventos.md) | La tabla de sesiones es estado vivo, no historia | Con autenticación | Propuesta |
| [0011](0011-la-pasada-es-una-funcion-y-el-disparador-va-aparte.md) | La pasada periódica es una función, y el disparador va aparte | Con `server/` | Propuesta |
| [0012](0012-el-prefijo-api-v1-se-aplica-al-montar.md) | El prefijo `/api/v1` se aplica al montar | Con FastAPI | Propuesta |
| [0013](0013-un-enum-hereda-de-strenum-y-se-guarda-como-varchar-con-check.md) | Un enum hereda de `StrEnum` y se guarda como VARCHAR con CHECK | Con base de datos | Propuesta |
| [0014](0014-una-pagina-se-escribe-desde-la-recomendacion-oficial.md) | Una página de plataforma se escribe desde la recomendación oficial, no desde el código | `plataformas/` | Reemplazada por ADR-0016 |
| [0015](0015-el-sobre-de-error-sigue-el-rfc-9457.md) | El sobre de error sigue el RFC 9457 | Con `server/` y sus clientes | Aceptada |
| [0016](0016-una-pagina-es-un-catalogo-de-convenciones-que-sale-de-la-recomendacion-oficial.md) | Una página de plataforma es un catálogo de convenciones que sale de la recomendación oficial | `plataformas/` | Reemplazada por ADR-0018 |
| [0017](0017-la-marca-vive-en-brand.md) | El logo y los colores del producto viven en `brand/` | Todos | Aceptada |
| [0018](0018-una-pagina-se-revisa-contra-la-copia-de-sus-estandares-y-solo-dice-lo-que-elige-endurece-o-no-cubren.md) | Una página se revisa contra la copia de sus estándares y solo dice lo que elige, endurece o no cubren | `plataformas/` | Aceptada |
| [0019](0019-el-ci-corre-cada-semana-aunque-no-haya-commits.md) | El CI corre cada semana aunque no haya commits | Todos | Propuesta |
