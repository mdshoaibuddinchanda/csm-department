import os
import base64
import logging
import httpx

logger = logging.getLogger("medschedule")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# meta-llama/llama-4-scout-17b-16e-instruct supports both text + vision (free)
GROQ_VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
GROQ_TEXT_MODEL   = "llama-3.3-70b-versatile"

DENTAL_SYSTEM_PROMPT = """You are DentalAssist AI, a friendly and knowledgeable dental health assistant 
for a smart dental management system. Your role is to help patients understand their dental symptoms 
BEFORE they see a dentist.

Your responsibilities:
1. Listen carefully to the patient's dental complaint in plain language OR analyse the dental image they share
2. Identify the likely dental issue (e.g., cavity, gum disease, abscess, sensitivity, wisdom tooth, etc.)
3. Assess the SERIOUSNESS: Low / Moderate / High / Emergency
4. Provide simple PRECAUTIONS they can take at home right now
5. Tell them WHAT TYPE of dental appointment to book (routine checkup, urgent, emergency)
6. Always recommend booking an appointment with a dentist — never replace professional advice

If the user shares an IMAGE:
- Describe what you can visually observe in simple terms (discoloration, swelling, gum recession, etc.)
- Give your best assessment based on visual evidence
- Be extra clear that visual AI analysis is not a substitute for an in-person exam

Response format (always structured like this):
🦷 **Possible Issue:** [what it might be, in simple terms]
⚠️ **Seriousness:** [Low / Moderate / High / Emergency] — [1 sentence why]
💊 **What you can do now:** [2-3 practical home precautions]
📅 **Next step:** [type of appointment to book + urgency]
💬 **Note:** [1 reassuring line reminding them this is AI guidance, not a diagnosis]

Rules:
- Always respond in a warm, calm, non-alarming tone
- Use simple everyday language — no medical jargon
- If symptoms suggest a dental emergency (severe pain, swelling, fever, trauma), say so clearly
- Keep responses concise — under 220 words
- Never diagnose definitively; always say "this could be" or "it looks like"
- If the question/image is not dental-related, gently redirect: "I'm only able to help with dental concerns!"
"""


def _encode_image(image_bytes: bytes, content_type: str) -> str:
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{content_type};base64,{b64}"


async def get_dental_ai_response(
    user_message: str,
    image_bytes: bytes | None = None,
    image_content_type: str = "image/jpeg",
) -> str:
    """
    Sends user message (and optionally an image) to Groq API.
    - image provided → vision model
    - text only      → fast text model
    """
    if not GROQ_API_KEY:
        logger.error("GROQ_API_KEY not set in environment")
        return "⚠️ AI assistant is currently unavailable. Please call us or book an appointment directly."

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    # ── Build message content ──────────────────────────────────────
    if image_bytes:
        image_data_url = _encode_image(image_bytes, image_content_type)
        user_text = (
            user_message.strip()
            if user_message.strip()
            else "Please analyse this dental image and tell me what you see."
        )
        content = [
            {"type": "image_url", "image_url": {"url": image_data_url}},
            {"type": "text",      "text": user_text},
        ]
        model = GROQ_VISION_MODEL
    else:
        content = user_message.strip()
        model   = GROQ_TEXT_MODEL

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": DENTAL_SYSTEM_PROMPT},
            {"role": "user",   "content": content},
        ],
        "max_tokens": 450,
        "temperature": 0.5,
    }

    # ── Call Groq ──────────────────────────────────────────────────
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(GROQ_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            data  = response.json()
            reply = data["choices"][0]["message"]["content"].strip()
            logger.info(
                f"Dental AI response generated | model={model} | vision={'yes' if image_bytes else 'no'}"
            )
            return reply

    except httpx.TimeoutException:
        logger.warning("Groq API timed out")
        return "⏱️ The AI is taking a bit longer than usual. Please try again in a moment."

    except httpx.HTTPStatusError as e:
        logger.error(f"Groq API HTTP error: {e.response.status_code} — {e.response.text}")
        return "⚠️ AI assistant is temporarily unavailable. Please try again shortly."

    except Exception as e:
        logger.exception(f"Unexpected error in dental AI service: {str(e)}")
        return "⚠️ Something went wrong. Please try again or contact us directly."