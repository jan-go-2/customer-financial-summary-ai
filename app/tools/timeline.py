from __future__ import annotations

from datetime import date
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

    Assumptions:
    - The extraction layer returns dates in ISO format (YYYY-MM-DD).
    - Each extracted document contains:
        * file_path
        * doc_type
        * confidence_score
        * extracted_data
    - Timeline is responsible only for building and sorting events.
    """

    events: List[TimelineEvent] = []

    for document in extracted_documents:
        doc_type = document.get("doc_type", "").lower()

        builder = EVENT_BUILDERS.get(doc_type)

        if not builder:
            continue   # or log it later

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

    company = data.get("company_name", "Unknown Company")
    pay_period = data.get("pay_period")

    return TimelineEvent(
        event_type=EventType.SALARY_RECEIVED,
        event_date=pay_period,
        description=f"Salary received from {company}",
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

    property_name = data.get(
        "property_address",
        "Unknown Property",
    )

    return TimelineEvent(
        event_type=EventType.PROPERTY_SOLD,
        event_date=data.get("agreement_date"),
        description=f"Property sold ({property_name})",
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

    property_name = data.get(
        "property_address",
        "Unknown Property",
    )

    return TimelineEvent(
        event_type=EventType.PROPERTY_PURCHASED,
        event_date=data.get("agreement_date"),
        description=f"Property purchased ({property_name})",
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