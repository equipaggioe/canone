# ADR-0100 · Los registros salen a equipaggio: el journal por WireGuard, y `event_log` por una ruta de salud

- **Estado:** Aceptada
- **Fecha:** 2026-10-28
- **Alcance:** «Registros», «Máquina» y «Proyecto» de
  [`plataformas/despliegue.md`](../plataformas/despliegue.md); «Registro de eventos» y «Salud» de
  [`plataformas/fastapi.md`](../plataformas/fastapi.md); `plantilla/infra/`, `plantilla/server/`,
  `scripts/infra/` y `.github/workflows/infra.yml`

## Contexto

El
[ADR-0098](0098-protection-se-cumple-con-los-permisos-y-el-respaldo-y-no-detecta-ni-audita-accesos.md)
dejó sin efecto, en *Protection*, detectar que un registro se cambió o se borró y registrar y
vigilar cada acceso, y pidió volver a evaluarlos si los eventos salían a un sistema central de logs.
El journal, con `sshd`, Caddy, PostgreSQL y las unidades de la app, no sale de la máquina, ni
siquiera en el respaldo: quien consigue `root` borra lo que pasó desde el último respaldo, en el
journal y en `event_log`.

Comprobado en Debian 13.5 con systemd 257.13, wireguard-tools 1.0.20210914 y PostgreSQL 17:

- El `systemd-journal-remote` de Debian está compilado sin GnuTLS (`-GNUTLS` en `--version`) y
  rechaza `--trust=`: no puede verificar el certificado de quien envía.
- Por un túnel de WireGuard, `systemd-journal-remote` guarda lo de cada máquina en el archivo de su
  dirección en el túnel (`remote-10.77.0.2.journal`), y otra llave que usa la misma dirección no
  llega.
- `systemd-journal-upload` sigue desde su `--save-state`, y al seguir vuelve a enviar la última
  entrada que ya había enviado.
- La unidad de Debian queda en `failed` después de cinco fallos rápidos (`Start request repeated
  too quickly`) y no vuelve a intentar. Con `StartLimitIntervalSec=0` sigue intentando, cada vez más
  espaciado, hasta 60 s.
- journald borra un archivo entero cuando su primera entrada pasa `MaxRetentionSec=`: con 20 s de
  retención, una entrada recién escrita se borró junto con otra de 25 s del mismo archivo, y una del
  archivo activo pasó la retención sin borrarse hasta que el archivo rotó.
- Con `log_destination = 'syslog'`, PostgreSQL escribe en el journal de `postgresql@17-main.service`,
  y después de arrancar deja de escribir en `/var/log/postgresql/`.
- Con una transacción abierta que escribió primero y otra que confirmó después, una lectura por `id`
  ve la segunda y no la primera. Con `xid < pg_snapshot_xmin(pg_current_snapshot())` no ve ninguna
  hasta que la primera confirma, y después ve las dos.

## Decisión

1. Los registros de cada producto salen a un registro central, en la máquina de equipaggio.
2. *(propuesta)* journald guarda en disco y 365 días, con un archivo por día.
3. *(propuesta)* PostgreSQL escribe en el journal, con `log_destination = 'syslog'`.
4. *(propuesta)* `systemd-journal-upload` envía el journal a `http://10.77.0.1:19532` por un túnel
   de WireGuard, `wg-quick@logs`, solo con `install.py --logs`. `install.py` genera la llave del
   túnel la primera vez, la conserva e imprime la pública.
5. *(propuesta)* `systemd-journal-upload` reintenta sin límite.
6. *(propuesta)* `GET /api/health/event-log`, con el token de `/api/health/events`, responde
   `event_log` por páginas, en orden de `(xid, id)`, y solo las filas con un `xid` menor que
   `pg_snapshot_xmin(pg_current_snapshot())`.
7. *(propuesta)* Detectar que un registro de `event_log` se cambió o se borró le toca a equipaggio,
   que compara su copia con la ruta. Reemplaza el punto 3 del ADR-0098.
8. *(propuesta)* Registrar y vigilar cada acceso sigue sin efecto, como dice el punto 4 del
   ADR-0098.

## Consecuencias

- Lo que pasa en una máquina sale en segundos, y quien consigue `root` no borra lo que ya salió.
- Equipaggio junta los registros de todos los productos, con IP y user agent de personas. Ya junta
  el texto de cada SMS y el destinatario y el asunto de cada correo, así que no suma un tipo de dato
  nuevo.
- La máquina de equipaggio no envía sus propios registros: su journal y su `event_log` siguen como
  dice el ADR-0098.
- Si equipaggio cae, cada máquina conserva su journal y lo envía cuando vuelve.
- El journal llega al menos una vez: un reinicio del uploader repite la última entrada. La copia de
  `event_log` es exacta.
- Una transacción larga que escribe un evento demora en la ruta todos los eventos posteriores hasta
  que confirma.
- La última página responde un `nextPageToken` vacío: para seguir después, equipaggio guarda el
  token que lo llevó a la última página y vuelve a leer esa página.
- La purga borra lo que pasó la retención, y equipaggio no lo cuenta como un borrado.
- En cada máquina, la dirección 10.77.0.1 queda tomada por el túnel.
- Equipaggio tiene que construir el extremo del túnel con `systemd-journal-remote`, la retención de
  su copia, la copia y la comparación de `event_log`, y el aviso cuando una máquina deja de enviar.
- El CI no comprueba `StartLimitIntervalSec=0`, la retención ni `log_destination`: necesitan
  systemd corriendo, y se probaron a mano.

## Descartado

- **Un servicio externo de logs, como Grafana Cloud o Better Stack:** le manda IP y user agent de
  personas a un tercero, que *Protection* pide revisar antes y que el ADR-0004 de equipaggio
  descartó para las visitas. Sus planes gratuitos guardan 14 y 3 días, no 365. Su agente, como Alloy
  o Vector, no está en Debian 13. Y avisa por otro canal que el push de equipaggio.
- **Un servidor propio con su buscador, como Grafana Loki, Graylog u OpenSearch:** ninguno está en
  Debian 13, y es otro servicio que operar, cuando `journalctl` ya filtra los archivos de
  `systemd-journal-remote`.
- **Una máquina aparte solo para los registros:** los separa de equipaggio, que ya junta los SMS y
  los correos de todos, y suma una máquina que pagar y que nadie vigila.
- **La receptora de respaldos:** no siempre está encendida ni tiene IP pública, así que no recibe en
  el momento ni avisa.
- **`systemd-journal-remote` con TLS y certificados de cliente:** el de Debian 13 no los verifica.
- **Caddy con certificados de cliente delante de `systemd-journal-remote`:** el receptor ve todo
  desde loopback y junta las máquinas en un archivo, y suma una autoridad de certificados con
  vencimientos. Una llave de WireGuard no vence.
- **Que equipaggio lea con `systemd-journal-gatewayd`:** abre en cada máquina un puerto que entrega
  todo el journal.
- **Mandar `event_log` por el journal:** el evento de un cambio de fila se escribe antes de
  confirmar, y el journal guardaría eventos de transacciones deshechas. La comparación necesita una
  copia exacta.
- **Un cursor por `id` o por hora:** se salta la fila de una transacción que confirma tarde.
- **Un token aparte para la ruta:** el consumidor es el mismo, y los dos tokens vivirían cifrados
  con la misma llave en equipaggio.
- **pgaudit, para el punto 4 del ADR-0098:** el dueño le quita el `SELECT` al auditor sin aviso, y
  equipaggio lo recibiría sin poder notarlo.
