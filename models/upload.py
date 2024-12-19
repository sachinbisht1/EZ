"""All account request models."""
from pydantic import BaseModel


class Get_file(BaseModel):
    file_name: str
