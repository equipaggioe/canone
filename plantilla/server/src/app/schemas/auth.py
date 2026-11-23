"""The bodies and responses of signing in."""

from typing import Annotated, Literal, Self

from pydantic import AfterValidator, Field, StringConstraints, model_validator

from app.enums import TokenErrorCode
from app.schemas.base import InputSchema, Schema

# autenticacion.md: the server lowers the email when it receives it.
Email = Annotated[str, AfterValidator(str.lower)]
# A +, the country code and digits only.
Phone = Annotated[str, StringConstraints(pattern=r"^\+[0-9]+$")]


class PasswordLogin(InputSchema):
    """A password, and either the email or the phone of the account."""

    email: Email | None = None
    phone: Phone | None = None
    password: str

    @model_validator(mode="after")
    def one_identifier(self) -> Self:
        """Take exactly one of the email and the phone."""
        if (self.email is None) == (self.phone is None):
            raise ValueError("send either email or phone")
        return self


class TokenResponse(Schema):
    """The tokens of an app, with the member names of RFC 6749."""

    access_token: str = Field(alias="access_token")
    token_type: Literal["Bearer"] = Field(alias="token_type")
    expires_in: int = Field(alias="expires_in")
    refresh_token: str = Field(alias="refresh_token")


class TokenError(Schema):
    """An error of the token endpoint, as RFC 6749 writes it."""

    error: TokenErrorCode
