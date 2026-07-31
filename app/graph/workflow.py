from typing import Dict, Any, List
from langgraph.graph import StateGraph, START, END
from app.graph.state import GraphState

from app.services.file_validation import validate_files
from app.services.classifier import classify_document
from app.services.entity_extractor import extract_fields
from app.tools.timeline import build_timeline

DOC_TYPE_MAP = {
    # Property Documents
    "SALE_DEED": "property_sale_deed",
    "PROPERTY_SALE_DEED": "property_sale_deed",
    "PURCHASE_AGREEMENT": "purchase_agreement",
    "INHERITANCE_DOCUMENT": "inheritance_document",

    # Income Documents
    "SALARY_SLIP": "salary_slip",
    "BONUS_LETTER": "bonus_letter",
    "FORM_16": "form_16",
    "INCOME_TAX_RETURN": "income_tax_return",

    # Banking Documents
    "BANK_STATEMENT": "bank_statement",
    "FIXED_DEPOSIT_RECEIPT": "fixed_deposit_receipt",

    # Asset Documents
    "MUTUAL_FUND_STATEMENT": "mutual_fund_statement",
    "DEMAT_STATEMENT": "demat_statement",
    "INSURANCE_POLICY": "insurance_policy",

    # Liability Documents
    "HOME_LOAN_STATEMENT": "home_loan_statement",
    "CAR_LOAN_STATEMENT": "car_loan_statement",
    "CREDIT_CARD_STATEMENT": "credit_card_statement",

    # Employment Documents
    "OFFER_LETTER": "offer_letter",
    "PROMOTION_LETTER": "promotion_letter",
    "EXPERIENCE_LETTER": "experience_letter",

    # Identity Documents -- routed to the specific schemas, not the old combined one
    "PAN_CARD": "pan_card",
    "AADHAR_CARD": "aadhaar_card",     # classifier's spelling (missing second "A")
    "AADHAAR_CARD": "aadhaar_card",    # correct spelling, in case classifier uses this instead
    "IDENTITY_DOCUMENT": "identity_document",  # generic fallback, kept for backward compatibility

    # Legal Documents
    "POWER_OF_ATTORNEY": "power_of_attorney",
    "AFFIDAVIT": "affidavit",
}


def _map_doc_type_to_schema(doc_type: str) -> str:
    normalized = (doc_type or "").upper()
    return DOC_TYPE_MAP.get(normalized, normalized.lower())


# --- Node Definitions ---

def file_validation_node(state: GraphState) -> Dict[str, Any]:
    """Step 1: File Validation Node"""
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
        "status": "VALIDATED" if valid_file_paths else "FAILED_VALIDATION",
    }


def classifier_node(state: GraphState) -> Dict[str, Any]:
    """Step 2: Document Classifier Node"""
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
                "page_count": 0,
            })

    return {
        "classified_documents": classified_docs,
        "errors": errors,
        "status": "CLASSIFIED" if classified_docs else state.get("status", "VALIDATED"),
    }


def extractor_node(state: GraphState) -> Dict[str, Any]:
    """
    Step 3: Entity Extraction Node.
    Uses _map_doc_type_to_schema() so raw classifier labels (e.g. "SALE_DEED")
    get converted to schema keys (e.g. "property_sale_deed") before extraction --
    this was silently missing before and would fail every extraction.
    Skips anything classified as UNKNOWN, since there's no schema to extract against.
    """
    classified_docs = state.get("classified_documents", [])
    provider = state.get("provider", "groq")
    errors = list(state.get("errors", []))
    extracted_docs = []

    for doc in classified_docs:
        file_path = doc.get("file_path")
        doc_type_raw = doc.get("document_type")

        if not doc_type_raw or doc_type_raw == "UNKNOWN":
            errors.append(f"Skipped extraction for '{file_path}': classified as UNKNOWN")
            continue

        doc_type = _map_doc_type_to_schema(doc_type_raw)

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
    """Step 4: Timeline Builder Node. Converts extracted data into chronological events."""
    extracted_docs = state.get("extracted_documents", [])
    errors = list(state.get("errors", []))

    if not extracted_docs:
        return {"timeline": [], "status": "NO_EXTRACTED_DOCUMENTS", "errors": errors}

    try:
        timeline_response = build_timeline(extracted_docs)
        return {"timeline": timeline_response.events, "status": "TIMELINE_BUILT", "errors": errors}
    except Exception as exc:
        errors.append(f"Timeline generation failed: {str(exc)}")
        return {"timeline": [], "status": "FAILED_TIMELINE", "errors": errors}


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
        {"classifier": "classifier", END: END},
    )
    builder.add_edge("classifier", "extractor")
    builder.add_edge("extractor", "timeline")
    builder.add_edge("timeline", END)

    return builder.compile()


workflow_app = build_workflow()


def run_pipeline(file_paths: List[str], provider: str = "groq") -> Dict[str, Any]:
    """
    Single entry point: validate -> classify -> extract -> build timeline,
    for one or more files. Runs entirely through the graph.
    """
    initial_state: GraphState = {
        "file_paths": file_paths,
        "provider": provider,
        "validation_results": None,
        "validated_files": [],
        "classified_documents": [],
        "extracted_documents": [],
        "timeline": [],
        "errors": [],
        "status": "INITIATED",
    }

    return workflow_app.invoke(initial_state)


# Backward-compatible alias, in case other code still calls the old name.
run_financial_summary_pipeline = run_pipeline