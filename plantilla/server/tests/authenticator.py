"""An authenticator of software, to sign the ceremonies of the tests."""

import hashlib
import json
import secrets
import struct
from typing import Any

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from sqlalchemy.ext.asyncio import AsyncSession
from webauthn.helpers import bytes_to_base64url

from app.config import settings
from app.models.account.account import Account
from app.models.account.passkey import Passkey

ORIGIN = f"https://app.{settings.domain}"
UP, UV, BE, BS, ED = 0x01, 0x04, 0x08, 0x10, 0x80


def cbor_bytes(value: bytes) -> bytes:
    """Encode a byte string of up to 255 bytes in CBOR."""
    return bytes([0x58, len(value)]) + value


class Authenticator:
    """A passkey of software: an ES256 key and its sign count."""

    def __init__(self, *, flags: int = UP | UV, counts: bool = True) -> None:
        """Make the key and the credential ID.

        An authenticator that does not count signs with 0.
        """
        self.key = ec.generate_private_key(ec.SECP256R1())
        self.credential_id = secrets.token_bytes(32)
        self.flags = flags
        self.counts = counts
        self.sign_count = 0

    def cose_key(self) -> bytes:
        """Return the public key as a COSE EC2 key with ES256."""
        numbers = self.key.public_key().public_numbers()
        x, y = numbers.x.to_bytes(32, "big"), numbers.y.to_bytes(32, "big")
        # {1: 2, 3: -7, -1: 1, -2: x, -3: y}
        return b"\xa5\x01\x02\x03\x26\x20\x01\x21" + cbor_bytes(x) + b"\x22" + cbor_bytes(y)

    def sign(
        self,
        challenge: str,
        user_handle: bytes | None,
        *,
        origin: str = ORIGIN,
        rp_id: str = settings.domain,
        extensions: bytes = b"",
        client: dict[str, object] | None = None,
    ) -> dict[str, Any]:
        """Answer navigator.credentials.get() for challenge."""
        self.sign_count += self.counts
        flags = self.flags | (ED if extensions else 0)
        auth_data = (
            hashlib.sha256(rp_id.encode()).digest()
            + bytes([flags])
            + struct.pack(">I", self.sign_count)
            + extensions
        )
        client_data = {"type": "webauthn.get", "challenge": challenge, "origin": origin}
        client_data_json = json.dumps({**client_data, **(client or {})}).encode()
        signature = self.key.sign(
            auth_data + hashlib.sha256(client_data_json).digest(), ec.ECDSA(hashes.SHA256())
        )
        return {
            "id": bytes_to_base64url(self.credential_id),
            "rawId": bytes_to_base64url(self.credential_id),
            "type": "public-key",
            "response": {
                "clientDataJSON": bytes_to_base64url(client_data_json),
                "authenticatorData": bytes_to_base64url(auth_data),
                "signature": bytes_to_base64url(signature),
                "userHandle": bytes_to_base64url(user_handle) if user_handle else None,
            },
            "clientExtensionResults": {},
            "authenticatorAttachment": "platform",
        }


async def register(
    session: AsyncSession, account: Account, authenticator: Authenticator
) -> Passkey:
    """Store the passkey, as its registration would."""
    row = Passkey(
        account_id=account.id,
        credential_id=authenticator.credential_id,
        public_key=authenticator.cose_key(),
        sign_count=authenticator.sign_count,
        uv_initialized=bool(authenticator.flags & UV),
        transports=["internal"],
        backup_eligible=bool(authenticator.flags & BE),
        backup_state=bool(authenticator.flags & BS),
        name="Phone",
    )
    session.add(row)
    await session.flush()
    return row
