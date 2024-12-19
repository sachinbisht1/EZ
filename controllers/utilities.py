import os
import time
from uuid import uuid4
from typing import Optional
from fastapi import Cookie
from datetime import datetime
from controllers.secrets_io import parse_jwt_access_data, decrypt_data
from controllers.api_request_error import BadRequestException


def add_path(base_path, endpoint):
    """Add endpoint to an url."""
    if endpoint[0] == "/":
        endpoint = endpoint[1:]
    return os.path.join(base_path, endpoint)


def current_time_in_time_format():
    return time.time()


def generate_uuid():
    """Generate unique string."""
    uuid_str = str(uuid4())
    return uuid_str.replace('-', '')


def get_access_token(access_token: Optional[str] = Cookie(None)) -> dict:
    """Get access_token."""
    print(f"{access_token=}")
    if access_token is None:
        return BadRequestException(detail=404)
    access_token_data = decrypt_data(parse_jwt_access_data(token=access_token))

    return access_token_data


def upload_file_name():
    today_date = datetime.today()

    # Format the date as "day_month_year"
    formatted_date = today_date.strftime("%d_%B_%Y").lower()

    return formatted_date
