"""Listen on the ports of the server, or probe them from outside.

    python3 network.py listen
    python3 network.py probe <address>
    python3 network.py out <address>

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
    for port in TCP_OPEN + TCP_CLOSED:
        server = socket.create_server(("0.0.0.0", port))
        threading.Thread(target=accept, args=(server,), daemon=True).start()
    for port in UDP_OPEN + UDP_CLOSED:
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server.bind(("0.0.0.0", port))
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


def probe(address: str) -> None:
    """Fail unless exactly the open ports get through."""
    wrong = [
        f"{kind} {port}"
        for kind, reaches, ports, expected in (
            ("tcp", reaches_tcp, TCP_OPEN, True),
            ("tcp", reaches_tcp, TCP_CLOSED, False),
            ("udp", reaches_udp, UDP_OPEN, True),
            ("udp", reaches_udp, UDP_CLOSED, False),
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


if __name__ == "__main__":
    command, *arguments = sys.argv[1:]
    {"listen": listen, "probe": probe, "out": out}[command](*arguments)
