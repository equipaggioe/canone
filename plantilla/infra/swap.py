r"""Leave as much swap as memory, which install.py asks for, in /swapfile.

    sudo python3 swap.py

It creates /swapfile with what the swap there is lacks, and adds it to /etc/fstab. A /swapfile
that falls short is made again. With as much swap as memory, it changes nothing.

From canone: plataformas/despliegue.md, «Máquina».
"""

import os
import subprocess
from pathlib import Path

SWAPFILE = Path("/swapfile")
FSTAB = Path("/etc/fstab")
LINE = f"{SWAPFILE} none swap sw 0 0"


def kibibytes(field: str) -> int:
    """Return a field of /proc/meminfo, in KiB."""
    for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
        name, _, value = line.partition(":")
        if name == field:
            return int(value.split()[0])
    raise SystemExit(f"/proc/meminfo has no {field}.")


def active() -> bool:
    """Return whether /swapfile is in use."""
    names = subprocess.run(
        ["swapon", "--show=NAME", "--noheadings"], capture_output=True, text=True, check=True
    ).stdout.split()
    return str(SWAPFILE) in names


def remember() -> None:
    """Add /swapfile to /etc/fstab, unless it is there."""
    text = FSTAB.read_text(encoding="utf-8") if FSTAB.exists() else ""
    if any(line.split()[:1] == [str(SWAPFILE)] for line in text.splitlines()):
        return
    if text and not text.endswith("\n"):
        text += "\n"
    FSTAB.write_text(f"{text}{LINE}\n", encoding="utf-8")


def main() -> None:
    """Create /swapfile with what the swap lacks to match the memory."""
    if os.geteuid() != 0:
        raise SystemExit("swap.py runs as root: run it with sudo.")
    memory = kibibytes("MemTotal")
    if kibibytes("SwapTotal") >= memory:
        print("There is already as much swap as memory.")
        return
    if active():
        subprocess.run(["swapoff", str(SWAPFILE)], check=True)
    SWAPFILE.unlink(missing_ok=True)
    missing = (memory - kibibytes("SwapTotal")) // 1024 + 1
    subprocess.run(["fallocate", "-l", f"{missing}M", str(SWAPFILE)], check=True)
    SWAPFILE.chmod(0o600)
    subprocess.run(["mkswap", str(SWAPFILE)], check=True, stdout=subprocess.DEVNULL)
    subprocess.run(["swapon", str(SWAPFILE)], check=True)
    remember()
    print(f"Swap of {missing} MiB in {SWAPFILE}.")


if __name__ == "__main__":
    main()
