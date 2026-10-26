r"""Install the users, database, units, Valkey, Caddy and ssh access of an app on this machine.

    python3 install.py <app> <domain> <memory> --admin <name> --key <key> --key <key> \
        [--without sweep|web|panel|landing] [--allow <feature>] [--extension <name>]

The first time it runs as root, and creates the account that administers the machine with its
keys and the password it asks for. Afterwards ssh only takes keys and root does not log in, so it
runs with sudo from that account, and --admin and --key only add keys.

From canone: plataformas/despliegue.md.
"""

import argparse
import getpass
import os
import pwd
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).parent
UNITS = Path("/etc/systemd/system")
SITES = Path("/etc/caddy/sites")
CREDENTIALS = Path("/etc/credstore.encrypted")
# The files that are not units or sites, and where each one goes.
TARGETS = {
    "sysusers.conf": "/etc/sysusers.d/PRODUCTO.conf",
    "valkey.conf": "/etc/valkey/valkey-PRODUCTO.conf",
    "valkey-group.conf": f"{UNITS}/valkey-server@PRODUCTO.service.d/group.conf",
    "sysctl.conf": "/etc/sysctl.d/valkey.conf",
    "tmpfiles.conf": "/etc/tmpfiles.d/PRODUCTO.conf",
    "sshd.conf": "/etc/ssh/sshd_config.d/00-PRODUCTO.conf",
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
    parser.add_argument("--extension", action="append", default=[], help="like postgis")
    parser.add_argument("--admin", help="the account that administers the machine")
    parser.add_argument("--key", action="append", default=[], help="a public key of --admin")
    return parser.parse_args()


def find_admin(arguments: argparse.Namespace) -> str:
    """Return the account that administers the machine, the way in once root cannot."""
    if shutil.which("sudo") is None:
        raise SystemExit("sudo is not installed, and root will not log in.")
    if arguments.admin is not None:
        if not arguments.key:
            raise SystemExit("--admin needs its keys in --key.")
        user = arguments.admin
    else:
        if arguments.key:
            raise SystemExit("--key needs the account in --admin.")
        user = os.environ.get("SUDO_USER")
        if user is None or user == "root":
            raise SystemExit(
                "Run install.py as root with --admin and --key, or with sudo from it."
            )
    app = arguments.app
    # ADR-0087: sysusers keeps an account that exists, and the app would run in sudo.
    if user in (app, f"{app}_owner", f"{app}-receiver"):
        raise SystemExit(f"{user} is an account of the app, not the one that administers.")
    return user


def check_keys(keys: list[str]) -> None:
    """Fail on a key that ssh-keygen cannot read."""
    for key in keys:
        subprocess.run(["ssh-keygen", "-l", "-f", "-"], input=key, text=True, check=True)


def create_admin(name: str, keys: list[str]) -> None:
    """Create the account in sudo with the password it asks for, and add the keys it lacks."""
    try:
        pwd.getpwnam(name)
    except KeyError:
        # ADR-0084: a key kept off your computer lets you in when that computer is lost.
        if len(keys) < 2:
            raise SystemExit("A new account needs two keys: yours and one kept elsewhere.")
        password = getpass.getpass(f"Password of {name}: ")
        if not password or password != getpass.getpass("Again: "):
            raise SystemExit("The passwords are empty or do not match.")
        subprocess.run(
            ["useradd", "--create-home", "--shell", "/bin/bash", "--groups", "sudo", name],
            check=True,
        )
        subprocess.run(["chpasswd"], input=f"{name}:{password}", text=True, check=True)
    account = pwd.getpwnam(name)
    folder = Path(account.pw_dir) / ".ssh"
    target = folder / "authorized_keys"
    folder.mkdir(mode=0o700, exist_ok=True)
    present = target.read_text(encoding="utf-8").splitlines() if target.is_file() else []
    lines = present + [key for key in keys if key not in present]
    if not any(line.strip() for line in lines):
        raise SystemExit(f"{target} has no key, and ssh will only take keys.")
    target.write_text("".join(f"{line}\n" for line in lines), encoding="utf-8")
    target.chmod(0o600)
    for path in (folder, target):
        os.chown(path, account.pw_uid, account.pw_gid)


def create_database(app: str, extensions: list[str]) -> None:
    """Create the database, its two roles and its extensions."""
    owner = f"{app}_owner"
    script = [
        f"SELECT 'CREATE ROLE {role} LOGIN' WHERE NOT EXISTS "
        f"(SELECT FROM pg_roles WHERE rolname = '{role}') \\gexec"
        for role in (app, owner)
    ]
    script += [
        (
            f"SELECT 'CREATE DATABASE {app} OWNER {owner}' WHERE NOT EXISTS "
            f"(SELECT FROM pg_database WHERE datname = '{app}') \\gexec"
        ),
        f"\\connect {app}",
        # An extension that is not trusted, like postgis, needs a superuser.
        *(f"CREATE EXTENSION IF NOT EXISTS {name};" for name in extensions),
    ]
    subprocess.run(
        ["runuser", "-u", "postgres", "--", "psql", "-X", "-q", "-v", "ON_ERROR_STOP=1"],
        input="\n".join(script),
        text=True,
        cwd="/",
        check=True,
    )


def encrypt(folder: str, name: str, value: str) -> None:
    """Write value as the credential app_<name> of folder, encrypted."""
    target = CREDENTIALS / folder / name
    target.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["systemd-creds", "encrypt", f"--name=app_{name}", "-", str(target)],
        input=value,
        text=True,
        check=True,
    )


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
    admin = find_admin(arguments)
    check_keys(arguments.key)
    create_admin(admin, arguments.key)
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
    # ADR-0085: each role logs in by peer, from the account of its name.
    create_database(app, arguments.extension)
    for folder, role in ((app, app), (f"{app}-migrate", f"{app}_owner")):
        encrypt(folder, "database_url", f"postgresql+asyncpg://{role}@/{app}?host=/run/postgresql")
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
    # ADR-0084: the console of the provider takes the account that administers, not root.
    subprocess.run(["passwd", "--lock", "root"], check=True)


if __name__ == "__main__":
    main()
