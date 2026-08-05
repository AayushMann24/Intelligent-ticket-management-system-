import json
import re


def parse_llm_json(response: str) -> dict:
    """
    Extracts JSON from an LLM response.

    Handles:
    - Plain JSON
    - ```json ... ```
    - ``` ... ```
    """

    text = response.strip()

    # Remove markdown code blocks
    text = re.sub(r"^```json", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```", "", text)
    text = re.sub(r"```$", "", text)

    text = text.strip()

    try:
        return json.loads(text)

    except Exception:
        return {}