from __future__ import annotations

from datetime import date
from typing import Callable, Dict, List

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

    Assumptions:
    - Extraction returns dates in ISO format (YYYY-MM-DD).
    - One document may generate multiple timeline events.
    """

    events: List[TimelineEvent] = []

    for document in extracted_documents:
        doc_type = document.get("doc_type", "").lower()

        builder = EVENT_BUILDERS.get(doc_type)

        if not builder:
            continue

        document_events = builder(document)

        if document_events:
            events.extend(document_events)

    events.sort(
        key=lambda event: event.event_date or date.max
    )

    return TimelineResponse(events=events)


# -------------------------------------------------------------------------
# Salary
# -------------------------------------------------------------------------

def build_salary_event(document: Dict) -> List[TimelineEvent]:

    data = document.get("extracted_data", {})

    return [
        TimelineEvent(
            event_type=EventType.SALARY_RECEIVED,
            event_date=data.get("pay_period"),
            description=f"Salary received from {data.get('company_name', 'Unknown Company')}",
            source_document=document.get("file_path", ""),
            confidence_score=document.get("confidence_score", 0.0),
            metadata=data,
        )
    ]


# -------------------------------------------------------------------------
# Property Purchase
# -------------------------------------------------------------------------

def build_property_purchase_event(document: Dict) -> List[TimelineEvent]:

    data = document.get("extracted_data", {})

    property_name = data.get(
        "property_address",
        "Unknown Property",
    )

    return [
        TimelineEvent(
            event_type=EventType.PROPERTY_PURCHASED,
            event_date=data.get("agreement_date"),
            description=f"Property purchased ({property_name})",
            source_document=document.get("file_path", ""),
            confidence_score=document.get("confidence_score", 0.0),
            metadata=data,
        )
    ]


# -------------------------------------------------------------------------
# Property Sale
# -------------------------------------------------------------------------

def build_property_sale_event(document: Dict) -> List[TimelineEvent]:

    data = document.get("extracted_data", {})

    property_name = data.get(
        "property_address",
        "Unknown Property",
    )

    return [
        TimelineEvent(
            event_type=EventType.PROPERTY_SOLD,
            event_date=data.get("agreement_date"),
            description=f"Property sold ({property_name})",
            source_document=document.get("file_path", ""),
            confidence_score=document.get("confidence_score", 0.0),
            metadata=data,
        )
    ]


# -------------------------------------------------------------------------
# Inheritance
# -------------------------------------------------------------------------

def build_inheritance_event(document: Dict) -> List[TimelineEvent]:

    data = document.get("extracted_data", {})

    return [
        TimelineEvent(
            event_type=EventType.INHERITANCE_RECEIVED,
            event_date=data.get("date_of_inheritance"),
            description=f"Inheritance received from {data.get('deceased_name', 'Unknown')}",
            source_document=document.get("file_path", ""),
            confidence_score=document.get("confidence_score", 0.0),
            metadata=data,
        )
    ]


# -------------------------------------------------------------------------
# Relieving Letter
# -------------------------------------------------------------------------

def build_relieving_event(document: Dict) -> List[TimelineEvent]:

    data = document.get("extracted_data", {})

    company = data.get("company_name", "Unknown Company")
    designation = data.get("designation", "Employee")

    return [
        TimelineEvent(
            event_type=EventType.EMPLOYMENT_STARTED,
            event_date=data.get("date_of_joining"),
            description=f"Joined {company} as {designation}",
            source_document=document.get("file_path", ""),
            confidence_score=document.get("confidence_score", 0.0),
            metadata=data,
        ),
        TimelineEvent(
            event_type=EventType.EMPLOYMENT_ENDED,
            event_date=data.get("relieving_date"),
            description=f"Employment ended at {company}",
            source_document=document.get("file_path", ""),
            confidence_score=document.get("confidence_score", 0.0),
            metadata=data,
        ),
    ]


def build_bank_statement_event(
    document: Dict,
) -> List[TimelineEvent]:

    data = document.get("extracted_data", {})

    period = data.get("statement_period")

    start_date = None
    if period and " - " in period:
        start_date = period.split(" - ")[0]

    return [
        TimelineEvent(
            event_type=EventType.BANK_STATEMENT,
            event_date=start_date,
            description="Bank statement available",
            source_document=document.get("file_path", ""),
            confidence_score=document.get("confidence_score", 0.0),
            metadata=data,
        )
    ]

# -------------------------------------------------------------------------
# Registry
# -------------------------------------------------------------------------

EVENT_BUILDERS: Dict[
    str,
    Callable[[Dict], List[TimelineEvent]]
] = {
    # Income
    "salary_slip": build_salary_event,

    # Property
    "purchase_agreement": build_property_purchase_event,
    "property_purchase_deed": build_property_purchase_event,
    "property_sale_deed": build_property_sale_event,

    # Legal
    "inheritance_document": build_inheritance_event,

    # Employment
    "relieving_letter": build_relieving_event,
    "bank_statement": build_bank_statement_event, 
}