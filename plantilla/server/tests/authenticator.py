"""An authenticator of software, to sign the ceremonies of the tests."""

import hashlib
import json
import secrets
import struct
from datetime import UTC, datetime, timedelta
from typing import Any

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID
from sqlalchemy.ext.asyncio import AsyncSession
from webauthn.helpers import bytes_to_base64url
from webauthn.helpers.encode_cbor import encode_cbor

from app.config import settings
from app.models.account.account import Account
from app.models.account.passkey import Passkey

ORIGIN = f"https://app.{settings.domain}"
UP, UV, BE, BS, AT, ED = 0x01, 0x04, 0x08, 0x10, 0x40, 0x80


def attestation_certificate(key: ec.EllipticCurvePrivateKey) -> bytes:
    """Make the certificate of a packed attestation, signed by itself.

    It has what WebAuthn asks of a packed certificate; the server
    refuses it anyway.
    """
    name = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, "CL"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Tests"),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Authenticator Attestation"),
            x509.NameAttribute(NameOID.COMMON_NAME, "Tests"),
        ]
    )
    now = datetime.now(UTC)
    certificate = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(days=1))
        .not_valid_after(now + timedelta(days=1))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .sign(key, hashes.SHA256())
    )
    return certificate.public_bytes(serialization.Encoding.DER)


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

    def attested(self, rp_id: str, extensions: dict[str, object] | None) -> bytes:
        """Write the authenticator data of a registration."""
        flags = self.flags | AT | (ED if extensions else 0)
        credential = len(self.credential_id).to_bytes(2, "big") + self.credential_id
        return (
            hashlib.sha256(rp_id.encode()).digest()
            + bytes([flags])
            + struct.pack(">I", self.sign_count)
            + bytes(16)
            + credential
            + self.cose_key()
            + (encode_cbor(extensions) if extensions else b"")
        )

    def create(
        self,
        challenge: str,
        *,
        fmt: str = "none",
        origin: str = ORIGIN,
        rp_id: str = settings.domain,
        extensions: dict[str, object] | None = None,
        client: dict[str, object] | None = None,
    ) -> dict[str, Any]:
        """Answer navigator.credentials.create() for challenge.

        packed signs as its own attestation; packed-x5c signs with the
        key of a certificate, which the library accepts without a root.
        """
        auth_data = self.attested(rp_id, extensions)
        client_data = {"type": "webauthn.create", "challenge": challenge, "origin": origin}
        client_data_json = json.dumps({**client_data, **(client or {})}).encode()
        statement: dict[str, object] = {}
        signed = auth_data + hashlib.sha256(client_data_json).digest()
        if fmt == "packed":
            statement = {"alg": -7, "sig": self.key.sign(signed, ec.ECDSA(hashes.SHA256()))}
        if fmt == "packed-x5c":
            key = ec.generate_private_key(ec.SECP256R1())
            statement = {
                "alg": -7,
                "sig": key.sign(signed, ec.ECDSA(hashes.SHA256())),
                "x5c": [attestation_certificate(key)],
            }
        attestation = {
            "fmt": fmt.removesuffix("-x5c"),
            "attStmt": statement,
            "authData": auth_data,
        }
        return {
            "id": bytes_to_base64url(self.credential_id),
            "rawId": bytes_to_base64url(self.credential_id),
            "type": "public-key",
            "response": {
                "clientDataJSON": bytes_to_base64url(client_data_json),
                "attestationObject": bytes_to_base64url(encode_cbor(attestation)),
                "transports": ["internal", "hybrid"],
                "authenticatorData": bytes_to_base64url(auth_data),
                "publicKeyAlgorithm": -7,
            },
            "clientExtensionResults": {},
            "authenticatorAttachment": "platform",
        }

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
