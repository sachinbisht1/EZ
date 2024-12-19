"""All constants of utilities."""
from dotenv import load_dotenv
import os
load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = 30    # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
DEACTIVATED_ACCOUNT_DELTION_TIME = 90  # DAYS
PROJECT_COOKIES_EXP = 1800   # 30 minutes
ALGORITHM = "HS256"
JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']   # should be kept secret
JWT_REFRESH_SECRET_KEY = os.environ['JWT_REFRESH_SECRET_KEY']
PEPPER_TEXT = os.environ['PEPPER_TEXT']
TOKEN_TYPE = "Bearer"
DATE_TIME_FORMAT = "%Y%m%dT%H%M%S"
CLOUDWATCH_LOG = os.environ['CLOUDWATCH_LOG']   # Log group name
INTERLEAVED = bool(os.environ['INTERLEAVED'])   # True
SECRET_KEY = "secret_key"
EXPIRE_TIME = 'exp'
ACCESS_TOKEN = "access_token"
REFRESH_TOKEN = "refresh_token"
SAME_SITE = "none"
FERNET_KEY = os.environ['FERNET_KEY']
DATA = "data"
OTP_LENGTH = 6
OTP_VALID_FOR_TIME = 300  # in-seconds
DATABASE_DIR = "database"
HASHED_ENCODING = "utf-8"
DEFAULT_PAGE_SIZE = 20
CLOUDFLARE_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
