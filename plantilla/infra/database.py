r"""Empty, migrate or seed the database of the app on this machine.

    sudo python3 /usr/local/lib/PRODUCTO/database.py empty
    sudo python3 /usr/local/lib/PRODUCTO/database.py migrate
    sudo python3 /usr/local/lib/PRODUCTO/database.py seed [--mock]

empty stops the server, deletes the database and the files of the
users, and creates the database again as install.py does: empty and
without migrations. migrate runs the migrations and the seeders of the
active version and starts the server. seed runs them without touching
the server, and with --mock, the example data. empty and seed --mock
run only on a machine that install.py set up with --development.

install.py installs it with the name of the app. From canone:
plataformas/despliegue.md, «PostgreSQL».
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

APP = "PRODUCTO"
SERVICE = f"{APP}.service"
# install.py --development leaves it, and without it, deletes it.
MARK = Path("/etc") / APP / "development"
FILES = Path("/var/lib") / APP / "files"
CURRENT = Path("/srv") / APP / "current"
MIGRATE = "PRODUCTO-migrate@{}.service"
MOCK = "PRODUCTO-mock@{}.service"


def psql(script: str, database: str = "postgres") -> str:
    """Run script as postgres on database and return what it prints."""
    command = ["runuser", "-u", "postgres", "--", "psql", "-X", "-q", "-At"]
    command += ["-v", "ON_ERROR_STOP=1", f"--dbname={database}"]
    result = subprocess.run(
        command, input=script, capture_output=True, text=True, cwd="/", check=True
    )
    return result.stdout


def create_database(app: str, extensions: list[str]) -> None:
    """Create the database, its roles and its extensions."""
    owner, reader = f"{app}_owner", f"{app}_read"
    script = [
        f"SELECT 'CREATE ROLE {role} LOGIN' WHERE NOT EXISTS "
        f"(SELECT FROM pg_roles WHERE rolname = '{role}') \\gexec"
        for role in (app, owner, reader)
    ]
    script += [
        (
            f"SELECT 'CREATE DATABASE {app} OWNER {owner}' WHERE NOT EXISTS "
            f"(SELECT FROM pg_database WHERE datname = '{app}') \\gexec"
        ),
        f"\\connect {app}",
        # An extension that is not trusted, like postgis, needs a
        # superuser.
        *(f"CREATE EXTENSION IF NOT EXISTS {name};" for name in extensions),
        # The reader sees what the owner creates, and changes nothing.
        f"ALTER DEFAULT PRIVILEGES FOR ROLE {owner} IN SCHEMA public "
        f"GRANT SELECT ON TABLES TO {reader};",
        f"GRANT SELECT ON ALL TABLES IN SCHEMA public TO {reader};",
        # fastapi.md: only the server and the owner read event_log.
        "DO $$ BEGIN IF to_regclass('public.event_log') IS NOT NULL THEN "
        f"REVOKE SELECT ON event_log FROM {reader}; END IF; END $$;",
    ]
    psql("\n".join(script))


def development() -> None:
    """Fail on a machine that is not in development."""
    if not MARK.exists():
        raise SystemExit(
            f"{MARK} does not exist: the machine is not in development, and its database stays."
        )


def active() -> str:
    """Return the active version."""
    if not CURRENT.exists():
        raise SystemExit(f"{CURRENT} does not exist: deploy.py installs a version first.")
    return CURRENT.resolve().name


def empty() -> None:
    """Delete the database and the files, and create it again."""
    development()
    # The extensions of install.py, not those a migration creates.
    extensions = psql(
        "SELECT extname FROM pg_extension e JOIN pg_roles r ON r.oid = e.extowner "
        f"WHERE r.rolname <> '{APP}_owner' AND extname <> 'plpgsql' ORDER BY extname",
        APP,
    ).split()
    subprocess.run(["systemctl", "stop", SERVICE], check=True)
    # The purge or the sweep may still be connected.
    psql(f"DROP DATABASE {APP} WITH (FORCE)")
    create_database(APP, extensions)
    # The files point at rows that no longer exist.
    if FILES.is_dir():
        for path in FILES.iterdir():
            if path.is_dir() and not path.is_symlink():
                shutil.rmtree(path)
            else:
                path.unlink()


def migrate() -> None:
    """Run the migrations and the seeders, and start the server."""
    seed(mock=False)
    # install.py imports this file from the template, where deploy.py
    # does not run until it writes the data of the app.
    import deploy

    try:
        deploy.restart()
    except deploy.Unhealthy as error:
        raise SystemExit(str(error)) from error


def seed(*, mock: bool) -> None:
    """Run the seeders of the active version, or its example data."""
    if mock:
        development()
    unit = MOCK if mock else MIGRATE
    subprocess.run(["systemctl", "start", unit.format(active())], check=True)


def main() -> None:
    """Run the command it receives."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("command", choices=("empty", "migrate", "seed"))
    parser.add_argument("--mock", action="store_true", help="the example data, with seed")
    arguments = parser.parse_args()
    command = arguments.command
    if arguments.mock and command != "seed":
        parser.error("--mock goes with seed")
    try:
        if command == "empty":
            empty()
        elif command == "migrate":
            migrate()
        else:
            seed(mock=arguments.mock)
    except subprocess.CalledProcessError as error:
        sys.exit(f"{' '.join(error.cmd)} failed:\n{error.stderr or ''}")
    print(f"{command}: done")


if __name__ == "__main__":
    main()
