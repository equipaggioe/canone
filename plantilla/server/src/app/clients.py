"""The apps of the desktop that sign in with the authorization code.

autenticacion.md: each repository registers its own, or none.
"""

# The full redirect URIs of each client ID, on loopback and with any
# port: http://127.0.0.1/callback.
CLIENTS: dict[str, frozenset[str]] = {}
