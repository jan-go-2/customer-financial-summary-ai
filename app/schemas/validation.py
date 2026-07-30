from pydantic import BaseModel, Field
from typing import List, Optional


class ValidatedFileItem(BaseModel):
    file_path: str
    file_name: str
    extension: str
    size_bytes: int = 0
    mime_type: str = "application/octet-stream"
    is_valid: bool = True


class InvalidFileItem(BaseModel):
    file_path: str
    reason: str
    error_code: str = "INVALID_FORMAT"


class FileValidationResponse(BaseModel):
    status: str = Field(default="SUCCESS", description="SUCCESS | PARTIAL_SUCCESS | FAILED")
    error: Optional[str] = Field(default=None, description="Error message provided from validation")
    valid_files: List[ValidatedFileItem] = Field(default_factory=list)
    invalid_files: List[InvalidFileItem] = Field(default_factory=list)


