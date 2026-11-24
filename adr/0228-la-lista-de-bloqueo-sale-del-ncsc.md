# ADR-0228 · La lista de bloqueo sale del NCSC

- **Estado:** Aceptada
- **Fecha:** 2026-11-23
- **Alcance:** `autenticacion.md`, `fastapi.md`, `fuentes/`, `scripts/` y `plantilla/server/`

## Contexto

`autenticacion.md` pedía una lista de bloqueo con las 3000 contraseñas más comunes, contraseñas
filtradas y las palabras del producto, y que el servidor obligue a cambiar una contraseña
comprometida, sin decir de dónde sale la lista ni cómo se obliga.

Las esperas y el límite de 100 fallos frenan a quien prueba muchas contraseñas en una cuenta, pero
no a quien prueba las pocas más comunes en todas las cuentas. Contra eso sirve la lista.

La lista del NCSC del Reino Unido, en la copia de SecLists del commit `e6b76a2`, tiene 99.840
contraseñas; 46.483 quedan con 8 puntos de código o más, en NFC y con `casefold`.

## Decisión

1. La lista de bloqueo son las contraseñas de 8 caracteres o más de la lista del NCSC, sacada de las
   filtraciones de Have I Been Pwned. `scripts/bloqueo.py` la deriva de `fuentes/`, y
   `verificar.py --canone` comprueba que la plantilla la tenga al día.
2. La comparación es de la contraseña entera, en NFC y con `casefold`.
3. Una contraseña tiene a lo sumo 128 caracteres.
4. Una contraseña de la lista se rechaza con 422 de tipo `password-blocked`.
5. Cambiar la contraseña pone en cero sus fallos y la vuelve a habilitar, y una cuenta de
   administración no agrega una.

## Consecuencias

- La lista se carga en memoria al arrancar el servidor.

## Descartado

- **Las palabras del producto en un archivo de cada repositorio.** El nombre del producto no llega a
  8 caracteres en casi ningún caso, y sus derivados no son las contraseñas que se prueban en todas
  las cuentas. Un archivo más por repositorio no lo paga.
- **Obligar a cambiar una contraseña comprometida.** La única evidencia que tiene el servidor es la
  lista, y ya se aplicó al crear la contraseña: solo cambiaría con una lista nueva del NCSC.
- **La lista de 10 millones de xato-net.** Más grande, y NIST dice que una lista muy grande aporta
  poco contra ataques que ya limita la espera.
- **Distinguir mayúsculas.** Las variantes triviales de una contraseña de la lista pasarían.
- **Un 422 de `validation` con un texto.** El cliente tendría que leer el texto para decir por qué.
