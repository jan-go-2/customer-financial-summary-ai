from typing import Dict, Any, List
from langgraph.graph import StateGraph, START, END
from app.graph.state import GraphState

from app.services.file_validation import validate_files
from app.services.classifier import classify_document
from app.services.entity_extractor import extract_fields
from app.tools.timeline import build_timeline

DOC_TYPE_MAP = {
    "SALE_DEED": "property_sale_deed",
    "PURCHASE_AGREEMENT": "property_purchase_deed",
    "PROPERTY_SALE_DEED": "property_sale_deed",
    "SALARY_SLIP": "salary_slip",
    "BONUS_LETTER": "salary_slip",
    "PAN_CARD": "identity_document",
    "AADHAR_CARD": "identity_document",
    "IDENTITY_DOCUMENT": "identity_document"
}


def _map_doc_type_to_schema(doc_type: str) -> str:
    normalized = doc_type.upper()
    if normalized in DOC_TYPE_MAP:
        return DOC_TYPE_MAP[normalized]
    return doc_type.lower()


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

    classified_docs = []
    errors = list(state.get("errors", []))

    for file_path in validated_files:
        try:
            classification_res = classify_document(file_path)
            classified_docs.append(classification_res.model_dump())
        except Exception as e:
            errors.append(f"Classification skipped/failed for '{file_path}': {e}")
            classified_docs.append({
                "file_path": file_path,
                "document_type": "UNKNOWN",
                "category": "UNKNOWN",
                "confidence_score": 0.0,
                "page_count": 0
            })

    return {
        "classified_documents": classified_docs,
        "errors": errors,
        "status": "CLASSIFIED" if classified_docs else state.get("status", "VALIDATED")
    }

def extractor_node(state: GraphState) -> Dict[str, Any]:
    """
    Step 3: Entity Extraction Node.
    """
    classified_docs = state.get("classified_documents", [])
    provider = state.get("provider", "groq")
    errors = list(state.get("errors", []))
    extracted_docs = []
 
    for doc in classified_docs:
        file_path = doc.get("file_path")
        doc_type_raw = doc.get("document_type")
        doc_type = doc_type_raw.lower() if isinstance(doc_type_raw, str) else str(doc_type_raw).lower()
 
        try:
            extracted = extract_fields(file_path, doc_type, provider=provider)
            extracted_docs.append({
                "file_path": file_path,
                "doc_type": doc_type,
                "confidence_score": doc.get("confidence_score"),
                "extracted_data": extracted.model_dump(),
            })
        except Exception as exc:
            errors.append(f"Extraction failed for {file_path}: {exc}")
 
    return {
        "extracted_documents": extracted_docs,
        "errors": errors,
        "status": "EXTRACTED" if extracted_docs else "FAILED_EXTRACTION",
    }

def timeline_node(state: GraphState) -> Dict[str, Any]:
    """
    Step 4: Timeline Builder Node.

    Converts extracted document data into chronological timeline events.
    """

    extracted_docs = state.get("extracted_documents", [])
    errors = list(state.get("errors", []))

    if not extracted_docs:
        return {
            "timeline": [],
            "status": "NO_EXTRACTED_DOCUMENTS",
            "errors": errors,
        }

    try:
        timeline_response = build_timeline(extracted_docs)

        return {
            "timeline": timeline_response.events,
            "status": "TIMELINE_BUILT",
            "errors": errors,
        }

    except Exception as exc:
        errors.append(f"Timeline generation failed: {str(exc)}")

        return {
            "timeline": [],
            "status": "FAILED_TIMELINE",
            "errors": errors,
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
    builder.add_node("extractor", extractor_node)
    builder.add_node("timeline", timeline_node)

    builder.add_edge(START, "file_validation")

    builder.add_conditional_edges(
        "file_validation",
        should_continue_after_validation,
        {
            "classifier": "classifier",
            END: END,
        },
    )

    builder.add_edge("classifier", "extractor")
    builder.add_edge("extractor", "timeline")
    builder.add_edge("timeline", END)

    return builder.compile()


workflow_app = build_workflow()


def run_financial_summary_pipeline(file_paths: List[str]) -> Dict[str, Any]:
    initial_state: GraphState = {
        "file_paths": file_paths,
        "validation_results": None,
        "validated_files": [],
        "classified_documents": [],
        "timeline": [],
        "errors": [],
        "status": "INITIATED"
    }

    return workflow_app.invoke(initial_state)


def run_pipeline(file_path: str, provider: str = "groq") -> Dict[str, Any]:
    validation = validate_files([file_path])
    if not validation.valid_files:
        return {"error": "Invalid file format or file failed validation"}

    try:
        classification = classify_document(file_path)
        doc_type_val = classification.document_type
        confidence = classification.confidence_score
        category = classification.category
    except Exception as e:
        return {"error": f"Failed to classify document: {str(e)}"}

    doc_type_schema_key = _map_doc_type_to_schema(doc_type_val)

    try:
        extracted = extract_fields(file_path, doc_type_schema_key, provider=provider)
        extracted_data = extracted.model_dump()
    except Exception as e:
        extracted_data = {"error": str(e)}

    return {
        "doc_type": doc_type_val,
        "category": category,
        "classification_confidence": confidence,
        "extracted_data": extracted_data,
        "narrative": f"Successfully processed {file_path} as {doc_type_val} ({category})."
    }

