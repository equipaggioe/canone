r"""Install the users, units, Valkey, Caddy and backup receiver of an app on this machine.

    sudo python3 install.py <app> <domain> <memory> \
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
    "sysctl.conf": "/etc/sysctl.d/valkey.conf",
    "tmpfiles.conf": "/etc/tmpfiles.d/PRODUCTO.conf",
    "sshd-receiver.conf": "/etc/ssh/sshd_config.d/PRODUCTO-receiver.conf",
    "backup-request": "/usr/local/libexec/PRODUCTO-backup-request",
    "Caddyfile": "/etc/caddy/Caddyfile",
}
# The files that run, and the file that holds the keys of the receivers.
EXECUTABLES = ("backup-request",)
RECEIVERS = "/etc/PRODUCTO/receivers"
# Units and sites of a piece the app may not have.
OPTIONAL = ("sweep", "web", "panel", "landing")
# ADR-0070: the standardized features of the W3C registry, at commit 2939804, and
# publickey-credentials-create of Web Authentication Level 3. The policy denies the ones the app
# does not allow.
FEATURES = (
    "accelerometer",
    "ambient-light-sensor",
    "attribution-reporting",
    "autoplay",
    "battery",
    "bluetooth",
    "camera",
    "ch-ua",
    "ch-ua-arch",
    "ch-ua-bitness",
    "ch-ua-full-version",
    "ch-ua-full-version-list",
    "ch-ua-high-entropy-values",
    "ch-ua-mobile",
    "ch-ua-model",
    "ch-ua-platform",
    "ch-ua-platform-version",
    "ch-ua-wow64",
    "compute-pressure",
    "cross-origin-isolated",
    "direct-sockets",
    "display-capture",
    "encrypted-media",
    "execution-while-not-rendered",
    "execution-while-out-of-viewport",
    "fullscreen",
    "geolocation",
    "gyroscope",
    "hid",
    "identity-credentials-get",
    "idle-detection",
    "keyboard-map",
    "magnetometer",
    "mediasession",
    "microphone",
    "midi",
    "navigation-override",
    "otp-credentials",
    "payment",
    "picture-in-picture",
    "publickey-credentials-create",
    "publickey-credentials-get",
    "screen-wake-lock",
    "serial",
    "storage-access",
    "sync-xhr",
    "tools",
    "usb",
    "web-share",
    "window-management",
    "xr-spatial-tracking",
)


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
    parser.add_argument("domain", help="the domain of the landing")
    parser.add_argument("memory", help="the maxmemory of its Valkey, like 256mb")
    parser.add_argument("--without", action="append", default=[], choices=OPTIONAL)
    parser.add_argument("--allow", action="append", default=[], choices=FEATURES)
    return parser.parse_args()


def check_swap() -> None:
    """Fail if the machine has less swap than memory, as Valkey setup tips asks."""
    meminfo = dict(
        line.split(":", 1)
        for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines()
    )
    memory = int(meminfo["MemTotal"].split()[0])
    swap = int(meminfo["SwapTotal"].split()[0])
    if swap < memory:
        raise SystemExit(f"The machine has {swap} kB of swap and {memory} kB of memory.")


def main() -> None:
    """Write the files of the app, and enable its services."""
    arguments = parse()
    check_swap()
    app = arguments.app
    policy = ", ".join(
        f"{name}=(self)" if name in arguments.allow else f"{name}=()" for name in FEATURES
    )
    values = {
        "PRODUCTO": app,
        "DOMINIO": arguments.domain,
        "PERMISOS": policy,
        "MEMORIA": arguments.memory,
    }
    for name, target in TARGETS.items():
        path = Path(target.replace("PRODUCTO", app))
        write(HERE / name, path, values)
        if name in EXECUTABLES:
            path.chmod(0o755)
    # ADR-0078: whoever deploys adds the key of each receiver.
    receivers = Path(RECEIVERS.replace("PRODUCTO", app))
    receivers.parent.mkdir(parents=True, exist_ok=True)
    receivers.touch(exist_ok=True)
    skipped = tuple(f"PRODUCTO-{name}." for name in arguments.without)
    triggers = []
    for source in sorted(HERE.glob("PRODUCTO*")):
        if source.name.startswith(skipped):
            continue
        folder = SITES if source.suffix == ".caddy" else UNITS
        target = folder / source.name.replace("PRODUCTO", app)
        write(source, target, values)
        if target.suffix in (".timer", ".path"):
            triggers.append(target.name)
    subprocess.run(["systemd-sysusers"], check=True)
    subprocess.run(["systemd-tmpfiles", "--create", f"/etc/tmpfiles.d/{app}.conf"], check=True)
    subprocess.run(["sysctl", "--system"], check=True)
    subprocess.run(["systemctl", "daemon-reload"], check=True)
    # ADR-0077: the app has its own instance, apart from the one of the package.
    subprocess.run(["systemctl", "disable", "--now", "valkey-server.service"], check=True)
    subprocess.run(["systemctl", "enable", "--now", f"valkey-server@{app}.service"], check=True)
    # deploy.py starts the server once there is a current version.
    subprocess.run(["systemctl", "enable", f"{app}.service"], check=True)
    subprocess.run(["systemctl", "enable", "--now", *triggers], check=True)
    subprocess.run(["systemctl", "reload", "caddy.service"], check=True)
    subprocess.run(["sshd", "-t"], check=True)
    subprocess.run(["systemctl", "reload", "ssh.service"], check=True)


if __name__ == "__main__":
    main()
