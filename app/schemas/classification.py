from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class DocumentType(str, Enum):
    SALARY_SLIP = "SALARY_SLIP"
    BANK_STATEMENT = "BANK_STATEMENT"
    TAX_RETURN = "TAX_RETURN"
    PROPERTY_DOCUMENT = "PROPERTY_DOCUMENT"
    BUSINESS_RECORD = "BUSINESS_RECORD"
    INHERITANCE_RECORD = "INHERITANCE_RECORD"
    OTHER = "OTHER"


class DocumentMetadata(BaseModel):
    is_scanned_pdf: bool = False
    requires_ocr: bool = False


class ClassifiedDocumentItem(BaseModel):
    file_path: str
    document_type: DocumentType = DocumentType.OTHER
    confidence_score: float = Field(default=0.9, ge=0.0, le=1.0)
    page_count: Optional[int] = 1
    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata)


class ClassificationResponse(BaseModel):
    classified_documents: List[ClassifiedDocumentItem] =  Field(
        default_factory=list
    )
