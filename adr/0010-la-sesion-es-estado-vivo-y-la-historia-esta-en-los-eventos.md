# ADR-0010 · La tabla de sesiones es estado vivo, no historia

- **Estado:** Propuesta. El punto 3, en lo que revoca, lo reemplaza el [ADR-0038](0038-el-login-sigue-a-owasp-y-el-conteo-de-intentos-fallidos-vive-en-valkey.md)
- **Fecha:** 2026-09-23
- **Alcance:** `server/app/models/`, todos los repositorios con autenticación

## Contexto

El ADR-0008 dice dónde va la historia. Falta decir qué guarda la tabla de sesiones, y ahí los cinco
servidores hacen tres cosas distintas, verificado el 2026-09-23:

| Forma | Quién | Qué cuesta |
|---|---|---|
| Una fila por sesión, digesto sobrescrito al rotar, `closed_at` que se queda para siempre | navetta, presenze | **No puede detectar el reuso**: el digesto viejo ya no existe. Y nada borra una fila nunca |
| Una fila **por rotación**, encadenada con `parent_id` y `replaced_by_id` | banditore | Crece con cada renovación, y purgarla obliga a borrar por cadena entera para no romper las referencias |
| Una fila **por token emitido**, borrada al cerrar sesión | vettore | Sin rotación de refresh: no hay reuso que detectar porque no hay qué rotar |

Las tres mezclan dos cosas que no son la misma: **qué sesiones están vivas ahora** —que es estado, y
se consulta en cada petición— y **qué pasó con ellas** —que es historia, y se consulta cuando algo
huele mal—. Guardar historia en la tabla de estado es lo que obliga a banditore a borrar por cadena
y lo que deja a presenze con filas cerradas que no caducan.

## Decisión

1. **Una fila por sesión.** No por rotación ni por token emitido.
2. **La fila guarda dos digestos: el vigente y el anterior.** Rotar mueve el vigente al anterior y
   escribe el nuevo. El conteo de filas no depende de cuántas veces se renovó.
3. **Presentar el digesto anterior es reuso** y revoca (ADR-0009). Un digesto que no es ninguno de
   los dos es un `401` normal, sin alarma. Cubre el caso que importa: si el ladrón rota, el token
   que presenta después el cliente legítimo **es** el anterior. Un token de varias rotaciones atrás
   solo puede existir si el cliente legítimo también rotó, y entonces ya tiene uno reciente.
4. **Cerrar sesión borra la fila.** No hay `closed_at`. Que la sesión terminó, y por qué, es un
   evento de categoría `auth` en el registro del ADR-0008, que sobrevive a la fila.
5. **La fila lleva** el usuario, el dispositivo, los dos digestos, `expires_at`, `last_seen_at`,
   `created_at`, y `tenant_id` si el repositorio es multi-tenant. Nada más: lo demás es historia.
6. **La purga son las vencidas**, pasada una gracia sobre `expires_at`. Sin filas cerradas
   acumuladas, es una sola condición y no hay referencias entre filas que respetar.

## Consecuencias

- «Tus sesiones activas» es `SELECT` de la tabla entera del usuario, sin filtro de cerradas.
- navetta y presenze ganan detección de reuso con **una columna**. Hoy no la tienen.
- banditore pierde la cadena, y con ella la regla de purgar por cadena entera de su ADR-0029.
  También pierde poder ver el historial de rotaciones, que hoy nadie lee.
- vettore, si algún día rota el refresh, ya tiene dónde.
- Se puede saber que una sesión existió y terminó, pero no reconstruir su cadena de rotaciones.
  Es deliberado: esa cadena es el crecimiento que el ADR-0008 quita.
- El rechazo de un token de una sesión ya borrada dice «no encontrada», no «revocada». Para el
  cliente es el mismo error.

## Descartado

- **Guardar todos los digestos de la cadena**, que es lo que permite detectar el reuso de un token
  de hace cinco rotaciones. Ese caso no se da sin que el cliente legítimo tenga ya uno reciente, y
  el precio es una fila por renovación para siempre.
- **`closed_at` en vez de borrar.** Deja la tabla de estado llena de filas que no son estado, y
  obliga a filtrarlas en el camino caliente de cada petición.
- **Sobrescribir el digesto sin guardar el anterior.** Es lo más barato y es lo que hay hoy en
  navetta y presenze: convierte un token robado y ya usado en un `401` indistinguible de uno
  caducado, y el robo no se entera nadie.
