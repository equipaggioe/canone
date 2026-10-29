r"""Encrypt the credentials of an app, read from stdin as one field=value per line.

    python3 credentials.py <app> < credentials

A field of Settings goes to /etc/credstore.encrypted/<app>/<field>, encrypted as app_<field>, the
name the units load it with. restic_password goes to <app>-backup/ and github_token to
<app>-deploy/, each encrypted under its own name. The value is the rest of the line, without
quotes. It writes only the fields it reads, and restarts the server if it runs.

From canone: plataformas/despliegue.md.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

CREDENTIALS = Path("/etc/credstore.encrypted")
# The credentials the server does not get, and the unit whose folder holds each one.
APART = {"restic_password": "backup", "github_token": "deploy"}
# install.py writes them: database_url for the roles it creates, and turn_secret once.
INSTALLED = ("database_url", "turn_secret")
FIELD = re.compile(r"[a-z][a-z0-9_]*")


def parse(text: str) -> dict[str, str]:
    """Return each field and its value, and fail on a line that is not a new field=value."""
    values: dict[str, str] = {}
    for number, line in enumerate(text.splitlines(), start=1):
        if not line.strip() or line.startswith("#"):
            continue
        field, equals, value = line.partition("=")
        # The message never carries the value: it is a secret.
        if not equals or not FIELD.fullmatch(field):
            raise SystemExit(f"Line {number} is not field=value.")
        if field in INSTALLED:
            raise SystemExit(f"install.py writes {field}.")
        if not value:
            raise SystemExit(f"{field} is empty.")
        if field in values:
            raise SystemExit(f"{field} comes twice.")
        values[field] = value
    if not values:
        raise SystemExit("stdin has no field=value.")
    return values


def encrypt(target: Path, name: str, value: str) -> None:
    """Write value into target, encrypted under the name its unit loads it with."""
    target.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["systemd-creds", "encrypt", f"--name={name}", "-", str(target)],
        input=value,
        text=True,
        check=True,
    )


def main() -> None:
    """Encrypt each credential in its folder, and restart the server so it reads them."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("app", help="the name of the repository")
    app = parser.parse_args().app
    for field, value in parse(sys.stdin.read()).items():
        if field in APART:
            encrypt(CREDENTIALS / f"{app}-{APART[field]}" / field, field, value)
        else:
            # ADR-0070: the units load the folder with the prefix app.
            encrypt(CREDENTIALS / app / field, f"app_{field}", value)
    subprocess.run(["systemctl", "try-restart", f"{app}.service"], check=True)


if __name__ == "__main__":
    main()
