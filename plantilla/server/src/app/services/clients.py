"""The public clients of the authorization code, and their return."""

from dataclasses import dataclass
from urllib.parse import urlsplit

from app.config import settings

LOOPBACK = "127.0.0.1"
# The client of the flow that the server runs for the web, in its tab.
WEB = "web"


@dataclass(frozen=True)
class Registration:
    """A public client: its ID and its full redirect URIs, no secret."""

    client_id: str
    redirect_uris: frozenset[str]


# Each app of the desktop, with the loopback URI it listens on: the
# port of a loopback URI may be any.
CLIENTS: dict[str, Registration] = {}


def surfaces() -> tuple[str, ...]:
    """Return the hosts of the web surfaces of domain."""
    return (settings.domain, f"app.{settings.domain}", f"panel.{settings.domain}")


def web_return(host: str) -> str:
    """Return the URI where the web flow of a surface comes back."""
    return f"https://{host}/api/auth/web/return"


def registration(client_id: str) -> Registration | None:
    """Find a client: the web, or an app of CLIENTS."""
    if client_id == WEB:
        return Registration(WEB, frozenset(web_return(host) for host in surfaces()))
    return CLIENTS.get(client_id)


def is_loopback(uri: str) -> bool:
    """Tell whether a URI returns to the loopback of the desktop."""
    parts = urlsplit(uri)
    return parts.scheme == "http" and parts.hostname == LOOPBACK


def matches(registered: str, presented: str) -> bool:
    """Compare a redirect URI as a string, but any loopback port."""
    if not is_loopback(registered):
        return presented == registered
    want, have = urlsplit(registered), urlsplit(presented)
    try:
        have.port
    except ValueError:
        return False
    same = (want.scheme, want.hostname, want.path, want.query, want.fragment)
    return same == (
        have.scheme,
        have.hostname,
        have.path,
        have.query,
        have.fragment,
    )


def redirect_uri(client: Registration, presented: str | None) -> str | None:
    """Return the URI to come back to, or none if it is not registered.

    Without one, a client with a single URI, not loopback, uses it.
    """
    if presented is None:
        only = next(iter(client.redirect_uris)) if len(client.redirect_uris) == 1 else None
        return only if only is not None and not is_loopback(only) else None
    return presented if any(matches(uri, presented) for uri in client.redirect_uris) else None
