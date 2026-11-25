"""The services this product sends a push through.

fastapi.md, «Push»: each repository chooses them, any of them or none.
"""

from app.enums import Push

PUSH: frozenset[Push] = frozenset({Push.FCM, Push.WEB})
