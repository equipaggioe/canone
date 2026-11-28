r"""Install the packages of the machine, before install.py.

    sudo python3 packages.py [--extension <name>]... [--turn] [--mail <host>] [--logs]
        [--java <piece>]... [--browser <task>=<OnCalendar>]... [--all]
    python3 packages.py --list [--extension <name>]... [--turn] [--mail <host>] [--logs]
        [--java <piece>]... [--browser <task>=<OnCalendar>]... [--all]

--extension, --turn, --mail, --logs, --java and --browser say what install.py receives with the same
names, and --all stands for all of them: every package this program can install. --list prints the
packages, one per line, and installs nothing: it runs on any system, also outside the machine.

Caddy comes from its own repository: packages.py writes it to apt, with its key, the series of
stack.md and its origin for unattended-upgrades, before it installs.

From canone: plataformas/despliegue.md, «Máquina».
"""

import argparse
import os
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
# ADR-0155: the repository of Caddy, its key, its series and its origin for unattended-upgrades.
CADDY = {
    "caddy.asc": Path("/etc/apt/keyrings/caddy.asc"),
    "caddy.sources": Path("/etc/apt/sources.list.d/caddy.sources"),
    "caddy.pref": Path("/etc/apt/preferences.d/caddy.pref"),
    "51caddy-upgrades": Path("/etc/apt/apt.conf.d/51caddy-upgrades"),
}

# What every machine needs: the programs of install.py and deploy.py, and what install.py checks.
BASE = (
    "caddy",
    "postgresql",
    "valkey-server",
    "restic",
    "sudo",
    "python3",
    "nftables",
    "unattended-upgrades",
    "systemd-timesyncd",
    "ca-certificates",
)
# The package of each extension that the postgresql package does not bring.
EXTENSIONS = {"postgis": ("postgresql-17-postgis-3",)}
TURN = ("coturn",)
# despliegue.md, «Correo»: Postfix, and the certificate it offers with STARTTLS.
MAIL = ("postfix", "ssl-cert")
LOGS = ("systemd-journal-remote", "wireguard-tools")
# despliegue.md, «Máquina»: the JRE of Debian 13 that runs each piece in Java.
JAVA = ("openjdk-21-jre-headless",)
# ADR-0172: the Chromium of Debian 13 that a task of install.py --browser drives.
BROWSER = ("chromium-headless-shell",)


def packages(
    extensions: list[str], turn: bool, mail: bool, logs: bool, java: bool, browser: bool
) -> list[str]:
    """Return the packages of a machine with those options of install.py."""
    names = list(BASE)
    for extension in extensions:
        names += EXTENSIONS.get(extension, ())
    if turn:
        names += TURN
    if mail:
        names += MAIL
    if logs:
        names += LOGS
    if java:
        names += JAVA
    if browser:
        names += BROWSER
    return names


def install(names: list[str]) -> None:
    """Write the repository of Caddy to apt, and install the packages."""
    environment = {**os.environ, "DEBIAN_FRONTEND": "noninteractive"}
    # apt reaches the repository of Caddy by HTTPS, with the certificates of Debian.
    subprocess.run(["apt-get", "update"], check=True, env=environment)
    subprocess.run(["apt-get", "install", "--yes", "ca-certificates"], check=True, env=environment)
    for name, target in CADDY.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(HERE / name, target)
        target.chmod(0o644)
    subprocess.run(["apt-get", "update"], check=True, env=environment)
    subprocess.run(["apt-get", "install", "--yes", *names], check=True, env=environment)


def main() -> None:
    """Install the packages, or print them with --list."""
    parser = argparse.ArgumentParser(description="Install the packages of the machine.")
    parser.add_argument("--extension", action="append", default=[], help="like postgis")
    parser.add_argument("--turn", action="store_true", help="the app relays calls with coturn")
    parser.add_argument("--mail", help="the host Postfix answers as, on the machine of equipaggio")
    parser.add_argument("--logs", action="store_true", help="the machine sends its journal")
    parser.add_argument("--java", action="append", default=[], help="a piece in Java")
    parser.add_argument(
        "--browser", action="append", default=[], help="a task that drives Chromium"
    )
    parser.add_argument("--all", action="store_true", help="every package it can install")
    parser.add_argument("--list", action="store_true", help="print them and install nothing")
    arguments = parser.parse_args()
    if arguments.all:
        names = packages(
            list(EXTENSIONS), turn=True, mail=True, logs=True, java=True, browser=True
        )
    else:
        names = packages(
            arguments.extension,
            arguments.turn,
            arguments.mail is not None,
            arguments.logs,
            bool(arguments.java),
            bool(arguments.browser),
        )
    if arguments.list:
        print("\n".join(names))
        return
    if os.geteuid() != 0:
        raise SystemExit("packages.py installs as root: run it with sudo.")
    install(names)


if __name__ == "__main__":
    main()
