# ADR-0076 · Lo que cambia entre despliegues sale de un solo archivo, y lo demás es código

- **Estado:** Aceptada
- **Fecha:** 2026-10-24
- **Alcance:** «Configuración» de [`plataformas/fastapi.md`](../plataformas/fastapi.md) y `.consola/`
  en [`repositorio.md`](../repositorio.md)

## Contexto

`Settings` exigía todo campo obligatorio y sin valor por defecto, así que cada plazo, umbral y
algoritmo pasaba por la configuración. En los `.env` de los repositorios, los secretos eran la
minoría: 8 de 34 campos en banditore, 8 de 67 en concordia y 1 de 14 en equipaggio. El resto eran
constantes que no cambian entre la máquina de quien desarrolla y el servidor.

Los valores vivían repartidos entre el `config.env` de consola y el `.env` del servidor, que llegaba
en claro por `scp`. El servidor ya no recibe un `.env`: cada campo llega cifrado como credencial
([ADR-0070](0070-las-unidades-cargan-la-carpeta-de-credenciales-y-permissions-policy-sigue-a-owasp.md)).

El factor III de [The Twelve-Factor App](https://12factor.net/config) llama *config* a lo que
cambia entre despliegues, y dice que la configuración interna, la que no cambia, va mejor en el
código. La sección 2.11 del *Secrets Management Cheat Sheet* de OWASP pide preparar el traslado de
un secreto a otra solución.

## Decisión

1. `Settings` lleva solo lo que cambia entre despliegues. Lo que no cambia es una constante del
   módulo que lo usa. Es una regla propia de `fastapi.md`.
2. Lo que cambia entre despliegues de un repositorio, secreto o no, vive en `.consola/config.env`,
   que no se commitea. Es la única fuente: lo que llega al servidor sale de ahí.
3. consola cifra cada valor en el servidor con `systemd-creds`, solo en la carpeta de la unidad que
   lo usa.
4. Un secreto se escribe hoy en claro. Si se adopta un gestor de contraseñas, el valor pasa a ser
   una referencia que consola resuelve, y el archivo y el despliegue no cambian.

## Consecuencias

- Los secretos de producción quedan en claro en la máquina de quien despliega: el disco tiene que
  estar cifrado.
- Lo que no es secreto, como el puerto o el dominio, no tiene historial en git.
- El [ADR-0074](0074-las-credenciales-del-respaldo-tienen-una-copia-fuera-del-servidor.md) guarda
  las credenciales del respaldo en un gestor de contraseñas, que hoy no se usa: falta decidir dónde
  va la copia de `config.env` fuera de esa máquina.
- La retención de `event_log`, de «Registro de eventos» en `fastapi.md`, sale de `Settings` y pasa
  a ser una constante: es la misma en todos los despliegues.
- Los valores de desarrollo de `credentials/` no salen de este archivo, y queda por decidir de
  dónde salen.

## Descartado

- **Citar el factor III en `fastapi.md`:** su convención central es guardar la configuración en
  variables de entorno, y en eso regula lo mismo que *Environment* y *Credentials* de
  `systemd.exec`, que cita `despliegue.md` y es de menor orden. Del factor III se toma solo la
  frontera entre configuración y código, así que va como regla propia.

- **Un gestor de contraseñas como única fuente desde ya:** suma una herramienta y una CLI que hoy
  no se usan. El punto 4 deja el camino listo.
- **Un `server/settings.toml` versionado con los no secretos:** las constantes son código, y lo que
  cambia entre despliegues no es lo mismo en cada uno.
- **Un archivo para los secretos y otro para el resto:** lo que cambia entre despliegues sin ser
  secreto son pocos valores, y dos archivos son dos fuentes.
- **El `.env` en el servidor:** systemd desaconseja las variables de entorno para secretos, en
  *Environment* de [`systemd.exec`](../fuentes/systemd/systemd.exec.xml).
