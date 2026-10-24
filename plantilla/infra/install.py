r"""Install the user, units, Valkey and Caddy of an app on this machine.

    sudo python3 install.py <app> <port> <domain> \
        [--without sweep|web|panel|landing] [--allow <feature>]

From canone: plataformas/despliegue.md.
"""

import argparse
import subprocess
from pathlib import Path

HERE = Path(__file__).parent
UNITS = Path("/etc/systemd/system")
SITES = Path("/etc/caddy/sites")
# The files that are not units or sites, and where each one goes.
TARGETS = {
    "sysusers.conf": "/etc/sysusers.d/PRODUCTO.conf",
    "valkey.conf": "/etc/valkey/valkey-PRODUCTO.conf",
    "valkey-group.conf": f"{UNITS}/valkey-server@PRODUCTO.service.d/group.conf",
    "Caddyfile": "/etc/caddy/Caddyfile",
}
# Units and sites of a piece the app may not have.
OPTIONAL = ("sweep", "web", "panel", "landing")
# ADR-0071: what WebRTC and the maps ask for.
FEATURES = ("camera", "display-capture", "geolocation", "microphone")


def write(source: Path, target: Path, values: dict[str, str]) -> None:
    """Write source into target with the values of the app."""
    text = source.read_text(encoding="utf-8")
    for name, value in values.items():
        text = text.replace(name, value)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def parse() -> argparse.Namespace:
    """Read the arguments of the command line."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("app", help="the name of the repository")
    parser.add_argument("port", type=int, help="the port the server listens on")
    parser.add_argument("domain", help="the domain of the landing")
    parser.add_argument("--without", action="append", default=[], choices=OPTIONAL)
    parser.add_argument("--allow", action="append", default=[], choices=FEATURES)
    return parser.parse_args()


def main() -> None:
    """Write the files of the app, and enable its services."""
    arguments = parse()
    app = arguments.app
    policy = ", ".join(
        f"{name}=(self)" if name in arguments.allow else f"{name}=()" for name in FEATURES
    )
    values = {
        "PRODUCTO": app,
        "PUERTO": str(arguments.port),
        "DOMINIO": arguments.domain,
        "PERMISOS": policy,
    }
    for name, target in TARGETS.items():
        write(HERE / name, Path(target.replace("PRODUCTO", app)), values)
    skipped = tuple(f"PRODUCTO-{name}." for name in arguments.without)
    timers = []
    for source in sorted(HERE.glob("PRODUCTO*")):
        if source.name.startswith(skipped):
            continue
        folder = SITES if source.suffix == ".caddy" else UNITS
        target = folder / source.name.replace("PRODUCTO", app)
        write(source, target, values)
        if target.suffix == ".timer":
            timers.append(target.name)
    subprocess.run(["systemd-sysusers"], check=True)
    subprocess.run(["systemctl", "daemon-reload"], check=True)
    # ADR-0071: no app shares the instance of the package.
    subprocess.run(["systemctl", "disable", "--now", "valkey-server.service"], check=True)
    subprocess.run(["systemctl", "enable", "--now", f"valkey-server@{app}.service"], check=True)
    # deploy.py starts the server once there is a current version.
    subprocess.run(["systemctl", "enable", f"{app}.service"], check=True)
    subprocess.run(["systemctl", "enable", "--now", *timers], check=True)
    subprocess.run(["systemctl", "reload", "caddy.service"], check=True)


if __name__ == "__main__":
    main()
