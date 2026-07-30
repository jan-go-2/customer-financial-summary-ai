import json


def clean_json_text(output: str) -> str:
    """Strip markdown code fences the model sometimes wraps its JSON in."""
    text = output.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    return text


def parse_json(output: str) -> dict:
    """Parse the model's raw text into a plain dict. Raises if invalid."""
    return json.loads(clean_json_text(output))


def print_json(output: str) -> None:
    """Same behavior as your original print_json(): pretty-print or show raw text."""
    try:
        parsed = parse_json(output)
        print(json.dumps(parsed, indent=4, ensure_ascii=False))
    except Exception:
        print("Could not parse JSON.\n")
        print(output)