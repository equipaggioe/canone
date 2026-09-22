# Autenticación y defensa

Cómo se autentica y qué protege cada capa. Aplica al servidor y a lo que cada cliente guarda.

## Contraseñas

**argon2id** vía `argon2-cffi`, con los parámetros por defecto de la biblioteca. No se bajan sin
medir: el coste **es** la defensa.

## Tokens

JWT firmados, con el tipo dentro del token. **Un tipo por superficie y por etapa**, no un token
único que sirva para todo:

| Tipo | Para qué |
|---|---|
| `access` | La API pública |
| `refresh` | Renovar; se guarda hasheado, nunca en claro |
| `backoffice` | La sesión de operación interna |
| `backoffice_preauth` | Solo entre la contraseña y el código TOTP. Minutos, no la sesión completa |

El tipo separa radios de daño: una cookie de backoffice robada no sirve contra la API pública, y un
pre-auth interceptado a medio login no es una sesión.

El refresh token se guarda hasheado en la base: un volcado de la tabla no da sesiones.

## Segundo factor

TOTP en las superficies de operación. El secreto se guarda cifrado, no en claro. El paso 1
(contraseña) entrega un `backoffice_preauth` de vida corta y el paso 2 (código) lo cambia por la
sesión real.

## Qué guarda cada cliente

| Cliente | Dónde |
|---|---|
| Flutter | `flutter_secure_storage`; lo demás en base cifrada |
| Flet y Qt | Almacenamiento seguro de la plataforma |
| Web | La sesión, y nada más, en el almacenamiento del navegador |

Ningún cliente guarda la contraseña. Un «recordar sesión» guarda el refresh token, que es opaco,
rota en cada uso y el servidor puede revocar.

## Límite de tasa

Los endpoints de autenticación y los que cuestan caro llevan límite por IP.

**Un limitador en memoria de proceso solo sirve con un proceso.** Con varias instancias cada una
lleva su propio conteo y el límite real es N veces el declarado: o el almacén es compartido (Redis),
o arrancar con varias instancias sin él tiene que fallar al arranque. Un límite que se multiplica en
silencio es peor que no tenerlo, porque se cree que está.

## Permisos

RBAC: roles con permisos, y el permiso se comprueba en una dependencia de FastAPI, no dentro de cada
endpoint a mano.

## Cabeceras y CSP

Las pone Caddy, no la aplicación — ver [despliegue.md](despliegue.md). **Cada regla de la CSP lleva
su host**: una CSP sin host es la de todos los sitios.

## Lo que depende de la topología de dominios

Los atributos de la cookie (`Domain`, `SameSite`, `Secure`, `Path`), la política de CORS y el
aislamiento de sesión del backoffice **no** viven en `core/security.py`: dependen de qué dominios y
subdominios tenga el producto, y elegirlos mal en silencio produce o una sesión que no viaja o una
que viaja de más. Van en un ADR del repositorio, decididos a la vista.
