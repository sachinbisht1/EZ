"""Helper for user db Api's."""
from initializers.query import QUERIES
from constants.table_names import USER_TABLE_NAME
from database.columns import user as columns
from initializers.http_handler import HANDLE_HTTP_EXCEPTION
from constants.http_status_code import BAD_REQUEST_ERROR_STATUS_CODE
import json
from base64 import b32encode


def remove_sensitive_data(user_details: dict):
    """Remove senstive data."""
    user_details[columns.secret_key] = "************"

    return user_details


def validate_user(user_email, raise_for_existence: bool = False, raise_for_non_existence: bool = False,
                  raise_for_verification: bool = True, raise_for_active: bool = True):
    """Validate user or raise error according to parameters."""
    user_data = QUERIES.get_item_by_partition_key(
        table_name=USER_TABLE_NAME,
        partiotion_key=columns.user_email,
        value=user_email
    )
    if raise_for_non_existence and not user_data:
        raise HANDLE_HTTP_EXCEPTION(BAD_REQUEST_ERROR_STATUS_CODE, error_message="user does not exist")

    if raise_for_existence and user_data:
        raise HANDLE_HTTP_EXCEPTION(BAD_REQUEST_ERROR_STATUS_CODE, error_message="user already exist")
    if not user_data.get(columns.verification_token) == "verified":
        if raise_for_verification and user_data.get(columns.verification_token):
            raise HANDLE_HTTP_EXCEPTION(BAD_REQUEST_ERROR_STATUS_CODE, error_message="user not yet verified")

    if raise_for_active and user_data.get(columns.trashed_time):
        raise HANDLE_HTTP_EXCEPTION(BAD_REQUEST_ERROR_STATUS_CODE, error_message="user is deactivated")

    return user_data


def get_totp_key(user_data: dict) -> dict:
    """Get user specific totp key."""
    user_data.pop(columns.secret_key, '')
    user_data.pop(columns.login_otp, '')
    user_data.pop(columns.password_otp, '')
    user_data.pop(columns.verification_token, '')
    user_data = str(hash(json.dumps(user_data)))
    return b32encode(user_data.encode())
