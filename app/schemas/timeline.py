from datetime import date
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TimelineEvent(BaseModel):
    """
    Represents one chronological event in the customer's financial journey.
    """

    event_type: str = Field(
        ...,
        description="Type of event (employment, property_purchase, property_sale, etc.)"
    )

    event_date: Optional[date] = Field(
        default=None,
        description="Primary date used for timeline ordering."
    )

    title: str = Field(
        ...,
        description="Short title shown in the timeline."
    )

    description: Optional[str] = Field(
        default=None,
        description="Additional information about the event."
    )

    source_document: Optional[str] = Field(
        default=None,
        description="Original document filename."
    )

    confidence_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=1,
        description="Confidence received from classifier/extraction."
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Extra extracted information associated with the event."
    )


class TimelineResponse(BaseModel):
    """
    Response returned by Timeline Builder.
    """

    events: List[TimelineEvent] = Field(default_factory=list)