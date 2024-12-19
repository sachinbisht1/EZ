"""All constants of AWS."""
import os
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.environ.get("ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("SECRET_ACCESS_KEY")
AWS_REGION_NAME = os.environ.get("DEFAULT_REGION")
DB_MASTER = os.environ.get("DB_MASTER")
BUCKET_NAME = "createabucket"
DP_BUCKET = "ez-databucket"
DP_S3_FOLDER = "dp"
DATA_FOLDER = "datafolder"
