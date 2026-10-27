# ADR-0092 · Las actualizaciones de Debian se instalan solas, con unattended-upgrades

- **Estado:** Aceptada
- **Fecha:** 2026-10-27
- **Alcance:** «Máquina» de [`plataformas/despliegue.md`](../plataformas/despliegue.md) y
  `plantilla/infra/`

## Contexto

`despliegue.md` no decía cómo llegan a la máquina las actualizaciones de seguridad de Debian. Las
imágenes cloud de Debian 13 traen `unattended-upgrades`, que las instala solas: está en
`config_space/13/package_config/SYSTEM_BOOT` de debian-cloud-images. La imagen de otro proveedor
puede no traerlo.

## Decisión

1. Regla propia: las actualizaciones de Debian 13 se instalan solas, cada día, con
   `unattended-upgrades`. Una actualización de seguridad que espera a que alguien la instale deja
   la máquina expuesta mientras tanto, y nadie mira la máquina cada día.
2. `unattended-upgrades` está en la lista de paquetes de «Máquina».
3. *(propuesta)* `install.py` lo enciende con `plantilla/infra/20auto-upgrades`, en
   `/etc/apt/apt.conf.d/20auto-upgrades`, y falla si no está instalado.
4. La actualización del kernel se aplica al reiniciar la máquina, a mano.

## Consecuencias

- Una actualización llega sin que nadie la pruebe antes con la app, y puede reiniciar PostgreSQL o
  Caddy unos segundos.
- Instala lo que instala por defecto: las actualizaciones de seguridad y las de cada versión menor
  de Debian 13, no las de `trixie-updates` ni las de backports, y no reinicia la máquina.
- Comprobado en Debian 13.5 con `unattended-upgrades` 2.12: instalarlo sin preguntas deja
  `unattended-upgrades/enable_auto_updates` en `true` y escribe `20auto-upgrades` con el mismo
  contenido que la plantilla.

## Descartado

- **Instalarlas a mano, después de leer su aviso:** la máquina queda expuesta hasta que alguien
  las instala.
- **La sección 4.1 de NIST SP 800-123:** pide no instalarlas solas, para probarlas antes en un
  servidor idéntico, y cada producto tiene una sola máquina.
- **La descripción de `pkgsel/update-policy` del instalador de Debian 13:** explica las dos
  opciones y no decide entre ellas.
- **NIST SP 800-40 Rev. 4:** sobre la instalación solo describe lo que se puede hacer.
- **Las páginas UnattendedUpgrades y PeriodicUpdates de la wiki de Debian:** las escribe la
  comunidad.
- **El *Securing Debian Manual*:** su capítulo de actualizaciones es de 2011.
- **ANSSI BP-028 y el CIS Benchmark de Debian:** sin leer. El sitio de ANSSI rechaza la descarga, y
  CIS pide registrarse.
