r"""Install the packages of the machine, before install.py.

    sudo python3 packages.py [--extension <name>]... [--turn] [--logs]
    python3 packages.py --list [--extension <name>]... [--turn] [--logs]

--extension, --turn and --logs say what install.py receives with the same names. --list prints the
packages, one per line, and installs nothing: it runs on any system, also outside the machine.

From canone: plataformas/despliegue.md, «Máquina».
"""

import argparse
import os
import subprocess

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
LOGS = ("systemd-journal-remote", "wireguard-tools")


def packages(extensions: list[str], turn: bool, logs: bool) -> list[str]:
    """Return the packages of a machine with those options of install.py."""
    names = list(BASE)
    for extension in extensions:
        names += EXTENSIONS.get(extension, ())
    if turn:
        names += TURN
    if logs:
        names += LOGS
    return names


def main() -> None:
    """Install the packages, or print them with --list."""
    parser = argparse.ArgumentParser(description="Install the packages of the machine.")
    parser.add_argument("--extension", action="append", default=[], help="like postgis")
    parser.add_argument("--turn", action="store_true", help="the app relays calls with coturn")
    parser.add_argument("--logs", action="store_true", help="the machine sends its journal")
    parser.add_argument("--list", action="store_true", help="print them and install nothing")
    arguments = parser.parse_args()
    names = packages(arguments.extension, arguments.turn, arguments.logs)
    if arguments.list:
        print("\n".join(names))
        return
    if os.geteuid() != 0:
        raise SystemExit("packages.py installs as root: run it with sudo.")
    environment = {**os.environ, "DEBIAN_FRONTEND": "noninteractive"}
    subprocess.run(["apt-get", "update"], check=True, env=environment)
    subprocess.run(["apt-get", "install", "--yes", *names], check=True, env=environment)


if __name__ == "__main__":
    main()
