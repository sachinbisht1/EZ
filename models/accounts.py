"""All account request models."""
from pydantic import BaseModel, EmailStr, SecretStr, Field
from typing import Optional


class TokenRequest(BaseModel):
    token: str


class Signup(BaseModel):
    """Account signup Api request model."""

    name: Optional[str] = ""
    about: Optional[str] = ""
    email: EmailStr
    password: SecretStr
    role: str = Field(None, description="Role of the user, e.g., 'Ops' or 'Not Ops'")


class ResetPasword(BaseModel):
    """Account reset passsword Api request model."""

    email: EmailStr
    new_password: SecretStr
    otp: SecretStr


class VerifyPasswordOtp(BaseModel):
    """Verify reset password otp."""

    otp: SecretStr
    email: EmailStr


class Login(BaseModel):
    """Login required data."""

    email: EmailStr
    otp: SecretStr = Field(description="6 digit otp")


class LoginOtp(BaseModel):
    """Login required data."""

    email: EmailStr
    password: SecretStr = Field(description='Password')


class RegenerateAccessToken(BaseModel):
    """Regenerate access token using refresh token."""

    token: SecretStr
