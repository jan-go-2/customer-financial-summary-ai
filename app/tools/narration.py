
from __future__ import annotations

import json

import httpx


OLLAMA_URL = "http://localhost:11434"
AI_MODEL = "qwen2.5:7b"


async def generate_narration(
    customer_name: str,
    timeline: list[dict],
    financial_summary: dict,
    triggers: list[dict],
    contradictions: list[dict],
    missing_information: list[str],
) -> str:
    evidence_package = {
        "customer_name": customer_name,
        "timeline": timeline,
        "financial_summary": financial_summary,
        "triggers": triggers,
        "contradictions": contradictions,
        "missing_information": missing_information
    }

    prompt = f"""
You are preparing a customer financial journey report
for a banking KYC analyst.

Validated evidence package:

{json.dumps(evidence_package, indent=2, default=str)}

Generate an approximately two-page customer profile.

Use these sections:
1. Customer overview
2. Employment history
3. Business history
4. Inheritance and gifts
5. Property purchase and sale journey
6. Documented financial position
7. Review triggers and evidence gaps
8. Conclusion

Rules:
- Use only the supplied validated information.
- Present events chronologically.
- Do not invent dates, values or relationships.
- Do not infer that salary or inheritance funded a purchase.
- Do not describe the customer as suspicious, fraudulent,
  high risk or low risk.
- Preserve original currencies.
- Explain that net worth is based only on documented values.
- Mention missing evidence clearly.
- Reference document names and page numbers when available.
"""

    async with httpx.AsyncClient(timeout=240) as client:
        response = await client.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": AI_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1
                }
            }
        )

        response.raise_for_status()

    return response.json()["response"]