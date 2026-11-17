# ADR-0172 · Una tarea que maneja Chromium corre en su instancia de `PRODUCTO-browser@`, con el Chromium de Debian

- **Estado:** Aceptada. Los puntos 4 y 5 son *(propuesta)*.
- **Fecha:** 2026-11-17
- **Alcance:** [`plataformas/despliegue.md`](../plataformas/despliegue.md), «Máquina» y «Procesos»; [`plataformas/fastapi.md`](../plataformas/fastapi.md), «Tareas»; [`stack.md`](../stack.md); `install.py`, `packages.py`, `PRODUCTO-browser@.service` y `PRODUCTO-browser@.timer` de `plantilla/infra/`

## Contexto

bot necesita una tarea periódica que abra un sitio en Chromium con Playwright y lea su captcha con
ddddocr. Se probó el 2026-11-17 en un Debian 13 (systemd 257), con la unidad `PRODUCTO-task@` de
la plantilla tomada como propiedades de `systemd-run`, con una cuenta de `systemd-sysusers` y con
Playwright 1.49.1 y 1.65.2:

- Con el aislamiento de `PRODUCTO-task@`, el Node que trae Playwright muere al arrancar, por
  `MemoryDenyWriteExecute=`: el JIT de V8 escribe el código que corre.
- Sin `MemoryDenyWriteExecute=`, el filtro de llamadas mata a Chromium por `setpriority` y
  `sched_setaffinity` (de `@resources`), `pkey_alloc` (fuera de `@system-service`) y `capset` (de
  `@privileged`). El Chromium 156.0.8078.79 de Debian no llama a `sched_setaffinity`; el que baja
  Playwright 1.49.1 sí. Sin cada una de las otras tres, el de Debian muere.
- Con esas tres permitidas y sin `MemoryDenyWriteExecute=`, el Chromium de Debian abre una página
  con JavaScript y otra por red, con los dos Playwright, tres veces seguidas cada uno.
- `RestrictNamespaces=yes` no estorba: Playwright lanza Chromium con `--no-sandbox`.
- ddddocr 1.6.1 lee un captcha con la unidad `PRODUCTO-task@` sin cambios: `onnxruntime` no
  necesita ninguna excepción.
- `systemd-analyze security` da 1.2 a `PRODUCTO-task@` y 1.3 a la unidad sin
  `MemoryDenyWriteExecute=` y con las tres llamadas.
- Con la cuenta de una unidad con `DynamicUser=`, que no tiene carpeta personal, el Node de
  Playwright 1.65.2 falla en `uv_os_homedir`. Con la de `sysusers.conf`, cuya carpeta es `/`, no.
- Cuando el filtro mató a un proceso hijo de Chromium, la vuelta quedó colgada sin terminar.
- En una unidad `oneshot`, `TimeoutStartSec=` corta la vuelta, y `RuntimeMaxSec=` no: se comprobó
  con `systemd-run`, y lo dice `systemd.service` de systemd 257.

## Decisión

1. **Una tarea que maneja Chromium corre en `PRODUCTO-browser@.service`**, una copia de
   `PRODUCTO-task@.service` sin `MemoryDenyWriteExecute=` y con `SystemCallFilter=setpriority`,
   `SystemCallFilter=pkey_alloc` y `SystemCallFilter=capset`, y la dispara
   `PRODUCTO-browser@.timer`. Las demás unidades no cambian.
2. **El Chromium es el de Debian 13, `chromium-headless-shell`**, que instala `packages.py
   --browser`. La tarea lo lanza con `executable_path="/usr/bin/chromium-headless-shell"`.
3. **`install.py --browser` falla sin `chromium-headless-shell`.**
4. *(propuesta)* **Una vuelta termina a la hora**, con `TimeoutStartSec=1h`.
5. *(propuesta)* **La app declara la tarea en `BROWSER_TIMERS` de `tasks.py`**, `{tarea:
   OnCalendar}`, como `TIMERS` del [ADR-0151](0151-una-tarea-con-otro-calendario-corre-en-su-instancia-de-task.md),
   y quien instala la pasa como `install.py --browser <tarea>=<OnCalendar>`, que escribe su
   calendario en `PRODUCTO-browser@<tarea>.timer.d/calendar.conf`. Una tarea va en un solo
   `--task` o `--browser`. `packages.py` recibe las mismas `--browser`.
6. **`scripts/infra/browser.sh` lo comprueba** en el job `install` de `infra.yml`, y `seccomp.sh`
   y el job `exposure` cubren la unidad nueva.

## Consecuencias

- Solo la tarea que lo pide pierde `MemoryDenyWriteExecute=`: el servidor, la purga, el barrido y
  las demás tareas siguen con él.
- Chromium corre sin su propio sandbox. Lo aísla la unidad, que no le deja crear espacios de
  nombres; el sandbox de Chromium los necesita.
- Chromium se actualiza con `unattended-upgrades`, y Debian 13 sube de versión mayor en sus
  actualizaciones de seguridad. Playwright solo garantiza el Chromium de su misma versión: una
  versión de Debian que rompa a Playwright la detecta `browser.sh` o la tarea en la máquina.
- La máquina carga unos 230 MB más con `chromium-headless-shell`.
- Una tarea que necesite más de una hora por vuelta no cabe en esta unidad.

## Descartado

- **Aflojar `PRODUCTO-task@`:** todas las tareas de todas las apps perderían
  `MemoryDenyWriteExecute=` y su filtro.
- **Un proceso permanente con su unidad:** un navegador colgado lo deja colgado, y la tarea
  periódica ya trabaja sobre lo que encuentra en la base.
- **El Chromium de Playwright, bajado en `release.yml` dentro del artefacto:** suma 101 MB
  comprimidos a cada versión, pide además `sched_setaffinity` y solo se actualiza al cambiar de
  versión de Playwright.
- **Bajarlo en `deploy.py`:** el navegador quedaría fuera del `.sha256` firmado.
- **`SystemCallErrorNumber=EPERM`:** una llamada negada fallaría en silencio, como dice el
  [ADR-0149](0149-las-unidades-de-la-app-permiten-mbind.md).
- **Sacar `@resources` o `@privileged` del filtro:** volverían todas sus llamadas, y Chromium usa
  una sola de cada grupo.
- **`RuntimeMaxSec=` como tope:** no corta una unidad `oneshot`.
