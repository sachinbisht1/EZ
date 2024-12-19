from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from fastapi.responses import JSONResponse
import os
from initializers.http_handler import HANDLE_HTTP_EXCEPTION
from constants.api_endpoints import data as endpoints
from backend import s3_api
from models import upload as models
from constants.utilities_constants import ACCESS_TOKEN
from controllers.utilities import get_access_token
from controllers.utilities import upload_file_name

# Define allowed file types
VALID_ARCHIVE_EXTENSIONS = ['.ppt', '.pptx', '.xls', '.xlsx', '.txt', '.doc', '.docx']

# Initialize router
data = APIRouter()


# Upload File API
@data.post(endpoints.UPLOAD_DATA)
async def upload_file(request: Request, file: UploadFile = File(...)):
    """Upload PPT, Excel, TXT, or Word files to the S3 bucket."""
    try:
        user_data = get_access_token(request.cookies.get(ACCESS_TOKEN, ''))
        if user_data.get("role") == "Ops":
            # Validate file extension
            original_extension = os.path.splitext(file.filename)[-1].lower()
            if original_extension not in VALID_ARCHIVE_EXTENSIONS:
                return HANDLE_HTTP_EXCEPTION(
                    status_code=400,
                    error_message="Invalid file type. Only PPT, Excel, TXT, and Word files are allowed."
                )
            # Generate file name and path
            original_file_name = os.path.splitext(file.filename)[0]
            folder_name = upload_file_name()
            file_path = f"{folder_name}/{original_file_name}{original_extension}"

            # Upload file to S3
            k = s3_api.upload_images_data_to_s3(file, file_path)
            if k == "failed":
                return JSONResponse(content={"message": "File failed"})
            return JSONResponse(content={"message": "File uploaded successfully", "file_path": file_path})
        else:
            return JSONResponse(content={"message": "only ops user is allowed"})
    except HTTPException as http_error:
        return HANDLE_HTTP_EXCEPTION(status_code=http_error.status_code, error_message=http_error.detail)
    except Exception as error:
        return HANDLE_HTTP_EXCEPTION(status_code=500, error_message=str(error))


# List Files API
@data.get(endpoints.GET_DATA_LIST)
def get_files_list(request: Request):
    """List all files for a given project in the S3 bucket."""
    try:
        user_data = get_access_token(request.cookies.get(ACCESS_TOKEN, ''))
        if user_data.get("role") == "Ops":
            folder_name = upload_file_name()
            print(f"{folder_name=}")
            files = s3_api.get_images_list_data_from_s3(folder_name)

            return JSONResponse(content={"files": files})
        else:
            return JSONResponse(content={"message": "only ops user is allowed"})
    except Exception as error:
        return HANDLE_HTTP_EXCEPTION(status_code=500, error_message=str(error))


# Download File API
@data.post(endpoints.GET_DATA)
def get_file(data: models.Get_file, request: Request):
    """Fetch the S3 URL for a specific file."""
    try:
        user_data = get_access_token(request.cookies.get(ACCESS_TOKEN, ''))
        if user_data.get("role") == "Ops":
            data = data.file_name
            folder_name = upload_file_name()
            file_name = f"{folder_name}/{data}"

            # Generate file URL from S3
            url = s3_api.get_images_data_from_s3(file_name)
            return JSONResponse(content={"url": url})
        else:
            return JSONResponse(content={"message": "only ops user is allowed"})
    except HTTPException as http_error:
        return HANDLE_HTTP_EXCEPTION(status_code=http_error.status_code, error_message=http_error.detail)
    except Exception as error:
        return HANDLE_HTTP_EXCEPTION(status_code=500, error_message=str(error))
