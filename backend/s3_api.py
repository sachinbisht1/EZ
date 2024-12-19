"""Api router for all S3 apis."""
# fastapi imports
from constants import aws as dp_aws
from initializers import aws
from fastapi import UploadFile
from constants import utilities_constants
from constants.aws import AWS_REGION_NAME
from initializers.http_handler import HANDLE_HTTP_EXCEPTION
from constants.http_status_code import COMMON_EXCEPTION_STATUS_CODE


def upload_images_data_to_s3(file: UploadFile, name: str):
    s3_client = aws.S3_CLIENT
    try:
        s3_client.upload_fileobj(file.file, dp_aws.DP_BUCKET, name)
        return f"https://{dp_aws.DP_BUCKET}.s3.{AWS_REGION_NAME}.amazonaws.com/{name}"
    except Exception as error:
        print(f"{error=}")
        return "failed"


def get_images_data_from_s3(name: str):
    try:
        key = name
        s3_client = aws.S3_CLIENT
        presigned_url = s3_client.generate_presigned_url("get_object", Params={'Bucket': dp_aws.DP_BUCKET, 'Key': key},
                                                         ExpiresIn=utilities_constants.REFRESH_TOKEN_EXPIRE_MINUTES)
        return presigned_url
    except Exception as error:
        return None


def get_images_list_data_from_s3(folder: str):
    try:
        s3_client = aws.S3_CLIENT
        response = s3_client.list_objects_v2(Bucket=dp_aws.DP_BUCKET, Prefix=folder)
        if 'Contents' in response:
            files = [obj['Key'] for obj in response['Contents']]
        else:
            files = []
        return files
    except Exception as error:
        return None