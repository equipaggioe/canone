# ADR de `canone`

Decisiones transversales. **Cada una dice a qué aplica**: la mayoría vale solo para los
repositorios que usan esa plataforma. Un repositorio que se aparta de una abre un ADR propio que
diga de qué se aparta y por qué.

Formato y reglas: [`documentacion.md`](../documentacion.md).

| # | Título | Aplica a | Estado |
|---|---|---|---|
| [0001](0001-el-estandar-vive-en-un-repositorio.md) | El estándar vive en un repositorio y los demás lo enlazan | Todos | Propuesta |
| [0002](0002-los-archivos-base-se-copian-y-se-verifican.md) | Los archivos base se copian y un script verifica la copia | Con `server/` | Propuesta |
| [0003](0003-enum-como-varchar-con-check.md) | Un enum se guarda como VARCHAR con CHECK | Con base de datos | Propuesta |
| [0004](0004-geografia-con-funciones.md) | Una columna geográfica se declara con una función, no con un Annotated | Con PostGIS | Propuesta |
| [0005](0005-prefijo-api-al-montar.md) | El prefijo `/api` se aplica al montar, y la ruta no lleva versión | Con FastAPI | Propuesta |
| [0006](0006-dependencias-con-pyproject-y-uv.md) | Las dependencias de Python se declaran en `pyproject.toml` con `uv` | Con Python | Propuesta |
| [0007](0007-adapter-static.md) | Toda superficie web usa `adapter-static` | Con SvelteKit | Propuesta |
