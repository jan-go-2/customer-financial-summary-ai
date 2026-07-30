from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict


class GraphState(TypedDict):
    file_paths: List[str]
    provider: str
    validation_results: Optional[Dict[str, Any]]
    validated_files: List[str]
    classified_documents: List[Dict[str, Any]]
    extracted_documents: List[Dict[str, Any]]
    errors: List[str]
    status: str