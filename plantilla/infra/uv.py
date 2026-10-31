r"""Install uv at /usr/local/bin/uv, the version deploy.py creates each environment with.

    sudo python3 uv.py

Debian 13 has no uv. It runs before the first deploy.py, and again when the version changes.

From canone: plataformas/despliegue.md, «Máquina».
"""

import hashlib
import platform
import shutil
import tarfile
import tempfile
import urllib.request
from pathlib import Path

# ADR-0090: the one exact version of python.md, which each pyproject.toml requires.
VERSION = "0.13.5"
# ADR-0110: the SHA-256 of the archive of each processor, from the release of that version.
CHECKSUMS = {
    "x86_64": "f68d291c75783122dad58ab77def0e13f3233f358731db5d6d7e8715603b928f",
    "aarch64": "4bb69cf95ed13f23713bb7bc09f241896ea0c75b7c557e615a20604b82f9c403",
}
RELEASES = "https://github.com/astral-sh/uv/releases/download"
TARGET = Path("/usr/local/bin/uv")


def download(name: str, expected: str, folder: Path) -> Path:
    """Download the archive name of VERSION into folder, and fail unless it has its SHA-256."""
    archive = folder / f"{name}.tar.gz"
    with urllib.request.urlopen(f"{RELEASES}/{VERSION}/{archive.name}") as response:
        with archive.open("wb") as file:
            shutil.copyfileobj(response, file)
    with archive.open("rb") as file:
        actual = hashlib.file_digest(file, "sha256").hexdigest()
    if actual != expected:
        raise SystemExit(f"{archive.name} does not match its SHA-256, and nothing was installed.")
    return archive


def main() -> None:
    """Install the uv of VERSION, in place of the one there is."""
    machine = platform.machine()
    if machine not in CHECKSUMS:
        raise SystemExit(f"uv {VERSION} has no archive for {machine}.")
    name = f"uv-{machine}-unknown-linux-gnu"
    # Next to the target, so the rename replaces it at once.
    new = TARGET.with_name("uv.new")
    with tempfile.TemporaryDirectory() as folder:
        archive = download(name, CHECKSUMS[machine], Path(folder))
        with tarfile.open(archive) as tar:
            binary = tar.extractfile(f"{name}/uv")
            if binary is None:
                raise SystemExit(f"{archive.name} has no uv.")
            with new.open("wb") as file:
                shutil.copyfileobj(binary, file)
    new.chmod(0o755)
    new.replace(TARGET)


if __name__ == "__main__":
    main()
