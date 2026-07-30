from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict


class GraphState(TypedDict):
    """
    Represents the shared state of the customer financial summary LangGraph workflow.
    """
    file_paths: List[str]
    validation_results: Optional[Dict[str, Any]]
    validated_files: List[str]
    classified_documents: List[Dict[str, Any]]
    errors: List[str]
    status: str
