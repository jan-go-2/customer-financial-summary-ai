from app.schemas.doc_schema import DOC_TYPE_SCHEMAS


def build_prompt(document_text: str, doc_type: str) -> str:
    if doc_type not in DOC_TYPE_SCHEMAS:
        raise ValueError(
            f"Unknown document type: {doc_type}\n"
            f"Supported: {list(DOC_TYPE_SCHEMAS.keys())}"
        )

    model_fields = DOC_TYPE_SCHEMAS[doc_type].model_fields

    field_lines = []
    for name, info in model_fields.items():
        if info.description:
            field_lines.append(f"- {name}: {info.description}")
        else:
            field_lines.append(f"- {name}")
    fields_block = "\n".join(field_lines)

    return f"""
You are an expert KYC document extraction assistant.

Document Type:
{doc_type}

Extract ONLY the following fields. If a field has a description below,
that description is the definition of the field -- follow it exactly,
even if the document doesn't use the same words. If a field has no
description, use your best reasonable judgment based on its name.

Fields:
{fields_block}

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