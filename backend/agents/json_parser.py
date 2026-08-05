import json
import re


def parse_llm_json(response: str) -> dict:
    """
    Safely extracts JSON from an LLM response.

    Handles:

    - Plain JSON
    - Markdown code blocks
    - Extra explanatory text
    - Invalid responses

    Returns an empty dictionary if parsing fails.
    """

    if not response:
        return {}

    response = response.strip()

    # ----------------------------------------
    # Remove markdown code fences
    # ----------------------------------------

    response = re.sub(r"^```json", "", response, flags=re.IGNORECASE)
    response = re.sub(r"^```", "", response)
    response = re.sub(r"```$", "", response)

    response = response.strip()

    # ----------------------------------------
    # Try direct JSON
    # ----------------------------------------

    try:
        return json.loads(response)
    except Exception:
        pass

    # ----------------------------------------
    # Try extracting the first JSON object
    # ----------------------------------------

    match = re.search(r"\{.*\}", response, re.DOTALL)

    if match:

        try:
            return json.loads(match.group())
        except Exception:
            pass

    return {}