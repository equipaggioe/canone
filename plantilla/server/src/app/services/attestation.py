"""Register a passkey: the options of create() and their answer."""

import secrets
from dataclasses import dataclass
from datetime import UTC, datetime
from http import HTTPStatus
from uuid import UUID

import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from webauthn import verify_registration_response
from webauthn.helpers import (
    base64url_to_bytes,
    bytes_to_base64url,
    parse_attestation_object,
    parse_cbor,
)
from webauthn.helpers.cose import COSEAlgorithmIdentifier
from webauthn.helpers.exceptions import WebAuthnException
from webauthn.helpers.structs import AttestationObject

from app import store
from app.config import settings
from app.enums import EventLevel
from app.models.account.account import Account
from app.models.account.passkey import Passkey
from app.schemas.auth import (
    AuthenticatorSelection,
    CredentialParameters,
    PasskeyCreationOptions,
    PasskeyRegistration,
    RelyingParty,
    UserEntity,
)
from app.services import events, passkeys
from app.services.passkeys import CHALLENGE_LIFETIME, Refused
from app.services.sessions import Client

# EdDSA, ES256 and RS256, in this order.
ALGORITHMS = [
    COSEAlgorithmIdentifier.EDDSA,
    COSEAlgorithmIdentifier.ECDSA_SHA_256,
    COSEAlgorithmIdentifier.RSASSA_PKCS1_v1_5_SHA_256,
]
LONGEST_ID = 1023
# Chrome asks credProtect of a security key by itself when it creates a
# discoverable passkey, and the key answers it.
CRED_PROTECT = range(1, 4)


@dataclass(frozen=True)
class Created:
    """A verified passkey, not stored yet, and its user handle."""

    user_handle: bytes
    credential_id: bytes
    public_key: bytes
    sign_count: int
    user_verified: bool
    backup_eligible: bool
    backup_state: bool
    transports: list[str]


def creation_key(challenge: bytes) -> str:
    """Name the challenge of a registration in Valkey."""
    return f"passkey:creation:{bytes_to_base64url(challenge)}"


async def options(
    user_handle: bytes, name: str, existing: list[Passkey]
) -> PasskeyCreationOptions:
    """Make the options of create(); the challenge keeps the handle.

    The passkeys of the account are excluded: two do not share an
    authenticator.
    """
    challenge = secrets.token_bytes(16)
    await store.client.set(creation_key(challenge), user_handle, ex=CHALLENGE_LIFETIME)
    return PasskeyCreationOptions(
        challenge=bytes_to_base64url(challenge),
        rp=RelyingParty(id=settings.domain, name=settings.domain),
        user=UserEntity(id=bytes_to_base64url(user_handle), name=name, display_name=""),
        pub_key_cred_params=[
            CredentialParameters(type="public-key", alg=algorithm.value)
            for algorithm in ALGORITHMS
        ],
        authenticator_selection=AuthenticatorSelection(
            resident_key="required", require_resident_key=True, user_verification="preferred"
        ),
        attestation="none",
        exclude_credentials=[passkeys.descriptor(passkey) for passkey in existing],
    )


def check_attestation(found: AttestationObject) -> None:
    """Accept none, and packed without x5c: the self attestation."""
    # canone ADR-0226: without root certificates the library checks no
    # chain, and takes packed with any certificate that signs.
    if found.fmt == "none":
        return
    if found.fmt == "packed" and found.att_stmt is not None and found.att_stmt.x5c is None:
        return
    raise Refused("attestation", format=str(found.fmt))


def check_extensions(found: AttestationObject) -> None:
    """Accept in the authenticator data only credProtect, 1 to 3."""
    if found.auth_data.extensions is None:
        return
    try:
        extensions = parse_cbor(found.auth_data.extensions)
    except (ValueError, WebAuthnException) as error:
        raise Refused("authenticator_data") from error
    if not isinstance(extensions, dict):
        raise Refused("authenticator_data")
    if set(extensions) == {"credProtect"} and extensions["credProtect"] in CRED_PROTECT:
        return
    raise Refused("extensions", extensions=sorted(str(name) for name in extensions))


async def check_credential(session: AsyncSession, found: AttestationObject) -> bytes:
    """Refuse a credential ID that is too long or already registered."""
    data = found.auth_data.attested_credential_data
    if data is None:
        raise Refused("credential")
    if len(data.credential_id) > LONGEST_ID:
        raise Refused("credential_length")
    taken = sa.select(Passkey.id).where(Passkey.credential_id == data.credential_id)
    if await session.scalar(taken) is not None:
        raise Refused("credential_taken")
    return data.credential_id


async def take_challenge(data: dict[str, object]) -> tuple[bytes, bytes]:
    """Delete the challenge; return it and its user handle."""
    try:
        challenge = base64url_to_bytes(str(data.get("challenge", "")))
    except ValueError as error:
        raise Refused("challenge") from error
    handle = await store.client.getdel(creation_key(challenge))
    if handle is None:
        raise Refused("challenge")
    return challenge, handle


async def verify(session: AsyncSession, credential: PasskeyRegistration) -> Created:
    """Check the answer of create(): the library, then the server."""
    data = passkeys.client_data(credential)
    challenge, handle = await take_challenge(data)
    passkeys.check_client(credential.client_extension_results, data)
    try:
        found = parse_attestation_object(
            base64url_to_bytes(credential.response.attestation_object)
        )
    except (ValueError, WebAuthnException) as error:
        raise Refused("attestation_object") from error
    check_attestation(found)
    check_extensions(found)
    await check_credential(session, found)
    try:
        verified = verify_registration_response(
            credential=credential.model_dump(mode="json", by_alias=True),
            expected_challenge=challenge,
            expected_rp_id=settings.domain,
            expected_origin=passkeys.origins(),
            supported_pub_key_algs=ALGORITHMS,
        )
    except (ValueError, WebAuthnException) as error:
        raise Refused("attestation") from error
    return Created(
        user_handle=handle,
        credential_id=verified.credential_id,
        public_key=verified.credential_public_key,
        sign_count=verified.sign_count,
        user_verified=verified.user_verified,
        backup_eligible=found.auth_data.flags.be,
        backup_state=verified.credential_backed_up,
        transports=credential.response.transports,
    )


async def create(
    session: AsyncSession, credential: PasskeyRegistration, client: Client
) -> Created:
    """Verify a new passkey, or answer 400 and log why."""
    try:
        return await verify(session, credential)
    except Refused as refused:
        await events.record(
            events.event(
                "input_validation_fail",
                EventLevel.WARN,
                target_type="passkey",
                ip_address=client.ip_address,
                user_agent=client.user_agent,
                details=refused.details,
            )
        )
        raise HTTPException(HTTPStatus.BAD_REQUEST, "The passkey was not registered") from refused


def keep(
    session: AsyncSession,
    account: Account,
    created: Created,
    name: str,
    passkey_id: UUID,
    client: Client,
) -> Passkey:
    """Store a verified passkey in an account, with its name and ID.

    Its link goes to event_log with the IP and the user agent.
    """
    now = datetime.now(UTC)
    row = Passkey(
        id=passkey_id,
        account_id=account.id,
        credential_id=created.credential_id,
        public_key=created.public_key,
        sign_count=created.sign_count,
        uv_initialized=created.user_verified,
        transports=created.transports,
        backup_eligible=created.backup_eligible,
        backup_state=created.backup_state,
        name=name,
        created_at=now,
        changed_at=now,
    )
    session.add(row)
    session.add(
        events.event(
            "sensitive_create",
            EventLevel.INFO,
            actor_id=account.id,
            target_type="passkey",
            target_id=str(passkey_id),
            ip_address=client.ip_address,
            user_agent=client.user_agent,
        )
    )
    return row
