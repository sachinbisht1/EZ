"""Controller to manage secretes."""
from typing import Union
from datetime import datetime, timedelta, timezone
import bcrypt
import pyotp
from jose import jwt, JWTError, ExpiredSignatureError
from http.cookies import SimpleCookie
import json
from pydantic import EmailStr
import time
from constants import utilities_constants
from database.columns.user import user_email as user_db_email_column
from constants.error_messages.accounts import PLEASE_LOGIN_AGAIN, INVALID_CREDENTIALS, SECRET_NOT_FOUND
from constants.error_messages.accounts import LOGIN_FAILED, PASSWORD_IS_NOT_CREATED_BY_USER
from constants.http_status_code import PERMISSION_DENIED_ERROR_STATUS_CODE, BAD_REQUEST_ERROR_STATUS_CODE
from constants.http_status_code import COMMON_EXCEPTION_STATUS_CODE

from initializers.http_handler import HANDLE_HTTP_EXCEPTION

from cryptography.fernet import Fernet


def get_hashed_secret(secret: Union[str, bool]) -> str:
    """Generate hash secret."""
    if not secret:
        raise HANDLE_HTTP_EXCEPTION(status_code=BAD_REQUEST_ERROR_STATUS_CODE,
                                    error_message=SECRET_NOT_FOUND)

    return bcrypt.hashpw(f"{secret}_-_{utilities_constants.PEPPER_TEXT}".encode(utilities_constants.HASHED_ENCODING),
                         bcrypt.gensalt()).decode()


def verify_secret(secret: str, hashed_pass: Union[str, bool]) -> bool:
    """Verify hash secret."""
    if not hashed_pass:
        raise Exception(PASSWORD_IS_NOT_CREATED_BY_USER)

    secret_password = f"{secret}_-_{utilities_constants.PEPPER_TEXT}".encode(utilities_constants.HASHED_ENCODING)

    if bcrypt.checkpw(secret_password, hashed_pass.encode(utilities_constants.HASHED_ENCODING)):
        return True

    raise HANDLE_HTTP_EXCEPTION(PERMISSION_DENIED_ERROR_STATUS_CODE, INVALID_CREDENTIALS)


def encrypt_data(data: dict):
    """Encrypt data sspeciall user data."""
    data = json.dumps(data).encode()
    return Fernet(key=utilities_constants.FERNET_KEY.encode()).encrypt(data=data).decode()


def encrypt_email(data: EmailStr):
    """Encrypt email id."""
    return Fernet(key=utilities_constants.FERNET_KEY.encode()).encrypt(data=data.encode()).decode()


def decrypt_email(data) -> EmailStr:
    """Decrypt email id."""
    return Fernet(key=utilities_constants.FERNET_KEY.encode()).decrypt(token=data).decode()


def decrypt_data(data) -> dict:
    """Decrypt data specially user data."""
    data = Fernet(key=utilities_constants.FERNET_KEY.encode()).decrypt(token=data.get('data'))
    return json.loads(data.decode())


def create_access_token(user_data):
    """Create a cookies access token."""
    jwt_token = jwt.encode(
        {
            utilities_constants.DATA: encrypt_data(data=user_data),
            utilities_constants.EXPIRE_TIME:
            datetime.now(timezone.utc) + timedelta(minutes=utilities_constants.ACCESS_TOKEN_EXPIRE_MINUTES)
        },
        algorithm=utilities_constants.ALGORITHM,
        key=utilities_constants.JWT_SECRET_KEY)
    return {utilities_constants.ACCESS_TOKEN: jwt_token}


def create_refresh_token(user_email):
    """Create a cookies refresh token."""
    jwt_token = jwt.encode(
        {
            user_db_email_column: encrypt_email(user_email),
            utilities_constants.EXPIRE_TIME:
            datetime.now(timezone.utc) + timedelta(minutes=utilities_constants.REFRESH_TOKEN_EXPIRE_MINUTES)
        },
        algorithm=utilities_constants.ALGORITHM,
        key=utilities_constants.JWT_REFRESH_SECRET_KEY)
    return {utilities_constants.REFRESH_TOKEN: jwt_token}


def cookies_parser(cookie_raw_data: Union[SimpleCookie, dict]):
    """Parse cookies into dict."""
    cookie = SimpleCookie()
    cookie.load(cookie_raw_data)
    cookies = {keys: values.value for keys, values in cookie.items()}
    return cookies


def parse_jwt_access_data(token: str):
    """Parse jwt access data."""
    if not token:
        raise JWTError("Access token is missing.")
    print(f"{token=}")
    jwt_data = jwt.decode(token=token, key=utilities_constants.JWT_SECRET_KEY,
                          algorithms=utilities_constants.ALGORITHM)
    print(f"{jwt_data=}")
    return jwt_data


def parse_jwt_refresh_data(token: str):
    """Parse jwt refresh data."""
    if not token:
        raise HANDLE_HTTP_EXCEPTION(PERMISSION_DENIED_ERROR_STATUS_CODE, PLEASE_LOGIN_AGAIN)
    try:
        jwt_data = jwt.decode(token=token, key=utilities_constants.JWT_REFRESH_SECRET_KEY,
                              algorithms=utilities_constants.ALGORITHM)
        return jwt_data
    except ExpiredSignatureError as err:
        return False, err.args
    except Exception as error:
        return HANDLE_HTTP_EXCEPTION(COMMON_EXCEPTION_STATUS_CODE, LOGIN_FAILED.format(error.args))


def parse_email_from_jwt(jwt_data):
    """Parse email from JWT."""
    access_data = parse_jwt_access_data(token=jwt_data)
    return access_data.get(user_db_email_column)


def generate_otp(totp_key):
    """Generate otp."""
    return pyotp.TOTP(totp_key, interval=utilities_constants.OTP_VALID_FOR_TIME,
                      digits=utilities_constants.OTP_LENGTH).now()


def verify_otp_expire(otp_generation_time):
    """Verify OTP to be valid only within 5 minutes from generation time."""
    try:
        current_time = time.time()
        otp_expiry_time = float(otp_generation_time) + float(utilities_constants.OTP_VALID_FOR_TIME)
        if current_time <= otp_expiry_time:
            return True

        return False
    except Exception as ex:
        print(f"Exception occurred: {ex}")
        return False


def generate_verification_token(user_email, project_id=""):
    """Generate verification token."""
    token = jwt.encode(
        {
            user_db_email_column: user_email
        },
        algorithm=utilities_constants.ALGORITHM, key=utilities_constants.JWT_SECRET_KEY
    )
    return token
