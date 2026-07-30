import shutil
import tempfile
from pathlib import Path
from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.graph.workflow import run_financial_summary_pipeline, run_pipeline

router = APIRouter()

UPLOAD_DIR = Path("uploaded_documents")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    uploaded_file_paths = []
    file_names = []

    for file in files:
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        uploaded_file_paths.append(str(file_path))
        file_names.append(file.filename)

    workflow_result = run_financial_summary_pipeline(uploaded_file_paths)

    return {
        "message": "Documents uploaded successfully.",
        "files": file_names,
        "workflow_result": workflow_result
    }


@router.post("/extract")
async def extract_document(file: UploadFile = File(...), provider: str = "groq"):
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    result = run_pipeline(tmp_path, provider=provider)

    if result.get("error"):
        raise HTTPException(status_code=422, detail=result["error"])

    return {
        "doc_type": result.get("doc_type"),
        "confidence": result.get("classification_confidence"),
        "extracted_data": result.get("extracted_data"),
        "narrative": result.get("narrative"),
    }