from pydantic import BaseModel
from typing import List

class UploadResponse(BaseModel):
    message: str
    files: List[str]