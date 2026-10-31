"""Listen on the ports of the server, or probe them from outside.

    python3 network.py listen
    python3 network.py probe <address> [turn]
    python3 network.py out <address>
    python3 network.py invalid <address> <source>
    python3 network.py tunneled <address> <native source>

plataformas/despliegue.md, «Firewall».
"""

import socket
import sys
import threading
import time

# ADR-0093: what comes in, and what does not.
TCP_OPEN = (22, 80, 443)
TCP_CLOSED = (8000, 5432)
UDP_OPEN = (443,)
UDP_CLOSED = (53,)
# ADR-0096: what comes in only with TURN.
TURN_TCP = (3478,)
TURN_UDP = (3478, 49152, 65535)
# RFC 8656, 21.4: TURN takes no request from Teredo or 6to4.
TUNNELED = ("2001:0:102:302::2", "2002:102:302::2")
TIMEOUT = 2


def accept(server: socket.socket) -> None:
    """Accept connections forever."""
    while True:
        server.accept()[0].close()


def echo(server: socket.socket) -> None:
    """Send back each datagram."""
    while True:
        data, sender = server.recvfrom(64)
        server.sendto(data, sender)


def listen() -> None:
    """Listen on every port the probe tries."""
    for port in TCP_OPEN + TCP_CLOSED + TURN_TCP:
        server = socket.create_server(("0.0.0.0", port))
        threading.Thread(target=accept, args=(server,), daemon=True).start()
    for port in UDP_OPEN + UDP_CLOSED + TURN_UDP:
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server.bind(("0.0.0.0", port))
        threading.Thread(target=echo, args=(server,), daemon=True).start()
    server = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    server.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
    server.bind(("::", TURN_UDP[0]))
    threading.Thread(target=echo, args=(server,), daemon=True).start()
    time.sleep(3600)


def reaches_tcp(address: str, port: int) -> bool:
    """Tell whether a TCP connection gets through."""
    try:
        socket.create_connection((address, port), TIMEOUT).close()
    except OSError:
        return False
    return True


def reaches_udp(address: str, port: int) -> bool:
    """Tell whether a datagram gets through and back."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
        client.settimeout(TIMEOUT)
        client.sendto(b"probe", (address, port))
        try:
            client.recvfrom(64)
        except OSError:
            return False
    return True


def reaches_udp6(address: str, port: int, source: str) -> bool:
    """Tell whether a datagram from the source gets through and back."""
    with socket.socket(socket.AF_INET6, socket.SOCK_DGRAM) as client:
        client.settimeout(TIMEOUT)
        client.bind((source, 0))
        client.sendto(b"probe", (address, port))
        try:
            client.recvfrom(64)
        except OSError:
            return False
    return True


def probe(address: str, *turn: str) -> None:
    """Fail unless exactly the open ports get through, with those of TURN if turn is given."""
    wrong = [
        f"{kind} {port}"
        for kind, reaches, ports, expected in (
            ("tcp", reaches_tcp, TCP_OPEN, True),
            ("tcp", reaches_tcp, TCP_CLOSED, False),
            ("udp", reaches_udp, UDP_OPEN, True),
            ("udp", reaches_udp, UDP_CLOSED, False),
            ("tcp", reaches_tcp, TURN_TCP, bool(turn)),
            ("udp", reaches_udp, TURN_UDP, bool(turn)),
        )
        for port in ports
        if reaches(address, port) != expected
    ]
    if wrong:
        raise SystemExit(f"these ports do not behave as the ruleset says: {', '.join(wrong)}")


def out(address: str) -> None:
    """Fail unless a connection that goes out is answered, here with a refusal."""
    try:
        socket.create_connection((address, 9), TIMEOUT)
    except ConnectionRefusedError:
        return
    except OSError as error:
        raise SystemExit(f"a connection that goes out is filtered: {error}") from error


def invalid(address: str, source: str) -> None:
    """Fail if an open port answers a source that is never valid."""
    try:
        socket.create_connection((address, TCP_OPEN[0]), TIMEOUT, (source, 0)).close()
    except OSError:
        return
    raise SystemExit(f"a connection from {source} gets through")


def tunneled(address: str, native: str) -> None:
    """Fail unless TURN answers a native IPv6 source, and no tunneled one."""
    expected = {native: True} | dict.fromkeys(TUNNELED, False)
    wrong = [
        source
        for source, reaches in expected.items()
        if reaches_udp6(address, TURN_UDP[0], source) != reaches
    ]
    if wrong:
        raise SystemExit(f"these sources do not behave as the TURN rules say: {', '.join(wrong)}")


if __name__ == "__main__":
    command, *arguments = sys.argv[1:]
    commands = {
        "listen": listen,
        "probe": probe,
        "out": out,
        "invalid": invalid,
        "tunneled": tunneled,
    }
    commands[command](*arguments)
