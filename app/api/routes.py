from fastapi import APIRouter, UploadFile, File
from typing import List
from pathlib import Path
import shutil

router = APIRouter()

UPLOAD_DIR = Path("uploaded_documents")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...)):

    uploaded_files = []

    for file in files:

        file_path = UPLOAD_DIR / file.filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        uploaded_files.append(file.filename)

    return {
        "message": "Documents uploaded successfully.",
        "files": uploaded_files
    }