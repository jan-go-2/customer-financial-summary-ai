import mimetypes
from pathlib import Path
from typing import List, Union

from app.schemas.validation import FileValidationResponse, ValidatedFileItem, InvalidFileItem

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".xlsx",
    ".xls",
    ".csv",
}

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit


def get_mime_type(extension: str) -> str:
    mime_map = {
        ".pdf": "application/pdf",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".xls": "application/vnd.ms-excel",
        ".csv": "text/csv",
    }
    return mime_map.get(extension.lower(), "application/octet-stream")


def validate_files(file_paths: List[Union[str, Path]]) -> FileValidationResponse:
    valid_files: List[ValidatedFileItem] = []
    invalid_files: List[InvalidFileItem] = []

    for file_item in file_paths:
        path = Path(file_item)
        str_path = str(path)

        if not path.exists():
            invalid_files.append(
                InvalidFileItem(
                    file_path=str_path,
                    reason="File does not exist",
                    error_code="FILE_NOT_FOUND"
                )
            )
            continue

        ext = path.suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            invalid_files.append(
                InvalidFileItem(
                    file_path=str_path,
                    reason=f"Unsupported format '{ext}' or file corrupted",
                    error_code="INVALID_FORMAT"
                )
            )
            continue

        size_bytes = path.stat().st_size
        if size_bytes > MAX_FILE_SIZE_BYTES:
            invalid_files.append(
                InvalidFileItem(
                    file_path=str_path,
                    reason=f"File size ({size_bytes} bytes) exceeds maximum limit",
                    error_code="FILE_TOO_LARGE"
                )
            )
            continue

        mime_type = get_mime_type(ext) or (mimetypes.guess_type(path)[0] or "application/octet-stream")

        valid_files.append(
            ValidatedFileItem(
                file_path=str_path,
                file_name=path.name,
                extension=ext,
                size_bytes=size_bytes,
                mime_type=mime_type,
                is_valid=True
            )
        )

    if valid_files and not invalid_files:
        status = "SUCCESS"
    elif valid_files and invalid_files:
        status = "PARTIAL_SUCCESS"
    else:
        status = "FAILED"

    return FileValidationResponse(
        status=status,
        valid_files=valid_files,
        invalid_files=invalid_files
    )