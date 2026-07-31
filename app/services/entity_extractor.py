from pathlib import Path
from app.prompts.extraction import build_prompt
from app.schemas.doc_schema import DOC_TYPE_SCHEMAS
from app.utils.json_utils import parse_json
from app.tools.llm_providers import call_llm
from typing import List, Dict, Any


def get_document_text(pdf_path: str) -> str:
    """
    Docling: reads a PDF that already has a text layer (digital or
    already-OCR'd) and converts it to markdown/plain text.
    """
    try:
        from docling.document_converter import DocumentConverter
        converter = DocumentConverter()
        result = converter.convert(pdf_path)
        return result.document.export_to_markdown()
    except Exception:
        path_obj = Path(pdf_path)
        if path_obj.exists():
            return path_obj.read_text(errors="ignore")
        return ""


def extract_fields(pdf_path: str, doc_type: str, provider: str = "groq"):
    """
    Reads the PDF, calls the LLM, and returns a VALIDATED Pydantic object
    (e.g. a PropertySaleDeed instance) -- not just a raw dict -- so bad or
    missing fields from the LLM raise immediately instead of silently
    passing through to your merge step.
    """
    if doc_type not in DOC_TYPE_SCHEMAS:
        raise ValueError(
            f"Unknown document type: {doc_type}\n"
            f"Supported: {list(DOC_TYPE_SCHEMAS.keys())}"
        )

    print("Reading document with Docling...")
    document_text = get_document_text(pdf_path)
    print(f"Characters extracted: {len(document_text)}")

    prompt = build_prompt(document_text, doc_type)
    raw_output = call_llm(prompt, provider)

    data = parse_json(raw_output)
    schema_cls = DOC_TYPE_SCHEMAS[doc_type]
    return schema_cls(**data)


def extract_fields_batch(documents: List[Dict[str, str]], provider: str = "groq") -> List[Dict[str, Any]]:
    """
    Runs extract_fields() once per document, since extract_fields() itself
    only handles one file at a time.

    documents: a list like
        [
            {"file_path": "salary_slip.pdf", "doc_type": "salary_slip"},
            {"file_path": "sale_deed.pdf", "doc_type": "property_sale_deed"},
        ]

    Returns a list of results in the same order, one per input document.
    A document that fails to extract does NOT stop the others -- its error
    is recorded instead, so one bad file doesn't kill the whole batch.
    """
    results = []

    for doc in documents:
        file_path = doc["file_path"]
        doc_type = doc["doc_type"]

        try:
            extracted = extract_fields(file_path, doc_type, provider=provider)
            results.append({
                "file_path": file_path,
                "doc_type": doc_type,
                "extracted_data": extracted.model_dump(),
            })
        except Exception as exc:
            results.append({
                "file_path": file_path,
                "doc_type": doc_type,
                "error": str(exc),
            })

    return results