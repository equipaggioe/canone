# ADR-0078 · El respaldo lo pide una receptora, y lo guarda su `rest-server`

- **Estado:** Aceptada. El punto 7 lo reemplaza el [ADR-0079](0079-canone-no-fija-la-operacion-del-respaldo.md)
- **Fecha:** 2026-10-24
- **Alcance:** «Respaldos», «Configuración» y «Proyecto» de
  [`plataformas/despliegue.md`](../plataformas/despliegue.md), `plantilla/infra/` y
  `plantilla/receiver/`

## Contexto

El punto 5 del
[ADR-0069](0069-el-servidor-se-instala-desde-plantilla-infra-y-sus-cabeceras-no-frenan-a-las-apps.md)
mandaba el respaldo a un repositorio S3 externo sin comparar otra salida, y obligaba a contratarlo.
Quien despliega quiere guardar los respaldos en una computadora propia, que no siempre está
encendida ni tiene una IP pública. Equipaggio respaldaba aparte la base de cada producto, sin
cifrar.

## Decisión

1. El respaldo va a una receptora: cualquier computadora de quien despliega, con `rest-server`
   0.14 en `--append-only`, sin contraseña y solo en su loopback.
2. La receptora inicia el respaldo: `plantilla/receiver/` abre `rest-server` y un túnel `ssh -R`,
   y la sesión pide el respaldo y espera el resultado. Sin timer en el servidor.
3. La cuenta `<app>-receiver` solo entra con llave y solo corre el comando que pide el respaldo,
   con un único túnel permitido, al 8001. El comando no tiene privilegios: toca un archivo que
   vigila `<app>-backup.path`.
4. El comando comprueba el túnel antes de pedir el respaldo, y el respaldo se corta a las 4 h.
5. El repositorio es una constante de la unidad, `rest:http://127.0.0.1:8001/<app>/`; la única
   credencial es `restic_password`.
6. Cada respaldo bueno cambia la fecha de `/var/lib/<app>/last-backup`, y el monitor de equipaggio
   avisa cuando tiene más de 48 h.
7. La limpieza de 7 diarios, 4 semanales y 12 mensuales la corre quien despliega, cada mes, en la
   receptora, junto con la prueba de la copia de la contraseña.
8. Equipaggio deja de respaldar la base de los productos.

## Consecuencias

- Nada que contratar, y la receptora no necesita IP pública ni puerto abierto: sale ella hacia el
  servidor.
- Un servidor comprometido no borra ni reescribe los respaldos, y una llave de receptora robada
  solo pide un respaldo.
- La receptora no necesita restic ni la contraseña para respaldar: los datos llegan cifrados.
- Una receptora guarda varios productos, uno por carpeta, y los respalda de a uno, porque todos
  usan el 8001.
- Entre una limpieza y la siguiente se juntan unos 30 respaldos de más; restic los deduplica.
- El monitor necesita leer la fecha del último respaldo; la vía se fija con las alertas.
- Comprobado en Debian 13, con restic 0.18.0, contra una receptora Windows con `rest-server`
  0.14.0 y `backup.ps1`:
  - El primer respaldo crea el repositorio, y los dos respaldos terminan con `backup: success` en
    5 s y 3 s. `last-backup` cambia, y `rest-server` queda detenido.
  - Con el dump fallado, la receptora recibe `backup: did not start`.
  - Una sesión sin túnel recibe `backup: no tunnel on 127.0.0.1:8001`, también si manda otro
    comando (`id; cat /etc/shadow`).
  - Un túnel a otro puerto falla con `remote port forwarding failed`, y pedir terminal, con
    `PTY allocation request failed`.
  - `<app>-backup.service` queda con exposición 1.5.
  - `backup.sh` y el corte de las 4 h no se probaron.

## Descartado

- **S3:** obliga a contratar un servicio, y un servidor con las llaves de S3 puede borrar sus
  respaldos.
- **Que el servidor empuje cuando la receptora esté en línea:** la receptora tendría que exponer un
  puerto a internet, o el servidor reintentar con un timer hasta encontrarla.
- **Que equipaggio guarde los respaldos:** solo mueve el riesgo a otro servidor, y su respaldo ya
  era redundante con restic.
- **`rest-server` con contraseña:** con un solo producto por VPS
  ([ADR-0077](0077-un-vps-aloja-un-solo-producto.md)) nadie más llega al túnel, y `--append-only`
  y el cifrado de restic ya cubren al servidor.
- **`sudo` o polkit para que la cuenta arranque la unidad:** le dan un privilegio, y el archivo
  vigilado no le da ninguno.
- **El respaldo en `event_log`:** el vocabulario de OWASP no tiene un evento de respaldo, y la
  unidad no tiene credencial de la base.
- **Limpiar desde el servidor:** `--append-only` lo impide, que es lo que protege los respaldos.
