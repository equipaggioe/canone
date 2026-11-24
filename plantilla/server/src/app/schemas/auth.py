"""The bodies and responses of signing in."""

import unicodedata
from typing import Annotated, Any, Literal, Self

import phonenumbers
from pydantic import AfterValidator, BeforeValidator, Field, StringConstraints, model_validator

from app.enums import TokenErrorCode
from app.schemas.base import InputSchema, Schema

# autenticacion.md: the server lowers the email when it receives it.
Email = Annotated[str, AfterValidator(str.lower)]


def valid_number(phone: str) -> str:
    """Let through a number that phonenumbers takes as valid."""
    try:
        valid = phonenumbers.is_valid_number(phonenumbers.parse(phone))
    except phonenumbers.NumberParseException as error:
        raise ValueError("not a phone number") from error
    if not valid:
        raise ValueError("not a valid phone number")
    return phone


# A +, the country code and digits only, of a valid number.
Phone = Annotated[str, StringConstraints(pattern=r"^\+[0-9]+$"), AfterValidator(valid_number)]
# The 6 digits of a code that verifies an email or a phone.
Code = Annotated[str, StringConstraints(pattern=r"^[0-9]{6}$")]


def fit_length(password: str) -> str:
    """Let through 8 to 128 code points, counted in NFC."""
    if not 8 <= len(unicodedata.normalize("NFC", password)) <= 128:
        raise ValueError("a password has 8 to 128 characters")
    return password


# autenticacion.md: a new password, counted as it is stored.
NewPassword = Annotated[str, AfterValidator(fit_length)]
# What the holder calls a passkey.
PasskeyName = Annotated[str, StringConstraints(min_length=1, max_length=64)]


def plain(code: object) -> object:
    """Read a saved code in any case, with spaces or dashes."""
    if not isinstance(code, str):
        return code
    return code.replace(" ", "").replace("-", "").upper()


# The saved recovery code: 80 bits in 16 characters of base32.
SavedCode = Annotated[str, BeforeValidator(plain), StringConstraints(pattern=r"^[A-Z2-7]{16}$")]


class Identifier(InputSchema):
    """Either the email or the phone of an account."""

    email: Email | None = None
    phone: Phone | None = None

    @model_validator(mode="after")
    def one_identifier(self) -> Self:
        """Take exactly one of the email and the phone."""
        if (self.email is None) == (self.phone is None):
            raise ValueError("send either email or phone")
        return self

    @property
    def address(self) -> str:
        """Return the email or the phone that came."""
        address = self.email or self.phone
        assert address is not None
        return address


class PasswordLogin(Identifier):
    """A password, and either the email or the phone of the account."""

    password: str


class PasswordReauth(InputSchema):
    """The password of the account of the session."""

    password: str


class SmsCode(InputSchema):
    """The phone of an account, which receives the code to sign in."""

    phone: Phone


class SmsLogin(SmsCode):
    """The phone of an account, and the code its SMS brought."""

    code: Code


class SmsReauth(InputSchema):
    """The code that the SMS brought to the phone of the account."""

    code: Code


class TokenResponse(Schema):
    """The tokens of an app, with the member names of RFC 6749."""

    access_token: str = Field(alias="access_token")
    token_type: Literal["Bearer"] = Field(alias="token_type")
    expires_in: int = Field(alias="expires_in")
    refresh_token: str = Field(alias="refresh_token")


class TokenError(Schema):
    """An error of the token endpoint, as RFC 6749 writes it."""

    error: TokenErrorCode


class CredentialDescriptor(Schema):
    """A passkey the ceremony may use, by its ID in base64url."""

    type: Literal["public-key"]
    id: str
    transports: list[str]


class PasskeyOptions(Schema):
    """The options of navigator.credentials.get(), in base64url."""

    challenge: str
    rp_id: str
    allow_credentials: list[CredentialDescriptor]
    user_verification: Literal["preferred"]


class AssertionResponse(InputSchema):
    """What the authenticator signed, in base64url."""

    client_data_json: str = Field(alias="clientDataJSON")
    authenticator_data: str
    signature: str
    user_handle: str | None = None


class PasskeyCredential(InputSchema):
    """The whole response of navigator.credentials.get()."""

    id: str
    raw_id: str
    type: Literal["public-key"]
    response: AssertionResponse
    client_extension_results: dict[str, Any]
    authenticator_attachment: str | None = None


class RelyingParty(Schema):
    """The RP of a registration: the domain is its ID and its name."""

    id: str
    name: str


class UserEntity(Schema):
    """The account of a registration: its handle, no display name."""

    id: str
    name: str
    display_name: Literal[""]


class CredentialParameters(Schema):
    """An algorithm that the server accepts, by its COSE number."""

    type: Literal["public-key"]
    alg: int


class AuthenticatorSelection(Schema):
    """A discoverable passkey, and UV preferred."""

    resident_key: Literal["required"]
    require_resident_key: Literal[True]
    user_verification: Literal["preferred"]


class PasskeyCreationOptions(Schema):
    """The options of navigator.credentials.create(), in base64url."""

    challenge: str
    rp: RelyingParty
    user: UserEntity
    pub_key_cred_params: list[CredentialParameters]
    authenticator_selection: AuthenticatorSelection
    attestation: Literal["none"]
    exclude_credentials: list[CredentialDescriptor]


class AttestationResponse(InputSchema):
    """What the authenticator created, in base64url, and transports."""

    client_data_json: str = Field(alias="clientDataJSON")
    attestation_object: str
    transports: list[str]
    authenticator_data: str | None = None
    public_key: str | None = None
    public_key_algorithm: int | None = None


class PasskeyRegistration(InputSchema):
    """The whole response of navigator.credentials.create()."""

    id: str
    raw_id: str
    type: Literal["public-key"]
    response: AttestationResponse
    client_extension_results: dict[str, Any]
    authenticator_attachment: str | None = None


class Registration(Identifier):
    """A new account: its verified address and its first authenticator.

    The authenticator is a named passkey or a password; a phone may come
    without one, where the product offers the SMS code. The setup code
    registers the first admin.
    """

    code: Code
    passkey_name: PasskeyName | None = None
    credential: PasskeyRegistration | None = None
    password: NewPassword | None = None
    setup_code: str | None = None

    @model_validator(mode="after")
    def one_authenticator(self) -> Self:
        """Take a named passkey or a password, not both."""
        if (self.credential is None) != (self.passkey_name is None):
            raise ValueError("send the credential with its name")
        if self.credential is not None and self.password is not None:
            raise ValueError("send either a passkey or a password")
        return self


class RecoveryProof(Identifier):
    """An email or a phone of an account, and the code it received."""

    code: Code


class PasswordRecovery(RecoveryProof):
    """The code, the saved code if any, and the new password."""

    recovery_code: SavedCode | None = None
    password: NewPassword


class PasskeyRecovery(RecoveryProof):
    """The code, the saved code if any, and the new passkey."""

    recovery_code: SavedCode | None = None
    passkey_name: PasskeyName
    credential: PasskeyRegistration


class RecoveryCodeView(Schema):
    """A saved recovery code, shown once."""

    recovery_code: str


class PasswordChange(InputSchema):
    """The new password of the account."""

    password: NewPassword
