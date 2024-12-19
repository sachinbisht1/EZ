"""All constants of AWS."""
import os
from dotenv import load_dotenv

load_dotenv()

CLOUDFLARE_SECRET_KEY = os.environ.get("CLOUDFLARE_SECRET_KEY")
STATUS = "status"
VERIFIED = "verified"
ALREADY_VERIFIED = "already_verified"
