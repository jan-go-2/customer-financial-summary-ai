from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict
<<<<<<< HEAD
from app.schemas.timeline import TimelineEvent
=======
>>>>>>> 089050e (add schema, prompt, extraction for all document types)


class GraphState(TypedDict):
    file_paths: List[str]
    provider: str
    validation_results: Optional[Dict[str, Any]]
    validated_files: List[str]
    classified_documents: List[Dict[str, Any]]
    extracted_documents: List[Dict[str, Any]]
<<<<<<< HEAD
    timeline: List[TimelineEvent]
=======
    timeline: List[Dict[str, Any]]
>>>>>>> 089050e (add schema, prompt, extraction for all document types)
    errors: List[str]
    status: str