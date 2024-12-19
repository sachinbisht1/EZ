"""All constants from frontend."""
from dotenv import load_dotenv
import os
load_dotenv()
FRONTEND_URL = os.environ.get("FRONTEND_URL")
FRONTEND_SIGNUP_VERIFICATION_ENDPOINT = "/account/verification/{}"
