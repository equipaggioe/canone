r"""Install the users, database, units, Valkey, Caddy, firewall, journal, coturn and ssh of an app.

    python3 install.py <app> <domain> <memory> --admin <name> --key <key> --key <key> \
        [--without sweep|web|panel|landing] [--allow <feature>] [--extension <name>] \
        [--turn [--turn-ip <public ipv4>]] \
        [--logs <host:port> --logs-key <key of equipaggio> --logs-ip <address in the tunnel>]

The first time it runs as root, and creates the account that administers the machine with its
keys and the password it asks for. Afterwards ssh only takes keys and root does not log in, so it
runs with sudo from that account, and --admin and --key only add keys.

From canone: plataformas/despliegue.md.
"""

import argparse
import getpass
import ipaddress
import json
import os
import pwd
import secrets
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
    "backup-request": "/usr/local/lib/PRODUCTO/backup-request",
    "Caddyfile": "/etc/caddy/Caddyfile",
    "nftables.conf": "/etc/nftables.conf",
    "20auto-upgrades": "/etc/apt/apt.conf.d/20auto-upgrades",
    "journald.conf": "/etc/systemd/journald.conf.d/00-PRODUCTO.conf",
    "postgresql.conf": "/etc/postgresql/17/main/conf.d/PRODUCTO.conf",
}
# The files that run, and the file that holds the keys of the receivers.
EXECUTABLES = ("backup-request",)
RECEIVERS = "/etc/PRODUCTO/receivers"
# The files of coturn and its ports, only with --turn.
TURN = {"turnserver.conf": "/etc/turnserver.conf", "turn.nft": "/etc/nftables.d/turn.nft"}
# The tunnel to equipaggio and its uploader, only with --logs.
LOGS = {
    "logs.conf": "/etc/wireguard/logs.conf",
    "journal-upload.conf": "/etc/systemd/journal-upload.conf.d/00-PRODUCTO.conf",
    "journal-upload-retry.conf": f"{UNITS}/systemd-journal-upload.service.d/PRODUCTO.conf",
}
UPLOADER = Path("/usr/lib/systemd/systemd-journal-upload")
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
    parser.add_argument("--turn", action="store_true", help="the app relays calls with coturn")
    parser.add_argument(
        "--turn-ip",
        type=ipaddress.IPv4Address,
        help="the public IPv4 of the machine, when its interface has only a private one",
    )
    parser.add_argument("--logs", help="the WireGuard endpoint of equipaggio, like host:51820")
    parser.add_argument("--logs-key", help="the WireGuard public key of equipaggio")
    parser.add_argument(
        "--logs-ip", type=ipaddress.IPv4Address, help="the address equipaggio gave the machine"
    )
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


def turn_secret() -> str:
    """Return the secret of coturn, new the first time: a credential handed out keeps working."""
    for line in Path(TURN["turnserver.conf"]).read_text(encoding="utf-8").splitlines():
        if line.startswith("static-auth-secret="):
            return line.removeprefix("static-auth-secret=")
    return secrets.token_urlsafe(32)


def check_logs(arguments: argparse.Namespace) -> None:
    """Fail on --logs without its tools or its two other flags, or on those flags without it.

    Fail without --logs on a machine that sends: equipaggio knows the key of its tunnel.
    """
    given = (arguments.logs_key is not None, arguments.logs_ip is not None)
    if arguments.logs is None:
        if any(given):
            raise SystemExit("--logs-key and --logs-ip need --logs.")
        if Path(LOGS["logs.conf"]).exists():
            raise SystemExit(
                f"This machine sends its journal to equipaggio, so it needs --logs. To stop, "
                f"disable wg-quick@logs and systemd-journal-upload, and delete {LOGS['logs.conf']}."
            )
        return
    if not all(given):
        raise SystemExit("--logs needs --logs-key and --logs-ip.")
    if shutil.which("wg-quick") is None or not UPLOADER.is_file():
        raise SystemExit(
            "wireguard-tools or systemd-journal-remote is not installed, and --logs needs them."
        )


def logs_key() -> str:
    """Return the private key of the tunnel, new the first time: equipaggio knows its pair."""
    config = Path(LOGS["logs.conf"])
    if config.is_file():
        for line in config.read_text(encoding="utf-8").splitlines():
            if line.startswith("PrivateKey = "):
                return line.removeprefix("PrivateKey = ")
    key = subprocess.run(["wg", "genkey"], capture_output=True, text=True, check=True)
    return key.stdout.strip()


def private_ip() -> str:
    """Return the IPv4 the machine goes out to the internet with, behind the NAT of --turn-ip."""
    # Any address of the internet takes the default route, and route get sends nothing.
    route = subprocess.run(
        ["ip", "-json", "-4", "route", "get", "192.0.2.1"],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(route.stdout)[0]["prefsrc"]


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
    # ADR-0092: without it, 20auto-upgrades turns on nothing and nothing says so.
    if shutil.which("unattended-upgrade") is None:
        raise SystemExit("unattended-upgrades is not installed, and Debian would not update.")
    if arguments.turn and shutil.which("turnserver") is None:
        raise SystemExit("coturn is not installed, and --turn needs it.")
    if arguments.turn_ip is not None and not arguments.turn:
        raise SystemExit("--turn-ip needs --turn.")
    check_logs(arguments)
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
        "SECRETO": turn_secret() if arguments.turn else "",
        "LLAVE": logs_key() if arguments.logs else "",
        "TUNEL": str(arguments.logs_ip),
        "CENTRAL": arguments.logs_key or "",
        "EXTREMO": arguments.logs or "",
    }
    for name, target in TARGETS.items():
        path = Path(target.replace("PRODUCTO", app))
        write(HERE / name, path, values)
        if name in EXECUTABLES:
            path.chmod(0o755)
    # ADR-0096: coturn relays only for an app with calls, and its secret is not for everyone.
    if arguments.turn:
        for name, target in TURN.items():
            write(HERE / name, Path(target), values)
        # ADR-0096: behind a NAT, coturn hands out its public address, not the private one.
        if arguments.turn_ip is not None:
            with Path(TURN["turnserver.conf"]).open("a", encoding="utf-8") as config:
                config.write(f"external-ip={arguments.turn_ip}/{private_ip()}\n")
        shutil.chown(TURN["turnserver.conf"], "root", "turnserver")
        Path(TURN["turnserver.conf"]).chmod(0o640)
        encrypt(app, "turn_secret", values["SECRETO"])
    else:
        Path(TURN["turn.nft"]).unlink(missing_ok=True)
    # ADR-0100: the journal goes to equipaggio only from a machine whose key it knows.
    if arguments.logs:
        for name, target in LOGS.items():
            write(HERE / name, Path(target.replace("PRODUCTO", app)), values)
        Path(LOGS["logs.conf"]).chmod(0o600)
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
    # ADR-0093: what comes in is denied unless the ruleset lists it.
    subprocess.run(["systemctl", "enable", "nftables.service"], check=True)
    subprocess.run(["systemctl", "reload-or-restart", "nftables.service"], check=True)
    # ADR-0085: each role logs in by peer, from the account of its name.
    create_database(app, arguments.extension)
    for folder, role in ((app, app), (f"{app}-migrate", f"{app}_owner")):
        encrypt(folder, "database_url", f"postgresql+asyncpg://{role}@/{app}?host=/run/postgresql")
    subprocess.run(["systemctl", "daemon-reload"], check=True)
    subprocess.run(["systemctl", "restart", "systemd-journald.service"], check=True)
    subprocess.run(["systemctl", "reload", "postgresql@17-main.service"], check=True)
    # ADR-0077: the app has its own instance, apart from the one of the package.
    subprocess.run(["systemctl", "disable", "--now", "valkey-server.service"], check=True)
    subprocess.run(["systemctl", "enable", "--now", f"valkey-server@{app}.service"], check=True)
    # deploy.py starts the server once there is a current version.
    subprocess.run(["systemctl", "enable", f"{app}.service"], check=True)
    subprocess.run(["systemctl", "enable", "--now", *triggers], check=True)
    subprocess.run(["systemctl", "reload", "caddy.service"], check=True)
    if arguments.turn:
        subprocess.run(["systemctl", "enable", "coturn.service"], check=True)
        subprocess.run(["systemctl", "restart", "coturn.service"], check=True)
    if arguments.logs:
        for unit in ("wg-quick@logs.service", "systemd-journal-upload.service"):
            subprocess.run(["systemctl", "enable", unit], check=True)
            subprocess.run(["systemctl", "restart", unit], check=True)
        public = subprocess.run(
            ["wg", "pubkey"], input=values["LLAVE"], capture_output=True, text=True, check=True
        )
        print(f"The key of this machine, for equipaggio: {public.stdout.strip()}")
    subprocess.run(["sshd", "-t"], check=True)
    subprocess.run(["systemctl", "reload", "ssh.service"], check=True)
    # ADR-0084: the console of the provider takes the account that administers, not root.
    subprocess.run(["passwd", "--lock", "root"], check=True)


if __name__ == "__main__":
    main()
