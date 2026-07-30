from typing import Dict, Any, List
from langgraph.graph import StateGraph, START, END
from app.graph.state import GraphState

from app.services.file_validation import validate_files
from app.services.classifier import classify_document


# --- Node Definitions ---

def file_validation_node(state: GraphState) -> Dict[str, Any]:
    """
    Step 1: File Validation Node
    """
    input_files = state.get("file_paths", [])
    validation_res = validate_files(input_files)

    valid_file_paths = [f.file_path for f in validation_res.valid_files]
    errors = list(state.get("errors", []))

    if validation_res.invalid_files:
        errors.append(f"Validation warnings: {len(validation_res.invalid_files)} invalid file(s) skipped.")

    return {
        "validation_results": validation_res.model_dump(),
        "validated_files": valid_file_paths,
        "errors": errors,
        "status": "VALIDATED" if valid_file_paths else "FAILED_VALIDATION"
    }


def classifier_node(state: GraphState) -> Dict[str, Any]:
    """
    Step 2: Document Classifier Node
    """
    validated_files = state.get("validated_files", [])
    if not validated_files:
        return {"classified_documents": [], "status": "NO_VALID_FILES"}

    classification_res = classify_document(validated_files)

    return {
        "classified_documents": [doc.model_dump() for doc in classification_res.classified_documents],
        "status": "CLASSIFIED"
    }


# --- Conditional Edge Logic ---

def should_continue_after_validation(state: GraphState) -> str:
    if state.get("validated_files"):
        return "classifier"
    return END


# --- Graph Construction ---

def build_workflow():
    builder = StateGraph(GraphState)

    builder.add_node("file_validation", file_validation_node)
    builder.add_node("classifier", classifier_node)

    builder.add_edge(START, "file_validation")
    builder.add_conditional_edges(
        "file_validation",
        should_continue_after_validation,
        {
            "classifier": "classifier",
            END: END
        }
    )
    builder.add_edge("classifier", END)

    return builder.compile()


workflow_app = build_workflow()


def run_financial_summary_pipeline(file_paths: List[str]) -> Dict[str, Any]:
    initial_state: GraphState = {
        "file_paths": file_paths,
        "validation_results": None,
        "validated_files": [],
        "classified_documents": [],
        "errors": [],
        "status": "INITIATED"
    }

    return workflow_app.invoke(initial_state)

