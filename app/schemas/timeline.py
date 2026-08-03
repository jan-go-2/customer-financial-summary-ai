from datetime import date
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class EventType(str, Enum):
    SALARY_RECEIVED = "salary_received"
    PROPERTY_PURCHASED = "property_purchased"
    PROPERTY_SOLD = "property_sold"
    BUSINESS_ACTIVITY = "business_activity"
    INHERITANCE_RECEIVED = "inheritance_received"
    EMPLOYMENT_ENDED = "employment_ended"
    OTHER = "other"


class TimelineEvent(BaseModel):
    event_type: EventType

    event_date: Optional[date] = None

    description: str

    source_document: str

    confidence_score: float = Field(
        default=0.0,
        ge=0,
        le=1,
    )

    metadata: Dict[str, Any] = Field(default_factory=dict)


class TimelineResponse(BaseModel):
    events: List[TimelineEvent] = Field(default_factory=list)