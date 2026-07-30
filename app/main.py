"""
Same as the __main__ block in your original doc_llm_extraction.py --
just run this file directly. No API, no agent, no LangGraph.
"""

from dotenv import load_dotenv

from app.services.entity_extractor import extract_fields
from app.utils.json_utils import print_json

load_dotenv()

PDF_PATH = "Sale_Agreement_For_Plot.pdf"
DOC_TYPE = "property_sale_deed"
PROVIDER = "groq"  # "local", "groq", "cerebras", "openrouter", "mistral", "nvidia_nim"


if __name__ == "__main__":
    print("=" * 60)
    print("PDF:", PDF_PATH)
    print("Document Type:", DOC_TYPE)
    print("Provider:", PROVIDER)
    print("=" * 60)

    result = extract_fields(PDF_PATH, DOC_TYPE, provider=PROVIDER)

    print("\nEXTRACTED (validated) DATA\n")
    print_json(result.model_dump_json())