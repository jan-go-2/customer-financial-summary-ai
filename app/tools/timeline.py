from __future__ import annotations

from datetime import datetime, date
from typing import Callable, Dict, List, Optional

from app.schemas.timeline import (
    TimelineEvent,
    TimelineResponse,
    EventType,
)


def build_timeline(
    extracted_documents: List[Dict],
) -> TimelineResponse:
    """
    Builds a chronological customer financial timeline from extracted documents.

    Input:
    [
        {
            "file_path": "uploaded_documents/salary_jan.pdf",
            "doc_type": "salary_slip",
            "confidence_score": 0.98,
            "extracted_data": {
                "employee_name": "John Doe",
                "company_name": "ABC Pvt Ltd",
                "gross_salary": "90000",
                "net_salary": "85000",
                "pay_period": "2024-01-31"
            }
        },
        {
            "file_path": "uploaded_documents/property_sale.pdf",
            "doc_type": "property_sale_deed",
            "confidence_score": 0.95,
            "extracted_data": {
                "seller_name": "John Doe",
                "buyer_name": "XYZ",
                "agreement_date": "2025-03-15",
                "sale_consideration": "7500000"
            }
        }
    ]

    Output:
    TimelineResponse(
        events=[
            TimelineEvent(
                event_type=EventType.SALARY_RECEIVED,
                event_date=date(2024, 1, 31),
                description="Salary received from ABC Pvt Ltd",
                source_document="uploaded_documents/salary_jan.pdf",
                confidence_score=0.98,
                metadata={...}
            ),
            TimelineEvent(
                event_type=EventType.PROPERTY_SOLD,
                event_date=date(2025, 3, 15),
                description="Property sold",
                source_document="uploaded_documents/property_sale.pdf",
                confidence_score=0.95,
                metadata={...}
            )
        ]
    )

    The returned events are sorted chronologically by event_date.
    """

    events: List[TimelineEvent] = []

    for document in extracted_documents:
        doc_type = document.get("doc_type", "").lower()

        builder = EVENT_BUILDERS.get(doc_type)

        if builder:
            event = builder(document)

            if event:
                events.append(event)

    # Sort chronologically.
    events.sort(
        key=lambda event: event.event_date or date.max
    )

    return TimelineResponse(events=events)


# -------------------------------------------------------------------------
# Event Builders
# -------------------------------------------------------------------------

def build_salary_event(
    document: Dict,
) -> Optional[TimelineEvent]:

    data = document.get("extracted_data", {})

    return TimelineEvent(
        event_type=EventType.SALARY_RECEIVED,
        event_date=parse_date(
            data.get("pay_period")
        ),
        description=f"Salary received from {data.get('company_name', 'Unknown Company')}",
        source_document=document.get("file_path", ""),
        confidence_score=document.get(
            "confidence_score",
            0.0,
        ),
        metadata=data,
    )


def build_property_sale_event(
    document: Dict,
) -> Optional[TimelineEvent]:

    data = document.get("extracted_data", {})

    return TimelineEvent(
        event_type=EventType.PROPERTY_SOLD,
        event_date=parse_date(
            data.get("agreement_date")
        ),
        description="Property sold",
        source_document=document.get("file_path", ""),
        confidence_score=document.get(
            "confidence_score",
            0.0,
        ),
        metadata=data,
    )


def build_property_purchase_event(
    document: Dict,
) -> Optional[TimelineEvent]:

    data = document.get("extracted_data", {})

    return TimelineEvent(
        event_type=EventType.PROPERTY_PURCHASED,
        event_date=parse_date(
            data.get("agreement_date")
        ),
        description="Property purchased",
        source_document=document.get("file_path", ""),
        confidence_score=document.get(
            "confidence_score",
            0.0,
        ),
        metadata=data,
    )


# -------------------------------------------------------------------------
# Registry
# -------------------------------------------------------------------------

EVENT_BUILDERS: Dict[
    str,
    Callable[[Dict], Optional[TimelineEvent]]
] = {
    "salary_slip": build_salary_event,
    "property_sale_deed": build_property_sale_event,
    "property_purchase_deed": build_property_purchase_event,
}


# -------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------

def parse_date(
    value: Optional[str],
) -> Optional[date]:

    if not value:
        return None

    formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%Y/%m/%d",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(
                value,
                fmt,
            ).date()
        except ValueError:
            continue

    return None