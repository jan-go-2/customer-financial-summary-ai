from fastapi import FastAPI
from dotenv import load_dotenv

from app.api.routes import router
from app.services.entity_extractor import extract_fields
from app.utils.json_utils import print_json

load_dotenv()

app = FastAPI(
    title="Customer Financial Summary AI"
)

app.include_router(router)

PDF_PATH = "Sale_Agreement_For_Plot.pdf"
DOC_TYPE = "property_sale_deed"
PROVIDER = "groq"


if __name__ == "__main__":
    print("=" * 60)
    print("PDF:", PDF_PATH)
    print("Document Type:", DOC_TYPE)
    print("Provider:", PROVIDER)
    print("=" * 60)

    result = extract_fields(PDF_PATH, DOC_TYPE, provider=PROVIDER)

    print("\nEXTRACTED (validated) DATA\n")
    print_json(result.model_dump_json())