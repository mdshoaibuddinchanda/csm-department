# extractor.py

import json
import os
import httpx

from treatments import get_treatment_by_alias

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME   = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")

SYSTEM_PROMPT = """You are an information extraction engine for a dental clinic appointment assistant.

Your job is to extract structured information from a single user message.

IMPORTANT RULES:
- Output STRICT JSON only
- Do NOT explain anything
- Do NOT guess missing values
- If something is unclear, set it to null
- If confidence is low, say so explicitly

You do NOT manage conversation.
You do NOT decide what to ask next.
You ONLY extract what is clearly stated.

--------------------------------

FIELDS TO EXTRACT:

intent:
- One of: BOOK, CANCEL, RESCHEDULE
- null if intent is unclear

date_text:
- Raw date phrase exactly as the user said it
- Examples: "next friday", "3rd feb", "same day"
- null if not mentioned

time_text:
- Raw time phrase exactly as the user said it
- Examples: "3pm", "after lunch", "same time"
- null if not mentioned

patient_name:
- Extract ONLY if the user clearly states their name
- Examples: "My name is Rahul", "This is Mustafa"
- DO NOT infer from casual sentences
- null if not explicit

patient_phone:
- Extract ONLY if a phone number is explicitly given
- Digits only
- null otherwise

treatment_text:
- Raw treatment phrase exactly as the user said it
- Examples: "root canal", "checkup", "tooth extraction", "filling"
- null if no treatment is mentioned

confidence:
- "high" → intent + info clearly stated
- "medium" → intent clear but some ambiguity
- "low" → unclear, vague, or conversational message

--------------------------------

EXAMPLES:

User: "Book an appointment next friday at 3pm for a root canal"
Output:
{
  "intent": "BOOK",
  "date_text": "next friday",
  "time_text": "3pm",
  "patient_name": null,
  "patient_phone": null,
  "treatment_text": "root canal",
  "confidence": "high"
}

User: "I need a tooth extraction on Monday"
Output:
{
  "intent": "BOOK",
  "date_text": "monday",
  "time_text": null,
  "patient_name": null,
  "patient_phone": null,
  "treatment_text": "tooth extraction",
  "confidence": "high"
}

User: "Book an appointment next friday at 3pm"
Output:
{
  "intent": "BOOK",
  "date_text": "next friday",
  "time_text": "3pm",
  "patient_name": null,
  "patient_phone": null,
  "treatment_text": null,
  "confidence": "high"
}

User: "Same time tomorrow"
Output:
{
  "intent": null,
  "date_text": "tomorrow",
  "time_text": "same time",
  "patient_name": null,
  "patient_phone": null,
  "treatment_text": null,
  "confidence": "medium"
}

User: "Hi"
Output:
{
  "intent": null,
  "date_text": null,
  "time_text": null,
  "patient_name": null,
  "patient_phone": null,
  "treatment_text": null,
  "confidence": "low"
}

"""

# Required fields — must always be present in output
_REQUIRED_KEYS = [
    "intent",
    "date_text",
    "time_text",
    "patient_name",
    "patient_phone",
    "treatment_text",
    "confidence",
]


def extract_entities(user_message: str, current_intent: str | None = None) -> dict:
    """
    Stateless. Safe. JSON-only.

    Returns all original fields PLUS:
      treatment_text  → raw phrase the patient said  (e.g. "root canal")
      treatment_key   → canonical key resolved locally (e.g. "root_canal")
                        None if treatment_text could not be matched
    """

    user_prompt = f"""User message:
"{user_message}"

Current intent (if known):
"{current_intent}"

Output STRICT JSON only. No explanation, no markdown."""

    try:
        response = httpx.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": user_prompt},
                ],
                "max_tokens": 250,
                "temperature": 0.0,  # deterministic for extraction
            },
            timeout=10.0,
        )
        response.raise_for_status()

        text = response.json()["choices"][0]["message"]["content"].strip()

        # Strip markdown fences if model wraps in ```json ... ```
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()

        data = json.loads(text)

        # ---- HARD SAFETY GUARDS ----
        if not isinstance(data, dict):
            raise ValueError("Invalid JSON")

        for key in _REQUIRED_KEYS:
            if key not in data:
                data[key] = None

        if data["confidence"] not in {"high", "medium", "low"}:
            data["confidence"] = "low"

        # ── Resolve treatment_key locally (fast, no LLM) ────────
        # Priority: treatment_text from LLM → fallback scan of raw message
        raw_phrase = data.get("treatment_text") or ""
        treatment = get_treatment_by_alias(raw_phrase) if raw_phrase else None

        # Fallback: scan the full user message directly
        if treatment is None:
            treatment = get_treatment_by_alias(user_message)

        data["treatment_key"] = treatment.key if treatment else None

        return data

    except Exception:
        # Absolute fallback: extractor must NEVER break the system
        return {
            "intent": None,
            "date_text": None,
            "time_text": None,
            "patient_name": None,
            "patient_phone": None,
            "treatment_text": None,
            "treatment_key": None,
            "confidence": "low",
        }