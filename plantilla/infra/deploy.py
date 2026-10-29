r"""Install a version of the server and the web on this machine.

    sudo python3 /usr/local/lib/PRODUCTO/deploy.py v1.4.0

Before that, on the machine that holds the key:

    gh release download v1.4.0 -p "*.sha256"
    ssh-keygen -Y sign -n deploy -f ~/.ssh/id_ed25519 \
        PRODUCTO-v1.4.0.sha256
    gh release upload v1.4.0 PRODUCTO-v1.4.0.sha256.sig

install.py installs it with the data of the app. From canone:
plataformas/despliegue.md, «Versiones».
"""

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

# install.py writes the owner of the repository on GitHub, whether it
# is private, and the desktop installers that each release brings.
APP = "PRODUCTO"
REPO = "DUENO/PRODUCTO"
PRIVATE: bool = PRIVADO
DESKTOP: tuple[str, ...] = INSTALABLES
# A private repository downloads with a read-only token, which
# credentials.py encrypts.
TOKEN = Path("/etc/credstore.encrypted") / f"{APP}-deploy" / "github_token"
# ADR-0106: the only unit of the server that install.py installs.
SERVICE = f"{APP}.service"
MIGRATE = "PRODUCTO-migrate@{}.service"
HEALTH_SECONDS = 30
KEEP = 5

ROOT = Path("/srv") / APP
RELEASES = ROOT / "releases"
CURRENT = ROOT / "current"
DOWNLOADS = ROOT / "downloads"
SIGNERS = Path("/etc") / APP / "allowed_signers"
VERSION = re.compile(r"v\d+\.\d+\.\d+")
# ADR-0077: the server always listens on 8000.
HEALTH = "http://127.0.0.1:8000/api/health"
API = f"https://api.github.com/repos/{REPO}"


class DeployError(Exception):
    """A step failed and the deployment stopped."""


class Unhealthy(DeployError):
    """The health check did not answer 204 in time."""


def run(*command: str, cwd: Path | None = None) -> str:
    """Run a command and return its output; fail on a nonzero exit."""
    return subprocess.run(command, cwd=cwd, check=True, capture_output=True, text=True).stdout


def request(url: str, accept: str, token: str | None) -> urllib.request.Request:
    """Build a GitHub request, with the token if there is one."""
    result = urllib.request.Request(url, headers={"Accept": accept})
    if token is not None:
        # Downloads redirect to another host, which must not receive
        # the token.
        result.add_unredirected_header("Authorization", f"Bearer {token}")
    return result


def release_assets(version: str, token: str | None) -> dict[str, str]:
    """Return the API url of each asset of the release, by name."""
    url = f"{API}/releases/tags/{version}"
    with urllib.request.urlopen(request(url, "application/vnd.github+json", token)) as response:
        release = json.load(response)
    return {asset["name"]: asset["url"] for asset in release["assets"]}


def download(url: str, target: Path, token: str | None) -> None:
    """Save the asset at url into target."""
    with urllib.request.urlopen(request(url, "application/octet-stream", token)) as response:
        with target.open("wb") as file:
            shutil.copyfileobj(response, file)


def verify(checksum: Path, signature: Path) -> None:
    """Check that a key of SIGNERS signed the checksum."""
    found = run("ssh-keygen", "-Y", "find-principals", "-f", str(SIGNERS), "-s", str(signature))
    command = ["ssh-keygen", "-Y", "verify", "-f", str(SIGNERS), "-n", "deploy"]
    command += ["-I", found.split()[0], "-s", str(signature)]
    with checksum.open("rb") as data:
        subprocess.run(command, stdin=data, check=True, capture_output=True, text=True)


def checked(name: str, path: Path, sums: dict[str, str]) -> None:
    """Fail unless the signed checksums give path as name."""
    # The checksums of another version do not name this artifact.
    if name not in sums:
        raise DeployError(f"the signed checksums do not name {name}")
    with path.open("rb") as file:
        actual = hashlib.file_digest(file, "sha256").hexdigest()
    if actual != sums[name]:
        raise DeployError(f"{name} does not match its SHA-256")


def fetch(
    version: str, assets: dict[str, str], folder: Path, token: str | None
) -> tuple[Path, dict[str, str]]:
    """Download the artifact and the signed checksums of every file."""
    archive = folder / f"{APP}-{version}.tar.gz"
    checksum = folder / f"{APP}-{version}.sha256"
    signature = folder / f"{APP}-{version}.sha256.sig"
    for path in (archive, checksum, signature):
        download(assets[path.name], path, token)
    verify(checksum, signature)
    lines = checksum.read_text(encoding="utf-8").splitlines()
    sums = {name: expected for expected, name in map(str.split, lines)}
    checked(archive.name, archive, sums)
    return archive, sums


def install(archive: Path, target: Path) -> None:
    """Unpack the artifact into target and create its virtual env."""
    unpacked = archive.parent / "release"
    with tarfile.open(archive) as tar:
        tar.extractall(unpacked, filter="data")
    unpacked.rename(target)
    run("uv", "sync", "--locked", "--no-dev", cwd=target / "server")


def stage(assets: dict[str, str], sums: dict[str, str], target: Path, token: str | None) -> None:
    """Download and check the desktop installers into the release."""
    folder = target / "downloads"
    folder.mkdir()
    for name in DESKTOP:
        download(assets[name], folder / name, token)
        checked(name, folder / name, sums)


def heads(release: Path) -> str:
    """Return the Alembic heads of a release, read from its scripts."""
    server = release / "server"
    return run(str(server / ".venv/bin/alembic"), "heads", cwd=server)


def point(target: Path) -> None:
    """Switch current to target in one rename."""
    link = ROOT / "current.new"
    link.unlink(missing_ok=True)
    link.symlink_to(target)
    link.replace(CURRENT)


def restart() -> None:
    """Restart the units and wait for the health check."""
    url = HEALTH
    run("systemctl", "restart", SERVICE)
    problem = "no answer"
    for _ in range(HEALTH_SECONDS):
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                if response.status == 204:
                    return
                problem = f"status {response.status}"
        except OSError as error:
            problem = str(error)
        time.sleep(1)
    raise Unhealthy(f"{url}: {problem}")


def migrate(version: str, target: Path, previous: Path | None, migrates: bool) -> None:
    """Migrate to version, with the server stopped if it changes."""
    # The previous code must not run on the migrated schema.
    if migrates:
        run("systemctl", "stop", SERVICE)
    try:
        run("systemctl", "start", MIGRATE.format(version))
    except subprocess.CalledProcessError:
        # env.py runs every migration in one transaction: the
        # schema did not change.
        shutil.rmtree(target)
        if migrates and previous is not None:
            restart()
        raise


def publish(target: Path) -> None:
    """Move the installers of target to those that Caddy serves."""
    DOWNLOADS.mkdir(exist_ok=True)
    staged = target / "downloads"
    for name in DESKTOP:
        (staged / name).replace(DOWNLOADS / name)
    staged.rmdir()


def prune() -> None:
    """Delete the releases older than the KEEP newest, never current."""
    active = CURRENT.resolve()
    installed = [path for path in RELEASES.iterdir() if VERSION.fullmatch(path.name)]
    installed.sort(key=lambda path: tuple(map(int, path.name[1:].split("."))), reverse=True)
    for path in installed[KEEP:]:
        if path != active:
            shutil.rmtree(path)


def deploy(version: str) -> None:
    """Install version and make it current, or say why not."""
    target = RELEASES / version
    if target.exists():
        raise DeployError(f"{target} already exists")
    previous = CURRENT.resolve() if CURRENT.exists() else None
    token = run("systemd-creds", "decrypt", str(TOKEN), "-").strip() if PRIVATE else None
    assets = release_assets(version, token)
    artifact = f"{APP}-{version}"
    names = {f"{artifact}.tar.gz", f"{artifact}.sha256", f"{artifact}.sha256.sig", *DESKTOP}
    missing = names - assets.keys()
    if missing:
        raise DeployError(f"the release {version} lacks {', '.join(sorted(missing))}")
    RELEASES.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(dir=RELEASES) as folder:
            archive, sums = fetch(version, assets, Path(folder), token)
            install(archive, target)
        stage(assets, sums, target, token)
        migrates = previous is None or heads(previous) != heads(target)
    except BaseException:
        if target.exists():
            shutil.rmtree(target)
        raise
    migrate(version, target, previous, migrates)
    point(target)
    try:
        restart()
    except Unhealthy as error:
        if migrates or previous is None:
            message = f"{error}. It ran migrations, so current stays on {version}"
            raise DeployError(message) from error
        point(previous)
        restart()
        raise DeployError(f"{error}. current is back on {previous.name}") from error
    publish(target)
    prune()


def main() -> None:
    """Parse the version and report how the deployment ended."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("version", help="the tag, like v1.4.0")
    version = parser.parse_args().version
    if not VERSION.fullmatch(version):
        sys.exit(f"{version} is not a tag like v1.4.0")
    try:
        deploy(version)
    except subprocess.CalledProcessError as error:
        sys.exit(f"{' '.join(error.cmd)} failed:\n{error.stderr}")
    except urllib.error.HTTPError as error:
        sys.exit(f"{error.url}: {error.code} {error.reason}")
    except DeployError as error:
        sys.exit(str(error))
    print(f"{version} is live")


if __name__ == "__main__":
    main()
