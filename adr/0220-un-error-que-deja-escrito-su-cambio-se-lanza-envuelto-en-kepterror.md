# ADR-0220 · Un error que deja escrito su cambio se lanza envuelto en `KeptError`

- **Estado:** Aceptada
- **Fecha:** 2026-11-23
- **Alcance:** `plataformas/fastapi.md` y `plantilla/server/`

## Contexto

Una petición abre una transacción que hace commit si la ruta termina y rollback si lanza. Algunos
errores tienen que dejar escrito un cambio: la contraseña equivocada suma un fallo, y el secreto de
refresco reusado borra la sesión. Lanzados, el cambio se deshace: las esperas no empiezan nunca, y
la sesión robada sigue viva. El punto 8 del
[ADR-0219](0219-una-app-presenta-un-token-de-acceso-opaco-y-el-login-tiene-una-ruta-por-metodo-y-forma.md)
proponía responderlos sin lanzarlos. El caso vuelve en el código por SMS, la recuperación y el
código de autorización presentado dos veces.

## Decisión

1. Un error que tiene que dejar escrito un cambio se lanza envuelto en `KeptError`, de `errors.py`.
2. `get_session` atrapa el `KeptError` dentro de la transacción, que hace commit, y después lanza el
   error que envuelve, que responde su manejador.
3. Los errores del endpoint de token son `TokenRefusal`, que su manejador responde como un 400 en
   JSON con `error`.

## Consecuencias

- Los servicios lanzan sus errores como en el resto del servidor, y la regla vive en un solo lugar.
- Lo que la petición escribió antes del `KeptError` también queda: se lanza solo donde lo escrito es
  lo que tiene que quedar.
- Un `KeptError` fuera de una ruta con `SessionDep` no tiene manejador y responde 500.

## Descartado

- **Responder el error sin lanzarlo.** Cada ruta arma su respuesta, y un error lanzado por costumbre
  pierde el cambio sin que nadie lo note.
- **Escribir el cambio en su propia transacción, como los eventos.** La petición bloquea la fila de
  la contraseña o de la sesión para que dos intentos no se pisen, y una segunda transacción sobre esa
  fila espera a la primera: se traban.
