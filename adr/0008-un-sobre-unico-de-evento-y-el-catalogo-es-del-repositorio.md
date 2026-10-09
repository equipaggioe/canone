# ADR-0008 · Lo que pasa se registra en un sobre único, y el catálogo es de cada repositorio

- **Estado:** Propuesta. El punto 3 lo reemplaza el [ADR-0038](0038-el-login-sigue-a-owasp-y-el-conteo-de-intentos-fallidos-vive-en-valkey.md)
- **Fecha:** 2026-09-23
- **Alcance:** `server/`, todos los repositorios

## Contexto

Los seis repositorios responden distinto a la misma pregunta —quién entró, quién cambió qué— y
ninguna de las respuestas está escrita aquí. Inventario verificado leyendo el código el 2026-09-23:

| Repositorio | Qué tiene |
|---|---|
| navetta | `audit_log`, `auth_log` y `activity_log`, y **ningún código escribe en ninguna** |
| presenze | Las tres, escritas, y además `POST` y `PATCH` sobre `audit_log` y `auth_log` desde la API |
| vettore | Una sola `security_logs` con `SecurityEventType` de 60 valores, `severity` y `target_type` |
| banditore | Solo `audit_log`, con `login` y `logout` dentro del mismo enum que `insert`/`update`/`delete` |
| concordia | `audit_log` con lista blanca por campo, `login_attempt` aparte, y retención de 730 días |

El síntoma está en los enums: en navetta `login` aparece en los tres a la vez, y en navetta y
banditore `AuditAction` mezcla «una fila cambió» con «una persona entró», que son dos preguntas sin
nada en común. presenze ya las separó bien; vettore ya tiene la forma que el resto de la industria
converge (OCSF, ECS, los audit logs de las nubes): **un solo flujo con la categoría como campo, no
un almacén por categoría.**

Una convención que intente fijar *qué eventos* tiene cada producto no se va a cumplir: presenze
timbra nóminas y banditore pide paradas. Lo que sí se puede fijar es el sobre y las reglas.

## Decisión

1. **Una tabla de eventos por repositorio, con un sobre fijo.** Se llama `event_log`. Columnas,
   y todas menos las marcadas son obligatorias:

   | Columna | Para qué |
   |---|---|
   | `occurred_at` / `created_at` | Cuándo pasó y cuándo se escribió. No siempre coinciden |
   | `tenant_id` | Solo si el repositorio es multi-tenant; entonces **todo** evento lo lleva |
   | `actor_id` | Quién. Nulo cuando no hay cuenta detrás |
   | `actor_label` | El identificador tal como llegó, para cuando `actor_id` es nulo |
   | `category` | Conjunto **cerrado**: `auth`, `security`, `admin`, `business` |
   | `action` | El catálogo del repositorio |
   | `target_type` / `target_id` | Sobre qué. Opcionales |
   | `outcome` | `success` o `failure` |
   | `severity` | `low`, `medium`, `high`, `critical` |
   | `ip_address`, `user_agent` | De dónde vino |
   | `trace_id` | El trace-id del W3C Trace Context, el mismo del log y del `traceId` del error |
   | `details` | JSONB, con la regla del punto 5 |

2. **La categoría es de la convención; la acción es del repositorio.** El enum de `action` vive en
   el `core/enums.py` de cada uno y crece sin tocar este ADR. La columna es `TEXT`: con
   `StringEnumType` el ancho lo fija el valor más largo, y vettore ya lleva en su código un
   comentario contando caracteres a mano para que un evento nuevo quepa sin migración.

3. **Los intentos de acceso van en su propia tabla.** `login_attempt` no es un registro del pasado
   sino **la entrada de una decisión** —el bloqueo del ADR-0009— en el camino caliente del login,
   con retención de días y no de años, y con el correo tal como se tecleó y sin clave foránea,
   porque un correo que no existe es justamente la señal que interesa.

4. **`audit_log` queda solo para cambios de fila**, con `table_name`, `record_id`, `old_values` y
   `new_values`. Un hecho que no es un cambio de fila —un TOTP fallido, un dispositivo revocado— no
   tiene valores anteriores que registrar y va a la tabla de eventos. Un repositorio puede no tener
   `audit_log` en absoluto.

5. **Lista blanca por tabla y por campo, nunca lista negra.** Un diccionario enumera qué columnas
   se registran con su valor; una columna nueva no empieza a registrarse sola. Lo que cambió pero
   no está permitido se registra como cambiado y sin su valor. Sin esto, la bitácora se vuelve un
   segundo almacén de datos personales que **sobrevive al derecho de supresión**: el mecanismo que
   existe para demostrar cumplimiento sería el que lo rompe.

6. **Se escribe dentro de la transacción de la acción registrada, y ninguna API lo escribe.**
   No hay `POST`, `PATCH` ni `DELETE` sobre una tabla de bitácora, con ningún permiso. Una
   bitácora que se puede editar por HTTP no es una bitácora.

7. **Una renovación de token no escribe nada.** Una fila por rotación es crecimiento puro, y
   mudarlo de tabla no lo convierte en un rastro.

8. **Una ventana de retención por registro, y `0` significa indefinida.** Cero es una decisión
   escrita; la ausencia de la variable es un olvido, y así se distinguen.

## Consecuencias

- navetta borra tres tablas que nadie escribe, o las llena. Hoy son esquema muerto.
- presenze pierde los endpoints de escritura sobre `audit_log` y `auth_log`. Es la corrección con
  consecuencia más visible de todo este ADR.
- banditore parte su `AuditAction`: los hechos de sesión salen a la tabla de eventos.
- vettore es el que menos cambia: ya tiene el sobre. Le sobra el enum nativo estrecho y le falta
  `login_attempt`.
- La tabla es el escalón presente, no el destino. Un registro de auditoría en la misma base a la
  que la aplicación tiene `DELETE` protege contra un error, no contra un compromiso; el destino es
  un recolector fuera de la máquina, y mientras no exista se dice que no existe.
- La retención se implementa hoy con borrado por edad. **La forma correcta a volumen es particionar
  por mes y soltar la partición**: un `DELETE` masivo genera WAL, deja bloat y exige VACUUM.
  concordia ya particiona `message`. Es una meta declarada, no una obligación inmediata.

## Descartado

- **Una tabla por categoría** (`auth_event`, `activity_log`, `security_log`). Es lo que más se
  parece a lo que hay hoy en presenze, y falla al investigar: «todo lo que pasó alrededor de las
  3:14» se vuelve la unión de cuatro consultas con esquemas distintos. Además fija contenido, que
  es lo que ningún repositorio comparte.
- **Un enum de acciones común a todos.** Ningún catálogo puede contener a la vez el timbrado de
  nómina de presenze y la parada de banditore sin volverse una lista de todo.
- **Serializar la fila completa en `old`/`new`**, que es el patrón por defecto. Ver el punto 5.
- **Disparadores en la base** para llenar `audit_log`. Es más fuerte que escribir a mano —una carga
  masiva o un SQL directo no dejan rastro por el camino de la aplicación— y el argumento de que no
  conocen al actor tiene respuesta conocida (`SET LOCAL`). Queda descartado **solo por ahora**, y
  por una razón de alcance: ninguno de los seis tiene hoy el actor puesto en la sesión de base de
  datos. Es la mejora que sigue, junto con las tablas versionadas por sistema y el CDC.
