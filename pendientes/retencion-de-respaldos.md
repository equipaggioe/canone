# La retención y la verificación de los respaldos

Tema pendiente: **sin decidir**. Salió de la revisión de `despliegue.md` del [ADR-0210](../adr/0210-despliegue-resume-las-cabeceras-en-security-headers-deja-entrar-solo-el-icmp-que-pide-nist-y-saca-lo-que-no-decide.md): «Respaldos» no dice cuánto guarda la receptora ni cómo se comprueba que lo guardado sirve.

## Estado (verificado 2026-11-21)

| Pieza | Estado |
| :--- | :--- |
| `plantilla/receiver/backup.sh` y `backup.ps1` | Abren `rest-server` con `--append-only`: el servidor agrega respaldos y no borra ninguno. Ninguno de los dos poda ni corre `restic check` |
| «Respaldos» de `despliegue.md` | No escribe una retención ni una verificación del repositorio |

## Qué empeora sin decidirlo

- El repositorio de la receptora crece sin fin hasta llenar su disco, y entonces el respaldo falla.
- Lo que la app borra, como las direcciones IP de `event_log`, que viven 365 días, sigue para siempre en los respaldos.
- Un repositorio dañado aparece recién al restaurar.

## Propuestas

1. La receptora poda su repositorio local, no a través de `rest-server`, con `restic forget --keep-daily 7 --keep-weekly 4 --keep-monthly 12 --prune` después de cada respaldo bueno. Los valores son una preferencia; los 12 meses se alinean con los 365 días del journal y de `event_log`.
2. La receptora corre `restic check` después de cada respaldo bueno, y el resultado sale en la línea `backup:` del script.

Falta: que el desarrollador elija los valores, y después escribirlos en «Respaldos», en `backup.sh` y `backup.ps1`, y probarlos en `scripts/infra/backup.sh`.
