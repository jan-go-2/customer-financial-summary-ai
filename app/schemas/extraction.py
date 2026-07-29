from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from app.schemas.classification import DocumentType


class CustomerInfo(BaseModel):
    customer_name: Optional[str] = None
    employer_name: Optional[str] = None
    designation: Optional[str] = None


class FinancialData(BaseModel):
    income_amount: Optional[float] = None
    net_amount: Optional[float] = None
    currency: str = "USD"
    statement_date: Optional[str] = None
    period_start: Optional[str] = None
    period_end: Optional[str] = None


class LineItem(BaseModel):
    description: str
    amount: float


class ExtractedEntityItem(BaseModel):
    file_path: str
    document_type: DocumentType
    extraction_status: str = "SUCCESS"
    customer_info: CustomerInfo = Field(default_factory=CustomerInfo)
    financial_data: FinancialData = Field(default_factory=FinancialData)
    line_items: List[LineItem] = []
    confidence: float = 0.95


class ExtractionResponse(BaseModel):
    extracted_entities: List[ExtractedEntityItem] = []
