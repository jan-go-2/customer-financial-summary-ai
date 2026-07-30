from app.schemas.doc_schema import DOC_TYPE_SCHEMAS


def build_prompt(document_text: str, doc_type: str) -> str:
    if doc_type not in DOC_TYPE_SCHEMAS:
        raise ValueError(
            f"Unknown document type: {doc_type}\n"
            f"Supported: {list(DOC_TYPE_SCHEMAS.keys())}"
        )

    fields = list(DOC_TYPE_SCHEMAS[doc_type].model_fields.keys())

    return f"""
You are an expert KYC document extraction assistant.

Document Type:
{doc_type}

Extract ONLY the following fields.

Fields:
{', '.join(fields)}

Instructions:
1. Return ONLY valid JSON.
2. Use the exact field names.
3. If a value is unavailable, return null.
4. Do not explain anything.
5. Do not include markdown.

Document:

{document_text}

JSON:
"""