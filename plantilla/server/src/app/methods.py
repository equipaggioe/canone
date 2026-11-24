"""The ways to sign in that this product offers.

autenticacion.md: each repository chooses them, any of them.
"""

from app.enums import Method

METHODS: frozenset[Method] = frozenset({Method.PASSKEY, Method.PASSWORD, Method.SMS})
