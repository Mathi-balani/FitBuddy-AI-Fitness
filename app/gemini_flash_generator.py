import logging

from .gemini_client import client, TIP_MODEL

logger = logging.getLogger(__name__)

def generate_nutrition_tip_with_flash(goal: str) -> str:
    prompt = f"""
Give one concise, practical nutrition or recovery tip for a person whose
fitness goal is: {goal}

Rules:
- 80 words maximum.
- General wellness guidance only.
- Do not prescribe supplements, extreme diets, fasting protocols, or medical treatment.
- Encourage balanced nutrition, hydration, sleep, and sustainable habits where relevant.
- Mention that people with medical/dietary conditions should consult a qualified professional.
"""
    if client is None:
        return "Build meals around vegetables or fruit, a protein source, and satisfying whole-food carbohydrates. Drink water regularly and prioritize sleep; consult a qualified professional for individual medical or dietary needs."

    try:
        response = client.models.generate_content(
            model=TIP_MODEL,
            contents=prompt,
        )
        return response.text.strip()
    except Exception as exc:
        logger.warning(
            "Gemini nutrition request failed (%s, status=%s); using built-in fallback.",
            type(exc).__name__,
            getattr(exc, "status_code", "unknown"),
        )
        return "Build meals around vegetables or fruit, a protein source, and satisfying whole-food carbohydrates. Drink water regularly and prioritize sleep; consult a qualified professional for individual medical or dietary needs."
