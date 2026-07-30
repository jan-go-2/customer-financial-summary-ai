from __future__ import annotations

from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


class EventType(str, Enum):
    ACTIVE_EMPLOYMENT = "active_employment"
    PAST_EMPLOYMENT = "past_employment"
    BUSINESS_INCOME = "business_income"
    PROPERTY_INHERITANCE = "property_inheritance"
    PROPERTY_PURCHASE = "property_purchase"
    PROPERTY_SALE = "property_sale"
    GIFT_RECEIVED = "gift_received"
    UNKNOWN = "unknown"


class Money(BaseModel):
    amount: float | None = None
    currency: str | None = None


class Evidence(BaseModel):
    document_id: str
    file_name: str
    page_number: int | None = None
    source_text: str | None = None


class FundingSource(BaseModel):
    source_type: str
    amount: Money | None = None
    supported_by_document: bool = False
    evidence: list[Evidence] = Field(default_factory=list)


class FinancialEvent(BaseModel):
    event_id: str
    document_id: str
    event_type: EventType

    customer_name: str | None = None

    start_date: date | None = None
    end_date: date | None = None
    status: str | None = None

    organization_name: str | None = None
    designation: str | None = None

    property_description: str | None = None
    property_id: str | None = None
    ownership_percentage: float | None = None

    monthly_income: Money | None = None
    annual_income: Money | None = None
    business_income: Money | None = None

    purchase_price: Money | None = None
    sale_price: Money | None = None
    inherited_value: Money | None = None
    gifted_value: Money | None = None

    current_documented_value: Money | None = None
    outstanding_liability: Money | None = None
    loan_repaid: Money | None = None
    net_sale_proceeds: Money | None = None

    funding_sources: list[FundingSource] = Field(default_factory=list)

    event_summary: str

    evidence: list[Evidence] = Field(default_factory=list)

    confidence: float = Field(
        default=0.0,
        ge=0,
        le=1
    )