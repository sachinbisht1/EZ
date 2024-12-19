from constants.api_endpoints import account as endpoints
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from initializers.http_handler import HANDLE_HTTP_EXCEPTION
from constants.http_status_code import COMMON_EXCEPTION_STATUS_CODE, STATUS_OK, BAD_REQUEST_ERROR_STATUS_CODE
from constants.http_status_code import STATUS_CREATED
from models import accounts as models
from controllers import user as controller
from database.columns import user as columns
from controllers import secrets_io
from constants.responses import user as response_key
from initializers.query import QUERIES
from constants.table_names import USER_TABLE_NAME
from constants.utilities_constants import ACCESS_TOKEN, REFRESH_TOKEN
from constants.utilities_constants import ACCESS_TOKEN_EXPIRE_MINUTES, SAME_SITE
from gateways.mail_sender import send_successfully_login_mail
from controllers.secrets_io import generate_verification_token, get_hashed_secret, parse_jwt_access_data
from controllers.utilities import add_path, current_time_in_time_format
from constants.frontend import FRONTEND_URL, FRONTEND_SIGNUP_VERIFICATION_ENDPOINT
from gateways.mail_sender import send_signup_mail, send_login_otp_mail
from constants import account


account_router = APIRouter()


@account_router.get(endpoints.ACCOUNT_ROOT)
def check_account_status():
    """Check server status of account router."""
    try:
        return JSONResponse(content={"server_status": STATUS_OK, "server_name": "Account"},
                            status_code=STATUS_OK)
    except HTTPException as http_error:
        return HANDLE_HTTP_EXCEPTION(status_code=http_error.status_code, error_message=http_error.detail)
    except Exception as error:
        HANDLE_HTTP_EXCEPTION(status_code=COMMON_EXCEPTION_STATUS_CODE, error_message=f"{error}")


@account_router.put(endpoints.ACCOUNT_LOGIN)
def account_login(data: models.Login, request: Request):
    """Authenticate account login using otp."""
    try:
        user_details = controller.validate_user(
            user_email=data.email,
            raise_for_non_existence=True,
            raise_for_verification=True,
            raise_for_active=True
        )
        print(f"{user_details=}")
        system_totp = user_details.get(columns.login_otp) or ''
        otp_generation_time = user_details.get(columns.otp_generation_time)
        if not secrets_io.verify_secret(data.otp.get_secret_value(), system_totp or ''):
            return HANDLE_HTTP_EXCEPTION(BAD_REQUEST_ERROR_STATUS_CODE,
                                         "Wrong otp")
        if not secrets_io.verify_otp_expire(otp_generation_time):
            return HANDLE_HTTP_EXCEPTION(BAD_REQUEST_ERROR_STATUS_CODE, "OTP expired")
        user_details = controller.remove_sensitive_data(user_details=user_details)
        access_token = secrets_io.create_access_token(user_data=user_details)
        refresh_token = secrets_io.create_refresh_token(user_email=data.email)
        response = JSONResponse(content={response_key.REFRESH_TOKEN: refresh_token},
                                status_code=STATUS_OK)
        QUERIES.update_item(
            table_name=USER_TABLE_NAME,
            key={columns.user_email: data.email},
            values_to_update={columns.login_otp: "",
                              columns.trashed_time: "",
                              columns.otp_generation_time: ""
                              }
        )
        response.set_cookie(key=ACCESS_TOKEN, value=access_token.get(ACCESS_TOKEN),
                            max_age=int(ACCESS_TOKEN_EXPIRE_MINUTES) * 60, secure=True, httponly=True,
                            samesite=SAME_SITE)
        send_successfully_login_mail(recipient=data.email)
        return response

    except HTTPException as http_error:
        return HANDLE_HTTP_EXCEPTION(status_code=http_error.status_code, error_message=http_error.detail)
    except Exception as error:
        HANDLE_HTTP_EXCEPTION(status_code=COMMON_EXCEPTION_STATUS_CODE, error_message=error.args)


@account_router.put(endpoints.ACCOUNT_LOGOUT)
def account_logout(request: Request):
    """Logout from your account."""
    response = JSONResponse(content=STATUS_OK, status_code=STATUS_OK)

    response.delete_cookie(key=ACCESS_TOKEN)
    response.delete_cookie(key=REFRESH_TOKEN)

    return response


@account_router.post(endpoints.RESEND_VERIFICATION_URL)
def send_verfication_mail(email: str, request: Request, verification_token="", no_response=False):
    """Resend signup verification mail to user."""
    try:
        print("sending verification mail")
        raise_error = False
        if not verification_token:
            user_details = QUERIES.get_item_by_partition_key(
                table_name=USER_TABLE_NAME,
                partiotion_key=columns.user_email,
                value=email
            )
            raise_error = True
            if not user_details:
                return JSONResponse(content={response_key.USER_ALREADY_EXIST: False}, status_code=STATUS_CREATED)
            verification_token = user_details.get(columns.verification_token) or ''
        if not verification_token:
            return JSONResponse(content={response_key.USER_EMAIL_VERIFIED: True}, status_code=STATUS_CREATED)

        verification_url = add_path(str(FRONTEND_URL),
                                    endpoint=FRONTEND_SIGNUP_VERIFICATION_ENDPOINT.format(verification_token,
                                                                                          ))
        send_signup_mail(verification_url=verification_url, recepient_name=email, recipient=email)
        if no_response:
            return
        response = {
            "message": "Verify signup using recieved email",
            "token": verification_token
        }
        if raise_error:
            return JSONResponse(content=response, status_code=BAD_REQUEST_ERROR_STATUS_CODE)
        return JSONResponse(content=response, status_code=STATUS_CREATED)

    except HTTPException as http_error:
        return HANDLE_HTTP_EXCEPTION(status_code=http_error.status_code, error_message=http_error.detail)
    except Exception as error:
        HANDLE_HTTP_EXCEPTION(status_code=COMMON_EXCEPTION_STATUS_CODE, error_message=error.args)


@account_router.post(endpoints.ACCOUNT_SIGNUP)
async def account_signup(data: models.Signup, request: Request,):
    """Create new account and verify using email."""
    try:
        user_data = controller.validate_user(
            user_email=data.email,
            raise_for_existence=False,
            raise_for_verification=False,
            raise_for_active=False
        )
        if user_data.get(columns.verification_token) == "verified":
            return JSONResponse(content={"message": "User already exist"},
                                status_code=STATUS_CREATED)
        if user_data and user_data.get(columns.verification_token, False):
            send_verfication_mail(email=data.email, request=request,
                                  verification_token=user_data.get(columns.verification_token, ''), no_response=True,
                                  )
            return JSONResponse(content={"message": "User already exist, Verify signup using recieved email."},
                                status_code=STATUS_CREATED)
        secret = data.password.get_secret_value()
        hashed_secret = get_hashed_secret(secret=secret)
        verification_token = generate_verification_token(user_email=data.email)
        QUERIES.update_item(
            table_name=USER_TABLE_NAME,
            key={columns.user_email: data.email},
            values_to_update={
                columns.name: data.name,
                columns.about: data.about,
                columns.secret_key: hashed_secret,
                columns.verification_token: verification_token,
                columns.role: data.role
            }
        )
        response = send_verfication_mail(email=data.email, request=request,
                                         verification_token=verification_token)
        return response

    except HTTPException as http_error:
        return HANDLE_HTTP_EXCEPTION(status_code=http_error.status_code, error_message=http_error.detail)
    except Exception as error:
        HANDLE_HTTP_EXCEPTION(status_code=COMMON_EXCEPTION_STATUS_CODE, error_message=error.args)


@account_router.get(endpoints.SIGNUP_VERIFICATION, include_in_schema=True)
def signup_verification(verification_token: str, request: Request):
    """Singup verification receiver."""
    try:
        user_data = parse_jwt_access_data(token=verification_token)
        print(f"{user_data=}")
        user_db_data = controller.validate_user(
            user_email=user_data.get(columns.user_email),
            raise_for_non_existence=True,
            raise_for_verification=False
        )
        if not user_db_data.get(columns.verification_token):
            return JSONResponse(content={account.STATUS: account.ALREADY_VERIFIED}, status_code=STATUS_OK)
        QUERIES.update_item(
            table_name=USER_TABLE_NAME,
            key={columns.user_email: user_data.get(columns.user_email)},
            values_to_update={columns.verification_token: "verified"}
        )
        return JSONResponse(content={account.STATUS: account.VERIFIED}, status_code=STATUS_CREATED)
    except HTTPException as http_error:
        return HANDLE_HTTP_EXCEPTION(status_code=http_error.status_code, error_message=http_error.detail)
    except Exception as error:
        HANDLE_HTTP_EXCEPTION(status_code=COMMON_EXCEPTION_STATUS_CODE, error_message=error.args)


@account_router.put(endpoints.VERIFY_OTP)
def verify_password_otp(data: models.VerifyPasswordOtp):
    """Get otp to verify resetting password."""
    try:
        user_details = controller.validate_user(
            user_email=data.email,
            raise_for_non_existence=True,
            raise_for_verification=True,
            raise_for_active=True
        )
        system_totp = (user_details.get(columns.password_otp))
        # totp_key = controller.get_totp_key(user_details)
        otp_generation_time = user_details.get(columns.otp_generation_time)
        if not secrets_io.verify_secret(data.otp.get_secret_value(), system_totp or ''):
            return HANDLE_HTTP_EXCEPTION(BAD_REQUEST_ERROR_STATUS_CODE,
                                         "Wrong otp")
        if not secrets_io.verify_otp_expire(otp_generation_time):
            return HANDLE_HTTP_EXCEPTION(BAD_REQUEST_ERROR_STATUS_CODE, "OTP expired")
        return JSONResponse(content={"message": "OTP Verified successfully"}, status_code=STATUS_CREATED)

    except HTTPException as http_error:
        return HANDLE_HTTP_EXCEPTION(status_code=http_error.status_code, error_message=http_error.detail)
    except Exception as error:
        HANDLE_HTTP_EXCEPTION(status_code=COMMON_EXCEPTION_STATUS_CODE, error_message=error.args)


@account_router.put(endpoints.ACCOUNT_LOGIN_OTP)
def generate_login_otp(data: models.LoginOtp, request: Request):
    """Generate otp to login."""
    try:
        try:
            user_data = controller.validate_user(
                user_email=data.email,
                raise_for_non_existence=True,
                raise_for_verification=True,
                raise_for_active=False
            )
        except HTTPException as http_error:
            return HANDLE_HTTP_EXCEPTION(status_code=http_error.status_code, error_message=http_error.detail)

        except Exception as err:
            if "user not yet verified" in err.args:
                return send_verfication_mail(data.email, request)

        if not secrets_io.verify_secret(data.password.get_secret_value(), user_data.get(columns.secret_key) or ''):
            return HANDLE_HTTP_EXCEPTION(status_code=BAD_REQUEST_ERROR_STATUS_CODE,
                                         error_message="Invalid password")
        totp_key = controller.get_totp_key(user_data=user_data)
        decoded_otp = secrets_io.generate_otp(totp_key)
        otp = get_hashed_secret(secret=decoded_otp)
        otp_generation_time = current_time_in_time_format()
        QUERIES.update_item(
            table_name=USER_TABLE_NAME,
            key={columns.user_email: data.email},
            values_to_update={
                columns.login_otp: otp,
                columns.otp_generation_time: otp_generation_time
            }
        )
        send_login_otp_mail(otp=decoded_otp, recipient=data.email)
        return JSONResponse(content={"message": response_key.LOGIN_OTP_SEND_ON_MAIL, "otp":decoded_otp}, status_code=STATUS_CREATED)
    except HTTPException as http_error:
        return HANDLE_HTTP_EXCEPTION(status_code=http_error.status_code, error_message=http_error.detail)
    except Exception as error:
        HANDLE_HTTP_EXCEPTION(status_code=COMMON_EXCEPTION_STATUS_CODE, error_message=error.args)
