r"""Add a public key to the authorized_keys of root, the way in before install.py.

    python3 authorize.py '<public key>'

A new machine of a provider may take only the password of root. Whoever prepares it runs this once
as root, entering with that password, and from then on packages.py, swap.py and install.py enter
with the key. It adds the key once, and fails without writing anything on a key that ssh-keygen
cannot read.

From canone: plataformas/despliegue.md, «SSH».
"""

import argparse
import os
import pwd
import subprocess
from pathlib import Path


def main() -> None:
    """Add the key it receives, unless it is there."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("key", help="the public key, as in its .pub file")
    key = parser.parse_args().key.strip()
    if os.geteuid() != 0:
        raise SystemExit("authorize.py runs as root.")
    check = subprocess.run(
        ["ssh-keygen", "-l", "-f", "-"], input=key, capture_output=True, text=True, check=False
    )
    if check.returncode != 0 or "\n" in key:
        raise SystemExit("That is not a public key, and nothing was written.")
    folder = Path(pwd.getpwuid(0).pw_dir) / ".ssh"
    folder.mkdir(mode=0o700, exist_ok=True)
    folder.chmod(0o700)
    target = folder / "authorized_keys"
    present = target.read_text(encoding="utf-8").splitlines() if target.is_file() else []
    if key not in present:
        target.write_text("".join(f"{line}\n" for line in [*present, key]), encoding="utf-8")
    target.chmod(0o600)


if __name__ == "__main__":
    main()
