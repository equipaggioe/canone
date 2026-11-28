"""The other ends of Postfix in mail.sh: the app, the server of the recipients, and two senders.

    python3 mailserver.py app <folder> <secret>
    python3 mailserver.py mx <folder>
    python3 mailserver.py send <address> <sender> <recipient> <text>
    python3 mailserver.py submit <sender> <recipient>

app answers on 127.0.0.1:8000 as the app takes the notices, and keeps each one it takes. mx answers
on 192.0.2.1:25 as a server that announces DSN, refuses nadie@ with 5.1.1 and keeps each message
and each command. send hands a message from outside, over STARTTLS, and submit hands one as the
app does, on 127.0.0.1:25, with an 8-bit body and NOTIFY=SUCCESS,FAILURE.

plataformas/despliegue.md, «Correo».
"""

import http.server
import smtplib
import socketserver
import ssl
import sys
import uuid
from pathlib import Path


def app(folder: str, secret: str) -> None:
    """Keep each notice posted with the secret, and refuse the others."""

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            body = self.rfile.read(int(self.headers["Content-Length"]))
            taken = (
                self.path == "/api/email-notices"
                and self.headers["Authorization"] == f"Bearer {secret}"
                and self.headers["Content-Type"] == "message/rfc822"
            )
            if taken:
                (Path(folder) / f"{uuid.uuid4()}.eml").write_bytes(body)
            self.send_response(204 if taken else 401)
            self.end_headers()

        def log_message(self, *_: object) -> None:
            """Keep the output of the test clean."""

    http.server.ThreadingHTTPServer(("127.0.0.1", 8000), Handler).serve_forever()


def mx(folder: str) -> None:
    """Answer as a server that announces DSN, and keep what it receives."""

    class Handler(socketserver.StreamRequestHandler):
        def handle(self) -> None:
            def answer(line: str) -> None:
                self.wfile.write(f"{line}\r\n".encode())

            answer("220 mx.remote.example ESMTP")
            commands = []
            while line := self.rfile.readline():
                text = line.decode("utf-8", "replace").rstrip("\r\n")
                commands.append(text)
                verb = text[:4].upper()
                if verb == "EHLO":
                    answer("250-mx.remote.example")
                    answer("250 DSN")
                elif verb == "RCPT":
                    answer("550 5.1.1 no such user" if "nadie@" in text else "250 OK")
                elif verb == "DATA":
                    answer("354 go on")
                    data = b""
                    while (chunk := self.rfile.readline()) not in (b".\r\n", b""):
                        data += chunk
                    (Path(folder) / f"{uuid.uuid4()}.eml").write_bytes(data)
                    answer("250 OK")
                elif verb == "QUIT":
                    answer("221 bye")
                    break
                else:
                    answer("250 OK")
            with (Path(folder) / "commands.log").open("a", encoding="utf-8") as log:
                log.write("".join(f"{command}\n" for command in commands))

    socketserver.ThreadingTCPServer.allow_reuse_address = True
    socketserver.ThreadingTCPServer(("192.0.2.1", 25), Handler).serve_forever()


def send(address: str, sender: str, recipient: str, text: str) -> None:
    """Hand a message from outside, over STARTTLS, without checking the certificate."""
    with smtplib.SMTP(address, 25, local_hostname="remote.example", timeout=30) as client:
        # The certificate of ssl-cert names no host.
        client.starttls(context=ssl._create_unverified_context())  # noqa: S323
        client.sendmail(sender, [recipient], f"Subject: {text}\r\n\r\n{text}\r\n")


def submit(sender: str, recipient: str) -> None:
    """Hand a message as the app does, with an 8-bit body and a notice of each result."""
    message = (
        "Subject: prueba\r\nMIME-Version: 1.0\r\n"
        "Content-Type: text/plain; charset=utf-8\r\nContent-Transfer-Encoding: 8bit\r\n\r\n"
        "Contraseña de ejemplo\r\n"
    ).encode()
    with smtplib.SMTP("127.0.0.1", 25, timeout=30) as client:
        client.sendmail(
            sender, [recipient], message, rcpt_options=["NOTIFY=SUCCESS,FAILURE"]
        )


if __name__ == "__main__":
    command, *arguments = sys.argv[1:]
    {"app": app, "mx": mx, "send": send, "submit": submit}[command](*arguments)
