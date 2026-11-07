# ADR-0126 · `database.py` vacía la base solo en una máquina en desarrollo, y quien administra la lee como `<app>_read`

- **Estado:** Aceptada
- **Fecha:** 2026-11-06
- **Alcance:** «PostgreSQL» de [plataformas/despliegue.md](../plataformas/despliegue.md),
  `plantilla/infra/install.py`, `plantilla/infra/database.py` y `scripts/infra/deploy.sh`

## Contexto

En desarrollo, el esquema cambia mucho y las migraciones se acumulan. De vez en cuando se juntan
todas en una inicial, también en el VPS de desarrollo, y producción arranca con una sola. Para eso,
la base del VPS tiene que poder vaciarse. Canone solo traía `install.py`, que crea la base, y
`deploy.py`, que la migra. Los botones de base de Consola, que vaciaban y exploraban la base por SSH
con `sudo -n` o por un túnel con contraseña, no funcionan contra una máquina de canone: `sudo` pide
la contraseña y los roles entran por `peer`. Lo vio Consola el 2026-11-02.

## Decisión

1. `install.py --development` deja la marca `/etc/<app>/development`, y sin la bandera la borra. Para
   pasar a producción, la máquina se instala otra vez sin la bandera.
2. `database.py`, que `install.py` instala junto a `deploy.py`, trae dos comandos:
   - `empty` falla sin la marca. Con ella, detiene `<app>.service`, borra la base y
     `/var/lib/<app>/files/`, y crea la base otra vez como `install.py`. La deja vacía y sin migrar.
   - `migrate` corre las migraciones de la versión activa y arranca el servidor.
3. `empty` no migra: al juntar las migraciones, la versión activa todavía tiene el historial viejo.
   Migrarla dejaría en `alembic_version` una revisión que la versión nueva no conoce, y su despliegue
   fallaría.
4. `empty` borra también los archivos de los usuarios, porque apuntan a filas que dejan de existir.
5. `install.py` crea el rol `<app>_read`, con `SELECT` sobre lo que crea `<app>_owner`, salvo
   `event_log`: solo el servidor y el dueño leen el registro. La cuenta que administra entra solo
   como `<app>_read`, por `peer` con un mapa de `pg_ident.conf`. Un túnel de `ssh` al socket entra
   igual, porque PostgreSQL ve la cuenta con la que `sshd` abre el túnel.
6. *(Propuesta)* `empty` crea otra vez las extensiones que no son de `<app>_owner`, las que creó
   `install.py` como `postgres`. Las que crea una migración vuelven con ella.

## Consecuencias

- La marca vive en la máquina, no en quien la llama. Frena también a quien corre `database.py` por
  `ssh`, o a quien apunta por error al VPS de producción. Es lo que hace Rails desde la versión 5:
  guarda el entorno junto a la base, y sus tareas destructivas se niegan en producción.
- Instalar otra vez una máquina de desarrollo sin `--development` le quita la marca. Quien la
  instala tiene que pasar la bandera cada vez.
- Explorar los datos de una máquina no pide `sudo` ni deja cambiarlos.
- `install.py` edita el `pg_hba.conf` y el `pg_ident.conf` de Debian. La línea de `<app>_read` va
  primera, porque PostgreSQL toma la primera línea que coincide, y la de Debian para cada cuenta local
  no tiene mapa.

## Descartado

- **Comandos de `deploy.py`:** `deploy.py` instala versiones, y vaciar la base es otra intención.
- **Solo el seguro de quien llama, como el de Consola:** es por repositorio, y una vez abierto no
  distingue la máquina de desarrollo de la de producción, ni cubre a quien entra por `ssh`.
- **Que `empty` migre:** ver el punto 3.
- **Una contraseña para `<app>_read` y un túnel TCP:** canone no da contraseña a ningún rol.
