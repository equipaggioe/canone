r"""Undo what install.py, credentials.py, deploy.py, packages.py, swap.py and uv.py leave.

    sudo python3 uninstall.py <app> database|app|machine [--dry-run]

database drops the database, its roles, their credentials and the files of the users, and stops
what uses them: install.py creates them again. app also takes every file, unit, account and
folder of the app. machine also takes the swap, uv, the files install.py writes for the whole
machine and the journal tunnel. --dry-run prints what it would do, and does nothing.

The packages stay, with the files install.py overwrote in them, like the Caddyfile or
nftables.conf: what the image brought is not known. To leave the machine as the provider delivers
it, the provider reinstalls it. Each level keeps the account that administers, its keys and
00-<app>.conf of ssh, and root stays locked: they are the way in.

From canone: plataformas/despliegue.md, «Desinstalar».
"""

import argparse
import os
import shutil
import subprocess
from pathlib import Path

from database import psql
from swap import FSTAB, SWAPFILE

UNITS = Path("/etc/systemd/system")
SITES = Path("/etc/caddy/sites")
CREDENTIALS = Path("/etc/credstore.encrypted")
HBA = Path("/etc/postgresql/17/main/pg_hba.conf")
IDENT = Path("/etc/postgresql/17/main/pg_ident.conf")
LEVELS = ("database", "app", "machine")
# The files of the app, besides its units, sites and credentials. 00-PRODUCTO.conf of ssh stays.
FILES = (
    "/etc/PRODUCTO",
    "/etc/sysusers.d/PRODUCTO.conf",
    "/etc/tmpfiles.d/PRODUCTO.conf",
    "/etc/valkey/valkey-PRODUCTO.conf",
    f"{UNITS}/valkey-server@PRODUCTO.service.d",
    "/etc/ssh/sshd_config.d/PRODUCTO-receiver.conf",
    "/etc/postgresql/17/main/conf.d/PRODUCTO.conf",
    "/etc/systemd/journald.conf.d/00-PRODUCTO.conf",
    "/etc/systemd/journal-upload.conf.d/00-PRODUCTO.conf",
    f"{UNITS}/systemd-journal-upload.service.d/PRODUCTO.conf",
    "/usr/local/lib/PRODUCTO",
    "/usr/local/sbin/PRODUCTO-deploy",
    "/usr/local/sbin/PRODUCTO-database",
    "/srv/PRODUCTO",
    "/var/lib/PRODUCTO",
    "/var/lib/PRODUCTO-dump",
    "/var/lib/valkey/PRODUCTO.rdb",
    "/var/cache/private/PRODUCTO-backup",
    "/run/PRODUCTO-receiver",
)
# The files install.py writes for the whole machine that no package brings. What it overwrote of a
# package, like the Caddyfile, nftables.conf or 20auto-upgrades, stays.
MACHINE = (
    "/etc/apt/apt.conf.d/52automatic-reboot",
    "/etc/sysctl.d/valkey.conf",
    "/etc/nftables.d/turn.nft",
    "/etc/wireguard/logs.conf",
    "/usr/local/bin/uv",
    "/root/.cache/uv",
)
# The tunnel of --logs, which install.py enables.
TUNNEL = ("wg-quick@logs.service", "systemd-journal-upload.service")


class Plan:
    """With --dry-run, what each step would do, in place of doing it."""

    dry = False
    steps: list[str] = []


def run(*command: str, check: bool = True) -> None:
    """Run a command, or note it with --dry-run."""
    if Plan.dry:
        Plan.steps.append(" ".join(command))
        return
    subprocess.run(command, check=check)


def systemctl(*arguments: str) -> None:
    """Run systemctl, which fails on nothing that is missing."""
    run("systemctl", *arguments, check=False)


def delete(path: Path) -> None:
    """Delete a file or a folder, if there is one."""
    if not path.exists() and not path.is_symlink():
        return
    if Plan.dry:
        Plan.steps.append(f"rm -r {path}")
    elif path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink()


def remove_lines(path: Path, start: str) -> None:
    """Remove the lines of path that start with start."""
    if not path.is_file():
        return
    lines = path.read_text(encoding="utf-8").splitlines()
    gone = [line for line in lines if line.startswith(start)]
    if Plan.dry:
        Plan.steps.extend(f"remove from {path}: {line}" for line in gone)
    elif gone:
        kept = [line for line in lines if not line.startswith(start)]
        path.write_text("".join(f"{line}\n" for line in kept), encoding="utf-8")


def owned(folder: Path, app: str) -> list[Path]:
    """Return what folder has under the name of the app: <app>, <app>.<suffix> or <app>-<name>."""
    return sorted(
        path for path in folder.glob(f"{app}*") if path.name == app or path.name[len(app)] in ".-"
    )


def triggers(app: str) -> list[str]:
    """Return the server, and the timers and path units that start the others."""
    found = [path.name for path in owned(UNITS, app) if path.suffix in (".timer", ".path")]
    return [f"{app}.service", *found]


def drop(kind: str, names: tuple[str, ...], catalog: str, column: str) -> None:
    """Drop the databases or roles of names that exist."""
    listed = ", ".join(f"'{name}'" for name in names)
    found = psql(f"SELECT {column} FROM {catalog} WHERE {column} IN ({listed})").split()
    suffix = " WITH (FORCE)" if kind == "DATABASE" else ""
    script = "".join(f"DROP {kind} {name}{suffix};\n" for name in found)
    if Plan.dry:
        Plan.steps.extend(script.splitlines())
    elif script:
        psql(script)


def drop_database(app: str) -> None:
    """Stop what uses the database, and drop it with its roles, credentials and files."""
    systemctl("stop", *triggers(app))
    if shutil.which("psql") is not None:
        drop("DATABASE", (app,), "pg_database", "datname")
        drop("ROLE", (app, f"{app}_owner", f"{app}_read"), "pg_roles", "rolname")
    remove_lines(HBA, f"local {app} {app}_read ")
    remove_lines(IDENT, f"{app}_read ")
    for path in (CREDENTIALS / app / "database_url", CREDENTIALS / f"{app}-migrate"):
        delete(path)
    for path in (Path(f"/var/lib/{app}/files"), Path(f"/var/lib/{app}-dump")):
        delete(path)
    systemctl("reload", "postgresql@17-main.service")


def remove_app(app: str) -> None:
    """Disable and delete the units, sites, files, credentials and accounts of the app."""
    units = [path.name for path in owned(UNITS, app) if path.is_file()]
    systemctl("disable", "--now", f"valkey-server@{app}.service", *units)
    for path in [*owned(UNITS, app), *owned(SITES, app), *owned(CREDENTIALS, app)]:
        delete(path)
    for name in FILES:
        delete(Path(name.replace("PRODUCTO", app)))
    for account in (app, f"{app}_owner", f"{app}-receiver"):
        if subprocess.run(["id", account], capture_output=True, check=False).returncode == 0:
            run("userdel", account)
    systemctl("daemon-reload")
    systemctl("restart", "systemd-journald.service")
    systemctl("reload", "caddy.service", "ssh.service", "postgresql@17-main.service")


def remove_machine() -> None:
    """Delete the swap, the journal tunnel, uv and the files install.py writes for the machine."""
    systemctl("disable", "--now", *TUNNEL)
    if SWAPFILE.exists():
        run("swapoff", str(SWAPFILE), check=False)
    delete(SWAPFILE)
    remove_lines(FSTAB, f"{SWAPFILE} ")
    for name in MACHINE:
        delete(Path(name))
    # The default of the kernel, which sysctl.d/valkey.conf changed.
    run("sysctl", "--quiet", "vm.overcommit_memory=0")


def main() -> None:
    """Undo the level it receives, and those below it."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("app", help="the name of the repository")
    parser.add_argument("level", choices=LEVELS)
    parser.add_argument("--dry-run", action="store_true", help="print it, and do nothing")
    arguments = parser.parse_args()
    if os.geteuid() != 0:
        raise SystemExit("uninstall.py runs as root: run it with sudo.")
    app, level = arguments.app, arguments.level
    Plan.dry = arguments.dry_run
    drop_database(app)
    if level in ("app", "machine"):
        remove_app(app)
    if level == "machine":
        remove_machine()
    if Plan.dry:
        print("\n".join(Plan.steps))
        return
    print(f"{app}: {level} uninstalled.")


if __name__ == "__main__":
    main()
