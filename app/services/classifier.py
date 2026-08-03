import os
import logging
import json
from typing import Literal, Tuple, Optional, List, Dict, Any
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import fitz  # PyMuPDF
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError

# Load environment variables from .env file into os.environ
load_dotenv()

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# Document Types & Categories
# ------------------------------------------------------------------
DocumentType = Literal[
    "BONUS_LETTER", "BANK_STATEMENT", "FIXED_DEPOSIT_RECEIPT",
    "MUTUAL_FUND_STATEMENT", "DEMAT_STATEMENT", "INSURANCE_POLICY",
    "HOME_LOAN_STATEMENT", "CAR_LOAN_STATEMENT", "CREDIT_CARD_STATEMENT",
    "SALE_DEED", "PURCHASE_AGREEMENT", "INHERITANCE_DOCUMENT",
    "OFFER_LETTER", "PROMOTION_LETTER", "RELIEVING_LETTER",
    "EXPERIENCE_LETTER", "PAN_CARD", "AADHAR_CARD", "AADHAAR_CARD",
    "POWER_OF_ATTORNEY", "AFFIDAVIT", "GUARDIAN_CONSENT_FOR_MINOR",
    "SALARY_SLIP", "OTHER", "UNKNOWN"
]

Category = Literal[
    "INCOME_DOC", "BANKING_DOC", "ASSET_DOC",
    "LIABILITY_DOC", "PROPERTY_DOC", "EMPLOYMENT_DOC",
    "IDENTITY_DOC", "LEGAL_DOC", "OTHER", "UNKNOWN"
]

# ------------------------------------------------------------------
# Output Schema
# ------------------------------------------------------------------
class DocumentClassificationResult(BaseModel):
    file_path: str = Field(description="The path or identifier of the input file")
    document_type: DocumentType = Field(description="The specific type of the document")
    category: Category = Field(description="The broader functional category of the document")
    confidence_score: float = Field(description="Confidence score between 0.0 and 1.0")
    page_count: int = Field(description="Total number of pages in the PDF")


# ------------------------------------------------------------------
# Internal Functions
# ------------------------------------------------------------------
def _get_genai_client(api_key: Optional[str] = None) -> genai.Client:
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("GEMINI_API_KEY must be set in your .env file or environment variables.")
    return genai.Client(api_key=key)


def extract_pdf_info(file_path: str, max_pages: int = 3) -> Tuple[str, int]:
    ext = os.path.splitext(file_path)[1].lower()

    # Handle text or CSV files safely
    if ext in [".csv", ".txt"]:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read(3000), 1
        except Exception as e:
            logger.error(f"Failed reading text/csv file '{file_path}': {e}")
            return f"[FILE: {os.path.basename(file_path)}]", 1

    # Extract text from PDF documents
    try:
        with fitz.open(file_path) as doc:
            page_count = len(doc)
            if doc.is_encrypted:
                raise ValueError(f"Document at '{file_path}' is encrypted or password-protected.")

            extracted_text = ""
            for page_num in range(min(max_pages, page_count)):
                page = doc[page_num]
                extracted_text += page.get_text()

            return extracted_text.strip(), page_count
    except Exception as e:
        logger.error(f"Failed to extract text from PDF '{file_path}': {e}")
        return f"[UNABLE TO EXTRACT TEXT FROM {os.path.basename(file_path)}]", 1


@retry(
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=1.5, min=2, max=30),
    retry=retry_if_exception_type((APIError, Exception)),
    reraise=True
)
def _call_gemini_api(client: genai.Client, prompt: str) -> str:
    response = client.models.generate_content(
        model="gemini-3.6-flash",  # Fixed invalid model name
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=DocumentClassificationResult,
            temperature=0.1,
            system_instruction="You are an expert document classifier. Categorize documents strictly into the provided response schema."
        )
    )
    return response.text


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------
def classify_document(
    file_path: str, 
    api_key: Optional[str] = None, 
    client: Optional[genai.Client] = None
) -> Dict[str, Any]:
    """Classifies a single PDF document and returns a dictionary."""
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    logger.info(f"Classifying document: {file_path}")

    if client is None:
        client = _get_genai_client(api_key)

    text_content, page_count = extract_pdf_info(file_path)

    if not text_content:
        logger.warning(f"No text extracted from '{file_path}'. File may be scanned or image-based.")
        text_content = "[NO TEXT EXTRACTED - SCANNED OR IMAGE-BASED PDF]"

    prompt = f"""
    Analyze the following document text and classify it.

    File Path: {os.path.basename(file_path)}
    Page Count: {page_count}

    Document Text Content:
    ---
    {text_content[:3000]}
    ---
    """

    raw_json_response = _call_gemini_api(client, prompt)
    result = DocumentClassificationResult.model_validate_json(raw_json_response)
    result.file_path = file_path

    logger.info(f"Classified '{file_path}' as {result.document_type} ({result.category})")
    
    return result.model_dump()


def classify_documents(file_paths: List[str], api_key: Optional[str] = None) -> List[Dict[str, Any]]:
    """Classifies multiple PDF documents and returns a list of dictionaries."""
    client = _get_genai_client(api_key)
    results: List[Dict[str, Any]] = []

    for path in file_paths:
        try:
            # FIXED: Calling singular classify_document instead of recursive classify_documents
            res_dict = classify_document(file_path=path, client=client)
            results.append(res_dict)
        except Exception as e:
            logger.error(f"Skipping file '{path}' due to error: {e}")

    return results


