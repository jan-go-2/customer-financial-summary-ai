"""
Your original extract_fields(), now provider-agnostic. The Docling text
extraction lives right here since it's one small function only used by
this file -- no need for a separate module for it.
"""

from docling.document_converter import DocumentConverter

from app.prompts.extraction import build_prompt
from app.schemas.kyc_schemas import DOC_TYPE_SCHEMAS
from app.utils.json_utils import parse_json
from app.tools.llm_providers import call_llm


def get_document_text(pdf_path: str) -> str:
    """
    Docling: reads a PDF that already has a text layer (digital or
    already-OCR'd) and converts it to markdown/plain text.

    NOTE: this is not OCR. If you later need to handle scanned/image-only
    PDFs with no text layer, add a get_document_text_via_ocr(pdf_path)
    function here and call it as a fallback when this returns empty text.
    """
    converter = DocumentConverter()
    result = converter.convert(pdf_path)
    return result.document.export_to_markdown()


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