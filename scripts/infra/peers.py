"""Fail unless coturn denies exactly the blocks that the IANA registries mark as not reachable.

    python3 peers.py <turnserver.conf> <folder of the registries>

plataformas/despliegue.md, «Coturn».
"""

import csv
import ipaddress
import re
import sys
from pathlib import Path

REGISTRIES = ("iana-ipv4-special-registry.csv", "iana-ipv6-special-registry.csv")


def registered(folder: Path) -> set[tuple[str, str]]:
    """Return the first and last address of each block that is not globally reachable."""
    blocks = set()
    for name in REGISTRIES:
        with (folder / name).open(encoding="utf-8", newline="") as registry:
            for row in csv.DictReader(registry):
                if not row["Globally Reachable"].startswith("False"):
                    continue
                for block in row["Address Block"].split(","):
                    network = ipaddress.ip_network(re.sub(r"\[\d+\]", "", block).strip())
                    # ADR-0096: coturn reads the unspecified address as any address.
                    if network.num_addresses == 1 and int(network[0]) == 0:
                        continue
                    blocks.add((str(network[0]), str(network[-1])))
    return blocks


def denied(config: Path) -> set[tuple[str, str]]:
    """Return the first and last address of each denied-peer-ip of the config."""
    blocks = set()
    for line in config.read_text(encoding="utf-8").splitlines():
        if line.startswith("denied-peer-ip="):
            first, last = line.removeprefix("denied-peer-ip=").split("-")
            blocks.add((str(ipaddress.ip_address(first)), str(ipaddress.ip_address(last))))
    return blocks


def main(config: str, folder: str) -> None:
    """Compare the config with the registries."""
    expected = registered(Path(folder))
    actual = denied(Path(config))
    wrong = [f"missing {first}-{last}" for first, last in sorted(expected - actual)]
    wrong += [f"extra {first}-{last}" for first, last in sorted(actual - expected)]
    if wrong:
        raise SystemExit(f"denied-peer-ip does not follow the registries: {', '.join(wrong)}")


if __name__ == "__main__":
    main(*sys.argv[1:])
