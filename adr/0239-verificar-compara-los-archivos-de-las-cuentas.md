# ADR-0239 · `verificar.py` compara los archivos de las cuentas

- **Estado:** Aceptada
- **Fecha:** 2026-11-24
- **Alcance:** `fastapi.md`, `autenticacion.md`, `scripts/verificar.py`, `plantilla/README.md` y
  `plantilla/server/`

## Contexto

Las páginas no decían qué archivos de autenticación se copian sin editar. `fastapi.md` decía que
`blocklist.txt` sí, y `verificar.py` no comparaba su copia. Se comprobó, con la suite de la plantilla:

- Con otros nombres, otro dominio, otro rol, otro cliente, otras credenciales, seis combinaciones de
  `METHODS` y tres valores de `PUSH` fallaban solo dos pruebas, que traían un valor escrito, y
  `test_openapi_file_is_current`, porque `openapi.json` se regenera.
- Con los textos del catálogo redactados de otra forma fallaban otras tres, que traían el texto.
- Un texto que el catálogo no traduce, o que está `fuzzy`, sale en inglés, sin error.

## Decisión

1. Un servidor con cuentas, el que tiene `models/account/`, copia sin editar los archivos que nombra
   la plantilla de cada sección de `autenticacion.md`, con sus pruebas, y `verificar.py` los compara.
2. Cada producto completa `clients.py`, `dependencies.py`, `errors.py`, `enums.py`, `config.py`,
   `main.py`, `tasks.py`, `methods.py`, `push.py`, los catálogos, las migraciones y `conftest.py`.
3. `CLIENTS` está en `clients.py`, con las URI de retorno de cada `client_id`.
4. Las pruebas de las cuentas toman de `Settings` y del catálogo lo que cada producto cambia.
5. `verificar.py --canone` falla si un archivo de `plantilla/server/` no está en ninguna lista.
6. `verificar.py` falla si el catálogo de un idioma no traduce un texto de la plantilla.

## Consecuencias

- Una corrección de seguridad de la plantilla se ve pendiente en cada repositorio con cuentas.
- Un producto que necesita más datos de una cuenta los pone en una tabla propia.

## Descartado

- **Comparar solo las pruebas:** dejarían pasar un cambio que ninguna cubre.
- **Comparar en todo servidor:** fallaría un producto sin cuentas.
- **Partir `dependencies.py` y `errors.py`:** las pruebas que se comparan ya cuidan lo suyo.
